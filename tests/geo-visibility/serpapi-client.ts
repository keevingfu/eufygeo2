// SerpAPI Client for Enhanced Google AI Overview Tracking
// Provides direct access to Google SERP data including AI Overviews

import axios from 'axios';

export interface SerpAPIConfig {
  apiKey: string;
  engine?: string;
  defaultParams?: Record<string, any>;
}

export interface AIOverviewData {
  content?: string;
  sources?: Array<{
    title: string;
    link: string;
    snippet?: string;
    position?: number;
  }>;
  highlighted_words?: string[];
}

export interface OrganicResult {
  position: number;
  title: string;
  link: string;
  domain: string;
  snippet: string;
  cached_page_link?: string;
  related_pages_link?: string;
}

export interface SerpAPIResponse {
  search_metadata: {
    id: string;
    status: string;
    created_at: string;
    processed_at: string;
    google_url: string;
    total_time_taken: number;
  };
  search_parameters: {
    q: string;
    location?: string;
    google_domain: string;
    gl: string;
    hl: string;
  };
  search_information: {
    query_displayed: string;
    total_results?: number;
    time_taken_displayed?: number;
  };
  ai_overview?: AIOverviewData;
  answer_box?: {
    type: string;
    title?: string;
    answer?: string;
    snippet?: string;
    snippet_highlighted_words?: string[];
    link?: string;
    displayed_link?: string;
  };
  organic_results?: OrganicResult[];
  related_questions?: Array<{
    question: string;
    snippet: string;
    title: string;
    link: string;
    displayed_link: string;
  }>;
  related_searches?: Array<{
    query: string;
    link: string;
  }>;
  knowledge_graph?: {
    title: string;
    type: string;
    description?: string;
    source?: {
      name: string;
      link: string;
    };
    attributes?: Record<string, any>;
  };
  featured_snippet?: {
    title: string;
    link: string;
    displayed_link: string;
    snippet: string;
    snippet_highlighted_words: string[];
  };
}

export class SerpAPIClient {
  private apiKey: string;
  private baseUrl: string = 'https://serpapi.com/search';
  private defaultParams: Record<string, any>;

  constructor(config: SerpAPIConfig) {
    this.apiKey = config.apiKey;
    this.defaultParams = {
      engine: config.engine || 'google',
      api_key: this.apiKey,
      ...config.defaultParams
    };
  }

  // Search Google and get results including AI Overview
  async search(query: string, params?: Record<string, any>): Promise<SerpAPIResponse> {
    try {
      const searchParams = {
        ...this.defaultParams,
        q: query,
        ...params
      };

      console.log(`🔍 Searching Google for: "${query}"`);
      
      const response = await axios.get(this.baseUrl, {
        params: searchParams,
        timeout: 30000
      });

      return response.data;
      
    } catch (error: any) {
      console.error(`❌ SerpAPI Error: ${error.message}`);
      if (error.response) {
        console.error('Response:', error.response.data);
      }
      throw error;
    }
  }

  // Get AI Overview visibility for a query
  async getAIOverviewVisibility(query: string, location: string = 'United States'): Promise<{
    hasAIOverview: boolean;
    aiOverview?: AIOverviewData;
    competitorVisibility: Record<string, {
      mentioned: boolean;
      citations: number;
      positions: number[];
    }>;
  }> {
    const result = await this.search(query, {
      location: location,
      google_domain: 'google.com',
      gl: 'us',
      hl: 'en'
    });

    const hasAIOverview = !!result.ai_overview;
    const competitorDomains = ['eufy.com', 'arlo.com', 'ring.com', 'nest.com', 'google.com/nest', 'wyze.com'];
    const competitorVisibility: Record<string, any> = {};

    // Initialize competitor tracking
    competitorDomains.forEach(domain => {
      competitorVisibility[domain] = {
        mentioned: false,
        citations: 0,
        positions: []
      };
    });

    // Check AI Overview for competitor mentions
    if (hasAIOverview && result.ai_overview) {
      const aiContent = result.ai_overview.content || '';
      const sources = result.ai_overview.sources || [];

      // Check content for brand mentions
      competitorDomains.forEach(domain => {
        const brandName = domain.split('.')[0];
        const regex = new RegExp(`\\b${brandName}\\b`, 'gi');
        if (regex.test(aiContent)) {
          competitorVisibility[domain].mentioned = true;
        }
      });

      // Check sources for competitor domains
      sources.forEach((source, index) => {
        competitorDomains.forEach(domain => {
          if (source.link && source.link.includes(domain)) {
            competitorVisibility[domain].citations++;
            competitorVisibility[domain].positions.push(index + 1);
          }
        });
      });
    }

    return {
      hasAIOverview,
      aiOverview: result.ai_overview,
      competitorVisibility
    };
  }

