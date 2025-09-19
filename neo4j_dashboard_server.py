#!/usr/bin/env python3
"""
Neo4j SEO Analysis API Server
Provides REST API endpoints for the frontend dashboard
"""

from flask import Flask, jsonify, request, render_template_string
from flask_cors import CORS
from neo4j import GraphDatabase
import json
from datetime import datetime
import os

app = Flask(__name__)
CORS(app)

# Neo4j connection configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "eufyseo2024")

class Neo4jConnection:
    def __init__(self):
        self.driver = None
        self.connect()
    
    def connect(self):
        try:
            self.driver = GraphDatabase.driver(
                NEO4J_URI,
                auth=(NEO4J_USER, NEO4J_PASSWORD)
            )
        except Exception as e:
            print(f"Failed to connect to Neo4j: {e}")
    
    def close(self):
        if self.driver:
            self.driver.close()
    
    def query(self, cypher_query, parameters=None):
        with self.driver.session() as session:
            result = session.run(cypher_query, parameters or {})
            return [dict(record) for record in result]

# Initialize database connection
db = Neo4jConnection()

# API Endpoints

@app.route('/api/overview')
def get_overview():
    """Get database overview statistics"""
    queries = {
        'total_keywords': "MATCH (k:Keyword) RETURN COUNT(k) AS count",
        'total_domains': "MATCH (d:Domain) RETURN COUNT(d) AS count",
        'total_urls': "MATCH (u:URL) RETURN COUNT(u) AS count",
        'total_rankings': "MATCH ()-[r:RANKS_FOR]->() RETURN COUNT(r) AS count",
        'avg_position': """
            MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)
            RETURN ROUND(AVG(r.position), 2) AS avg_position
        """,
        'total_search_volume': """
            MATCH (k:Keyword)
            RETURN SUM(k.search_volume) AS total_volume
        """
    }
    
    stats = {}
    for key, query in queries.items():
        result = db.query(query)
        if result and result[0]:
            value = list(result[0].values())[0]
            stats[key] = value if value is not None else 0
        else:
            stats[key] = 0
    
    return jsonify(stats)

@app.route('/api/competitors')
def get_competitors():
    """Get top competitors analysis"""
    query = """
    MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
    WITH d.name AS competitor,
         COUNT(DISTINCT k) AS keyword_count,
         SUM(r.traffic) AS total_traffic,
         AVG(r.position) AS avg_position,
         SUM(r.traffic_cost) AS traffic_value,
         COUNT(DISTINCT CASE WHEN r.position <= 3 THEN k END) AS top3_count,
         COUNT(DISTINCT CASE WHEN r.position <= 10 THEN k END) AS top10_count
    RETURN competitor,
           keyword_count,
           total_traffic,
           ROUND(avg_position, 2) AS avg_position,
           ROUND(traffic_value, 2) AS traffic_value,
           top3_count,
           top10_count
    ORDER BY keyword_count DESC
    LIMIT 20
    """
    
    return jsonify(db.query(query))

@app.route('/api/keyword-opportunities')
def get_keyword_opportunities():
    """Get high-value keyword opportunities"""
    query = """
    MATCH (k:Keyword)
    WHERE k.search_volume > 1000 AND k.difficulty < 50
    OPTIONAL MATCH (k)-[r:RANKS_FOR]->(u:URL)
    WITH k, COUNT(r) AS competitor_count, MIN(r.position) AS best_position
    WHERE competitor_count < 5 OR best_position > 10 OR best_position IS NULL
    RETURN k.text AS keyword,
           k.search_volume AS volume,
           k.difficulty AS difficulty,
           k.cpc AS cpc,
           competitor_count,
           best_position,
           ROUND(k.search_volume * k.cpc, 2) AS potential_value
    ORDER BY potential_value DESC
    LIMIT 50
    """
    
    return jsonify(db.query(query))

@app.route('/api/competitive-gaps')
def get_competitive_gaps():
    """Find keywords where competitors rank but not Eufy"""
    query = """
    MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
    WHERE r.position <= 20 AND k.search_volume > 500
    WITH k, MIN(r.position) AS best_competitor_position, COLLECT(DISTINCT d.name) AS competitors
    WHERE NOT 'eufy.com' IN competitors
    RETURN k.text AS keyword,
           k.search_volume AS volume,
           k.difficulty AS difficulty,
           best_competitor_position,
           k.cpc AS cpc,
           competitors[0..5] AS top_competitors
    ORDER BY volume DESC
    LIMIT 100
    """
    
    return jsonify(db.query(query))

@app.route('/api/market-share')
def get_market_share():
    """Calculate market share by domain"""
    query = """
    MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
    WHERE r.position <= 10
    WITH SUM(k.search_volume) AS total_market_volume
    MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
    WHERE r.position <= 10
    WITH d.name AS domain,
         SUM(k.search_volume) AS domain_volume,
         total_market_volume
    RETURN domain,
           domain_volume,
           ROUND(100.0 * domain_volume / total_market_volume, 2) AS market_share_percent
    ORDER BY domain_volume DESC
    LIMIT 15
    """
    
    return jsonify(db.query(query))

@app.route('/api/keyword-clusters')
def get_keyword_clusters():
    """Find keyword clusters based on ranking URLs"""
    query = """
    MATCH (u:URL)<-[:RANKS_FOR]-(k:Keyword)
    WITH u, COLLECT(k.text) AS keywords, COUNT(k) AS keyword_count, SUM(k.search_volume) AS total_volume
    WHERE keyword_count >= 5
    RETURN u.address AS url,
           keyword_count,
           total_volume,
           keywords[0..10] AS sample_keywords
    ORDER BY total_volume DESC
    LIMIT 30
    """
    
    return jsonify(db.query(query))

