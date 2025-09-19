# PRP: Keyword Management Module

## Component Overview
Build a comprehensive keyword management system that handles 850+ keywords with intelligent classification, real-time monitoring, and strategic prioritization for the Eufy GEO platform.

## Technical Specifications

### Database Schema
```sql
-- Keywords table
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL UNIQUE,
    search_volume INTEGER,
    difficulty DECIMAL(3,1),
    cpc DECIMAL(10,2),
    competition DECIMAL(3,2),
    priority_tier VARCHAR(2), -- P0, P1, P2, P3, P4
    aio_status VARCHAR(20), -- 'active', 'inactive', 'monitoring'
    current_rank INTEGER,
    previous_rank INTEGER,
    traffic INTEGER,
    traffic_value DECIMAL(10,2),
    product_category VARCHAR(50),
    user_intent VARCHAR(20), -- 'informational', 'transactional', 'navigational'
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Keyword history for tracking changes
CREATE TABLE keyword_history (
    id SERIAL PRIMARY KEY,
    keyword_id INTEGER REFERENCES keywords(id),
    search_volume INTEGER,
    rank INTEGER,
    aio_status VARCHAR(20),
    traffic INTEGER,
    recorded_at TIMESTAMP DEFAULT NOW()
);

-- Tags for flexible categorization
CREATE TABLE keyword_tags (
    keyword_id INTEGER REFERENCES keywords(id),
    tag VARCHAR(50),
    PRIMARY KEY (keyword_id, tag)
);
```

### API Endpoints
```typescript
// Keyword Management API
GET    /api/keywords                 // List with filters & pagination
GET    /api/keywords/:id            // Get single keyword details
POST   /api/keywords                // Create new keyword
PUT    /api/keywords/:id            // Update keyword
DELETE /api/keywords/:id            // Delete keyword
POST   /api/keywords/bulk-import    // Import CSV/JSON
GET    /api/keywords/export         // Export to CSV/JSON
GET    /api/keywords/analytics      // Aggregate analytics
POST   /api/keywords/classify       // Auto-classify keywords
GET    /api/keywords/pyramid        // Get pyramid visualization data
```

### Frontend Components

#### 1. Keyword Dashboard
```typescript
interface KeywordDashboardProps {
    filters: KeywordFilters;
    onFilterChange: (filters: KeywordFilters) => void;
    onKeywordSelect: (keyword: Keyword) => void;
}

// Features:
// - Search bar with autocomplete
// - Filter panels (tier, status, category, intent)
// - Sortable data grid
// - Bulk actions toolbar
// - Quick stats cards
```

#### 2. Pyramid Visualization
```typescript
interface PyramidVisualizationProps {
    keywords: Keyword[];
    onTierClick: (tier: string) => void;
}

// ECharts configuration for pyramid
const pyramidOption = {
    series: [{
        type: 'funnel',
        data: [
            { value: p0Count, name: 'P0: Core (>30K)' },
            { value: p1Count, name: 'P1: High (20-30K)' },
            { value: p2Count, name: 'P2: Medium (15-20K)' },
            { value: p3Count, name: 'P3: Low (10-15K)' },
            { value: p4Count, name: 'P4: Long-tail (<10K)' }
        ]
    }]
};
```

#### 3. Import/Export Interface
```typescript
interface ImportExportProps {
    onImport: (file: File, mapping: FieldMapping) => void;
    onExport: (format: 'csv' | 'json', filters?: KeywordFilters) => void;
}

// Features:
// - Drag & drop file upload
// - Column mapping interface
// - Preview imported data
// - Validation results display
// - Progress tracking
```

### Business Logic

#### Priority Classification Algorithm
```typescript
function classifyKeywordPriority(keyword: Keyword): string {
    const { search_volume, difficulty, cpc, aio_status } = keyword;
    
    // Base classification by search volume
    let tier = 'P4';
    if (search_volume >= 30000) tier = 'P0';
    else if (search_volume >= 20000) tier = 'P1';
    else if (search_volume >= 15000) tier = 'P2';
    else if (search_volume >= 10000) tier = 'P3';
    
    // Boost priority if AIO is active
    if (aio_status === 'active' && tier !== 'P0') {
        tier = upgradeeTier(tier);
    }
    
    // Consider commercial value
    if (cpc > 5 && difficulty < 50) {
        tier = upgradeTier(tier);
    }
    
    return tier;
}
```

