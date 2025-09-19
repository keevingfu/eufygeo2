# GEO Platform Examples

This directory contains example code patterns to follow when building the Eufy GEO Platform. Each example demonstrates best practices for specific components.

## Examples Overview

### 1. `keyword-dashboard.tsx`
**React Dashboard Component with ECharts**
- Shows how to integrate ECharts for pyramid visualization
- Demonstrates Material-UI DataGrid usage
- Includes filtering and search functionality
- Pattern for handling large datasets efficiently

Key patterns:
- Component structure with TypeScript interfaces
- ECharts configuration for funnel/pyramid charts
- DataGrid column definitions with custom rendering
- State management for real-time updates

### 2. `api-routes.ts`
**Express API with TypeScript and Validation**
- RESTful API design with proper HTTP methods
- Input validation using Zod schemas
- Redis caching implementation
- Error handling patterns
- TypeScript typing for Express

Key patterns:
- Zod schema validation
- Cache-aside pattern implementation
- Proper error responses with status codes
- Query parameter parsing and validation
- Batch operations endpoint

### 3. `schema.sql`
**PostgreSQL Schema Design**
- Optimized table structure for SEO data
- Efficient indexing strategy
- JSONB columns for flexible metadata
- Materialized views for performance
- Audit trail implementation

Key patterns:
- Composite indexes for common queries
- Partial indexes for filtered queries
- GIN indexes for JSONB search
- Triggers for automatic timestamps
- Views for denormalized data access

### 4. `redis-caching.ts`
**Redis Caching Service**
- Cache-aside pattern with TTL
- Batch operations for efficiency
- Pattern-based invalidation
- Pub/Sub for distributed cache invalidation
- Connection pooling and error handling

Key patterns:
- Generic type-safe caching methods
- Pipeline operations for batch processing
- Cache warming strategies
- Real-time invalidation across instances
- Graceful degradation on cache miss

### 5. `csv-import.ts`
**Bulk Import with Progress Tracking**
- Stream processing for large files
- Batch database operations
- Progress reporting
- Error recovery and logging
- Background job processing

Key patterns:
- Node.js streams for memory efficiency
- Database transactions for consistency
- Bull queue for background processing
- Progress tracking with callbacks
- Conflict resolution (upsert) logic

## Usage Guidelines

1. **Don't copy directly** - These are patterns to follow, not code to copy
2. **Adapt to context** - Modify patterns to fit specific requirements
3. **Maintain consistency** - Use similar patterns across the codebase
4. **Test thoroughly** - Each pattern should have corresponding tests
5. **Document deviations** - If you need to deviate from a pattern, document why

## Common Patterns Across Examples

### Error Handling
```typescript
try {
  // Operation
} catch (error) {
  if (error instanceof SpecificError) {
    // Handle specific error
  }
  console.error('Context:', error);
  // Return appropriate response
}
```

### Validation
- Always validate input at API boundaries
- Use Zod for runtime type checking
- Return clear error messages with details

### Performance
- Cache expensive operations
- Use database indexes effectively
- Implement pagination for large datasets
- Stream large files instead of loading to memory

### Security
- Never trust user input
- Use parameterized queries
- Implement rate limiting
- Validate authentication/authorization

### Testing
- Unit test each module
- Integration test API endpoints
- Test error scenarios
- Mock external dependencies