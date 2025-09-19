#!/usr/bin/env python3
"""
Quick Validation Test for Eufy GEO Project
Focused testing of key components with efficient execution
"""

import asyncio
import os
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright
import json

async def main():
    """Quick validation of key components"""
    print("🚀 Starting Eufy GEO Project Quick Validation...")
    
    base_url = "http://localhost:8080"
    results = {
        "timestamp": datetime.now().isoformat(),
        "tests": []
    }
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 1920, 'height': 1080})
        
        # Test key pages
        key_pages = [
            ("index.html", "Main Portal"),
            ("eufy-seo-dashboard.html", "SEO Dashboard"),
            ("eufy-seo-battle-dashboard.html", "Battle Dashboard"),
            ("eufy-geo-content-strategy.html", "GEO Strategy"),
            ("eufy-vs-arlo-vs-ring-comparison.html", "Brand Comparison"),
            ("neo4j-seo-dashboard.html", "Neo4j Dashboard")
        ]
        
        for page_file, page_name in key_pages:
            page = await context.new_page()
            try:
                print(f"📄 Testing {page_name}...")
                await page.goto(f"{base_url}/{page_file}")
                await page.wait_for_load_state('networkidle', timeout=10000)
                
                # Basic page validation
                title = await page.title()
                body_content = await page.locator('body').text_content()
                
                # Take screenshot
                screenshot_path = f"test-screenshots/validation_{page_file.replace('.html', '')}.png"
                await page.screenshot(path=screenshot_path, full_page=True)
                
                # Check for key elements
                has_content = len(body_content.strip()) > 100
                has_scripts = await page.locator('script').count() > 0
                has_styles = await page.locator('style, link[rel="stylesheet"]').count() > 0
                
                result = {
                    "page": page_name,
                    "file": page_file,
                    "status": "PASS" if has_content else "FAIL",
                    "title": title,
                    "content_length": len(body_content),
                    "has_scripts": has_scripts,
                    "has_styles": has_styles,
                    "screenshot": screenshot_path
                }
                
                results["tests"].append(result)
                print(f"  ✅ {page_name}: Title='{title}', Content={len(body_content)} chars")
                
            except Exception as e:
                result = {
                    "page": page_name,
                    "file": page_file,
                    "status": "FAIL",
                    "error": str(e)
                }
                results["tests"].append(result)
                print(f"  ❌ {page_name}: {str(e)}")
            finally:
                await page.close()
        
        await browser.close()
    
    # File structure validation
    print("\n📁 Validating File Structure...")
    
    key_files = [
        "CLAUDE.md",
        "README.md", 
        "package.json",
        "requirements.txt",
        "neo4j_dashboard_server.py",
        "content_optimization_engine.py",
        "GEO_CONTENT_OPTIMIZATION_TEMPLATES.md"
    ]
    
    file_results = []
    for file_name in key_files:
        exists = Path(file_name).exists()
        file_results.append({"file": file_name, "exists": exists})
        print(f"  {'✅' if exists else '❌'} {file_name}")
    
    results["file_structure"] = file_results
    
    # Directory validation
    print("\n📂 Validating Directory Structure...")
    
    key_dirs = [
        "Context-Engineering-Intro",
        "tests",
        "src", 
        "docs",
        "db"
    ]
    
    dir_results = []
    for dir_name in key_dirs:
        exists = Path(dir_name).exists() and Path(dir_name).is_dir()
        dir_results.append({"directory": dir_name, "exists": exists})
        print(f"  {'✅' if exists else '❌'} {dir_name}/")
    
    results["directory_structure"] = dir_results
    
    # Generate summary
    page_tests = results["tests"]
    passed_pages = len([t for t in page_tests if t.get("status") == "PASS"])
    total_pages = len(page_tests)
    
    file_tests = results["file_structure"] 
    existing_files = len([f for f in file_tests if f["exists"]])
    total_files = len(file_tests)
    
    dir_tests = results["directory_structure"]
    existing_dirs = len([d for d in dir_tests if d["exists"]])
    total_dirs = len(dir_tests)
    
    print(f"\n{'='*50}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*50}")
    print(f"📄 Pages: {passed_pages}/{total_pages} working")
    print(f"📁 Files: {existing_files}/{total_files} present")
    print(f"📂 Directories: {existing_dirs}/{total_dirs} present")
    
    overall_score = ((passed_pages/total_pages + existing_files/total_files + existing_dirs/total_dirs) / 3) * 100
    print(f"🎯 Overall Score: {overall_score:.1f}%")
    
    if overall_score >= 80:
        print("🟢 Project Status: EXCELLENT - Ready for production")
    elif overall_score >= 60:
        print("🟡 Project Status: GOOD - Minor issues to address")
    else:
        print("🔴 Project Status: NEEDS WORK - Several critical issues")
    
    # Save detailed results
    with open("validation-results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📋 Detailed results saved to: validation-results.json")
    print(f"🖼️  Screenshots saved to: test-screenshots/")
    
    return results

if __name__ == "__main__":
    # Ensure screenshots directory exists
    Path("test-screenshots").mkdir(exist_ok=True)
    
    # Run validation
    results = asyncio.run(main())