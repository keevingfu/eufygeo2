#!/usr/bin/env python3
"""
四大触点整合监控系统 (Integrated Monitoring System for Four Touchpoints)
统一GEO指挥中心 - Unified GEO Command Center

This system provides real-time monitoring and orchestration for all four major touchpoints:
1. AI搜索流量 (AI Search Traffic)
2. 社交内容流量 (Social Content Traffic) 
3. 电商AI导购 (E-commerce AI Shopping)
4. 私域AI客服 (Private Domain AI Customer Service)

Author: Claude AI
Date: 2024-11-19
Version: 1.0.0
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import redis
from flask import Flask, jsonify, request, render_template
from flask_socketio import SocketIO, emit
import threading
import queue
import sqlite3
from contextlib import contextmanager

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TouchpointType(Enum):
    AI_SEARCH = "ai_search"
    SOCIAL_CONTENT = "social_content"
    ECOMMERCE_AI = "ecommerce_ai"
    PRIVATE_DOMAIN = "private_domain"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"
    SUCCESS = "success"

@dataclass
class TouchpointMetrics:
    """四大触点指标数据结构"""
    touchpoint_id: str
    touchpoint_type: TouchpointType
    timestamp: datetime
    
    # 通用指标
    traffic_volume: float
    conversion_rate: float
    engagement_score: float
    geo_score: float
    ai_citation_rate: float
    
    # 特定指标
    platform_metrics: Dict[str, float]
    performance_indicators: Dict[str, float]
    quality_scores: Dict[str, float]
    
    # 状态信息
    status: str
    alerts: List[Dict[str, Any]]
    recommendations: List[str]

@dataclass
class SystemAlert:
    """系统警报数据结构"""
    alert_id: str
    touchpoint_type: TouchpointType
    level: AlertLevel
    title: str
    message: str
    timestamp: datetime
    metrics: Dict[str, float]
    action_required: bool
    resolution_steps: List[str]

class TouchpointMonitor:
    """单个触点监控器基类"""
    
    def __init__(self, touchpoint_type: TouchpointType, config: Dict[str, Any]):
        self.touchpoint_type = touchpoint_type
        self.config = config
        self.is_running = False
        self.metrics_history = []
        self.current_metrics = None
        
    async def collect_metrics(self) -> TouchpointMetrics:
        """收集触点指标 - 子类需要实现"""
        raise NotImplementedError("子类必须实现collect_metrics方法")
    
    async def analyze_performance(self, metrics: TouchpointMetrics) -> List[SystemAlert]:
        """分析性能并生成警报"""
        alerts = []
        
        # 基础性能检查
        if metrics.geo_score < self.config.get('geo_score_threshold', 60):
            alerts.append(SystemAlert(
                alert_id=f"{self.touchpoint_type.value}_geo_low_{int(time.time())}",
                touchpoint_type=self.touchpoint_type,
                level=AlertLevel.WARNING,
                title="GEO分数偏低",
                message=f"当前GEO分数: {metrics.geo_score:.1f}, 目标: {self.config.get('geo_score_threshold', 60)}",
                timestamp=datetime.now(),
                metrics={"geo_score": metrics.geo_score},
                action_required=True,
                resolution_steps=[
                    "检查内容结构化程度",
                    "优化AI引用率",
                    "提升权威性信号",
                    "改进语义优化"
                ]
            ))
        
        # AI引用率检查
        if metrics.ai_citation_rate < self.config.get('citation_rate_threshold', 15):
            alerts.append(SystemAlert(
                alert_id=f"{self.touchpoint_type.value}_citation_low_{int(time.time())}",
                touchpoint_type=self.touchpoint_type,
                level=AlertLevel.CRITICAL,
                title="AI引用率低于目标",
                message=f"当前AI引用率: {metrics.ai_citation_rate:.1f}%, 目标: {self.config.get('citation_rate_threshold', 15)}%",
                timestamp=datetime.now(),
                metrics={"ai_citation_rate": metrics.ai_citation_rate},
                action_required=True,
                resolution_steps=[
                    "优化答案卡片格式",
                    "增强结构化数据",
                    "提高内容权威性",
                    "改进语义匹配度"
                ]
            ))
        
        return alerts
    
    def generate_recommendations(self, metrics: TouchpointMetrics) -> List[str]:
        """生成优化建议"""
        recommendations = []
        
        if metrics.engagement_score < 0.7:
            recommendations.append(f"提升{self.touchpoint_type.value}用户参与度")
        
        if metrics.conversion_rate < 0.05:
            recommendations.append(f"优化{self.touchpoint_type.value}转化漏斗")
        
        if metrics.geo_score < 70:
            recommendations.append(f"加强{self.touchpoint_type.value}的GEO优化")
            
        return recommendations

class AISearchMonitor(TouchpointMonitor):
    """AI搜索流量监控器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(TouchpointType.AI_SEARCH, config)
        
    async def collect_metrics(self) -> TouchpointMetrics:
        """收集AI搜索相关指标"""
        try:
            # 模拟从AI搜索优化模块获取数据
            current_time = datetime.now()
            
            # 计算GEO分数 (模拟算法)
            geo_score = np.random.normal(75, 10)  # 实际应该从ai-search-optimization-module.py获取
            geo_score = max(0, min(100, geo_score))
            
            # AI引用率 (Google AI Overview, Perplexity等)
            ai_citation_rate = np.random.normal(18, 5)
            ai_citation_rate = max(0, min(100, ai_citation_rate))
            
            # 平台特定指标
            platform_metrics = {
                "google_ai_overview_appearances": np.random.poisson(150),
                "perplexity_citations": np.random.poisson(80),
                "bing_copilot_references": np.random.poisson(45),
                "claude_ai_mentions": np.random.poisson(25),
                "chatgpt_citations": np.random.poisson(35)
            }
            
            # 性能指标
            performance_indicators = {
                "answer_card_optimization": np.random.uniform(0.6, 0.9),
                "semantic_relevance": np.random.uniform(0.7, 0.95),
                "authority_signals": np.random.uniform(0.5, 0.85),
                "content_structure_score": np.random.uniform(0.65, 0.9)
            }
            
            # 质量分数
            quality_scores = {
                "content_accuracy": np.random.uniform(0.85, 0.98),
                "information_completeness": np.random.uniform(0.7, 0.92),
                "user_satisfaction": np.random.uniform(0.75, 0.9),
                "expert_authority": np.random.uniform(0.6, 0.85)
            }
            
            metrics = TouchpointMetrics(
                touchpoint_id=f"ai_search_{int(time.time())}",
                touchpoint_type=TouchpointType.AI_SEARCH,
                timestamp=current_time,
                traffic_volume=np.random.poisson(5000),
                conversion_rate=np.random.uniform(0.03, 0.08),
                engagement_score=np.random.uniform(0.6, 0.9),
                geo_score=geo_score,
                ai_citation_rate=ai_citation_rate,
                platform_metrics=platform_metrics,
                performance_indicators=performance_indicators,
                quality_scores=quality_scores,
                status="active",
                alerts=[],
                recommendations=[]
            )
            
            # 生成警报和建议
            alerts = await self.analyze_performance(metrics)
            metrics.alerts = [asdict(alert) for alert in alerts]
            metrics.recommendations = self.generate_recommendations(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"AI搜索监控器数据收集错误: {e}")
            raise

