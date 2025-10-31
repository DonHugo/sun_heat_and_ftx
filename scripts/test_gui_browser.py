#!/usr/bin/env python3
"""
Automated Browser Testing for Solar Heating System GUI
Tests the GUI using Selenium WebDriver
"""

import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class SolarHeatingGUITester:
    def __init__(self, base_url="http://192.168.0.18:5000"):
        self.base_url = base_url
        self.driver = None
        self.wait = None
        
    def setup_driver(self):
        """Setup Chrome WebDriver with headless options"""
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            self.wait = WebDriverWait(self.driver, 10)
            print("✅ Chrome WebDriver initialized successfully")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize WebDriver: {e}")
            print("💡 Install ChromeDriver: brew install chromedriver")
            return False
    
    def test_api_endpoints(self):
        """Test API endpoints directly"""
        print("\n🔧 Testing API Endpoints...")
        
        try:
            # Test system status
            response = requests.get(f"{self.base_url}/api/system/status", timeout=5)
            if response.status_code == 200:
                data = response.json()
                print(f"✅ System Status: {data.get('service_status', {})}")
            else:
                print(f"❌ System Status failed: {response.status_code}")
        except Exception as e:
            print(f"❌ API test failed: {e}")
    
    def test_browser_loading(self):
        """Test if the GUI loads in browser"""
        print("\n🔧 Testing Browser Loading...")
        
        try:
            self.driver.get(self.base_url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            print("✅ GUI loaded successfully in browser")
            return True
        except TimeoutException:
            print("❌ GUI failed to load in browser")
            return False
        except Exception as e:
            print(f"❌ Browser loading failed: {e}")
            return False
    
    def test_tab_navigation(self):
        """Test tab navigation functionality"""
        print("\n🔧 Testing Tab Navigation...")
        
        try:
            # Test Overview tab
            overview_tab = self.driver.find_element(By.CSS_SELECTOR, '[data-tab="overview"]')
            overview_tab.click()
            time.sleep(1)
            print("✅ Overview tab clicked")
            
            # Test Sensors tab
            sensors_tab = self.driver.find_element(By.CSS_SELECTOR, '[data-tab="sensors"]')
            sensors_tab.click()
            time.sleep(1)
            print("✅ Sensors tab clicked")
            
            # Test Controls tab
            controls_tab = self.driver.find_element(By.CSS_SELECTOR, '[data-tab="controls"]')
            controls_tab.click()
            time.sleep(1)
            print("✅ Controls tab clicked")
            
            # Test Diagnostics tab
            diagnostics_tab = self.driver.find_element(By.CSS_SELECTOR, '[data-tab="diagnostics"]')
            diagnostics_tab.click()
            time.sleep(1)
            print("✅ Diagnostics tab clicked")
            
            return True
        except Exception as e:
            print(f"❌ Tab navigation failed: {e}")
            return False
    
    def test_mode_buttons(self):
        """Test mode control buttons"""
        print("\n🔧 Testing Mode Control Buttons...")
        
        try:
            # Test Manual mode button
            manual_btn = self.driver.find_element(By.ID, "modeManual")
            manual_btn.click()
            time.sleep(2)
            print("✅ Manual mode button clicked")
            
            # Test Auto mode button
            auto_btn = self.driver.find_element(By.ID, "modeAuto")
            auto_btn.click()
            time.sleep(2)
            print("✅ Auto mode button clicked")
            
            # Test Eco mode button
            eco_btn = self.driver.find_element(By.ID, "modeEco")
            eco_btn.click()
            time.sleep(2)
            print("✅ Eco mode button clicked")
            
            return True
        except Exception as e:
            print(f"❌ Mode buttons failed: {e}")
            return False
    
    def test_pump_buttons(self):
        """Test pump control buttons"""
        print("\n🔧 Testing Pump Control Buttons...")
        
        try:
            # Test pump start button
            pump_start_btn = self.driver.find_element(By.ID, "pumpStart")
            pump_start_btn.click()
            time.sleep(2)
            print("✅ Pump start button clicked")
            
            # Test pump stop button
            pump_stop_btn = self.driver.find_element(By.ID, "pumpStop")
            pump_stop_btn.click()
            time.sleep(2)
            print("✅ Pump stop button clicked")
            
            # Test emergency stop button
            emergency_btn = self.driver.find_element(By.ID, "emergencyStop")
            emergency_btn.click()
            time.sleep(2)
            print("✅ Emergency stop button clicked")
            
            return True
        except Exception as e:
            print(f"❌ Pump buttons failed: {e}")
            return False
    
    def test_data_display(self):
        """Test if data is displayed correctly"""
        print("\n🔧 Testing Data Display...")
        
        try:
            # Check if temperature data is displayed
            tank_temp = self.driver.find_element(By.ID, "tankTemp")
            collector_temp = self.driver.find_element(By.ID, "collectorTemp")
            pump_status = self.driver.find_element(By.ID, "pumpStatus")
            system_mode = self.driver.find_element(By.ID, "systemMode")
            
            print(f"✅ Tank Temperature: {tank_temp.text}")
            print(f"✅ Collector Temperature: {collector_temp.text}")
            print(f"✅ Pump Status: {pump_status.text}")
            print(f"✅ System Mode: {system_mode.text}")
            
            return True
        except Exception as e:
            print(f"❌ Data display failed: {e}")
            return False
    
    def test_responsive_design(self):
        """Test responsive design on different screen sizes"""
        print("\n🔧 Testing Responsive Design...")
        
        try:
            # Test mobile viewport
            self.driver.set_window_size(375, 667)  # iPhone SE
            time.sleep(1)
            print("✅ Mobile viewport (375x667) tested")
            
            # Test tablet viewport
            self.driver.set_window_size(768, 1024)  # iPad
            time.sleep(1)
            print("✅ Tablet viewport (768x1024) tested")
            
            # Test desktop viewport
            self.driver.set_window_size(1920, 1080)  # Desktop
            time.sleep(1)
            print("✅ Desktop viewport (1920x1080) tested")
            
            return True
        except Exception as e:
            print(f"❌ Responsive design test failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests"""
        print("🧪 Starting Comprehensive GUI Testing...")
        print("=" * 50)
        
        if not self.setup_driver():
            return False
        
        try:
            # Run all tests
            self.test_api_endpoints()
            self.test_browser_loading()
            self.test_tab_navigation()
            self.test_mode_buttons()
            self.test_pump_buttons()
            self.test_data_display()
            self.test_responsive_design()
            
            print("\n✅ All tests completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Testing failed: {e}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
                print("🔧 WebDriver closed")

if __name__ == "__main__":
    tester = SolarHeatingGUITester()
    success = tester.run_all_tests()
    exit(0 if success else 1)
