# PRP: Eufy GEO Platform - Complete Implementation Guide

Generated from: INITIAL.md
Generated at: 2025-09-17
Version: 1.0

## Executive Summary

This PRP provides a comprehensive implementation guide for the Eufy GEO (Generative Engine Optimization) Platform. The system will help Eufy dominate AI-generated search results across Google AIO, YouTube, and Reddit through intelligent keyword management, AI-powered content creation, and real-time performance analytics.

## Project Context

### Business Objectives
- **Primary Goal**: Achieve 40% AI Overview (AIO) coverage for core keywords (>10K searches) within 3 months
- **Traffic Target**: 30% increase in GEO-driven organic traffic
- **Engagement Target**: 25% increase in positive Reddit mentions
- **Conversion Target**: 10% higher conversion rate compared to traditional SEO

### Technical Scope
- Manage 850+ keywords with P0-P4 priority classification
- Support bulk operations for 10,000+ keywords
- Real-time dashboard with <500ms update latency
- Multi-channel content distribution across three platforms
- Automated reporting with ROI attribution

## System Architecture

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend (React)                      │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Keyword    │  │   Content     │  │    Analytics     │  │
│  │  Dashboard  │  │   Editor      │  │    Dashboard     │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                      API Gateway (Express)                    │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │  Keywords   │  │   Content     │  │   Analytics      │  │
│  │  Service    │  │   Service     │  │   Service        │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────┬───────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                     Data Layer                               │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ PostgreSQL  │  │    Redis      │  │   Bull Queue     │  │
│  │  (Primary)  │  │   (Cache)     │  │    (Jobs)        │  │
│  └─────────────┘  └──────────────┘  └──────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────┴───────────────────────────────┐
│                   External Services                          │
│  ┌──────┐ ┌──────┐ ┌────────┐ ┌─────────┐ ┌────────────┐  │
│  │ GSC  │ │ GA4  │ │YouTube │ │ Reddit  │ │SEMrush/    │  │
│  │ API  │ │ API  │ │  API   │ │  API    │ │Ahrefs API  │  │
│  └──────┘ └──────┘ └────────┘ └─────────┘ └────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

#### Frontend
```json
{
  "framework": "React 18.2.0",
  "language": "TypeScript 5.0",
  "ui": "Material-UI 5.14",
  "charts": "ECharts 5.4",
  "state": "Redux Toolkit 1.9",
  "routing": "React Router 6.15",
  "forms": "React Hook Form 7.45",
  "build": "Vite 4.4"
}
```

#### Backend
```json
{
  "runtime": "Node.js 18 LTS",
  "framework": "Express 4.18",
  "language": "TypeScript 5.0",
  "database": "PostgreSQL 15",
  "cache": "Redis 7",
  "queue": "Bull 4.11",
  "validation": "Zod 3.22",
  "auth": "JWT + bcrypt"
}
```

## Module Specifications

### 1. Keyword Management Module

#### Database Schema
```sql
-- Main keywords table
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL UNIQUE,
    search_volume INTEGER NOT NULL DEFAULT 0,
    difficulty DECIMAL(3,1) CHECK (difficulty >= 0 AND difficulty <= 100),
    cpc DECIMAL(10,2) DEFAULT 0,
    competition DECIMAL(3,2) CHECK (competition >= 0 AND competition <= 1),
    priority_tier VARCHAR(2) CHECK (priority_tier IN ('P0', 'P1', 'P2', 'P3', 'P4')),
    aio_status VARCHAR(20) DEFAULT 'monitoring' CHECK (aio_status IN ('active', 'inactive', 'monitoring')),
    current_rank INTEGER,
    previous_rank INTEGER,
    traffic INTEGER DEFAULT 0,
    traffic_value DECIMAL(10,2) DEFAULT 0,
    product_category VARCHAR(50),
    user_intent VARCHAR(20) CHECK (user_intent IN ('informational', 'transactional', 'navigational', 'commercial')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Performance tracking
CREATE TABLE keyword_performance (
    id SERIAL PRIMARY KEY,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    date DATE NOT NULL,
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5,2),
    position DECIMAL(4,1),
    aio_appearances INTEGER DEFAULT 0,
    traffic_value DECIMAL(10,2),
    UNIQUE(keyword_id, date)
);

-- Indexes for performance
CREATE INDEX idx_keywords_priority_volume ON keywords(priority_tier, search_volume DESC);
CREATE INDEX idx_keywords_aio_active ON keywords(aio_status) WHERE aio_status = 'active';
CREATE INDEX idx_keywords_category ON keywords(product_category);
CREATE INDEX idx_keywords_updated ON keywords(updated_at DESC);
CREATE INDEX idx_perf_date_keyword ON keyword_performance(date DESC, keyword_id);
```

