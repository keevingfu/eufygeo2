#!/bin/bash

# Eufy SEO Dashboard Runner Script
# This script sets up and runs the Eufy SEO Dashboard

echo "=================================================="
echo "🚀 Eufy SEO Dashboard Setup & Runner"
echo "=================================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install required packages
echo "📚 Installing required packages..."
pip install --quiet --upgrade pip
pip install --quiet flask flask-cors pandas

# Check if database exists
DB_PATH="/Users/cavin/Desktop/dev/eufygeo2/eufygeo2.db"
if [ ! -f "$DB_PATH" ]; then
    echo "⚠️  Warning: Database not found at $DB_PATH"
    echo "   Please ensure the database exists before running the dashboard."
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Save the dashboard server script
echo "💾 Creating dashboard server script..."
cat > eufy_dashboard_server.py << 'EOF'
#!/usr/bin/env python3
"""
Eufy SEO Dashboard Server
Serves real-time data from SQLite database to web dashboard
"""

import sqlite3
import json
from flask import Flask, render_template_string, jsonify
from flask_cors import CORS
import pandas as pd
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Database configuration
DB_PATH = "/Users/cavin/Desktop/dev/eufygeo2/eufygeo2.db"

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def execute_query(query):
    """Execute query and return results as list of dicts"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(query)
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

# API Endpoints for dashboard data
@app.route('/api/metrics')
def get_metrics():
    """Get key metrics for dashboard"""
    metrics = {}
    
    # Total Keywords
    result = execute_query("SELECT COUNT(*) as count FROM eufy_organic_positions")
    metrics['total_keywords'] = result[0]['count']
    
    # Top 10 Count
    result = execute_query("SELECT COUNT(*) as count FROM eufy_organic_positions WHERE position <= 10")
    metrics['top10_count'] = result[0]['count']
    
    # Total Traffic
    result = execute_query("SELECT SUM(traffic) as total FROM eufy_organic_positions")
    metrics['total_traffic'] = result[0]['total'] or 0
    
    # Traffic Value
    result = execute_query("SELECT SUM(traffic_cost) as total FROM eufy_organic_positions")
    metrics['traffic_value'] = result[0]['total'] or 0
    
    # Average Position
    result = execute_query("SELECT AVG(position) as avg FROM eufy_organic_positions")
    metrics['avg_position'] = round(result[0]['avg'], 1) if result[0]['avg'] else 0
    
    # Unique URLs
    result = execute_query("SELECT COUNT(DISTINCT url) as count FROM eufy_organic_positions")
    metrics['unique_urls'] = result[0]['count']
    
    return jsonify(metrics)

@app.route('/api/ranking-distribution')
def get_ranking_distribution():
    """Get ranking distribution data"""
    query = """
    SELECT 
        CASE 
            WHEN position <= 3 THEN 'Top 3'
            WHEN position <= 10 THEN 'Top 4-10'
            WHEN position <= 20 THEN 'Top 11-20'
            WHEN position <= 50 THEN 'Top 21-50'
            ELSE '50+'
        END as tier,
        COUNT(*) as count
    FROM eufy_organic_positions
    GROUP BY tier
    ORDER BY 
        CASE tier
            WHEN 'Top 3' THEN 1
            WHEN 'Top 4-10' THEN 2
            WHEN 'Top 11-20' THEN 3
            WHEN 'Top 21-50' THEN 4
            ELSE 5
        END
    """
    return jsonify(execute_query(query))

@app.route('/api/top-pages')
def get_top_pages():
    """Get top performing pages"""
    query = """
    SELECT 
        SUBSTR(url, INSTR(url, '.com/') + 5, 50) as page,
        SUM(traffic) as total_traffic,
        COUNT(*) as keyword_count,
        AVG(position) as avg_position
    FROM eufy_organic_positions
    GROUP BY url
    ORDER BY total_traffic DESC
    LIMIT 10
    """
    return jsonify(execute_query(query))

@app.route('/api/quick-wins')
def get_quick_wins():
    """Get quick win opportunities"""
    query = """
    SELECT 
        keyword,
        position,
        search_volume,
        traffic,
        keyword_difficulty,
        cpc,
        url
    FROM eufy_organic_positions
    WHERE position BETWEEN 4 AND 10
        AND search_volume >= 1000
    ORDER BY search_volume DESC
    LIMIT 20
    """
    return jsonify(execute_query(query))

@app.route('/api/category-performance')
def get_category_performance():
    """Get product category performance"""
    query = """
    SELECT 
        CASE 
            WHEN LOWER(keyword) LIKE '%camera%' OR LOWER(keyword) LIKE '%cam%' THEN 'Camera'
            WHEN LOWER(keyword) LIKE '%doorbell%' THEN 'Doorbell'
            WHEN LOWER(keyword) LIKE '%vacuum%' OR LOWER(keyword) LIKE '%robovac%' THEN 'Vacuum'
            WHEN LOWER(keyword) LIKE '%lock%' THEN 'Smart Lock'
            WHEN LOWER(keyword) LIKE '%light%' OR LOWER(keyword) LIKE '%bulb%' THEN 'Lighting'
            WHEN LOWER(keyword) LIKE '%security%' THEN 'Security'
            ELSE 'Other'
        END as category,
        COUNT(*) as keyword_count,
        SUM(traffic) as total_traffic,
        AVG(position) as avg_position
    FROM eufy_organic_positions
    GROUP BY category
    ORDER BY total_traffic DESC
    """
    return jsonify(execute_query(query))

@app.route('/api/intent-distribution')
def get_intent_distribution():
    """Get search intent distribution"""
    query = """
    SELECT 
        keyword_intents as intent,
        COUNT(*) as count,
        SUM(traffic) as total_traffic
    FROM eufy_organic_positions
    WHERE keyword_intents IS NOT NULL AND keyword_intents != ''
    GROUP BY keyword_intents
    ORDER BY count DESC
    LIMIT 10
    """
    return jsonify(execute_query(query))

@app.route('/api/opportunity-matrix')
def get_opportunity_matrix():
    """Get data for opportunity matrix scatter plot"""
    query = """
    SELECT 
        keyword,
        position,
        search_volume,
        traffic,
        keyword_difficulty,
        ROUND(
            CASE 
                WHEN position <= 3 THEN search_volume * 0.3
                WHEN position <= 10 THEN search_volume * 0.15
                ELSE search_volume * 0.05
            END - traffic
        , 0) as traffic_potential
    FROM eufy_organic_positions
    WHERE search_volume > 500 
        AND position <= 50
    ORDER BY traffic_potential DESC
    LIMIT 200
    """
    return jsonify(execute_query(query))

@app.route('/api/difficulty-analysis')
def get_difficulty_analysis():
    """Get keyword difficulty analysis"""
    query = """
    SELECT 
        CASE 
            WHEN keyword_difficulty <= 20 THEN 'Easy (0-20)'
            WHEN keyword_difficulty <= 40 THEN 'Medium (21-40)'
            WHEN keyword_difficulty <= 60 THEN 'Hard (41-60)'
            WHEN keyword_difficulty <= 80 THEN 'Very Hard (61-80)'
            ELSE 'Extreme (81-100)'
        END as difficulty_tier,
        COUNT(*) as count,
        AVG(position) as avg_position,
        SUM(CASE WHEN position <= 10 THEN 1 ELSE 0 END) as top10_count
    FROM eufy_organic_positions
    WHERE keyword_difficulty IS NOT NULL
    GROUP BY difficulty_tier
    ORDER BY difficulty_tier
    """
    return jsonify(execute_query(query))

@app.route('/')
def dashboard():
    """Serve the main dashboard HTML"""
    return render_template_string(DASHBOARD_HTML)

# Dashboard HTML Template (embedded for simplicity)
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Eufy SEO Performance Dashboard</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/echarts/5.4.3/echarts.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/axios/1.5.0/axios.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            --primary: #2563eb;
            --secondary: #7c3aed;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #0f172a;
            --card: #1e293b;
            --text: #f1f5f9;
            --text-secondary: #94a3b8;
            --border: #334155;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, var(--dark) 0%, var(--card) 100%);
            min-height: 100vh;
            color: var(--text);
            padding: 20px;
        }

        .container {
            max-width: 1800px;
            margin: 0 auto;
        }

        .header {
            text-align: center;
            margin-bottom: 40px;
            padding: 30px;
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            border: 1px solid var(--border);
        }

        .header h1 {
            font-size: 2.5em;
            font-weight: 800;
            background: linear-gradient(90deg, var(--primary), var(--secondary), #ec4899);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }

        .metrics {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .metric-card {
            background: var(--card);
            border-radius: 15px;
            padding: 25px;
            border: 1px solid var(--border);
            transition: all 0.3s ease;
        }

        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
        }

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
        }

        .charts {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
            gap: 25px;
            margin-bottom: 30px;
        }

        .chart-card {
            background: var(--card);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid var(--border);
        }

        .chart-card.full-width {
            grid-column: 1 / -1;
        }

        .chart-card h3 {
            font-size: 1.3em;
            margin-bottom: 20px;
            color: var(--text);
        }

        .chart-container {
            width: 100%;
            height: 350px;
        }

        .table-card {
            background: var(--card);
            border-radius: 20px;
            padding: 25px;
            border: 1px solid var(--border);
            overflow-x: auto;
        }

        .table-card h3 {
            font-size: 1.3em;
            margin-bottom: 20px;
            color: var(--text);
        }

        table {
            width: 100%;
            border-collapse: collapse;
        }

        th {
            background: rgba(37, 99, 235, 0.1);
            padding: 12px;
            text-align: left;
            font-weight: 600;
            border-bottom: 2px solid var(--border);
        }

        td {
            padding: 12px;
            border-bottom: 1px solid rgba(51, 65, 85, 0.5);
            color: var(--text-secondary);
        }

        tr:hover {
            background: rgba(37, 99, 235, 0.05);
        }

        .badge {
            display: inline-block;
            padding: 4px 10px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }

        .badge.success { background: rgba(16, 185, 129, 0.2); color: #10b981; }
        .badge.warning { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .badge.info { background: rgba(37, 99, 235, 0.2); color: #2563eb; }

        .loading {
            display: flex;
            justify-content: center;
            align-items: center;
            height: 200px;
        }

        .spinner {
            border: 3px solid rgba(37, 99, 235, 0.2);
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

        @media (max-width: 768px) {
            .charts { grid-template-columns: 1fr; }
            .metrics { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Eufy SEO Performance Dashboard</h1>
            <p>Real-time Organic Search Analytics from SQLite Database</p>
        </div>

        <div class="metrics" id="metricsContainer">
            <div class="metric-card">
                <div class="label">Total Keywords</div>
                <div class="value" id="totalKeywords">-</div>
                <div class="change">Loading...</div>
            </div>
            <div class="metric-card">
                <div class="label">Top 10 Rankings</div>
                <div class="value" id="top10Count">-</div>
                <div class="change">Loading...</div>
            </div>
            <div class="metric-card">
                <div class="label">Total Traffic</div>
                <div class="value" id="totalTraffic">-</div>
                <div class="change">Loading...</div>
            </div>
            <div class="metric-card">
                <div class="label">Traffic Value</div>
                <div class="value" id="trafficValue">-</div>
                <div class="change">Loading...</div>
            </div>
            <div class="metric-card">
                <div class="label">Avg. Position</div>
                <div class="value" id="avgPosition">-</div>
                <div class="change">Loading...</div>
            </div>
            <div class="metric-card">
                <div class="label">Unique URLs</div>
                <div class="value" id="uniqueUrls">-</div>
                <div class="change">Loading...</div>
            </div>
        </div>

        <div class="charts">
            <div class="chart-card">
                <h3>Ranking Distribution</h3>
                <div id="rankingChart" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <h3>Top Performing Pages</h3>
                <div id="topPagesChart" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <h3>Product Categories</h3>
                <div id="categoryChart" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <h3>Keyword Difficulty</h3>
                <div id="difficultyChart" class="chart-container"></div>
            </div>
            <div class="chart-card full-width">
                <h3>Traffic Opportunity Matrix</h3>
                <div id="opportunityChart" class="chart-container"></div>
            </div>
            <div class="chart-card">
                <h3>Search Intent Distribution</h3>
                <div id="intentChart" class="chart-container"></div>
            </div>
        </div>

        <div class="table-card">
            <h3>Quick Win Opportunities (Position 4-10)</h3>
            <table id="quickWinsTable">
                <thead>
                    <tr>
                        <th>Keyword</th>
                        <th>Position</th>
                        <th>Search Volume</th>
                        <th>Traffic</th>
                        <th>Difficulty</th>
                        <th>CPC</th>
                    </tr>
                </thead>
                <tbody>
                    <tr><td colspan="6" class="loading"><div class="spinner"></div></td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        const API_BASE = 'http://localhost:5000/api';
        const chartTheme = {
            color: ['#2563eb', '#7c3aed', '#10b981', '#f59e0b', '#ef4444', '#ec4899'],
            backgroundColor: 'transparent',
            textStyle: { color: '#f1f5f9' },
            grid: { left: '3%', right: '4%', bottom: '3%', containLabel: true }
        };

        // Load metrics
        async function loadMetrics() {
            try {
                const response = await axios.get(`${API_BASE}/metrics`);
                const data = response.data;
                
                document.getElementById('totalKeywords').textContent = data.total_keywords.toLocaleString();
                document.getElementById('top10Count').textContent = data.top10_count.toLocaleString();
                document.getElementById('totalTraffic').textContent = (data.total_traffic / 1000).toFixed(1) + 'K';
                document.getElementById('trafficValue').textContent = '$' + (data.traffic_value / 1000).toFixed(1) + 'K';
                document.getElementById('avgPosition').textContent = data.avg_position;
                document.getElementById('uniqueUrls').textContent = data.unique_urls.toLocaleString();
                
                // Update change indicators
                document.querySelectorAll('.change').forEach(el => {
                    el.textContent = '✓ Live Data';
                    el.style.color = '#10b981';
                });
            } catch (error) {
                console.error('Error loading metrics:', error);
            }
        }

        // Load ranking distribution chart
        async function loadRankingChart() {
            try {
                const response = await axios.get(`${API_BASE}/ranking-distribution`);
                const data = response.data;
                
                const chart = echarts.init(document.getElementById('rankingChart'));
                const option = {
                    ...chartTheme,
                    tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
                    series: [{
                        type: 'pie',
                        radius: ['40%', '70%'],
                        data: data.map(item => ({
                            value: item.count,
                            name: item.tier,
                            itemStyle: { borderRadius: 10 }
                        })),
                        label: { show: true, formatter: '{b}\\n{d}%' }
                    }]
                };
                chart.setOption(option);
            } catch (error) {
                console.error('Error loading ranking chart:', error);
            }
        }

        // Load top pages chart
        async function loadTopPagesChart() {
            try {
                const response = await axios.get(`${API_BASE}/top-pages`);
                const data = response.data.slice(0, 7);
                
                const chart = echarts.init(document.getElementById('topPagesChart'));
                const option = {
                    ...chartTheme,
                    tooltip: { trigger: 'axis' },
                    xAxis: { type: 'value', name: 'Traffic' },
                    yAxis: {
                        type: 'category',
                        data: data.map(item => item.page || 'Homepage').reverse()
                    },
                    series: [{
                        type: 'bar',
                        data: data.map(item => item.total_traffic).reverse(),
                        itemStyle: {
                            color: new echarts.graphic.LinearGradient(0, 0, 1, 0, [
                                { offset: 0, color: '#7c3aed' },
                                { offset: 1, color: '#2563eb' }
                            ]),
                            borderRadius: [0, 8, 8, 0]
                        }
                    }]
                };
                chart.setOption(option);
            } catch (error) {
                console.error('Error loading top pages chart:', error);
            }
        }

        // Load category chart
        async function loadCategoryChart() {
            try {
                const response = await axios.get(`${API_BASE}/category-performance`);
                const data = response.data;
                
                const chart = echarts.init(document.getElementById('categoryChart'));
                const option = {
                    ...chartTheme,
                    tooltip: { trigger: 'axis' },
                    legend: { data: ['Keywords', 'Traffic'], textStyle: { color: '#94a3b8' } },
                    xAxis: {
                        type: 'category',
                        data: data.map(item => item.category)
                    },
                    yAxis: [
                        { type: 'value', name: 'Keywords' },
                        { type: 'value', name: 'Traffic' }
                    ],
                    series: [
                        {
                            name: 'Keywords',
                            type: 'bar',
                            data: data.map(item => item.keyword_count),
                            itemStyle: { color: '#2563eb', borderRadius: [8, 8, 0, 0] }
                        },
                        {
                            name: 'Traffic',
                            type: 'line',
                            yAxisIndex: 1,
                            data: data.map(item => item.total_traffic),
                            smooth: true,
                            itemStyle: { color: '#10b981' }
                        }
                    ]
                };
                chart.setOption(option);
            } catch (error) {
                console.error('Error loading category chart:', error);
            }
        }

        // Load difficulty chart
        async function loadDifficultyChart() {
            try {
                const response = await axios.get(`${API_BASE}/difficulty-analysis`);
                const data = response.data;
                
                const chart = echarts.init(document.getElementById('difficultyChart'));
                const option = {
                    ...chartTheme,
                    tooltip: { trigger: 'axis' },
                    xAxis: {
                        type: 'category',
                        data: data.map(item => item.difficulty_tier.split(' ')[0])
                    },
                    yAxis: { type: 'value', name: 'Keywords' },
                    series: [{
                        type: 'bar',
                        data: data.map(item => item.count),
                        itemStyle: {
                            color: function(params) {
                                const colors = ['#10b981', '#2563eb', '#f59e0b', '#ef4444', '#dc2626'];
                                return colors[params.dataIndex];
                            },
                            borderRadius: [8, 8, 0, 0]
                        }
                    }]
                };
                chart.setOption(option);
            } catch (error) {
                console.error('Error loading difficulty chart:', error);
            }
        }

        // Load opportunity matrix
        async function loadOpportunityChart() {
            try {
                const response = await axios.get(`${API_BASE}/opportunity-matrix`);
                const data = response.data;
                
                const chart = echarts.init(document.getElementById('opportunityChart'));
                const option = {
                    ...chartTheme,
                    tooltip: {
                        trigger: 'item',
                        formatter: function(params) {
                            const d = params.data;
                            return `${d[3]}<br/>Position: ${d[0]}<br/>Volume: ${d[1]}<br/>Traffic: ${d[2]}`;
                        }
                    },
                    xAxis: { type: 'value', name: 'Position', min: 1, max: 50 },
                    yAxis: { type: 'value', name: 'Search Volume' },
                    series: [{
                        type: 'scatter',
                        symbolSize: function(data) {
                            return Math.sqrt(data[1]) / 3;
                        },
                        data: data.map(item => [
                            item.position,
                            item.search_volume,
                            item.traffic,
                            item.keyword
                        ]),
                        itemStyle: {
                            color: function(params) {
                                const pos = params.value[0];
                                if (pos <= 3) return '#10b981';
                                if (pos <= 10) return '#2563eb';
                                if (pos <= 20) return '#7c3aed';
                                return '#f59e0b';
                            },
                            opacity: 0.7
                        }
                    }]
                };
                chart.setOption(option);
            } catch (error) {
                console.error('Error loading opportunity chart:', error);
            }
        }

        // Load intent chart
        async function loadIntentChart() {
            try {
                const response = await axios.get(`${API_BASE}/intent-distribution`);
                const data = response.data;
                
                const chart = echarts.init(document.getElementById('intentChart'));
                const option = {
                    ...chartTheme,
                    tooltip: { trigger: 'item', formatter: '{b}: {c}' },
                    series: [{
                        type: 'pie',
                        radius: '60%',
                        data: data.map(item => ({
                            value: item.count,
                            name: item.intent || 'Unknown'
                        })),
                        itemStyle: { borderRadius: 5 }
                    }]
                };
                chart.setOption(option);
            } catch (error) {
                console.error('Error loading intent chart:', error);
            }
        }

        // Load quick wins table
        async function loadQuickWinsTable() {
            try {
                const response = await axios.get(`${API_BASE}/quick-wins`);
                const data = response.data;
                
                const tbody = document.querySelector('#quickWinsTable tbody');
                tbody.innerHTML = '';
                
                data.forEach(item => {
                    const tr = document.createElement('tr');
                    tr.innerHTML = `
                        <td style="font-weight: 600; color: #f1f5f9">${item.keyword}</td>
                        <td><span class="badge info">#${item.position}</span></td>
                        <td>${item.search_volume.toLocaleString()}</td>
                        <td>${item.traffic.toLocaleString()}</td>
                        <td>${item.keyword_difficulty || 'N/A'}</td>
                        <td>$${item.cpc ? item.cpc.toFixed(2) : '0.00'}</td>
                    `;
                    tbody.appendChild(tr);
                });
            } catch (error) {
                console.error('Error loading quick wins table:', error);
            }
        }

        // Initialize dashboard
        async function initDashboard() {
            await loadMetrics();
            await loadRankingChart();
            await loadTopPagesChart();
            await loadCategoryChart();
            await loadDifficultyChart();
            await loadOpportunityChart();
            await loadIntentChart();
            await loadQuickWinsTable();
            
            // Make charts responsive
            window.addEventListener('resize', () => {
                ['rankingChart', 'topPagesChart', 'categoryChart', 'difficultyChart', 
                 'opportunityChart', 'intentChart'].forEach(id => {
                    const chart = echarts.getInstanceByDom(document.getElementById(id));
                    if (chart) chart.resize();
                });
            });
        }

        // Start dashboard
        document.addEventListener('DOMContentLoaded', initDashboard);
    </script>
</body>
</html>
"""

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 Eufy SEO Dashboard Server")
    print("=" * 60)
    print(f"📊 Database: {DB_PATH}")
    print(f"🌐 Dashboard URL: http://localhost:5000")
    print("=" * 60)
    print("\nAPI Endpoints:")
    print("  • /api/metrics - Key performance metrics")
    print("  • /api/ranking-distribution - Ranking tier distribution")
    print("  • /api/top-pages - Top performing pages")
    print("  • /api/quick-wins - Quick win opportunities")
    print("  • /api/category-performance - Product category analysis")
    print("  • /api/intent-distribution - Search intent breakdown")
    print("  • /api/opportunity-matrix - Traffic opportunity data")
    print("  • /api/difficulty-analysis - Keyword difficulty tiers")
    print("\n" + "=" * 60)
    print("Press Ctrl+C to stop the server")
    print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
EOF

# Run the dashboard server
echo "=================================================="
echo "🚀 Starting Eufy SEO Dashboard Server"
echo "=================================================="
echo ""
echo "📊 Database: $DB_PATH"
echo "🌐 Dashboard URL: http://localhost:5000"
echo ""
echo "📱 You can also access from other devices on your network at:"
echo "   http://$(ipconfig getifaddr en0):5000"
echo ""
echo "=================================================="
echo "Press Ctrl+C to stop the server"
echo "=================================================="
echo ""

# Run the Flask server
python3 eufy_dashboard_server.py
