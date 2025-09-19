#!/usr/bin/env python3
"""
Eufy Competitor SEO Data Import to Neo4j
Imports competitor organic search data into a Neo4j graph database
"""

import pandas as pd
import os
from urllib.parse import urlparse
from neo4j import GraphDatabase
import logging
from datetime import datetime
import json

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CompetitorSEOGraphImporter:
    def __init__(self, csv_path, neo4j_uri="bolt://localhost:7687", 
                 neo4j_user="neo4j", neo4j_password="password"):
        """
        Initialize the importer with database connection details
        """
        self.csv_path = csv_path
        self.neo4j_uri = neo4j_uri
        self.neo4j_user = neo4j_user
        self.neo4j_password = neo4j_password
        self.driver = None
        
    def connect(self):
        """Connect to Neo4j database"""
        try:
            self.driver = GraphDatabase.driver(
                self.neo4j_uri,
                auth=(self.neo4j_user, self.neo4j_password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")
    
    def clear_database(self):
        """Clear all nodes and relationships from database"""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            logger.info("Cleared existing database")
    
    def create_indexes(self):
        """Create indexes for better query performance"""
        indexes = [
            # Keyword indexes
            "CREATE INDEX keyword_text IF NOT EXISTS FOR (k:Keyword) ON (k.text)",
            "CREATE INDEX keyword_search_volume IF NOT EXISTS FOR (k:Keyword) ON (k.search_volume)",
            "CREATE INDEX keyword_difficulty IF NOT EXISTS FOR (k:Keyword) ON (k.difficulty)",
            
            # URL indexes
            "CREATE INDEX url_address IF NOT EXISTS FOR (u:URL) ON (u.address)",
            "CREATE INDEX url_domain IF NOT EXISTS FOR (u:URL) ON (u.domain)",
            
            # Domain indexes
            "CREATE INDEX domain_name IF NOT EXISTS FOR (d:Domain) ON (d.name)",
            
            # Intent indexes
            "CREATE INDEX intent_type IF NOT EXISTS FOR (i:Intent) ON (i.type)",
            
            # SERP Feature indexes
            "CREATE INDEX serp_feature IF NOT EXISTS FOR (s:SERPFeature) ON (s.name)",
            
            # Timestamp index
            "CREATE INDEX ranking_timestamp IF NOT EXISTS FOR (r:Ranking) ON (r.timestamp)"
        ]
        
        with self.driver.session() as session:
            for index in indexes:
                try:
                    session.run(index)
                    logger.info(f"Created index: {index.split('FOR')[1].split('ON')[0].strip()}")
                except Exception as e:
                    logger.warning(f"Index creation note: {e}")
    
    def extract_domain(self, url):
        """Extract domain from URL"""
        try:
            parsed = urlparse(url)
            domain = parsed.netloc or parsed.path
            # Remove www. prefix if present
            if domain.startswith('www.'):
                domain = domain[4:]
            return domain
        except:
            return "unknown"
    
    def parse_serp_features(self, serp_features_str):
        """Parse SERP features string into list"""
        if pd.isna(serp_features_str) or not serp_features_str:
            return []
        # Assuming comma-separated or similar format
        features = str(serp_features_str).split(',')
        return [f.strip() for f in features if f.strip()]
    
    def parse_intents(self, intents_str):
        """Parse keyword intents string into list"""
        if pd.isna(intents_str) or not intents_str:
            return []
        # Assuming comma-separated or similar format
        intents = str(intents_str).split(',')
        return [i.strip() for i in intents if i.strip()]
    
    def batch_create_nodes(self, session, batch_data):
        """Create nodes in batch for better performance"""
        # Create Keywords
        keyword_query = """
        UNWIND $keywords AS keyword
        MERGE (k:Keyword {text: keyword.text})
        SET k.search_volume = keyword.search_volume,
            k.difficulty = keyword.difficulty,
            k.cpc = keyword.cpc,
            k.competition = keyword.competition,
            k.num_results = keyword.num_results
        """
        
        # Create URLs and Domains
        url_query = """
        UNWIND $urls AS url
        MERGE (u:URL {address: url.address})
        SET u.domain = url.domain
        WITH u, url
        MERGE (d:Domain {name: url.domain})
        MERGE (u)-[:BELONGS_TO]->(d)
        """
        
        # Create Intents
        intent_query = """
        UNWIND $intents AS intent
        MERGE (i:Intent {type: intent})
        """
        
        # Create SERP Features
        serp_query = """
        UNWIND $serp_features AS feature
        MERGE (s:SERPFeature {name: feature})
        """
        
        # Execute queries
        session.run(keyword_query, keywords=batch_data['keywords'])
        session.run(url_query, urls=batch_data['urls'])
        session.run(intent_query, intents=batch_data['intents'])
        session.run(serp_query, serp_features=batch_data['serp_features'])
    
    def batch_create_relationships(self, session, batch_rels):
        """Create relationships in batch"""
        # Ranking relationships
        ranking_query = """
        UNWIND $rankings AS ranking
        MATCH (k:Keyword {text: ranking.keyword})
        MATCH (u:URL {address: ranking.url})
        MERGE (k)-[r:RANKS_FOR {
            position: ranking.position,
            previous_position: ranking.previous_position,
            traffic: ranking.traffic,
            traffic_percent: ranking.traffic_percent,
            traffic_cost: ranking.traffic_cost,
            timestamp: ranking.timestamp,
            position_type: ranking.position_type,
            trends: ranking.trends
        }]->(u)
        """
        
        # Intent relationships
        intent_rel_query = """
        UNWIND $intent_rels AS rel
        MATCH (k:Keyword {text: rel.keyword})
        MATCH (i:Intent {type: rel.intent})
        MERGE (k)-[:HAS_INTENT]->(i)
        """
        
        # SERP Feature relationships
        serp_rel_query = """
        UNWIND $serp_rels AS rel
        MATCH (k:Keyword {text: rel.keyword})
        MATCH (s:SERPFeature {name: rel.feature})
        MERGE (k)-[:HAS_SERP_FEATURE]->(s)
        """
        
        # Execute queries
        if batch_rels['rankings']:
            session.run(ranking_query, rankings=batch_rels['rankings'])
        if batch_rels['intent_rels']:
            session.run(intent_rel_query, intent_rels=batch_rels['intent_rels'])
        if batch_rels['serp_rels']:
            session.run(serp_rel_query, serp_rels=batch_rels['serp_rels'])
    
    def import_data(self, batch_size=1000, clear_existing=False):
        """Main import function"""
        if clear_existing:
            self.clear_database()
        
        # Create indexes first
        self.create_indexes()
        
        # Read CSV file
        logger.info(f"Reading CSV file: {self.csv_path}")
        try:
            df = pd.read_csv(self.csv_path)
            logger.info(f"Loaded {len(df)} rows from CSV")
        except Exception as e:
            logger.error(f"Failed to read CSV: {e}")
            return False
        
        # Process data in batches
        total_rows = len(df)
        
        for start_idx in range(0, total_rows, batch_size):
            end_idx = min(start_idx + batch_size, total_rows)
            batch = df.iloc[start_idx:end_idx]
            
            logger.info(f"Processing batch {start_idx//batch_size + 1}/{(total_rows-1)//batch_size + 1}")
            
            # Prepare batch data
            batch_data = {
                'keywords': [],
                'urls': [],
                'intents': set(),
                'serp_features': set()
            }
            
            batch_rels = {
                'rankings': [],
                'intent_rels': [],
                'serp_rels': []
            }
            
            for _, row in batch.iterrows():
                # Prepare keyword data
                keyword_text = str(row['Keyword'])
                batch_data['keywords'].append({
                    'text': keyword_text,
                    'search_volume': row.get('Search Volume', 0),
                    'difficulty': row.get('Keyword Difficulty', 0),
                    'cpc': row.get('CPC', 0.0),
                    'competition': row.get('Competition', 0.0),
                    'num_results': row.get('Number of Results', 0)
                })
                
                # Prepare URL data
                url = str(row.get('URL', ''))
                if url and url != 'nan':
                    domain = self.extract_domain(url)
                    batch_data['urls'].append({
                        'address': url,
                        'domain': domain
                    })
                    
                    # Prepare ranking relationship
                    batch_rels['rankings'].append({
                        'keyword': keyword_text,
                        'url': url,
                        'position': row.get('Position', 0),
                        'previous_position': row.get('Previous position', 0),
                        'traffic': row.get('Traffic', 0),
                        'traffic_percent': row.get('Traffic (%)', 0.0),
                        'traffic_cost': row.get('Traffic Cost', 0.0),
                        'timestamp': row.get('Timestamp', datetime.now().isoformat()),
                        'position_type': row.get('Position Type', 'organic'),
                        'trends': str(row.get('Trends', ''))
                    })
                
                # Process intents
                intents = self.parse_intents(row.get('Keyword Intents'))
                for intent in intents:
                    batch_data['intents'].add(intent)
                    batch_rels['intent_rels'].append({
                        'keyword': keyword_text,
                        'intent': intent
                    })
                
                # Process SERP features
                serp_features = self.parse_serp_features(row.get('SERP Features by Keyword'))
                for feature in serp_features:
                    batch_data['serp_features'].add(feature)
                    batch_rels['serp_rels'].append({
                        'keyword': keyword_text,
                        'feature': feature
                    })
            
            # Convert sets to lists
            batch_data['intents'] = list(batch_data['intents'])
            batch_data['serp_features'] = list(batch_data['serp_features'])
            
            # Create nodes and relationships
            with self.driver.session() as session:
                self.batch_create_nodes(session, batch_data)
                self.batch_create_relationships(session, batch_rels)
            
            logger.info(f"Batch {start_idx//batch_size + 1} completed")
        
        logger.info("Data import completed successfully!")
        return True
    
    def create_competitor_analysis_views(self):
        """Create useful analysis views and aggregations"""
        views = [
            # Top competitors by keyword coverage
            ("Top Competitors", """
            MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
            WITH d.name AS competitor, COUNT(DISTINCT k) AS keyword_count,
                 SUM(r.traffic) AS total_traffic,
                 AVG(r.position) AS avg_position
            RETURN competitor, keyword_count, total_traffic, 
                   ROUND(avg_position, 2) AS avg_position
            ORDER BY keyword_count DESC
            LIMIT 20
            """),
            
            # Keywords with multiple competitors
            ("Competitive Keywords", """
            MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
            WITH k.text AS keyword, k.search_volume AS volume,
                 COUNT(DISTINCT d) AS competitor_count,
                 COLLECT(DISTINCT d.name) AS competitors
            WHERE competitor_count > 3
            RETURN keyword, volume, competitor_count, competitors
            ORDER BY volume DESC
            LIMIT 50
            """),
            
            # High-value keyword opportunities
            ("High Value Opportunities", """
            MATCH (k:Keyword)
            WHERE k.search_volume > 1000 AND k.difficulty < 50
            OPTIONAL MATCH (k)-[r:RANKS_FOR]->(u:URL)
            WITH k, COUNT(r) AS ranking_count, MIN(r.position) AS best_position
            WHERE ranking_count < 5 OR best_position > 10
            RETURN k.text AS keyword, k.search_volume AS volume,
                   k.difficulty AS difficulty, k.cpc AS cpc,
                   ranking_count, best_position
            ORDER BY volume DESC
            LIMIT 100
            """)
        ]
        
        with self.driver.session() as session:
            for view_name, query in views:
                logger.info(f"Creating view: {view_name}")
                result = session.run(query)
                records = list(result)
                logger.info(f"  Found {len(records)} results")
                if records:
                    # Show first 3 results as sample
                    for record in records[:3]:
                        logger.info(f"    {dict(record)}")
    
    def get_database_stats(self):
        """Get database statistics"""
        stats_queries = {
            "Total Keywords": "MATCH (k:Keyword) RETURN COUNT(k) AS count",
            "Total URLs": "MATCH (u:URL) RETURN COUNT(u) AS count",
            "Total Domains": "MATCH (d:Domain) RETURN COUNT(d) AS count",
            "Total Rankings": "MATCH ()-[r:RANKS_FOR]->() RETURN COUNT(r) AS count",
            "Total Intents": "MATCH (i:Intent) RETURN COUNT(i) AS count",
            "Total SERP Features": "MATCH (s:SERPFeature) RETURN COUNT(s) AS count"
        }
        
        logger.info("\n" + "="*60)
        logger.info("DATABASE STATISTICS")
        logger.info("="*60)
        
        with self.driver.session() as session:
            for stat_name, query in stats_queries.items():
                result = session.run(query).single()
                count = result['count'] if result else 0
                logger.info(f"{stat_name}: {count:,}")
        
        logger.info("="*60)


def main():
    """Main execution function"""
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║     Eufy Competitor SEO Data Neo4j Import Tool          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    # Configuration
    CSV_FILE = "/Users/cavin/Desktop/dev/eufygeo2/eufy-competitor-organic-us-202509.csv"
    
    # Neo4j connection settings
    # Note: Update these settings based on your Neo4j installation
    NEO4J_URI = "bolt://localhost:7687"
    NEO4J_USER = "neo4j"
    NEO4J_PASSWORD = "eufyseo2024"  # Using configured password from docker-compose.yml
    
    # Create importer instance
    importer = CompetitorSEOGraphImporter(
        csv_path=CSV_FILE,
        neo4j_uri=NEO4J_URI,
        neo4j_user=NEO4J_USER,
        neo4j_password=NEO4J_PASSWORD
    )
    
    # Connect to database
    if not importer.connect():
        print("Failed to connect to Neo4j. Please ensure Neo4j is running.")
        print("\nTo start Neo4j:")
        print("1. Install Neo4j Desktop or Community Edition")
        print("2. Create a new database or use existing")
        print("3. Start the database")
        print("4. Update connection settings in this script")
        return
    
    try:
        # Clear existing data for fresh import
        clear_existing = True  # Auto-set to True for clean import
        
        # Import data
        print("\nStarting data import...")
        print("This may take several minutes for large datasets...")
        
        success = importer.import_data(
            batch_size=1000,
            clear_existing=clear_existing
        )
        
        if success:
            # Show statistics
            importer.get_database_stats()
            
            # Create analysis views
            print("\nCreating analysis views...")
            importer.create_competitor_analysis_views()
            
            print("\n✅ Import completed successfully!")
            print("\nYou can now:")
            print("1. Open Neo4j Browser at http://localhost:7474")
            print("2. Run Cypher queries to analyze the data")
            print("3. Use Neo4j Bloom for visualization")
            
            print("\nSample queries to try:")
            print("- MATCH (n) RETURN n LIMIT 100")
            print("- MATCH (k:Keyword)-[:RANKS_FOR]->(u:URL) RETURN k, u LIMIT 50")
            print("- MATCH (d:Domain) RETURN d.name, SIZE((d)<-[:BELONGS_TO]-()) AS pages")
        else:
            print("\n❌ Import failed. Please check the logs above.")
    
    finally:
        importer.close()


if __name__ == "__main__":
    main()
