// Firecrawl Test Configuration for Eufy SEO Analysis

export const FIRECRAWL_CONFIG = {
  apiKey: process.env.FIRECRAWL_API_KEY || 'fc-7106bd7009b94c8884a082beaecf4294',
  apiUrl: process.env.FIRECRAWL_API_URL || 'https://api.firecrawl.dev/v1',
  
  // Retry configuration
  retry: {
    maxAttempts: parseInt(process.env.FIRECRAWL_RETRY_MAX_ATTEMPTS || '5'),
    initialDelay: parseInt(process.env.FIRECRAWL_RETRY_INITIAL_DELAY || '2000'),
    maxDelay: parseInt(process.env.FIRECRAWL_RETRY_MAX_DELAY || '30000'),
    backoffFactor: parseInt(process.env.FIRECRAWL_RETRY_BACKOFF_FACTOR || '2')
  },
  
  // Credit monitoring
  credit: {
    warningThreshold: parseInt(process.env.FIRECRAWL_CREDIT_WARNING_THRESHOLD || '2000'),
    criticalThreshold: parseInt(process.env.FIRECRAWL_CREDIT_CRITICAL_THRESHOLD || '500')
  }
};

// Test data specific to Eufy competitive analysis
export const EUFY_COMPETITORS = {
  primary: [
    {
      name: 'Arlo',
      domain: 'arlo.com',
      urls: {
        home: 'https://www.arlo.com',
        products: 'https://www.arlo.com/en-us/cameras',
        support: 'https://www.arlo.com/en-us/support'
      }
    },
    {
      name: 'Ring',
      domain: 'ring.com',
      urls: {
        home: 'https://ring.com',
        products: 'https://ring.com/security-cameras',
        support: 'https://support.ring.com'
      }
    },
    {
      name: 'Google Nest',
      domain: 'nest.com',
      urls: {
        home: 'https://www.google.com/nest',
        products: 'https://store.google.com/category/connected_home',
        support: 'https://support.google.com/googlenest'
      }
    },
    {
      name: 'Wyze',
      domain: 'wyze.com',
      urls: {
        home: 'https://www.wyze.com',
        products: 'https://www.wyze.com/products/wyze-cam',
        blog: 'https://www.wyze.com/blog'
      }
    }
  ],
  
  secondary: [
    {
      name: 'Blink',
      domain: 'blinkforhome.com',
      urls: {
        home: 'https://blinkforhome.com',
        products: 'https://blinkforhome.com/products'
      }
    },
    {
      name: 'SimpliSafe',
      domain: 'simplisafe.com',
      urls: {
        home: 'https://simplisafe.com',
        products: 'https://simplisafe.com/home-security-cameras'
      }
    }
  ]
};

// SEO-specific test queries
export const SEO_TEST_QUERIES = {
  productComparisons: [
    'eufy vs arlo security camera',
    'best wireless security camera 2024',
    'ring vs nest doorbell camera',
    'home security camera comparison'
  ],
  
  features: [
    'security camera night vision',
    'wireless outdoor camera weatherproof',
    '4K security camera system',
    'AI motion detection camera'
  ],
  
  buyingGuides: [
    'how to choose security camera',
    'security camera buying guide',
    'home security system cost',
    'DIY security camera installation'
  ],
  
  localSEO: [
    'security camera installation near me',
    'home security systems los angeles',
    'security camera repair service',
    'smart home installation companies'
  ]
};

// Schema definitions for data extraction
export const EXTRACTION_SCHEMAS = {
  productPage: {
    type: "object",
    properties: {
      url: { type: "string" },
      productName: { type: "string" },
      brand: { type: "string" },
      price: {
        type: "object",
        properties: {
          current: { type: "string" },
          original: { type: "string" },
          currency: { type: "string" }
        }
      },
      rating: {
        type: "object",
        properties: {
          average: { type: "number" },
          count: { type: "integer" },
          distribution: {
            type: "object",
            properties: {
              "5": { type: "integer" },
              "4": { type: "integer" },
              "3": { type: "integer" },
              "2": { type: "integer" },
              "1": { type: "integer" }
            }
          }
        }
      },
      features: {
        type: "array",
        items: { type: "string" }
      },
      specifications: {
        type: "object",
        properties: {
          resolution: { type: "string" },
          fieldOfView: { type: "string" },
          nightVisionRange: { type: "string" },
          weatherRating: { type: "string" },
          powerSource: { type: "string" },
          connectivity: { type: "string" },
          storage: { type: "string" }
        }
      },
      images: {
        type: "array",
        items: {
          type: "object",
          properties: {
            url: { type: "string" },
            alt: { type: "string" }
          }
        }
      }
    },
    required: ["url", "productName", "features"]
  },
  
  seoMetadata: {
    type: "object",
    properties: {
      url: { type: "string" },
      title: { type: "string" },
      metaDescription: { type: "string" },
      metaKeywords: { type: "string" },
      ogTitle: { type: "string" },
      ogDescription: { type: "string" },
      ogImage: { type: "string" },
      canonicalUrl: { type: "string" },
      robots: { type: "string" },
      headings: {
        type: "object",
        properties: {
          h1: { type: "array", items: { type: "string" } },
          h2: { type: "array", items: { type: "string" } },
          h3: { type: "array", items: { type: "string" } }
        }
      },
      schemaMarkup: {
        type: "array",
        items: {
          type: "object",
          properties: {
            type: { type: "string" },
            properties: { type: "object" }
          }
        }
      }
    },
    required: ["url", "title", "headings"]
  },
  
  contentAnalysis: {
    type: "object",
    properties: {
      url: { type: "string" },
      wordCount: { type: "integer" },
      readingTime: { type: "integer" },
      mainTopics: {
        type: "array",
        items: { type: "string" }
      },
      keywordDensity: {
        type: "object",
        additionalProperties: { type: "number" }
      },
      internalLinks: {
        type: "array",
        items: {
          type: "object",
          properties: {
            url: { type: "string" },
            anchorText: { type: "string" }
          }
        }
      },
      externalLinks: {
        type: "array",
        items: {
          type: "object",
          properties: {
            url: { type: "string" },
            anchorText: { type: "string" },
            isNofollow: { type: "boolean" }
          }
        }
      },
      images: {
        type: "array",
        items: {
          type: "object",
          properties: {
            src: { type: "string" },
            alt: { type: "string" },
            title: { type: "string" }
          }
        }
      }
    }
  }
};

// Helper functions for test data
export function getRandomCompetitor() {
  const all = [...EUFY_COMPETITORS.primary, ...EUFY_COMPETITORS.secondary];
  return all[Math.floor(Math.random() * all.length)];
}

export function getRandomQuery() {
  const allQueries = [
    ...SEO_TEST_QUERIES.productComparisons,
    ...SEO_TEST_QUERIES.features,
    ...SEO_TEST_QUERIES.buyingGuides,
    ...SEO_TEST_QUERIES.localSEO
  ];
  return allQueries[Math.floor(Math.random() * allQueries.length)];
}

// Rate limiting helper
export async function respectRateLimit(delayMs: number = 2000) {
  await new Promise(resolve => setTimeout(resolve, delayMs));
}

// Batch processing helper
export function chunkArray<T>(array: T[], chunkSize: number): T[][] {
  const chunks: T[][] = [];
  for (let i = 0; i < array.length; i += chunkSize) {
    chunks.push(array.slice(i, i + chunkSize));
  }
  return chunks;
}