// ============================================================
// Eufy Competitor SEO Analysis - Cypher Queries Collection
// ============================================================

// ============================================================
// BASIC EXPLORATION QUERIES
// ============================================================

// 1. View sample of the graph structure
MATCH (n)
RETURN n
LIMIT 50;

// 2. Count different node types
MATCH (n)
RETURN labels(n)[0] AS NodeType, COUNT(n) AS Count
ORDER BY Count DESC;

// 3. Count relationship types
MATCH ()-[r]->()
RETURN type(r) AS RelationshipType, COUNT(r) AS Count
ORDER BY Count DESC;

// ============================================================
// COMPETITOR ANALYSIS QUERIES
// ============================================================

// 4. Top competitors by keyword coverage
MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WITH d.name AS competitor, 
     COUNT(DISTINCT k) AS keyword_count,
     SUM(r.traffic) AS total_traffic,
     AVG(r.position) AS avg_position
RETURN competitor, 
       keyword_count, 
       total_traffic,
       ROUND(avg_position, 2) AS avg_position
ORDER BY keyword_count DESC
LIMIT 20;

// 5. Competitor domain distribution
MATCH (d:Domain)
OPTIONAL MATCH (d)<-[:BELONGS_TO]-(u:URL)
WITH d.name AS domain, COUNT(u) AS page_count
RETURN domain, page_count
ORDER BY page_count DESC
LIMIT 30;

// 6. Competitors ranking in top 10
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE r.position <= 10
WITH d.name AS competitor,
     COUNT(DISTINCT k) AS top10_keywords,
     SUM(k.search_volume) AS total_search_volume,
     AVG(r.position) AS avg_position
RETURN competitor,
       top10_keywords,
       total_search_volume,
       ROUND(avg_position, 2) AS avg_position_in_top10
ORDER BY top10_keywords DESC
LIMIT 20;

// ============================================================
// KEYWORD OPPORTUNITY ANALYSIS
// ============================================================

// 7. High-value keyword opportunities (high volume, low difficulty)
MATCH (k:Keyword)
WHERE k.search_volume > 5000 AND k.difficulty < 40
OPTIONAL MATCH (k)-[r:RANKS_FOR]->(u:URL)
WITH k, COUNT(r) AS competitor_count, MIN(r.position) AS best_position
RETURN k.text AS keyword,
       k.search_volume AS volume,
       k.difficulty AS difficulty,
       k.cpc AS cpc,
       competitor_count,
       best_position,
       (k.search_volume * k.cpc) AS potential_value
ORDER BY potential_value DESC
LIMIT 50;

// 8. Keywords with low competition
MATCH (k:Keyword)
OPTIONAL MATCH (k)-[r:RANKS_FOR]->(u:URL)
WITH k, COUNT(r) AS ranking_count
WHERE ranking_count < 3 AND k.search_volume > 1000
RETURN k.text AS keyword,
       k.search_volume AS volume,
       k.difficulty AS difficulty,
       ranking_count AS competitors_ranking,
       k.cpc AS cpc
ORDER BY volume DESC
LIMIT 100;

// 9. Keywords dominated by single competitor
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE r.position <= 3
WITH k, d, r.position AS position
ORDER BY k.text, position
WITH k, COLLECT(d.name)[0] AS top_competitor
WHERE k.search_volume > 1000
RETURN k.text AS keyword,
       k.search_volume AS volume,
       top_competitor,
       k.difficulty AS difficulty
ORDER BY volume DESC
LIMIT 50;

// ============================================================
// COMPETITIVE GAP ANALYSIS
// ============================================================

// 10. Keywords where competitors rank but not Eufy
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE NOT d.name CONTAINS 'eufy' 
  AND r.position <= 20
  AND k.search_volume > 500
WITH k, MIN(r.position) AS best_competitor_position
WHERE NOT EXISTS {
  MATCH (k)-[:RANKS_FOR]->(eu:URL)-[:BELONGS_TO]->(ed:Domain)
  WHERE ed.name CONTAINS 'eufy'
}
RETURN k.text AS keyword,
       k.search_volume AS volume,
       k.difficulty AS difficulty,
       best_competitor_position,
       k.cpc AS cpc
