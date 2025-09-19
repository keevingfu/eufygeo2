#!/usr/bin/env python3
"""
Playwright test script to verify Neo4j dashboard functionality
Tests both the dashboard interface and Neo4j data access
"""

import asyncio
from playwright.async_api import async_playwright
import json

async def test_neo4j_browser():
    """Test Neo4j Browser access"""
    print("🔍 Testing Neo4j Browser...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Navigate to Neo4j Browser
        await page.goto('http://localhost:7474')
        await page.wait_for_load_state('networkidle')
        
        # Take screenshot
        await page.screenshot(path='neo4j-browser.png')
        print("✅ Neo4j Browser screenshot saved as neo4j-browser.png")
        
        # Check if login form exists
        try:
            await page.wait_for_selector('input[type="text"]', timeout=5000)
            print("✅ Neo4j Browser login page loaded successfully")
            
            # Try to login
            await page.fill('input[type="text"]', 'neo4j')
            await page.fill('input[type="password"]', 'eufyseo2024')
            await page.click('button[type="submit"]')
            
            # Wait for main interface
            await page.wait_for_selector('.monaco-editor', timeout=10000)
            print("✅ Successfully logged into Neo4j Browser")
            
            # Take screenshot of main interface
            await page.screenshot(path='neo4j-browser-main.png')
            print("✅ Neo4j Browser main interface screenshot saved")
            
        except Exception as e:
            print(f"⚠️ Could not complete Neo4j Browser test: {e}")
        
        await browser.close()

async def test_dashboard_api():
    """Test dashboard API endpoints"""
    print("\n🔍 Testing Dashboard API endpoints...")
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()
        page = await context.new_page()
        
        # Test overview endpoint
        response = await page.goto('http://localhost:5001/api/overview')
        if response.ok:
            data = await response.json()
            print(f"✅ Overview API: {json.dumps(data, indent=2)}")
        else:
            print(f"❌ Overview API failed: {response.status}")
        
        # Test competitors endpoint
        response = await page.goto('http://localhost:5001/api/competitors')
        if response.ok:
            data = await response.json()
            print(f"✅ Competitors API: Found {len(data)} competitors")
            if data:
                print(f"   Top competitor: {data[0]['competitor']} with {data[0]['keyword_count']} keywords")
        else:
            print(f"❌ Competitors API failed: {response.status}")
        
        # Test keyword opportunities endpoint
        response = await page.goto('http://localhost:5001/api/keyword-opportunities?min_volume=1000&max_difficulty=50')
        if response.ok:
            data = await response.json()
            print(f"✅ Keyword Opportunities API: Found {len(data)} opportunities")
            if data:
                print(f"   Top opportunity: {data[0]['keyword']} (volume: {data[0]['volume']})")
        else:
            print(f"❌ Keyword Opportunities API failed: {response.status}")
        
        await browser.close()

async def test_dashboard_interface():
    """Test the dashboard HTML interface"""
    print("\n🔍 Testing Dashboard Interface...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)
        context = await browser.new_context()
        page = await context.new_page()
        
        # Test main SEO dashboard
        dashboard_file = 'file:///Users/cavin/Desktop/dev/eufygeo2/eufy-seo-dashboard.html'
        await page.goto(dashboard_file)
        await page.wait_for_load_state('networkidle')
        
        print("✅ Dashboard loaded successfully")
        
        # Wait for data to load
        await page.wait_for_timeout(3000)
        
        # Take screenshot
        await page.screenshot(path='dashboard-main.png', full_page=True)
        print("✅ Dashboard screenshot saved as dashboard-main.png")
        
        # Check for key elements
        try:
            # Check for overview cards
            overview_cards = await page.query_selector_all('.metric-card')
            print(f"✅ Found {len(overview_cards)} overview metric cards")
            
            # Check for charts
            charts = await page.query_selector_all('.chart-container')
            print(f"✅ Found {len(charts)} chart containers")
            
            # Check if data is loaded
            keyword_count = await page.text_content('#totalKeywords')
            if keyword_count and keyword_count != '-':
                print(f"✅ Total keywords displayed: {keyword_count}")
            
            # Test tab switching
            tabs = await page.query_selector_all('.tab-button')
            for i, tab in enumerate(tabs):
                await tab.click()
                await page.wait_for_timeout(1000)
                tab_text = await tab.text_content()
                print(f"✅ Tab '{tab_text}' is clickable")
                
        except Exception as e:
            print(f"⚠️ Error checking dashboard elements: {e}")
        
        # Test Neo4j SEO Dashboard
        print("\n🔍 Testing Neo4j SEO Dashboard...")
        neo4j_dashboard_file = 'file:///Users/cavin/Desktop/dev/eufygeo2/neo4j-seo-dashboard.html'
        await page.goto(neo4j_dashboard_file)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)
        
        await page.screenshot(path='neo4j-dashboard.png', full_page=True)
        print("✅ Neo4j dashboard screenshot saved as neo4j-dashboard.png")
        
        # Test Battle Dashboard
        print("\n🔍 Testing Battle Dashboard...")
        battle_dashboard_file = 'file:///Users/cavin/Desktop/dev/eufygeo2/eufy-seo-battle-dashboard.html'
        await page.goto(battle_dashboard_file)
        await page.wait_for_load_state('networkidle')
        await page.wait_for_timeout(3000)
        
        await page.screenshot(path='battle-dashboard.png', full_page=True)
        print("✅ Battle dashboard screenshot saved as battle-dashboard.png")
        
        await browser.close()

async def main():
    """Run all tests"""
    print("🚀 Starting Playwright tests for Neo4j SEO Dashboard\n")
    
    # Test API endpoints first
    await test_dashboard_api()
    
    # Test Neo4j Browser
    await test_neo4j_browser()
    
    # Test dashboard interfaces
    await test_dashboard_interface()
    
    print("\n✅ All tests completed!")
    print("📸 Screenshots saved:")
    print("   - neo4j-browser.png")
    print("   - neo4j-browser-main.png")
    print("   - dashboard-main.png")
    print("   - neo4j-dashboard.png")
    print("   - battle-dashboard.png")

if __name__ == "__main__":
    asyncio.run(main())