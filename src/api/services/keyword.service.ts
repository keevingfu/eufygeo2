import { Pool } from 'pg';
import { redis } from '../config/database';
import { 
  Keyword, 
  KeywordFilters, 
  PaginatedResponse, 
  ImportResult,
  PyramidData,
  PriorityTier 
} from '../../types';

export class KeywordService {
  constructor(private db: Pool) {}

  // Cache key generators
  private getCacheKey(type: string, params?: any): string {
    if (params) {
      return `keywords:${type}:${JSON.stringify(params)}`;
    }
    return `keywords:${type}`;
  }

  // Get paginated keywords with filters
  async getKeywords(filters: KeywordFilters): Promise<PaginatedResponse<Keyword>> {
    const { 
      page = 1, 
      limit = 50, 
      sort = 'search_volume', 
      order = 'desc',
      priority_tier,
      aio_status,
      product_category,
      min_volume,
      max_volume,
      search
    } = filters;

    const offset = (page - 1) * limit;
    const cacheKey = this.getCacheKey('list', filters);

    // Check cache
    const cached = await redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    // Build query
    const conditions: string[] = [];
    const values: any[] = [];
    let valueIndex = 1;

    if (priority_tier) {
      conditions.push(`priority_tier = $${valueIndex++}`);
      values.push(priority_tier);
    }

    if (aio_status) {
      conditions.push(`aio_status = $${valueIndex++}`);
      values.push(aio_status);
    }

    if (product_category) {
      conditions.push(`product_category = $${valueIndex++}`);
      values.push(product_category);
    }

    if (min_volume !== undefined) {
      conditions.push(`search_volume >= $${valueIndex++}`);
      values.push(min_volume);
    }

    if (max_volume !== undefined) {
      conditions.push(`search_volume <= $${valueIndex++}`);
      values.push(max_volume);
    }

    if (search) {
      conditions.push(`keyword ILIKE $${valueIndex++}`);
      values.push(`%${search}%`);
    }

    const whereClause = conditions.length > 0 ? `WHERE ${conditions.join(' AND ')}` : '';

    // Get total count
    const countQuery = `SELECT COUNT(*) FROM keywords ${whereClause}`;
    const countResult = await this.db.query(countQuery, values);
    const totalCount = parseInt(countResult.rows[0].count);

    // Get paginated results with computed fields
    const query = `
      SELECT 
        k.*,
        COUNT(DISTINCT ck.content_id) as content_count,
        COALESCE(AVG(kp.position), 999) as avg_position_30d,
        COALESCE(SUM(kp.clicks), 0) as clicks_30d
      FROM keywords k
      LEFT JOIN content_keywords ck ON k.id = ck.keyword_id
      LEFT JOIN keyword_performance kp ON k.id = kp.keyword_id 
        AND kp.date >= CURRENT_DATE - INTERVAL '30 days'
      ${whereClause}
      GROUP BY k.id
      ORDER BY ${sort} ${order}
      LIMIT $${valueIndex} OFFSET $${valueIndex + 1}
    `;

    values.push(limit, offset);
    const result = await this.db.query(query, values);

    const response: PaginatedResponse<Keyword> = {
      data: result.rows,
      pagination: {
        page,
        limit,
        total: totalCount,
        pages: Math.ceil(totalCount / limit)
      }
    };

    // Cache for 5 minutes
    await redis.setex(cacheKey, 300, JSON.stringify(response));

    return response;
  }

  // Get single keyword by ID
  async getKeywordById(id: number): Promise<Keyword | null> {
    const cacheKey = this.getCacheKey('single', id);
    
    const cached = await redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    const query = `
      SELECT 
        k.*,
        COUNT(DISTINCT ck.content_id) as content_count,
        COALESCE(AVG(kp.position), 999) as avg_position_30d,
        COALESCE(SUM(kp.clicks), 0) as clicks_30d
      FROM keywords k
      LEFT JOIN content_keywords ck ON k.id = ck.keyword_id
      LEFT JOIN keyword_performance kp ON k.id = kp.keyword_id 
        AND kp.date >= CURRENT_DATE - INTERVAL '30 days'
      WHERE k.id = $1
      GROUP BY k.id
    `;

    const result = await this.db.query(query, [id]);
    
    if (result.rows.length === 0) {
      return null;
    }

    const keyword = result.rows[0];
    
    // Cache for 10 minutes
    await redis.setex(cacheKey, 600, JSON.stringify(keyword));

    return keyword;
  }