@app.route('/api/intent-analysis')
def get_intent_analysis():
    """Analyze search intent distribution"""
    query = """
    MATCH (i:Intent)<-[:HAS_INTENT]-(k:Keyword)
    WITH i.type AS intent,
         COUNT(k) AS keyword_count,
         SUM(k.search_volume) AS total_volume,
         AVG(k.difficulty) AS avg_difficulty,
         AVG(k.cpc) AS avg_cpc
    RETURN intent,
           keyword_count,
           total_volume,
           ROUND(avg_difficulty, 2) AS avg_difficulty,
           ROUND(avg_cpc, 2) AS avg_cpc
    ORDER BY total_volume DESC
    """
    
    return jsonify(db.query(query))

@app.route('/api/serp-features')
def get_serp_features():
    """Analyze SERP feature distribution"""
    query = """
    MATCH (s:SERPFeature)<-[:HAS_SERP_FEATURE]-(k:Keyword)
    WITH s.name AS feature,
         COUNT(k) AS keyword_count,
         SUM(k.search_volume) AS total_volume,
         AVG(k.difficulty) AS avg_difficulty
    RETURN feature,
           keyword_count,
           total_volume,
           ROUND(avg_difficulty, 2) AS avg_difficulty
    ORDER BY keyword_count DESC
    LIMIT 20
    """
    
    return jsonify(db.query(query))

@app.route('/api/position-changes')
def get_position_changes():
    """Track significant position changes"""
    query = """
    MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
    WHERE ABS(r.position - r.previous_position) > 5 
      AND r.previous_position > 0
      AND k.search_volume > 1000
    RETURN k.text AS keyword,
           d.name AS domain,
           r.previous_position AS old_position,
           r.position AS new_position,
           (r.previous_position - r.position) AS position_change,
           k.search_volume AS volume
    ORDER BY ABS(position_change) DESC
    LIMIT 50
    """
    
    return jsonify(db.query(query))

@app.route('/api/competitive-landscape')
def get_competitive_landscape():
    """Get comprehensive competitive landscape data"""
    query = """
    MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
    WITH d,
         COUNT(DISTINCT k) AS total_keywords,
         COUNT(DISTINCT CASE WHEN r.position <= 3 THEN k END) AS top3_keywords,
         COUNT(DISTINCT CASE WHEN r.position BETWEEN 4 AND 10 THEN k END) AS top4_10_keywords,
         SUM(r.traffic) AS total_traffic,
         SUM(r.traffic_cost) AS total_traffic_value,
         AVG(r.position) AS avg_position,
         AVG(k.difficulty) AS avg_keyword_difficulty
    RETURN d.name AS competitor,
           total_keywords,
           top3_keywords,
           top4_10_keywords,
           total_traffic,
           ROUND(total_traffic_value, 2) AS traffic_value,
           ROUND(avg_position, 2) AS avg_position,
           ROUND(avg_keyword_difficulty, 2) AS avg_difficulty
    ORDER BY total_keywords DESC
    LIMIT 25
    """
    
    return jsonify(db.query(query))

@app.route('/api/graph-visualization')
def get_graph_visualization():
    """Get data for graph visualization"""
    limit = request.args.get('limit', 100, type=int)
    query = """
    MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
    WHERE k.search_volume > 5000 AND r.position <= 10
    WITH k, u, d, r
    LIMIT $limit
    RETURN k.text AS keyword,
           k.search_volume AS volume,
           u.address AS url,
           d.name AS domain,
           r.position AS position
    """
    
    data = db.query(query, {'limit': limit})
    
    # Format for D3.js force graph
    nodes = []
    links = []
    node_map = {}
    
    for row in data:
        # Add keyword node
        keyword_id = f"keyword_{row['keyword']}"
        if keyword_id not in node_map:
            nodes.append({
                'id': keyword_id,
                'label': row['keyword'],
                'type': 'keyword',
                'value': row['volume']
            })
            node_map[keyword_id] = True
        
        # Add domain node
        domain_id = f"domain_{row['domain']}"
        if domain_id not in node_map:
            nodes.append({
                'id': domain_id,
                'label': row['domain'],
                'type': 'domain',
                'value': 1
            })
            node_map[domain_id] = True
        
        # Add link
        links.append({
            'source': keyword_id,
            'target': domain_id,
            'value': 11 - row['position']  # Higher value for better positions
        })
    
    return jsonify({'nodes': nodes, 'links': links})

@app.route('/api/custom-query', methods=['POST'])
def run_custom_query():
    """Execute custom Cypher query (with safety limits)"""
    try:
        query = request.json.get('query', '')
        
        # Basic safety checks
        forbidden_keywords = ['DELETE', 'REMOVE', 'CREATE', 'MERGE', 'SET', 'DETACH']
        if any(keyword in query.upper() for keyword in forbidden_keywords):
            return jsonify({'error': 'Only read queries are allowed'}), 403
        
        # Add limit if not present
        if 'LIMIT' not in query.upper():
            query += ' LIMIT 100'
        
        result = db.query(query)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/')
def dashboard():
    """Serve the main dashboard HTML"""
    return render_template_string(DASHBOARD_HTML)

