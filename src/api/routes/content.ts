import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db } from '../config/database';
import { authorize } from '../middleware/auth';
import { asyncHandler } from '../middleware/errorHandler';
import { realtimeService } from '../server';

const router = Router();

// Validation schemas
const createContentSchema = z.object({
  title: z.string().min(1).max(255),
  type: z.enum(['article', 'video', 'social']),
  status: z.enum(['draft', 'published', 'scheduled']).default('draft'),
  content_body: z.string(),
  meta_description: z.string().max(160).optional(),
  target_keywords: z.array(z.number()).optional(),
  published_at: z.string().datetime().optional(),
  channel: z.string(),
  metadata: z.object({}).passthrough().optional()
});

const updateContentSchema = createContentSchema.partial();

// GET /content - List all content with pagination
router.get('/', asyncHandler(async (req: Request, res: Response) => {
  const page = parseInt(req.query.page as string) || 1;
  const limit = parseInt(req.query.limit as string) || 20;
  const status = req.query.status as string;
  const type = req.query.type as string;
  const channel = req.query.channel as string;
  const search = req.query.search as string;
  
  const offset = (page - 1) * limit;
  
  // Build query
  const conditions: string[] = [];
  const values: any[] = [];
  let valueIndex = 1;
  
  if (status) {
    conditions.push(`status = $${valueIndex++}`);
    values.push(status);
  }
  
  if (type) {
    conditions.push(`type = $${valueIndex++}`);
    values.push(type);
  }
  
  if (channel) {
    conditions.push(`channel = $${valueIndex++}`);
    values.push(channel);
  }
  
  if (search) {
    conditions.push(`(title ILIKE $${valueIndex} OR content_body ILIKE $${valueIndex})`);
    values.push(`%${search}%`);
    valueIndex++;
  }
  
  const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';
  
  // Get total count
  const countQuery = `SELECT COUNT(*) FROM content ${whereClause}`;
  const countResult = await db.query(countQuery, values);
  const totalCount = parseInt(countResult.rows[0].count);
  
  // Get paginated results
  const query = `
    SELECT 
      c.*,
      u.name as author_name,
      COUNT(DISTINCT ck.keyword_id) as keyword_count,
      COALESCE(SUM(cp.impressions), 0) as total_impressions,
      COALESCE(SUM(cp.clicks), 0) as total_clicks
    FROM content c
    LEFT JOIN users u ON c.created_by = u.id
    LEFT JOIN content_keywords ck ON c.id = ck.content_id
    LEFT JOIN content_performance cp ON c.id = cp.content_id
    ${whereClause}
    GROUP BY c.id, u.name
    ORDER BY c.created_at DESC
    LIMIT $${valueIndex} OFFSET $${valueIndex + 1}
  `;
  
  values.push(limit, offset);
  const result = await db.query(query, values);
  
  res.json({
    data: result.rows,
    pagination: {
      page,
      limit,
      total: totalCount,
      pages: Math.ceil(totalCount / limit)
    }
  });
}));

// GET /content/:id - Get single content item
router.get('/:id', asyncHandler(async (req: Request, res: Response) => {
  const query = `
    SELECT 
      c.*,
      u.name as author_name,
      array_agg(
        DISTINCT jsonb_build_object(
          'id', k.id,
          'keyword', k.keyword,
          'priority_tier', k.priority_tier
        )
      ) FILTER (WHERE k.id IS NOT NULL) as keywords
    FROM content c
    LEFT JOIN users u ON c.created_by = u.id
    LEFT JOIN content_keywords ck ON c.id = ck.content_id
    LEFT JOIN keywords k ON ck.keyword_id = k.id
    WHERE c.id = $1
    GROUP BY c.id, u.name
  `;
  
  const result = await db.query(query, [req.params.id]);
  
  if (result.rows.length === 0) {
    return res.status(404).json({ error: 'Content not found' });
  }
  
  res.json(result.rows[0]);
}));

