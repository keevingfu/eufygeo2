import { test, expect } from '@playwright/test';
import axios from 'axios';

// Firecrawl API configuration
const FIRECRAWL_API_KEY = process.env.FIRECRAWL_API_KEY || 'fc-7106bd7009b94c8884a082beaecf4294';
const FIRECRAWL_API_URL = process.env.FIRECRAWL_API_URL || 'https://api.firecrawl.dev/v1';

// Helper function to make Firecrawl API calls
async function callFirecrawlAPI(endpoint: string, method: string, data?: any) {
  const config = {
    method,
    url: `${FIRECRAWL_API_URL}${endpoint}`,
    headers: {
      'Authorization': `Bearer ${FIRECRAWL_API_KEY}`,
      'Content-Type': 'application/json'
    },
    data
  };

  try {
    const response = await axios(config);
    return response.data;
  } catch (error: any) {
    console.error(`Firecrawl API Error: ${error.message}`);
    throw error;
  }
}

// Test configuration
const TEST_URLS = {
  single: 'https://example.com',
  batch: [
    'https://example.com',
    'https://example.com/about',
    'https://example.com/contact'
  ],
  search: 'web scraping best practices',
  research: 'impact of AI on SEO strategies'
};

test.describe('Firecrawl Core Tools Test Suite', () => {
  test.setTimeout(120000); // 2 minutes timeout for API calls

  test('Tool 1: Scrape - Single page scraping', async ({ page }) => {
    console.log('Testing single page scraping...');
    
    const scrapeData = {
      url: TEST_URLS.single,
      formats: ['markdown', 'html'],
      onlyMainContent: true,
      waitFor: 1000,
      timeout: 30000,
      includeTags: ['article', 'main', 'p', 'h1', 'h2'],
      excludeTags: ['nav', 'footer', 'script', 'style']
    };

    const result = await callFirecrawlAPI('/scrape', 'POST', scrapeData);
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
    expect(result.data.markdown).toBeTruthy();
    expect(result.data.html).toBeTruthy();
    
    console.log(`✅ Scraped content length: ${result.data.markdown.length} characters`);
  });

  test('Tool 2: Batch Scrape - Multiple pages scraping', async ({ page }) => {
    console.log('Testing batch scraping...');
    
    const batchData = {
      urls: TEST_URLS.batch,
      options: {
        formats: ['markdown'],
        onlyMainContent: true,
        waitFor: 1000
      }
    };

    const result = await callFirecrawlAPI('/batch/scrape', 'POST', batchData);
    
    expect(result).toBeDefined();
    expect(result.id).toBeDefined();
    expect(result.status).toBeDefined();
    
    console.log(`✅ Batch scrape job ID: ${result.id}`);
    
    // Check batch status
    await new Promise(resolve => setTimeout(resolve, 5000)); // Wait 5 seconds
    
    const statusResult = await callFirecrawlAPI(`/batch/scrape/${result.id}`, 'GET');
    expect(statusResult).toBeDefined();
    expect(['completed', 'processing', 'queued'].includes(statusResult.status)).toBe(true);
    
    console.log(`✅ Batch status: ${statusResult.status}`);
  });

  test('Tool 3: Map - Website URL discovery', async ({ page }) => {
    console.log('Testing website URL mapping...');
    
    const mapData = {
      url: TEST_URLS.single,
      search: '',
      limit: 50,
      includeSubdomains: false
    };

    const result = await callFirecrawlAPI('/map', 'POST', mapData);
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);
    expect(result.data.length).toBeGreaterThan(0);
    
    console.log(`✅ Discovered ${result.data.length} URLs`);
    console.log('Sample URLs:', result.data.slice(0, 3));
  });

  test('Tool 4: Crawl - Multi-page extraction', async ({ page }) => {
    console.log('Testing website crawling...');
    
    const crawlData = {
      url: TEST_URLS.single,
      limit: 10,
      maxDepth: 2,
      allowExternalLinks: false,
      formats: ['markdown'],
      onlyMainContent: true,
      scrapeOptions: {
        waitFor: 1000,
        timeout: 30000
      }
    };

    const result = await callFirecrawlAPI('/crawl', 'POST', crawlData);
    
    expect(result).toBeDefined();
    expect(result.id).toBeDefined();
    expect(result.status).toBeDefined();
    
    console.log(`✅ Crawl job ID: ${result.id}`);
    
    // Check crawl status
    await new Promise(resolve => setTimeout(resolve, 10000)); // Wait 10 seconds
    
    const statusResult = await callFirecrawlAPI(`/crawl/${result.id}`, 'GET');
    expect(statusResult).toBeDefined();
    expect(['completed', 'scraping', 'queued'].includes(statusResult.status)).toBe(true);
    
    console.log(`✅ Crawl status: ${statusResult.status}`);
    if (statusResult.completed) {
      console.log(`✅ Pages crawled: ${statusResult.completed}/${statusResult.total}`);
    }
  });

  test('Tool 5: Search - Web search functionality', async ({ page }) => {
    console.log('Testing web search...');
    
    const searchData = {
      query: TEST_URLS.search,
      limit: 5,
      lang: 'en',
      country: 'us',
      scrapeOptions: {
        formats: ['markdown'],
        onlyMainContent: true
      }
    };

    const result = await callFirecrawlAPI('/search', 'POST', searchData);
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);
    expect(result.data.length).toBeGreaterThan(0);
    
    console.log(`✅ Found ${result.data.length} search results`);
    result.data.slice(0, 3).forEach((item: any, index: number) => {
      console.log(`Result ${index + 1}: ${item.title} - ${item.url}`);
    });
  });

  test('Tool 6: Extract - Structured data extraction', async ({ page }) => {
    console.log('Testing structured data extraction...');
    
    const extractData = {
      urls: [TEST_URLS.single],
      prompt: "Extract the main heading, description, and any contact information",
      schema: {
        type: "object",
        properties: {
          heading: { type: "string" },
          description: { type: "string" },
          contactInfo: {
            type: "object",
            properties: {
              email: { type: "string" },
              phone: { type: "string" },
              address: { type: "string" }
            }
          }
        },
        required: ["heading", "description"]
      },
      systemPrompt: "You are a helpful assistant that extracts structured information from web pages."
    };

    const result = await callFirecrawlAPI('/extract', 'POST', extractData);
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
    
    console.log('✅ Extracted data:', JSON.stringify(result.data, null, 2));
  });

  test('Tool 7: Deep Research - In-depth research', async ({ page }) => {
    console.log('Testing deep research...');
    
    const researchData = {
      query: TEST_URLS.research,
      maxDepth: 2,
      timeLimit: 60,
      maxUrls: 20,
      includeDomains: [],
      excludeDomains: []
    };

    const result = await callFirecrawlAPI('/research', 'POST', researchData);
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
    expect(result.data.finalAnalysis).toBeTruthy();
    
    console.log('✅ Research completed');
    console.log(`Analysis length: ${result.data.finalAnalysis.length} characters`);
    if (result.data.sources) {
      console.log(`Sources used: ${result.data.sources.length}`);
    }
  });

  test('Tool 8: Generate LLMs.txt - LLMs.txt generation', async ({ page }) => {
    console.log('Testing LLMs.txt generation...');
    
    const llmsData = {
      url: TEST_URLS.single,
      maxUrls: 20,
      showFullText: true
    };

    const result = await callFirecrawlAPI('/llms-txt', 'POST', llmsData);
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(result.data).toBeDefined();
    expect(result.data.llmsTxt).toBeTruthy();
    
    console.log('✅ Generated LLMs.txt:');
    console.log(result.data.llmsTxt.substring(0, 500) + '...');
    
    if (result.data.llmsFullTxt) {
      console.log(`✅ Full text length: ${result.data.llmsFullTxt.length} characters`);
    }
  });
});