# Dashboard HTML Template
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eufy Competitor SEO Analysis - Neo4j Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/d3/7.8.5/d3.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.5.0/axios.min.js"></script>
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #0891b2;
            --secondary: #6366f1;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #0f172a;
            --card: #1e293b;
            --text: #f1f5f9;
            --text-secondary: #94a3b8;
            --border: #334155;
            --gradient-1: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --gradient-2: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            --gradient-3: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, #1a202c 100%);
            min-height: 100vh;
            color: var(--text);
        }

        .container {
            max-width: 1920px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(20px);
            border-radius: 20px;
            padding: 30px;
            margin-bottom: 30px;
            border: 1px solid var(--border);
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
        }

        .header h1 {
            font-size: 2.8em;
            font-weight: 800;
            background: linear-gradient(90deg, var(--primary), var(--secondary), #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .header .subtitle {
            color: var(--text-secondary);
            font-size: 1.2em;
            margin-bottom: 20px;
        }

        .nav-tabs {
            display: flex;
            gap: 15px;
            flex-wrap: wrap;
        }

        .nav-tab {
            padding: 12px 24px;
            background: rgba(30, 41, 59, 0.6);
            border: 1px solid var(--border);
            border-radius: 12px;
            cursor: pointer;
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 600;
        }

        .nav-tab:hover {
            background: rgba(30, 41, 59, 0.9);
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.2);
        }

        .nav-tab.active {
            background: var(--gradient-1);
            border-color: transparent;
            color: white;
        }

        .nav-tab i {
            font-size: 1.2em;
        }

        .content-section {
            display: none;
            animation: fadeIn 0.5s ease;
        }

        .content-section.active {
            display: block;
        }

        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }

        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 16px;
            padding: 24px;
            border: 1px solid var(--border);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }

        .metric-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 3px;
            background: var(--gradient-1);
        }

        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0, 0, 0, 0.3);
        }

        .metric-card .icon {
            width: 50px;
            height: 50px;
            border-radius: 12px;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 1.5em;
            margin-bottom: 15px;
        }

        .metric-card.primary .icon { background: rgba(8, 145, 178, 0.2); color: var(--primary); }
        .metric-card.secondary .icon { background: rgba(99, 102, 241, 0.2); color: var(--secondary); }
        .metric-card.success .icon { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .metric-card.warning .icon { background: rgba(245, 158, 11, 0.2); color: var(--warning); }

        .metric-card .label {
            color: var(--text-secondary);
            font-size: 0.9em;
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .metric-card .value {
            font-size: 2.2em;
            font-weight: 700;
            margin-bottom: 10px;
        }

        .metric-card .change {
            font-size: 0.9em;
            color: var(--success);
            display: flex;
            align-items: center;
            gap: 5px;
        }

        .chart-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .chart-card {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid var(--border);
        }

        .chart-card.full-width {
            grid-column: 1 / -1;
        }

        .chart-card h3 {
            font-size: 1.4em;
            margin-bottom: 20px;
            color: var(--text);
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .chart-container {
            width: 100%;
            height: 400px;
        }

        .table-container {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid var(--border);
            overflow-x: auto;
        }

        .table-container h3 {
            font-size: 1.4em;
            margin-bottom: 20px;
            color: var(--text);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background: rgba(8, 145, 178, 0.1);
            padding: 14px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid var(--border);
            position: sticky;
            top: 0;
            z-index: 10;
        }

        td {
            padding: 14px;
            border-bottom: 1px solid rgba(51, 65, 85, 0.3);
            color: var(--text-secondary);
        }

        tr:hover {
            background: rgba(8, 145, 178, 0.05);
        }

        .badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .badge.primary { background: rgba(8, 145, 178, 0.2); color: var(--primary); }
        .badge.success { background: rgba(16, 185, 129, 0.2); color: var(--success); }
        .badge.warning { background: rgba(245, 158, 11, 0.2); color: var(--warning); }
        .badge.danger { background: rgba(239, 68, 68, 0.2); color: var(--danger); }

        .graph-container {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid var(--border);
            height: 600px;
            position: relative;
        }

        #graphVisualization {
            width: 100%;
            height: 100%;
        }

        .query-container {
            background: rgba(30, 41, 59, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid var(--border);
            margin-bottom: 20px;
        }

        .query-input {
            width: 100%;
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 12px;
            border-radius: 10px;
            font-family: 'Monaco', 'Courier New', monospace;
            font-size: 14px;
            min-height: 100px;
            resize: vertical;
        }

        .query-button {
            margin-top: 15px;
            padding: 12px 24px;
            background: var(--gradient-1);
            border: none;
            border-radius: 10px;
            color: white;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .query-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.3);
        }

        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }

        .spinner {
            border: 3px solid rgba(8, 145, 178, 0.2);
            border-top: 3px solid var(--primary);
            border-radius: 50%;
            width: 40px;
            height: 40px;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .filter-controls {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }

        .filter-control {
            display: flex;
            flex-direction: column;
            gap: 5px;
        }

        .filter-control label {
            font-size: 0.9em;
            color: var(--text-secondary);
        }

        .filter-control select,
        .filter-control input {
            background: rgba(15, 23, 42, 0.6);
            border: 1px solid var(--border);
            color: var(--text);
            padding: 8px 12px;
            border-radius: 8px;
        }

        @media (max-width: 768px) {
            .chart-grid { grid-template-columns: 1fr; }
            .metrics-grid { grid-template-columns: 1fr; }
            .nav-tabs { flex-direction: column; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 Eufy Competitor SEO Analysis</h1>
            <div class="subtitle">Neo4j Graph Database Intelligence Dashboard</div>
            
            <div class="nav-tabs">
                <div class="nav-tab active" data-section="overview">
                    <i class="fas fa-chart-line"></i> Overview
                </div>
                <div class="nav-tab" data-section="competitors">
                    <i class="fas fa-users"></i> Competitors
                </div>
                <div class="nav-tab" data-section="opportunities">
                    <i class="fas fa-lightbulb"></i> Opportunities
                </div>
                <div class="nav-tab" data-section="gaps">
                    <i class="fas fa-search-minus"></i> Content Gaps
                </div>
                <div class="nav-tab" data-section="clusters">
                    <i class="fas fa-project-diagram"></i> Keyword Clusters
                </div>
                <div class="nav-tab" data-section="visualization">
                    <i class="fas fa-network-wired"></i> Graph View
                </div>
                <div class="nav-tab" data-section="query">
                    <i class="fas fa-terminal"></i> Query Console
                </div>
            </div>
        </div>

        <!-- Overview Section -->
        <div id="overview" class="content-section active">
            <div class="metrics-grid">
                <div class="metric-card primary">
                    <div class="icon"><i class="fas fa-key"></i></div>
                    <div class="label">Total Keywords</div>
                    <div class="value" id="totalKeywords">-</div>
                    <div class="change"><i class="fas fa-chart-up"></i> Live Data</div>
                </div>
                
                <div class="metric-card secondary">
                    <div class="icon"><i class="fas fa-globe"></i></div>
                    <div class="label">Domains Analyzed</div>
                    <div class="value" id="totalDomains">-</div>
                    <div class="change"><i class="fas fa-check-circle"></i> Active</div>
                </div>
                
                <div class="metric-card success">
                    <div class="icon"><i class="fas fa-link"></i></div>
                    <div class="label">Total URLs</div>
                    <div class="value" id="totalUrls">-</div>
                    <div class="change"><i class="fas fa-database"></i> Indexed</div>
                </div>
                
                <div class="metric-card warning">
                    <div class="icon"><i class="fas fa-search"></i></div>
                    <div class="label">Search Volume</div>
                    <div class="value" id="totalVolume">-</div>
                    <div class="change"><i class="fas fa-trending-up"></i> Monthly</div>
                </div>
            </div>

            <div class="chart-grid">
                <div class="chart-card">
                    <h3><i class="fas fa-chart-pie"></i> Market Share Distribution</h3>
                    <div id="marketShareChart" class="chart-container"></div>
                </div>
                
                <div class="chart-card">
                    <h3><i class="fas fa-bullseye"></i> Search Intent Analysis</h3>
                    <div id="intentChart" class="chart-container"></div>
                </div>
                
                <div class="chart-card full-width">
                    <h3><i class="fas fa-trophy"></i> Top Competitors Performance</h3>
                    <div id="competitorChart" class="chart-container"></div>
                </div>
            </div>
        </div>

        <!-- Competitors Section -->
        <div id="competitors" class="content-section">
            <div class="chart-grid">
                <div class="chart-card full-width">
                    <h3><i class="fas fa-chart-bar"></i> Competitive Landscape Analysis</h3>
                    <div id="landscapeChart" class="chart-container"></div>
                </div>
            </div>
            
            <div class="table-container">
                <h3><i class="fas fa-table"></i> Competitor Details</h3>
                <table id="competitorTable">
                    <thead>
                        <tr>
                            <th>Competitor</th>
                            <th>Keywords</th>
                            <th>Top 3</th>
                            <th>Top 10</th>
                            <th>Traffic</th>
                            <th>Traffic Value</th>
                            <th>Avg Position</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="7" class="loading"><div class="spinner"></div></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Opportunities Section -->
        <div id="opportunities" class="content-section">
            <div class="filter-controls">
                <div class="filter-control">
                    <label>Min Volume</label>
                    <input type="number" id="minVolume" value="1000" />
                </div>
                <div class="filter-control">
                    <label>Max Difficulty</label>
                    <input type="number" id="maxDifficulty" value="50" />
                </div>
                <div class="filter-control">
                    <label>Sort By</label>
                    <select id="sortBy">
                        <option value="volume">Search Volume</option>
                        <option value="difficulty">Difficulty</option>
                        <option value="value">Potential Value</option>
                    </select>
                </div>
            </div>
            
            <div class="chart-grid">
                <div class="chart-card full-width">
                    <h3><i class="fas fa-gem"></i> High-Value Keyword Opportunities</h3>
                    <div id="opportunityChart" class="chart-container"></div>
                </div>
            </div>
            
            <div class="table-container">
                <h3><i class="fas fa-list"></i> Opportunity Details</h3>
                <table id="opportunityTable">
                    <thead>
                        <tr>
                            <th>Keyword</th>
                            <th>Volume</th>
                            <th>Difficulty</th>
                            <th>CPC</th>
                            <th>Competitors</th>
                            <th>Best Position</th>
                            <th>Potential Value</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="7" class="loading"><div class="spinner"></div></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Content Gaps Section -->
        <div id="gaps" class="content-section">
            <div class="chart-grid">
                <div class="chart-card">
                    <h3><i class="fas fa-chart-scatter"></i> Content Gap Matrix</h3>
                    <div id="gapChart" class="chart-container"></div>
                </div>
                
                <div class="chart-card">
                    <h3><i class="fas fa-tags"></i> SERP Features Distribution</h3>
                    <div id="serpChart" class="chart-container"></div>
                </div>
            </div>
            
            <div class="table-container">
                <h3><i class="fas fa-exclamation-triangle"></i> Critical Content Gaps</h3>
                <table id="gapTable">
                    <thead>
                        <tr>
                            <th>Keyword</th>
                            <th>Volume</th>
                            <th>Difficulty</th>
                            <th>Best Competitor Position</th>
                            <th>CPC</th>
                            <th>Top Competitors</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="6" class="loading"><div class="spinner"></div></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Keyword Clusters Section -->
        <div id="clusters" class="content-section">
            <div class="chart-grid">
                <div class="chart-card full-width">
                    <h3><i class="fas fa-sitemap"></i> Keyword Cluster Visualization</h3>
                    <div id="clusterChart" class="chart-container"></div>
                </div>
            </div>
            
            <div class="table-container">
                <h3><i class="fas fa-layer-group"></i> Cluster Details</h3>
                <table id="clusterTable">
                    <thead>
                        <tr>
                            <th>URL</th>
                            <th>Keywords Count</th>
                            <th>Total Volume</th>
                            <th>Sample Keywords</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr><td colspan="4" class="loading"><div class="spinner"></div></td></tr>
                    </tbody>
                </table>
            </div>
        </div>

        <!-- Graph Visualization Section -->
        <div id="visualization" class="content-section">
            <div class="filter-controls">
                <div class="filter-control">
                    <label>Node Limit</label>
                    <select id="graphLimit">
                        <option value="50">50 nodes</option>
                        <option value="100" selected>100 nodes</option>
                        <option value="200">200 nodes</option>
                        <option value="500">500 nodes</option>
                    </select>
                </div>
            </div>
            
            <div class="graph-container">
                <h3><i class="fas fa-project-diagram"></i> Interactive Knowledge Graph</h3>
                <svg id="graphVisualization"></svg>
            </div>
        </div>

        <!-- Query Console Section -->
        <div id="query" class="content-section">
            <div class="query-container">
                <h3><i class="fas fa-code"></i> Cypher Query Console</h3>
                <textarea class="query-input" id="queryInput" placeholder="Enter your Cypher query here...
Example:
MATCH (k:Keyword)-[:RANKS_FOR]->(u:URL)
WHERE k.search_volume > 5000
RETURN k.text, u.address, k.search_volume
LIMIT 10"></textarea>
                <button class="query-button" onclick="runCustomQuery()">
                    <i class="fas fa-play"></i> Run Query
                </button>
            </div>
            
            <div class="table-container">
                <h3><i class="fas fa-table"></i> Query Results</h3>
                <div id="queryResults"></div>
            </div>
        </div>
    </div>

    <script>
        const API_BASE = 'http://localhost:5001/api';
        let currentSection = 'overview';
        
        // Chart theme
        const chartTheme = {
            color: ['#0891b2', '#6366f1', '#10b981', '#f59e0b', '#ef4444', '#ec4899', '#8b5cf6'],
            backgroundColor: 'transparent',
            textStyle: { color: '#f1f5f9' },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true }
        };

        // Navigation
        document.querySelectorAll('.nav-tab').forEach(tab => {
            tab.addEventListener('click', () => {
                const section = tab.dataset.section;
                
                // Update active tab
                document.querySelectorAll('.nav-tab').forEach(t => t.classList.remove('active'));
                tab.classList.add('active');
                
                // Update active section
                document.querySelectorAll('.content-section').forEach(s => s.classList.remove('active'));
                document.getElementById(section).classList.add('active');
                
                currentSection = section;
                
                // Load section data
                loadSectionData(section);
            });
        });

        // Load section data
        async function loadSectionData(section) {
            switch(section) {
                case 'overview':
                    await loadOverview();
                    break;
                case 'competitors':
                    await loadCompetitors();
                    break;
                case 'opportunities':
                    await loadOpportunities();
                    break;
                case 'gaps':
                    await loadGaps();
                    break;
                case 'clusters':
                    await loadClusters();
                    break;
                case 'visualization':
                    await loadGraphVisualization();
                    break;
            }
        }

        // Load overview data
        async function loadOverview() {
            try {
                // Load metrics
                const stats = await axios.get(`${API_BASE}/overview`);
                document.getElementById('totalKeywords').textContent = 
                    (stats.data.total_keywords || 0).toLocaleString();
                document.getElementById('totalDomains').textContent = 
                    (stats.data.total_domains || 0).toLocaleString();
                document.getElementById('totalUrls').textContent = 
                    (stats.data.total_urls || 0).toLocaleString();
                document.getElementById('totalVolume').textContent = 
                    ((stats.data.total_search_volume || 0) / 1000000).toFixed(1) + 'M';
                
                // Load market share chart
                const marketShare = await axios.get(`${API_BASE}/market-share`);
                renderMarketShareChart(marketShare.data);
                
                // Load intent chart
                const intents = await axios.get(`${API_BASE}/intent-analysis`);
                renderIntentChart(intents.data);
                
                // Load competitor chart
                const competitors = await axios.get(`${API_BASE}/competitors`);
                renderCompetitorChart(competitors.data);
                
            } catch (error) {
                console.error('Error loading overview:', error);
            }
        }

        // Render market share chart
        function renderMarketShareChart(data) {
            const chart = echarts.init(document.getElementById('marketShareChart'));
            const option = {
                ...chartTheme,
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {d}%'
                },
                series: [{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: data.map(item => ({
                        value: item.domain_volume,
                        name: item.domain,
                        label: {
                            formatter: '{b}\\n{d}%'
                        }
                    })),
                    itemStyle: {
                        borderRadius: 10
                    }
                }]
            };
            chart.setOption(option);
        }

        // Render intent chart
        function renderIntentChart(data) {
            const chart = echarts.init(document.getElementById('intentChart'));
            const option = {
                ...chartTheme,
                tooltip: { trigger: 'axis' },
                xAxis: {
                    type: 'category',
                    data: data.map(item => item.intent || 'Unknown'),
                    axisLabel: { rotate: 45 }
                },
                yAxis: { type: 'value', name: 'Keywords' },
                series: [{
                    type: 'bar',
                    data: data.map(item => item.keyword_count),
                    itemStyle: {
                        color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
                            { offset: 0, color: '#0891b2' },
                            { offset: 1, color: '#6366f1' }
                        ]),
                        borderRadius: [8, 8, 0, 0]
                    }
                }]
            };
            chart.setOption(option);
        }

        // Render competitor chart
        function renderCompetitorChart(data) {
            const chart = echarts.init(document.getElementById('competitorChart'));
            const topCompetitors = data.slice(0, 10);
            
            const option = {
                ...chartTheme,
                tooltip: { trigger: 'axis' },
                legend: {
                    data: ['Keywords', 'Traffic', 'Top 10'],
                    textStyle: { color: '#94a3b8' }
                },
                xAxis: {
                    type: 'category',
                    data: topCompetitors.map(item => item.competitor)
                },
                yAxis: [
                    { type: 'value', name: 'Count' },
                    { type: 'value', name: 'Traffic' }
                ],
                series: [
                    {
                        name: 'Keywords',
                        type: 'bar',
                        data: topCompetitors.map(item => item.keyword_count),
                        itemStyle: { color: '#0891b2' }
                    },
                    {
                        name: 'Top 10',
                        type: 'bar',
                        data: topCompetitors.map(item => item.top10_count),
                        itemStyle: { color: '#6366f1' }
                    },
                    {
                        name: 'Traffic',
                        type: 'line',
                        yAxisIndex: 1,
                        data: topCompetitors.map(item => item.total_traffic),
                        smooth: true,
                        itemStyle: { color: '#10b981' }
                    }
                ]
            };
            chart.setOption(option);
        }

        // Load competitors data
        async function loadCompetitors() {
            try {
                const landscape = await axios.get(`${API_BASE}/competitive-landscape`);
                renderLandscapeChart(landscape.data);
                renderCompetitorTable(landscape.data);
            } catch (error) {
                console.error('Error loading competitors:', error);
            }
        }

        // Render landscape chart
        function renderLandscapeChart(data) {
            const chart = echarts.init(document.getElementById('landscapeChart'));
            const option = {
                ...chartTheme,
                tooltip: {
                    trigger: 'axis',
                    axisPointer: { type: 'cross' }
                },
                xAxis: {
                    type: 'value',
                    name: 'Total Keywords',
                    nameLocation: 'middle',
                    nameGap: 30
                },
                yAxis: {
                    type: 'value',
                    name: 'Traffic Value',
                    nameLocation: 'middle',
                    nameGap: 50
                },
                series: [{
                    type: 'scatter',
                    symbolSize: function(data) {
                        return Math.sqrt(data[2]) / 10;
                    },
                    data: data.map(item => [
                        item.total_keywords,
                        item.traffic_value,
                        item.total_traffic,
                        item.competitor
                    ]),
                    itemStyle: {
                        color: function(params) {
                            const value = params.value[0];
                            if (value > 10000) return '#ef4444';
                            if (value > 5000) return '#f59e0b';
                            if (value > 1000) return '#10b981';
                            return '#6366f1';
                        },
                        opacity: 0.7
                    },
                    emphasis: {
                        itemStyle: {
                            opacity: 1,
                            shadowBlur: 10,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
            };
            chart.setOption(option);
        }

        // Render competitor table
        function renderCompetitorTable(data) {
            const tbody = document.querySelector('#competitorTable tbody');
            tbody.innerHTML = '';
            
            data.forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 600">${item.competitor}</td>
                    <td>${item.total_keywords.toLocaleString()}</td>
                    <td><span class="badge success">${item.top3_keywords}</span></td>
                    <td><span class="badge primary">${item.top4_10_keywords}</span></td>
                    <td>${(item.total_traffic || 0).toLocaleString()}</td>
                    <td>$${(item.traffic_value || 0).toFixed(2)}</td>
                    <td>${item.avg_position}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Load opportunities
        async function loadOpportunities() {
            try {
                const opportunities = await axios.get(`${API_BASE}/keyword-opportunities`);
                renderOpportunityChart(opportunities.data);
                renderOpportunityTable(opportunities.data);
            } catch (error) {
                console.error('Error loading opportunities:', error);
            }
        }

        // Render opportunity chart
        function renderOpportunityChart(data) {
            const chart = echarts.init(document.getElementById('opportunityChart'));
            const topData = data.slice(0, 20);
            
            const option = {
                ...chartTheme,
                tooltip: {
                    trigger: 'axis',
                    formatter: function(params) {
                        const item = params[0];
                        return `${item.name}<br/>
                                Volume: ${item.value}<br/>
                                Difficulty: ${topData[item.dataIndex].difficulty}<br/>
                                Value: $${topData[item.dataIndex].potential_value}`;
                    }
                },
                xAxis: {
                    type: 'category',
                    data: topData.map(item => item.keyword),
                    axisLabel: {
                        rotate: 45,
                        interval: 0,
                        formatter: function(value) {
                            return value.length > 15 ? value.substr(0, 15) + '...' : value;
                        }
                    }
                },
                yAxis: {
                    type: 'value',
                    name: 'Search Volume'
                },
                series: [{
                    type: 'bar',
                    data: topData.map(item => item.volume),
                    itemStyle: {
                        color: function(params) {
                            const difficulty = topData[params.dataIndex].difficulty;
                            if (difficulty < 30) return '#10b981';
                            if (difficulty < 50) return '#f59e0b';
                            return '#ef4444';
                        },
                        borderRadius: [8, 8, 0, 0]
                    }
                }]
            };
            chart.setOption(option);
        }

        // Render opportunity table
        function renderOpportunityTable(data) {
            const tbody = document.querySelector('#opportunityTable tbody');
            tbody.innerHTML = '';
            
            data.slice(0, 50).forEach(item => {
                const tr = document.createElement('tr');
                const difficultyClass = item.difficulty < 30 ? 'success' : 
                                       item.difficulty < 50 ? 'warning' : 'danger';
                
                tr.innerHTML = `
                    <td style="font-weight: 600">${item.keyword}</td>
                    <td>${item.volume.toLocaleString()}</td>
                    <td><span class="badge ${difficultyClass}">${item.difficulty}</span></td>
                    <td>$${(item.cpc || 0).toFixed(2)}</td>
                    <td>${item.competitor_count}</td>
                    <td>${item.best_position || 'N/A'}</td>
                    <td style="font-weight: 600; color: var(--success)">
                        $${(item.potential_value || 0).toFixed(2)}
                    </td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Load content gaps
        async function loadGaps() {
            try {
                const gaps = await axios.get(`${API_BASE}/competitive-gaps`);
                renderGapChart(gaps.data);
                renderGapTable(gaps.data);
                
                const serp = await axios.get(`${API_BASE}/serp-features`);
                renderSerpChart(serp.data);
            } catch (error) {
                console.error('Error loading gaps:', error);
            }
        }

        // Render gap chart
        function renderGapChart(data) {
            const chart = echarts.init(document.getElementById('gapChart'));
            const option = {
                ...chartTheme,
                tooltip: {
                    trigger: 'item',
                    formatter: function(params) {
                        const d = params.data;
                        return `${d[3]}<br/>
                                Volume: ${d[0]}<br/>
                                Difficulty: ${d[1]}<br/>
                                Best Position: ${d[2]}`;
                    }
                },
                xAxis: {
                    type: 'value',
                    name: 'Search Volume',
                    nameLocation: 'middle',
                    nameGap: 30
                },
                yAxis: {
                    type: 'value',
                    name: 'Difficulty',
                    nameLocation: 'middle',
                    nameGap: 50
                },
                series: [{
                    type: 'scatter',
                    symbolSize: function(data) {
                        return Math.sqrt(data[0]) / 10;
                    },
                    data: data.slice(0, 100).map(item => [
                        item.volume,
                        item.difficulty,
                        item.best_competitor_position,
                        item.keyword
                    ]),
                    itemStyle: {
                        color: function(params) {
                            const pos = params.value[2];
                            if (pos <= 3) return '#ef4444';
                            if (pos <= 10) return '#f59e0b';
                            return '#10b981';
                        },
                        opacity: 0.6
                    }
                }]
            };
            chart.setOption(option);
        }

        // Render SERP chart
        function renderSerpChart(data) {
            const chart = echarts.init(document.getElementById('serpChart'));
            const option = {
                ...chartTheme,
                tooltip: {
                    trigger: 'item',
                    formatter: '{b}: {c} keywords'
                },
                series: [{
                    type: 'pie',
                    radius: '60%',
                    data: data.slice(0, 10).map(item => ({
                        value: item.keyword_count,
                        name: item.feature || 'Unknown'
                    })),
                    itemStyle: {
                        borderRadius: 5
                    }
                }]
            };
            chart.setOption(option);
        }

        // Render gap table
        function renderGapTable(data) {
            const tbody = document.querySelector('#gapTable tbody');
            tbody.innerHTML = '';
            
            data.slice(0, 50).forEach(item => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td style="font-weight: 600">${item.keyword}</td>
                    <td>${item.volume.toLocaleString()}</td>
                    <td><span class="badge warning">${item.difficulty}</span></td>
                    <td><span class="badge danger">Position ${item.best_competitor_position}</span></td>
                    <td>$${(item.cpc || 0).toFixed(2)}</td>
                    <td>${(item.top_competitors || []).join(', ')}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Load keyword clusters
        async function loadClusters() {
            try {
                const clusters = await axios.get(`${API_BASE}/keyword-clusters`);
                renderClusterChart(clusters.data);
                renderClusterTable(clusters.data);
            } catch (error) {
                console.error('Error loading clusters:', error);
            }
        }

        // Render cluster chart
        function renderClusterChart(data) {
            const chart = echarts.init(document.getElementById('clusterChart'));
            const nodes = [];
            const links = [];
            
            data.slice(0, 20).forEach((cluster, idx) => {
                // Add URL node
                nodes.push({
                    id: `url_${idx}`,
                    name: cluster.url.split('/').pop() || 'Home',
                    symbolSize: Math.sqrt(cluster.total_volume) / 50,
                    category: 0,
                    value: cluster.total_volume
                });
                
                // Add keyword nodes
                cluster.sample_keywords.forEach((keyword, kidx) => {
                    const keywordId = `keyword_${idx}_${kidx}`;
                    nodes.push({
                        id: keywordId,
                        name: keyword,
                        symbolSize: 10,
                        category: 1
                    });
                    
                    links.push({
                        source: `url_${idx}`,
                        target: keywordId
                    });
                });
            });
            
            const option = {
                ...chartTheme,
                tooltip: {
                    trigger: 'item',
                    formatter: function(params) {
                        if (params.dataType === 'node') {
                            return `${params.name}<br/>Value: ${params.value || 'N/A'}`;
                        }
                        return params.name;
                    }
                },
                legend: {
                    data: ['URL', 'Keyword'],
                    textStyle: { color: '#94a3b8' }
                },
                series: [{
                    type: 'graph',
                    layout: 'force',
                    data: nodes,
                    links: links,
                    categories: [
                        { name: 'URL', itemStyle: { color: '#0891b2' } },
                        { name: 'Keyword', itemStyle: { color: '#6366f1' } }
                    ],
                    roam: true,
                    label: {
                        show: true,
                        position: 'right',
                        formatter: '{b}'
                    },
                    force: {
                        repulsion: 100,
                        edgeLength: 50
                    }
                }]
            };
            chart.setOption(option);
        }

        // Render cluster table
        function renderClusterTable(data) {
            const tbody = document.querySelector('#clusterTable tbody');
            tbody.innerHTML = '';
            
            data.forEach(item => {
                const tr = document.createElement('tr');
                const shortUrl = item.url.length > 50 ? 
                    item.url.substr(0, 50) + '...' : item.url;
                
                tr.innerHTML = `
                    <td title="${item.url}">${shortUrl}</td>
                    <td><span class="badge primary">${item.keyword_count}</span></td>
                    <td>${(item.total_volume || 0).toLocaleString()}</td>
                    <td>${item.sample_keywords.slice(0, 5).join(', ')}</td>
                `;
                tbody.appendChild(tr);
            });
        }

        // Load graph visualization
        async function loadGraphVisualization() {
            try {
                const limit = document.getElementById('graphLimit').value;
                const response = await axios.get(`${API_BASE}/graph-visualization?limit=${limit}`);
                renderForceGraph(response.data);
            } catch (error) {
                console.error('Error loading graph:', error);
            }
        }

        // Render D3 force graph
        function renderForceGraph(data) {
            const container = document.getElementById('graphVisualization');
            const width = container.clientWidth;
            const height = container.clientHeight;
            
            // Clear previous graph
            d3.select(container).selectAll('*').remove();
            
            const svg = d3.select(container)
                .attr('width', width)
                .attr('height', height);
            
            const simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.links).id(d => d.id).distance(50))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2));
            
            const link = svg.append('g')
                .selectAll('line')
                .data(data.links)
                .enter().append('line')
                .attr('stroke', '#334155')
                .attr('stroke-opacity', 0.6)
                .attr('stroke-width', d => Math.sqrt(d.value));
            
            const node = svg.append('g')
                .selectAll('circle')
                .data(data.nodes)
                .enter().append('circle')
                .attr('r', d => d.type === 'keyword' ? Math.sqrt(d.value) / 50 : 10)
                .attr('fill', d => d.type === 'keyword' ? '#0891b2' : '#6366f1')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            const label = svg.append('g')
                .selectAll('text')
                .data(data.nodes)
                .enter().append('text')
                .text(d => d.label)
                .attr('font-size', '10px')
                .attr('fill', '#f1f5f9')
                .attr('dx', 12)
                .attr('dy', 4);
            
            node.append('title')
                .text(d => d.label);
            
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
                
                label
                    .attr('x', d => d.x)
                    .attr('y', d => d.y);
            });
            
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
        }

        // Run custom query
        async function runCustomQuery() {
            const query = document.getElementById('queryInput').value;
            const resultsDiv = document.getElementById('queryResults');
            
            if (!query.trim()) {
                resultsDiv.innerHTML = '<p style="color: var(--warning)">Please enter a query</p>';
                return;
            }
            
            resultsDiv.innerHTML = '<div class="loading"><div class="spinner"></div></div>';
            
            try {
                const response = await axios.post(`${API_BASE}/custom-query`, { query });
                
                if (response.data.length === 0) {
                    resultsDiv.innerHTML = '<p>No results found</p>';
                    return;
                }
                
                // Create table from results
                const keys = Object.keys(response.data[0]);
                let html = '<table><thead><tr>';
                keys.forEach(key => {
                    html += `<th>${key}</th>`;
                });
                html += '</tr></thead><tbody>';
                
                response.data.forEach(row => {
                    html += '<tr>';
                    keys.forEach(key => {
                        let value = row[key];
                        if (typeof value === 'object') {
                            value = JSON.stringify(value);
                        }
                        html += `<td>${value || 'null'}</td>`;
                    });
                    html += '</tr>';
                });
                
                html += '</tbody></table>';
                resultsDiv.innerHTML = html;
                
            } catch (error) {
                resultsDiv.innerHTML = `
                    <p style="color: var(--danger)">
                        Error: ${error.response?.data?.error || error.message}
                    </p>
                `;
            }
        }

        // Handle window resize
        window.addEventListener('resize', () => {
            // Resize all charts
            ['marketShareChart', 'intentChart', 'competitorChart', 'landscapeChart',
             'opportunityChart', 'gapChart', 'serpChart', 'clusterChart'].forEach(id => {
                const element = document.getElementById(id);
                if (element) {
                    const chart = echarts.getInstanceByDom(element);
                    if (chart) chart.resize();
                }
            });
            
            // Reload graph if visible
            if (currentSection === 'visualization') {
                loadGraphVisualization();
            }
        });

        // Initialize on load
        document.addEventListener('DOMContentLoaded', () => {
            loadSectionData('overview');
        });
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5001
    
    print("=" * 60)
    print("🚀 Neo4j SEO Analysis Dashboard Server")
    print("=" * 60)
    print(f"📊 Neo4j URI: {NEO4J_URI}")
    print(f"🌐 Dashboard URL: http://localhost:{port}")
    print("=" * 60)
    print("\nAPI Endpoints:")
    print("  • /api/overview - Database statistics")
    print("  • /api/competitors - Competitor analysis")
    print("  • /api/keyword-opportunities - High-value keywords")
    print("  • /api/competitive-gaps - Content gaps")
    print("  • /api/market-share - Market share analysis")
    print("  • /api/keyword-clusters - Keyword clustering")
    print("  • /api/intent-analysis - Search intent")
    print("  • /api/serp-features - SERP features")
    print("  • /api/graph-visualization - Graph data")
    print("  • /api/custom-query - Custom Cypher queries")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=port)
