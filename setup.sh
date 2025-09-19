#!/bin/bash
# EufyGeo2 项目一键安装脚本

echo "🚀 开始安装EufyGeo2项目依赖..."

# 检查Python版本
python_version=$(python3 --version 2>&1 | cut -d" " -f2 | cut -d"." -f1-2)
echo "Python版本: $python_version"

# 升级pip
echo "📦 升级pip..."
python3 -m pip install --upgrade pip

# 安装Python依赖
echo "📦 安装Python依赖..."
pip3 install -r requirements.txt

# 安装Playwright浏览器
echo "🌐 安装Playwright浏览器..."
playwright install

# 检查Redis安装
if ! command -v redis-server &> /dev/null; then
    echo "⚠️ Redis未安装"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "💡 在macOS上安装Redis: brew install redis"
    elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
        echo "💡 在Ubuntu/Debian上安装Redis: sudo apt-get install redis-server"
    fi
else
    echo "✅ Redis已安装"
fi

# 检查Neo4j
echo "🔍 检查Neo4j..."
if ! command -v docker &> /dev/null; then
    echo "⚠️ Docker未安装，Neo4j需要Docker运行"
    echo "💡 请安装Docker: https://docs.docker.com/get-docker/"
else
    echo "✅ Docker已安装"
    if ! docker ps | grep -q neo4j; then
        echo "🔄 启动Neo4j Docker容器..."
        docker-compose up -d neo4j 2>/dev/null || echo "⚠️ Neo4j容器启动失败，请手动启动"
    else
        echo "✅ Neo4j容器已运行"
    fi
fi

# 创建必要目录
mkdir -p test_screenshots templates logs data

# 设置权限
chmod +x start_monitoring.py
chmod +x setup.sh

echo "✅ 安装完成！"
echo ""
echo "🎯 启动说明："
echo "1. 启动监控系统: python3 start_monitoring.py"
echo "2. 启动Neo4j仪表板: python3 neo4j_dashboard_server.py"
echo "3. 运行测试: python3 playwright_comprehensive_testing.py"
echo ""
echo "🌐 访问地址："
echo "- 监控系统仪表板: http://localhost:5002"
echo "- Neo4j仪表板: http://localhost:5001"
echo "- Neo4j浏览器: http://localhost:7474"
