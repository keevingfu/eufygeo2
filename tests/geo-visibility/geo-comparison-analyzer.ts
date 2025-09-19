// GEO Comparison Analyzer
// Compares and validates results from SerpAPI and Firecrawl

import { SerpAPIClient, SerpAPIResponse, AIOverviewData } from './serpapi-client';
import { callFirecrawlAPI } from '../firecrawl/test-config';

export interface ComparisonResult {
  query: string;
  timestamp: string;
  serpApiData: {
    hasAIOverview: boolean;
    aiOverviewLength?: number;
    citedSources: number;
    organicResults: number;
    serpFeatures: string[];
  };
  firecrawlData: {
    searchSuccess: boolean;
    resultsFound: number;
    contentScraped: boolean;
    error?: string;
  };
  validation: {
    aiOverviewMatch: boolean | 'unknown';
    topResultsOverlap: number;
    dataQuality: 'high' | 'medium' | 'low';
    confidence: number;
  };
  insights: string[];
}

export class GEOComparisonAnalyzer {
  private serpClient: SerpAPIClient;
  private comparisonResults: ComparisonResult[] = [];

  constructor(serpApiKey: string) {
    this.serpClient = new SerpAPIClient({
      apiKey: serpApiKey,
      defaultParams: {
        num: 10,
        no_cache: true
      }
    });
  }

  // Compare results from both sources
  async compareResults(query: string): Promise<ComparisonResult> {
    console.log(`\n🔄 Comparing results for: "${query}"`);
    
    const result: ComparisonResult = {
      query,
      timestamp: new Date().toISOString(),
      serpApiData: {
        hasAIOverview: false,
        citedSources: 0,
        organicResults: 0,
        serpFeatures: []
      },
      firecrawlData: {
        searchSuccess: false,
        resultsFound: 0,
        contentScraped: false
      },
      validation: {
        aiOverviewMatch: 'unknown',
        topResultsOverlap: 0,
        dataQuality: 'low',
        confidence: 0
      },
      insights: []
    };

    // Get SerpAPI data
    try {
      const serpResponse = await this.serpClient.search(query);
      result.serpApiData = this.extractSerpData(serpResponse);
      console.log(`✅ SerpAPI: AI Overview ${result.serpApiData.hasAIOverview ? 'found' : 'not found'}`);
    } catch (error) {
      console.error(`❌ SerpAPI error: ${error.message}`);
      result.insights.push(`SerpAPI failed: ${error.message}`);
    }

    // Get Firecrawl data
    try {
      const firecrawlSearch = await callFirecrawlAPI('/search', 'POST', {
        query: query,
        limit: 10,
        scrapeOptions: {
          formats: ['markdown', 'html'],
          onlyMainContent: false,
          waitFor: 3000
        }
      });

      if (firecrawlSearch.success) {
        result.firecrawlData = {
          searchSuccess: true,
          resultsFound: firecrawlSearch.data?.length || 0,
          contentScraped: true
        };
        console.log(`✅ Firecrawl: Found ${result.firecrawlData.resultsFound} results`);
      }
    } catch (error) {
      result.firecrawlData.error = error.message;
      console.error(`❌ Firecrawl error: ${error.message}`);
      result.insights.push(`Firecrawl failed: ${error.message}`);
    }

    // Validate and compare
    result.validation = this.validateResults(result);
    result.insights.push(...this.generateInsights(result));

    this.comparisonResults.push(result);
    return result;
  }

  // Extract key data from SerpAPI response
  private extractSerpData(response: SerpAPIResponse): ComparisonResult['serpApiData'] {
    const serpFeatures: string[] = [];
    
    if (response.ai_overview) serpFeatures.push('ai_overview');
    if (response.featured_snippet) serpFeatures.push('featured_snippet');
    if (response.answer_box) serpFeatures.push('answer_box');
    if (response.knowledge_graph) serpFeatures.push('knowledge_graph');
    if (response.related_questions) serpFeatures.push('people_also_ask');

    return {
      hasAIOverview: !!response.ai_overview,
      aiOverviewLength: response.ai_overview?.content?.length,
      citedSources: response.ai_overview?.sources?.length || 0,
      organicResults: response.organic_results?.length || 0,
      serpFeatures
    };
  }

  // Validate results between sources
  private validateResults(result: ComparisonResult): ComparisonResult['validation'] {
    let confidence = 50; // Base confidence
    let dataQuality: 'high' | 'medium' | 'low' = 'medium';

    // Both sources successful
    if (result.serpApiData.organicResults > 0 && result.firecrawlData.searchSuccess) {
      confidence += 30;
      dataQuality = 'high';
    }

    // AI Overview validation is complex - Firecrawl might not detect it reliably
    const aiOverviewMatch = 'unknown' as const;

    // Calculate overlap (simplified - would need actual URL comparison)
    const topResultsOverlap = Math.min(
      result.serpApiData.organicResults,
      result.firecrawlData.resultsFound
    ) / Math.max(1, Math.max(
      result.serpApiData.organicResults,
      result.firecrawlData.resultsFound
    ));

    if (topResultsOverlap > 0.7) {
      confidence += 20;
    }

    return {
      aiOverviewMatch,
      topResultsOverlap: Math.round(topResultsOverlap * 100),
      dataQuality,
      confidence: Math.min(100, confidence)
    };
  }

