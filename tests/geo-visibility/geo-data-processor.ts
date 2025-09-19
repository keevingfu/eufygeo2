// GEO Data Processor for Neo4j Integration
// Processes Google AI Overview visibility data for import into Neo4j

import { promises as fs } from 'fs';
import path from 'path';

// Data structures for Neo4j
interface GEONode {
  type: 'Query' | 'AIOverview' | 'Citation' | 'Competitor';
  properties: Record<string, any>;
}

interface GEORelationship {
  from: string;
  to: string;
  type: string;
  properties: Record<string, any>;
}

export class GEODataProcessor {
  private nodes: Map<string, GEONode> = new Map();
  private relationships: GEORelationship[] = [];

  // Process GEO visibility results for Neo4j
  async processGEOResults(resultsPath: string): Promise<void> {
    console.log('📊 Processing GEO visibility data for Neo4j...');
    
    try {
      // Load results
      const data = await fs.readFile(resultsPath, 'utf-8');
      const geoData = JSON.parse(data);
      
      // Create summary node
      this.createSummaryNode(geoData.summary);
      
      // Process each query result
      geoData.queryResults.forEach((result: any) => {
        this.processQueryResult(result);
      });
      
      console.log(`✅ Processed ${this.nodes.size} nodes and ${this.relationships.length} relationships`);
      
    } catch (error) {
      console.error('❌ Error processing GEO data:', error);
      throw error;
    }
  }

  // Create summary node
  private createSummaryNode(summary: any): void {
    const summaryId = `geo_summary_${new Date().toISOString()}`;
    
    this.nodes.set(summaryId, {
      type: 'AIOverview',
      properties: {
        id: summaryId,
        analysisDate: new Date().toISOString(),
        totalQueries: summary.totalQueries,
        queriesWithAIOverview: summary.queriesWithAIOverview,
        aiOverviewRate: summary.aiOverviewRate,
        type: 'summary'
      }
    });
    
    // Create competitor ranking nodes
    summary.competitorRankings.forEach((competitor: any, index: number) => {
      const competitorId = `competitor_${competitor.domain}`;
      
      if (!this.nodes.has(competitorId)) {
        this.nodes.set(competitorId, {
          type: 'Competitor',
          properties: {
            id: competitorId,
            domain: competitor.domain,
            name: competitor.domain.split('.')[0].toUpperCase()
          }
        });
      }
      
      // Add ranking relationship
      this.relationships.push({
        from: summaryId,
        to: competitorId,
        type: 'RANKS',
        properties: {
          position: index + 1,
          visibilityScore: parseFloat(competitor.visibilityScore),
          totalCitations: competitor.citations,
          appearances: competitor.queries
        }
      });
    });
  }

  // Process individual query results
  private processQueryResult(result: any): void {
    const queryId = `query_${result.query.replace(/\s+/g, '_').toLowerCase()}`;
    
    // Create query node
    this.nodes.set(queryId, {
      type: 'Query',
      properties: {
        id: queryId,
        text: result.query,
        timestamp: result.timestamp,
        hasAIOverview: result.hasAIOverview,
        queryType: this.classifyQuery(result.query)
      }
    });
    
    if (result.hasAIOverview) {
      // Create AI Overview node
      const aiOverviewId = `ai_overview_${queryId}`;
      
      this.nodes.set(aiOverviewId, {
        type: 'AIOverview',
        properties: {
          id: aiOverviewId,
          contentLength: result.aiOverviewContent?.length || 0,
          citationCount: result.citedSources.length,
          timestamp: result.timestamp
        }
      });
      
      // Link query to AI Overview
      this.relationships.push({
        from: queryId,
        to: aiOverviewId,
        type: 'HAS_AI_OVERVIEW',
        properties: {
          timestamp: result.timestamp
        }
      });
      
      // Process citations
      result.citedSources.forEach((source: any) => {
        const citationId = `citation_${source.url.replace(/[^a-zA-Z0-9]/g, '_')}`;
        
        if (!this.nodes.has(citationId)) {
          this.nodes.set(citationId, {
            type: 'Citation',
            properties: {
              id: citationId,
              url: source.url,
              domain: source.domain,
              title: source.title
            }
          });
        }
        
        // Link AI Overview to citation
        this.relationships.push({
          from: aiOverviewId,
          to: citationId,
          type: 'CITES',
          properties: {
            position: source.position
          }
        });
        
        // Link citation to competitor if applicable
        const competitorDomain = this.identifyCompetitor(source.domain);
        if (competitorDomain) {
          const competitorId = `competitor_${competitorDomain}`;
          
          if (!this.nodes.has(competitorId)) {
            this.nodes.set(competitorId, {
              type: 'Competitor',
              properties: {
                id: competitorId,
                domain: competitorDomain,
                name: competitorDomain.split('.')[0].toUpperCase()
              }
            });
          }
          
          this.relationships.push({
            from: citationId,
            to: competitorId,
            type: 'BELONGS_TO',
            properties: {
              timestamp: result.timestamp
            }
          });
        }
      });
      
      // Track competitor visibility
      Object.entries(result.competitorVisibility).forEach(([domain, visibility]: [string, any]) => {
        if (visibility.isCited) {
          const competitorId = `competitor_${domain}`;
          
          this.relationships.push({
            from: queryId,
            to: competitorId,
            type: 'SHOWS_COMPETITOR',
            properties: {
              citations: visibility.citations,
              positions: visibility.positions,
              inAIOverview: true
            }
          });
        }
      });
    }
    
    // Process organic results
    result.organicResults.slice(0, 10).forEach((organic: any) => {
      const competitorDomain = this.identifyCompetitor(organic.url);
      if (competitorDomain) {
        const competitorId = `competitor_${competitorDomain}`;
        
        this.relationships.push({
          from: queryId,
          to: competitorId,
          type: 'RANKS_ORGANICALLY',
          properties: {
            position: organic.position,
            title: organic.title,
            url: organic.url
          }
        });
      }
    });
  }