#### AIO Status Monitoring
```typescript
async function updateAIOStatus(keywords: Keyword[]): Promise<void> {
    const batchSize = 10;
    
    for (let i = 0; i < keywords.length; i += batchSize) {
        const batch = keywords.slice(i, i + batchSize);
        
        const results = await Promise.all(
            batch.map(keyword => checkAIOStatus(keyword))
        );
        
        await updateKeywordStatuses(results);
        
        // Rate limiting
        await delay(1000);
    }
}

async function checkAIOStatus(keyword: Keyword): Promise<AIOResult> {
    // Integration with SERP API or web scraping
    const serpData = await fetchSERPData(keyword.keyword);
    
    return {
        keyword_id: keyword.id,
        aio_active: serpData.hasAIOverview,
        aio_content: serpData.aiContent,
        checked_at: new Date()
    };
}
```

### Integration Points

#### 1. External APIs
```typescript
// SEMrush Integration
class SEMrushClient {
    async getKeywordData(keywords: string[]): Promise<KeywordData[]> {
        const response = await fetch(`${SEMRUSH_API}/keywords`, {
            method: 'POST',
            headers: { 'Api-Key': process.env.SEMRUSH_API_KEY },
            body: JSON.stringify({ keywords })
        });
        return response.json();
    }
}

// Google Search Console
class GSCClient {
    async getSearchAnalytics(startDate: Date, endDate: Date): Promise<SearchData[]> {
        const auth = await authorize();
        const response = await searchConsole.searchanalytics.query({
            siteUrl: SITE_URL,
            startDate: startDate.toISOString(),
            endDate: endDate.toISOString(),
            dimensions: ['query'],
            metrics: ['clicks', 'impressions', 'ctr', 'position']
        });
        return response.data.rows;
    }
}
```

#### 2. Internal Services
```typescript
// Content Service Integration
interface ContentServiceClient {
    getContentByKeyword(keyword_id: number): Promise<Content[]>;
    getKeywordCoverage(keyword_ids: number[]): Promise<CoverageStats>;
}

// Analytics Service Integration
interface AnalyticsServiceClient {
    getKeywordPerformance(keyword_id: number): Promise<PerformanceData>;
    getTrafficAttribution(keyword_ids: number[]): Promise<Attribution[]>;
}
```

### Performance Optimizations

1. **Database Indexing**
```sql
CREATE INDEX idx_keywords_priority ON keywords(priority_tier);
CREATE INDEX idx_keywords_volume ON keywords(search_volume DESC);
CREATE INDEX idx_keywords_aio ON keywords(aio_status);
CREATE INDEX idx_keywords_category ON keywords(product_category);
```

2. **Caching Strategy**
```typescript
// Redis caching for expensive operations
const cacheKey = `keywords:pyramid:${JSON.stringify(filters)}`;
const cached = await redis.get(cacheKey);
if (cached) return JSON.parse(cached);

const result = await calculatePyramidData(filters);
await redis.setex(cacheKey, 300, JSON.stringify(result)); // 5 min cache
```

3. **Batch Processing**
```typescript
// Queue system for bulk operations
const importQueue = new Bull('keyword-import');

importQueue.process(async (job) => {
    const { file, userId } = job.data;
    const keywords = await parseCSV(file);
    
    // Process in batches
    for (const batch of chunk(keywords, 100)) {
        await bulkInsertKeywords(batch);
        await job.progress(job.progress() + (100 / chunks.length));
    }
});
```

### UI/UX Features

1. **Smart Filters**
   - Quick filters: "P0 Only", "AIO Active", "Uncovered"
   - Advanced filters with AND/OR logic
   - Saved filter presets
   - Filter history

2. **Bulk Operations**
   - Select all/none/inverse
   - Bulk priority assignment
   - Bulk tagging
   - Bulk export selected

3. **Real-time Updates**
   - WebSocket for live AIO status updates
   - Auto-refresh data every 5 minutes
   - Visual indicators for recent changes
   - Push notifications for important changes

4. **Analytics Integration**
   - Click to view keyword performance
   - Inline traffic trends sparklines
   - Competitor comparison overlay
   - Content coverage indicators

### Success Metrics

1. **Performance**
   - Page load < 1 second
   - Search results < 500ms
   - Import 10K keywords < 30 seconds
   - Export 50K keywords < 10 seconds

2. **Usability**
   - 90% task completion rate
   - < 3 clicks to any feature
   - Zero training required
   - Mobile responsive

3. **Data Quality**
   - 99% import success rate
   - Real-time sync with APIs
   - Automatic deduplication
   - Data validation on entry