  // Get comprehensive SERP analysis
  async analyzeSERP(query: string): Promise<{
    query: string;
    timestamp: string;
    aiOverview: {
      present: boolean;
      data?: AIOverviewData;
    };
    featuredSnippet?: any;
    peopleAlsoAsk?: any[];
    organicResults: Array<{
      position: number;
      domain: string;
      title: string;
      url: string;
    }>;
    competitorRankings: Record<string, number[]>;
    serpFeatures: string[];
  }> {
    const result = await this.search(query);
    const timestamp = new Date().toISOString();
    
    // Track SERP features
    const serpFeatures: string[] = [];
    if (result.ai_overview) serpFeatures.push('ai_overview');
    if (result.featured_snippet) serpFeatures.push('featured_snippet');
    if (result.answer_box) serpFeatures.push('answer_box');
    if (result.knowledge_graph) serpFeatures.push('knowledge_graph');
    if (result.related_questions) serpFeatures.push('people_also_ask');
    if (result.related_searches) serpFeatures.push('related_searches');

    // Track competitor organic rankings
    const competitorDomains = ['eufy.com', 'arlo.com', 'ring.com', 'nest.com', 'google.com/nest', 'wyze.com'];
    const competitorRankings: Record<string, number[]> = {};
    
    competitorDomains.forEach(domain => {
      competitorRankings[domain] = [];
    });

    const organicResults = (result.organic_results || []).map(r => {
      const url = r.link || '';
      
      // Check if this is a competitor result
      competitorDomains.forEach(domain => {
        if (url.includes(domain)) {
          competitorRankings[domain].push(r.position);
        }
      });

      return {
        position: r.position,
        domain: r.domain || new URL(url).hostname,
        title: r.title,
        url: url
      };
    });

    return {
      query,
      timestamp,
      aiOverview: {
        present: !!result.ai_overview,
        data: result.ai_overview
      },
      featuredSnippet: result.featured_snippet,
      peopleAlsoAsk: result.related_questions,
      organicResults,
      competitorRankings,
      serpFeatures
    };
  }

  // Batch analyze multiple queries
  async batchAnalyze(queries: string[], delayMs: number = 2000): Promise<any[]> {
    const results = [];
    
    for (const query of queries) {
      try {
        const result = await this.analyzeSERP(query);
        results.push(result);
        
        // Rate limiting
        if (delayMs > 0) {
          await new Promise(resolve => setTimeout(resolve, delayMs));
        }
      } catch (error) {
        console.error(`Failed to analyze query "${query}":`, error);
        results.push({
          query,
          error: error.message,
          timestamp: new Date().toISOString()
        });
      }
    }
    
    return results;
  }

  // Get location-specific results
  async searchByLocation(query: string, location: string): Promise<SerpAPIResponse> {
    return this.search(query, {
      location: location,
      google_domain: 'google.com'
    });
  }

  // Get mobile results
  async searchMobile(query: string): Promise<SerpAPIResponse> {
    return this.search(query, {
      device: 'mobile',
      mobile: 'true'
    });
  }
}

// Export helper functions
export function createSerpAPIClient(apiKey: string): SerpAPIClient {
  return new SerpAPIClient({
    apiKey,
    defaultParams: {
      num: 20,  // Get more results for better analysis
      no_cache: true  // Always get fresh results
    }
  });
}

// Analyze competitor presence in AI Overview
export function analyzeCompetitorPresence(
  aiOverview: AIOverviewData | undefined,
  competitors: string[] = ['eufy', 'arlo', 'ring', 'nest', 'wyze']
): Record<string, { mentioned: boolean; sourceCount: number }> {
  const presence: Record<string, { mentioned: boolean; sourceCount: number }> = {};
  
  competitors.forEach(brand => {
    presence[brand] = { mentioned: false, sourceCount: 0 };
  });

  if (!aiOverview) return presence;

  // Check AI Overview content
  const content = (aiOverview.content || '').toLowerCase();
  competitors.forEach(brand => {
    if (content.includes(brand.toLowerCase())) {
      presence[brand].mentioned = true;
    }
  });

  // Check sources
  (aiOverview.sources || []).forEach(source => {
    const sourceText = `${source.title} ${source.link} ${source.snippet || ''}`.toLowerCase();
    competitors.forEach(brand => {
      if (sourceText.includes(brand.toLowerCase())) {
        presence[brand].sourceCount++;
      }
    });
  });

  return presence;
}

// Calculate GEO visibility score
export function calculateGEOScore(
  hasAIOverview: boolean,
  mentioned: boolean,
  sourceCount: number,
  organicPosition?: number
): number {
  let score = 0;
  
  // AI Overview presence is most valuable
  if (hasAIOverview) {
    if (mentioned) score += 50;  // Direct mention in AI Overview
    score += sourceCount * 20;    // Each source citation
  }
  
  // Organic ranking still matters
  if (organicPosition) {
    if (organicPosition === 1) score += 30;
    else if (organicPosition <= 3) score += 20;
    else if (organicPosition <= 5) score += 10;
    else if (organicPosition <= 10) score += 5;
  }
  
  return Math.min(score, 100);  // Cap at 100
}