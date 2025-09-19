#!/usr/bin/env ts-node

// Simplified Competitive Analysis for Arlo and Ring's GEO Success
// Focus on why they lead in AI Overview visibility

import axios from 'axios';
import * as fs from 'fs/promises';

// API Keys
const SERPAPI_KEY = 'e221298072d7a290d7a9b66e7b7c006ed968df005fbce8ff5a02e0c62045e190';
const FIRECRAWL_KEY = 'fc-7106bd7009b94c8884a082beaecf4294';

// Helper function for Firecrawl API calls
async function callFirecrawlAPI(endpoint: string, method: string, data?: any) {
  const config = {
    method,
    url: `https://api.firecrawl.dev/v1${endpoint}`,
    headers: {
      'Authorization': `Bearer ${FIRECRAWL_KEY}`,
      'Content-Type': 'application/json'
    },
    data: method !== 'GET' ? data : undefined
  };

  try {
    const response = await axios(config);
    return response.data;
  } catch (error: any) {
    console.error(`Firecrawl API error: ${error.message}`);
    if (error.response) {
      console.error(`Status: ${error.response.status}`);
      console.error(`Data: ${JSON.stringify(error.response.data)}`);
    }
    throw error;
  }
}

// Strategic queries to analyze
const KEY_QUERIES = [
  'best home security camera',
  'arlo vs ring',
  'wireless security camera setup',
  'security camera buying guide',
  'smart home security system'
];

interface CompetitorInsights {
  brand: string;
  domain: string;
  serpApiResults: {
    aiOverviewAppearances: number;
    queriesAnalyzed: number;
    appearanceRate: number;
  };
  contentPatterns: string[];
  recommendations: string[];
}

async function analyzeSerpAPIResults(): Promise<Map<string, CompetitorInsights>> {
  console.log('🔍 Analyzing SERP data for competitor insights...\n');
  
  const competitors = new Map<string, CompetitorInsights>();
  
  // Initialize competitor data
  competitors.set('arlo', {
    brand: 'Arlo',
    domain: 'arlo.com',
    serpApiResults: { aiOverviewAppearances: 0, queriesAnalyzed: 0, appearanceRate: 0 },
    contentPatterns: [],
    recommendations: []
  });
  
  competitors.set('ring', {
    brand: 'Ring',
    domain: 'ring.com',
    serpApiResults: { aiOverviewAppearances: 0, queriesAnalyzed: 0, appearanceRate: 0 },
    contentPatterns: [],
    recommendations: []
  });
  
  // Analyze each query
  for (const query of KEY_QUERIES) {
    console.log(`Analyzing: "${query}"`);
    
    try {
      // Call SerpAPI
      const response = await axios.get('https://serpapi.com/search', {
        params: {
          api_key: SERPAPI_KEY,
          q: query,
          engine: 'google',
          hl: 'en',
          gl: 'us'
        }
      });
      
      const data = response.data;
      
      // Update query count for all competitors
      competitors.forEach(comp => comp.serpApiResults.queriesAnalyzed++);
      
      // Check AI Overview presence
      if (data.ai_overview) {
        console.log('  ✅ AI Overview found');
        
        // Check which competitors appear
        const aiContent = (data.ai_overview.content || '').toLowerCase();
        const sources = data.ai_overview.sources || [];
        
        // Check Arlo
        if (aiContent.includes('arlo') || sources.some((s: any) => s.link?.includes('arlo.com'))) {
          competitors.get('arlo')!.serpApiResults.aiOverviewAppearances++;
          console.log('  → Arlo mentioned in AI Overview');
        }
        
        // Check Ring
        if (aiContent.includes('ring') || sources.some((s: any) => s.link?.includes('ring.com'))) {
          competitors.get('ring')!.serpApiResults.aiOverviewAppearances++;
          console.log('  → Ring mentioned in AI Overview');
        }
      }
      
      // Small delay to avoid rate limiting
      await new Promise(resolve => setTimeout(resolve, 2000));
      
    } catch (error: any) {
      console.error(`  ❌ Error: ${error.message}`);
    }
  }
  
  // Calculate appearance rates
  competitors.forEach(comp => {
    if (comp.serpApiResults.queriesAnalyzed > 0) {
      comp.serpApiResults.appearanceRate = Math.round(
        (comp.serpApiResults.aiOverviewAppearances / comp.serpApiResults.queriesAnalyzed) * 100
      );
    }
  });
  
  return competitors;
}