ORDER BY volume DESC
LIMIT 100;

// ============================================================
// INTENT ANALYSIS
// ============================================================

// 11. Search intent distribution
MATCH (i:Intent)<-[:HAS_INTENT]-(k:Keyword)
WITH i.type AS intent,
     COUNT(k) AS keyword_count,
     SUM(k.search_volume) AS total_volume,
     AVG(k.difficulty) AS avg_difficulty
RETURN intent,
       keyword_count,
       total_volume,
       ROUND(avg_difficulty, 2) AS avg_difficulty
ORDER BY keyword_count DESC;

// 12. High-value intents
MATCH (i:Intent)<-[:HAS_INTENT]-(k:Keyword)
WITH i.type AS intent,
     SUM(k.search_volume * k.cpc) AS total_value,
     COUNT(k) AS keyword_count,
     AVG(k.cpc) AS avg_cpc
RETURN intent,
       keyword_count,
       ROUND(total_value, 2) AS total_value,
       ROUND(avg_cpc, 2) AS avg_cpc
ORDER BY total_value DESC;

// ============================================================
// SERP FEATURE ANALYSIS
// ============================================================

// 13. SERP feature distribution
MATCH (s:SERPFeature)<-[:HAS_SERP_FEATURE]-(k:Keyword)
WITH s.name AS feature,
     COUNT(k) AS keyword_count,
     SUM(k.search_volume) AS total_volume
RETURN feature,
       keyword_count,
       total_volume
ORDER BY keyword_count DESC;

// 14. Keywords with multiple SERP features
MATCH (k:Keyword)-[:HAS_SERP_FEATURE]->(s:SERPFeature)
WITH k, COUNT(s) AS feature_count, COLLECT(s.name) AS features
WHERE feature_count > 2 AND k.search_volume > 1000
RETURN k.text AS keyword,
       k.search_volume AS volume,
       feature_count,
       features
ORDER BY volume DESC
LIMIT 50;

// ============================================================
// URL PERFORMANCE ANALYSIS
// ============================================================

// 15. Top performing URLs by traffic
MATCH (u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WITH u.address AS url,
     COUNT(k) AS ranking_keywords,
     SUM(r.traffic) AS total_traffic,
     AVG(r.position) AS avg_position
WHERE total_traffic > 0
RETURN url,
       ranking_keywords,
       total_traffic,
       ROUND(avg_position, 2) AS avg_position
ORDER BY total_traffic DESC
LIMIT 30;

// 16. URLs ranking for high-value keywords
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)
WHERE k.search_volume > 5000 AND r.position <= 10
WITH u.address AS url,
     COUNT(k) AS high_value_keywords,
     SUM(k.search_volume) AS total_volume,
     AVG(r.position) AS avg_position
RETURN url,
       high_value_keywords,
       total_volume,
       ROUND(avg_position, 2) AS avg_position
ORDER BY total_volume DESC
LIMIT 30;

// ============================================================
// POSITION MOVEMENT ANALYSIS
// ============================================================

// 17. Keywords with significant position changes
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)
WHERE ABS(r.position - r.previous_position) > 5
  AND r.previous_position > 0
  AND k.search_volume > 1000
RETURN k.text AS keyword,
       u.address AS url,
       r.previous_position AS old_position,
       r.position AS new_position,
       (r.previous_position - r.position) AS position_change,
       k.search_volume AS volume
ORDER BY ABS(position_change) DESC
LIMIT 50;

// 18. Improving vs declining rankings
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE r.previous_position > 0
WITH d.name AS domain,
     SUM(CASE WHEN r.position < r.previous_position THEN 1 ELSE 0 END) AS improving,
     SUM(CASE WHEN r.position > r.previous_position THEN 1 ELSE 0 END) AS declining,
     SUM(CASE WHEN r.position = r.previous_position THEN 1 ELSE 0 END) AS stable
RETURN domain,
       improving,
       declining,
       stable,
       improving + declining + stable AS total
ORDER BY total DESC
LIMIT 20;

// ============================================================
// COMPETITIVE KEYWORD CLUSTERS
// ============================================================

