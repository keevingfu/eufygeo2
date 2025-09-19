import { test, expect } from '@playwright/test';
import { createSerpAPIClient, analyzeCompetitorPresence, calculateGEOScore } from './serpapi-client';
import { callFirecrawlAPI } from '../firecrawl/test-config';
import { EUFY_COMPETITORS, SEO_TEST_QUERIES } from '../firecrawl/test-config';

// SerpAPI configuration
const SERPAPI_KEY = process.env.SERPAPI_KEY || 'e221298072d7a290d7a9b66e7b7c006ed968df005fbce8ff5a02e0c62045e190';

// Enhanced GEO queries including new AI-focused searches
const ENHANCED_GEO_QUERIES = {
  ...SEO_TEST_QUERIES,
  aiOptimized: [
    "explain home security camera features",
    "compare wireless security camera brands",
    "how to choose security camera system",
    "security camera installation guide",
    "smart home security camera setup"
  ],
  brandSpecific: [
    "is eufy security camera good",
    "arlo camera review",
    "ring doorbell pros and cons",
    "nest camera features",
    "wyze camera vs eufy"
  ]
};

// Data structure for enhanced results
interface EnhancedGEOResult {
  query: string;
  timestamp: string;
  serpApiData: {
    hasAIOverview: boolean;
    aiOverviewContent?: string;
    aiOverviewSources?: Array<{ title: string; link: string; snippet?: string }>;
    featuredSnippet?: any;
    organicResults: Array<{ position: number; domain: string; title: string; url: string }>;
    serpFeatures: string[];
  };
  firecrawlData?: {
    scraped: boolean;
    content?: string;
    error?: string;
  };
  competitorAnalysis: {
    [brand: string]: {
      geoScore: number;
      aiOverviewMention: boolean;
      aiOverviewSources: number;
      organicPositions: number[];
      featuredInSnippet: boolean;
    };
  };
  recommendations: string[];
}