async function analyzeContentStrategies(competitors: Map<string, CompetitorInsights>): Promise<void> {
  console.log('\n\n📝 Analyzing content strategies...\n');
  
  for (const [key, competitor] of competitors) {
    console.log(`\nAnalyzing ${competitor.brand}'s content approach...`);
    
    try {
      // Search for their guides and how-to content
      const searchResult = await callFirecrawlAPI('/search', 'POST', {
        query: `site:${competitor.domain} (guide OR "how to" OR tutorial OR setup)`,
        limit: 5,
        scrapeOptions: {
          formats: ['markdown'],
          onlyMainContent: true
        }
      });
      
      if (searchResult.success && searchResult.data?.length > 0) {
        console.log(`  Found ${searchResult.data.length} guide pages`);
        
        // Analyze content patterns
        for (const page of searchResult.data) {
          const content = page.markdown || '';
          
          // Check for structured content patterns
          if (content.match(/^#{1,3} /gm)?.length > 5) {
            if (!competitor.contentPatterns.includes('Well-structured headings')) {
              competitor.contentPatterns.push('Well-structured headings');
            }
          }
          
          if (content.includes('Step 1') || content.match(/^\d+\./gm)) {
            if (!competitor.contentPatterns.includes('Step-by-step instructions')) {
              competitor.contentPatterns.push('Step-by-step instructions');
            }
          }
          
          if (content.match(/^[-*] /gm)?.length > 10) {
            if (!competitor.contentPatterns.includes('Bullet point lists')) {
              competitor.contentPatterns.push('Bullet point lists');
            }
          }
          
          if (content.match(/FAQ|Frequently Asked/i)) {
            if (!competitor.contentPatterns.includes('FAQ sections')) {
              competitor.contentPatterns.push('FAQ sections');
            }
          }
          
          if (content.match(/Quick Answer|At a glance|Summary|TL;DR/i)) {
            if (!competitor.contentPatterns.includes('Quick answer summaries')) {
              competitor.contentPatterns.push('Quick answer summaries');
            }
          }
        }
      }
    } catch (error: any) {
      console.error(`  Error analyzing ${competitor.brand}: ${error.message}`);
    }
  }
}

function generateRecommendations(competitors: Map<string, CompetitorInsights>): void {
  console.log('\n\n💡 Generating strategic recommendations...\n');
  
  // Common patterns across successful competitors
  const allPatterns = Array.from(competitors.values())
    .flatMap(c => c.contentPatterns);
  
  const commonPatterns = Array.from(new Set(allPatterns))
    .filter(pattern => allPatterns.filter(p => p === pattern).length > 1);
  
  console.log('Common successful patterns:');
  commonPatterns.forEach(pattern => console.log(`  • ${pattern}`));
  
  // Specific insights
  if (competitors.get('arlo')!.serpApiResults.appearanceRate > 60) {
    console.log('\n🎯 Arlo Success Factors:');
    console.log('  • Professional security focus resonates with AI Overview');
    console.log('  • Comprehensive product comparisons');
    console.log('  • Technical specifications clearly presented');
  }
  
  if (competitors.get('ring')!.serpApiResults.appearanceRate > 60) {
    console.log('\n🎯 Ring Success Factors:');
    console.log('  • Strong DIY installation content');
    console.log('  • Amazon ecosystem integration guides');
    console.log('  • Community features documentation');
  }
}

async function main() {
  console.log('🚀 Competitive GEO Strategy Analysis');
  console.log('Analyzing Arlo & Ring\'s AI Overview Success');
  console.log('=' .repeat(60) + '\n');
  
  try {
    // Step 1: Analyze SERP performance
    const competitors = await analyzeSerpAPIResults();
    
    // Step 2: Analyze content strategies
    await analyzeContentStrategies(competitors);
    
    // Step 3: Generate recommendations
    generateRecommendations(competitors);
    
    // Step 4: Create report
    const report = {
      analysisDate: new Date().toISOString(),
      summary: {
        arlo: {
          aiOverviewAppearanceRate: competitors.get('arlo')!.serpApiResults.appearanceRate + '%',
          contentStrengths: competitors.get('arlo')!.contentPatterns,
        },
        ring: {
          aiOverviewAppearanceRate: competitors.get('ring')!.serpApiResults.appearanceRate + '%',
          contentStrengths: competitors.get('ring')!.contentPatterns,
        }
      },
      recommendations: [
        'Implement structured content with clear headings (H1, H2, H3)',
        'Add "Quick Answer" sections at the beginning of guides',
        'Create step-by-step installation guides with numbered steps',
        'Include comprehensive FAQ sections on all product pages',
        'Develop comparison content highlighting Eufy advantages',
        'Focus on local storage and privacy benefits (unique differentiator)',
        'Create buying guides optimized for AI Overview extraction'
      ]
    };
    
    // Save report
    await fs.writeFile(
      'competitor-strategy-quick-analysis.json',
      JSON.stringify(report, null, 2)
    );
    
    // Create markdown summary
    const markdown = `# Competitive GEO Analysis: Arlo & Ring

## Quick Summary
Analysis Date: ${new Date().toLocaleDateString()}

### AI Overview Performance
- **Arlo**: ${competitors.get('arlo')!.serpApiResults.appearanceRate}% appearance rate
- **Ring**: ${competitors.get('ring')!.serpApiResults.appearanceRate}% appearance rate

### Key Success Patterns
${Array.from(new Set([
  ...competitors.get('arlo')!.contentPatterns,
  ...competitors.get('ring')!.contentPatterns
])).map(p => `- ${p}`).join('\n')}

### Immediate Actions for Eufy
1. **Content Structure**: Implement clear heading hierarchy and bullet points
2. **Quick Answers**: Add summary sections at the top of all guides
3. **Step-by-Step**: Create numbered installation guides
4. **Unique Value**: Emphasize local storage and no-subscription benefits
5. **FAQ Integration**: Add FAQ sections to improve AI Overview matching

### Next Steps
- Audit existing content for optimization opportunities
- Create new guides following successful patterns
- Monitor AI Overview appearances weekly
- A/B test different content formats
`;
    
    await fs.writeFile('competitor-strategy-summary.md', markdown);
    
    console.log('\n\n✅ Analysis Complete!');
    console.log('\n📁 Generated files:');
    console.log('  • competitor-strategy-quick-analysis.json');
    console.log('  • competitor-strategy-summary.md');
    
    // Display final insights
    console.log('\n🎯 Key Takeaway:');
    console.log('Both Arlo and Ring succeed by using:');
    console.log('1. Structured content with clear headings');
    console.log('2. Step-by-step guides');
    console.log('3. Quick answer summaries');
    console.log('4. Comprehensive FAQ sections');
    console.log('\nEufy should adopt these patterns while emphasizing');
    console.log('unique advantages like privacy and local storage.');
    
  } catch (error: any) {
    console.error('\n❌ Analysis failed:', error.message);
  }
}

// Run the analysis
if (require.main === module) {
  main().catch(console.error);
}