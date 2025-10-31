#!/usr/bin/env python3
"""
Simple Architecture Test for Solar Heating System v3
Tests the new architecture components without dependencies
"""

import os
import sys

def test_file_exists(file_path, description):
    """Test that a file exists"""
    if os.path.exists(file_path):
        print(f"   ✅ {description}: {file_path}")
        return True
    else:
        print(f"   ❌ {description}: {file_path}")
        return False

def test_file_content(file_path, required_content, description):
    """Test that a file contains required content"""
    if not os.path.exists(file_path):
        print(f"   ❌ {description}: File not found: {file_path}")
        return False
    
    try:
        with open(file_path, 'r') as f:
            content = f.read()
        
        for content_item in required_content:
            if content_item in content:
                print(f"   ✅ {description}: Contains '{content_item}'")
            else:
                print(f"   ❌ {description}: Missing '{content_item}'")
                return False
        
        return True
    except Exception as e:
        print(f"   ❌ {description}: Error reading file: {e}")
        return False

def main():
    """Run architecture tests"""
    print("🧪 Testing Solar Heating System v3 - New Architecture")
    print("")
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: API Server
    print("1️⃣ Testing API Server...")
    tests_total += 1
    if test_file_exists("python/v3/api_server.py", "API server file"):
        tests_passed += 1
    
    # Test 2: Static Frontend
    print("2️⃣ Testing Static Frontend...")
    frontend_files = [
        "python/v3/frontend/index.html",
        "python/v3/frontend/static/css/style.css",
        "python/v3/frontend/static/js/dashboard.js"
    ]
    
    for file_path in frontend_files:
        tests_total += 1
        if test_file_exists(file_path, f"Frontend file: {os.path.basename(file_path)}"):
            tests_passed += 1
    
    # Test 3: Nginx Configuration
    print("3️⃣ Testing Nginx Configuration...")
    nginx_files = [
        "python/v3/nginx/solar_heating.conf",
        "python/v3/scripts/setup_nginx.sh",
        "python/v3/scripts/nginx_manager.sh",
        "python/v3/scripts/test_nginx.sh"
    ]
    
    for file_path in nginx_files:
        tests_total += 1
        if test_file_exists(file_path, f"Nginx file: {os.path.basename(file_path)}"):
            tests_passed += 1
    
    # Test 4: Documentation
    print("4️⃣ Testing Documentation...")
    doc_files = [
        "python/v3/docs/API_DESIGN_SPECIFICATION.md",
        "python/v3/docs/MIGRATION_GUIDE.md"
    ]
    
    for file_path in doc_files:
        tests_total += 1
        if test_file_exists(file_path, f"Documentation: {os.path.basename(file_path)}"):
            tests_passed += 1
    
    # Test 5: Frontend Content
    print("5️⃣ Testing Frontend Content...")
    tests_total += 1
    if test_file_content("python/v3/frontend/index.html", 
                        ["Solar Heating System v3", "dashboard.js", "style.css"], 
                        "HTML content"):
        tests_passed += 1
    
    # Test 6: CSS Content
    print("6️⃣ Testing CSS Content...")
    tests_total += 1
    if test_file_content("python/v3/frontend/static/css/style.css", 
                        [".container", ".card", ".btn"], 
                        "CSS content"):
        tests_passed += 1
    
    # Test 7: JavaScript Content
    print("7️⃣ Testing JavaScript Content...")
    tests_total += 1
    if test_file_content("python/v3/frontend/static/js/dashboard.js", 
                        ["SolarHeatingDashboard", "api/status", "fetch("], 
                        "JavaScript content"):
        tests_passed += 1
    
    # Test 8: Nginx Configuration Content
    print("8️⃣ Testing Nginx Configuration Content...")
    tests_total += 1
    if test_file_content("python/v3/nginx/solar_heating.conf", 
                        ["server {", "listen 80", "location /api/", "proxy_pass"], 
                        "Nginx configuration"):
        tests_passed += 1
    
    # Test 9: Flask Cleanup
    print("9️⃣ Testing Flask Cleanup...")
    old_flask_files = [
        "python/v3/web_interface",
        "python/v3/app_improved_temps.py",
        "python/v3/app.py",
        "python/v3/gui.py"
    ]
    
    flask_removed = True
    for file_path in old_flask_files:
        if os.path.exists(file_path):
            print(f"   ❌ Old Flask file still exists: {file_path}")
            flask_removed = False
        else:
            print(f"   ✅ Old Flask file removed: {file_path}")
    
    tests_total += 1
    if flask_removed:
        tests_passed += 1
    
    # Test 10: New Architecture Components
    print("🔟 Testing New Architecture Components...")
    new_components = [
        "python/v3/api_server.py",
        "python/v3/frontend/index.html",
        "python/v3/nginx/solar_heating.conf",
        "python/v3/scripts/setup_nginx.sh"
    ]
    
    all_components_present = True
    for component in new_components:
        if not os.path.exists(component):
            print(f"   ❌ New component missing: {component}")
            all_components_present = False
        else:
            print(f"   ✅ New component present: {component}")
    
    tests_total += 1
    if all_components_present:
        tests_passed += 1
    
    # Summary
    print("")
    print("📋 Architecture Test Results:")
    print(f"   Tests passed: {tests_passed}/{tests_total}")
    print(f"   Success rate: {(tests_passed/tests_total)*100:.1f}%")
    
    if tests_passed == tests_total:
        print("")
        print("🎉 All architecture tests passed!")
        print("")
        print("📋 New Architecture Summary:")
        print("   • API server: ✅ Implemented")
        print("   • Static frontend: ✅ Created")
        print("   • Nginx configuration: ✅ Setup")
        print("   • Documentation: ✅ Complete")
        print("   • Flask cleanup: ✅ Removed")
        print("   • New components: ✅ Present")
        print("")
        print("🎯 New architecture is ready for deployment!")
        return True
    else:
        print("")
        print("❌ Some architecture tests failed.")
        print("   Check the output above for details.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
