# Neo4j SEO分析快速查询指南

## 🚀 快速启动

### 1. 启动整个系统
```bash
# 一键启动Dashboard
./launch_dashboard.sh

# 或手动步骤：
docker-compose up -d                    # 启动Neo4j
python3 neo4j_dashboard_server.py       # 启动API服务器
```

### 2. 访问界面
- **Neo4j Browser**: http://localhost:7474
  - 用户名: `neo4j`
  - 密码: `eufyseo2024`
- **分析Dashboard**: http://localhost:5001

## 📊 高价值查询集合

### 🎯 机会发现类

#### 1. 找出高价值低竞争关键词（立即可攻击）
```cypher
MATCH (k:Keyword)
WHERE k.search_volume > 10000 
  AND k.difficulty < 30
  AND NOT EXISTS {
    MATCH (k)-[r:RANKS_FOR]->(u:URL)
    WHERE r.position <= 10
  }
RETURN k.text AS keyword,
       k.search_volume AS volume,
       k.difficulty AS difficulty,
       k.cpc AS cpc,
       k.search_volume * k.cpc AS potential_value
ORDER BY potential_value DESC
LIMIT 50
```

#### 2. 竞争对手覆盖但Eufy缺失的关键词
```cypher
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE r.position <= 20 
  AND k.search_volume > 5000
  AND NOT d.name CONTAINS 'eufy'
WITH k, MIN(r.position) AS best_position, 
     COLLECT(DISTINCT d.name)[0..3] AS top_competitors
RETURN k.text AS keyword,
       k.search_volume AS volume,
       k.difficulty AS difficulty,
       best_position,
       top_competitors,
       k.cpc AS cpc
ORDER BY volume DESC
LIMIT 100
```

### 🏆 竞争分析类

#### 3. 主要竞争对手实力分析
```cypher
MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WITH d.name AS competitor,
     COUNT(DISTINCT k) AS total_keywords,
     COUNT(DISTINCT CASE WHEN r.position <= 3 THEN k END) AS top3,
     COUNT(DISTINCT CASE WHEN r.position <= 10 THEN k END) AS top10,
     SUM(r.traffic) AS total_traffic,
     SUM(r.traffic_cost) AS traffic_value,
     AVG(r.position) AS avg_position
RETURN competitor,
       total_keywords,
       top3,
       top10,
       total_traffic,
       ROUND(traffic_value, 2) AS traffic_value_usd,
       ROUND(avg_position, 2) AS avg_position
ORDER BY total_keywords DESC
LIMIT 20
```

#### 4. 市场份额分析（Top 10位置）
```cypher
MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WHERE r.position <= 10
WITH SUM(k.search_volume) AS total_market
MATCH (d:Domain)<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WHERE r.position <= 10
WITH d.name AS domain,
     SUM(k.search_volume) AS domain_volume,
     total_market
RETURN domain,
       domain_volume,
       ROUND(100.0 * domain_volume / total_market, 2) AS market_share_percent
ORDER BY market_share_percent DESC
LIMIT 15
```

### 📈 内容策略类

#### 5. 关键词集群分析（找出内容枢纽）
```cypher
MATCH (u:URL)<-[:RANKS_FOR]-(k:Keyword)
WITH u, 
     COUNT(k) AS keyword_count,
     SUM(k.search_volume) AS total_volume,
     COLLECT(k.text)[0..10] AS sample_keywords
WHERE keyword_count >= 10
RETURN u.address AS url,
       keyword_count,
       total_volume,
       sample_keywords
ORDER BY total_volume DESC
LIMIT 30
```

#### 6. 意图分析与内容优化
```cypher
MATCH (i:Intent)<-[:HAS_INTENT]-(k:Keyword)
WITH i.type AS intent,
     COUNT(k) AS keyword_count,
     SUM(k.search_volume) AS total_volume,
     AVG(k.difficulty) AS avg_difficulty,
     SUM(k.search_volume * k.cpc) AS total_value
RETURN intent,
       keyword_count,
       total_volume,
       ROUND(avg_difficulty, 2) AS avg_difficulty,
       ROUND(total_value, 2) AS market_value_usd
ORDER BY total_value DESC
```

### 🔥 竞争激烈区域

#### 7. 多方竞争的高价值关键词
```cypher
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE r.position <= 20
WITH k, COUNT(DISTINCT d) AS competitor_count, 
     COLLECT(DISTINCT d.name) AS competitors
WHERE competitor_count >= 5 
  AND k.search_volume > 5000
RETURN k.text AS keyword,
       k.search_volume AS volume,
       k.difficulty AS difficulty,
       competitor_count,
       competitors[0..5] AS top_competitors
ORDER BY volume DESC
LIMIT 50
```

### 📊 SERP特性分析

