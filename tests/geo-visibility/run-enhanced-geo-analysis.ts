#!/usr/bin/env ts-node

// Enhanced GEO Analysis Runner with SerpAPI Integration
// Provides more accurate Google AI Overview visibility tracking

import { exec } from 'child_process';
import { promisify } from 'util';
import { createGEOComparisonAnalyzer } from './geo-comparison-analyzer';
import { processGEOData } from './geo-data-processor';

const execAsync = promisify(exec);

// Configuration
const SERPAPI_KEY = process.env.SERPAPI_KEY || 'e221298072d7a290d7a9b66e7b7c006ed968df005fbce8ff5a02e0c62045e190';

async function runEnhancedGEOAnalysis() {
  console.log('🚀 Enhanced Google AI Overview (GEO) Visibility Analysis');
  console.log('Powered by SerpAPI + Firecrawl Integration');
  console.log('=' .repeat(60));
  
  try {
    // Step 1: Run enhanced GEO tests with SerpAPI
    console.log('\n1️⃣ Running enhanced GEO visibility tests with SerpAPI...');
    console.log('This provides direct access to Google\'s AI Overview data.\n');
    
    try {
      const { stdout, stderr } = await execAsync(
        'npx playwright test tests/geo-visibility/enhanced-geo-tracker.test.ts --reporter=list'
      );
      
      if (stdout) console.log(stdout);
      if (stderr && !stderr.includes('Warning')) console.error(stderr);
      
      console.log('\n✅ Enhanced GEO tests completed!');
      
    } catch (testError: any) {
      if (testError.code === 1 && testError.stdout) {
        console.log(testError.stdout);
        console.log('\n⚠️ Some tests encountered issues, continuing with available results...');
      } else {
        throw testError;
      }
    }
    
    // Step 2: Run comparison analysis
    console.log('\n2️⃣ Running comparison analysis between SerpAPI and Firecrawl...');
    
    const analyzer = createGEOComparisonAnalyzer(SERPAPI_KEY);
    
    // Test queries for comparison
    const comparisonQueries = [
      'best home security camera',
      'eufy vs arlo',
      'wireless security camera setup',
      'security camera buying guide'
    ];
    
    console.log(`Comparing ${comparisonQueries.length} queries...\n`);
    
    await analyzer.batchCompare(comparisonQueries, 2000);
    
    // Generate comparison report
    const comparisonReport = analyzer.generateReport();
    console.log('\n📊 Data Source Comparison:');
    console.log(`   - SerpAPI Success Rate: ${comparisonReport.summary.serpApiSuccessRate}`);
    console.log(`   - Firecrawl Success Rate: ${comparisonReport.summary.firecrawlSuccessRate}`);
    console.log(`   - Average Confidence: ${comparisonReport.summary.avgConfidence}%`);
    console.log(`   - Reliability Score: ${comparisonReport.reliabilityScore}/100`);
    
    // Export comparison results
    await analyzer.exportResults('geo-comparison-results.json');
    
    // Step 3: Process results for Neo4j
    console.log('\n3️⃣ Processing enhanced results for Neo4j import...');
    
    // Check if enhanced results exist
    const fs = require('fs').promises;
    let resultsProcessed = false;
    
    try {
      await fs.access('enhanced-geo-visibility-results.json');
      console.log('Processing enhanced results...');
      
      // Process the enhanced data
      await processGEOData(
        'enhanced-geo-visibility-results.json',
        'enhanced-geo-import-queries.cypher',
        'enhanced-geo-visibility-report.md'
      );
      
      resultsProcessed = true;
      
    } catch (error) {
      console.log('⚠️ Enhanced results not found, using comparison results instead...');
      
      // Process comparison results as fallback
      await processGEOData(
        'geo-comparison-results.json',
        'geo-comparison-import-queries.cypher',
        'geo-comparison-report.md'
      );
    }
    
    // Step 4: Import to Neo4j
    console.log('\n4️⃣ Checking Neo4j connection...');
    
    try {
      const { stdout: neo4jCheck } = await execAsync(
        'docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 "RETURN 1;"'
      );
      
      if (neo4jCheck) {
        console.log('✅ Neo4j is running. Importing enhanced GEO data...');
        
        const cypherFile = resultsProcessed ? 
          'enhanced-geo-import-queries.cypher' : 
          'geo-comparison-import-queries.cypher';
        
        const { stdout: importResult } = await execAsync(
          `docker exec -i eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 < ${cypherFile}`
        );
        
        console.log('✅ Enhanced GEO data imported to Neo4j!');
        
        // Run verification query
        const { stdout: verifyResult } = await execAsync(
          'docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 ' +
          '"MATCH (c:Competitor)<-[:SHOWS_COMPETITOR]-(q:Query) ' +
          'WHERE q.hasAIOverview = true ' +
          'WITH c, COUNT(DISTINCT q) as aiAppearances ' +
          'RETURN c.name as Competitor, aiAppearances ' +
          'ORDER BY aiAppearances DESC LIMIT 5;"'
        );
        
        console.log('\n🏆 Top competitors in AI Overviews:');
        console.log(verifyResult);
      }
      
    } catch (neo4jError) {
      console.log('⚠️ Neo4j is not running. Start it to import the data:');
      console.log('   docker-compose up -d');
      console.log(`   Then run: neo4j-shell -f ${resultsProcessed ? 'enhanced-geo-import-queries.cypher' : 'geo-comparison-import-queries.cypher'}`);
    }
    
    // Step 5: Display insights and recommendations
    console.log('\n5️⃣ Analysis Complete!');
    console.log('=' .repeat(60));
    
    console.log('\n📁 Generated files:');
    console.log('   - enhanced-geo-visibility-results.json  (SerpAPI enhanced data)');
    console.log('   - geo-comparison-results.json           (Data source comparison)');
    console.log('   - *-import-queries.cypher               (Neo4j import scripts)');
    console.log('   - *-report.md                           (Summary reports)');
    
    // Read and display key insights
    try {
      const enhancedData = await fs.readFile('enhanced-geo-visibility-results.json', 'utf-8');
      const parsed = JSON.parse(enhancedData);
      
      console.log('\n🔍 Key Insights from Enhanced Analysis:');
      console.log(`   - AI Overview Rate: ${parsed.metadata.aiOverviewRate}%`);
      console.log(`   - Data Quality: High (direct Google API access)`);
      
      if (parsed.competitorRankings && parsed.competitorRankings.length > 0) {
        console.log('\n🏆 GEO Visibility Rankings (Average Score /100):');
        parsed.competitorRankings.slice(0, 5).forEach((comp: any) => {
          console.log(`   ${comp.rank}. ${comp.brand}: ${comp.avgScore}`);
        });
      }
      
      if (parsed.insights && parsed.insights.opportunities) {
        console.log('\n💡 Top Improvement Opportunities:');
        parsed.insights.opportunities.slice(0, 3).forEach((opp: any) => {
          console.log(`   - "${opp.query}" (Current score: ${opp.currentScore}/100)`);
          if (opp.recommendations && opp.recommendations.length > 0) {
            console.log(`     Recommendation: ${opp.recommendations[0]}`);
          }
        });
      }
      
    } catch (readError) {
      console.log('⚠️ Could not read enhanced results');
    }
    
    // Provide recommendations based on comparison
    console.log('\n📋 Recommendations from Comparison Analysis:');
    if (comparisonReport.recommendations) {
      comparisonReport.recommendations.forEach(rec => {
        console.log(`   • ${rec}`);
      });
    }
    
    console.log('\n🎯 Next Steps:');
    console.log('1. Review the enhanced report for detailed insights');
    console.log('2. Focus on queries where competitors dominate AI Overviews');
    console.log('3. Implement GEO optimization strategies:');
    console.log('   - Create comprehensive, structured content');
    console.log('   - Use clear headings and bullet points');
    console.log('   - Include authoritative sources and data');
    console.log('   - Optimize for featured snippets');
    console.log('4. Monitor changes in AI Overview visibility weekly');
    
    // Neo4j analysis queries
    console.log('\n💡 Useful Neo4j Queries for GEO Analysis:');
    
    console.log('\n// Find queries where Eufy is NOT in AI Overview but competitors are:');
    console.log('MATCH (q:Query)-[:SHOWS_COMPETITOR]->(c:Competitor)');
    console.log('WHERE q.hasAIOverview = true AND c.domain <> "eufy.com"');
    console.log('AND NOT EXISTS {');
    console.log('  MATCH (q)-[:SHOWS_COMPETITOR]->(eufy:Competitor {domain: "eufy.com"})');
    console.log('}');
    console.log('RETURN q.text as OpportunityQuery, COLLECT(c.name) as Competitors');
    console.log('ORDER BY SIZE(COLLECT(c.name)) DESC;');
    
    console.log('\n// Calculate GEO market share:');
    console.log('MATCH (q:Query {hasAIOverview: true})');
    console.log('WITH COUNT(DISTINCT q) as totalAIQueries');
    console.log('MATCH (q2:Query {hasAIOverview: true})-[:SHOWS_COMPETITOR]->(c:Competitor)');
    console.log('WITH c.name as Brand, COUNT(DISTINCT q2) as appearances, totalAIQueries');
    console.log('RETURN Brand, appearances, ');
    console.log('       ROUND(toFloat(appearances) * 100 / totalAIQueries, 1) as MarketSharePercent');
    console.log('ORDER BY appearances DESC;');
    
  } catch (error: any) {
    console.error('\n❌ Error during enhanced GEO analysis:', error.message);
    if (error.stack) {
      console.error('\nStack trace:', error.stack);
    }
    process.exit(1);
  }
}

// Run the enhanced analysis
if (require.main === module) {
  runEnhancedGEOAnalysis().catch(console.error);
}