#!/usr/bin/env ts-node

// GEO Analysis Runner
// Executes Google AI Overview visibility analysis and processes results

import { exec } from 'child_process';
import { promisify } from 'util';
import { processGEOData } from './geo-data-processor';

const execAsync = promisify(exec);

async function runGEOAnalysis() {
  console.log('🚀 Starting Google AI Overview (GEO) Visibility Analysis');
  console.log('=' .repeat(60));
  
  try {
    // Step 1: Run Playwright tests to collect data
    console.log('\n1️⃣ Running GEO visibility tests...');
    console.log('This may take several minutes as we analyze multiple queries.\n');
    
    try {
      const { stdout, stderr } = await execAsync(
        'npx playwright test tests/geo-visibility/google-ai-overview-tracker.test.ts --reporter=list'
      );
      
      if (stdout) console.log(stdout);
      if (stderr && !stderr.includes('Warning')) console.error(stderr);
      
      console.log('\n✅ GEO visibility tests completed!');
      
    } catch (testError: any) {
      if (testError.code === 1 && testError.stdout) {
        // Some tests failed but we got results
        console.log(testError.stdout);
        console.log('\n⚠️ Some tests failed, but continuing with available results...');
      } else {
        throw testError;
      }
    }
    
    // Step 2: Process results for Neo4j
    console.log('\n2️⃣ Processing results for Neo4j import...');
    await processGEOData();
    
    // Step 3: Import to Neo4j (if running)
    console.log('\n3️⃣ Checking Neo4j connection...');
    
    try {
      const { stdout: neo4jCheck } = await execAsync(
        'docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 "RETURN 1;"'
      );
      
      if (neo4jCheck) {
        console.log('✅ Neo4j is running. Importing GEO data...');
        
        // Import the generated Cypher queries
        const { stdout: importResult } = await execAsync(
          'docker exec -i eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 < geo-import-queries.cypher'
        );
        
        console.log('✅ GEO data imported to Neo4j successfully!');
        
        // Run a quick verification query
        const { stdout: verifyResult } = await execAsync(
          'docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 ' +
          '"MATCH (n) WHERE n.id STARTS WITH \'geo_\' OR n.id STARTS WITH \'query_\' RETURN labels(n)[0] as Type, COUNT(n) as Count;"'
        );
        
        console.log('\n📊 Imported data summary:');
        console.log(verifyResult);
      }
      
    } catch (neo4jError) {
      console.log('⚠️ Neo4j is not running. Start Neo4j to import the data:');
      console.log('   docker-compose up -d');
      console.log('   Then run: neo4j-shell -f geo-import-queries.cypher');
    }
    
    // Step 4: Display summary
    console.log('\n4️⃣ Analysis Complete!');
    console.log('=' .repeat(60));
    console.log('\n📁 Generated files:');
    console.log('   - geo-visibility-results.json    (Raw data)');
    console.log('   - geo-import-queries.cypher      (Neo4j import queries)');
    console.log('   - geo-visibility-report.md       (Summary report)');
    
    // Read and display key findings from report
    const fs = require('fs').promises;
    try {
      const report = await fs.readFile('geo-visibility-report.md', 'utf-8');
      const lines = report.split('\n');
      
      console.log('\n🔍 Key Findings:');
      
      // Extract summary statistics
      const summaryStart = lines.findIndex(line => line.includes('## Summary Statistics'));
      if (summaryStart !== -1) {
        for (let i = summaryStart + 2; i < summaryStart + 6 && i < lines.length; i++) {
          if (lines[i].startsWith('-')) {
            console.log('  ' + lines[i]);
          }
        }
      }
      
      // Show competitor rankings
      console.log('\n🏆 Competitor AI Overview Visibility:');
      const tableStart = lines.findIndex(line => line.includes('| Competitor | AI Overview Citations |'));
      if (tableStart !== -1) {
        for (let i = tableStart + 2; i < lines.length && lines[i].startsWith('|'); i++) {
          const parts = lines[i].split('|').map(p => p.trim());
          if (parts.length >= 3 && parts[1]) {
            console.log(`   ${parts[1]}: ${parts[2]} citations`);
          }
        }
      }
      
    } catch (readError) {
      console.log('⚠️ Could not read report file');
    }
    
    // Provide next steps
    console.log('\n📋 Recommended Next Steps:');
    console.log('1. Review the detailed report: cat geo-visibility-report.md');
    console.log('2. Explore data in Neo4j Browser: http://localhost:7474');
    console.log('3. Run custom analysis queries from geo-import-queries.cypher');
    console.log('4. Set up regular monitoring for key queries');
    console.log('5. Compare Eufy\'s visibility against competitors');
    
    // Neo4j query examples
    console.log('\n💡 Useful Neo4j Queries:');
    console.log('\n// Find queries where Eufy appears in AI Overview:');
    console.log('MATCH (q:Query)-[:SHOWS_COMPETITOR]->(c:Competitor {domain: "eufy.com"})');
    console.log('WHERE q.hasAIOverview = true');
    console.log('RETURN q.text as Query, r.citations as Citations');
    console.log('ORDER BY r.citations DESC;');
    
    console.log('\n// Compare competitor visibility scores:');
    console.log('MATCH (q:Query)-[r:SHOWS_COMPETITOR]->(c:Competitor)');
    console.log('WHERE q.hasAIOverview = true');
    console.log('WITH c.name as Competitor, COUNT(DISTINCT q) as Appearances, SUM(r.citations) as TotalCitations');
    console.log('RETURN Competitor, Appearances, TotalCitations, ');
    console.log('       toFloat(TotalCitations) / Appearances as AvgCitationsPerAppearance');
    console.log('ORDER BY Appearances DESC;');
    
  } catch (error: any) {
    console.error('\n❌ Error during GEO analysis:', error.message);
    if (error.stack) {
      console.error('\nStack trace:', error.stack);
    }
    process.exit(1);
  }
}

// Run the analysis
if (require.main === module) {
  runGEOAnalysis().catch(console.error);
}