test.describe('Enhanced GEO Tracker with SerpAPI Integration', () => {
  const serpClient = createSerpAPIClient(SERPAPI_KEY);
  const enhancedResults: EnhancedGEOResult[] = [];

  test.beforeAll(async () => {
    console.log('🚀 Enhanced GEO Visibility Tracker');
    console.log('=====================================');
    console.log('Combining SerpAPI and Firecrawl for comprehensive analysis\n');
  });

  test('Analyze AI-optimized queries with SerpAPI', async ({ page }) => {
    console.log('🔍 Analyzing AI-optimized queries...\n');

    for (const query of ENHANCED_GEO_QUERIES.aiOptimized.slice(0, 3)) {
      console.log(`\n📊 Query: "${query}"`);
      
      try {
        // Get SERP data from SerpAPI
        const serpData = await serpClient.analyzeSERP(query);
        
        // Analyze AI Overview visibility
        const aiOverviewAnalysis = await serpClient.getAIOverviewVisibility(query);
        
        // Initialize result
        const result: EnhancedGEOResult = {
          query,
          timestamp: new Date().toISOString(),
          serpApiData: {
            hasAIOverview: aiOverviewAnalysis.hasAIOverview,
            aiOverviewContent: aiOverviewAnalysis.aiOverview?.content,
            aiOverviewSources: aiOverviewAnalysis.aiOverview?.sources,
            featuredSnippet: serpData.featuredSnippet,
            organicResults: serpData.organicResults,
            serpFeatures: serpData.serpFeatures
          },
          competitorAnalysis: {},
          recommendations: []
        };

        // Analyze each competitor
        const competitors = ['eufy', 'arlo', 'ring', 'nest', 'wyze'];
        
        console.log(`\n✅ AI Overview: ${aiOverviewAnalysis.hasAIOverview ? 'Present' : 'Not present'}`);
        
        if (aiOverviewAnalysis.hasAIOverview) {
          console.log(`📝 Sources cited: ${aiOverviewAnalysis.aiOverview?.sources?.length || 0}`);
          
          // Analyze competitor presence
          const competitorPresence = analyzeCompetitorPresence(aiOverviewAnalysis.aiOverview, competitors);
          
          console.log('\n🏆 Competitor presence in AI Overview:');
          competitors.forEach(brand => {
            const presence = competitorPresence[brand];
            const visibility = aiOverviewAnalysis.competitorVisibility[`${brand}.com`] || 
                             aiOverviewAnalysis.competitorVisibility[`${brand === 'nest' ? 'google.com/nest' : brand + '.com'}`];
            
            const organicPositions = serpData.competitorRankings[`${brand}.com`] || [];
            const geoScore = calculateGEOScore(
              true,
              presence.mentioned || visibility?.mentioned,
              presence.sourceCount + (visibility?.citations || 0),
              organicPositions[0]
            );

            result.competitorAnalysis[brand] = {
              geoScore,
              aiOverviewMention: presence.mentioned || visibility?.mentioned || false,
              aiOverviewSources: presence.sourceCount + (visibility?.citations || 0),
              organicPositions,
              featuredInSnippet: false
            };

            if (presence.mentioned || visibility?.mentioned) {
              console.log(`   ✓ ${brand}: GEO Score ${geoScore}/100 (Mentioned: Yes, Sources: ${presence.sourceCount})`);
            } else {
              console.log(`   ✗ ${brand}: GEO Score ${geoScore}/100 (Not mentioned in AI Overview)`);
            }
          });
        } else {
          // No AI Overview, calculate scores based on organic rankings
          competitors.forEach(brand => {
            const organicPositions = serpData.competitorRankings[`${brand}.com`] || [];
            const geoScore = calculateGEOScore(false, false, 0, organicPositions[0]);
            
            result.competitorAnalysis[brand] = {
              geoScore,
              aiOverviewMention: false,
              aiOverviewSources: 0,
              organicPositions,
              featuredInSnippet: false
            };
          });
        }

        // Check featured snippet
        if (serpData.featuredSnippet) {
          console.log('\n📌 Featured Snippet present');
          const snippetDomain = new URL(serpData.featuredSnippet.link).hostname;
          competitors.forEach(brand => {
            if (snippetDomain.includes(brand)) {
              result.competitorAnalysis[brand].featuredInSnippet = true;
              console.log(`   ✓ Owned by: ${brand}`);
            }
          });
        }

        // Generate recommendations
        result.recommendations = generateGEORecommendations(result);
        
        // Store result
        enhancedResults.push(result);
        
      } catch (error) {
        console.error(`❌ Error analyzing query "${query}":`, error.message);
      }
      
      // Rate limiting
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  });

  test('Compare brand-specific queries', async ({ page }) => {
    console.log('\n🔍 Analyzing brand-specific queries...\n');

    for (const query of ENHANCED_GEO_QUERIES.brandSpecific.slice(0, 3)) {
      console.log(`\n📊 Query: "${query}"`);
      
      try {
        // SerpAPI analysis
        const serpData = await serpClient.analyzeSERP(query);
        const aiOverviewAnalysis = await serpClient.getAIOverviewVisibility(query);
        
        // Optional: Enhance with Firecrawl data for top results
        let firecrawlData = { scraped: false, content: undefined, error: undefined };
        
        if (serpData.organicResults.length > 0) {
          try {
            const topUrl = serpData.organicResults[0].url;
            const scrapeResult = await callFirecrawlAPI('/scrape', 'POST', {
              url: topUrl,
              formats: ['markdown'],
              onlyMainContent: true,
              timeout: 30000
            });
            
            if (scrapeResult.success) {
              firecrawlData = {
                scraped: true,
                content: scrapeResult.data.markdown
              };
            }
          } catch (error) {
            firecrawlData.error = error.message;
          }
        }

        // Create enhanced result
        const result: EnhancedGEOResult = {
          query,
          timestamp: new Date().toISOString(),
          serpApiData: {
            hasAIOverview: aiOverviewAnalysis.hasAIOverview,
            aiOverviewContent: aiOverviewAnalysis.aiOverview?.content,
            aiOverviewSources: aiOverviewAnalysis.aiOverview?.sources,
            featuredSnippet: serpData.featuredSnippet,
            organicResults: serpData.organicResults.slice(0, 10),
            serpFeatures: serpData.serpFeatures
          },
          firecrawlData,
          competitorAnalysis: {},
          recommendations: []
        };

        // Display results
        console.log(`✅ AI Overview: ${aiOverviewAnalysis.hasAIOverview ? 'Present' : 'Not present'}`);
        console.log(`📋 SERP Features: ${serpData.serpFeatures.join(', ')}`);
        console.log(`🔗 Top result: ${serpData.organicResults[0]?.domain || 'N/A'}`);
        
        if (firecrawlData.scraped) {
          console.log(`📄 Enhanced with content analysis (${firecrawlData.content?.length} chars)`);
        }

        enhancedResults.push(result);
        
      } catch (error) {
        console.error(`❌ Error analyzing query "${query}":`, error.message);
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  });

  test('Validate results with Firecrawl cross-check', async ({ page }) => {
    console.log('\n🔄 Cross-validating with Firecrawl...\n');

    // Select queries that showed AI Overview in SerpAPI
    const queriesWithAI = enhancedResults
      .filter(r => r.serpApiData.hasAIOverview)
      .slice(0, 2);

    for (const result of queriesWithAI) {
      console.log(`\n🔍 Validating: "${result.query}"`);
      
      try {
        // Use Firecrawl to search and scrape
        const searchData = {
          query: result.query,
          limit: 5,
          lang: 'en',
          country: 'us',
          scrapeOptions: {
            formats: ['markdown', 'html'],
            onlyMainContent: false,
            waitFor: 3000
          }
        };

        const firecrawlSearch = await callFirecrawlAPI('/search', 'POST', searchData);
        
        if (firecrawlSearch.success && firecrawlSearch.data?.length > 0) {
          console.log(`✅ Firecrawl found ${firecrawlSearch.data.length} results`);
          
          // Compare top domains
          const serpTopDomains = result.serpApiData.organicResults.slice(0, 5).map(r => r.domain);
          const firecrawlDomains = firecrawlSearch.data.map((r: any) => new URL(r.url).hostname);
          
          const overlap = serpTopDomains.filter(d => firecrawlDomains.includes(d));
          console.log(`🔄 Domain overlap: ${overlap.length}/5 (${overlap.join(', ')})`);
          
          // Update result with validation data
          result.firecrawlData = {
            scraped: true,
            content: `Validated with ${firecrawlSearch.data.length} results`
          };
        }
        
      } catch (error) {
        console.error(`⚠️ Firecrawl validation error: ${error.message}`);
      }
    }
  });

  test('Generate comprehensive GEO report', async ({ page }) => {
    console.log('\n📈 Generating Enhanced GEO Visibility Report...\n');

    // Overall statistics
    const totalQueries = enhancedResults.length;
    const queriesWithAI = enhancedResults.filter(r => r.serpApiData.hasAIOverview).length;
    const aiRate = (queriesWithAI / totalQueries * 100).toFixed(1);

    console.log('📊 Summary Statistics:');
    console.log(`   - Total queries analyzed: ${totalQueries}`);
    console.log(`   - Queries with AI Overview: ${queriesWithAI} (${aiRate}%)`);
    console.log(`   - Data sources: SerpAPI + Firecrawl validation`);

    // Competitor GEO scores
    const competitorScores: Record<string, { totalScore: number; appearances: number; avgScore: number }> = {};
    const competitors = ['eufy', 'arlo', 'ring', 'nest', 'wyze'];

    competitors.forEach(brand => {
      competitorScores[brand] = { totalScore: 0, appearances: 0, avgScore: 0 };
    });

    enhancedResults.forEach(result => {
      competitors.forEach(brand => {
        if (result.competitorAnalysis[brand]) {
          competitorScores[brand].totalScore += result.competitorAnalysis[brand].geoScore;
          competitorScores[brand].appearances += 1;
        }
      });
    });

    // Calculate average scores
    competitors.forEach(brand => {
      const score = competitorScores[brand];
      score.avgScore = score.appearances > 0 ? score.totalScore / score.appearances : 0;
    });

    // Rank by average GEO score
    console.log('\n🏆 Competitor GEO Visibility Rankings:');
    const rankings = Object.entries(competitorScores)
      .sort(([,a], [,b]) => b.avgScore - a.avgScore)
      .map(([brand, score], index) => ({
        rank: index + 1,
        brand,
        avgScore: score.avgScore.toFixed(1),
        appearances: score.appearances
      }));

    rankings.forEach(({ rank, brand, avgScore, appearances }) => {
      console.log(`${rank}. ${brand.charAt(0).toUpperCase() + brand.slice(1)}:`);
      console.log(`   - Average GEO Score: ${avgScore}/100`);
      console.log(`   - Analyzed queries: ${appearances}`);
    });

    // Key insights
    console.log('\n💡 Key Insights:');
    
    // Find queries where Eufy performs well
    const eufyWins = enhancedResults.filter(r => {
      const eufyScore = r.competitorAnalysis.eufy?.geoScore || 0;
      const maxScore = Math.max(...competitors.map(c => r.competitorAnalysis[c]?.geoScore || 0));
      return eufyScore === maxScore && eufyScore > 0;
    });

    console.log(`   - Eufy leads in ${eufyWins.length} queries:`);
    eufyWins.forEach(win => {
      console.log(`     • "${win.query}" (Score: ${win.competitorAnalysis.eufy.geoScore})`);
    });

    // Opportunities
    const opportunities = enhancedResults.filter(r => {
      const eufyScore = r.competitorAnalysis.eufy?.geoScore || 0;
      return r.serpApiData.hasAIOverview && eufyScore < 50;
    });

    console.log(`\n   - Improvement opportunities: ${opportunities.length} queries`);
    opportunities.slice(0, 3).forEach(opp => {
      console.log(`     • "${opp.query}" - Current score: ${opp.competitorAnalysis.eufy?.geoScore || 0}/100`);
    });

    // Save enhanced results
    const fs = require('fs').promises;
    const enhancedReport = {
      metadata: {
        analysisDate: new Date().toISOString(),
        totalQueries,
        queriesWithAI,
        aiOverviewRate: parseFloat(aiRate),
        dataSource: 'SerpAPI + Firecrawl'
      },
      competitorRankings: rankings,
      queryResults: enhancedResults,
      insights: {
        eufyWins: eufyWins.map(w => w.query),
        opportunities: opportunities.map(o => ({
          query: o.query,
          currentScore: o.competitorAnalysis.eufy?.geoScore || 0,
          recommendations: o.recommendations
        }))
      }
    };

    await fs.writeFile(
      'enhanced-geo-visibility-results.json',
      JSON.stringify(enhancedReport, null, 2)
    );

    console.log('\n✅ Enhanced report saved to: enhanced-geo-visibility-results.json');
  });
});

// Helper function to generate GEO optimization recommendations
function generateGEORecommendations(result: EnhancedGEOResult): string[] {
  const recommendations: string[] = [];
  const eufyAnalysis = result.competitorAnalysis.eufy;

  if (!eufyAnalysis || eufyAnalysis.geoScore < 50) {
    if (!result.serpApiData.hasAIOverview) {
      recommendations.push('Create comprehensive content that could trigger AI Overview');
      recommendations.push('Include structured data and clear headings');
    } else if (!eufyAnalysis?.aiOverviewMention) {
      recommendations.push('Optimize content to be cited in AI Overview');
      recommendations.push('Create authoritative guides with unique insights');
      recommendations.push('Use question-answer format for better AI comprehension');
    }

    if (!eufyAnalysis?.organicPositions.length || eufyAnalysis.organicPositions[0] > 5) {
      recommendations.push('Improve organic rankings through traditional SEO');
      recommendations.push('Target long-tail keywords related to this query');
    }

    if (result.serpApiData.featuredSnippet && !eufyAnalysis?.featuredInSnippet) {
      recommendations.push('Optimize for featured snippet with concise answers');
      recommendations.push('Use lists, tables, and structured formats');
    }
  }

  return recommendations;
}

// Additional test for location-based GEO visibility
test.describe('Location-Based GEO Analysis', () => {
  test('Compare GEO visibility across locations', async ({ page }) => {
    console.log('\n🌍 Analyzing location-based GEO visibility...\n');

    const serpClient = createSerpAPIClient(SERPAPI_KEY);
    const testQuery = 'best home security camera';
    const locations = ['United States', 'United Kingdom', 'Canada', 'Australia'];

    for (const location of locations) {
      console.log(`\n📍 Location: ${location}`);
      
      try {
        const result = await serpClient.searchByLocation(testQuery, location);
        const hasAI = !!result.ai_overview;
        
        console.log(`   - AI Overview: ${hasAI ? 'Present' : 'Not present'}`);
        
        if (hasAI && result.ai_overview?.sources) {
          console.log(`   - Sources: ${result.ai_overview.sources.length}`);
          
          // Check for Eufy presence
          const eufyMentioned = result.ai_overview.sources.some(s => 
            s.link?.includes('eufy') || s.title?.toLowerCase().includes('eufy')
          );
          
          console.log(`   - Eufy mentioned: ${eufyMentioned ? 'Yes' : 'No'}`);
        }
        
      } catch (error) {
        console.error(`   ❌ Error: ${error.message}`);
      }
      
      await new Promise(resolve => setTimeout(resolve, 2000));
    }
  });
});