// POST /content - Create new content
router.post('/', 
  authorize('admin', 'manager'),
  asyncHandler(async (req: Request, res: Response) => {
    const data = createContentSchema.parse(req.body);
    const userId = req.user!.userId;
    
    const client = await db.connect();
    try {
      await client.query('BEGIN');
      
      // Create content
      const contentQuery = `
        INSERT INTO content (
          title, type, status, content_body, meta_description,
          published_at, channel, metadata, created_by
        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
        RETURNING *
      `;
      
      const contentValues = [
        data.title,
        data.type,
        data.status,
        data.content_body,
        data.meta_description,
        data.published_at,
        data.channel,
        JSON.stringify(data.metadata || {}),
        userId
      ];
      
      const contentResult = await client.query(contentQuery, contentValues);
      const content = contentResult.rows[0];
      
      // Associate keywords if provided
      if (data.target_keywords && data.target_keywords.length > 0) {
        const keywordValues = data.target_keywords
          .map((keywordId, index) => `($1, $${index + 2})`)
          .join(', ');
        
        const keywordQuery = `
          INSERT INTO content_keywords (content_id, keyword_id)
          VALUES ${keywordValues}
        `;
        
        await client.query(keywordQuery, [content.id, ...data.target_keywords]);
      }
      
      await client.query('COMMIT');
      
      // Notify real-time clients
      realtimeService.broadcastContentUpdate('created', content);
      
      res.status(201).json(content);
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  })
);

// PUT /content/:id - Update content
router.put('/:id',
  authorize('admin', 'manager'),
  asyncHandler(async (req: Request, res: Response) => {
    const data = updateContentSchema.parse(req.body);
    const contentId = req.params.id;
    
    const client = await db.connect();
    try {
      await client.query('BEGIN');
      
      // Build update query
      const fields = [];
      const values = [];
      let valueIndex = 1;
      
      Object.entries(data).forEach(([key, value]) => {
        if (value !== undefined && key !== 'target_keywords') {
          fields.push(`${key} = $${valueIndex++}`);
          values.push(value);
        }
      });
      
      if (fields.length === 0) {
        return res.status(400).json({ error: 'No fields to update' });
      }
      
      fields.push(`updated_at = NOW()`);
      values.push(contentId);
      
      const updateQuery = `
        UPDATE content 
        SET ${fields.join(', ')}
        WHERE id = $${valueIndex}
        RETURNING *
      `;
      
      const result = await client.query(updateQuery, values);
      
      if (result.rows.length === 0) {
        await client.query('ROLLBACK');
        return res.status(404).json({ error: 'Content not found' });
      }
      
      // Update keywords if provided
      if (data.target_keywords !== undefined) {
        // Remove existing keywords
        await client.query('DELETE FROM content_keywords WHERE content_id = $1', [contentId]);
        
        // Add new keywords
        if (data.target_keywords.length > 0) {
          const keywordValues = data.target_keywords
            .map((keywordId, index) => `($1, $${index + 2})`)
            .join(', ');
          
          const keywordQuery = `
            INSERT INTO content_keywords (content_id, keyword_id)
            VALUES ${keywordValues}
          `;
          
          await client.query(keywordQuery, [contentId, ...data.target_keywords]);
        }
      }
      
      await client.query('COMMIT');
      
      // Notify real-time clients
      realtimeService.broadcastContentUpdate('updated', result.rows[0]);
      
      res.json(result.rows[0]);
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  })
);

// DELETE /content/:id - Delete content
router.delete('/:id',
  authorize('admin'),
  asyncHandler(async (req: Request, res: Response) => {
    const result = await db.query(
      'DELETE FROM content WHERE id = $1 RETURNING id',
      [req.params.id]
    );
    
    if (result.rowCount === 0) {
      return res.status(404).json({ error: 'Content not found' });
    }
    
    // Notify real-time clients
    realtimeService.broadcastContentUpdate('deleted', { id: req.params.id });
    
    res.status(204).send();
  })
);

// POST /content/:id/performance - Track content performance
router.post('/:id/performance',
  authorize('admin', 'manager', 'analyst'),
  asyncHandler(async (req: Request, res: Response) => {
    const performanceData = z.object({
      impressions: z.number().min(0),
      clicks: z.number().min(0),
      ctr: z.number().min(0).max(1),
      engagement_rate: z.number().min(0).max(1),
      conversions: z.number().min(0).optional()
    }).parse(req.body);
    
    const contentId = req.params.id;
    
    // Check if content exists
    const contentCheck = await db.query('SELECT id FROM content WHERE id = $1', [contentId]);
    
    if (contentCheck.rows.length === 0) {
      return res.status(404).json({ error: 'Content not found' });
    }
    
    // Insert or update performance data
    const query = `
      INSERT INTO content_performance (
        content_id, date, impressions, clicks, ctr, 
        engagement_rate, conversions
      ) VALUES ($1, CURRENT_DATE, $2, $3, $4, $5, $6)
      ON CONFLICT (content_id, date) DO UPDATE SET
        impressions = EXCLUDED.impressions,
        clicks = EXCLUDED.clicks,
        ctr = EXCLUDED.ctr,
        engagement_rate = EXCLUDED.engagement_rate,
        conversions = EXCLUDED.conversions
    `;
    
    await db.query(query, [
      contentId,
      performanceData.impressions,
      performanceData.clicks,
      performanceData.ctr,
      performanceData.engagement_rate,
      performanceData.conversions || 0
    ]);
    
    res.json({ message: 'Performance data recorded' });
  })
);

export default router;