# EufyGeo2 项目完整安装指南
## Complete Installation Guide for EufyGeo2 Project

### 🎯 项目概述 Project Overview
EufyGeo2是基于GEO(生成式引擎优化)理念的AI内容优化平台，包含四大核心触点：
- AI搜索流量优化 (AI Search Optimization) 
- 社交内容GEO优化 (Social Content GEO)
- 电商AI导购优化 (E-commerce AI Shopping)
- 私域AI客服优化 (Private Domain AI Service)

---

## 🚀 完整安装步骤 Complete Installation Steps

### 第一步：环境准备 Environment Setup

#### 1.1 Python环境
```bash
# 检查Python版本 (需要3.8+)
python3 --version

# 创建虚拟环境 (推荐)
python3 -m venv eufygeo2_env
source eufygeo2_env/bin/activate  # macOS/Linux
# 或 eufygeo2_env\Scripts\activate  # Windows
```

#### 1.2 依赖安装
```bash
# 基础依赖
pip install -r requirements_complete.txt

# 如果某些包安装失败，分步安装：
pip install flask flask-socketio requests numpy pandas scipy
pip install scikit-learn transformers torch textstat
pip install spacy nltk librosa opencv-python
pip install beautifulsoup4 lxml openai
pip install redis neo4j playwright python-dotenv pytz
```

#### 1.3 额外配置
```bash
# 安装spaCy语言模型
python -m spacy download en_core_web_sm
python -m spacy download zh_core_web_sm

# 安装Playwright浏览器
playwright install

# 下载NLTK数据
python -c "import nltk; nltk.download('punkt'); nltk.download('stopwords')"
```

### 第二步：数据库配置 Database Setup

#### 2.1 Redis安装启动
```bash
# macOS
brew install redis
brew services start redis

# Ubuntu/Debian
sudo apt-get install redis-server
sudo systemctl start redis

# 验证Redis连接
redis-cli ping
```

#### 2.2 Neo4j安装启动  
```bash
# 使用Docker (推荐)
docker-compose up -d neo4j

# 或手动启动Docker
docker run -d \
    --name eufy-seo-neo4j \
    -p 7474:7474 -p 7687:7687 \
    -e NEO4J_AUTH=neo4j/eufyseo2024 \
    -e NEO4J_PLUGINS='["apoc"]' \
    neo4j:5.13.0

# 验证Neo4j连接
curl http://localhost:7474
```

### 第三步：模块测试 Module Testing

#### 3.1 基础功能测试
```bash
# 测试E-commerce优化器 (已修复)
python3 -c "
exec(open('ecommerce-ai-shopping-optimizer.py').read())
optimizer = EcommerceAIShoppingAssistantOptimizer()
result = optimizer.optimize_product_for_ai_assistant(199.99, EcommercePlatform.AMAZON_RUFUS)
print('✅ E-commerce优化器运行正常')
print('AI就绪度得分:', result.ai_readiness_score)
"

# 测试私域AI客服
python3 -c "
exec(open('private-domain-ai-customer-service.py').read())
optimizer = PrivateDomainAICustomerServiceOptimizer()
print('✅ 私域AI客服系统运行正常')
"
```

#### 3.2 完整功能验证
```bash
# 运行综合测试
python3 playwright_comprehensive_testing.py

# 查看测试报告
ls -la test_report_*.txt
```

### 第四步：服务启动 Service Startup

#### 4.1 监控系统
```bash
# 启动四大触点监控系统
python3 start_monitoring.py
# 访问: http://localhost:5002
```

#### 4.2 Neo4j仪表板
```bash
# 启动Neo4j仪表板服务
python3 neo4j_dashboard_server.py
# 访问: http://localhost:5001

# 如果有CSV数据，先导入
python3 import_competitor_data_to_neo4j.py
```

#### 4.3 HTML仪表板
```bash
# 启动简单HTTP服务器
python3 -m http.server 8000
# 访问各个仪表板:
# - http://localhost:8000/eufy-seo-dashboard.html
# - http://localhost:8000/neo4j-seo-dashboard.html  
# - http://localhost:8000/eufy-seo-battle-dashboard.html
# - http://localhost:8000/eufy-geo-content-strategy.html
```

---

## 🔧 常见问题解决 Troubleshooting

### 问题1：依赖安装失败
```bash
# 解决方案1：更新pip
pip install --upgrade pip

# 解决方案2：使用conda
conda install -c conda-forge librosa spacy

# 解决方案3：系统包管理器
# macOS: brew install portaudio  # for pyaudio
# Ubuntu: sudo apt-get install portaudio19-dev
```

### 问题2：端口被占用
```bash
# 查看端口占用
lsof -i :5001  # Neo4j仪表板
lsof -i :5002  # 监控系统
lsof -i :8000  # HTML服务器

# 终止占用进程
kill -9 <PID>
```

### 问题3：Neo4j连接失败
```bash
# 检查Docker容器状态
docker ps | grep neo4j

# 查看容器日志
docker logs eufy-seo-neo4j

# 重启Neo4j
docker restart eufy-seo-neo4j
```

### 问题4：模块导入错误
```bash
# 检查Python路径
python3 -c "import sys; print(sys.path)"

# 在当前目录运行
export PYTHONPATH=$PYTHONPATH:$(pwd)
python3 your_script.py
```

---

## 📊 系统监控 System Monitoring

### 性能指标
- **GEO总分**: 目标75+
- **AI引用率**: 目标20-25%
- **页面响应时间**: <2秒
- **API响应时间**: <200ms

### 监控检查清单
- [ ] Redis服务运行状态
- [ ] Neo4j数据库连接
- [ ] 各模块导入正常
- [ ] HTML图表显示正常
- [ ] API接口响应正常

---

## 📞 支持联系 Support

如遇问题，请：
1. 检查本安装指南
2. 查看测试报告定位问题
3. 查看相关日志文件
4. 提交详细的错误信息

---

## 📈 后续优化 Future Optimization

1. **性能优化**: 缓存机制、数据库索引优化
2. **UI改进**: 响应式设计、交互优化  
3. **功能扩展**: 更多AI平台支持、高级分析功能
4. **自动化**: CI/CD流程、自动测试部署

---

**EufyGeo2项目 - 引领AI时代的内容优化革命** 🚀
