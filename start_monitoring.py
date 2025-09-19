#!/usr/bin/env python3
"""
四大触点监控系统启动脚本
Startup script for integrated monitoring system
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖"""
    try:
        import redis
        import flask_socketio
        import sqlite3
        return True
    except ImportError as e:
        print(f"❌ 缺失依赖: {e}")
        return False

def start_redis_if_needed():
    """如果需要，启动Redis"""
    try:
        import redis
        client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        client.ping()
        print("✅ Redis已运行")
        return True
    except:
        print("⚠️ Redis未运行，请手动启动Redis服务器")
        return False

def main():
    """主函数"""
    print("🚀 启动四大触点监控系统...")
    
    # 检查依赖
    if not check_dependencies():
        print("❌ 请先安装依赖: pip install -r requirements.txt")
        return
    
    # 检查Redis
    if not start_redis_if_needed():
        print("💡 提示: brew install redis && brew services start redis")
    
    # 启动监控系统
    try:
        from integrated_monitoring_system import IntegratedMonitoringSystem
        
        monitoring_system = IntegratedMonitoringSystem()
        monitoring_system.run_server(host='127.0.0.1', port=5002, debug=False)
        
    except ImportError:
        print("❌ 无法导入监控系统模块")
        # 尝试直接运行
        script_path = Path(__file__).parent / "integrated-monitoring-system.py"
        if script_path.exists():
            subprocess.run([sys.executable, str(script_path)])
        else:
            print("❌ 找不到监控系统脚本")

if __name__ == "__main__":
    main()
