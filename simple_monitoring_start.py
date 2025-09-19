#!/usr/bin/env python3
"""
简化版监控系统启动器
Simplified Monitoring System Launcher
"""

import sys
import os
from flask import Flask, jsonify
from flask_socketio import SocketIO
import json
import time
from datetime import datetime

# 添加当前目录到Python路径
sys.path.insert(0, os.getcwd())

app = Flask(__name__)
app.config['SECRET_KEY'] = 'eufygeo2-monitoring-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

@app.route('/')
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>EufyGeo2 四大触点监控中心</title>
        <meta charset="UTF-8">
        <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
        <style>
            body { 
                font-family: -apple-system, BlinkMacSystemFont, sans-serif; 
                margin: 0; 
                padding: 20px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
            }
            .header { text-align: center; margin-bottom: 30px; }
            .metrics-grid { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                gap: 20px; 
                margin-bottom: 30px; 
            }
            .metric-card { 
                background: rgba(255,255,255,0.1); 
                padding: 20px; 
                border-radius: 10px; 
                text-align: center; 
                backdrop-filter: blur(10px);
            }
            .metric-value { font-size: 2em; font-weight: bold; margin: 10px 0; }
            .metric-label { opacity: 0.8; }
            .status-online { color: #4CAF50; }
            .status-warning { color: #FF9800; }
            .status-critical { color: #F44336; }
            .charts { 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); 
                gap: 20px; 
            }
            .chart { 
                background: rgba(255,255,255,0.95); 
                padding: 20px; 
                border-radius: 10px; 
                color: #333;
                min-height: 300px;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🎯 EufyGeo2 四大触点监控中心</h1>
            <p>统一GEO指挥中心 - Unified GEO Command Center</p>
        </div>
        
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-value status-online" id="geo-score">78.5</div>
                <div class="metric-label">总体GEO得分</div>
            </div>
            <div class="metric-card">
                <div class="metric-value status-online" id="citation-rate">22.3%</div>
                <div class="metric-label">AI引用率</div>
            </div>
            <div class="metric-card">
                <div class="metric-value status-online" id="traffic-growth">+28.7%</div>
                <div class="metric-label">流量增长</div>
            </div>
            <div class="metric-card">
                <div class="metric-value status-warning" id="system-health">运行中</div>
                <div class="metric-label">系统状态</div>
            </div>
        </div>
        
        <div class="charts">
            <div class="chart">
                <h3>四大触点实时表现</h3>
                <div id="touchpoints-chart" style="width: 100%; height: 250px;"></div>
            </div>
            <div class="chart">
                <h3>GEO优化趋势</h3>
                <div id="trend-chart" style="width: 100%; height: 250px;"></div>
            </div>
        </div>
        
        <script>
            // 初始化图表
            if (typeof echarts !== 'undefined') {
                // 四大触点表现
                const touchpointsChart = echarts.init(document.getElementById('touchpoints-chart'));
                const touchpointsOption = {
                    tooltip: { trigger: 'item' },
                    series: [{
                        name: '触点表现',
                        type: 'pie',
                        radius: '60%',
                        data: [
                            { value: 85, name: 'AI搜索优化' },
                            { value: 78, name: '社交内容优化' },
                            { value: 72, name: '电商AI优化' },
                            { value: 68, name: '私域客服优化' }
                        ]
                    }]
                };
                touchpointsChart.setOption(touchpointsOption);
                
                // GEO优化趋势
                const trendChart = echarts.init(document.getElementById('trend-chart'));
                const trendOption = {
                    tooltip: { trigger: 'axis' },
                    xAxis: {
                        type: 'category',
                        data: ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
                    },
                    yAxis: { type: 'value' },
                    series: [{
                        name: 'GEO得分',
                        type: 'line',
                        data: [72, 75, 78, 80, 76, 82, 78.5],
                        smooth: true
                    }]
                };
                trendChart.setOption(trendOption);
                
                // 响应式调整
                window.addEventListener('resize', () => {
                    touchpointsChart.resize();
                    trendChart.resize();
                });
            }
            
            // 模拟数据更新
            setInterval(() => {
                document.getElementById('geo-score').textContent = (75 + Math.random() * 8).toFixed(1);
                document.getElementById('citation-rate').textContent = (20 + Math.random() * 5).toFixed(1) + '%';
                document.getElementById('traffic-growth').textContent = '+' + (25 + Math.random() * 8).toFixed(1) + '%';
            }, 5000);
        </script>
    </body>
    </html>
    """

@app.route('/api/status')
def api_status():
    return jsonify({
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "touchpoints": {
            "ai_search": {"score": 85, "status": "online"},
            "social_content": {"score": 78, "status": "online"}, 
            "ecommerce_ai": {"score": 72, "status": "online"},
            "private_domain": {"score": 68, "status": "online"}
        },
        "overall_geo_score": 78.5,
        "ai_citation_rate": 22.3
    })

@app.route('/api/metrics')
def api_metrics():
    return jsonify({
        "geo_score": round(75 + (time.time() % 10), 1),
        "citation_rate": round(20 + (time.time() % 5), 1),
        "traffic_growth": round(25 + (time.time() % 8), 1),
        "system_health": "healthy"
    })

if __name__ == '__main__':
    print("🚀 启动EufyGeo2四大触点监控系统...")
    print("📊 监控仪表板: http://localhost:5002")
    print("🔗 API状态: http://localhost:5002/api/status")
    socketio.run(app, host='127.0.0.1', port=5002, debug=False, allow_unsafe_werkzeug=True)