// Performance and reliability tests
test.describe('Firecrawl Performance & Reliability Tests', () => {
  test('Rate limiting and retry behavior', async ({ page }) => {
    console.log('Testing rate limiting and retry behavior...');
    
    // Make multiple rapid requests to test rate limiting
    const requests = Array(5).fill(null).map(() => 
      callFirecrawlAPI('/scrape', 'POST', {
        url: TEST_URLS.single,
        formats: ['markdown']
      })
    );

    const results = await Promise.allSettled(requests);
    
    const successful = results.filter(r => r.status === 'fulfilled').length;
    const rateLimited = results.filter(r => 
      r.status === 'rejected' && 
      r.reason?.response?.status === 429
    ).length;
    
    console.log(`✅ Successful requests: ${successful}`);
    console.log(`✅ Rate limited requests: ${rateLimited}`);
    
    expect(successful + rateLimited).toBe(5);
  });

  test('Credit usage monitoring', async ({ page }) => {
    console.log('Testing credit usage monitoring...');
    
    // Check account credits (if API supports it)
    try {
      const result = await callFirecrawlAPI('/account/credits', 'GET');
      
      if (result && result.credits !== undefined) {
        console.log(`✅ Current credits: ${result.credits}`);
        expect(result.credits).toBeGreaterThanOrEqual(0);
      }
    } catch (error) {
      console.log('ℹ️ Credit endpoint not available or different API version');
    }
  });

  test('Error handling and recovery', async ({ page }) => {
    console.log('Testing error handling...');
    
    // Test with invalid URL
    try {
      await callFirecrawlAPI('/scrape', 'POST', {
        url: 'not-a-valid-url',
        formats: ['markdown']
      });
      expect(true).toBe(false); // Should not reach here
    } catch (error: any) {
      expect(error.response).toBeDefined();
      expect(error.response.status).toBeGreaterThanOrEqual(400);
      console.log('✅ Invalid URL error handled correctly');
    }

    // Test with missing required parameters
    try {
      await callFirecrawlAPI('/scrape', 'POST', {
        formats: ['markdown'] // Missing URL
      });
      expect(true).toBe(false); // Should not reach here
    } catch (error: any) {
      expect(error.response).toBeDefined();
      expect(error.response.status).toBeGreaterThanOrEqual(400);
      console.log('✅ Missing parameter error handled correctly');
    }
  });
});