  // Create new keyword
  async createKeyword(data: Partial<Keyword>): Promise<Keyword> {
    const {
      keyword,
      search_volume = 0,
      difficulty,
      cpc = 0,
      competition,
      priority_tier,
      product_category,
      user_intent,
      metadata = {}
    } = data;

    // Auto-classify if not provided
    const finalTier = priority_tier || this.classifyKeywordPriority({
      search_volume,
      difficulty,
      cpc
    });

    const query = `
      INSERT INTO keywords (
        keyword, search_volume, difficulty, cpc, competition,
        priority_tier, product_category, user_intent, metadata
      ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
      RETURNING *
    `;

    const values = [
      keyword,
      search_volume,
      difficulty,
      cpc,
      competition,
      finalTier,
      product_category,
      user_intent,
      JSON.stringify(metadata)
    ];

    const result = await this.db.query(query, values);
    
    // Clear related caches
    await this.clearKeywordCaches();

    return result.rows[0];
  }

  // Update keyword
  async updateKeyword(id: number, data: Partial<Keyword>): Promise<Keyword | null> {
    const fields = [];
    const values = [];
    let valueIndex = 1;

    // Build dynamic update query
    Object.entries(data).forEach(([key, value]) => {
      if (value !== undefined && key !== 'id' && key !== 'created_at') {
        fields.push(`${key} = $${valueIndex++}`);
        values.push(value);
      }
    });

    if (fields.length === 0) {
      return this.getKeywordById(id);
    }

    fields.push(`updated_at = NOW()`);
    values.push(id);

    const query = `
      UPDATE keywords 
      SET ${fields.join(', ')}
      WHERE id = $${valueIndex}
      RETURNING *
    `;

    const result = await this.db.query(query, values);

    if (result.rows.length === 0) {
      return null;
    }

    // Clear related caches
    await this.clearKeywordCaches(id);

    return result.rows[0];
  }

  // Delete keyword
  async deleteKeyword(id: number): Promise<boolean> {
    const query = 'DELETE FROM keywords WHERE id = $1 RETURNING id';
    const result = await this.db.query(query, [id]);
    
    if (result.rowCount > 0) {
      await this.clearKeywordCaches(id);
      return true;
    }

    return false;
  }

  // Get pyramid visualization data
  async getPyramidData(): Promise<PyramidData> {
    const cacheKey = this.getCacheKey('pyramid');
    
    const cached = await redis.get(cacheKey);
    if (cached) {
      return JSON.parse(cached);
    }

    const query = `
      SELECT 
        priority_tier,
        COUNT(*) as count,
        AVG(search_volume) as avg_volume,
        SUM(traffic) as total_traffic,
        COUNT(CASE WHEN aio_status = 'active' THEN 1 END) as aio_active_count
      FROM keywords
      WHERE priority_tier IS NOT NULL
      GROUP BY priority_tier
      ORDER BY priority_tier
    `;

    const result = await this.db.query(query);
    
    const pyramidData: PyramidData = {
      tiers: result.rows.map(row => ({
        priority_tier: row.priority_tier,
        count: parseInt(row.count),
        avg_volume: parseFloat(row.avg_volume || 0),
        total_traffic: parseInt(row.total_traffic || 0),
        aio_active_count: parseInt(row.aio_active_count || 0)
      })),
      summary: {
        total_keywords: result.rows.reduce((sum, tier) => sum + parseInt(tier.count), 0),
        total_traffic: result.rows.reduce((sum, tier) => sum + parseInt(tier.total_traffic || 0), 0),
        aio_coverage: result.rows.reduce((sum, tier) => sum + parseInt(tier.aio_active_count || 0), 0)
      }
    };

    // Cache for 15 minutes
    await redis.setex(cacheKey, 900, JSON.stringify(pyramidData));

    return pyramidData;
  }

