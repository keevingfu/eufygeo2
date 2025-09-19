#!/usr/bin/env python3
"""
EufyGeo2 项目 Playwright 综合功能验证测试套件
Comprehensive Playwright Testing Suite for EufyGeo2 Project

测试覆盖范围:
1. AI搜索流量优化模块功能验证
2. 社交内容GEO优化工具测试
3. 电商AI导购优化系统检测
4. 私域AI客服系统验证
5. 四大触点整合监控系统测试
6. Neo4j SEO仪表板功能检测
7. 用户体验和界面交互测试

Author: Claude AI
Date: 2024-11-19
Version: 1.0.0
"""

import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
import subprocess
import sys
import os
import signal
import requests
from pathlib import Path

# Playwright导入
try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    from playwright.sync_api import sync_playwright
except ImportError:
    print("❌ Playwright未安装，请运行: pip install playwright")
    print("   然后运行: playwright install")
    sys.exit(1)

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class TestResult:
    """测试结果数据结构"""
    test_name: str
    module_name: str
    status: str  # passed, failed, skipped, error
    execution_time: float
    error_message: Optional[str] = None
    screenshot_path: Optional[str] = None
    details: Dict[str, Any] = None
    recommendations: List[str] = None

@dataclass
class ModuleStatus:
    """模块状态信息"""
    name: str
    file_path: str
    is_executable: bool
    has_server: bool
    server_port: Optional[int] = None
    dependencies: List[str] = None
    status: str = "unknown"  # running, stopped, error