#### API Endpoints
```typescript
// Keyword Management API
GET    /api/keywords                    // List with pagination and filters
GET    /api/keywords/:id               // Get single keyword details
POST   /api/keywords                   // Create new keyword
PUT    /api/keywords/:id               // Update keyword
DELETE /api/keywords/:id               // Delete keyword
POST   /api/keywords/bulk-import       // Import CSV (up to 10k keywords)
GET    /api/keywords/export            // Export filtered keywords
POST   /api/keywords/classify          // Auto-classify priorities
GET    /api/keywords/pyramid           // Get pyramid visualization data
GET    /api/keywords/:id/history       // Get historical performance
POST   /api/keywords/aio-check         // Check AIO status for keywords
```

#### Frontend Components
```typescript
// Main dashboard component structure
<KeywordDashboard>
  <KeywordFilters />
  <KeywordStats />
  <PyramidChart />
  <KeywordDataGrid />
  <BulkActions />
</KeywordDashboard>

// Key features
- Real-time filtering with debouncing
- Virtualized data grid for 10k+ rows
- Drag-and-drop CSV import
- Batch operations with progress
- Export with current filters
```

### 2. Content Management Module

#### Database Schema
```sql
-- Content table
CREATE TABLE content (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    slug VARCHAR(255) UNIQUE,
    type VARCHAR(50) CHECK (type IN ('blog', 'video', 'reddit_post')),
    status VARCHAR(20) DEFAULT 'draft' CHECK (status IN ('draft', 'review', 'approved', 'published', 'archived')),
    content_brief TEXT,
    content_body TEXT,
    meta_title VARCHAR(255),
    meta_description TEXT,
    target_keywords INTEGER[],
    author_id INTEGER REFERENCES users(id),
    reviewer_id INTEGER REFERENCES users(id),
    published_at TIMESTAMP,
    version INTEGER DEFAULT 1,
    ai_generated BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Content-keyword relationship
CREATE TABLE content_keywords (
    content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
    keyword_id INTEGER REFERENCES keywords(id) ON DELETE CASCADE,
    is_primary BOOLEAN DEFAULT false,
    relevance_score DECIMAL(3,2),
    PRIMARY KEY (content_id, keyword_id)
);

-- Content versions for history
CREATE TABLE content_versions (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    title VARCHAR(255),
    content_body TEXT,
    changed_by INTEGER REFERENCES users(id),
    change_summary TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Workflow tracking
CREATE TABLE content_workflow (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES content(id) ON DELETE CASCADE,
    from_status VARCHAR(20),
    to_status VARCHAR(20),
    user_id INTEGER REFERENCES users(id),
    comment TEXT,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### API Endpoints
```typescript
// Content Management API
GET    /api/content                    // List content with filters
GET    /api/content/:id               // Get content details
POST   /api/content                   // Create new content
PUT    /api/content/:id               // Update content
DELETE /api/content/:id               // Delete content
POST   /api/content/:id/publish       // Publish content
POST   /api/content/:id/review        // Submit for review
GET    /api/content/:id/versions      // Get version history
POST   /api/content/ai-generate       // Generate content with AI
GET    /api/content/calendar          // Get publishing calendar
POST   /api/content/:id/analyze       // Analyze SEO optimization
```

#### Content Editor Features
```typescript
// GEO-optimized editor with real-time validation
<ContentEditor>
  <EditorToolbar />
  <RichTextEditor />
  <GEOChecklist />
  <AIAssistant />
  <PreviewPane />
</ContentEditor>

