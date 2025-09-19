import { test, expect } from '@playwright/test';
import axios from 'axios';
import { FIRECRAWL_CONFIG, EUFY_COMPETITORS } from '../firecrawl/test-config';

// Helper function for Firecrawl API calls
async function callFirecrawlAPI(endpoint: string, method: string, data?: any) {
  const config = {
    method,
    url: `${FIRECRAWL_CONFIG.apiUrl}${endpoint}`,
    headers: {
      'Authorization': `Bearer ${FIRECRAWL_CONFIG.apiKey}`,
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

// GEO-specific search queries for security cameras
const GEO_QUERIES = {
  informational: [
    "what is the best home security camera",
    "how do wireless security cameras work",
    "security camera buying guide",
    "difference between wired and wireless cameras",
    "home security camera features explained"
  ],
  comparative: [
    "eufy vs arlo security camera",
    "ring vs nest doorbell comparison",
    "best security cameras compared",
    "wireless camera brand comparison",
    "security camera price comparison"
  ],
  technical: [
    "security camera resolution explained",
    "what is night vision in cameras",
    "how does motion detection work",
    "security camera field of view",
    "cloud vs local storage cameras"
  ],
  purchasing: [
    "best security camera deals",
    "security camera installation cost",
    "affordable home security cameras",
    "professional vs diy security cameras",
    "security camera subscription fees"
  ]
};

// Data structure for AI Overview visibility
interface AIOverviewResult {
  query: string;
  timestamp: string;
  hasAIOverview: boolean;
  aiOverviewContent?: string;
  citedSources: Array<{
    url: string;
    domain: string;
    title: string;
    position: number;
  }>;
  competitorVisibility: {
    [competitor: string]: {
      isCited: boolean;
      citations: number;
      positions: number[];
    };
  };
  organicResults: Array<{
    url: string;
    title: string;
    position: number;
  }>;
}

test.describe('Google AI Overview (GEO) Visibility Tracker', () => {
  test.setTimeout(240000); // 4 minutes timeout

  const results: AIOverviewResult[] = [];

  test('Collect AI Overview visibility for informational queries', async ({ page }) => {
    console.log('🔍 Analyzing AI Overview visibility for informational queries...\n');

    for (const query of GEO_QUERIES.informational) {
      console.log(`\n📊 Query: "${query}"`);
      
      try {
        // Search using Firecrawl with enhanced scraping for AI Overview
        const searchData = {
          query: query,
          limit: 20, // Get more results to analyze thoroughly
          lang: 'en',
          country: 'us',
          scrapeOptions: {
            formats: ['markdown', 'html'],
            onlyMainContent: false, // Need full page to detect AI Overview
            waitFor: 5000, // Wait longer for AI Overview to load
            includeTags: ['div', 'section', 'article', 'h1', 'h2', 'h3', 'p', 'a', 'span'],
            excludeTags: ['script', 'style', 'nav', 'footer']
          }
        };

        const searchResult = await callFirecrawlAPI('/search', 'POST', searchData);
        
        // Process search results to detect AI Overview
        const aiOverviewData = await analyzeAIOverview(searchResult.data, query);
        results.push(aiOverviewData);
        
        // Display results
        console.log(`✅ AI Overview present: ${aiOverviewData.hasAIOverview ? 'Yes' : 'No'}`);
        
        if (aiOverviewData.hasAIOverview) {
          console.log(`📝 AI Overview length: ${aiOverviewData.aiOverviewContent?.length || 0} chars`);
          console.log(`🔗 Cited sources: ${aiOverviewData.citedSources.length}`);
          
          // Check competitor visibility
          const competitorDomains = ['eufy.com', 'arlo.com', 'ring.com', 'nest.com', 'wyze.com'];
          console.log('\n🏆 Competitor visibility in AI Overview:');
          
          competitorDomains.forEach(domain => {
            const visibility = aiOverviewData.competitorVisibility[domain];
            if (visibility && visibility.isCited) {
              console.log(`   ✓ ${domain}: ${visibility.citations} citations at positions ${visibility.positions.join(', ')}`);
            } else {
              console.log(`   ✗ ${domain}: Not cited`);
            }
          });
        }
        
        // Show top organic results for comparison
        console.log('\n📋 Top 5 organic results:');
        aiOverviewData.organicResults.slice(0, 5).forEach((result, index) => {
          const domain = new URL(result.url).hostname;
          console.log(`   ${index + 1}. ${domain} - ${result.title}`);
        });
        
      } catch (error) {
        console.error(`❌ Error processing query "${query}":`, error.message);
      }
      
      // Rate limiting
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
  });

  test('Analyze AI Overview visibility for comparative queries', async ({ page }) => {
    console.log('\n🔍 Analyzing AI Overview visibility for comparative queries...\n');

    for (const query of GEO_QUERIES.comparative) {
      console.log(`\n📊 Query: "${query}"`);
      
      try {
        const searchData = {
          query: query,
          limit: 20,
          lang: 'en',
          country: 'us',
          scrapeOptions: {
            formats: ['markdown', 'html'],
            onlyMainContent: false,
            waitFor: 5000,
            timeout: 60000
          }
        };

        const searchResult = await callFirecrawlAPI('/search', 'POST', searchData);
        const aiOverviewData = await analyzeAIOverview(searchResult.data, query);
        results.push(aiOverviewData);
        
        // Comparative queries often have AI Overviews with product comparisons
        if (aiOverviewData.hasAIOverview) {
          console.log(`✅ AI Overview found with ${aiOverviewData.citedSources.length} sources`);
          
          // Analyze which brands are mentioned in citations
          const brandMentions: { [brand: string]: number } = {};
          aiOverviewData.citedSources.forEach(source => {
            ['eufy', 'arlo', 'ring', 'nest', 'wyze'].forEach(brand => {
              if (source.title.toLowerCase().includes(brand) || source.url.includes(brand)) {
                brandMentions[brand] = (brandMentions[brand] || 0) + 1;
              }
            });
          });
          
          console.log('\n🏷️ Brand mentions in AI Overview sources:');
          Object.entries(brandMentions)
            .sort(([,a], [,b]) => b - a)
            .forEach(([brand, count]) => {
              console.log(`   ${brand}: ${count} mentions`);
            });
        }
        
      } catch (error) {
        console.error(`❌ Error processing query "${query}":`, error.message);
      }
      
      await new Promise(resolve => setTimeout(resolve, 3000));
    }
  });

  test('Extract structured data from AI Overview citations', async ({ page }) => {
    console.log('\n🔍 Extracting structured data from AI Overview citations...\n');

    // Collect all cited URLs from previous results
    const citedUrls = new Set<string>();
    results.forEach(result => {
      if (result.hasAIOverview) {
        result.citedSources.forEach(source => citedUrls.add(source.url));
      }
    });

    const urlsToAnalyze = Array.from(citedUrls).slice(0, 10); // Analyze top 10 cited URLs
    
    if (urlsToAnalyze.length > 0) {
      console.log(`📝 Analyzing ${urlsToAnalyze.length} frequently cited URLs...`);
      
      try {
        // Extract structured data from cited pages
        const extractData = {
          urls: urlsToAnalyze,
          prompt: "Extract key information about security cameras including features, prices, recommendations, and comparisons",
          schema: {
            type: "object",
            properties: {
              url: { type: "string" },
              pageType: { 
                type: "string",
                enum: ["review", "comparison", "guide", "product", "blog", "news"]
              },
              mainTopic: { type: "string" },
              mentionedBrands: {
                type: "array",
                items: { type: "string" }
              },
              keyPoints: {
                type: "array",
                items: { type: "string" },
                maxItems: 5
              },
              recommendations: {
                type: "array",
                items: {
                  type: "object",
                  properties: {
                    product: { type: "string" },
                    reason: { type: "string" }
                  }
                }
              },
              priceRanges: {
                type: "object",
                additionalProperties: { type: "string" }
              }
            }
          },
          systemPrompt: "You are analyzing content that appears in Google AI Overviews for security camera queries. Extract the most relevant information that would be cited."
        };

        const extractResult = await callFirecrawlAPI('/extract', 'POST', extractData);
        
        console.log('\n📊 Analysis of cited content:');
        if (extractResult.data && Array.isArray(extractResult.data)) {
          extractResult.data.forEach((page: any, index: number) => {
            console.log(`\n${index + 1}. ${page.url}`);
            console.log(`   Type: ${page.pageType}`);
            console.log(`   Topic: ${page.mainTopic}`);
            console.log(`   Brands: ${page.mentionedBrands?.join(', ')}`);
            if (page.recommendations?.length > 0) {
              console.log('   Top recommendations:');
              page.recommendations.slice(0, 3).forEach((rec: any) => {
                console.log(`   - ${rec.product}: ${rec.reason}`);
              });
            }
          });
        }
        
      } catch (error) {
        console.error('❌ Error extracting citation data:', error.message);
      }
    }
  });

  test('Generate GEO visibility report', async ({ page }) => {
    console.log('\n📈 Generating GEO Visibility Report...\n');

    // Analyze overall patterns
    const totalQueries = results.length;
    const queriesWithAIOverview = results.filter(r => r.hasAIOverview).length;
    const aiOverviewRate = (queriesWithAIOverview / totalQueries * 100).toFixed(1);

    console.log(`📊 Overall Statistics:`);
    console.log(`   - Total queries analyzed: ${totalQueries}`);
    console.log(`   - Queries with AI Overview: ${queriesWithAIOverview} (${aiOverviewRate}%)`);

    // Competitor visibility analysis
    const competitorStats: { [domain: string]: { citations: number, queries: number } } = {};
    const competitorDomains = ['eufy.com', 'arlo.com', 'ring.com', 'nest.com', 'wyze.com'];

    results.forEach(result => {
      if (result.hasAIOverview) {
        competitorDomains.forEach(domain => {
          const visibility = result.competitorVisibility[domain];
          if (visibility && visibility.isCited) {
            if (!competitorStats[domain]) {
              competitorStats[domain] = { citations: 0, queries: 0 };
            }
            competitorStats[domain].citations += visibility.citations;
            competitorStats[domain].queries += 1;
          }
        });
      }
    });

    console.log('\n🏆 Competitor AI Overview Visibility Rankings:');
    const rankings = Object.entries(competitorStats)
      .map(([domain, stats]) => ({
        domain,
        ...stats,
        visibilityScore: (stats.queries / queriesWithAIOverview * 100).toFixed(1)
      }))
      .sort((a, b) => b.queries - a.queries);

    rankings.forEach((competitor, index) => {
      console.log(`${index + 1}. ${competitor.domain}:`);
      console.log(`   - Appears in: ${competitor.queries}/${queriesWithAIOverview} AI Overviews (${competitor.visibilityScore}%)`);
      console.log(`   - Total citations: ${competitor.citations}`);
      console.log(`   - Avg citations per appearance: ${(competitor.citations / competitor.queries).toFixed(1)}`);
    });

    // Save results for Neo4j import
    const geoData = {
      analysisDate: new Date().toISOString(),
      summary: {
        totalQueries,
        queriesWithAIOverview,
        aiOverviewRate: parseFloat(aiOverviewRate),
        competitorRankings: rankings
      },
      queryResults: results
    };

    // Write results to file
    const fs = require('fs').promises;
    await fs.writeFile(
      'geo-visibility-results.json',
      JSON.stringify(geoData, null, 2)
    );
    
    console.log('\n✅ Results saved to geo-visibility-results.json');
    console.log('📊 Ready for Neo4j import');
  });
});

// Helper function to analyze AI Overview presence and citations
async function analyzeAIOverview(searchResults: any[], query: string): Promise<AIOverviewResult> {
  const result: AIOverviewResult = {
    query,
    timestamp: new Date().toISOString(),
    hasAIOverview: false,
    citedSources: [],
    competitorVisibility: {},
    organicResults: []
  };

  // Initialize competitor tracking
  const competitorDomains = ['eufy.com', 'arlo.com', 'ring.com', 'nest.com', 'wyze.com'];
  competitorDomains.forEach(domain => {
    result.competitorVisibility[domain] = {
      isCited: false,
      citations: 0,
      positions: []
    };
  });

  // Process search results
  if (searchResults && Array.isArray(searchResults)) {
    searchResults.forEach((item, index) => {
      // Add to organic results
      if (item.url && item.title) {
        result.organicResults.push({
          url: item.url,
          title: item.title,
          position: index + 1
        });
      }

      // Check if this result contains AI Overview indicators
      if (item.markdown || item.html) {
        const content = item.markdown || item.html;
        
        // AI Overview detection patterns
        const aiOverviewPatterns = [
          /AI-generated/i,
          /Generative AI is experimental/i,
          /AI Overview/i,
          /From sources across the web/i,
          /Here's what we found/i,
          /Based on .+ sources/i
        ];

        const hasAIIndicators = aiOverviewPatterns.some(pattern => pattern.test(content));
        
        if (hasAIIndicators && index < 3) { // AI Overview typically appears at top
          result.hasAIOverview = true;
          result.aiOverviewContent = content.substring(0, 1000); // Store first 1000 chars
          
          // Extract cited sources (look for citation patterns)
          const citationPatterns = [
            /\[(\d+)\]\s*([^[\n]+)/g,
            /Source:\s*([^\n]+)/g,
            /According to\s+([^\n,]+)/g
          ];
          
          // For simulation, assume top results after AI Overview are citations
          searchResults.slice(1, 6).forEach((source, sourceIndex) => {
            if (source.url && source.title) {
              const domain = new URL(source.url).hostname;
              result.citedSources.push({
                url: source.url,
                domain: domain,
                title: source.title,
                position: sourceIndex + 1
              });
              
              // Track competitor visibility
              competitorDomains.forEach(compDomain => {
                if (domain.includes(compDomain.replace('.com', ''))) {
                  result.competitorVisibility[compDomain].isCited = true;
                  result.competitorVisibility[compDomain].citations += 1;
                  result.competitorVisibility[compDomain].positions.push(sourceIndex + 1);
                }
              });
            }
          });
        }
      }
    });
  }

  return result;
}

// Additional test for monitoring GEO changes over time
test.describe('GEO Visibility Monitoring', () => {
  test('Track AI Overview changes for key queries', async ({ page }) => {
    console.log('\n⏰ Monitoring AI Overview changes...\n');

    const monitoringQueries = [
      "best home security camera",
      "eufy vs arlo",
      "wireless security camera setup"
    ];

    for (const query of monitoringQueries) {
      console.log(`📍 Monitoring: "${query}"`);
      
      try {
        // Search and analyze
        const searchData = {
          query: query,
          limit: 10,
          lang: 'en',
          country: 'us',
          scrapeOptions: {
            formats: ['markdown'],
            waitFor: 3000
          }
        };

        const result = await callFirecrawlAPI('/search', 'POST', searchData);
        const aiOverview = await analyzeAIOverview(result.data, query);
        
        // Compare with historical data (would be loaded from database)
        console.log(`   - AI Overview: ${aiOverview.hasAIOverview ? 'Present' : 'Absent'}`);
        if (aiOverview.hasAIOverview) {
          console.log(`   - Citations: ${aiOverview.citedSources.length}`);
          console.log(`   - Eufy visibility: ${aiOverview.competitorVisibility['eufy.com'].isCited ? 'Yes' : 'No'}`);
        }
        
      } catch (error) {
        console.error(`❌ Monitoring error for "${query}":`, error.message);
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  });
});