class SocialContentMonitor(TouchpointMonitor):
    """社交内容流量监控器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(TouchpointType.SOCIAL_CONTENT, config)
        
    async def collect_metrics(self) -> TouchpointMetrics:
        """收集社交内容相关指标"""
        try:
            current_time = datetime.now()
            
            # 社交内容GEO分数
            geo_score = np.random.normal(72, 8)
            geo_score = max(0, min(100, geo_score))
            
            # AI推荐引用率
            ai_citation_rate = np.random.normal(16, 4)
            ai_citation_rate = max(0, min(100, ai_citation_rate))
            
            # 平台特定指标
            platform_metrics = {
                "tiktok_search_visibility": np.random.uniform(0.6, 0.9),
                "instagram_explore_reach": np.random.poisson(3000),
                "youtube_shorts_impressions": np.random.poisson(8000),
                "pinterest_discovery_rate": np.random.uniform(0.4, 0.7),
                "twitter_trending_score": np.random.uniform(0.3, 0.8)
            }
            
            # 性能指标
            performance_indicators = {
                "hook_strength_score": np.random.uniform(0.7, 0.95),
                "hashtag_optimization": np.random.uniform(0.6, 0.9),
                "visual_appeal_score": np.random.uniform(0.75, 0.92),
                "engagement_velocity": np.random.uniform(0.5, 0.85)
            }
            
            # 质量分数
            quality_scores = {
                "content_relevance": np.random.uniform(0.8, 0.95),
                "trend_alignment": np.random.uniform(0.65, 0.88),
                "audience_resonance": np.random.uniform(0.7, 0.9),
                "viral_potential": np.random.uniform(0.4, 0.8)
            }
            
            metrics = TouchpointMetrics(
                touchpoint_id=f"social_content_{int(time.time())}",
                touchpoint_type=TouchpointType.SOCIAL_CONTENT,
                timestamp=current_time,
                traffic_volume=np.random.poisson(12000),
                conversion_rate=np.random.uniform(0.02, 0.06),
                engagement_score=np.random.uniform(0.65, 0.92),
                geo_score=geo_score,
                ai_citation_rate=ai_citation_rate,
                platform_metrics=platform_metrics,
                performance_indicators=performance_indicators,
                quality_scores=quality_scores,
                status="active",
                alerts=[],
                recommendations=[]
            )
            
            # 生成警报和建议
            alerts = await self.analyze_performance(metrics)
            metrics.alerts = [asdict(alert) for alert in alerts]
            metrics.recommendations = self.generate_recommendations(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"社交内容监控器数据收集错误: {e}")
            raise

class EcommerceAIMonitor(TouchpointMonitor):
    """电商AI导购监控器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(TouchpointType.ECOMMERCE_AI, config)
        
    async def collect_metrics(self) -> TouchpointMetrics:
        """收集电商AI导购相关指标"""
        try:
            current_time = datetime.now()
            
            # 电商GEO分数
            geo_score = np.random.normal(78, 9)
            geo_score = max(0, min(100, geo_score))
            
            # AI导购引用率
            ai_citation_rate = np.random.normal(22, 6)
            ai_citation_rate = max(0, min(100, ai_citation_rate))
            
            # 平台特定指标
            platform_metrics = {
                "amazon_rufus_recommendations": np.random.poisson(180),
                "tiktok_shop_ai_picks": np.random.poisson(95),
                "instagram_shop_suggestions": np.random.poisson(120),
                "google_shopping_ai_results": np.random.poisson(200),
                "alibaba_ai_assistant_mentions": np.random.poisson(75)
            }
            
            # 性能指标
            performance_indicators = {
                "product_data_completeness": np.random.uniform(0.8, 0.96),
                "comparison_matrix_quality": np.random.uniform(0.75, 0.92),
                "price_competitiveness": np.random.uniform(0.65, 0.88),
                "feature_highlighting": np.random.uniform(0.7, 0.9)
            }
            
            # 质量分数
            quality_scores = {
                "product_description_quality": np.random.uniform(0.85, 0.96),
                "review_sentiment_score": np.random.uniform(0.75, 0.92),
                "inventory_accuracy": np.random.uniform(0.9, 0.99),
                "recommendation_relevance": np.random.uniform(0.8, 0.94)
            }
            
            metrics = TouchpointMetrics(
                touchpoint_id=f"ecommerce_ai_{int(time.time())}",
                touchpoint_type=TouchpointType.ECOMMERCE_AI,
                timestamp=current_time,
                traffic_volume=np.random.poisson(8000),
                conversion_rate=np.random.uniform(0.08, 0.15),
                engagement_score=np.random.uniform(0.7, 0.88),
                geo_score=geo_score,
                ai_citation_rate=ai_citation_rate,
                platform_metrics=platform_metrics,
                performance_indicators=performance_indicators,
                quality_scores=quality_scores,
                status="active",
                alerts=[],
                recommendations=[]
            )
            
            # 生成警报和建议
            alerts = await self.analyze_performance(metrics)
            metrics.alerts = [asdict(alert) for alert in alerts]
            metrics.recommendations = self.generate_recommendations(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"电商AI监控器数据收集错误: {e}")
            raise

