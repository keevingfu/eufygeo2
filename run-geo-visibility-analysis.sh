#!/bin/bash

# Google AI Overview (GEO) Visibility Analysis Runner
# Collects and analyzes competitor visibility in Google's AI-generated search results

echo "🤖 Google AI Overview (GEO) Visibility Tracker"
echo "=============================================="
echo "Analyzing competitor visibility in AI-generated search results"
echo ""

# Set environment variables
export FIRECRAWL_API_KEY="fc-7106bd7009b94c8884a082beaecf4294"
export NODE_ENV="production"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# Function to print colored output
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

# Check dependencies
print_status "Checking dependencies..."

if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18+."
    exit 1
fi

if ! command -v npx &> /dev/null; then
    print_error "npx is not available. Please install npm."
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    print_status "Installing dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        print_error "Failed to install dependencies"
        exit 1
    fi
fi

# Check if TypeScript is available
if [ ! -d "node_modules/typescript" ]; then
    print_status "Installing TypeScript..."
    npm install --save-dev typescript ts-node
fi

# Main menu
echo ""
echo "🎯 GEO Analysis Options:"
echo ""
echo "1) Quick Analysis - Top queries only (5 min)"
echo "2) Standard Analysis - All query types (15 min)"
echo "3) Deep Analysis - Extended competitor set (30 min)"
echo "4) Custom Analysis - Select specific queries"
echo "5) View Previous Results"
echo "6) Generate Neo4j Import"
echo "7) Exit"
echo ""

read -p "Select analysis type (1-7): " choice

case $choice in
    1)
        print_status "Running Quick GEO Analysis..."
        export GEO_ANALYSIS_MODE="quick"
        npm run analyze:geo
        ;;
    2)
        print_status "Running Standard GEO Analysis..."
        export GEO_ANALYSIS_MODE="standard"
        npm run analyze:geo
        ;;
    3)
        print_status "Running Deep GEO Analysis..."
        print_warning "This will take approximately 30 minutes"
        export GEO_ANALYSIS_MODE="deep"
        npm run analyze:geo
        ;;
    4)
        echo ""
        echo "Select query categories to analyze:"
        echo "a) Informational queries"
        echo "b) Comparative queries"
        echo "c) Technical queries"
        echo "d) Purchasing queries"
        echo ""
        read -p "Enter selections (e.g., 'abc'): " selections
        
        export GEO_ANALYSIS_MODE="custom"
        export GEO_QUERY_TYPES="$selections"
        npm run analyze:geo
        ;;
    5)
        if [ -f "geo-visibility-report.md" ]; then
            print_info "Displaying previous results..."
            echo ""
            cat geo-visibility-report.md
        else
            print_error "No previous results found. Run an analysis first."
        fi
        exit 0
        ;;
    6)
        if [ -f "geo-visibility-results.json" ]; then
            print_status "Generating Neo4j import from existing data..."
            npx ts-node -e "
                const { processGEOData } = require('./tests/geo-visibility/geo-data-processor');
                processGEOData().catch(console.error);
            "
        else
            print_error "No results found. Run an analysis first."
        fi
        exit 0
        ;;
    7)
        print_info "Exiting..."
        exit 0
        ;;
    *)
        print_error "Invalid choice"
        exit 1
        ;;
esac

# Post-analysis actions
if [[ $choice =~ ^[1-4]$ ]]; then
    echo ""
    print_status "Analysis complete! Next steps:"
    echo ""
    
    # Check if results were generated
    if [ -f "geo-visibility-results.json" ]; then
        print_success "Results saved to: geo-visibility-results.json"
        
        # Show summary
        if [ -f "geo-visibility-report.md" ]; then
            echo ""
            print_info "Summary Report:"
            echo ""
            # Show first 20 lines of report
            head -n 30 geo-visibility-report.md
            echo ""
            echo "... (see full report in geo-visibility-report.md)"
        fi
        
        # Offer Neo4j import
        echo ""
        read -p "Import results to Neo4j? (y/n): " import_neo4j
        if [[ $import_neo4j == "y" || $import_neo4j == "Y" ]]; then
            print_status "Checking Neo4j..."
            
            # Check if Neo4j is running
            if docker ps | grep -q eufy-seo-neo4j; then
                print_status "Importing to Neo4j..."
                docker exec -i eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 < geo-import-queries.cypher
                
                if [ $? -eq 0 ]; then
                    print_success "Data imported to Neo4j!"
                    echo ""
                    print_info "View in Neo4j Browser: http://localhost:7474"
                    print_info "Username: neo4j, Password: eufyseo2024"
                else
                    print_error "Failed to import to Neo4j"
                fi
            else
                print_warning "Neo4j is not running. Start it with: docker-compose up -d"
            fi
        fi
        
        # Suggest visualizations
        echo ""
        print_info "Visualization Options:"
        echo "1. Open Neo4j Browser for graph visualization"
        echo "2. View Eufy dashboard: http://localhost:5001"
        echo "3. Generate custom reports with Neo4j queries"
        
    else
        print_error "No results were generated. Check for errors above."
    fi
fi

echo ""
print_status "GEO Analysis session ended"