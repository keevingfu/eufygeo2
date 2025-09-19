## FEATURE:

Comprehensive GEO (Generative Engine Optimization) Platform for Eufy smart home products with the following core modules:
- Keyword Management System (850+ keywords with P0-P4 classification)
- Content Lifecycle Management with AI integration
- Analytics Dashboard with real-time performance tracking
- Multi-channel Distribution (Google AIO, YouTube, Reddit)
- ROI Attribution and Automated Reporting

Business Goals:
- 40% AIO coverage for core keywords (>10K searches) in 3 months
- 30% increase in GEO traffic
- 25% increase in Reddit positive mentions
- 10% higher conversion rate vs traditional SEO

## EXAMPLES:

The following examples from our existing codebase demonstrate patterns to follow:
- `examples/keyword-dashboard.tsx` - React component with ECharts pyramid visualization
- `examples/api-routes.ts` - Express/TypeScript API patterns with validation
- `examples/schema.sql` - PostgreSQL schema for SEO platforms
- `examples/redis-caching.ts` - Caching strategies for performance
- `examples/csv-import.ts` - Bulk data import with progress tracking

## DOCUMENTATION:

External APIs and services to integrate:
- Google Search Console API: https://developers.google.com/webmaster-tools/search-console-api-original
- Google Analytics 4 API: https://developers.google.com/analytics/devguides/reporting/data/v1
- YouTube Data API: https://developers.google.com/youtube/v3
- SEMrush API: https://www.semrush.com/api-documentation/
- Reddit API: https://www.reddit.com/dev/api/

Technical Stack Documentation:
- React 18: https://react.dev/
- Material-UI: https://mui.com/
- ECharts: https://echarts.apache.org/
- Express.js: https://expressjs.com/
- TypeScript: https://www.typescriptlang.org/
- PostgreSQL: https://www.postgresql.org/docs/
- Redis: https://redis.io/docs/

## OTHER CONSIDERATIONS:

Critical Implementation Details:
1. **Performance**: All queries must respond in <2 seconds. Use Redis caching aggressively.
2. **Scalability**: Design for 10,000+ concurrent users from day one.
3. **Security**: Implement JWT with refresh tokens, RBAC, rate limiting.
4. **Data Volume**: System must handle bulk imports of 10,000+ keywords efficiently.
5. **Real-time Updates**: Dashboard must update within 500ms of data changes.

Common Pitfalls to Avoid:
- Don't create monolithic files - keep modules under 500 lines
- Always implement proper error handling for external API calls
- Use database transactions for multi-table operations
- Implement retry logic with exponential backoff for API requests
- Cache invalidation strategy is critical - plan it upfront

Required Environment Variables:
- Database: DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD
- Redis: REDIS_HOST, REDIS_PORT
- APIs: GOOGLE_API_KEY, YOUTUBE_API_KEY, SEMRUSH_API_KEY, REDDIT_CLIENT_ID
- Security: JWT_SECRET, BCRYPT_ROUNDS
- App: NODE_ENV, PORT

Development Workflow:
1. Use TypeScript strict mode
2. Write tests for all critical paths
3. Document all API endpoints with OpenAPI
4. Use conventional commits for version control
5. Implement health checks for all services
