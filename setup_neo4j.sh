#!/bin/bash

# ============================================================
# Eufy Competitor SEO Neo4j Setup Script
# ============================================================

echo "╔══════════════════════════════════════════════════════════╗"
echo "║     Eufy Competitor SEO Neo4j Database Setup            ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed${NC}"
    echo "Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker is running
if ! docker info &> /dev/null; then
    echo -e "${RED}❌ Docker is not running${NC}"
    echo "Please start Docker Desktop and try again"
    exit 1
fi

echo -e "${GREEN}✅ Docker is installed and running${NC}"

# Function to display menu
show_menu() {
    echo ""
    echo "Select an option:"
    echo "1) Start Neo4j database"
    echo "2) Stop Neo4j database"
    echo "3) Import CSV data to Neo4j"
    echo "4) View database status"
    echo "5) Open Neo4j Browser"
    echo "6) Run sample Cypher queries"
    echo "7) Clean database (remove all data)"
    echo "8) Complete setup (start + import)"
    echo "9) Exit"
    echo ""
}

# Start Neo4j
start_neo4j() {
    echo -e "${YELLOW}Starting Neo4j database...${NC}"
    docker-compose up -d neo4j
    
    echo "Waiting for Neo4j to be ready..."
    sleep 10
    
    # Wait for Neo4j to be healthy
    while [ "$(docker inspect -f '{{.State.Health.Status}}' eufy-seo-neo4j 2>/dev/null)" != "healthy" ]; do
        echo -n "."
        sleep 2
    done
    
    echo ""
    echo -e "${GREEN}✅ Neo4j is running!${NC}"
    echo ""
    echo "Access Neo4j Browser at: http://localhost:7474"
    echo "Username: neo4j"
    echo "Password: eufyseo2024"
    echo ""
}

# Stop Neo4j
stop_neo4j() {
    echo -e "${YELLOW}Stopping Neo4j database...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ Neo4j stopped${NC}"
}

# Import data
import_data() {
    echo -e "${YELLOW}Importing CSV data to Neo4j...${NC}"
    
    # Check if Neo4j is running
    if [ "$(docker ps -q -f name=eufy-seo-neo4j)" ]; then
        # Check if CSV file exists
        if [ ! -f "eufycompetitororganicus202509.csv" ]; then
            echo -e "${RED}❌ CSV file not found: eufycompetitororganicus202509.csv${NC}"
            echo "Please ensure the CSV file is in the current directory"
            return 1
        fi
        
        # Install required Python packages
        echo "Installing required Python packages..."
        pip3 install -q neo4j pandas
        
        # Run import script
        echo "Running import script..."
        python3 import_competitor_data_to_neo4j.py
        
        echo -e "${GREEN}✅ Data import completed${NC}"
    else
        echo -e "${RED}❌ Neo4j is not running. Please start it first.${NC}"
    fi
}

# View status
view_status() {
    echo -e "${YELLOW}Neo4j Database Status:${NC}"
    echo ""
    
    if [ "$(docker ps -q -f name=eufy-seo-neo4j)" ]; then
        echo -e "${GREEN}✅ Neo4j is running${NC}"
        docker ps --filter name=eufy-seo-neo4j --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
        
        # Show database stats if available
        echo ""
        echo "Database Statistics:"
        docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 \
            "MATCH (n) RETURN labels(n)[0] AS NodeType, COUNT(n) AS Count ORDER BY Count DESC;" 2>/dev/null || \
            echo "Run data import to populate database"
    else
        echo -e "${RED}❌ Neo4j is not running${NC}"
    fi
}

# Open browser
open_browser() {
    URL="http://localhost:7474"
    echo -e "${YELLOW}Opening Neo4j Browser...${NC}"
    
    # Check which OS and open browser accordingly
    if [[ "$OSTYPE" == "darwin"* ]]; then
        open $URL
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        xdg-open $URL
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        start $URL
    else
        echo "Please open your browser and navigate to: $URL"
    fi
}

# Run sample queries
run_samples() {
    echo -e "${YELLOW}Running sample Cypher queries...${NC}"
    
    if [ "$(docker ps -q -f name=eufy-seo-neo4j)" ]; then
        echo ""
        echo "1. Top 5 Competitors by Keyword Count:"
        docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 \
            "MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword) 
             WITH d.name AS competitor, COUNT(DISTINCT k) AS keyword_count 
             RETURN competitor, keyword_count 
             ORDER BY keyword_count DESC LIMIT 5;" 2>/dev/null || \
            echo "No data found. Please import data first."
        
        echo ""
        echo "2. High-Value Keyword Opportunities:"
        docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 \
            "MATCH (k:Keyword) 
             WHERE k.search_volume > 5000 AND k.difficulty < 40 
             RETURN k.text AS keyword, k.search_volume AS volume, k.difficulty AS difficulty 
             ORDER BY volume DESC LIMIT 5;" 2>/dev/null || \
            echo "No data found. Please import data first."
    else
        echo -e "${RED}❌ Neo4j is not running${NC}"
    fi
}

# Clean database
clean_database() {
    echo -e "${YELLOW}⚠️  WARNING: This will delete all data in the database!${NC}"
    read -p "Are you sure? (y/N): " confirm
    
    if [[ $confirm == [yY] ]]; then
        if [ "$(docker ps -q -f name=eufy-seo-neo4j)" ]; then
            docker exec eufy-seo-neo4j cypher-shell -u neo4j -p eufyseo2024 \
                "MATCH (n) DETACH DELETE n;" 2>/dev/null
            echo -e "${GREEN}✅ Database cleaned${NC}"
        else
            echo -e "${RED}❌ Neo4j is not running${NC}"
        fi
    else
        echo "Cancelled"
    fi
}

# Complete setup
complete_setup() {
    echo -e "${YELLOW}Running complete setup...${NC}"
    start_neo4j
    import_data
    view_status
    echo ""
    echo -e "${GREEN}✅ Setup completed!${NC}"
    echo ""
    echo "You can now:"
    echo "1. Access Neo4j Browser at: http://localhost:7474"
    echo "2. Login with username: neo4j, password: eufyseo2024"
    echo "3. Run queries from neo4j_cypher_queries.cypher file"
}

# Main loop
while true; do
    show_menu
    read -p "Enter your choice: " choice
    
    case $choice in
        1) start_neo4j ;;
        2) stop_neo4j ;;
        3) import_data ;;
        4) view_status ;;
        5) open_browser ;;
        6) run_samples ;;
        7) clean_database ;;
        8) complete_setup ;;
        9) echo "Goodbye!"; exit 0 ;;
        *) echo -e "${RED}Invalid option${NC}" ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
done
