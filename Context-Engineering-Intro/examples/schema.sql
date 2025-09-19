-- Example PostgreSQL schema for SEO/GEO platform
-- Demonstrates:
-- 1. Efficient indexing strategy
-- 2. JSON columns for flexible data
-- 3. Audit trail with triggers
-- 4. Views for common queries

-- Keywords table with comprehensive tracking
CREATE TABLE keywords (
    id SERIAL PRIMARY KEY,
    keyword TEXT NOT NULL UNIQUE,
    search_volume INTEGER,
    difficulty DECIMAL(3,1),
    priority_tier VARCHAR(2),
    aio_status VARCHAR(20) DEFAULT 'monitoring',
    metadata JSONB, -- Flexible field for additional data
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX idx_keywords_tier_volume ON keywords(priority_tier, search_volume DESC);
CREATE INDEX idx_keywords_aio_status ON keywords(aio_status) WHERE aio_status = 'active';
CREATE INDEX idx_keywords_metadata ON keywords USING GIN(metadata);

-- Keyword performance tracking
CREATE TABLE keyword_performance (
    id SERIAL PRIMARY KEY,
    keyword_id INTEGER REFERENCES keywords(id),
    date DATE NOT NULL,
    metrics JSONB NOT NULL, -- {impressions, clicks, ctr, position, aio_appearances}
    UNIQUE(keyword_id, date)
);

-- Partition by date for better performance
CREATE INDEX idx_perf_date ON keyword_performance(date DESC);

-- Materialized view for dashboard
CREATE MATERIALIZED VIEW keyword_summary AS
SELECT 
    k.priority_tier,
    COUNT(*) as total_keywords,
    AVG(k.search_volume) as avg_volume,
    COUNT(CASE WHEN k.aio_status = 'active' THEN 1 END) as aio_active,
    SUM((p.metrics->>'clicks')::int) as total_clicks_30d
FROM keywords k
LEFT JOIN keyword_performance p ON k.id = p.keyword_id 
    AND p.date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY k.priority_tier;

-- Refresh materialized view periodically
CREATE INDEX idx_keyword_summary_tier ON keyword_summary(priority_tier);

-- Audit trigger
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER keywords_updated_at 
    BEFORE UPDATE ON keywords
    FOR EACH ROW EXECUTE FUNCTION update_updated_at();