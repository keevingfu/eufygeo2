import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db, redis } from '../server';

// Example of Express/TypeScript API with Zod validation
// Demonstrates:
// 1. Input validation with Zod schemas
// 2. Redis caching strategy
// 3. Error handling patterns
// 4. TypeScript typing

const router = Router();

// Validation schema
const KeywordFilterSchema = z.object({
  priority_tier: z.enum(['P0', 'P1', 'P2', 'P3', 'P4']).optional(),
  min_volume: z.number().min(0).optional(),
  max_volume: z.number().optional(),
  page: z.number().default(1),
  limit: z.number().min(1).max(100).default(50)
});

// GET /api/keywords with caching
router.get('/keywords', async (req: Request, res: Response) => {
  try {
    // Validate input
    const filters = KeywordFilterSchema.parse(req.query);
    
    // Check cache
    const cacheKey = `keywords:${JSON.stringify(filters)}`;
    const cached = await redis.get(cacheKey);
    if (cached) {
      return res.json(JSON.parse(cached));
    }

    // Query database
    const result = await db.query(`
      SELECT * FROM keywords 
      WHERE ($1::text IS NULL OR priority_tier = $1)
      AND search_volume >= COALESCE($2, 0)
      AND search_volume <= COALESCE($3, 999999)
      ORDER BY search_volume DESC
      LIMIT $4 OFFSET $5
    `, [
      filters.priority_tier || null,
      filters.min_volume || 0,
      filters.max_volume || 999999,
      filters.limit,
      (filters.page - 1) * filters.limit
    ]);

    // Cache for 5 minutes
    await redis.setex(cacheKey, 300, JSON.stringify(result.rows));
    
    res.json({
      keywords: result.rows,
      pagination: {
        page: filters.page,
        limit: filters.limit
      }
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return res.status(400).json({ error: 'Invalid input', details: error.errors });
    }
    console.error('Error fetching keywords:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// POST /api/keywords/bulk-import
router.post('/keywords/bulk-import', async (req: Request, res: Response) => {
  // Example of bulk operation with progress tracking
  const { keywords } = req.body;
  const batchSize = 100;
  
  for (let i = 0; i < keywords.length; i += batchSize) {
    const batch = keywords.slice(i, i + batchSize);
    // Process batch...
    
    // Report progress
    const progress = Math.round((i + batch.length) / keywords.length * 100);
    // Send progress via SSE or WebSocket
  }
  
  res.json({ imported: keywords.length });
});

export default router;