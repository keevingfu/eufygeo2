import { Router, Request, Response } from 'express';
import { z } from 'zod';
import { db, redis } from '../config/database';
import { authorize } from '../middleware/auth';
import { asyncHandler } from '../middleware/errorHandler';
import { realtimeService } from '../server';

const router = Router();

// Validation schemas
const dateRangeSchema = z.object({
  start_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/),
  end_date: z.string().regex(/^\d{4}-\d{2}-\d{2}$/)
});

// GET /analytics/dashboard - Get dashboard overview
router.get('/dashboard', asyncHandler(async (req: Request, res: Response) => {
  const { start_date = '30_days_ago', end_date = 'today' } = req.query;
  
  // Calculate actual dates
  const endDate = end_date === 'today' ? new Date() : new Date(end_date as string);
  const startDate = start_date === '30_days_ago' 
    ? new Date(endDate.getTime() - 30 * 24 * 60 * 60 * 1000)
    : new Date(start_date as string);

  const cacheKey = `analytics:dashboard:${startDate.toISOString().split('T')[0]}:${endDate.toISOString().split('T')[0]}`;
  
  // Check cache
  const cached = await redis.get(cacheKey);
  if (cached) {
    return res.json(JSON.parse(cached));
  }

  // Get key metrics
  const queries = {
    // Total keywords by tier
    keywordsByTier: `
      SELECT priority_tier, COUNT(*) as count
      FROM keywords
      WHERE priority_tier IS NOT NULL
      GROUP BY priority_tier
    `,
    
    // AIO coverage
    aioCoverage: `
      SELECT 
        COUNT(CASE WHEN aio_status = 'active' THEN 1 END) as active,
        COUNT(CASE WHEN aio_status = 'monitoring' THEN 1 END) as monitoring,
        COUNT(CASE WHEN aio_status = 'inactive' THEN 1 END) as inactive,
        COUNT(*) as total
      FROM keywords
    `,
    
    // Content performance
    contentPerformance: `
      SELECT 
        c.type,
        COUNT(DISTINCT c.id) as content_count,
        COALESCE(SUM(cp.impressions), 0) as total_impressions,
        COALESCE(SUM(cp.clicks), 0) as total_clicks,
        COALESCE(AVG(cp.ctr), 0) as avg_ctr
      FROM content c
      LEFT JOIN content_performance cp ON c.id = cp.content_id
        AND cp.date BETWEEN $1 AND $2
      WHERE c.status = 'published'
      GROUP BY c.type
    `,
    
    // Traffic trends
    trafficTrends: `
      SELECT 
        date,
        SUM(impressions) as impressions,
        SUM(clicks) as clicks,
        AVG(position) as avg_position
      FROM keyword_performance
      WHERE date BETWEEN $1 AND $2
      GROUP BY date
      ORDER BY date
    `,
    
    // Top performing keywords
    topKeywords: `
      SELECT 
        k.keyword,
        k.priority_tier,
        SUM(kp.clicks) as clicks,
        SUM(kp.impressions) as impressions,
        AVG(kp.ctr) as avg_ctr,
        AVG(kp.position) as avg_position
      FROM keywords k
      JOIN keyword_performance kp ON k.id = kp.keyword_id
      WHERE kp.date BETWEEN $1 AND $2
      GROUP BY k.id, k.keyword, k.priority_tier
      ORDER BY clicks DESC
      LIMIT 10
    `,
    
    // Channel distribution
    channelDistribution: `
      SELECT 
        channel,
        COUNT(*) as content_count,
        SUM(impressions) as impressions,
        SUM(clicks) as clicks
      FROM content c
      JOIN content_performance cp ON c.id = cp.content_id
      WHERE cp.date BETWEEN $1 AND $2
        AND c.status = 'published'
      GROUP BY channel
    `
  };

  const results: any = {};
  
  // Execute all queries in parallel
  const promises = Object.entries(queries).map(async ([key, query]) => {
    const needsDates = query.includes('$1');
    const params = needsDates ? [startDate, endDate] : [];
    const result = await db.query(query, params);
    results[key] = result.rows;
  });

  await Promise.all(promises);

  // Calculate summary metrics
  const summary = {
    totalKeywords: results.keywordsByTier.reduce((sum: number, tier: any) => sum + parseInt(tier.count), 0),
    aioCoverageRate: results.aioCoverage[0]?.total > 0 
      ? (results.aioCoverage[0].active / results.aioCoverage[0].total) * 100 
      : 0,
    totalImpressions: results.contentPerformance.reduce((sum: number, item: any) => sum + parseInt(item.total_impressions), 0),
    totalClicks: results.contentPerformance.reduce((sum: number, item: any) => sum + parseInt(item.total_clicks), 0),
    avgCtr: results.contentPerformance.length > 0
      ? results.contentPerformance.reduce((sum: number, item: any) => sum + parseFloat(item.avg_ctr), 0) / results.contentPerformance.length
      : 0
  };

  const dashboard = {
    summary,
    keywordsByTier: results.keywordsByTier,
    aioCoverage: results.aioCoverage[0],
    contentPerformance: results.contentPerformance,
    trafficTrends: results.trafficTrends,
    topKeywords: results.topKeywords,
    channelDistribution: results.channelDistribution,
    dateRange: {
      start: startDate.toISOString().split('T')[0],
      end: endDate.toISOString().split('T')[0]
    }
  };

  // Cache for 1 hour
  await redis.setex(cacheKey, 3600, JSON.stringify(dashboard));

  res.json(dashboard);
}));