// Validation checklist
- Keyword density (1-3%)
- H1/H2/H3 structure
- Meta title/description length
- Internal/external links
- Image alt texts
- Readability score
- AIO optimization factors
```

### 3. Analytics Module

#### Database Schema
```sql
-- Analytics aggregation tables
CREATE TABLE daily_analytics (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    keyword_id INTEGER REFERENCES keywords(id),
    source VARCHAR(50), -- 'google', 'youtube', 'reddit'
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    ctr DECIMAL(5,2),
    position DECIMAL(4,1),
    aio_appearances INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    UNIQUE(date, keyword_id, source)
);

-- ROI tracking
CREATE TABLE roi_attribution (
    id SERIAL PRIMARY KEY,
    content_id INTEGER REFERENCES content(id),
    keyword_id INTEGER REFERENCES keywords(id),
    channel VARCHAR(50),
    sessions INTEGER DEFAULT 0,
    conversions INTEGER DEFAULT 0,
    revenue DECIMAL(10,2) DEFAULT 0,
    cost DECIMAL(10,2) DEFAULT 0,
    roi DECIMAL(5,2) GENERATED ALWAYS AS ((revenue - cost) / NULLIF(cost, 0) * 100) STORED,
    date DATE NOT NULL
);

-- Report configurations
CREATE TABLE report_configs (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type VARCHAR(50), -- 'weekly', 'monthly', 'quarterly'
    metrics JSONB,
    filters JSONB,
    recipients TEXT[],
    schedule_cron VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT NOW()
);
```

#### Analytics Dashboard Components
```typescript
// Main analytics dashboard
<AnalyticsDashboard>
  <KPICards>
    <AIOCoverageCard />
    <TrafficGrowthCard />
    <ConversionRateCard />
    <ROICard />
  </KPICards>
  <Charts>
    <TrafficTrendChart />
    <KeywordPerformanceChart />
    <ChannelDistributionChart />
    <ConversionFunnelChart />
  </Charts>
  <DataTables>
    <TopPerformingKeywords />
    <ContentPerformance />
    <CompetitorComparison />
  </DataTables>
</AnalyticsDashboard>
```

### 4. Integration Services

#### External API Integrations
```typescript
// Google Search Console
class GSCService {
  async getSearchAnalytics(startDate: Date, endDate: Date) {
    // Implementation with auth, rate limiting, error handling
  }
  
  async getURLInspection(url: string) {
    // Check indexing status
  }
}

// Google Analytics 4
class GA4Service {
  async getTrafficData(dimensions: string[], metrics: string[]) {
    // Fetch traffic and conversion data
  }
  
  async getEcommerceData(dateRange: DateRange) {
    // Get revenue attribution
  }
}

// YouTube Analytics
class YouTubeService {
  async getVideoMetrics(videoIds: string[]) {
    // Views, watch time, engagement
  }
  
  async getSearchTerms() {
    // How users find videos
  }
}

// Reddit API
class RedditService {
  async searchMentions(keywords: string[]) {
    // Find brand/product mentions
  }
  
  async postContent(subreddit: string, content: RedditPost) {
    // Managed posting with rate limits
  }
}

// SEMrush/Ahrefs
class SEOToolsService {
  async getKeywordData(keywords: string[]) {
    // Volume, difficulty, SERP features
  }
  
