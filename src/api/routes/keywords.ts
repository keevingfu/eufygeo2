import { Router, Request, Response } from 'express';
import { z } from 'zod';
import multer from 'multer';
import csv from 'csv-parse';
import { createReadStream } from 'fs';
import { unlink } from 'fs/promises';
import { KeywordService } from '../services/keyword.service';
import { db } from '../config/database';
import { authorize } from '../middleware/auth';
import { asyncHandler } from '../middleware/errorHandler';
import { realtimeService } from '../server';
import { KeywordFilters, Keyword } from '../../types';

// Initialize service
const keywordService = new KeywordService(db);

// Configure multer for CSV uploads
const upload = multer({
  dest: 'uploads/temp/',
  limits: { fileSize: 10 * 1024 * 1024 }, // 10MB
  fileFilter: (req, file, cb) => {
    if (file.mimetype === 'text/csv' || file.mimetype === 'application/vnd.ms-excel') {
      cb(null, true);
    } else {
      cb(new Error('Only CSV files are allowed'));
    }
  }
});

// Validation schemas
const createKeywordSchema = z.object({
  keyword: z.string().min(1).max(255),
  search_volume: z.number().min(0).optional(),
  difficulty: z.number().min(0).max(100).optional(),
  cpc: z.number().min(0).optional(),
  competition: z.number().min(0).max(1).optional(),
  priority_tier: z.enum(['P0', 'P1', 'P2', 'P3', 'P4']).optional(),
  product_category: z.string().optional(),
  user_intent: z.enum(['informational', 'navigational', 'commercial', 'transactional']).optional(),
  metadata: z.object({}).passthrough().optional()
});

const updateKeywordSchema = createKeywordSchema.partial();

const router = Router();

// GET /keywords - Get paginated keywords with filters
router.get('/', asyncHandler(async (req: Request, res: Response) => {
  const filters: KeywordFilters = {
    page: parseInt(req.query.page as string) || 1,
    limit: parseInt(req.query.limit as string) || 50,
    sort: req.query.sort as string || 'search_volume',
    order: (req.query.order as string || 'desc') as 'asc' | 'desc',
    priority_tier: req.query.priority_tier as string,
    aio_status: req.query.aio_status as string,
    product_category: req.query.product_category as string,
    min_volume: req.query.min_volume ? parseInt(req.query.min_volume as string) : undefined,
    max_volume: req.query.max_volume ? parseInt(req.query.max_volume as string) : undefined,
    search: req.query.search as string
  };

  const result = await keywordService.getKeywords(filters);
  
  res.json(result);
}));

// GET /keywords/pyramid - Get pyramid visualization data
router.get('/pyramid', asyncHandler(async (req: Request, res: Response) => {
  const pyramidData = await keywordService.getPyramidData();
  res.json(pyramidData);
}));

// GET /keywords/:id - Get single keyword
router.get('/:id', asyncHandler(async (req: Request, res: Response) => {
  const keyword = await keywordService.getKeywordById(parseInt(req.params.id));
  
  if (!keyword) {
    return res.status(404).json({ error: 'Keyword not found' });
  }
  
  res.json(keyword);
}));

// POST /keywords - Create new keyword (admin/manager only)
router.post('/', 
  authorize('admin', 'manager'),
  asyncHandler(async (req: Request, res: Response) => {
    const data = createKeywordSchema.parse(req.body);
    const keyword = await keywordService.createKeyword(data);
    
    // Notify real-time clients
    realtimeService.broadcastKeywordUpdate('created', keyword);
    
    res.status(201).json(keyword);
  })
);

// PUT /keywords/:id - Update keyword (admin/manager only)
router.put('/:id',
  authorize('admin', 'manager'),
  asyncHandler(async (req: Request, res: Response) => {
    const data = updateKeywordSchema.parse(req.body);
    const keyword = await keywordService.updateKeyword(parseInt(req.params.id), data);
    
    if (!keyword) {
      return res.status(404).json({ error: 'Keyword not found' });
    }
    
    // Notify real-time clients
    realtimeService.broadcastKeywordUpdate('updated', keyword);
    
    res.json(keyword);
  })
);

// DELETE /keywords/:id - Delete keyword (admin only)
router.delete('/:id',
  authorize('admin'),
  asyncHandler(async (req: Request, res: Response) => {
    const deleted = await keywordService.deleteKeyword(parseInt(req.params.id));
    
    if (!deleted) {
      return res.status(404).json({ error: 'Keyword not found' });
    }
    
    // Notify real-time clients
    realtimeService.broadcastKeywordUpdate('deleted', { id: parseInt(req.params.id) });
    
    res.status(204).send();
  })
);