  // Generate insights from comparison
  private generateInsights(result: ComparisonResult): string[] {
    const insights: string[] = [];

    if (result.serpApiData.hasAIOverview) {
      insights.push(`AI Overview detected with ${result.serpApiData.citedSources} cited sources`);
      
      if (result.serpApiData.aiOverviewLength && result.serpApiData.aiOverviewLength > 500) {
        insights.push('Comprehensive AI Overview (>500 chars) indicates high query importance');
      }
    }

    if (result.serpApiData.serpFeatures.length > 3) {
      insights.push(`Rich SERP with ${result.serpApiData.serpFeatures.length} features - competitive query`);
    }

    if (result.validation.confidence < 70) {
      insights.push('Low confidence - consider manual verification');
    }

    if (!result.firecrawlData.searchSuccess && result.serpApiData.organicResults > 0) {
      insights.push('Firecrawl search failed but SerpAPI succeeded - use SerpAPI data');
    }

    return insights;
  }

  // Batch comparison
  async batchCompare(queries: string[], delayMs: number = 2000): Promise<ComparisonResult[]> {
    const results: ComparisonResult[] = [];

    for (const query of queries) {
      try {
        const result = await this.compareResults(query);
        results.push(result);
      } catch (error) {
        console.error(`Failed to compare query "${query}": ${error.message}`);
      }

      if (delayMs > 0) {
        await new Promise(resolve => setTimeout(resolve, delayMs));
      }
    }

    return results;
  }

  // Generate comparison report
  generateReport(): {
    summary: any;
    reliabilityScore: number;
    recommendations: string[];
  } {
    const totalComparisons = this.comparisonResults.length;
    const successfulComparisons = this.comparisonResults.filter(
      r => r.validation.confidence > 70
    ).length;

    const avgConfidence = this.comparisonResults.reduce(
      (sum, r) => sum + r.validation.confidence, 0
    ) / totalComparisons;

    const serpApiSuccess = this.comparisonResults.filter(
      r => r.serpApiData.organicResults > 0
    ).length;

    const firecrawlSuccess = this.comparisonResults.filter(
      r => r.firecrawlData.searchSuccess
    ).length;

    const reliabilityScore = (avgConfidence * 0.5) + 
      (serpApiSuccess / totalComparisons * 25) + 
      (firecrawlSuccess / totalComparisons * 25);

    const recommendations: string[] = [];

    if (serpApiSuccess > firecrawlSuccess * 1.5) {
      recommendations.push('SerpAPI shows higher reliability - prioritize for production use');
    }

    if (avgConfidence < 70) {
      recommendations.push('Overall confidence is low - implement additional validation');
    }

    const aiOverviewQueries = this.comparisonResults.filter(
      r => r.serpApiData.hasAIOverview
    ).length;

    recommendations.push(
      `${aiOverviewQueries}/${totalComparisons} queries show AI Overview - ` +
      'focus GEO optimization on these high-value queries'
    );

    return {
      summary: {
        totalComparisons,
        successfulComparisons,
        avgConfidence: avgConfidence.toFixed(1),
        serpApiSuccessRate: (serpApiSuccess / totalComparisons * 100).toFixed(1) + '%',
        firecrawlSuccessRate: (firecrawlSuccess / totalComparisons * 100).toFixed(1) + '%',
        aiOverviewRate: (aiOverviewQueries / totalComparisons * 100).toFixed(1) + '%'
      },
      reliabilityScore: Math.round(reliabilityScore),
      recommendations
    };
  }

  // Get detailed results
  getResults(): ComparisonResult[] {
    return this.comparisonResults;
  }

  // Export results for analysis
  async exportResults(filename: string = 'geo-comparison-results.json'): Promise<void> {
    const fs = require('fs').promises;
    
    const exportData = {
      metadata: {
        timestamp: new Date().toISOString(),
        totalQueries: this.comparisonResults.length
      },
      results: this.comparisonResults,
      report: this.generateReport()
    };

    await fs.writeFile(filename, JSON.stringify(exportData, null, 2));
    console.log(`✅ Comparison results exported to: ${filename}`);
  }
}

// Helper function to identify the most reliable data source per query
export function selectBestDataSource(comparison: ComparisonResult): 'serpapi' | 'firecrawl' | 'both' {
  if (comparison.validation.confidence > 80 && comparison.validation.topResultsOverlap > 70) {
    return 'both';
  }
  
  if (comparison.serpApiData.organicResults > 0 && !comparison.firecrawlData.searchSuccess) {
    return 'serpapi';
  }
  
  if (!comparison.serpApiData.organicResults && comparison.firecrawlData.searchSuccess) {
    return 'firecrawl';
  }
  
  // Default to SerpAPI for AI Overview data
  if (comparison.serpApiData.hasAIOverview) {
    return 'serpapi';
  }
  
  return comparison.validation.confidence > 50 ? 'serpapi' : 'both';
}

// Create analyzer instance
export function createGEOComparisonAnalyzer(serpApiKey: string): GEOComparisonAnalyzer {
  return new GEOComparisonAnalyzer(serpApiKey);
}