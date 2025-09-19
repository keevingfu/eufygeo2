#\!/usr/bin/env python3
import sys
import os
import subprocess
import time

def main():
    try:
        print("🚀 启动四大触点监控系统...")
        
        # 检查依赖
        try:
            import flask
            import flask_socketio
            print("✅ Flask依赖正常")
        except ImportError as e:
            print(f"❌ 依赖缺失: {e}")
            sys.exit(1)
        
        # 导入监控系统
        sys.path.append(os.getcwd())
        exec(open('integrated-monitoring-system.py').read())
        
        # 初始化监控系统
        monitoring_system = IntegratedMonitoringSystem()
        print("✅ 监控系统初始化成功")
        
        # 启动服务器
        print("🌐 启动监控系统服务器 (端口5002)...")
        monitoring_system.run_server(host='127.0.0.1', port=5002, debug=False)
        
    except Exception as e:
        print(f"❌ 监控系统启动失败: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
