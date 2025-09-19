import Redis from 'ioredis';

// Example Redis caching patterns for high-performance
// Demonstrates:
// 1. Cache-aside pattern
// 2. Cache invalidation strategies
// 3. Batch operations
// 4. Pub/Sub for real-time updates

export class CacheService {
  private redis: Redis;
  private defaultTTL = 300; // 5 minutes

  constructor() {
    this.redis = new Redis({
      host: process.env.REDIS_HOST || 'localhost',
      port: parseInt(process.env.REDIS_PORT || '6379'),
      maxRetriesPerRequest: 3,
      enableReadyCheck: true,
      lazyConnect: true
    });
  }

  // Cache-aside pattern with automatic serialization
  async getOrSet<T>(
    key: string, 
    factory: () => Promise<T>, 
    ttl: number = this.defaultTTL
  ): Promise<T> {
    // Try cache first
    const cached = await this.redis.get(key);
    if (cached) {
      return JSON.parse(cached);
    }

    // Cache miss - fetch from source
    const value = await factory();
    
    // Store in cache
    await this.redis.setex(key, ttl, JSON.stringify(value));
    
    return value;
  }

  // Batch get with pipeline
  async getBatch(keys: string[]): Promise<(string | null)[]> {
    const pipeline = this.redis.pipeline();
    keys.forEach(key => pipeline.get(key));
    const results = await pipeline.exec();
    return results?.map(([err, val]) => val as string | null) || [];
  }

  // Pattern-based cache invalidation
  async invalidatePattern(pattern: string): Promise<void> {
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }

  // Distributed cache warming
  async warmCache(data: Array<{ key: string; value: any; ttl?: number }>): Promise<void> {
    const pipeline = this.redis.pipeline();
    
    data.forEach(({ key, value, ttl = this.defaultTTL }) => {
      pipeline.setex(key, ttl, JSON.stringify(value));
    });
    
    await pipeline.exec();
  }

  // Real-time cache invalidation via pub/sub
  subscribeToInvalidation(callback: (pattern: string) => void): void {
    const subscriber = new Redis();
    subscriber.subscribe('cache:invalidate');
    
    subscriber.on('message', (channel, pattern) => {
      callback(pattern);
    });
  }

  publishInvalidation(pattern: string): void {
    this.redis.publish('cache:invalidate', pattern);
  }
}

// Usage examples:
export const cacheService = new CacheService();

// Example 1: Cache keywords with automatic fetch
export async function getCachedKeywords(filters: any) {
  return cacheService.getOrSet(
    `keywords:${JSON.stringify(filters)}`,
    async () => {
      // Expensive database query
      return db.query('SELECT * FROM keywords WHERE ...');
    },
    600 // 10 minutes for keyword data
  );
}

// Example 2: Invalidate all keyword caches when data changes
export async function invalidateKeywordCache() {
  await cacheService.invalidatePattern('keywords:*');
  cacheService.publishInvalidation('keywords:*');
}