class ComprehensiveTestSuite:
    """综合测试套件"""
    
    def __init__(self):
        self.project_root = Path("/Users/cavin/Desktop/dev/eufygeo2")
        self.test_results = []
        self.running_processes = []
        self.browser = None
        self.context = None
        self.screenshots_dir = self.project_root / "test_screenshots"
        self.screenshots_dir.mkdir(exist_ok=True)
        
        # 定义所有模块
        self.modules = {
            "ai_search_optimization": {
                "file": "ai-search-optimization-module.py",
                "port": None,
                "has_ui": False,
                "test_functions": ["test_semantic_analysis", "test_content_optimization", "test_geo_scoring"]
            },
            "social_content_optimizer": {
                "file": "social-content-geo-optimizer.py", 
                "port": None,
                "has_ui": False,
                "test_functions": ["test_video_analysis", "test_hashtag_optimization", "test_platform_optimization"]
            },
            "ecommerce_ai_optimizer": {
                "file": "ecommerce-ai-shopping-optimizer.py",
                "port": None, 
                "has_ui": False,
                "test_functions": ["test_product_optimization", "test_comparison_matrix", "test_platform_integration"]
            },
            "private_domain_service": {
                "file": "private-domain-ai-customer-service.py",
                "port": None,
                "has_ui": False, 
                "test_functions": ["test_conversation_flow", "test_answer_generation", "test_personalization"]
            },
            "integrated_monitoring": {
                "file": "integrated-monitoring-system.py",
                "port": 5002,
                "has_ui": True,
                "test_functions": ["test_dashboard_loading", "test_realtime_updates", "test_alert_system"]
            },
            "neo4j_dashboard": {
                "file": "neo4j_dashboard_server.py",
                "port": 5001,
                "has_ui": True,
                "test_functions": ["test_database_connection", "test_api_endpoints", "test_data_visualization"]
            },
            "seo_dashboard": {
                "file": "eufy-seo-dashboard.html",
                "port": 8000,
                "has_ui": True,
                "test_functions": ["test_chart_rendering", "test_responsive_design", "test_data_loading"]
            }
        }
    
    async def setup_browser(self):
        """初始化浏览器"""
        try:
            playwright = await async_playwright().start()
            self.browser = await playwright.chromium.launch(
                headless=False,  # 显示浏览器以便观察测试过程
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-web-security',
                    '--allow-running-insecure-content'
                ]
            )
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
            )
            logger.info("✅ 浏览器初始化成功")
        except Exception as e:
            logger.error(f"❌ 浏览器初始化失败: {e}")
            raise
    
    async def cleanup_browser(self):
        """清理浏览器资源"""
        try:
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            logger.info("✅ 浏览器资源清理完成")
        except Exception as e:
            logger.error(f"⚠️ 浏览器清理警告: {e}")
    
    def start_server_process(self, module_name: str, file_path: str, port: int) -> Optional[subprocess.Popen]:
        """启动服务器进程"""
        try:
            full_path = self.project_root / file_path
            if not full_path.exists():
                logger.warning(f"⚠️ 文件不存在: {full_path}")
                return None
            
            # 检查端口是否被占用
            if self.is_port_in_use(port):
                logger.info(f"🔄 端口 {port} 已被占用，尝试终止现有进程")
                self.kill_process_on_port(port)
                time.sleep(2)
            
            if file_path.endswith('.py'):
                process = subprocess.Popen(
                    [sys.executable, str(full_path)],
                    cwd=str(self.project_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
            elif file_path.endswith('.html'):
                # 使用Python内置HTTP服务器托管HTML文件
                process = subprocess.Popen(
                    [sys.executable, '-m', 'http.server', str(port)],
                    cwd=str(self.project_root),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    universal_newlines=True
                )
            else:
                logger.warning(f"⚠️ 不支持的文件类型: {file_path}")
                return None
            
            self.running_processes.append((module_name, process))
            
            # 等待服务器启动
            time.sleep(3)
            
            # 验证服务器是否成功启动
            if self.is_port_in_use(port):
                logger.info(f"✅ {module_name} 服务器启动成功 (端口: {port})")
                return process
            else:
                logger.error(f"❌ {module_name} 服务器启动失败")
                process.terminate()
                return None
                
        except Exception as e:
            logger.error(f"❌ 启动 {module_name} 服务器失败: {e}")
            return None
    
    def is_port_in_use(self, port: int) -> bool:
        """检查端口是否被占用"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                return s.connect_ex(('localhost', port)) == 0
        except:
            return False
    
    def kill_process_on_port(self, port: int):
        """终止占用指定端口的进程"""
        try:
            if sys.platform == "darwin":  # macOS
                subprocess.run(['lsof', '-ti', f':{port}', '|', 'xargs', 'kill', '-9'], 
                             shell=True, capture_output=True)
            elif sys.platform.startswith("linux"):
                subprocess.run(['fuser', '-k', f'{port}/tcp'], capture_output=True)
        except:
            pass
    
    async def take_screenshot(self, page: Page, test_name: str) -> str:
        """截取页面截图"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = self.screenshots_dir / f"{test_name}_{timestamp}.png"
            await page.screenshot(path=str(screenshot_path))
            return str(screenshot_path)
        except Exception as e:
            logger.error(f"❌ 截图失败: {e}")
            return None
    
    async def test_ai_search_optimization_module(self) -> List[TestResult]:
        """测试AI搜索优化模块"""
        results = []
        module_name = "ai_search_optimization"
        
        try:
            # 测试模块导入
            start_time = time.time()
            
            # 尝试导入模块
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "ai_search_module", 
                self.project_root / "ai-search-optimization-module.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            execution_time = time.time() - start_time
            
            # 测试主要类是否存在
            required_classes = ['AIOptimizedContentEngine', 'SemanticAnalyzer', 'AnswerCardGenerator']
            missing_classes = []
            
            for class_name in required_classes:
                if not hasattr(module, class_name):
                    missing_classes.append(class_name)
            
            if missing_classes:
                results.append(TestResult(
                    test_name="class_availability",
                    module_name=module_name,
                    status="failed",
                    execution_time=execution_time,
                    error_message=f"缺失类: {', '.join(missing_classes)}",
                    recommendations=["检查类定义和导入"]
                ))
            else:
                results.append(TestResult(
                    test_name="class_availability", 
                    module_name=module_name,
                    status="passed",
                    execution_time=execution_time,
                    details={"available_classes": required_classes}
                ))
            
            # 测试功能调用
            try:
                engine = module.AIOptimizedContentEngine()
                test_content = "Eufy security cameras provide advanced home monitoring."
                
                # 测试语义分析
                start_time = time.time()
                semantic_result = engine.analyze_content_semantics(test_content)
                execution_time = time.time() - start_time
                
                if semantic_result and 'semantic_score' in semantic_result:
                    results.append(TestResult(
                        test_name="semantic_analysis",
                        module_name=module_name, 
                        status="passed",
                        execution_time=execution_time,
                        details={"semantic_score": semantic_result['semantic_score']}
                    ))
                else:
                    results.append(TestResult(
                        test_name="semantic_analysis",
                        module_name=module_name,
                        status="failed", 
                        execution_time=execution_time,
                        error_message="语义分析返回结果格式错误",
                        recommendations=["检查语义分析算法", "验证返回数据结构"]
                    ))
                
            except Exception as func_error:
                results.append(TestResult(
                    test_name="function_execution",
                    module_name=module_name,
                    status="error",
                    execution_time=0,
                    error_message=f"功能调用错误: {str(func_error)}",
                    recommendations=["检查模块依赖", "验证初始化参数", "修复运行时错误"]
                ))
                
        except Exception as e:
            results.append(TestResult(
                test_name="module_import",
                module_name=module_name,
                status="error", 
                execution_time=0,
                error_message=f"模块导入失败: {str(e)}",
                recommendations=["检查文件路径", "验证语法错误", "安装缺失依赖"]
            ))
        
        return results
    
    async def test_social_content_optimizer(self) -> List[TestResult]:
        """测试社交内容优化工具"""
        results = []
        module_name = "social_content_optimizer"
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "social_content_module", 
                self.project_root / "social-content-geo-optimizer.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 测试主要类
            required_classes = ['SocialContentGEOOptimizer', 'VideoAnalyzer', 'HashtagOptimizer']
            for class_name in required_classes:
                start_time = time.time()
                if hasattr(module, class_name):
                    results.append(TestResult(
                        test_name=f"{class_name}_availability",
                        module_name=module_name,
                        status="passed",
                        execution_time=time.time() - start_time
                    ))
                else:
                    results.append(TestResult(
                        test_name=f"{class_name}_availability", 
                        module_name=module_name,
                        status="failed",
                        execution_time=time.time() - start_time,
                        error_message=f"类 {class_name} 不存在",
                        recommendations=["检查类定义", "验证导入路径"]
                    ))
            
            # 测试功能
            try:
                optimizer = module.SocialContentGEOOptimizer()
                
                # 测试视频分析功能
                test_video_data = {
                    "title": "Best Security Camera Setup 2024",
                    "description": "Learn how to set up eufy cameras",
                    "duration": 300,
                    "platform": "tiktok"
                }
                
                start_time = time.time()
                video_result = optimizer.optimize_video_content(test_video_data)
                execution_time = time.time() - start_time
                
                if video_result and 'optimization_score' in video_result:
                    results.append(TestResult(
                        test_name="video_optimization",
                        module_name=module_name,
                        status="passed", 
                        execution_time=execution_time,
                        details={"optimization_score": video_result['optimization_score']}
                    ))
                else:
                    results.append(TestResult(
                        test_name="video_optimization",
                        module_name=module_name,
                        status="failed",
                        execution_time=execution_time,
                        error_message="视频优化返回结果格式错误",
                        recommendations=["检查视频分析算法", "验证返回数据结构"]
                    ))
                    
            except Exception as func_error:
                results.append(TestResult(
                    test_name="function_execution", 
                    module_name=module_name,
                    status="error",
                    execution_time=0,
                    error_message=f"功能执行错误: {str(func_error)}",
                    recommendations=["检查依赖库", "验证输入参数", "修复运行时错误"]
                ))
                
        except Exception as e:
            results.append(TestResult(
                test_name="module_import",
                module_name=module_name, 
                status="error",
                execution_time=0,
                error_message=f"模块导入失败: {str(e)}",
                recommendations=["检查文件语法", "安装依赖包", "验证模块结构"]
            ))
        
        return results
    
    async def test_ecommerce_ai_optimizer(self) -> List[TestResult]:
        """测试电商AI导购优化系统"""
        results = []
        module_name = "ecommerce_ai_optimizer"
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "ecommerce_module",
                self.project_root / "ecommerce-ai-shopping-optimizer.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 测试关键类
            key_classes = ['EcommerceAIShoppingAssistantOptimizer', 'ProductDataStructurer', 'ComparisonMatrixGenerator']
            for class_name in key_classes:
                start_time = time.time()
                if hasattr(module, class_name):
                    results.append(TestResult(
                        test_name=f"{class_name}_check",
                        module_name=module_name,
                        status="passed",
                        execution_time=time.time() - start_time
                    ))
                else:
                    results.append(TestResult(
                        test_name=f"{class_name}_check",
                        module_name=module_name, 
                        status="failed",
                        execution_time=time.time() - start_time,
                        error_message=f"缺失关键类: {class_name}",
                        recommendations=["检查类定义完整性", "验证继承关系"]
                    ))
            
            # 测试产品优化功能
            try:
                optimizer = module.EcommerceAIShoppingAssistantOptimizer()
                
                test_product = {
                    "name": "eufy Security Camera",
                    "price": 199.99,
                    "features": ["4K Resolution", "Night Vision", "Two-Way Audio"],
                    "category": "security_cameras"
                }
                
                start_time = time.time()
                optimization_result = optimizer.optimize_product_for_ai_assistant(
                    test_product, 
                    module.EcommercePlatform.AMAZON_RUFUS
                )
                execution_time = time.time() - start_time
                
                if optimization_result and hasattr(optimization_result, 'ai_shopping_score'):
                    results.append(TestResult(
                        test_name="product_optimization",
                        module_name=module_name,
                        status="passed",
                        execution_time=execution_time,
                        details={"ai_shopping_score": optimization_result.ai_shopping_score}
                    ))
                else:
                    results.append(TestResult(
                        test_name="product_optimization",
                        module_name=module_name,
                        status="failed", 
                        execution_time=execution_time,
                        error_message="产品优化结果结构错误",
                        recommendations=["检查优化算法逻辑", "验证结果数据结构", "测试不同产品类型"]
                    ))
                    
            except Exception as func_error:
                results.append(TestResult(
                    test_name="product_optimization_execution",
                    module_name=module_name,
                    status="error",
                    execution_time=0,
                    error_message=f"产品优化执行错误: {str(func_error)}",
                    recommendations=["检查算法实现", "验证输入数据格式", "处理边界条件"]
                ))
                
        except Exception as e:
            results.append(TestResult(
                test_name="module_import",
                module_name=module_name,
                status="error",
                execution_time=0,
                error_message=f"模块导入失败: {str(e)}",
                recommendations=["检查模块语法", "确认依赖安装", "验证文件完整性"]
            ))
        
        return results
    
    async def test_private_domain_service(self) -> List[TestResult]:
        """测试私域AI客服系统"""
        results = []
        module_name = "private_domain_service"
        
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "private_domain_module",
                self.project_root / "private-domain-ai-customer-service.py"
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # 测试核心类
            core_classes = ['PrivateDomainAICustomerServiceOptimizer', 'ConversationFlowOptimizer', 'MessageOptimizer']
            for class_name in core_classes:
                start_time = time.time()
                if hasattr(module, class_name):
                    results.append(TestResult(
                        test_name=f"{class_name}_availability",
                        module_name=module_name,
                        status="passed",
                        execution_time=time.time() - start_time
                    ))
                else:
                    results.append(TestResult(
                        test_name=f"{class_name}_availability",
                        module_name=module_name,
                        status="failed",
                        execution_time=time.time() - start_time,
                        error_message=f"核心类缺失: {class_name}",
                        recommendations=["检查类定义", "验证模块结构", "确认实现完整性"]
                    ))
            
            # 测试对话优化功能
            try:
                optimizer = module.PrivateDomainAICustomerServiceOptimizer()
                
                test_faq_data = [
                    {
                        "question": "How to reset eufy camera?",
                        "answer": "Press and hold the reset button for 10 seconds.",
                        "category": "troubleshooting"
                    }
                ]
                
                test_product_catalog = {
                    "cameras": [
                        {"name": "eufyCam 3", "price": 199.99, "features": ["4K", "Battery"]}
                    ]
                }
                
                start_time = time.time()
                answer_library = optimizer.create_ai_optimized_answer_library(
                    test_faq_data, 
                    test_product_catalog
                )
                execution_time = time.time() - start_time
                
                if answer_library and 'standardized_answers' in answer_library:
                    results.append(TestResult(
                        test_name="answer_library_creation",
                        module_name=module_name,
                        status="passed",
                        execution_time=execution_time,
                        details={"answers_count": len(answer_library['standardized_answers'])}
                    ))
                else:
                    results.append(TestResult(
                        test_name="answer_library_creation", 
                        module_name=module_name,
                        status="failed",
                        execution_time=execution_time,
                        error_message="答案库创建结果格式错误",
                        recommendations=["检查答案生成逻辑", "验证数据结构", "测试不同输入格式"]
                    ))
                    
            except Exception as func_error:
                results.append(TestResult(
                    test_name="conversation_optimization",
                    module_name=module_name, 
                    status="error",
                    execution_time=0,
                    error_message=f"对话优化功能错误: {str(func_error)}",
                    recommendations=["检查算法实现", "验证NLP处理", "测试边界情况"]
                ))
                
        except Exception as e:
            results.append(TestResult(
                test_name="module_import",
                module_name=module_name,
                status="error", 
                execution_time=0,
                error_message=f"模块导入失败: {str(e)}",
                recommendations=["检查Python语法", "安装NLP依赖", "验证文件完整性"]
            ))
        
        return results
    
    async def test_integrated_monitoring_system(self) -> List[TestResult]:
        """测试四大触点整合监控系统"""
        results = []
        module_name = "integrated_monitoring"
        
        # 启动监控系统服务器
        process = self.start_server_process(module_name, "integrated-monitoring-system.py", 5002)
        
        if not process:
            results.append(TestResult(
                test_name="server_startup",
                module_name=module_name,
                status="failed",
                execution_time=0,
                error_message="监控系统服务器启动失败",
                recommendations=["检查端口占用", "验证依赖安装", "查看服务器日志"]
            ))
            return results
        
        # 等待服务器完全启动
        await asyncio.sleep(5)
        
        # 测试服务器响应
        try:
            start_time = time.time()
            response = requests.get("http://127.0.0.1:5002", timeout=10)
            execution_time = time.time() - start_time
            
            if response.status_code == 200:
                results.append(TestResult(
                    test_name="server_response",
                    module_name=module_name,
                    status="passed", 
                    execution_time=execution_time,
                    details={"status_code": response.status_code, "content_length": len(response.content)}
                ))
            else:
                results.append(TestResult(
                    test_name="server_response",
                    module_name=module_name,
                    status="failed",
                    execution_time=execution_time,
                    error_message=f"服务器响应错误: {response.status_code}",
                    recommendations=["检查服务器配置", "验证路由设置", "查看错误日志"]
                ))
        except requests.RequestException as e:
            results.append(TestResult(
                test_name="server_response",
                module_name=module_name,
                status="error",
                execution_time=0,
                error_message=f"服务器连接失败: {str(e)}",
                recommendations=["检查服务器状态", "验证网络连接", "确认端口可访问"]
            ))
        
        # 测试API端点
        api_endpoints = [
            "/api/dashboard",
            "/api/alerts"
        ]
        
        for endpoint in api_endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"http://127.0.0.1:5002{endpoint}", timeout=10)
                execution_time = time.time() - start_time
                
                if response.status_code == 200:
                    data = response.json()
                    results.append(TestResult(
                        test_name=f"api_{endpoint.replace('/', '_')}",
                        module_name=module_name,
                        status="passed",
                        execution_time=execution_time,
                        details={"endpoint": endpoint, "data_keys": list(data.keys()) if isinstance(data, dict) else "non-dict"}
                    ))
                else:
                    results.append(TestResult(
                        test_name=f"api_{endpoint.replace('/', '_')}",
                        module_name=module_name,
                        status="failed",
                        execution_time=execution_time,
                        error_message=f"API端点错误: {response.status_code}",
                        recommendations=["检查API实现", "验证数据库连接", "确认权限设置"]
                    ))
            except Exception as e:
                results.append(TestResult(
                    test_name=f"api_{endpoint.replace('/', '_')}",
                    module_name=module_name,
                    status="error",
                    execution_time=0,
                    error_message=f"API测试失败: {str(e)}",
                    recommendations=["检查API可用性", "验证请求格式", "确认服务器运行状态"]
                ))
        
        # 浏览器UI测试
        if self.context:
            try:
                page = await self.context.new_page()
                start_time = time.time()
                
                await page.goto("http://127.0.0.1:5002", wait_until='networkidle', timeout=15000)
                execution_time = time.time() - start_time
                
                # 检查页面标题
                title = await page.title()
                if "GEO" in title and "监控" in title:
                    results.append(TestResult(
                        test_name="dashboard_ui_loading",
                        module_name=module_name,
                        status="passed",
                        execution_time=execution_time,
                        details={"page_title": title},
                        screenshot_path=await self.take_screenshot(page, "monitoring_dashboard")
                    ))
                else:
                    results.append(TestResult(
                        test_name="dashboard_ui_loading", 
                        module_name=module_name,
                        status="failed",
                        execution_time=execution_time,
                        error_message=f"页面标题不符合预期: {title}",
                        recommendations=["检查HTML模板", "验证页面内容", "确认资源加载"],
                        screenshot_path=await self.take_screenshot(page, "monitoring_dashboard_failed")
                    ))
                
                # 检查图表元素
                chart_elements = await page.query_selector_all('.chart-container')
                if len(chart_elements) > 0:
                    results.append(TestResult(
                        test_name="dashboard_charts",
                        module_name=module_name,
                        status="passed",
                        execution_time=0,
                        details={"chart_count": len(chart_elements)}
                    ))
                else:
                    results.append(TestResult(
                        test_name="dashboard_charts",
                        module_name=module_name,
                        status="failed",
                        execution_time=0,
                        error_message="未找到图表元素",
                        recommendations=["检查ECharts集成", "验证数据加载", "确认图表初始化"]
                    ))
                
                await page.close()
                
            except Exception as e:
                results.append(TestResult(
                    test_name="dashboard_ui_test",
                    module_name=module_name,
                    status="error",
                    execution_time=0,
                    error_message=f"UI测试失败: {str(e)}",
                    recommendations=["检查页面加载", "验证JavaScript执行", "确认网络连接"]
                ))
        
        return results
    
    async def test_neo4j_dashboard_system(self) -> List[TestResult]:
        """测试Neo4j仪表板系统"""
        results = []
        module_name = "neo4j_dashboard"
        
        # 检查Neo4j数据库连接
        try:
            start_time = time.time()
            neo4j_running = self.is_port_in_use(7474)  # Neo4j HTTP端口
            execution_time = time.time() - start_time
            
            if neo4j_running:
                results.append(TestResult(
                    test_name="neo4j_database_connection",
                    module_name=module_name, 
                    status="passed",
                    execution_time=execution_time,
                    details={"neo4j_port": 7474, "status": "running"}
                ))
            else:
                results.append(TestResult(
                    test_name="neo4j_database_connection",
                    module_name=module_name,
                    status="failed",
                    execution_time=execution_time,
                    error_message="Neo4j数据库未运行",
                    recommendations=["启动Neo4j数据库", "检查Docker容器", "验证数据库配置"]
                ))
        except Exception as e:
            results.append(TestResult(
                test_name="neo4j_database_connection", 
                module_name=module_name,
                status="error",
                execution_time=0,
                error_message=f"数据库连接检查失败: {str(e)}",
                recommendations=["检查网络连接", "验证端口配置", "确认数据库状态"]
            ))
        
        # 启动仪表板服务器
        dashboard_server_path = self.project_root / "neo4j_dashboard_server.py"
        if dashboard_server_path.exists():
            process = self.start_server_process(module_name, "neo4j_dashboard_server.py", 5001)
            
            if process:
                await asyncio.sleep(3)
                
                # 测试API端点
                api_tests = [
                    "/api/overview",
                    "/api/competitors", 
                    "/api/keywords/opportunities"
                ]
                
                for endpoint in api_tests:
                    try:
                        start_time = time.time()
                        response = requests.get(f"http://127.0.0.1:5001{endpoint}", timeout=10)
                        execution_time = time.time() - start_time
                        
                        if response.status_code == 200:
                            results.append(TestResult(
                                test_name=f"neo4j_api_{endpoint.replace('/', '_').replace(':', '_')}",
                                module_name=module_name,
                                status="passed",
                                execution_time=execution_time,
                                details={"endpoint": endpoint, "status_code": response.status_code}
                            ))
                        else:
                            results.append(TestResult(
                                test_name=f"neo4j_api_{endpoint.replace('/', '_').replace(':', '_')}",
                                module_name=module_name,
                                status="failed", 
                                execution_time=execution_time,
                                error_message=f"API响应错误: {response.status_code}",
                                recommendations=["检查数据库查询", "验证API实现", "确认数据存在"]
                            ))
                    except Exception as e:
                        results.append(TestResult(
                            test_name=f"neo4j_api_{endpoint.replace('/', '_').replace(':', '_')}",
                            module_name=module_name,
                            status="error",
                            execution_time=0,
                            error_message=f"API测试失败: {str(e)}",
                            recommendations=["检查服务器状态", "验证网络连接", "确认API可用性"]
                        ))
            else:
                results.append(TestResult(
                    test_name="neo4j_server_startup",
                    module_name=module_name,
                    status="failed",
                    execution_time=0,
                    error_message="Neo4j仪表板服务器启动失败", 
                    recommendations=["检查Python环境", "安装缺失依赖", "验证文件权限"]
                ))
        else:
            results.append(TestResult(
                test_name="neo4j_server_file_check",
                module_name=module_name,
                status="failed",
                execution_time=0,
                error_message="Neo4j仪表板服务器文件不存在",
                recommendations=["检查文件路径", "确认文件完整性", "重新创建服务器文件"]
            ))
        
        return results
    
    async def test_html_dashboards(self) -> List[TestResult]:
        """测试HTML仪表板"""
        results = []
        module_name = "html_dashboards"
        
        html_files = [
            "eufy-seo-dashboard.html",
            "neo4j-seo-dashboard.html", 
            "eufy-seo-battle-dashboard.html",
            "eufy-geo-content-strategy.html"
        ]
        
        # 启动HTTP服务器
        process = self.start_server_process("html_server", "eufy-seo-dashboard.html", 8000)
        
        if not process:
            results.append(TestResult(
                test_name="html_server_startup",
                module_name=module_name,
                status="failed",
                execution_time=0,
                error_message="HTML服务器启动失败",
                recommendations=["检查端口占用", "验证Python HTTP服务器", "确认文件权限"]
            ))
            return results
        
        await asyncio.sleep(2)
        
        # 测试每个HTML文件
        for html_file in html_files:
            file_path = self.project_root / html_file
            if not file_path.exists():
                results.append(TestResult(
                    test_name=f"file_existence_{html_file.replace('.html', '').replace('-', '_')}",
                    module_name=module_name,
                    status="failed",
                    execution_time=0,
                    error_message=f"HTML文件不存在: {html_file}",
                    recommendations=["检查文件路径", "确认文件完整性", "重新创建HTML文件"]
                ))
                continue
            
            # 浏览器测试
            if self.context:
                try:
                    page = await self.context.new_page()
                    start_time = time.time()
                    
                    await page.goto(f"http://127.0.0.1:8000/{html_file}", 
                                   wait_until='networkidle', timeout=15000)
                    execution_time = time.time() - start_time
                    
                    # 检查页面标题
                    title = await page.title()
                    
                    # 检查是否有ECharts图表
                    chart_elements = await page.query_selector_all('div[id*="chart"], div[class*="chart"]')
                    
                    # 检查是否有JavaScript错误
                    js_errors = []
                    page.on('console', lambda msg: js_errors.append(msg.text) if msg.type == 'error' else None)
                    
                    await asyncio.sleep(2)  # 等待JavaScript执行
                    
                    if title and len(chart_elements) > 0 and len(js_errors) == 0:
                        results.append(TestResult(
                            test_name=f"html_page_{html_file.replace('.html', '').replace('-', '_')}",
                            module_name=module_name,
                            status="passed",
                            execution_time=execution_time,
                            details={
                                "title": title,
                                "chart_elements": len(chart_elements),
                                "js_errors": len(js_errors)
                            },
                            screenshot_path=await self.take_screenshot(page, f"html_{html_file.replace('.html', '')}")
                        ))
                    else:
                        error_messages = []
                        if not title:
                            error_messages.append("页面标题为空")
                        if len(chart_elements) == 0:
                            error_messages.append("未找到图表元素")
                        if len(js_errors) > 0:
                            error_messages.append(f"JavaScript错误: {js_errors}")
                        
                        results.append(TestResult(
                            test_name=f"html_page_{html_file.replace('.html', '').replace('-', '_')}",
                            module_name=module_name,
                            status="failed",
                            execution_time=execution_time,
                            error_message="; ".join(error_messages),
                            recommendations=["检查HTML结构", "验证JavaScript加载", "确认CSS样式", "修复图表初始化"],
                            screenshot_path=await self.take_screenshot(page, f"html_{html_file.replace('.html', '')}_failed")
                        ))
                    
                    await page.close()
                    
                except Exception as e:
                    results.append(TestResult(
                        test_name=f"html_page_{html_file.replace('.html', '').replace('-', '_')}",
                        module_name=module_name,
                        status="error",
                        execution_time=0,
                        error_message=f"页面测试失败: {str(e)}",
                        recommendations=["检查页面加载", "验证网络连接", "确认服务器状态"]
                    ))
        
        return results
    
    def cleanup_processes(self):
        """清理所有启动的进程"""
        for module_name, process in self.running_processes:
            try:
                process.terminate()
                process.wait(timeout=5)
                logger.info(f"✅ {module_name} 进程已终止")
            except subprocess.TimeoutExpired:
                process.kill()
                logger.warning(f"⚠️ {module_name} 进程强制终止")
            except Exception as e:
                logger.error(f"❌ 清理 {module_name} 进程失败: {e}")
        
        self.running_processes.clear()
    
    def generate_test_report(self) -> str:
        """生成测试报告"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "passed"])
        failed_tests = len([r for r in self.test_results if r.status == "failed"])
        error_tests = len([r for r in self.test_results if r.status == "error"])
        
        report = f"""
🎯 EufyGeo2 项目综合功能验证测试报告
====================================

📊 测试概览:
- 总测试数: {total_tests}
- ✅ 通过: {passed_tests} ({passed_tests/total_tests*100:.1f}%)
- ❌ 失败: {failed_tests} ({failed_tests/total_tests*100:.1f}%)
- 🚫 错误: {error_tests} ({error_tests/total_tests*100:.1f}%)

📋 详细结果:
"""
        
        # 按模块分组显示结果
        modules = {}
        for result in self.test_results:
            if result.module_name not in modules:
                modules[result.module_name] = []
            modules[result.module_name].append(result)
        
        for module_name, results in modules.items():
            module_passed = len([r for r in results if r.status == "passed"])
            module_total = len(results)
            
            report += f"\n🔧 {module_name} ({module_passed}/{module_total} 通过):\n"
            
            for result in results:
                status_emoji = {"passed": "✅", "failed": "❌", "error": "🚫"}[result.status]
                report += f"  {status_emoji} {result.test_name} ({result.execution_time:.2f}s)"
                
                if result.error_message:
                    report += f"\n    错误: {result.error_message}"
                
                if result.recommendations:
                    report += f"\n    建议: {'; '.join(result.recommendations)}"
                
                if result.screenshot_path:
                    report += f"\n    截图: {result.screenshot_path}"
                
                report += "\n"
        
        # 总结和建议
        report += f"\n🎯 总结与建议:\n"
        
        critical_issues = [r for r in self.test_results if r.status in ["failed", "error"]]
        if critical_issues:
            report += "\n⚠️ 需要立即修复的问题:\n"
            for issue in critical_issues[:10]:  # 只显示前10个关键问题
                report += f"  - {issue.module_name}: {issue.test_name} - {issue.error_message}\n"
        
        # 按优先级给出改进建议
        all_recommendations = []
        for result in self.test_results:
            if result.recommendations:
                all_recommendations.extend(result.recommendations)
        
        unique_recommendations = list(set(all_recommendations))
        if unique_recommendations:
            report += "\n💡 改进建议 (按重要性排序):\n"
            for i, rec in enumerate(unique_recommendations[:15], 1):
                report += f"  {i}. {rec}\n"
        
        return report
    
    async def run_comprehensive_tests(self):
        """运行综合测试"""
        try:
            logger.info("🚀 开始EufyGeo2项目综合功能验证测试")
            
            # 初始化浏览器
            await self.setup_browser()
            
            # 运行各模块测试
            test_functions = [
                ("AI搜索优化模块", self.test_ai_search_optimization_module),
                ("社交内容优化工具", self.test_social_content_optimizer),
                ("电商AI导购系统", self.test_ecommerce_ai_optimizer),
                ("私域AI客服系统", self.test_private_domain_service),
                ("四大触点监控系统", self.test_integrated_monitoring_system),
                ("Neo4j仪表板系统", self.test_neo4j_dashboard_system),
                ("HTML仪表板界面", self.test_html_dashboards)
            ]
            
            for test_name, test_func in test_functions:
                logger.info(f"📋 正在测试: {test_name}")
                try:
                    results = await test_func()
                    self.test_results.extend(results)
                    logger.info(f"✅ {test_name} 测试完成，共 {len(results)} 个测试用例")
                except Exception as e:
                    logger.error(f"❌ {test_name} 测试失败: {e}")
                    self.test_results.append(TestResult(
                        test_name="module_test_execution",
                        module_name=test_name.lower().replace(" ", "_"),
                        status="error",
                        execution_time=0,
                        error_message=f"测试执行失败: {str(e)}",
                        recommendations=["检查测试环境", "验证依赖安装", "修复代码错误"]
                    ))
            
            # 生成测试报告
            report = self.generate_test_report()
            
            # 保存报告到文件
            report_file = self.project_root / f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"📄 测试报告已保存到: {report_file}")
            print(report)
            
        except Exception as e:
            logger.error(f"❌ 综合测试执行失败: {e}")
        finally:
            # 清理资源
            await self.cleanup_browser()
            self.cleanup_processes()
            logger.info("🧹 测试环境清理完成")

async def main():
    """主函数"""
    test_suite = ComprehensiveTestSuite()
    await test_suite.run_comprehensive_tests()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("🛑 测试被用户中断")
    except Exception as e:
        logger.error(f"❌ 程序执行失败: {e}")