  async getCompetitorKeywords(domain: string) {
    // Competitive analysis
  }
}
```

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
1. **Infrastructure Setup**
   - Docker environment configuration
   - Database schema creation and migration
   - Redis and Bull queue setup
   - Basic CI/CD pipeline

2. **Core Backend**
   - Authentication system with JWT
   - Keyword management API
   - Basic content CRUD operations
   - File upload handling

3. **Frontend Scaffold**
   - React app structure
   - Routing configuration
   - Redux store setup
   - Material-UI theming

### Phase 2: Keyword Management (Weeks 3-4)
1. **Backend Features**
   - CSV import with validation
   - Auto-classification algorithm
   - Performance data aggregation
   - Caching layer implementation

2. **Frontend Components**
   - Keyword dashboard UI
   - Pyramid visualization
   - Data grid with filtering
   - Bulk operations interface

3. **Integration**
   - SEMrush/Ahrefs API connection
   - Initial GSC integration
   - Background job processing

### Phase 3: Content System (Weeks 5-6)
1. **Content Backend**
   - Workflow engine
   - Version control system
   - AI integration setup
   - Publishing pipeline

2. **Editor Development**
   - Rich text editor
   - GEO validation checklist
   - Real-time preview
   - Collaboration features

3. **Channel Distribution**
   - Multi-channel publishing
   - Content calendar
   - Scheduling system

### Phase 4: Analytics & Reporting (Weeks 7-8)
1. **Data Pipeline**
   - ETL processes for external data
   - Analytics aggregation jobs
   - Real-time data streaming
   - ROI calculation engine

2. **Dashboard Creation**
   - KPI visualization components
   - Interactive charts
   - Custom report builder
   - Export functionality

3. **Automation**
   - Scheduled reports
   - Alert system
   - Performance monitoring

### Phase 5: Optimization & Launch (Weeks 9-10)
1. **Performance Optimization**
   - Query optimization
   - Caching strategies
   - Frontend bundle optimization
   - Load testing

2. **Security Hardening**
   - Penetration testing
   - Security audit
   - GDPR compliance
   - Rate limiting

3. **Launch Preparation**
   - User documentation
   - Training materials
   - Deployment procedures
   - Monitoring setup

## Code Implementation Details

### Keyword Priority Classification Algorithm
```typescript
export function classifyKeywordPriority(
  keyword: KeywordInput
): PriorityTier {
  const { search_volume, difficulty, cpc, aio_status } = keyword;
  
  // Base classification by search volume
  let tier: PriorityTier = 'P4';
  if (search_volume >= 30000) tier = 'P0';
  else if (search_volume >= 20000) tier = 'P1';
  else if (search_volume >= 15000) tier = 'P2';
  else if (search_volume >= 10000) tier = 'P3';
  
  // Boost for active AIO
  if (aio_status === 'active' && tier !== 'P0') {
    tier = upgradeTier(tier);
  }
  
  // Boost for high commercial value
  const commercialScore = calculateCommercialScore(cpc, difficulty);
  if (commercialScore > 0.8 && tier !== 'P0') {
    tier = upgradeTier(tier);
  }
  
  // Special handling for branded terms
  if (isBrandedKeyword(keyword.keyword)) {
    tier = Math.min(tier, 'P1') as PriorityTier;
  }
  
  return tier;
}

function calculateCommercialScore(cpc: number, difficulty: number): number {
  // High CPC with low difficulty = high commercial value
  const cpcScore = Math.min(cpc / 10, 1); // Normalize to 0-1
  const difficultyScore = 1 - (difficulty / 100); // Inverse, 0-1
  return (cpcScore * 0.6 + difficultyScore * 0.4);
}

function isBrandedKeyword(keyword: string): boolean {
  const brandTerms = ['eufy', 'anker'];
  return brandTerms.some(term => 
    keyword.toLowerCase().includes(term)
  );
}
```

### Redis Caching Strategy
```typescript
export class CacheManager {
  private redis: Redis;
  
  // Cache key patterns
  private readonly KEYS = {
    KEYWORDS: (filters: string) => `keywords:list:${filters}`,
    KEYWORD: (id: number) => `keywords:single:${id}`,
    PYRAMID: () => 'keywords:pyramid',
    ANALYTICS: (date: string) => `analytics:daily:${date}`,
    USER_SESSION: (userId: number) => `session:${userId}`
  };
  
  // TTL configurations (in seconds)
  private readonly TTL = {
    KEYWORDS_LIST: 300,      // 5 minutes
    KEYWORD_SINGLE: 600,     // 10 minutes
    PYRAMID: 900,            // 15 minutes
    ANALYTICS: 3600,         // 1 hour
    USER_SESSION: 86400      // 24 hours
  };
  
  async getOrSet<T>(
    key: string,
    factory: () => Promise<T>,
    ttl: number
  ): Promise<T> {
    try {
      // Try cache first
      const cached = await this.redis.get(key);
      if (cached) {
        return JSON.parse(cached);
      }
      
      // Cache miss - get from source
      const value = await factory();
      
      // Set in cache with TTL
      await this.redis.setex(
        key, 
        ttl, 
        JSON.stringify(value)
      );
      
      return value;
    } catch (error) {
      // Log error but don't fail the request
      console.error('Cache error:', error);
      return factory(); // Fallback to source
    }
  }
  