// 19. Find keyword clusters (keywords ranking for same URLs)
MATCH (u:URL)<-[:RANKS_FOR]-(k1:Keyword)
WITH u, COLLECT(k1.text) AS keywords, COUNT(k1) AS keyword_count
WHERE keyword_count > 5
RETURN u.address AS url,
       keyword_count,
       keywords[0..10] AS sample_keywords
ORDER BY keyword_count DESC
LIMIT 20;

// 20. Competitive intensity by keyword
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE r.position <= 20
WITH k.text AS keyword,
     k.search_volume AS volume,
     COUNT(DISTINCT d) AS competing_domains,
     COLLECT(DISTINCT d.name) AS competitors
WHERE competing_domains > 5
RETURN keyword,
       volume,
       competing_domains,
       competitors[0..5] AS top_competitors
ORDER BY volume DESC
LIMIT 50;

// ============================================================
// TRAFFIC VALUE ANALYSIS
// ============================================================

// 21. Domains by traffic value
MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WITH d.name AS domain,
     SUM(r.traffic_cost) AS total_traffic_value,
     SUM(r.traffic) AS total_traffic,
     COUNT(DISTINCT k) AS keyword_count
RETURN domain,
       ROUND(total_traffic_value, 2) AS traffic_value,
       total_traffic,
       keyword_count
ORDER BY total_traffic_value DESC
LIMIT 20;

// 22. High ROI keywords (high traffic value, low difficulty)
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)
WHERE k.difficulty < 50 AND r.traffic_cost > 100
WITH k.text AS keyword,
     k.search_volume AS volume,
     k.difficulty AS difficulty,
     SUM(r.traffic_cost) AS total_value,
     AVG(r.position) AS avg_position
RETURN keyword,
       volume,
       difficulty,
       ROUND(total_value, 2) AS traffic_value,
       ROUND(avg_position, 2) AS avg_position
ORDER BY total_value DESC
LIMIT 50;

// ============================================================
// ADVANCED ANALYTICS
// ============================================================

// 23. Market share analysis
MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WHERE r.position <= 10
WITH SUM(k.search_volume) AS total_market_volume
MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WHERE r.position <= 10
WITH d.name AS domain,
     SUM(k.search_volume) AS domain_volume,
     total_market_volume
RETURN domain,
       domain_volume,
       ROUND(100.0 * domain_volume / total_market_volume, 2) AS market_share_percent
ORDER BY domain_volume DESC
LIMIT 20;

// 24. Content gap opportunities
MATCH (k:Keyword)
WHERE k.search_volume > 1000
  AND NOT EXISTS {
    MATCH (k)-[r:RANKS_FOR]->(u:URL)
    WHERE r.position <= 20
  }
RETURN k.text AS keyword,
       k.search_volume AS volume,
       k.difficulty AS difficulty,
       k.cpc AS cpc,
       (k.search_volume * k.cpc) AS potential_value
ORDER BY potential_value DESC
LIMIT 100;

// 25. Create a comprehensive competitor landscape view
MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WITH d,
     COUNT(DISTINCT k) AS total_keywords,
     COUNT(DISTINCT CASE WHEN r.position <= 3 THEN k END) AS top3_keywords,
     COUNT(DISTINCT CASE WHEN r.position BETWEEN 4 AND 10 THEN k END) AS top4_10_keywords,
     COUNT(DISTINCT CASE WHEN r.position BETWEEN 11 AND 20 THEN k END) AS top11_20_keywords,
     SUM(r.traffic) AS total_traffic,
     SUM(r.traffic_cost) AS total_traffic_value,
     AVG(r.position) AS avg_position,
     AVG(k.difficulty) AS avg_keyword_difficulty
RETURN d.name AS competitor,
       total_keywords,
       top3_keywords,
       top4_10_keywords,
       top11_20_keywords,
       total_traffic,
       ROUND(total_traffic_value, 2) AS traffic_value,
       ROUND(avg_position, 2) AS avg_position,
       ROUND(avg_keyword_difficulty, 2) AS avg_difficulty
ORDER BY total_keywords DESC
LIMIT 30;
