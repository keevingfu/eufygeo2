#!/bin/bash

# Enhanced Google AI Overview (GEO) Visibility Analysis with SerpAPI
# Provides more accurate data using Google Search API

echo "🤖 Enhanced GEO Visibility Tracker (SerpAPI + Firecrawl)"
echo "========================================================"
echo "Direct Google AI Overview data + validation"
echo ""

# Set environment variables
export SERPAPI_KEY="e221298072d7a290d7a9b66e7b7c006ed968df005fbce8ff5a02e0c62045e190"
export FIRECRAWL_API_KEY="fc-7106bd7009b94c8884a082beaecf4294"
export NODE_ENV="production"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Functions
print_status() {
    echo -e "${BLUE}[$(date +'%H:%M:%S')]${NC} $1"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_info() {
    echo -e "${MAGENTA}ℹ️  $1${NC}"
}

print_highlight() {
    echo -e "${CYAN}🔍 $1${NC}"
}

# Check dependencies
print_status "Checking dependencies..."

if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        print_error "Failed to install dependencies"
        exit 1
    fi
fi

# Main menu
echo ""
print_highlight "Enhanced GEO Analysis Options:"
echo ""
echo "1) Quick Enhanced Analysis - Top queries with SerpAPI (3 min)"
echo "2) Standard Enhanced Analysis - Full comparison (10 min)"
echo "3) Deep Competitive Analysis - All competitors & queries (20 min)"
echo "4) Data Source Comparison - SerpAPI vs Firecrawl validation"
echo "5) Location-Based Analysis - Multi-region GEO visibility"
echo "6) View Previous Enhanced Results"
echo "7) Import to Neo4j"
echo "8) Exit"
echo ""

read -p "Select analysis type (1-8): " choice

case $choice in
    1)
        print_status "Running Quick Enhanced Analysis with SerpAPI..."
        print_info "This uses direct Google API data for highest accuracy"
        npm run test:geo:enhanced -- --grep "AI-optimized queries"
        ;;
    2)
        print_status "Running Standard Enhanced Analysis..."
        print_info "Full SerpAPI analysis with Firecrawl validation"
        npm run analyze:geo:enhanced
        ;;
    3)
        print_status "Running Deep Competitive Analysis..."
        print_warning "This will analyze all competitors across many queries"
        export GEO_ANALYSIS_MODE="deep"
        npm run test:geo:enhanced
        ;;
    4)
        print_status "Running Data Source Comparison..."
        print_info "Validating SerpAPI accuracy against Firecrawl"
        npm run test:geo:enhanced -- --grep "Validate results"
        ;;
    5)
        print_status "Running Location-Based Analysis..."
        print_info "Comparing GEO visibility across regions"
        npm run test:geo:enhanced -- --grep "Location-Based"
        ;;
    6)
        if [ -f "enhanced-geo-visibility-results.json" ]; then
            print_info "Displaying enhanced results..."
            echo ""
            
            # Extract key metrics using Node.js
            node -e "
                const fs = require('fs');
                const data = JSON.parse(fs.readFileSync('enhanced-geo-visibility-results.json'));
                
                console.log('📊 Enhanced GEO Analysis Summary');
                console.log('================================');
                console.log('Analysis Date:', data.metadata.analysisDate);
                console.log('Data Source:', data.metadata.dataSource);
                console.log('');
                console.log('AI Overview Statistics:');
                console.log('- Total Queries:', data.metadata.totalQueries);
                console.log('- With AI Overview:', data.metadata.queriesWithAI, '(' + data.metadata.aiOverviewRate + '%)');
                console.log('');
                console.log('🏆 Competitor Rankings (GEO Score /100):');
                data.competitorRankings.forEach(r => {
                    console.log(r.rank + '.', r.brand + ':', r.avgScore);
                });
                
                if (data.insights && data.insights.eufyWins) {
                    console.log('');
                    console.log('✨ Queries where Eufy leads:');
                    data.insights.eufyWins.forEach(q => console.log('  •', q));
                }
            "
            
            echo ""
            print_info "Full report: enhanced-geo-visibility-report.md"
        else
            print_error "No enhanced results found. Run an analysis first."
        fi
        exit 0
        ;;
    7)
        if [ -f "enhanced-geo-import-queries.cypher" ]; then
            print_status "Importing enhanced GEO data to Neo4j..."
            
            if docker ps | grep -q eufy-seo-neo4j; then
                docker exec -i eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 < enhanced-geo-import-queries.cypher
                
                if [ $? -eq 0 ]; then
                    print_success "Enhanced data imported to Neo4j!"
                    echo ""
                    print_info "Running GEO visibility query..."
                    
                    docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 \
                        "MATCH (c:Competitor)<-[:SHOWS_COMPETITOR]-(q:Query {hasAIOverview: true}) 
                         WITH c.name as Brand, COUNT(DISTINCT q) as AIAppearances 
                         RETURN Brand, AIAppearances 
                         ORDER BY AIAppearances DESC;"
                else
                    print_error "Import failed"
                fi
            else
                print_warning "Neo4j is not running. Start with: docker-compose up -d"
            fi
        else
            print_error "No import file found. Run enhanced analysis first."
        fi
        exit 0
        ;;
    8)
        print_info "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Post-analysis actions
if [[ $choice =~ ^[1-5]$ ]]; then
    echo ""
    print_status "Enhanced analysis complete!"
    echo ""
    
    # Show data source comparison if available
    if [ -f "geo-comparison-results.json" ]; then
        print_highlight "Data Source Reliability:"
        node -e "
            const fs = require('fs');
            const data = JSON.parse(fs.readFileSync('geo-comparison-results.json'));
            
            console.log('- SerpAPI Success Rate:', data.report.summary.serpApiSuccessRate);
            console.log('- Firecrawl Success Rate:', data.report.summary.firecrawlSuccessRate);
            console.log('- Reliability Score:', data.report.reliabilityScore + '/100');
            console.log('');
            data.report.recommendations.forEach(rec => console.log('💡', rec));
        "
    fi
    
    echo ""
    print_info "Available Actions:"
    echo "1. View detailed reports (enhanced-geo-visibility-report.md)"
    echo "2. Import to Neo4j for visualization"
    echo "3. Export data for further analysis"
    echo ""
    
    read -p "Would you like to import to Neo4j now? (y/n): " import_choice
    if [[ $import_choice == "y" || $import_choice == "Y" ]]; then
        $0 && exit  # Re-run script and select option 7
    fi
fi

echo ""
print_status "Enhanced GEO analysis session completed"