  async invalidatePattern(pattern: string): Promise<void> {
    const keys = await this.redis.keys(pattern);
    if (keys.length > 0) {
      await this.redis.del(...keys);
    }
  }
  
  // Invalidate related caches when data changes
  async invalidateKeywordCaches(keywordId?: number): Promise<void> {
    const patterns = [
      'keywords:list:*',
      'keywords:pyramid'
    ];
    
    if (keywordId) {
      patterns.push(`keywords:single:${keywordId}`);
    }
    
    await Promise.all(
      patterns.map(pattern => this.invalidatePattern(pattern))
    );
  }
}
```

### Bulk Import with Progress Tracking
```typescript
export class BulkImportService {
  constructor(
    private db: Pool,
    private queue: Queue,
    private eventEmitter: EventEmitter
  ) {}
  
  async importKeywords(
    file: Express.Multer.File,
    userId: number
  ): Promise<ImportResult> {
    // Create import job
    const job = await this.queue.add('keyword-import', {
      filePath: file.path,
      fileName: file.originalname,
      userId,
      uploadedAt: new Date()
    });
    
    // Return job ID for progress tracking
    return {
      jobId: job.id as string,
      status: 'processing'
    };
  }
  
  // Process import job
  @Process('keyword-import')
  async processImport(job: Job<ImportJobData>) {
    const { filePath, userId } = job.data;
    const results = {
      total: 0,
      imported: 0,
      updated: 0,
      errors: [] as ImportError[]
    };
    
    // Parse CSV with streaming
    const stream = fs.createReadStream(filePath)
      .pipe(csv())
      .on('data', async (row) => {
        stream.pause();
        results.total++;
        
        try {
          const keyword = await this.processKeywordRow(row);
          const result = await this.upsertKeyword(keyword);
          
          if (result.created) {
            results.imported++;
          } else {
            results.updated++;
          }
          
          // Update progress
          const progress = Math.round(
            (results.imported + results.updated) / results.total * 100
          );
          await job.progress(progress);
          
          // Emit real-time progress
          this.eventEmitter.emit(`import:${job.id}:progress`, {
            progress,
            ...results
          });
          
        } catch (error) {
          results.errors.push({
            row: results.total,
            error: error.message,
            data: row
          });
        }
        
        stream.resume();
      });
    
    return new Promise((resolve, reject) => {
      stream.on('end', () => {
        // Clean up temp file
        fs.unlinkSync(filePath);
        
        // Final event
        this.eventEmitter.emit(`import:${job.id}:complete`, results);
        
        resolve(results);
      });
      
      stream.on('error', reject);
    });
  }
  
  private async processKeywordRow(row: any): Promise<KeywordData> {
    // Validate and transform CSV row
    const schema = z.object({
      keyword: z.string().min(1).max(255),
      search_volume: z.coerce.number().default(0),
      difficulty: z.coerce.number().min(0).max(100).optional(),
      cpc: z.coerce.number().optional(),
      category: z.string().optional()
    });
    
    const validated = schema.parse(row);
    
    // Auto-classify
    const priority_tier = classifyKeywordPriority(validated);
    
    return {
      ...validated,
      priority_tier
    };
  }
}
```

### Real-time Dashboard Updates
```typescript
// WebSocket service for real-time updates
export class RealtimeService {
  private io: Server;
  private rooms = new Map<string, Set<string>>();
  
  constructor(httpServer: http.Server) {
    this.io = new Server(httpServer, {
      cors: {
        origin: process.env.FRONTEND_URL,
        credentials: true
      }
    });
    
    this.setupHandlers();
  }
  
  private setupHandlers() {
    this.io.on('connection', (socket) => {
      console.log('Client connected:', socket.id);
      
      // Join dashboard room
      socket.on('join:dashboard', (userId: string) => {
        socket.join(`dashboard:${userId}`);
        this.trackUserRoom(socket.id, `dashboard:${userId}`);
      });
      
      // Subscribe to keyword updates
      socket.on('subscribe:keywords', (filters: any) => {
        const room = `keywords:${JSON.stringify(filters)}`;
        socket.join(room);
        this.trackUserRoom(socket.id, room);
      });
      
      // Clean up on disconnect
      socket.on('disconnect', () => {
        this.cleanupUser(socket.id);
      });
    });
  }
  