// GET /analytics/keywords/performance - Get keyword performance data
router.get('/keywords/performance', asyncHandler(async (req: Request, res: Response) => {
  const { 
    start_date,
    end_date,
    priority_tier,
    limit = '50',
    offset = '0'
  } = req.query;

  // Build query
  const conditions: string[] = [];
  const values: any[] = [];
  let valueIndex = 1;

  if (start_date) {
    conditions.push(`kp.date >= $${valueIndex++}`);
    values.push(start_date);
  }

  if (end_date) {
    conditions.push(`kp.date <= $${valueIndex++}`);
    values.push(end_date);
  }

  if (priority_tier) {
    conditions.push(`k.priority_tier = $${valueIndex++}`);
    values.push(priority_tier);
  }

  const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

  const query = `
    SELECT 
      k.id,
      k.keyword,
      k.priority_tier,
      k.aio_status,
      COUNT(kp.date) as data_points,
      SUM(kp.impressions) as total_impressions,
      SUM(kp.clicks) as total_clicks,
      AVG(kp.ctr) as avg_ctr,
      AVG(kp.position) as avg_position,
      MIN(kp.position) as best_position,
      SUM(kp.aio_appearances) as total_aio_appearances
    FROM keywords k
    LEFT JOIN keyword_performance kp ON k.id = kp.keyword_id
    ${whereClause}
    GROUP BY k.id, k.keyword, k.priority_tier, k.aio_status
    ORDER BY total_clicks DESC
    LIMIT $${valueIndex} OFFSET $${valueIndex + 1}
  `;

  values.push(limit, offset);
  const result = await db.query(query, values);

  res.json({
    data: result.rows,
    pagination: {
      limit: parseInt(limit as string),
      offset: parseInt(offset as string)
    }
  });
}));

