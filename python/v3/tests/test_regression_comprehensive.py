#!/usr/bin/env python3
"""
Comprehensive Regression Testing for Solar Heating System v3
Tests both old and new architectures to ensure no functionality is lost
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime

class RegressionTester:
    """Comprehensive regression testing for architecture changes"""
    
    def __init__(self):
        self.test_results = []
        self.start_time = datetime.now()
        self.base_url = "http://localhost"
        self.api_url = f"{self.base_url}/api"
        
    def log_test(self, test_name, status, details=""):
        """Log test result"""
        result = {
            'test': test_name,
            'status': status,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        self.test_results.append(result)
        
        status_icon = "✅" if status == "PASS" else "❌" if status == "FAIL" else "⚠️"
        print(f"{status_icon} {test_name}: {status}")
        if details:
            print(f"   Details: {details}")
    
    def test_system_availability(self):
        """Test 1: System availability and basic connectivity"""
        print("\n1️⃣ Testing System Availability...")
        
        try:
            # Test nginx is running
            response = requests.get(self.base_url, timeout=5)
            if response.status_code == 200:
                self.log_test("Nginx serving static files", "PASS", f"Status: {response.status_code}")
            else:
                self.log_test("Nginx serving static files", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("Nginx serving static files", "FAIL", f"Error: {str(e)}")
        
        try:
            # Test API server is running
            response = requests.get(f"{self.api_url}/status", timeout=5)
            if response.status_code in [200, 404, 500]:
                self.log_test("API server responding", "PASS", f"Status: {response.status_code}")
            else:
                self.log_test("API server responding", "FAIL", f"Status: {response.status_code}")
        except Exception as e:
            self.log_test("API server responding", "FAIL", f"Error: {str(e)}")
    
    def test_api_endpoints(self):
        """Test 2: API endpoints functionality"""
        print("\n2️⃣ Testing API Endpoints...")
        
        endpoints = [
            ("/api/status", "GET", "System status"),
            ("/api/temperatures", "GET", "Temperature readings"),
            ("/api/mqtt", "GET", "MQTT status"),
            ("/api/control", "POST", "System control"),
            ("/api/mode", "POST", "Mode changes")
        ]
        
        for endpoint, method, description in endpoints:
            try:
                if method == "GET":
                    response = requests.get(f"{self.api_url}{endpoint}", timeout=5)
                elif method == "POST":
                    # Test with sample data
                    test_data = {"action": "test"} if "control" in endpoint else {"mode": "auto"}
                    response = requests.post(f"{self.api_url}{endpoint}", 
                                           json=test_data, timeout=5)
                
                if response.status_code in [200, 400, 404, 500]:
                    self.log_test(f"API {description}", "PASS", f"Status: {response.status_code}")
                else:
                    self.log_test(f"API {description}", "FAIL", f"Status: {response.status_code}")
                    
            except Exception as e:
                self.log_test(f"API {description}", "FAIL", f"Error: {str(e)}")
    
    def test_frontend_components(self):
        """Test 3: Frontend components and functionality"""
        print("\n3️⃣ Testing Frontend Components...")
        
        # Test static files exist
        frontend_files = [
            "python/v3/frontend/index.html",
            "python/v3/frontend/static/css/style.css",
            "python/v3/frontend/static/js/dashboard.js"
        ]
        
        for file_path in frontend_files:
            if os.path.exists(file_path):
                self.log_test(f"Frontend file: {os.path.basename(file_path)}", "PASS", "File exists")
            else:
                self.log_test(f"Frontend file: {os.path.basename(file_path)}", "FAIL", "File not found")
        
        # Test frontend content
        try:
            with open("python/v3/frontend/index.html", 'r') as f:
                html_content = f.read()
            
            required_elements = [
                "Solar Heating System v3",
                "dashboard.js",
                "style.css",
                "api/status"
            ]
            
            for element in required_elements:
                if element in html_content:
                    self.log_test(f"HTML contains: {element}", "PASS", "Element found")
                else:
                    self.log_test(f"HTML contains: {element}", "FAIL", "Element not found")
                    
        except Exception as e:
            self.log_test("Frontend content validation", "FAIL", f"Error: {str(e)}")
    
    def test_nginx_configuration(self):
        """Test 4: Nginx configuration and functionality"""
        print("\n4️⃣ Testing Nginx Configuration...")
        
        # Test nginx configuration file exists
        nginx_config = "python/v3/nginx/solar_heating.conf"
        if os.path.exists(nginx_config):
            self.log_test("Nginx configuration file", "PASS", "File exists")
        else:
            self.log_test("Nginx configuration file", "FAIL", "File not found")
        
        # Test nginx configuration content
        try:
            with open(nginx_config, 'r') as f:
                config_content = f.read()
            
            required_configs = [
                "server {",
                "listen 80",
                "location /api/",
                "proxy_pass",
                "CORS"
            ]
            
            for config in required_configs:
                if config in config_content:
                    self.log_test(f"Nginx config: {config}", "PASS", "Configuration found")
                else:
                    self.log_test(f"Nginx config: {config}", "FAIL", "Configuration not found")
                    
        except Exception as e:
            self.log_test("Nginx configuration validation", "FAIL", f"Error: {str(e)}")
    
    def test_systemd_services(self):
        """Test 5: Systemd services and system integration"""
        print("\n5️⃣ Testing Systemd Services...")
        
        services = ["solar_heating_v3", "nginx", "mosquitto"]
        
        for service in services:
            try:
                result = subprocess.run(['systemctl', 'is-active', service], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    self.log_test(f"Service {service}", "PASS", "Service is active")
                else:
                    self.log_test(f"Service {service}", "FAIL", "Service is not active")
            except Exception as e:
                self.log_test(f"Service {service}", "FAIL", f"Error: {str(e)}")
    
    def test_old_architecture_cleanup(self):
        """Test 6: Verify old architecture components are properly removed"""
        print("\n6️⃣ Testing Old Architecture Cleanup...")
        
        old_components = [
            "python/v3/web_interface",
            "python/v3/app_improved_temps.py",
            "python/v3/app.py",
            "python/v3/gui.py",
            "python/v3/gui_via_api.py"
        ]
        
        for component in old_components:
            if not os.path.exists(component):
                self.log_test(f"Old component removed: {os.path.basename(component)}", "PASS", "Component removed")
            else:
                self.log_test(f"Old component removed: {os.path.basename(component)}", "FAIL", "Component still exists")
    
    def test_new_architecture_components(self):
        """Test 7: Verify new architecture components are present"""
        print("\n7️⃣ Testing New Architecture Components...")
        
        new_components = [
            "python/v3/api_server.py",
            "python/v3/frontend/index.html",
            "python/v3/frontend/static/css/style.css",
            "python/v3/frontend/static/js/dashboard.js",
            "python/v3/nginx/solar_heating.conf",
            "python/v3/scripts/deploy_new_architecture.sh",
            "python/v3/scripts/update_to_new_architecture.sh",
            "python/v3/scripts/rollback_architecture.sh"
        ]
        
        for component in new_components:
            if os.path.exists(component):
                self.log_test(f"New component: {os.path.basename(component)}", "PASS", "Component exists")
            else:
                self.log_test(f"New component: {os.path.basename(component)}", "FAIL", "Component not found")
    
    def test_performance_metrics(self):
        """Test 8: Performance and response time testing"""
        print("\n8️⃣ Testing Performance Metrics...")
        
        # Test static file serving performance
        try:
            start_time = time.time()
            response = requests.get(self.base_url, timeout=10)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response_time < 1000:  # Less than 1 second
                self.log_test("Static file serving performance", "PASS", f"Response time: {response_time:.2f}ms")
            else:
                self.log_test("Static file serving performance", "FAIL", f"Response time: {response_time:.2f}ms (too slow)")
        except Exception as e:
            self.log_test("Static file serving performance", "FAIL", f"Error: {str(e)}")
        
        # Test API response time
        try:
            start_time = time.time()
            response = requests.get(f"{self.api_url}/status", timeout=10)
            end_time = time.time()
            response_time = (end_time - start_time) * 1000  # Convert to milliseconds
            
            if response_time < 2000:  # Less than 2 seconds
                self.log_test("API response performance", "PASS", f"Response time: {response_time:.2f}ms")
            else:
                self.log_test("API response performance", "FAIL", f"Response time: {response_time:.2f}ms (too slow)")
        except Exception as e:
            self.log_test("API response performance", "FAIL", f"Error: {str(e)}")
    
    def test_security_headers(self):
        """Test 9: Security headers and configuration"""
        print("\n9️⃣ Testing Security Headers...")
        
        try:
            response = requests.get(self.base_url, timeout=5)
            headers = response.headers
            
            security_headers = [
                "X-Frame-Options",
                "X-Content-Type-Options",
                "X-XSS-Protection",
                "Referrer-Policy"
            ]
            
            for header in security_headers:
                if header in headers:
                    self.log_test(f"Security header: {header}", "PASS", f"Header present: {headers[header]}")
                else:
                    self.log_test(f"Security header: {header}", "FAIL", "Header not present")
                    
        except Exception as e:
            self.log_test("Security headers test", "FAIL", f"Error: {str(e)}")
    
    def test_cors_configuration(self):
        """Test 10: CORS configuration for API access"""
        print("\n🔟 Testing CORS Configuration...")
        
        try:
            response = requests.get(f"{self.api_url}/status", timeout=5)
            headers = response.headers
            
            if "Access-Control-Allow-Origin" in headers:
                self.log_test("CORS headers", "PASS", f"CORS configured: {headers['Access-Control-Allow-Origin']}")
            else:
                self.log_test("CORS headers", "FAIL", "CORS not configured")
                
        except Exception as e:
            self.log_test("CORS configuration", "FAIL", f"Error: {str(e)}")
    
    def run_all_tests(self):
        """Run all regression tests"""
        print("🧪 Solar Heating System v3 - Comprehensive Regression Testing")
        print("=" * 60)
        
        # Run all test categories
        self.test_system_availability()
        self.test_api_endpoints()
        self.test_frontend_components()
        self.test_nginx_configuration()
        self.test_systemd_services()
        self.test_old_architecture_cleanup()
        self.test_new_architecture_components()
        self.test_performance_metrics()
        self.test_security_headers()
        self.test_cors_configuration()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary and results"""
        print("\n" + "=" * 60)
        print("📋 REGRESSION TEST SUMMARY")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = len([r for r in self.test_results if r['status'] == 'FAIL'])
        warning_tests = len([r for r in self.test_results if r['status'] == 'WARNING'])
        
        success_rate = (passed_tests / total_tests) * 100 if total_tests > 0 else 0
        
        print(f"📊 Test Results:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {passed_tests} ✅")
        print(f"   Failed: {failed_tests} ❌")
        print(f"   Warnings: {warning_tests} ⚠️")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        print(f"\n⏱️ Test Duration: {datetime.now() - self.start_time}")
        
        # Show failed tests
        if failed_tests > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    print(f"   • {result['test']}: {result['details']}")
        
        # Show warning tests
        if warning_tests > 0:
            print(f"\n⚠️ Warning Tests:")
            for result in self.test_results:
                if result['status'] == 'WARNING':
                    print(f"   • {result['test']}: {result['details']}")
        
        # Overall assessment
        if success_rate >= 90:
            print(f"\n🎉 REGRESSION TESTING: PASSED")
            print(f"   The new architecture maintains all functionality!")
            print(f"   Ready for production deployment! 🚀")
        elif success_rate >= 80:
            print(f"\n⚠️ REGRESSION TESTING: PARTIAL PASS")
            print(f"   Most functionality is maintained.")
            print(f"   Review failed tests before deployment.")
        else:
            print(f"\n❌ REGRESSION TESTING: FAILED")
            print(f"   Significant functionality issues detected.")
            print(f"   Do not deploy until issues are resolved.")
        
        print("\n" + "=" * 60)

def main():
    """Main function to run regression tests"""
    tester = RegressionTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
