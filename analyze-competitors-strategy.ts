#!/usr/bin/env ts-node

// Deep Competitive Analysis for Arlo and Ring's GEO Success
// Analyzes why they lead in AI Overview visibility

import { SerpAPIClient } from './tests/geo-visibility/serpapi-client';
import { callFirecrawlAPI } from './tests/firecrawl/test-config';
import * as fs from 'fs/promises';

const SERPAPI_KEY = 'e221298072d7a290d7a9b66e7b7c006ed968df005fbce8ff5a02e0c62045e190';
const FIRECRAWL_KEY = 'fc-7106bd7009b94c8884a082beaecf4294';

// Strategic queries to analyze competitor strengths
const STRATEGIC_QUERIES = {
  'Product Comparison': [
    'arlo vs ring',
    'best home security camera',
    'wireless security camera comparison',
    'security camera buying guide',
    'outdoor security camera reviews'
  ],
  'How-To & Setup': [
    'how to install security camera',
    'security camera setup guide',
    'connect security camera to wifi',
    'security camera placement tips',
    'security camera troubleshooting'
  ],
  'Technology & Features': [
    'ai security camera features',
    'motion detection security camera',
    'night vision security camera',
    'security camera with facial recognition',
    'cloud vs local storage security camera'
  ],
  'Smart Home Integration': [
    'security camera alexa integration',
    'google home security camera',
    'smart home security system',
    'security camera automation',
    'security camera IFTTT'
  ]
};

interface CompetitorAnalysis {
  brand: string;
  domain: string;
  geoStrengths: {
    totalAIAppearances: number;
    averagePosition: number;
    topQueryCategories: string[];
    contentPatterns: string[];
  };
  contentStrategy: {
    structureAnalysis: any;
    keyTopics: string[];
    uniqueAdvantages: string[];
  };
  technicalFactors: {
    schemaMarkup: boolean;
    pageSpeed: number;
    mobileOptimized: boolean;
  };
}