// GET /analytics/content/performance - Get content performance data
router.get('/content/performance', asyncHandler(async (req: Request, res: Response) => {
  const { 
    start_date,
    end_date,
    type,
    channel,
    limit = '50',
    offset = '0'
  } = req.query;

  // Build query
  const conditions: string[] = ['c.status = \'published\''];
  const values: any[] = [];
  let valueIndex = 1;

  if (start_date) {
    conditions.push(`cp.date >= $${valueIndex++}`);
    values.push(start_date);
  }

  if (end_date) {
    conditions.push(`cp.date <= $${valueIndex++}`);
    values.push(end_date);
  }

  if (type) {
    conditions.push(`c.type = $${valueIndex++}`);
    values.push(type);
  }

  if (channel) {
    conditions.push(`c.channel = $${valueIndex++}`);
    values.push(channel);
  }

  const whereClause = `WHERE ${conditions.join(' AND ')}`;

  const query = `
    SELECT 
      c.id,
      c.title,
      c.type,
      c.channel,
      c.published_at,
      COUNT(cp.date) as data_points,
      SUM(cp.impressions) as total_impressions,
      SUM(cp.clicks) as total_clicks,
      AVG(cp.ctr) as avg_ctr,
      AVG(cp.engagement_rate) as avg_engagement_rate,
      SUM(cp.conversions) as total_conversions
    FROM content c
    LEFT JOIN content_performance cp ON c.id = cp.content_id
    ${whereClause}
    GROUP BY c.id, c.title, c.type, c.channel, c.published_at
    ORDER BY total_clicks DESC
    LIMIT $${valueIndex} OFFSET $${valueIndex + 1}
  `;

  values.push(limit, offset);
  const result = await db.query(query, values);

  res.json({
    data: result.rows,
    pagination: {
      limit: parseInt(limit as string),
      offset: parseInt(offset as string)
    }
  });
}));

