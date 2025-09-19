# Firecrawl Integration Tests for Eufy SEO Analysis

This test suite validates the integration of Firecrawl's 8 core tools with the Eufy SEO competitive analysis system.

## Test Coverage

### 1. Core Functionality Tests (`firecrawl.test.ts`)
Tests each of the 8 Firecrawl tools:
- **Scrape**: Single page content extraction
- **Batch Scrape**: Multiple URL processing
- **Map**: Website structure discovery
- **Crawl**: Deep website analysis
- **Search**: Web search functionality
- **Extract**: Structured data extraction
- **Deep Research**: Multi-source research
- **Generate LLMs.txt**: AI policy generation

### 2. SEO Analysis Tests (`firecrawl-seo-analysis.test.ts`)
Eufy-specific competitive intelligence tests:
- Competitor homepage SEO analysis
- Product page data extraction
- Site structure mapping
- Content strategy analysis
- SERP competition tracking
- Structured product data extraction
- Integration with Neo4j pipeline

## Setup

### Prerequisites
1. Node.js 18+ installed
2. Firecrawl API key (already configured in tests)
3. Neo4j database running (for integration tests)

### Installation
```bash
# Install dependencies
npm install

# Install Playwright browsers
npm run install
```

## Running Tests

### Run all Firecrawl tests
```bash
npm run test:firecrawl
```

### Run basic functionality tests only
```bash
npm run test:firecrawl:basic
```

### Run SEO analysis tests only
```bash
npm run test:firecrawl:seo
```

### Run with UI mode (interactive)
```bash
npm run test:ui
```

### Run in debug mode
```bash
npm run test:debug
```

### Run with browser visible
```bash
npm run test:headed
```

## Test Configuration

### Environment Variables
Create a `.env` file for custom configuration:
```env
# Firecrawl API Configuration
FIRECRAWL_API_KEY=fc-7106bd7009b94c8884a082beaecf4294
FIRECRAWL_API_URL=https://api.firecrawl.dev/v1

# Retry Configuration
FIRECRAWL_RETRY_MAX_ATTEMPTS=5
FIRECRAWL_RETRY_INITIAL_DELAY=2000
FIRECRAWL_RETRY_MAX_DELAY=30000
FIRECRAWL_RETRY_BACKOFF_FACTOR=2

# Credit Monitoring
FIRECRAWL_CREDIT_WARNING_THRESHOLD=2000
FIRECRAWL_CREDIT_CRITICAL_THRESHOLD=500
```

### Test Data
Test configuration and data are defined in `test-config.ts`:
- Competitor URLs and domains
- SEO test queries
- Data extraction schemas
- Helper functions

## Test Results

### Viewing Reports
```bash
# Open HTML report
npm run report
```

Reports are generated in:
- `playwright-report/` - HTML report
- `test-results/` - JSON results
- Screenshots on failure in `test-results/`

## Expected Results

### Tool 1: Scrape
- Extracts title, meta description, headings
- Counts H1/H2 tags
- Measures content length

### Tool 2: Batch Scrape
- Processes multiple product pages
- Extracts pricing patterns
- Identifies feature keywords

### Tool 3: Map
- Discovers 50-100+ URLs per site
- Categorizes by type (product, blog, support)
- Provides site structure insights

### Tool 4: Crawl
- Deep crawls blog/resource sections
- Analyzes content topics
- Tracks keyword frequency

### Tool 5: Search
- Retrieves top 10 SERP results
- Identifies competitor presence
- Shows ranking positions

### Tool 6: Extract
- Extracts structured product data
- Captures prices, features, specs
- Formats for Neo4j import

### Tool 7: Deep Research
- Provides comprehensive analysis
- Lists sources used
- Generates insights summary

### Tool 8: Generate LLMs.txt
- Creates AI crawling guidelines
- Analyzes robot policies
- Checks crawl permissions

## Integration with Neo4j

The test suite includes a complete data pipeline test that:
1. Discovers competitor URLs
2. Extracts structured data
3. Formats for Neo4j import
4. Provides import instructions

To import extracted data to Neo4j:
```bash
# Save test output as JSON
# Then run:
python3 import_competitor_data_to_neo4j.py --json-file competitor_data.json
```

## Troubleshooting

### Common Issues

1. **Rate Limiting**
   - Tests include delays between requests
   - Retry logic handles 429 errors
   - Adjust delays in `respectRateLimit()`

2. **Timeout Errors**
   - Default timeout is 3 minutes per test
   - Increase in `playwright.config.ts` if needed
   - Some operations (crawl, research) take longer

3. **API Key Issues**
   - Verify API key in test files
   - Check credit balance
   - Monitor usage with credit tests

4. **Connection Errors**
   - Ensure internet connectivity
   - Check if target sites are accessible
   - Some sites may block automated access

## Best Practices

1. **Run tests sequentially** to avoid rate limiting
2. **Monitor credit usage** to stay within limits
3. **Use test data** instead of production URLs when possible
4. **Cache results** when developing tests
5. **Respect robots.txt** and site policies

## Contributing

When adding new tests:
1. Follow existing test structure
2. Use descriptive test names
3. Add appropriate assertions
4. Include error handling
5. Document expected results
6. Update this README

## Support

For issues with:
- **Firecrawl API**: Check [Firecrawl docs](https://docs.firecrawl.dev)
- **Playwright**: See [Playwright docs](https://playwright.dev)
- **Test Suite**: Open an issue in the project repository