  // Emit updates to relevant clients
  emitKeywordUpdate(keyword: Keyword) {
    // Notify all dashboard users
    this.io.to('dashboard:*').emit('keyword:updated', keyword);
    
    // Notify specific filtered views
    this.rooms.forEach((_, room) => {
      if (room.startsWith('keywords:')) {
        const filters = JSON.parse(room.split(':')[1]);
        if (this.matchesFilters(keyword, filters)) {
          this.io.to(room).emit('keyword:updated', keyword);
        }
      }
    });
  }
  
  emitAnalyticsUpdate(data: AnalyticsUpdate) {
    this.io.emit('analytics:updated', data);
  }
  
  emitImportProgress(jobId: string, progress: ImportProgress) {
    this.io.emit(`import:${jobId}:progress`, progress);
  }
}

// Frontend React hook for real-time updates
export function useRealtimeUpdates<T>(
  event: string,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null);
  const socketRef = useRef<Socket>();
  
  useEffect(() => {
    // Connect to WebSocket
    socketRef.current = io(process.env.REACT_APP_WS_URL, {
      withCredentials: true
    });
    
    // Subscribe to event
    socketRef.current.on(event, (newData: T) => {
      setData(newData);
    });
    
    // Cleanup
    return () => {
      socketRef.current?.disconnect();
    };
  }, dependencies);
  
  return data;
}

// Usage in component
function KeywordDashboard() {
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  
  // Subscribe to real-time updates
  const keywordUpdate = useRealtimeUpdates<Keyword>('keyword:updated');
  
  useEffect(() => {
    if (keywordUpdate) {
      // Update local state
      setKeywords(prev => {
        const index = prev.findIndex(k => k.id === keywordUpdate.id);
        if (index >= 0) {
          const updated = [...prev];
          updated[index] = keywordUpdate;
          return updated;
        }
        return [...prev, keywordUpdate];
      });
    }
  }, [keywordUpdate]);
  
  return <DataGrid data={keywords} />;
}
```

## Testing Strategy

### Unit Tests
```typescript
// Keyword classification tests
describe('KeywordClassification', () => {
  it('should classify by volume correctly', () => {
    expect(classifyKeywordPriority({ 
      search_volume: 35000 
    })).toBe('P0');
    
    expect(classifyKeywordPriority({ 
      search_volume: 25000 
    })).toBe('P1');
  });
  
  it('should boost for active AIO', () => {
    expect(classifyKeywordPriority({
      search_volume: 25000,
      aio_status: 'active'
    })).toBe('P0'); // Boosted from P1
  });
  
  it('should consider commercial value', () => {
    expect(classifyKeywordPriority({
      search_volume: 18000,
      cpc: 8.50,
      difficulty: 35
    })).toBe('P1'); // Boosted from P2
  });
});

// API endpoint tests
describe('Keywords API', () => {
  it('should filter keywords correctly', async () => {
    const response = await request(app)
      .get('/api/keywords')
      .query({ priority_tier: 'P0', min_volume: 30000 });
    
    expect(response.status).toBe(200);
    expect(response.body.keywords).toHaveLength(8);
    expect(
      response.body.keywords.every(k => k.priority_tier === 'P0')
    ).toBe(true);
  });
  
  it('should handle bulk import', async () => {
    const response = await request(app)
      .post('/api/keywords/bulk-import')
      .attach('file', 'test-data/keywords.csv')
      .set('Authorization', `Bearer ${authToken}`);
    
    expect(response.status).toBe(200);
    expect(response.body.jobId).toBeDefined();
  });
});
```

### Integration Tests
```typescript
// End-to-end workflow tests
describe('Content Publishing Workflow', () => {
  it('should complete full publishing cycle', async () => {
    // 1. Create content
    const content = await createContent({
      title: 'Test Content',
      target_keywords: [1, 2, 3]
    });
    
    // 2. Submit for review
    await submitForReview(content.id);
    
    // 3. Approve content
    await approveContent(content.id);
    
    // 4. Publish to channels
    const published = await publishContent(content.id, {
      channels: ['google', 'youtube']
    });
    
    // 5. Verify analytics tracking
    await waitFor(async () => {
      const analytics = await getContentAnalytics(content.id);
      expect(analytics.impressions).toBeGreaterThan(0);
    });
  });
});
```

### Performance Tests
```typescript
// Load testing with k6
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [
    { duration: '2m', target: 100 },  // Ramp up
    { duration: '5m', target: 100 },  // Stay at 100 users
    { duration: '2m', target: 200 },  // Spike to 200
    { duration: '5m', target: 200 },  // Stay at 200
    { duration: '2m', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests under 2s
    http_req_failed: ['rate<0.1'],     // Error rate under 10%
  },
};