#### 8. SERP特性机会
```cypher
MATCH (s:SERPFeature)<-[:HAS_SERP_FEATURE]-(k:Keyword)
WITH s.name AS feature,
     COUNT(k) AS keyword_count,
     SUM(k.search_volume) AS total_volume,
     AVG(k.difficulty) AS avg_difficulty
WHERE keyword_count > 50
RETURN feature,
       keyword_count,
       total_volume,
       ROUND(avg_difficulty, 2) AS avg_difficulty
ORDER BY total_volume DESC
```

### 🎯 快速赢取机会

#### 9. Position 4-10 提升机会
```cypher
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE r.position BETWEEN 4 AND 10
  AND k.search_volume > 5000
  AND d.name CONTAINS 'eufy'
RETURN k.text AS keyword,
       r.position AS current_position,
       k.search_volume AS volume,
       k.difficulty AS difficulty,
       r.traffic AS current_traffic,
       ROUND(k.search_volume * 0.3 - r.traffic, 0) AS traffic_potential
ORDER BY traffic_potential DESC
LIMIT 50
```

### 📉 风险监控

#### 10. 排名大幅下降警报
```cypher
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE r.previous_position > 0
  AND r.position - r.previous_position > 10
  AND k.search_volume > 1000
RETURN k.text AS keyword,
       d.name AS domain,
       r.previous_position AS was,
       r.position AS now,
       r.position - r.previous_position AS drop,
       k.search_volume AS volume
ORDER BY volume DESC
LIMIT 50
```

## 🔧 实用工具查询

### 数据库统计
```cypher
// 节点统计
MATCH (n)
RETURN labels(n)[0] AS type, COUNT(n) AS count
ORDER BY count DESC;

// 关系统计
MATCH ()-[r]->()
RETURN type(r) AS relationship, COUNT(r) AS count;
```

### 数据质量检查
```cypher
// 检查缺失数据
MATCH (k:Keyword)
WHERE k.search_volume IS NULL 
   OR k.difficulty IS NULL
RETURN COUNT(k) AS missing_data_count;
```

### 导出关键数据
```cypher
// 导出高价值关键词到CSV格式
MATCH (k:Keyword)
WHERE k.search_volume > 10000
RETURN k.text AS keyword,
       k.search_volume AS volume,
       k.difficulty AS difficulty,
       k.cpc AS cpc
ORDER BY volume DESC
LIMIT 1000
```

## 💡 高级分析查询

### 竞争对手内容策略反向工程
```cypher
MATCH (d:Domain {name: 'competitor.com'})<-[:BELONGS_TO]-(u:URL)<-[r:RANKS_FOR]-(k:Keyword)
WHERE r.position <= 10
WITH u, COUNT(k) AS keywords, SUM(k.search_volume) AS volume
RETURN u.address AS top_pages,
       keywords,
       volume
ORDER BY volume DESC
LIMIT 20
```

### 季节性关键词识别
```cypher
MATCH (k:Keyword)
WHERE k.text CONTAINS 'christmas' 
   OR k.text CONTAINS 'black friday'
   OR k.text CONTAINS 'summer'
   OR k.text CONTAINS 'winter'
RETURN k.text AS seasonal_keyword,
       k.search_volume AS volume,
       k.difficulty AS difficulty
ORDER BY volume DESC
LIMIT 100
```

## 🚨 监控告警查询

### 每日监控仪表板
```cypher
// 今日概览
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)
RETURN COUNT(DISTINCT k) AS total_keywords,
       COUNT(CASE WHEN r.position <= 10 THEN 1 END) AS top10_count,
       AVG(r.position) AS avg_position,
       SUM(r.traffic) AS total_traffic
```

### 竞争对手动向
```cypher
// 竞争对手新增关键词
MATCH (k:Keyword)-[r:RANKS_FOR]->(u:URL)-[:BELONGS_TO]->(d:Domain)
WHERE r.previous_position = 0 
  AND r.position <= 20
  AND NOT d.name CONTAINS 'eufy'
RETURN d.name AS competitor,
       COUNT(k) AS new_keywords,
       SUM(k.search_volume) AS new_volume
ORDER BY new_volume DESC
```

## 🎓 学习资源

### Neo4j Cypher语法
- `MATCH`: 模式匹配
- `WHERE`: 条件过滤
- `RETURN`: 返回结果
- `WITH`: 管道处理
- `ORDER BY`: 排序
- `LIMIT`: 限制结果数

### 常用函数
- `COUNT()`: 计数
- `SUM()`: 求和
- `AVG()`: 平均值
- `MIN()/MAX()`: 最小/最大值
- `COLLECT()`: 聚合成列表
- `ROUND()`: 四舍五入

## 📝 注意事项

1. **性能优化**: 大查询加 `LIMIT` 限制
2. **索引使用**: 确保关键字段有索引
3. **定期更新**: 每周更新数据保持准确性
4. **备份数据**: 定期备份Neo4j数据库

---

💡 **提示**: 将常用查询保存为Neo4j Browser的收藏夹，方便快速访问！
