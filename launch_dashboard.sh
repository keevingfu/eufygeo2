#!/bin/bash

# ============================================================
# Eufy Neo4j SEO Analysis Dashboard Launcher
# ============================================================

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Eufy Competitor SEO Analysis Dashboard              ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if Neo4j is running
check_neo4j() {
    if [ "$(docker ps -q -f name=eufy-seo-neo4j)" ]; then
        echo -e "${GREEN}✅ Neo4j is running${NC}"
        return 0
    else
        echo -e "${RED}❌ Neo4j is not running${NC}"
        return 1
    fi
}

# Start Neo4j if not running
start_neo4j() {
    if ! check_neo4j; then
        echo -e "${YELLOW}Starting Neo4j...${NC}"
        docker-compose up -d neo4j
        
        echo "Waiting for Neo4j to be ready..."
        sleep 10
        
        while [ "$(docker inspect -f '{{.State.Health.Status}}' eufy-seo-neo4j 2>/dev/null)" != "healthy" ]; do
            echo -n "."
            sleep 2
        done
        echo ""
        echo -e "${GREEN}✅ Neo4j started successfully${NC}"
    fi
}

# Install Python dependencies
install_dependencies() {
    echo -e "${YELLOW}Installing Python dependencies...${NC}"
    pip3 install -q flask flask-cors neo4j pandas
    echo -e "${GREEN}✅ Dependencies installed${NC}"
}

# Start the dashboard server
start_dashboard() {
    echo -e "${YELLOW}Starting dashboard server...${NC}"
    echo ""
    echo "=============================================="
    echo "📊 Dashboard will be available at:"
    echo -e "${BLUE}http://localhost:5001${NC}"
    echo ""
    echo "📱 Access from other devices at:"
    echo -e "${BLUE}http://$(ipconfig getifaddr en0 2>/dev/null || hostname -I | awk '{print $1}'):5001${NC}"
    echo "=============================================="
    echo ""
    echo "Press Ctrl+C to stop the server"
    echo ""
    
    # Run the Flask server
    python3 neo4j_dashboard_server.py 5001
}

# Main execution
main() {
    echo -e "${BLUE}🔍 Checking system requirements...${NC}"
    echo ""
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker is not installed${NC}"
        echo "Please install Docker Desktop first"
        exit 1
    fi
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python 3 is not installed${NC}"
        echo "Please install Python 3 first"
        exit 1
    fi
    
    # Start Neo4j
    start_neo4j
    
    # Install dependencies
    install_dependencies
    
    echo ""
    echo -e "${GREEN}✅ All systems ready!${NC}"
    echo ""
    
    # Check if data exists
    HAS_DATA=$(docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 \
        "MATCH (n) RETURN COUNT(n) AS count LIMIT 1;" 2>/dev/null | grep -o '[0-9]*' | head -1)
    
    if [ -z "$HAS_DATA" ] || [ "$HAS_DATA" -eq "0" ]; then
        echo -e "${YELLOW}⚠️  No data found in Neo4j${NC}"
        echo "Please import data first using:"
        echo "  python3 import_competitor_data_to_neo4j.py"
        echo ""
        read -p "Continue anyway? (y/N): " continue
        if [[ ! $continue =~ ^[Yy]$ ]]; then
            exit 0
        fi
    else
        echo -e "${GREEN}✅ Found $HAS_DATA nodes in database${NC}"
    fi
    
    echo ""
    
    # Start dashboard
    start_dashboard
}

# Handle cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Shutting down...${NC}"
    # Optionally stop Neo4j
    read -p "Stop Neo4j database? (y/N): " stop_neo4j
    if [[ $stop_neo4j =~ ^[Yy]$ ]]; then
        docker-compose down
        echo -e "${GREEN}✅ Neo4j stopped${NC}"
    fi
    echo "Goodbye!"
}

trap cleanup EXIT

# Run main function
main
