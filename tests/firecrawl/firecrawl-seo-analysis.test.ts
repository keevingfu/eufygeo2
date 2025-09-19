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
    if (error.response) {
      console.error('Response data:', error.response.data);
    }
    throw error;
  }
}

// SEO-focused test URLs for Eufy competitors
const SEO_TEST_TARGETS = {
  competitors: [
    'https://www.arlo.com',
    'https://ring.com',
    'https://www.google.com/nest',
    'https://www.wyze.com'
  ],
  productPages: [
    'https://www.arlo.com/en-us/cameras',
    'https://ring.com/security-cameras',
    'https://store.google.com/category/connected_home',
    'https://www.wyze.com/products/wyze-cam'
  ],
  searchQueries: [
    'best home security cameras 2024',
    'wireless security camera reviews',
    'smart home security systems comparison',
    'eufy vs arlo vs ring comparison'
  ]
};

test.describe('Firecrawl SEO Analysis for Eufy Competitive Intelligence', () => {
  test.setTimeout(180000); // 3 minutes timeout for complex operations

  test('Tool 1: Scrape - Analyze competitor homepage SEO elements', async ({ page }) => {
    console.log('🔍 Analyzing competitor homepage SEO elements...');
    
    for (const competitorUrl of SEO_TEST_TARGETS.competitors.slice(0, 2)) {
      console.log(`\nAnalyzing: ${competitorUrl}`);
      
      const scrapeData = {
        url: competitorUrl,
        formats: ['markdown', 'html'],
        onlyMainContent: false, // We want full page for SEO analysis
        waitFor: 3000,
        timeout: 30000,
        includeTags: ['title', 'meta', 'h1', 'h2', 'h3', 'p', 'a'],
        excludeTags: ['script', 'style', 'noscript']
      };

      try {
        const result = await callFirecrawlAPI('/scrape', 'POST', scrapeData);
        
        expect(result).toBeDefined();
        expect(result.success).toBe(true);
        expect(result.data).toBeDefined();
        
        // Extract SEO elements
        const html = result.data.html || '';
        const markdown = result.data.markdown || '';
        
        // Extract title
        const titleMatch = html.match(/<title>(.*?)<\/title>/i);
        const title = titleMatch ? titleMatch[1] : 'No title found';
        
        // Extract meta description
        const metaDescMatch = html.match(/<meta\s+name="description"\s+content="([^"]+)"/i);
        const metaDescription = metaDescMatch ? metaDescMatch[1] : 'No meta description';
        
        // Count headings
        const h1Count = (html.match(/<h1/gi) || []).length;
        const h2Count = (html.match(/<h2/gi) || []).length;
        
        console.log(`✅ SEO Analysis for ${competitorUrl}:`);
        console.log(`   - Title (${title.length} chars): ${title.substring(0, 60)}...`);
        console.log(`   - Meta Description (${metaDescription.length} chars): ${metaDescription.substring(0, 100)}...`);
        console.log(`   - H1 tags: ${h1Count}`);
        console.log(`   - H2 tags: ${h2Count}`);
        console.log(`   - Content length: ${markdown.length} characters`);
        
      } catch (error) {
        console.log(`⚠️ Failed to scrape ${competitorUrl}: ${error.message}`);
      }
      
      // Rate limiting delay
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  });

  test('Tool 2: Batch Scrape - Analyze multiple product pages', async ({ page }) => {
    console.log('🔍 Batch analyzing competitor product pages...');
    
    const batchData = {
      urls: SEO_TEST_TARGETS.productPages,
      options: {
        formats: ['markdown', 'html'],
        onlyMainContent: true,
        waitFor: 2000,
        includeTags: ['title', 'h1', 'h2', 'h3', 'p', 'span', 'div'],
        excludeTags: ['script', 'style']
      }
    };

    const result = await callFirecrawlAPI('/batch/scrape', 'POST', batchData);
    
    expect(result).toBeDefined();
    expect(result.id).toBeDefined();
    
    console.log(`✅ Batch scrape job initiated: ${result.id}`);
    
    // Wait for batch processing
    await new Promise(resolve => setTimeout(resolve, 15000));
    
    // Check batch status
    const statusResult = await callFirecrawlAPI(`/batch/scrape/${result.id}`, 'GET');
    console.log(`✅ Batch status: ${statusResult.status}`);
    
    if (statusResult.data && Array.isArray(statusResult.data)) {
      console.log(`✅ Successfully scraped ${statusResult.data.length} product pages`);
      
      // Analyze product page patterns
      statusResult.data.forEach((page: any, index: number) => {
        if (page.markdown) {
          console.log(`\nProduct Page ${index + 1} Analysis:`);
          console.log(`   - URL: ${page.url}`);
          console.log(`   - Content length: ${page.markdown.length} chars`);
          
          // Look for pricing patterns
          const priceMatches = page.markdown.match(/\$\d+\.?\d*/g) || [];
          console.log(`   - Price mentions: ${priceMatches.length}`);
          
          // Look for feature keywords
          const features = ['wireless', 'HD', '1080p', '4K', 'motion', 'night vision', 'weatherproof'];
          features.forEach(feature => {
            const count = (page.markdown.match(new RegExp(feature, 'gi')) || []).length;
            if (count > 0) console.log(`   - "${feature}" mentions: ${count}`);
          });
        }
      });
    }
  });

  test('Tool 3: Map - Discover competitor site structure', async ({ page }) => {
    console.log('🔍 Mapping competitor website structure...');
    
    const testUrl = 'https://www.wyze.com'; // Using Wyze as it's typically smaller
    
    const mapData = {
      url: testUrl,
      search: '',
      limit: 100,
      includeSubdomains: false
    };

    const result = await callFirecrawlAPI('/map', 'POST', mapData);
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    expect(Array.isArray(result.data)).toBe(true);
    
    console.log(`✅ Discovered ${result.data.length} URLs on ${testUrl}`);
    
    // Categorize URLs
    const categories = {
      products: result.data.filter((url: string) => url.includes('/product')),
      blog: result.data.filter((url: string) => url.includes('/blog') || url.includes('/news')),
      support: result.data.filter((url: string) => url.includes('/support') || url.includes('/help')),
      about: result.data.filter((url: string) => url.includes('/about') || url.includes('/company'))
    };
    
    console.log('\nURL Structure Analysis:');
    console.log(`   - Product pages: ${categories.products.length}`);
    console.log(`   - Blog/News pages: ${categories.blog.length}`);
    console.log(`   - Support pages: ${categories.support.length}`);
    console.log(`   - About pages: ${categories.about.length}`);
    
    // Show sample URLs
    if (categories.products.length > 0) {
      console.log('\nSample product URLs:');
      categories.products.slice(0, 3).forEach(url => console.log(`   - ${url}`));
    }
  });

  test('Tool 4: Crawl - Deep crawl competitor blog/resources', async ({ page }) => {
    console.log('🔍 Deep crawling competitor content strategy...');
    
    const crawlData = {
      url: 'https://www.wyze.com/blog',
      limit: 10,
      maxDepth: 2,
      allowExternalLinks: false,
      formats: ['markdown'],
      onlyMainContent: true,
      includePaths: ['/blog/*', '/news/*'],
      excludePaths: ['/login', '/cart', '/checkout'],
      scrapeOptions: {
        waitFor: 2000,
        timeout: 30000
      }
    };

    const result = await callFirecrawlAPI('/crawl', 'POST', crawlData);
    
    expect(result).toBeDefined();
    expect(result.id).toBeDefined();
    
    console.log(`✅ Crawl job initiated: ${result.id}`);
    
    // Wait for crawl to process
    await new Promise(resolve => setTimeout(resolve, 20000));
    
    // Check crawl status
    const statusResult = await callFirecrawlAPI(`/crawl/${result.id}`, 'GET');
    console.log(`✅ Crawl status: ${statusResult.status}`);
    
    if (statusResult.data && Array.isArray(statusResult.data)) {
      console.log(`✅ Crawled ${statusResult.data.length} pages`);
      
      // Analyze content topics
      const topics: { [key: string]: number } = {};
      const keywords = ['security', 'camera', 'smart', 'home', 'wireless', 'installation', 'review', 'comparison'];
      
      statusResult.data.forEach((page: any) => {
        if (page.markdown) {
          keywords.forEach(keyword => {
            const count = (page.markdown.match(new RegExp(keyword, 'gi')) || []).length;
            topics[keyword] = (topics[keyword] || 0) + count;
          });
        }
      });
      
      console.log('\nContent Topic Analysis:');
      Object.entries(topics)
        .sort(([,a], [,b]) => b - a)
        .forEach(([topic, count]) => {
          console.log(`   - "${topic}": ${count} mentions`);
        });
    }
  });

  test('Tool 5: Search - Analyze SERP competition', async ({ page }) => {
    console.log('🔍 Analyzing SERP competition for key queries...');
    
    for (const query of SEO_TEST_TARGETS.searchQueries.slice(0, 2)) {
      console.log(`\nSearching: "${query}"`);
      
      const searchData = {
        query: query,
        limit: 10,
        lang: 'en',
        country: 'us',
        scrapeOptions: {
          formats: ['markdown'],
          onlyMainContent: true,
          waitFor: 2000
        }
      };

      try {
        const result = await callFirecrawlAPI('/search', 'POST', searchData);
        
        expect(result).toBeDefined();
        expect(result.success).toBe(true);
        
        console.log(`✅ Found ${result.data.length} results for "${query}"`);
        
        // Analyze competitor presence
        const competitorDomains = ['arlo.com', 'ring.com', 'nest.com', 'wyze.com', 'eufy.com'];
        const competitorResults = result.data.filter((item: any) => 
          competitorDomains.some(domain => item.url?.includes(domain))
        );
        
        console.log(`   - Competitor results: ${competitorResults.length}/${result.data.length}`);
        
        // Show top 5 results
        console.log('   - Top 5 results:');
        result.data.slice(0, 5).forEach((item: any, index: number) => {
          const domain = new URL(item.url).hostname;
          console.log(`     ${index + 1}. ${item.title} (${domain})`);
        });
        
      } catch (error) {
        console.log(`⚠️ Search failed for "${query}": ${error.message}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
  });

  test('Tool 6: Extract - Extract competitor product data', async ({ page }) => {
    console.log('🔍 Extracting structured product data from competitors...');
    
    const extractData = {
      urls: SEO_TEST_TARGETS.productPages.slice(0, 2),
      prompt: "Extract product information including name, price, key features, and technical specifications",
      schema: {
        type: "object",
        properties: {
          productName: { type: "string" },
          price: { 
            type: "object",
            properties: {
              current: { type: "string" },
              original: { type: "string" },
              discount: { type: "string" }
            }
          },
          keyFeatures: {
            type: "array",
            items: { type: "string" }
          },
          technicalSpecs: {
            type: "object",
            properties: {
              resolution: { type: "string" },
              fieldOfView: { type: "string" },
              nightVision: { type: "string" },
              weatherResistance: { type: "string" },
              connectivity: { type: "string" }
            }
          },
          ratings: {
            type: "object",
            properties: {
              average: { type: "number" },
              count: { type: "number" }
            }
          }
        },
        required: ["productName", "keyFeatures"]
      },
      systemPrompt: "You are an expert at extracting product information from e-commerce websites. Focus on security cameras and smart home devices."
    };

    const result = await callFirecrawlAPI('/extract', 'POST', extractData);
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    
    console.log('✅ Extracted competitor product data:');
    console.log(JSON.stringify(result.data, null, 2));
    
    // Store this data for Neo4j import
    if (result.data && Array.isArray(result.data)) {
      console.log('\n📊 Product Data Summary:');
      result.data.forEach((product: any, index: number) => {
        console.log(`\nProduct ${index + 1}:`);
        console.log(`   - Name: ${product.productName || 'Unknown'}`);
        console.log(`   - Price: ${product.price?.current || 'Not found'}`);
        console.log(`   - Features: ${product.keyFeatures?.length || 0} key features`);
        console.log(`   - Specs: ${Object.keys(product.technicalSpecs || {}).length} specifications`);
      });
    }
  });

  test('Tool 7: Deep Research - SEO and content strategy research', async ({ page }) => {
    console.log('🔍 Conducting deep research on SEO strategies...');
    
    const researchData = {
      query: "home security camera SEO strategies and content marketing best practices 2024",
      maxDepth: 3,
      timeLimit: 90,
      maxUrls: 30,
      includeDomains: [],
      excludeDomains: ['facebook.com', 'twitter.com', 'instagram.com']
    };

    const result = await callFirecrawlAPI('/research', 'POST', researchData);
    
    expect(result).toBeDefined();
    expect(result.success).toBe(true);
    
    console.log('✅ Deep research completed');
    
    if (result.data.finalAnalysis) {
      console.log('\n📋 Research Summary:');
      console.log(result.data.finalAnalysis.substring(0, 500) + '...');
      console.log(`\nTotal analysis length: ${result.data.finalAnalysis.length} characters`);
    }
    
    if (result.data.sources) {
      console.log(`\n📚 Sources analyzed: ${result.data.sources.length}`);
      console.log('Top sources:');
      result.data.sources.slice(0, 5).forEach((source: any, index: number) => {
        console.log(`   ${index + 1}. ${source.title || source.url}`);
      });
    }
  });

  test('Tool 8: Generate LLMs.txt - Analyze competitor AI policies', async ({ page }) => {
    console.log('🔍 Analyzing competitor LLMs.txt and AI policies...');
    
    const competitors = ['https://www.arlo.com', 'https://ring.com'];
    
    for (const competitor of competitors) {
      console.log(`\nGenerating LLMs.txt for ${competitor}`);
      
      const llmsData = {
        url: competitor,
        maxUrls: 50,
        showFullText: true
      };

      try {
        const result = await callFirecrawlAPI('/llms-txt', 'POST', llmsData);
        
        expect(result).toBeDefined();
        expect(result.success).toBe(true);
        
        console.log(`✅ Generated LLMs.txt for ${competitor}`);
        
        // Analyze the content
        const llmsTxt = result.data.llmsTxt || '';
        
        // Check for common patterns
        const hasRobotsTxt = llmsTxt.includes('robots.txt');
        const hasCrawlDelay = llmsTxt.includes('crawl-delay');
        const hasDisallow = llmsTxt.includes('disallow');
        const hasAllow = llmsTxt.includes('allow');
        
        console.log('   - Analysis:');
        console.log(`     • References robots.txt: ${hasRobotsTxt ? 'Yes' : 'No'}`);
        console.log(`     • Specifies crawl delay: ${hasCrawlDelay ? 'Yes' : 'No'}`);
        console.log(`     • Has disallow rules: ${hasDisallow ? 'Yes' : 'No'}`);
        console.log(`     • Has allow rules: ${hasAllow ? 'Yes' : 'No'}`);
        
        if (result.data.llmsFullTxt) {
          console.log(`     • Full content size: ${result.data.llmsFullTxt.length} characters`);
        }
        
      } catch (error) {
        console.log(`⚠️ Failed to generate LLMs.txt for ${competitor}: ${error.message}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  });
});

// Integration test with Neo4j
test.describe('Firecrawl to Neo4j Integration', () => {
  test('Complete SEO data pipeline', async ({ page }) => {
    console.log('🔄 Testing complete data pipeline from Firecrawl to Neo4j...');
    
    // Step 1: Discover URLs
    console.log('\n1️⃣ Discovering competitor URLs...');
    const mapResult = await callFirecrawlAPI('/map', 'POST', {
      url: 'https://www.wyze.com',
      limit: 20
    });
    
    const productUrls = mapResult.data.filter((url: string) => 
      url.includes('/product') || url.includes('/shop')
    ).slice(0, 5);
    
    console.log(`   Found ${productUrls.length} product URLs`);
    
    // Step 2: Extract structured data
    console.log('\n2️⃣ Extracting product data...');
    const extractResult = await callFirecrawlAPI('/extract', 'POST', {
      urls: productUrls,
      schema: {
        type: "object",
        properties: {
          url: { type: "string" },
          title: { type: "string" },
          description: { type: "string" },
          price: { type: "string" },
          keywords: { type: "array", items: { type: "string" } }
        }
      }
    });
    
    console.log(`   Extracted data from ${extractResult.data?.length || 0} products`);
    
    // Step 3: Format for Neo4j
    console.log('\n3️⃣ Formatting data for Neo4j import...');
    const neo4jData = {
      domain: 'wyze.com',
      products: extractResult.data || [],
      timestamp: new Date().toISOString()
    };
    
    console.log('✅ Data ready for Neo4j import:');
    console.log(JSON.stringify(neo4jData, null, 2));
    
    // This data would typically be imported using the import_competitor_data_to_neo4j.py script
    console.log('\n💡 To import this data to Neo4j, save it as JSON and run:');
    console.log('   python3 import_competitor_data_to_neo4j.py --json-file competitor_data.json');
  });
});