  // Auto-classify keywords without tier
  async autoClassifyKeywords(): Promise<{ classified: number; tiers: Record<string, number> }> {
    const query = `
      SELECT id, search_volume, difficulty, cpc 
      FROM keywords 
      WHERE priority_tier IS NULL
    `;
    
    const result = await this.db.query(query);
    const tiers: Record<string, number> = {};
    
    const client = await this.db.connect();
    try {
      await client.query('BEGIN');
      
      for (const keyword of result.rows) {
        const tier = this.classifyKeywordPriority(keyword);
        
        await client.query(
          'UPDATE keywords SET priority_tier = $1, updated_at = NOW() WHERE id = $2',
          [tier, keyword.id]
        );
        
        tiers[tier] = (tiers[tier] || 0) + 1;
      }
      
      await client.query('COMMIT');
      
      // Clear caches
      await this.clearKeywordCaches();
      
      return {
        classified: result.rows.length,
        tiers
      };
    } catch (error) {
      await client.query('ROLLBACK');
      throw error;
    } finally {
      client.release();
    }
  }

  // Keyword classification algorithm
  private classifyKeywordPriority(keyword: {
    search_volume?: number;
    difficulty?: number;
    cpc?: number;
  }): PriorityTier {
    const { search_volume = 0, difficulty = 50, cpc = 0 } = keyword;
    
    // Base classification by search volume
    let tier: PriorityTier = 'P4';
    if (search_volume >= 30000) tier = 'P0';
    else if (search_volume >= 20000) tier = 'P1';
    else if (search_volume >= 15000) tier = 'P2';
    else if (search_volume >= 10000) tier = 'P3';
    
    // Boost for high commercial value
    if (cpc > 5 && difficulty < 50 && tier !== 'P0') {
      const tierMap: Record<string, PriorityTier> = {
        'P1': 'P0',
        'P2': 'P1',
        'P3': 'P2',
        'P4': 'P3'
      };
      tier = tierMap[tier] || tier;
    }
    
    return tier;
  }

  // Clear keyword-related caches
  private async clearKeywordCaches(keywordId?: number): Promise<void> {
    const patterns = [
      'keywords:list:*',
      'keywords:pyramid'
    ];
    
    if (keywordId) {
      patterns.push(`keywords:single:${keywordId}`);
    }
    
    for (const pattern of patterns) {
      const keys = await redis.keys(pattern);
      if (keys.length > 0) {
        await redis.del(...keys);
      }
    }
  }

  // Track keyword performance
  async trackPerformance(keywordId: number, data: {
    impressions: number;
    clicks: number;
    ctr: number;
    position: number;
    aio_appearances?: number;
  }): Promise<void> {
    const query = `
      INSERT INTO keyword_performance (
        keyword_id, date, impressions, clicks, ctr, position, aio_appearances
      ) VALUES ($1, CURRENT_DATE, $2, $3, $4, $5, $6)
      ON CONFLICT (keyword_id, date) DO UPDATE SET
        impressions = EXCLUDED.impressions,
        clicks = EXCLUDED.clicks,
        ctr = EXCLUDED.ctr,
        position = EXCLUDED.position,
        aio_appearances = EXCLUDED.aio_appearances
    `;

    await this.db.query(query, [
      keywordId,
      data.impressions,
      data.clicks,
      data.ctr,
      data.position,
      data.aio_appearances || 0
    ]);

    // Update traffic value if applicable
    if (data.clicks > 0) {
      await this.db.query(
        'UPDATE keywords SET traffic = traffic + $1 WHERE id = $2',
        [data.clicks, keywordId]
      );
    }
  }
}