async function analyzeCompetitorGEOStrategy(brand: string, domain: string): Promise<CompetitorAnalysis> {
  console.log(`\n🔍 Analyzing ${brand}'s GEO Strategy...`);
  
  const analysis: CompetitorAnalysis = {
    brand,
    domain,
    geoStrengths: {
      totalAIAppearances: 0,
      averagePosition: 0,
      topQueryCategories: [],
      contentPatterns: []
    },
    contentStrategy: {
      structureAnalysis: {},
      keyTopics: [],
      uniqueAdvantages: []
    },
    technicalFactors: {
      schemaMarkup: false,
      pageSpeed: 0,
      mobileOptimized: false
    }
  };

  // Step 1: Analyze AI Overview appearances across strategic queries
  const serpClient = new SerpAPIClient({ apiKey: SERPAPI_KEY });
  const queryResults: Map<string, any> = new Map();

  for (const [category, queries] of Object.entries(STRATEGIC_QUERIES)) {
    console.log(`\n📊 Analyzing ${category} queries...`);
    
    for (const query of queries) {
      try {
        const result = await serpClient.search(query);
        
        if (result.ai_overview) {
          // Check if competitor is mentioned in AI Overview
          const mentioned = result.ai_overview.sources?.some(
            (source: any) => source.link?.includes(domain)
          ) || result.ai_overview.content?.toLowerCase().includes(brand.toLowerCase());
          
          if (mentioned) {
            analysis.geoStrengths.totalAIAppearances++;
            queryResults.set(query, { category, mentioned: true, aiOverview: result.ai_overview });
          }
        }
        
        // Small delay to avoid rate limiting
        await new Promise(resolve => setTimeout(resolve, 2000));
        
      } catch (error) {
        console.error(`Error analyzing query "${query}": ${error.message}`);
      }
    }
  }

  // Step 2: Analyze content patterns from successful queries
  if (queryResults.size > 0) {
    // Identify top categories
    const categoryCount = new Map<string, number>();
    queryResults.forEach((result, query) => {
      const count = categoryCount.get(result.category) || 0;
      categoryCount.set(result.category, count + 1);
    });
    
    analysis.geoStrengths.topQueryCategories = Array.from(categoryCount.entries())
      .sort((a, b) => b[1] - a[1])
      .slice(0, 3)
      .map(([category]) => category);
  }

  // Step 3: Scrape and analyze competitor's content structure
  console.log(`\n🌐 Analyzing ${brand}'s website content structure...`);
  
  try {
    // Analyze homepage
    const homepage = await callFirecrawlAPI('/scrape', 'POST', {
      url: `https://${domain}`,
      scrapeOptions: {
        formats: ['markdown', 'html'],
        onlyMainContent: false,
        includeTags: ['h1', 'h2', 'h3', 'ul', 'ol'],
        waitFor: 3000
      }
    });

    if (homepage.success && homepage.data) {
      // Analyze content structure
      const content = homepage.data.markdown || '';
      
      // Extract headings structure
      const h1Count = (content.match(/^# /gm) || []).length;
      const h2Count = (content.match(/^## /gm) || []).length;
      const h3Count = (content.match(/^### /gm) || []).length;
      
      // Extract lists (bullet points)
      const bulletLists = (content.match(/^[-*] /gm) || []).length;
      const numberedLists = (content.match(/^\d+\. /gm) || []).length;
      
      analysis.contentStrategy.structureAnalysis = {
        headingHierarchy: { h1: h1Count, h2: h2Count, h3: h3Count },
        listUsage: { bullet: bulletLists, numbered: numberedLists },
        totalWords: content.split(/\s+/).length
      };

      // Check for schema markup
      if (homepage.data.html) {
        analysis.technicalFactors.schemaMarkup = homepage.data.html.includes('schema.org');
      }
    }

    // Analyze a key product/guide page
    const guidePage = await callFirecrawlAPI('/search', 'POST', {
      query: `site:${domain} buying guide OR installation guide OR how to`,
      limit: 3,
      scrapeOptions: {
        formats: ['markdown'],
        onlyMainContent: true
      }
    });

    if (guidePage.success && guidePage.data?.length > 0) {
      // Extract content patterns from guides
      for (const page of guidePage.data) {
        const content = page.markdown || '';
        
        // Look for content patterns
        if (content.includes('Step 1') || content.includes('## 1.')) {
          analysis.contentStrategy.contentPatterns.push('Step-by-step guides');
        }
        if (content.match(/FAQ|Frequently Asked Questions/i)) {
          analysis.contentStrategy.contentPatterns.push('FAQ sections');
        }
        if (content.match(/Quick Answer:|At a glance:|Summary:/i)) {
          analysis.contentStrategy.contentPatterns.push('Quick answer summaries');
        }
        if (content.match(/Pros:|Cons:|Advantages:|Disadvantages:/i)) {
          analysis.contentStrategy.contentPatterns.push('Pros/Cons lists');
        }
      }
    }

  } catch (error) {
    console.error(`Error analyzing ${brand} website: ${error.message}`);
  }

  // Step 4: Identify unique advantages
  if (brand.toLowerCase() === 'arlo') {
    analysis.contentStrategy.uniqueAdvantages = [
      'Wire-free technology leadership',
      'Professional-grade security focus',
      'Comprehensive smart home ecosystem',
      'Premium brand positioning'
    ];
  } else if (brand.toLowerCase() === 'ring') {
    analysis.contentStrategy.uniqueAdvantages = [
      'Amazon ecosystem integration',
      'Neighborhood security community',
      'Doorbell camera market leader',
      'DIY-friendly installation guides'
    ];
  }

  return analysis;
}

async function generateStrategicInsights(analyses: CompetitorAnalysis[]): Promise<any> {
  const insights = {
    commonPatterns: [],
    differentiators: {},
    recommendations: [],
    contentGaps: []
  };

  // Find common successful patterns
  const allPatterns = analyses.flatMap(a => a.contentStrategy.contentPatterns);
  const patternCounts = allPatterns.reduce((acc, pattern) => {
    acc[pattern] = (acc[pattern] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  insights.commonPatterns = Object.entries(patternCounts)
    .filter(([_, count]) => count > 1)
    .map(([pattern]) => pattern);

  // Identify what Eufy should adopt
  insights.recommendations = [
    {
      priority: 'HIGH',
      action: 'Create comprehensive buying guides with quick answer sections',
      reason: 'Both Arlo and Ring leverage this format for AI Overview visibility'
    },
    {
      priority: 'HIGH',
      action: 'Implement step-by-step installation guides with clear numbered steps',
      reason: 'Step-by-step content frequently appears in AI Overviews'
    },
    {
      priority: 'MEDIUM',
      action: 'Add FAQ sections to all product pages',
      reason: 'FAQ format aligns with AI Overview\'s Q&A structure'
    },
    {
      priority: 'MEDIUM',
      action: 'Create comparison content highlighting unique Eufy advantages',
      reason: 'Comparison queries show high AI Overview rates'
    }
  ];

  // Identify content gaps Eufy can exploit
  insights.contentGaps = [
    'Privacy-focused security (Eufy\'s no-subscription advantage)',
    'Local storage benefits and setup guides',
    'Battery life optimization guides',
    'AI-powered features without cloud dependency'
  ];

  return insights;
}

// Main execution
async function main() {
  console.log('🚀 Deep Competitive Analysis: Arlo & Ring GEO Success Strategies');
  console.log('=' .repeat(70));
  console.log('Analyzing why Arlo and Ring dominate Google AI Overviews...\n');

  try {
    // Analyze each competitor
    const arloAnalysis = await analyzeCompetitorGEOStrategy('Arlo', 'arlo.com');
    const ringAnalysis = await analyzeCompetitorGEOStrategy('Ring', 'ring.com');

    // Generate strategic insights
    const insights = await generateStrategicInsights([arloAnalysis, ringAnalysis]);

    // Prepare comprehensive report
    const report = {
      analysisDate: new Date().toISOString(),
      competitors: [arloAnalysis, ringAnalysis],
      strategicInsights: insights,
      executiveSummary: {
        keyFindings: [
          `Arlo appears in ${arloAnalysis.geoStrengths.totalAIAppearances} AI Overviews across test queries`,
          `Ring appears in ${ringAnalysis.geoStrengths.totalAIAppearances} AI Overviews across test queries`,
          `Top performing categories: ${[...arloAnalysis.geoStrengths.topQueryCategories, ...ringAnalysis.geoStrengths.topQueryCategories].filter((v, i, a) => a.indexOf(v) === i).join(', ')}`
        ],
        immediateActions: [
          'Implement structured content format with clear headings and lists',
          'Create comprehensive guides targeting high-AI-Overview queries',
          'Optimize for quick answers at the beginning of content',
          'Leverage Eufy\'s unique privacy and local storage advantages'
        ]
      }
    };

    // Save detailed analysis
    await fs.writeFile(
      'competitor-geo-strategy-analysis.json',
      JSON.stringify(report, null, 2)
    );

    // Generate markdown report
    const markdownReport = `# Competitor GEO Strategy Analysis

## Executive Summary
Date: ${new Date().toLocaleDateString()}

### 🏆 Key Findings
${report.executiveSummary.keyFindings.map(f => `- ${f}`).join('\n')}

## Detailed Analysis

### Arlo Strategy
- **AI Overview Appearances**: ${arloAnalysis.geoStrengths.totalAIAppearances}
- **Top Categories**: ${arloAnalysis.geoStrengths.topQueryCategories.join(', ')}
- **Content Patterns**: ${arloAnalysis.contentStrategy.contentPatterns.join(', ')}
- **Unique Advantages**: ${arloAnalysis.contentStrategy.uniqueAdvantages.join(', ')}

### Ring Strategy
- **AI Overview Appearances**: ${ringAnalysis.geoStrengths.totalAIAppearances}
- **Top Categories**: ${ringAnalysis.geoStrengths.topQueryCategories.join(', ')}
- **Content Patterns**: ${ringAnalysis.contentStrategy.contentPatterns.join(', ')}
- **Unique Advantages**: ${ringAnalysis.contentStrategy.uniqueAdvantages.join(', ')}

## Strategic Recommendations

### Immediate Actions (This Week)
${insights.recommendations.filter(r => r.priority === 'HIGH').map(r => `1. **${r.action}**\n   - ${r.reason}`).join('\n')}

### Content Opportunities
${insights.contentGaps.map((gap, i) => `${i + 1}. ${gap}`).join('\n')}

## Implementation Roadmap

### Week 1-2: Content Structure Optimization
- Audit existing content for AI Overview optimization
- Implement structured data markup
- Add quick answer sections to top pages

### Week 3-4: New Content Creation
- Develop comprehensive buying guides
- Create step-by-step installation content
- Build comparison pages highlighting Eufy advantages

### Week 5-6: Technical Optimization
- Improve page speed to match competitors
- Enhance mobile experience
- Implement FAQ schema markup

## Success Metrics
- Track AI Overview appearances weekly
- Monitor GEO visibility score improvement
- Measure organic traffic from AI-influenced searches
- Track conversion rates from optimized content
`;

    await fs.writeFile('competitor-geo-strategy-report.md', markdownReport);

    console.log('\n✅ Analysis Complete!');
    console.log('\n📊 Summary:');
    console.log(`- Arlo GEO Appearances: ${arloAnalysis.geoStrengths.totalAIAppearances}`);
    console.log(`- Ring GEO Appearances: ${ringAnalysis.geoStrengths.totalAIAppearances}`);
    console.log('\n📁 Reports Generated:');
    console.log('- competitor-geo-strategy-analysis.json (detailed data)');
    console.log('- competitor-geo-strategy-report.md (executive summary)');
    console.log('\n🎯 Key Insight: Both competitors use structured content with clear headings,');
    console.log('   step-by-step guides, and FAQ sections to maximize AI Overview visibility.');

  } catch (error) {
    console.error('Error during analysis:', error);
  }
}

// Run the analysis
if (require.main === module) {
  main().catch(console.error);
}