export default function() {
  // Test keyword search
  const searchResponse = http.get(
    'http://localhost:5001/api/keywords?priority_tier=P0'
  );
  
  check(searchResponse, {
    'search status is 200': (r) => r.status === 200,
    'search response time < 2s': (r) => r.timings.duration < 2000,
  });
  
  // Test analytics dashboard
  const analyticsResponse = http.get(
    'http://localhost:5001/api/analytics/dashboard'
  );
  
  check(analyticsResponse, {
    'analytics status is 200': (r) => r.status === 200,
    'analytics response time < 2s': (r) => r.timings.duration < 2000,
  });
}
```

## Security Implementation

### Authentication & Authorization
```typescript
// JWT middleware with role-based access
export const authenticate = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const token = req.headers.authorization?.split(' ')[1];
    if (!token) {
      return res.status(401).json({ error: 'No token provided' });
    }
    
    const payload = jwt.verify(token, process.env.JWT_SECRET) as JWTPayload;
    const user = await userService.findById(payload.userId);
    
    if (!user) {
      return res.status(401).json({ error: 'Invalid token' });
    }
    
    req.user = user;
    next();
  } catch (error) {
    return res.status(401).json({ error: 'Invalid token' });
  }
};

// Role-based access control
export const authorize = (...roles: Role[]) => {
  return (req: Request, res: Response, next: NextFunction) => {
    if (!req.user) {
      return res.status(401).json({ error: 'Not authenticated' });
    }
    
    if (!roles.includes(req.user.role)) {
      return res.status(403).json({ error: 'Insufficient permissions' });
    }
    
    next();
  };
};

// Usage
router.post(
  '/api/keywords/bulk-import',
  authenticate,
  authorize('admin', 'strategist'),
  uploadMiddleware,
  keywordController.bulkImport
);
```

### API Rate Limiting
```typescript
// Rate limiting configuration
export const rateLimiters = {
  // General API limit
  api: rateLimit({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // 100 requests per window
    message: 'Too many requests, please try again later',
    standardHeaders: true,
    legacyHeaders: false,
  }),
  
  // Strict limit for expensive operations
  expensive: rateLimit({
    windowMs: 60 * 60 * 1000, // 1 hour
    max: 10, // 10 requests per hour
    skipSuccessfulRequests: false,
  }),
  
  // Auth endpoints
  auth: rateLimit({
    windowMs: 15 * 60 * 1000,
    max: 5, // 5 login attempts per 15 minutes
    skipFailedRequests: false,
  })
};

// Apply rate limiting
app.use('/api/', rateLimiters.api);
app.use('/api/auth/login', rateLimiters.auth);
app.use('/api/keywords/bulk-import', rateLimiters.expensive);
```

## Deployment Configuration

### Docker Setup
```dockerfile
# Backend Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production

FROM node:18-alpine
WORKDIR /app
COPY --from=builder /app/node_modules ./node_modules
COPY . .
RUN npm run build
EXPOSE 5001
CMD ["node", "dist/server.js"]

# Frontend Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Kubernetes Configuration
```yaml
# Deployment configuration
apiVersion: apps/v1
kind: Deployment
metadata:
  name: geo-platform-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: geo-platform-api
  template:
    metadata:
      labels:
        app: geo-platform-api
    spec:
      containers:
      - name: api
        image: eufy-geo-platform:latest
        ports:
        - containerPort: 5001
        env:
        - name: NODE_ENV
          value: "production"
        - name: DB_HOST
          valueFrom:
            secretKeyRef:
              name: db-secret
              key: host
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
        livenessProbe:
          httpGet:
            path: /health
            port: 5001
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 5001
          initialDelaySeconds: 5
          periodSeconds: 5

---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: geo-platform-api-hpa
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: geo-platform-api
  minReplicas: 3
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  - type: Resource
    resource:
      name: memory
      target:
        type: Utilization
        averageUtilization: 80
```