// POST /keywords/bulk-import - Bulk import keywords from CSV (admin/manager only)
router.post('/bulk-import',
  authorize('admin', 'manager'),
  upload.single('file'),
  asyncHandler(async (req: Request, res: Response) => {
    if (!req.file) {
      return res.status(400).json({ error: 'No file uploaded' });
    }

    const results: { success: number; failed: number; errors: string[] } = {
      success: 0,
      failed: 0,
      errors: []
    };

    try {
      // Parse CSV file
      const parser = createReadStream(req.file.path).pipe(
        csv.parse({
          columns: true,
          skip_empty_lines: true,
          trim: true
        })
      );

      const batchSize = 100;
      const batch: Partial<Keyword>[] = [];

      for await (const row of parser) {
        try {
          // Map CSV columns to keyword data
          const keywordData: Partial<Keyword> = {
            keyword: row.keyword || row.Keyword,
            search_volume: parseInt(row.search_volume || row['Search Volume'] || '0'),
            difficulty: row.difficulty ? parseFloat(row.difficulty) : undefined,
            cpc: row.cpc ? parseFloat(row.cpc) : undefined,
            competition: row.competition ? parseFloat(row.competition) : undefined,
            product_category: row.product_category || row['Product Category'],
            user_intent: row.user_intent || row['User Intent']
          };

          // Validate required fields
          if (!keywordData.keyword) {
            throw new Error('Keyword field is required');
          }

          batch.push(keywordData);

          // Process batch when it reaches the limit
          if (batch.length >= batchSize) {
            await processBatch(batch, results);
            batch.length = 0;
            
            // Send progress update
            realtimeService.broadcastImportProgress({
              total: results.success + results.failed,
              processed: results.success + results.failed,
              success: results.success,
              failed: results.failed
            });
          }
        } catch (error) {
          results.failed++;
          results.errors.push(`Row ${results.success + results.failed + 1}: ${error.message}`);
        }
      }

      // Process remaining items
      if (batch.length > 0) {
        await processBatch(batch, results);
      }

      // Clean up uploaded file
      await unlink(req.file.path);

      // Auto-classify new keywords
      if (results.success > 0) {
        const classifyResult = await keywordService.autoClassifyKeywords();
        
        res.json({
          message: 'Import completed',
          results: {
            ...results,
            classified: classifyResult.classified,
            classification: classifyResult.tiers
          }
        });
      } else {
        res.json({
          message: 'Import completed with errors',
          results
        });
      }
    } catch (error) {
      // Clean up uploaded file on error
      await unlink(req.file.path);
      throw error;
    }
  })
);

// POST /keywords/auto-classify - Auto-classify unassigned keywords (admin/manager only)
router.post('/auto-classify',
  authorize('admin', 'manager'),
  asyncHandler(async (req: Request, res: Response) => {
    const result = await keywordService.autoClassifyKeywords();
    
    res.json({
      message: 'Auto-classification completed',
      ...result
    });
  })
);

// POST /keywords/:id/performance - Track keyword performance
router.post('/:id/performance',
  authorize('admin', 'manager', 'analyst'),
  asyncHandler(async (req: Request, res: Response) => {
    const performanceData = z.object({
      impressions: z.number().min(0),
      clicks: z.number().min(0),
      ctr: z.number().min(0).max(1),
      position: z.number().min(1),
      aio_appearances: z.number().min(0).optional()
    }).parse(req.body);

    await keywordService.trackPerformance(parseInt(req.params.id), performanceData);
    
    res.json({ message: 'Performance data recorded' });
  })
);

// Helper function to process batch of keywords
async function processBatch(
  batch: Partial<Keyword>[], 
  results: { success: number; failed: number; errors: string[] }
) {
  for (const keywordData of batch) {
    try {
      await keywordService.createKeyword(keywordData);
      results.success++;
    } catch (error) {
      results.failed++;
      if (error.code === '23505') {
        // Duplicate keyword - try to update instead
        try {
          const existing = await db.query(
            'SELECT id FROM keywords WHERE keyword = $1',
            [keywordData.keyword]
          );
          
          if (existing.rows.length > 0) {
            await keywordService.updateKeyword(existing.rows[0].id, keywordData);
            results.success++;
            results.failed--; // Correct the count
          }
        } catch (updateError) {
          results.errors.push(`Keyword "${keywordData.keyword}": ${updateError.message}`);
        }
      } else {
        results.errors.push(`Keyword "${keywordData.keyword}": ${error.message}`);
      }
    }
  }
}

export default router;