  // Classify query type
  private classifyQuery(query: string): string {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('vs') || lowerQuery.includes('comparison') || lowerQuery.includes('compare')) {
      return 'comparative';
    } else if (lowerQuery.includes('how') || lowerQuery.includes('what') || lowerQuery.includes('guide')) {
      return 'informational';
    } else if (lowerQuery.includes('best') || lowerQuery.includes('top') || lowerQuery.includes('review')) {
      return 'commercial';
    } else if (lowerQuery.includes('buy') || lowerQuery.includes('price') || lowerQuery.includes('deal')) {
      return 'transactional';
    }
    
    return 'general';
  }

  // Identify competitor from domain
  private identifyCompetitor(url: string): string | null {
    const competitorDomains = ['eufy.com', 'arlo.com', 'ring.com', 'nest.com', 'wyze.com'];
    const domain = url.toLowerCase();
    
    for (const competitor of competitorDomains) {
      if (domain.includes(competitor.replace('.com', ''))) {
        return competitor;
      }
    }
    
    return null;
  }

  // Generate Cypher queries for Neo4j import
  async generateCypherQueries(outputPath: string): Promise<void> {
    console.log('📝 Generating Cypher queries for Neo4j...');
    
    const queries: string[] = [];
    
    // Clear existing GEO data (optional)
    queries.push('// Clear existing GEO data');
    queries.push('MATCH (n) WHERE n.id STARTS WITH "geo_" OR n.id STARTS WITH "query_" OR n.id STARTS WITH "ai_overview_" OR n.id STARTS WITH "citation_" DETACH DELETE n;');
    queries.push('');
    
    // Create indexes
    queries.push('// Create indexes for GEO data');
    queries.push('CREATE INDEX query_text_idx IF NOT EXISTS FOR (q:Query) ON (q.text);');
    queries.push('CREATE INDEX citation_url_idx IF NOT EXISTS FOR (c:Citation) ON (c.url);');
    queries.push('CREATE INDEX competitor_domain_idx IF NOT EXISTS FOR (c:Competitor) ON (c.domain);');
    queries.push('');
    
    // Create nodes
    queries.push('// Create nodes');
    this.nodes.forEach((node, id) => {
      const labels = node.type;
      const props = Object.entries(node.properties)
        .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
        .join(', ');
      
      queries.push(`CREATE (n:${labels} {${props}});`);
    });
    queries.push('');
    
    // Create relationships
    queries.push('// Create relationships');
    this.relationships.forEach(rel => {
      const props = Object.entries(rel.properties)
        .map(([key, value]) => `${key}: ${JSON.stringify(value)}`)
        .join(', ');
      
      queries.push(
        `MATCH (a {id: "${rel.from}"}), (b {id: "${rel.to}"}) ` +
        `CREATE (a)-[:${rel.type} {${props}}]->(b);`
      );
    });
    
    // Add analysis queries
    queries.push('');
    queries.push('// Analysis queries');
    queries.push('');
    queries.push('// 1. Competitor AI Overview visibility ranking');
    queries.push(`MATCH (c:Competitor)<-[:SHOWS_COMPETITOR]-(q:Query)
WHERE q.hasAIOverview = true
WITH c, COUNT(DISTINCT q) as appearances, SUM(r.citations) as totalCitations
RETURN c.name as Competitor, appearances as AIOverviewAppearances, totalCitations as TotalCitations
ORDER BY appearances DESC;`);
    
    queries.push('');
    queries.push('// 2. Most cited domains in AI Overviews');
    queries.push(`MATCH (ai:AIOverview)-[:CITES]->(c:Citation)
WITH c.domain as domain, COUNT(*) as citations
RETURN domain, citations
ORDER BY citations DESC
LIMIT 20;`);
    
    queries.push('');
    queries.push('// 3. Query types with highest AI Overview rate');
    queries.push(`MATCH (q:Query)
WITH q.queryType as type, COUNT(*) as total, SUM(CASE WHEN q.hasAIOverview THEN 1 ELSE 0 END) as withAI
RETURN type, total, withAI, toFloat(withAI) * 100 / total as aiOverviewRate
ORDER BY aiOverviewRate DESC;`);
    
    // Write to file
    await fs.writeFile(outputPath, queries.join('\n'));
    console.log(`✅ Cypher queries written to ${outputPath}`);
  }

  // Generate summary report
  async generateReport(outputPath: string): Promise<void> {
    console.log('📄 Generating GEO visibility report...');
    
    let report = '# Google AI Overview (GEO) Visibility Report\n\n';
    report += `Generated: ${new Date().toISOString()}\n\n`;
    
    // Summary statistics
    const queries = Array.from(this.nodes.values()).filter(n => n.type === 'Query');
    const aiOverviews = queries.filter(q => q.properties.hasAIOverview);
    
    report += '## Summary Statistics\n\n';
    report += `- Total queries analyzed: ${queries.length}\n`;
    report += `- Queries with AI Overview: ${aiOverviews.length} (${(aiOverviews.length / queries.length * 100).toFixed(1)}%)\n`;
    report += `- Total citations collected: ${Array.from(this.nodes.values()).filter(n => n.type === 'Citation').length}\n`;
    report += `- Unique competitors tracked: ${Array.from(this.nodes.values()).filter(n => n.type === 'Competitor').length}\n\n`;
    
    // Query type breakdown
    report += '## Query Type Analysis\n\n';
    const queryTypes: Record<string, number> = {};
    queries.forEach(q => {
      const type = q.properties.queryType;
      queryTypes[type] = (queryTypes[type] || 0) + 1;
    });
    
    Object.entries(queryTypes)
      .sort(([,a], [,b]) => b - a)
      .forEach(([type, count]) => {
        report += `- ${type}: ${count} queries\n`;
      });
    
    // Competitor visibility
    report += '\n## Competitor Visibility\n\n';
    const competitors = Array.from(this.nodes.values())
      .filter(n => n.type === 'Competitor')
      .map(c => c.properties.domain)
      .sort();
    
    report += '| Competitor | AI Overview Citations | Organic Rankings |\n';
    report += '|------------|---------------------|------------------|\n';
    
    competitors.forEach(domain => {
      const aiCitations = this.relationships
        .filter(r => r.type === 'SHOWS_COMPETITOR' && r.to === `competitor_${domain}`)
        .reduce((sum, r) => sum + (r.properties.citations || 0), 0);
      
      const organicRankings = this.relationships
        .filter(r => r.type === 'RANKS_ORGANICALLY' && r.to === `competitor_${domain}`)
        .length;
      
      report += `| ${domain} | ${aiCitations} | ${organicRankings} |\n`;
    });
    
    await fs.writeFile(outputPath, report);
    console.log(`✅ Report written to ${outputPath}`);
  }
}

// Export functions for direct use
export async function processGEOData(
  resultsPath: string = 'geo-visibility-results.json',
  cypherPath: string = 'geo-import-queries.cypher',
  reportPath: string = 'geo-visibility-report.md'
): Promise<void> {
  const processor = new GEODataProcessor();
  
  await processor.processGEOResults(resultsPath);
  await processor.generateCypherQueries(cypherPath);
  await processor.generateReport(reportPath);
  
  console.log('\n✅ GEO data processing complete!');
  console.log('📊 Next steps:');
  console.log('1. Review the generated report: geo-visibility-report.md');
  console.log('2. Import to Neo4j using: neo4j-shell -f geo-import-queries.cypher');
  console.log('3. Run analysis queries in Neo4j Browser');
}