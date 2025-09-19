# Google AI Overview (GEO) Visibility Tracker

This module tracks and analyzes competitor visibility in Google's AI-generated search overviews, providing critical insights for SEO strategy in the age of generative AI search.

## 🎯 Purpose

As Google increasingly uses AI to generate direct answers (AI Overviews) at the top of search results, traditional SEO metrics are becoming less relevant. This tool helps you understand:

- **Which queries trigger AI Overviews** in your industry
- **Which competitors are cited** in these AI-generated answers
- **How often your brand appears** compared to competitors
- **What content gets referenced** by Google's AI

## 📊 What is GEO (Generative Engine Optimization)?

GEO is the practice of optimizing content to appear in AI-generated search results:

1. **AI Overviews**: Google's AI-generated summaries that appear above traditional results
2. **Citations**: Sources that the AI references in its answers
3. **Visibility**: How prominently brands appear in these AI-generated sections

## 🚀 Quick Start

### Run the complete analysis:
```bash
# Using TypeScript
npx ts-node tests/geo-visibility/run-geo-analysis.ts

# Or using npm script (add to package.json)
npm run analyze:geo
```

### Run tests only:
```bash
npx playwright test tests/geo-visibility/google-ai-overview-tracker.test.ts
```

## 📁 Files Overview

- **`google-ai-overview-tracker.test.ts`**: Main test suite that collects GEO visibility data
- **`geo-data-processor.ts`**: Processes raw data for Neo4j import
- **`run-geo-analysis.ts`**: Orchestrates the complete analysis pipeline
- **`README.md`**: This documentation file

## 🔍 Tracked Metrics

### 1. AI Overview Presence
- Percentage of queries that trigger AI Overviews
- Types of queries most likely to show AI content
- Changes in AI Overview frequency over time

### 2. Competitor Citations
- How often each competitor is cited in AI Overviews
- Average citation positions
- Citation context and relevance

### 3. Visibility Rankings
- Overall GEO visibility scores
- Comparison with traditional organic rankings
- Market share in AI-generated results

### 4. Content Analysis
- What types of content get cited most
- Key topics and themes in citations
- Optimal content formats for AI visibility

## 📈 Sample Output

```
📊 Overall Statistics:
   - Total queries analyzed: 20
   - Queries with AI Overview: 14 (70.0%)

🏆 Competitor AI Overview Visibility Rankings:
1. arlo.com:
   - Appears in: 8/14 AI Overviews (57.1%)
   - Total citations: 12
   - Avg citations per appearance: 1.5

2. ring.com:
   - Appears in: 7/14 AI Overviews (50.0%)
   - Total citations: 9
   - Avg citations per appearance: 1.3

3. eufy.com:
   - Appears in: 4/14 AI Overviews (28.6%)
   - Total citations: 5
   - Avg citations per appearance: 1.3
```

## 🗄️ Neo4j Integration

The tool generates data ready for Neo4j import:

### Generated Files:
- **`geo-visibility-results.json`**: Raw collected data
- **`geo-import-queries.cypher`**: Ready-to-run Neo4j import queries
- **`geo-visibility-report.md`**: Human-readable summary report

### Neo4j Schema:
```
(Query)-[:HAS_AI_OVERVIEW]->(AIOverview)
(AIOverview)-[:CITES]->(Citation)
(Citation)-[:BELONGS_TO]->(Competitor)
(Query)-[:SHOWS_COMPETITOR]->(Competitor)
(Query)-[:RANKS_ORGANICALLY]->(Competitor)
```

### Useful Neo4j Queries:

Find Eufy's AI Overview appearances:
```cypher
MATCH (q:Query)-[r:SHOWS_COMPETITOR]->(c:Competitor {domain: "eufy.com"})
WHERE q.hasAIOverview = true
RETURN q.text as Query, r.citations as Citations
ORDER BY r.citations DESC;
```

Compare competitor visibility:
```cypher
MATCH (c:Competitor)<-[:SHOWS_COMPETITOR]-(q:Query)
WHERE q.hasAIOverview = true
WITH c, COUNT(DISTINCT q) as appearances
RETURN c.name as Competitor, appearances as AIOverviewAppearances
ORDER BY appearances DESC;
```

## 🔧 Configuration

### Query Categories:
1. **Informational**: "How does X work?", "What is X?"
2. **Comparative**: "X vs Y", "Compare X and Y"
3. **Technical**: Feature explanations, specifications
4. **Purchasing**: "Best X", "X buying guide"

### Tracked Competitors:
- Eufy
- Arlo
- Ring
- Google Nest
- Wyze

## 📊 Monitoring Strategy

### Daily Tracking:
- High-value queries (top 10)
- Brand comparison queries
- New product queries

### Weekly Analysis:
- Visibility trends
- New AI Overview patterns
- Competitor strategy changes

### Monthly Reporting:
- Overall visibility scores
- Market share in AI results
- Content optimization recommendations

## 🎯 Optimization Strategies

Based on GEO analysis, optimize content for AI visibility:

### 1. Content Structure
- Clear headings and subheadings
- Bullet points and lists
- Concise, factual statements
- Structured data markup

### 2. Authority Signals
- Expert authorship
- Citations and sources
- Updated timestamps
- Comprehensive coverage

### 3. Query Matching
- Direct answer formatting
- FAQ sections
- Comparison tables
- Technical specifications

## 🚨 Limitations & Considerations

1. **Dynamic Results**: AI Overviews can vary by location, personalization, and time
2. **API Limitations**: Firecrawl may not capture all AI Overview nuances
3. **Rate Limiting**: Respect search engine rate limits
4. **Accuracy**: Results are approximations of actual AI Overview behavior

## 🔄 Future Enhancements

1. **Real-time Monitoring**: Continuous tracking of key queries
2. **Alert System**: Notifications for visibility changes
3. **Content Recommendations**: AI-driven optimization suggestions
4. **Competitive Intelligence**: Deeper analysis of competitor strategies
5. **Multi-language Support**: Track GEO visibility across languages

## 📚 Resources

- [Understanding Google AI Overviews](https://blog.google/products/search/generative-ai-overview/)
- [GEO Best Practices](https://www.searchenginejournal.com/generative-engine-optimization/)
- [Neo4j Graph Analytics](https://neo4j.com/docs/)

## 🤝 Contributing

To improve GEO tracking:
1. Add new query categories in test configuration
2. Enhance AI Overview detection patterns
3. Improve citation extraction logic
4. Add new competitor domains
5. Create visualization dashboards

## 📝 License

This tool is part of the Eufy SEO Analysis System and follows the project's licensing terms.