// POST /analytics/generate-report - Generate custom analytics report
router.post('/generate-report',
  authorize('admin', 'manager', 'analyst'),
  asyncHandler(async (req: Request, res: Response) => {
    const reportSchema = z.object({
      name: z.string(),
      type: z.enum(['keyword_performance', 'content_performance', 'channel_analysis', 'custom']),
      date_range: dateRangeSchema,
      filters: z.object({
        priority_tiers: z.array(z.string()).optional(),
        channels: z.array(z.string()).optional(),
        content_types: z.array(z.string()).optional()
      }).optional(),
      metrics: z.array(z.string()).optional(),
      format: z.enum(['json', 'csv', 'pdf']).default('json')
    });

    const data = reportSchema.parse(req.body);
    const reportId = `report_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    // Store report request
    await db.query(
      `INSERT INTO analytics_reports (id, name, type, config, status, created_by)
       VALUES ($1, $2, $3, $4, 'processing', $5)`,
      [reportId, data.name, data.type, JSON.stringify(data), req.user!.userId]
    );

    // In a real implementation, this would be handled by a background job
    // For now, we'll simulate processing
    setTimeout(async () => {
      try {
        // Generate report based on type
        let reportData: any = {};

        switch (data.type) {
          case 'keyword_performance':
            reportData = await generateKeywordPerformanceReport(data);
            break;
          case 'content_performance':
            reportData = await generateContentPerformanceReport(data);
            break;
          case 'channel_analysis':
            reportData = await generateChannelAnalysisReport(data);
            break;
          case 'custom':
            reportData = await generateCustomReport(data);
            break;
        }

        // Update report status
        await db.query(
          `UPDATE analytics_reports 
           SET status = 'completed', result = $1, completed_at = NOW()
           WHERE id = $2`,
          [JSON.stringify(reportData), reportId]
        );

        // Notify via WebSocket
        realtimeService.broadcastReportProgress(reportId, 100, 'completed');
      } catch (error) {
        await db.query(
          `UPDATE analytics_reports 
           SET status = 'failed', error = $1
           WHERE id = $2`,
          [error.message, reportId]
        );

        realtimeService.broadcastReportProgress(reportId, 0, 'failed');
      }
    }, 2000);

    res.json({
      reportId,
      status: 'processing',
      message: 'Report generation started. You will be notified when complete.'
    });
  })
);

// GET /analytics/reports/:id - Get report status/result
router.get('/reports/:id', asyncHandler(async (req: Request, res: Response) => {
  const result = await db.query(
    'SELECT * FROM analytics_reports WHERE id = $1',
    [req.params.id]
  );

  if (result.rows.length === 0) {
    return res.status(404).json({ error: 'Report not found' });
  }

  const report = result.rows[0];

  // Check permission
  if (report.created_by !== req.user!.userId && !['admin', 'manager'].includes(req.user!.role)) {
    return res.status(403).json({ error: 'Unauthorized' });
  }

  res.json(report);
}));

// Helper functions for report generation
async function generateKeywordPerformanceReport(config: any) {
  const { date_range, filters } = config;
  
  let conditions = [`kp.date BETWEEN $1 AND $2`];
  const values = [date_range.start_date, date_range.end_date];
  let valueIndex = 3;

  if (filters?.priority_tiers?.length > 0) {
    conditions.push(`k.priority_tier = ANY($${valueIndex++})`);
    values.push(filters.priority_tiers);
  }

  const whereClause = conditions.join(' AND ');

  const query = `
    SELECT 
      k.keyword,
      k.priority_tier,
      k.aio_status,
      SUM(kp.impressions) as impressions,
      SUM(kp.clicks) as clicks,
      AVG(kp.position) as avg_position,
      COUNT(DISTINCT kp.date) as days_tracked
    FROM keywords k
    JOIN keyword_performance kp ON k.id = kp.keyword_id
    WHERE ${whereClause}
    GROUP BY k.id, k.keyword, k.priority_tier, k.aio_status
    ORDER BY clicks DESC
  `;

  const result = await db.query(query, values);
  return result.rows;
}

async function generateContentPerformanceReport(config: any) {
  const { date_range, filters } = config;
  
  let conditions = [`cp.date BETWEEN $1 AND $2`, `c.status = 'published'`];
  const values = [date_range.start_date, date_range.end_date];
  let valueIndex = 3;

  if (filters?.channels?.length > 0) {
    conditions.push(`c.channel = ANY($${valueIndex++})`);
    values.push(filters.channels);
  }

  if (filters?.content_types?.length > 0) {
    conditions.push(`c.type = ANY($${valueIndex++})`);
    values.push(filters.content_types);
  }

  const whereClause = conditions.join(' AND ');

  const query = `
    SELECT 
      c.title,
      c.type,
      c.channel,
      SUM(cp.impressions) as impressions,
      SUM(cp.clicks) as clicks,
      AVG(cp.engagement_rate) as avg_engagement_rate,
      SUM(cp.conversions) as conversions
    FROM content c
    JOIN content_performance cp ON c.id = cp.content_id
    WHERE ${whereClause}
    GROUP BY c.id, c.title, c.type, c.channel
    ORDER BY clicks DESC
  `;

  const result = await db.query(query, values);
  return result.rows;
}

async function generateChannelAnalysisReport(config: any) {
  const { date_range } = config;

  const query = `
    SELECT 
      c.channel,
      COUNT(DISTINCT c.id) as content_count,
      COUNT(DISTINCT ck.keyword_id) as keywords_targeted,
      SUM(cp.impressions) as total_impressions,
      SUM(cp.clicks) as total_clicks,
      AVG(cp.ctr) as avg_ctr,
      SUM(cp.conversions) as total_conversions
    FROM content c
    LEFT JOIN content_performance cp ON c.id = cp.content_id
      AND cp.date BETWEEN $1 AND $2
    LEFT JOIN content_keywords ck ON c.id = ck.content_id
    WHERE c.status = 'published'
    GROUP BY c.channel
    ORDER BY total_clicks DESC
  `;

  const result = await db.query(query, [date_range.start_date, date_range.end_date]);
  return result.rows;
}

async function generateCustomReport(config: any) {
  // Implement custom report logic based on metrics selected
  return { message: 'Custom report generation not implemented yet' };
}

export default router;