## Monitoring & Observability

### Application Monitoring
```typescript
// Prometheus metrics
import { register, Counter, Histogram, Gauge } from 'prom-client';

// Request metrics
const httpRequestDuration = new Histogram({
  name: 'http_request_duration_seconds',
  help: 'Duration of HTTP requests in seconds',
  labelNames: ['method', 'route', 'status_code'],
  buckets: [0.1, 0.5, 1, 2, 5]
});

const httpRequestTotal = new Counter({
  name: 'http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code']
});

// Business metrics
const keywordsImported = new Counter({
  name: 'keywords_imported_total',
  help: 'Total number of keywords imported',
  labelNames: ['source']
});

const aioActiveCoverage = new Gauge({
  name: 'aio_active_coverage_ratio',
  help: 'Ratio of keywords with active AIO',
  labelNames: ['priority_tier']
});

// Middleware to track metrics
export const metricsMiddleware = (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  const start = Date.now();
  
  res.on('finish', () => {
    const duration = (Date.now() - start) / 1000;
    const labels = {
      method: req.method,
      route: req.route?.path || 'unknown',
      status_code: res.statusCode.toString()
    };
    
    httpRequestDuration.observe(labels, duration);
    httpRequestTotal.inc(labels);
  });
  
  next();
};

// Metrics endpoint
app.get('/metrics', (req, res) => {
  res.set('Content-Type', register.contentType);
  res.end(register.metrics());
});
```

### Logging Strategy
```typescript
// Structured logging with Winston
import winston from 'winston';

const logger = winston.createLogger({
  level: process.env.LOG_LEVEL || 'info',
  format: winston.format.combine(
    winston.format.timestamp(),
    winston.format.errors({ stack: true }),
    winston.format.json()
  ),
  defaultMeta: { 
    service: 'geo-platform',
    environment: process.env.NODE_ENV
  },
  transports: [
    // Console for development
    new winston.transports.Console({
      format: winston.format.simple()
    }),
    // File for production
    new winston.transports.File({ 
      filename: 'error.log', 
      level: 'error' 
    }),
    new winston.transports.File({ 
      filename: 'combined.log' 
    })
  ]
});

// Log important business events
export const logBusinessEvent = (
  event: string,
  data: any,
  userId?: number
) => {
  logger.info('business_event', {
    event,
    data,
    userId,
    timestamp: new Date().toISOString()
  });
};

// Usage
logBusinessEvent('keyword_import_completed', {
  imported: 1500,
  updated: 300,
  errors: 5,
  duration: 45.2
}, req.user.id);
```

## Success Metrics & KPIs

### Technical Metrics
- **Performance**: 95% of API requests < 2 seconds
- **Availability**: 99.9% uptime (8.76 hours downtime/year)
- **Error Rate**: < 0.1% 5xx errors
- **Throughput**: Support 10,000 concurrent users

### Business Metrics
- **AIO Coverage**: 40% of P0 keywords with active AIO
- **Traffic Growth**: 30% increase in GEO traffic within 3 months
- **Content Velocity**: 50+ pieces of optimized content per week
- **ROI**: 5:1 return on investment within 6 months

### User Satisfaction
- **Adoption Rate**: 90% of target users actively using platform
- **Task Completion**: 95% successful task completion rate
- **Response Time**: < 24 hour response to user feedback
- **Training Time**: < 2 hours to onboard new users

## Conclusion

This PRP provides a complete blueprint for implementing the Eufy GEO Platform. The modular architecture allows for parallel development while maintaining system coherence. Focus on delivering the MVP features first, then iteratively add advanced capabilities based on user feedback and business priorities.

The success of this platform depends on:
1. Fast, reliable data processing
2. Intuitive user interfaces
3. Accurate analytics and attribution
4. Seamless integration with external services
5. Continuous optimization based on results

With proper execution, this platform will position Eufy as a leader in AI-driven search optimization.