class PrivateDomainMonitor(TouchpointMonitor):
    """私域AI客服监控器"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(TouchpointType.PRIVATE_DOMAIN, config)
        
    async def collect_metrics(self) -> TouchpointMetrics:
        """收集私域AI客服相关指标"""
        try:
            current_time = datetime.now()
            
            # 私域GEO分数
            geo_score = np.random.normal(80, 7)
            geo_score = max(0, min(100, geo_score))
            
            # AI客服引用率
            ai_citation_rate = np.random.normal(85, 8)
            ai_citation_rate = max(0, min(100, ai_citation_rate))
            
            # 平台特定指标
            platform_metrics = {
                "whatsapp_business_interactions": np.random.poisson(500),
                "wechat_bot_conversations": np.random.poisson(800),
                "email_ai_responses": np.random.poisson(300),
                "website_chatbot_sessions": np.random.poisson(1200),
                "app_in_chat_support": np.random.poisson(400)
            }
            
            # 性能指标
            performance_indicators = {
                "response_accuracy": np.random.uniform(0.85, 0.96),
                "conversation_flow_optimization": np.random.uniform(0.75, 0.9),
                "customer_satisfaction": np.random.uniform(0.8, 0.94),
                "resolution_rate": np.random.uniform(0.7, 0.88)
            }
            
            # 质量分数
            quality_scores = {
                "answer_relevance": np.random.uniform(0.9, 0.98),
                "response_personalization": np.random.uniform(0.75, 0.9),
                "proactive_assistance": np.random.uniform(0.65, 0.85),
                "escalation_efficiency": np.random.uniform(0.8, 0.95)
            }
            
            metrics = TouchpointMetrics(
                touchpoint_id=f"private_domain_{int(time.time())}",
                touchpoint_type=TouchpointType.PRIVATE_DOMAIN,
                timestamp=current_time,
                traffic_volume=np.random.poisson(3200),
                conversion_rate=np.random.uniform(0.12, 0.25),
                engagement_score=np.random.uniform(0.8, 0.95),
                geo_score=geo_score,
                ai_citation_rate=ai_citation_rate,
                platform_metrics=platform_metrics,
                performance_indicators=performance_indicators,
                quality_scores=quality_scores,
                status="active",
                alerts=[],
                recommendations=[]
            )
            
            # 生成警报和建议
            alerts = await self.analyze_performance(metrics)
            metrics.alerts = [asdict(alert) for alert in alerts]
            metrics.recommendations = self.generate_recommendations(metrics)
            
            return metrics
            
        except Exception as e:
            logger.error(f"私域AI客服监控器数据收集错误: {e}")
            raise

class IntegratedMonitoringSystem:
    """四大触点整合监控系统主控制器"""
    
    def __init__(self, config_file: str = "monitoring_config.json"):
        self.config = self._load_config(config_file)
        self.redis_client = redis.Redis(host='localhost', port=6379, decode_responses=True)
        self.db_path = "monitoring_data.db"
        self._init_database()
        
        # 初始化四大触点监控器
        self.monitors = {
            TouchpointType.AI_SEARCH: AISearchMonitor(self.config.get('ai_search', {})),
            TouchpointType.SOCIAL_CONTENT: SocialContentMonitor(self.config.get('social_content', {})),
            TouchpointType.ECOMMERCE_AI: EcommerceAIMonitor(self.config.get('ecommerce_ai', {})),
            TouchpointType.PRIVATE_DOMAIN: PrivateDomainMonitor(self.config.get('private_domain', {}))
        }
        
        # 系统状态
        self.is_running = False
        self.metrics_queue = queue.Queue()
        self.alert_queue = queue.Queue()
        self.current_metrics = {}
        self.alert_history = []
        
        # Flask应用和SocketIO
        self.app = Flask(__name__)
        self.app.config['SECRET_KEY'] = 'geo_monitoring_secret_key'
        self.socketio = SocketIO(self.app, cors_allowed_origins="*")
        
        self._setup_routes()
        
    def _load_config(self, config_file: str) -> Dict[str, Any]:
        """加载配置文件"""
        default_config = {
            "collection_interval": 30,  # 秒
            "ai_search": {
                "geo_score_threshold": 70,
                "citation_rate_threshold": 15
            },
            "social_content": {
                "geo_score_threshold": 65,
                "citation_rate_threshold": 12
            },
            "ecommerce_ai": {
                "geo_score_threshold": 75,
                "citation_rate_threshold": 20
            },
            "private_domain": {
                "geo_score_threshold": 80,
                "citation_rate_threshold": 80
            }
        }
        
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        except FileNotFoundError:
            logger.warning(f"配置文件 {config_file} 未找到，使用默认配置")
            
        return default_config
    
    def _init_database(self):
        """初始化SQLite数据库"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # 创建指标表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS touchpoint_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    touchpoint_id TEXT,
                    touchpoint_type TEXT,
                    timestamp TEXT,
                    traffic_volume REAL,
                    conversion_rate REAL,
                    engagement_score REAL,
                    geo_score REAL,
                    ai_citation_rate REAL,
                    platform_metrics TEXT,
                    performance_indicators TEXT,
                    quality_scores TEXT,
                    status TEXT,
                    alerts TEXT,
                    recommendations TEXT
                )
            ''')
            
            # 创建警报表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS system_alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id TEXT UNIQUE,
                    touchpoint_type TEXT,
                    level TEXT,
                    title TEXT,
                    message TEXT,
                    timestamp TEXT,
                    metrics TEXT,
                    action_required BOOLEAN,
                    resolution_steps TEXT,
                    resolved BOOLEAN DEFAULT FALSE
                )
            ''')
            
            conn.commit()
    
    @contextmanager
    def get_db_connection(self):
        """数据库连接上下文管理器"""
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
        finally:
            conn.close()
    
    def save_metrics(self, metrics: TouchpointMetrics):
        """保存指标到数据库"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO touchpoint_metrics (
                    touchpoint_id, touchpoint_type, timestamp, traffic_volume,
                    conversion_rate, engagement_score, geo_score, ai_citation_rate,
                    platform_metrics, performance_indicators, quality_scores,
                    status, alerts, recommendations
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metrics.touchpoint_id,
                metrics.touchpoint_type.value,
                metrics.timestamp.isoformat(),
                metrics.traffic_volume,
                metrics.conversion_rate,
                metrics.engagement_score,
                metrics.geo_score,
                metrics.ai_citation_rate,
                json.dumps(metrics.platform_metrics),
                json.dumps(metrics.performance_indicators),
                json.dumps(metrics.quality_scores),
                metrics.status,
                json.dumps(metrics.alerts),
                json.dumps(metrics.recommendations)
            ))
            conn.commit()
    
    def save_alert(self, alert: SystemAlert):
        """保存警报到数据库"""
        with self.get_db_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute('''
                    INSERT INTO system_alerts (
                        alert_id, touchpoint_type, level, title, message,
                        timestamp, metrics, action_required, resolution_steps
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    alert.alert_id,
                    alert.touchpoint_type.value,
                    alert.level.value,
                    alert.title,
                    alert.message,
                    alert.timestamp.isoformat(),
                    json.dumps(alert.metrics),
                    alert.action_required,
                    json.dumps(alert.resolution_steps)
                ))
                conn.commit()
            except sqlite3.IntegrityError:
                # 警报ID已存在，跳过
                pass
    
    async def collect_all_metrics(self) -> Dict[TouchpointType, TouchpointMetrics]:
        """收集所有触点的指标"""
        metrics = {}
        tasks = []
        
        for touchpoint_type, monitor in self.monitors.items():
            task = monitor.collect_metrics()
            tasks.append((touchpoint_type, task))
        
        for touchpoint_type, task in tasks:
            try:
                metric = await task
                metrics[touchpoint_type] = metric
                self.save_metrics(metric)
                
                # 保存警报
                for alert_data in metric.alerts:
                    alert = SystemAlert(
                        alert_id=alert_data['alert_id'],
                        touchpoint_type=TouchpointType(alert_data['touchpoint_type']),
                        level=AlertLevel(alert_data['level']),
                        title=alert_data['title'],
                        message=alert_data['message'],
                        timestamp=datetime.fromisoformat(alert_data['timestamp']),
                        metrics=alert_data['metrics'],
                        action_required=alert_data['action_required'],
                        resolution_steps=alert_data['resolution_steps']
                    )
                    self.save_alert(alert)
                    self.alert_queue.put(alert)
                
            except Exception as e:
                logger.error(f"收集 {touchpoint_type.value} 指标时出错: {e}")
        
        return metrics
    
    def calculate_overall_geo_score(self, metrics: Dict[TouchpointType, TouchpointMetrics]) -> float:
        """计算整体GEO分数"""
        if not metrics:
            return 0.0
        
        # 权重分配
        weights = {
            TouchpointType.AI_SEARCH: 0.3,
            TouchpointType.SOCIAL_CONTENT: 0.25,
            TouchpointType.ECOMMERCE_AI: 0.3,
            TouchpointType.PRIVATE_DOMAIN: 0.15
        }
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for touchpoint_type, metric in metrics.items():
            weight = weights.get(touchpoint_type, 0.25)
            weighted_score += metric.geo_score * weight
            total_weight += weight
        
        return weighted_score / total_weight if total_weight > 0 else 0.0
    
    def generate_system_recommendations(self, metrics: Dict[TouchpointType, TouchpointMetrics]) -> List[str]:
        """生成系统级优化建议"""
        recommendations = []
        
        overall_geo_score = self.calculate_overall_geo_score(metrics)
        
        if overall_geo_score < 70:
            recommendations.append("整体GEO分数偏低，需要全面优化各触点")
        
        # 分析各触点表现
        low_performing = [t.value for t, m in metrics.items() if m.geo_score < 65]
        if low_performing:
            recommendations.append(f"优先关注表现较差的触点: {', '.join(low_performing)}")
        
        # AI引用率分析
        low_citation = [t.value for t, m in metrics.items() if m.ai_citation_rate < 15]
        if low_citation:
            recommendations.append(f"提升AI引用率较低的触点: {', '.join(low_citation)}")
        
        return recommendations
    
    async def monitoring_loop(self):
        """主监控循环"""
        logger.info("开始四大触点整合监控...")
        
        while self.is_running:
            try:
                # 收集所有触点指标
                metrics = await self.collect_all_metrics()
                self.current_metrics = metrics
                
                # 计算整体指标
                overall_geo_score = self.calculate_overall_geo_score(metrics)
                system_recommendations = self.generate_system_recommendations(metrics)
                
                # 准备仪表板数据
                dashboard_data = {
                    "timestamp": datetime.now().isoformat(),
                    "overall_geo_score": overall_geo_score,
                    "touchpoints": {
                        t.value: asdict(m) for t, m in metrics.items()
                    },
                    "system_recommendations": system_recommendations,
                    "active_alerts": len([
                        alert for metric in metrics.values() 
                        for alert in metric.alerts
                    ])
                }
                
                # 缓存到Redis
                self.redis_client.setex(
                    "geo_monitoring:dashboard", 
                    300,  # 5分钟过期
                    json.dumps(dashboard_data)
                )
                
                # 发送实时更新到前端
                self.socketio.emit('dashboard_update', dashboard_data)
                
                logger.info(f"监控数据已更新 - 整体GEO分数: {overall_geo_score:.1f}")
                
                # 等待下次收集
                await asyncio.sleep(self.config['collection_interval'])
                
            except Exception as e:
                logger.error(f"监控循环错误: {e}")
                await asyncio.sleep(5)  # 错误后短暂等待
    
    def _setup_routes(self):
        """设置Flask路由"""
        
        @self.app.route('/')
        def dashboard():
            """主仪表板页面"""
            return render_template('monitoring_dashboard.html')
        
        @self.app.route('/api/dashboard')
        def api_dashboard():
            """获取仪表板数据"""
            cached_data = self.redis_client.get("geo_monitoring:dashboard")
            if cached_data:
                return jsonify(json.loads(cached_data))
            
            return jsonify({
                "error": "暂无数据",
                "timestamp": datetime.now().isoformat()
            })
        
        @self.app.route('/api/metrics/<touchpoint_type>')
        def api_touchpoint_metrics(touchpoint_type):
            """获取特定触点的历史指标"""
            try:
                with self.get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT * FROM touchpoint_metrics 
                        WHERE touchpoint_type = ? 
                        ORDER BY timestamp DESC 
                        LIMIT 100
                    ''', (touchpoint_type,))
                    
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    
                    metrics = []
                    for row in rows:
                        metric_dict = dict(zip(columns, row))
                        # 解析JSON字段
                        json_fields = ['platform_metrics', 'performance_indicators', 'quality_scores', 'alerts', 'recommendations']
                        for field in json_fields:
                            if metric_dict[field]:
                                metric_dict[field] = json.loads(metric_dict[field])
                        metrics.append(metric_dict)
                    
                    return jsonify(metrics)
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/alerts')
        def api_alerts():
            """获取系统警报"""
            try:
                with self.get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        SELECT * FROM system_alerts 
                        WHERE resolved = FALSE 
                        ORDER BY timestamp DESC 
                        LIMIT 50
                    ''', )
                    
                    rows = cursor.fetchall()
                    columns = [description[0] for description in cursor.description]
                    
                    alerts = []
                    for row in rows:
                        alert_dict = dict(zip(columns, row))
                        # 解析JSON字段
                        alert_dict['metrics'] = json.loads(alert_dict['metrics'] or '{}')
                        alert_dict['resolution_steps'] = json.loads(alert_dict['resolution_steps'] or '[]')
                        alerts.append(alert_dict)
                    
                    return jsonify(alerts)
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
        @self.app.route('/api/alerts/<alert_id>/resolve', methods=['POST'])
        def api_resolve_alert(alert_id):
            """标记警报为已解决"""
            try:
                with self.get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE system_alerts 
                        SET resolved = TRUE 
                        WHERE alert_id = ?
                    ''', (alert_id,))
                    conn.commit()
                    
                    return jsonify({"success": True})
                    
            except Exception as e:
                return jsonify({"error": str(e)}), 500
    
    def start_monitoring(self):
        """启动监控系统"""
        self.is_running = True
        
        # 启动监控循环
        monitoring_thread = threading.Thread(
            target=lambda: asyncio.run(self.monitoring_loop())
        )
        monitoring_thread.daemon = True
        monitoring_thread.start()
        
        logger.info("四大触点整合监控系统已启动")
    
    def stop_monitoring(self):
        """停止监控系统"""
        self.is_running = False
        logger.info("四大触点整合监控系统已停止")
    
    def run_server(self, host='127.0.0.1', port=5002, debug=False):
        """运行Flask服务器"""
        self.start_monitoring()
        logger.info(f"监控仪表板启动: http://{host}:{port}")
        self.socketio.run(self.app, host=host, port=port, debug=debug)

def create_monitoring_dashboard_template():
    """创建监控仪表板HTML模板"""
    template_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>GEO四大触点整合监控系统</title>
    <script src="https://cdn.socket.io/4.7.2/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/echarts@5.4.3/dist/echarts.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Microsoft YaHei', sans-serif; background: #f5f7fa; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
        .dashboard { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; padding: 20px; }
        .card { background: white; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
        .metric-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
        .metric-item { text-align: center; padding: 15px; border-radius: 8px; background: #f8f9fa; }
        .metric-value { font-size: 24px; font-weight: bold; margin-bottom: 5px; }
        .metric-label { font-size: 12px; color: #6c757d; }
        .alert { padding: 10px; border-radius: 5px; margin: 5px 0; }
        .alert-warning { background: #fff3cd; border-left: 4px solid #ffc107; }
        .alert-critical { background: #f8d7da; border-left: 4px solid #dc3545; }
        .chart-container { height: 300px; }
        .status-indicator { display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 8px; }
        .status-active { background: #28a745; }
        .status-warning { background: #ffc107; }
        .status-critical { background: #dc3545; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🎯 GEO四大触点整合监控系统</h1>
        <p>实时监控AI搜索、社交内容、电商AI导购、私域客服</p>
    </div>

    <div class="dashboard">
        <!-- 整体概览 -->
        <div class="card">
            <h3>🌟 整体GEO表现</h3>
            <div class="chart-container" id="overallGeoChart"></div>
        </div>

        <!-- 四大触点状态 -->
        <div class="card">
            <h3>📊 四大触点状态</h3>
            <div id="touchpointStatus"></div>
        </div>

        <!-- AI引用率趋势 -->
        <div class="card">
            <h3>🤖 AI引用率趋势</h3>
            <div class="chart-container" id="citationRateChart"></div>
        </div>

        <!-- 系统警报 -->
        <div class="card">
            <h3>🚨 系统警报</h3>
            <div id="systemAlerts"></div>
        </div>
    </div>

    <script>
        // WebSocket连接
        const socket = io();
        
        // 图表实例
        let overallGeoChart = echarts.init(document.getElementById('overallGeoChart'));
        let citationRateChart = echarts.init(document.getElementById('citationRateChart'));
        
        // 监听数据更新
        socket.on('dashboard_update', function(data) {
            updateDashboard(data);
        });
        
        function updateDashboard(data) {
            updateOverallGeoChart(data.overall_geo_score);
            updateTouchpointStatus(data.touchpoints);
            updateCitationRateChart(data.touchpoints);
            updateSystemAlerts(data.touchpoints);
        }
        
        function updateOverallGeoChart(score) {
            const option = {
                series: [{
                    type: 'gauge',
                    axisLine: {
                        lineStyle: {
                            width: 30,
                            color: [
                                [0.3, '#fd666d'],
                                [0.7, '#ffc107'],
                                [1, '#28a745']
                            ]
                        }
                    },
                    pointer: { itemStyle: { color: 'auto' } },
                    axisTick: { distance: -30, length: 8, lineStyle: { color: '#fff', width: 2 } },
                    splitLine: { distance: -30, length: 30, lineStyle: { color: '#fff', width: 4 } },
                    axisLabel: { color: 'auto', distance: 40, fontSize: 14 },
                    detail: { fontSize: 24, formatter: '{value}分' },
                    data: [{ value: score, name: 'GEO分数' }]
                }]
            };
            overallGeoChart.setOption(option);
        }
        
        function updateTouchpointStatus(touchpoints) {
            const container = document.getElementById('touchpointStatus');
            container.innerHTML = '';
            
            const touchpointNames = {
                'ai_search': 'AI搜索流量',
                'social_content': '社交内容流量',
                'ecommerce_ai': '电商AI导购',
                'private_domain': '私域AI客服'
            };
            
            Object.entries(touchpoints).forEach(([key, data]) => {
                const status = data.geo_score >= 70 ? 'active' : (data.geo_score >= 50 ? 'warning' : 'critical');
                const statusDiv = document.createElement('div');
                statusDiv.className = 'metric-item';
                statusDiv.innerHTML = `
                    <div class="metric-value">
                        <span class="status-indicator status-${status}"></span>
                        ${data.geo_score.toFixed(1)}分
                    </div>
                    <div class="metric-label">${touchpointNames[key]}</div>
                `;
                container.appendChild(statusDiv);
            });
        }
        
        function updateCitationRateChart(touchpoints) {
            const data = Object.entries(touchpoints).map(([key, data]) => ({
                name: key,
                value: data.ai_citation_rate
            }));
            
            const option = {
                tooltip: { trigger: 'item' },
                legend: { bottom: '5%' },
                series: [{
                    type: 'pie',
                    radius: ['40%', '70%'],
                    data: data,
                    emphasis: {
                        itemStyle: {
                            shadowBlur: 10,
                            shadowOffsetX: 0,
                            shadowColor: 'rgba(0, 0, 0, 0.5)'
                        }
                    }
                }]
            };
            citationRateChart.setOption(option);
        }
        
        function updateSystemAlerts(touchpoints) {
            const container = document.getElementById('systemAlerts');
            container.innerHTML = '';
            
            Object.values(touchpoints).forEach(data => {
                data.alerts.forEach(alert => {
                    const alertDiv = document.createElement('div');
                    alertDiv.className = `alert alert-${alert.level}`;
                    alertDiv.innerHTML = `
                        <strong>${alert.title}</strong><br>
                        ${alert.message}
                    `;
                    container.appendChild(alertDiv);
                });
            });
            
            if (container.children.length === 0) {
                container.innerHTML = '<div class="alert">✅ 系统运行正常，暂无警报</div>';
            }
        }
        
        // 初始化加载数据
        fetch('/api/dashboard')
            .then(response => response.json())
            .then(data => updateDashboard(data))
            .catch(error => console.error('Error loading dashboard data:', error));
    </script>
</body>
</html>
    """
    
    # 创建模板目录
    import os
    os.makedirs('templates', exist_ok=True)
    
    with open('templates/monitoring_dashboard.html', 'w', encoding='utf-8') as f:
        f.write(template_content)

if __name__ == "__main__":
    # 创建仪表板模板
    create_monitoring_dashboard_template()
    
    # 启动监控系统
    monitoring_system = IntegratedMonitoringSystem()
    
    try:
        monitoring_system.run_server(host='127.0.0.1', port=5002, debug=False)
    except KeyboardInterrupt:
        monitoring_system.stop_monitoring()
        logger.info("监控系统已安全关闭")