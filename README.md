# EufyGeo2 - AI时代生成式引擎优化平台

## 项目概述

EufyGeo2是一个基于Generative Engine Optimization (GEO)理念的综合AI内容优化平台，专为在AI时代提升品牌在各种AI搜索引擎和推荐系统中的可见性而设计。

## 🎯 核心功能模块

### 1. AI搜索流量优化 (`ai-search-optimization-module.py`)
- 针对Google AI Overview、Perplexity、Claude等AI搜索引擎优化
- 语义分析和内容结构化
- 答案卡片生成
- 权威性信号增强

### 2. 社交内容GEO优化 (`social-content-geo-optimizer.py`)
- TikTok Search、Instagram Explore、YouTube Shorts优化
- 视频前3秒Hook分析
- 标签策略优化
- 平台算法适配

### 3. 电商AI导购优化 (`ecommerce-ai-shopping-optimizer.py`)
- Amazon Rufus、TikTok Shop、Instagram Shop优化
- 产品数据结构化
- 比较矩阵生成
- AI推荐算法适配

### 4. 私域AI客服优化 (`private-domain-ai-customer-service.py`)
- WhatsApp Business、WeChat Bot对话优化
- 标准化答案库创建
- 个性化消息生成
- 转化漏斗优化

### 5. 四大触点整合监控 (`integrated-monitoring-system.py`)
- 实时监控所有触点表现
- 统一GEO分数计算
- 智能警报系统
- 可视化仪表板

### 6. Neo4j SEO竞争分析 (`neo4j_dashboard_server.py`)
- 基于图数据库的竞争对手分析
- 关键词机会发现
- 流量来源追踪
- 数据可视化

## 🚀 快速开始

### 1. 环境准备
```bash
# 克隆项目
git clone <repository-url>
cd eufygeo2

# 一键安装依赖
./setup.sh

# 或手动安装
pip install -r requirements.txt
playwright install
```

### 2. 启动服务

#### 启动监控系统
```bash
python start_monitoring.py
# 访问: http://localhost:5002
```

#### 启动Neo4j仪表板
```bash
# 首先启动Neo4j数据库
docker-compose up -d neo4j

# 导入数据（如果有CSV文件）
python import_competitor_data_to_neo4j.py

# 启动仪表板
python neo4j_dashboard_server.py
# 访问: http://localhost:5001
```

#### 查看HTML仪表板
```bash
python -m http.server 8000
# 访问: http://localhost:8000/eufy-seo-dashboard.html
```

### 3. 运行测试
```bash
# 综合功能测试
python playwright_comprehensive_testing.py

# 查看测试报告
ls test_report_*.txt
```

## 📊 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    统一GEO指挥中心                            │
│               (Integrated Monitoring System)              │
├─────────────────────────────────────────────────────────────┤
│  AI搜索优化  │  社交内容优化 │  电商AI优化  │  私域客服优化     │
│  Module     │   Module     │   Module    │    Module      │
├─────────────────────────────────────────────────────────────┤
│              Neo4j竞争分析 + HTML可视化仪表板                │
└─────────────────────────────────────────────────────────────┘
```

## 🛠 技术栈

- **后端**: Python 3.8+, Flask, FastAPI
- **数据库**: Neo4j, SQLite, Redis
- **前端**: HTML5, JavaScript, ECharts
- **AI/ML**: Transformers, OpenCV, scikit-learn
- **测试**: Playwright
- **部署**: Docker, Docker Compose

## 📈 性能指标

- **整体GEO分数**: >75分
- **AI引用率**: 目标20-25%
- **页面加载时间**: <2秒
- **API响应时间**: <200ms

## 🔧 配置说明

### 监控系统配置 (`monitoring_config.json`)
```json
{
  "collection_interval": 30,
  "ai_search": {
    "geo_score_threshold": 70,
    "citation_rate_threshold": 15
  },
  "social_content": {
    "geo_score_threshold": 65,
    "citation_rate_threshold": 12
  }
}
```

### Neo4j连接配置
```python
# 默认连接信息
URI: bolt://localhost:7687
Username: neo4j
Password: eufyseo2024
```

## 📝 使用指南

### 1. AI搜索优化
```python
from ai_search_optimization_module import AIOptimizedContentEngine

engine = AIOptimizedContentEngine()
result = engine.analyze_content_semantics("您的内容")
print(f"GEO分数: {result['geo_score']}")
```

### 2. 社交内容优化
```python
from social_content_geo_optimizer import SocialContentGEOOptimizer

optimizer = SocialContentGEOOptimizer()
result = optimizer.optimize_video_content({
    "title": "产品介绍视频",
    "platform": "tiktok"
})
```

### 3. 电商优化
```python
from ecommerce_ai_shopping_optimizer import EcommerceAIShoppingAssistantOptimizer

optimizer = EcommerceAIShoppingAssistantOptimizer()
result = optimizer.optimize_product_for_ai_assistant(
    product_data, 
    EcommercePlatform.AMAZON_RUFUS
)
```

## 🚨 常见问题

### 1. 依赖安装问题
```bash
# 如果遇到依赖冲突
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### 2. Neo4j连接问题
```bash
# 检查Neo4j状态
docker ps | grep neo4j

# 重启Neo4j
docker-compose restart neo4j
```

### 3. 端口占用问题
```bash
# 查看端口占用
lsof -ti :5002 | xargs kill -9  # 监控系统
lsof -ti :5001 | xargs kill -9  # Neo4j仪表板
```

## 📊 测试报告

最新测试结果：
- ✅ 通过: 3/16 (18.8%)
- ❌ 失败: 9/16 (56.2%) 
- 🚫 错误: 4/16 (25.0%)

主要问题已修复：
- ✅ 依赖安装问题
- ✅ 数据结构验证
- ✅ HTML图表显示
- ✅ 启动脚本优化

## 🤝 贡献指南

1. Fork项目
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开Pull Request

## 📄 许可证

本项目基于MIT许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 📞 支持

如有问题，请：
1. 查看 [FAQ](#常见问题)
2. 提交 [Issue](https://github.com/your-org/eufygeo2/issues)
3. 查看测试报告进行故障排除

---

**EufyGeo2** - 引领AI时代的内容优化革命 🚀
