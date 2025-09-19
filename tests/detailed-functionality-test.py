#!/usr/bin/env python3
"""
Detailed Functionality Test for Eufy GEO Project
In-depth testing of interactive features and data integration
"""

import asyncio
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import json

async def test_interactive_features():
    """Test interactive features and functionality"""
    print("🔍 Starting Detailed Functionality Tests...")
    
    base_url = "http://localhost:8080"
    test_results = {
        "timestamp": datetime.now().isoformat(),
        "interactive_tests": [],
        "data_validation": [],
        "ui_components": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=500)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # Test Main Portal Navigation
        print("🏠 Testing Main Portal Navigation...")
        page = await context.new_page()
        try:
            await page.goto(f"{base_url}/index.html")
            await page.wait_for_load_state('networkidle')
            
            # Screenshot of main portal
            await page.screenshot(path="test-screenshots/portal_main_full.png", full_page=True)
            
            # Test navigation links
            nav_links = await page.locator('a[href*=".html"], .nav-link, .dashboard-link').all()
            print(f"  Found {len(nav_links)} navigation links")
            
            # Test responsive design
            await page.set_viewport_size({"width": 375, "height": 667})  # Mobile
            await page.screenshot(path="test-screenshots/portal_mobile.png", full_page=True)
            
            await page.set_viewport_size({"width": 768, "height": 1024})  # Tablet
            await page.screenshot(path="test-screenshots/portal_tablet.png", full_page=True)
            
            await page.set_viewport_size({"width": 1920, "height": 1080})  # Desktop
            
            test_results["interactive_tests"].append({
                "component": "Portal Navigation",
                "status": "PASS",
                "details": f"Found {len(nav_links)} navigation elements"
            })
            
        except Exception as e:
            test_results["interactive_tests"].append({
                "component": "Portal Navigation", 
                "status": "FAIL",
                "error": str(e)
            })
        finally:
            await page.close()
        
        # Test SEO Dashboard Functionality
        print("📊 Testing SEO Dashboard Features...")
        page = await context.new_page()
        try:
            await page.goto(f"{base_url}/eufy-seo-dashboard.html")
            await page.wait_for_load_state('networkidle')
            
            # Take detailed screenshots
            await page.screenshot(path="test-screenshots/seo_dashboard_full.png", full_page=True)
            
            # Check for charts and interactive elements
            charts = await page.locator('.chart, canvas, svg, [id*="chart"], [class*="chart"]').count()
            buttons = await page.locator('button, .btn, input[type="button"]').count()
            dropdowns = await page.locator('select, .dropdown, .select').count()
            
            # Test ECharts integration
            try:
                echarts_version = await page.evaluate("typeof echarts !== 'undefined' ? echarts.version : 'not loaded'")
            except:
                echarts_version = "not detected"
            
            test_results["ui_components"].append({
                "dashboard": "SEO Dashboard",
                "charts": charts,
                "buttons": buttons,
                "dropdowns": dropdowns,
                "echarts": echarts_version
            })
            
            print(f"  Charts: {charts}, Buttons: {buttons}, Dropdowns: {dropdowns}")
            print(f"  ECharts: {echarts_version}")
            
        except Exception as e:
            test_results["interactive_tests"].append({
                "component": "SEO Dashboard",
                "status": "FAIL", 
                "error": str(e)
            })
        finally:
            await page.close()
        
        # Test Battle Dashboard
        print("⚔️ Testing Battle Dashboard...")
        page = await context.new_page()
        try:
            await page.goto(f"{base_url}/eufy-seo-battle-dashboard.html")
            await page.wait_for_load_state('networkidle')
            
            await page.screenshot(path="test-screenshots/battle_dashboard_detailed.png", full_page=True)
            
            # Look for competitor comparison elements
            competitors = await page.locator(':has-text("arlo"), :has-text("ring"), :has-text("wyze")').count()
            battle_elements = await page.locator('.battle, .vs, .comparison, .competitor').count()
            
            test_results["data_validation"].append({
                "dashboard": "Battle Dashboard",
                "competitor_mentions": competitors,
                "battle_elements": battle_elements
            })
            
            print(f"  Competitor mentions: {competitors}, Battle elements: {battle_elements}")
            
        except Exception as e:
            test_results["interactive_tests"].append({
                "component": "Battle Dashboard",
                "status": "FAIL",
                "error": str(e)
            })
        finally:
            await page.close()
        
        # Test GEO Content Strategy
        print("🌍 Testing GEO Content Strategy...")
        page = await context.new_page()
        try:
            await page.goto(f"{base_url}/eufy-geo-content-strategy.html")
            await page.wait_for_load_state('networkidle')
            
            await page.screenshot(path="test-screenshots/geo_strategy_detailed.png", full_page=True)
            
            # Check for GEO-specific elements
            geo_elements = await page.locator('[data-geo], .geo, .location, .region').count()
            content_tools = await page.locator('.content, .template, .strategy, .optimization').count()
            
            test_results["data_validation"].append({
                "dashboard": "GEO Content Strategy",
                "geo_elements": geo_elements,
                "content_tools": content_tools
            })
            
            print(f"  GEO elements: {geo_elements}, Content tools: {content_tools}")
            
        except Exception as e:
            test_results["interactive_tests"].append({
                "component": "GEO Content Strategy",
                "status": "FAIL",
                "error": str(e)
            })
        finally:
            await page.close()
        
        # Test Brand Comparison Page
        print("🔍 Testing Brand Comparison Features...")
        page = await context.new_page()
        try:
            await page.goto(f"{base_url}/eufy-vs-arlo-vs-ring-comparison.html")
            await page.wait_for_load_state('networkidle')
            
            await page.screenshot(path="test-screenshots/comparison_detailed.png", full_page=True)
            
            # Check for structured data
            schema_scripts = await page.locator('script[type="application/ld+json"]').count()
            comparison_tables = await page.locator('table, .comparison-table, .vs-table').count()
            brand_mentions = {
                "eufy": await page.locator(':has-text("eufy")').count(),
                "arlo": await page.locator(':has-text("arlo")').count(), 
                "ring": await page.locator(':has-text("ring")').count()
            }
            
            test_results["data_validation"].append({
                "page": "Brand Comparison",
                "schema_markup": schema_scripts,
                "comparison_tables": comparison_tables,
                "brand_mentions": brand_mentions
            })
            
            print(f"  Schema markup: {schema_scripts}, Tables: {comparison_tables}")
            print(f"  Brand mentions: {brand_mentions}")
            
        except Exception as e:
            test_results["interactive_tests"].append({
                "component": "Brand Comparison",
                "status": "FAIL",
                "error": str(e)
            })
        finally:
            await page.close()
        
        # Test Neo4j Dashboard
        print("🔗 Testing Neo4j Graph Dashboard...")
        page = await context.new_page()
        try:
            await page.goto(f"{base_url}/neo4j-seo-dashboard.html")
            await page.wait_for_load_state('networkidle')
            
            await page.screenshot(path="test-screenshots/neo4j_dashboard_detailed.png", full_page=True)
            
            # Check for graph-related elements
            graph_elements = await page.locator('.graph, .network, .node, .edge, [id*="graph"]').count()
            query_elements = await page.locator('.query, .cypher, textarea, .code').count()
            
            test_results["data_validation"].append({
                "dashboard": "Neo4j Graph Dashboard",
                "graph_elements": graph_elements,
                "query_elements": query_elements
            })
            
            print(f"  Graph elements: {graph_elements}, Query elements: {query_elements}")
            
        except Exception as e:
            test_results["interactive_tests"].append({
                "component": "Neo4j Dashboard",
                "status": "FAIL",
                "error": str(e)
            })
        finally:
            await page.close()
        
        await browser.close()
    
    # Test API Server Files
    print("🔧 Testing Backend Components...")
    
    # Check Python server files
    server_files = [
        "neo4j_dashboard_server.py",
        "eufy-seo-dashboard-server.py", 
        "content_optimization_engine.py"
    ]
    
    for server_file in server_files:
        if Path(server_file).exists():
            try:
                with open(server_file, 'r') as f:
                    content = f.read()
                    has_flask = 'flask' in content.lower() or 'app.run' in content.lower()
                    has_api_routes = 'route' in content.lower() or 'api' in content.lower()
                    
                    test_results["data_validation"].append({
                        "component": f"Server - {server_file}",
                        "has_flask": has_flask,
                        "has_api_routes": has_api_routes,
                        "file_size": len(content)
                    })
                    
                    print(f"  {server_file}: Flask={has_flask}, API routes={has_api_routes}")
            except Exception as e:
                print(f"  {server_file}: Error reading file - {str(e)}")
    
    # Generate comprehensive report
    print("\n" + "="*60)
    print("🏆 DETAILED FUNCTIONALITY TEST RESULTS")
    print("="*60)
    
    # Count successes
    successful_tests = len([t for t in test_results["interactive_tests"] if t.get("status") == "PASS"])
    total_interactive_tests = len(test_results["interactive_tests"])
    
    print(f"📋 Interactive Tests: {successful_tests}/{total_interactive_tests} passed")
    print(f"📊 UI Components Tested: {len(test_results['ui_components'])}")
    print(f"📈 Data Validations: {len(test_results['data_validation'])}")
    
    # Save results
    with open("detailed-functionality-results.json", "w") as f:
        json.dump(test_results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: detailed-functionality-results.json")
    print(f"📸 Enhanced screenshots saved to: test-screenshots/")
    
    return test_results

if __name__ == "__main__":
    # Ensure screenshots directory exists
    Path("test-screenshots").mkdir(exist_ok=True)
    
    # Run detailed tests
    results = asyncio.run(test_interactive_features())