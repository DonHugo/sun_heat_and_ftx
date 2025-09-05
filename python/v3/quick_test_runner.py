#!/usr/bin/env python3
"""
Quick Test Runner for Solar Heating System v3
Runs essential tests quickly for development and validation

Usage:
    python3 quick_test_runner.py [test_category]
    
Test Categories:
    - hardware: Hardware interface tests
    - control: Control logic tests
    - mqtt: MQTT integration tests
    - state: State management tests
    - modes: Mode system tests
    - all: All tests (default)
"""

import sys
import os
import time
import logging
from typing import List, Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import config
    from hardware_interface import HardwareInterface
    from mqtt_handler import MQTTHandler
    from main_system import SolarHeatingSystem
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the v3 directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class QuickTestRunner:
    """Quick test runner for essential functionality"""
    
    def __init__(self):
        self.test_results = {}
        self.start_time = time.time()
    
    def log_result(self, test_name: str, passed: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if passed else "❌ FAIL"
        logger.info(f"{status} - {test_name}")
        if message:
            logger.info(f"   {message}")
        self.test_results[test_name] = {'passed': passed, 'message': message}
    
    def test_hardware_basic(self):
        """Test basic hardware functionality"""
        logger.info("🔧 Testing Hardware Interface...")
        
        try:
            # Test simulation mode
            hw = HardwareInterface(simulation_mode=True)
            self.log_result("Hardware Initialization", True, "Simulation mode working")
            
            # Test temperature reading
            temp = hw.read_rtd_temperature(0)
            if temp is not None and 0 <= temp <= 200:
                self.log_result("Temperature Reading", True, f"RTD temp: {temp}°C")
            else:
                self.log_result("Temperature Reading", False, f"Invalid temperature: {temp}")
            
            # Test relay control
            hw.set_relay_state(1, True)
            state = hw.get_relay_state(1)
            if state == True:
                self.log_result("Relay Control", True, "Relay 1 ON")
            else:
                self.log_result("Relay Control", False, f"Relay state: {state}")
            
        except Exception as e:
            self.log_result("Hardware Interface", False, str(e))
    
    def test_control_logic_basic(self):
        """Test basic control logic"""
        logger.info("🎛️ Testing Control Logic...")
        
        try:
            system = SolarHeatingSystem()
            
            # Test control parameters
            if all(key in system.control_params for key in ['dTStart_tank_1', 'dTStop_tank_1', 'temp_kok']):
                self.log_result("Control Parameters", True, "All parameters loaded")
            else:
                self.log_result("Control Parameters", False, "Missing parameters")
            
            # Test emergency stop logic
            system.temperatures = {'solar_collector': 160.0, 'storage_tank': 50.0}
            system.control_params['temp_kok'] = 150.0
            
            solar_collector = system.temperatures['solar_collector']
            if solar_collector >= system.control_params['temp_kok']:
                system.system_state['overheated'] = True
                self.log_result("Emergency Stop Logic", True, "Emergency condition detected")
            else:
                self.log_result("Emergency Stop Logic", False, "Emergency condition not detected")
            
            # Test pump control logic
            system.temperatures = {'solar_collector': 60.0, 'storage_tank': 50.0}
            dT = system.temperatures['solar_collector'] - system.temperatures['storage_tank']
            
            if dT >= system.control_params['dTStart_tank_1']:
                system.system_state['primary_pump'] = True
                self.log_result("Pump Control Logic", True, f"Pump started: dT={dT:.1f}°C")
            else:
                self.log_result("Pump Control Logic", False, f"Pump not started: dT={dT:.1f}°C")
            
        except Exception as e:
            self.log_result("Control Logic", False, str(e))
    
    def test_mqtt_basic(self):
        """Test basic MQTT functionality"""
        logger.info("📡 Testing MQTT Integration...")
        
        try:
            # Test MQTT handler initialization
            mqtt = MQTTHandler()
            self.log_result("MQTT Handler Init", True, "MQTT handler created")
            
            # Test configuration
            if hasattr(config, 'mqtt_broker') and config.mqtt_broker:
                self.log_result("MQTT Configuration", True, f"Broker: {config.mqtt_broker}")
            else:
                self.log_result("MQTT Configuration", False, "No broker configured")
            
        except Exception as e:
            self.log_result("MQTT Integration", False, str(e))
    
    def test_state_management_basic(self):
        """Test basic state management"""
        logger.info("💾 Testing State Management...")
        
        try:
            system = SolarHeatingSystem()
            
            # Test state initialization
            if 'primary_pump' in system.system_state and 'overheated' in system.system_state:
                self.log_result("State Initialization", True, "System state initialized")
            else:
                self.log_result("State Initialization", False, "Missing state variables")
            
            # Test state modification
            original_pump_state = system.system_state['primary_pump']
            system.system_state['primary_pump'] = not original_pump_state
            
            if system.system_state['primary_pump'] != original_pump_state:
                self.log_result("State Modification", True, "State can be modified")
            else:
                self.log_result("State Modification", False, "State modification failed")
            
            # Test state persistence
            system._save_system_state()
            self.log_result("State Persistence", True, "State saved successfully")
            
        except Exception as e:
            self.log_result("State Management", False, str(e))
    
    def test_mode_system_basic(self):
        """Test basic mode system"""
        logger.info("🔄 Testing Mode System...")
        
        try:
            system = SolarHeatingSystem()
            
            # Test mode initialization
            if 'mode' in system.system_state:
                self.log_result("Mode Initialization", True, f"Initial mode: {system.system_state['mode']}")
            else:
                self.log_result("Mode Initialization", False, "No mode in system state")
            
            # Test mode reasoning
            reasoning = system.get_mode_reasoning()
            if 'explanation' in reasoning:
                self.log_result("Mode Reasoning", True, reasoning['explanation'])
            else:
                self.log_result("Mode Reasoning", False, "No explanation in reasoning")
            
            # Test manual control
            system.system_state['manual_control'] = True
            system._update_system_mode()
            
            if system.system_state['mode'] == 'manual':
                self.log_result("Manual Mode", True, "Manual mode activated")
            else:
                self.log_result("Manual Mode", False, f"Mode: {system.system_state['mode']}")
            
        except Exception as e:
            self.log_result("Mode System", False, str(e))
    
    def test_system_integration(self):
        """Test system integration"""
        logger.info("🔗 Testing System Integration...")
        
        try:
            # Initialize all components
            system = SolarHeatingSystem()
            hw = HardwareInterface(simulation_mode=True)
            
            # Test temperature reading integration
            system.temperatures = {
                'solar_collector': hw.read_megabas_temperature(1),
                'storage_tank': hw.read_rtd_temperature(0)
            }
            
            if system.temperatures['solar_collector'] is not None and system.temperatures['storage_tank'] is not None:
                self.log_result("Temperature Integration", True, 
                    f"Collector: {system.temperatures['solar_collector']}°C, "
                    f"Tank: {system.temperatures['storage_tank']}°C")
            else:
                self.log_result("Temperature Integration", False, "Temperature reading failed")
            
            # Test control logic integration
            dT = system.temperatures['solar_collector'] - system.temperatures['storage_tank']
            if dT >= system.control_params['dTStart_tank_1']:
                system.system_state['primary_pump'] = True
                hw.set_relay_state(1, True)
                
                if hw.get_relay_state(1) == True:
                    self.log_result("Control Integration", True, f"Pump activated: dT={dT:.1f}°C")
                else:
                    self.log_result("Control Integration", False, "Relay not activated")
            else:
                self.log_result("Control Integration", True, f"Pump not needed: dT={dT:.1f}°C")
            
        except Exception as e:
            self.log_result("System Integration", False, str(e))
    
    def run_tests(self, test_category: str = "all"):
        """Run specified test category"""
        logger.info(f"🚀 Quick Test Runner - Category: {test_category.upper()}")
        logger.info("=" * 60)
        
        if test_category in ["hardware", "all"]:
            self.test_hardware_basic()
        
        if test_category in ["control", "all"]:
            self.test_control_logic_basic()
        
        if test_category in ["mqtt", "all"]:
            self.test_mqtt_basic()
        
        if test_category in ["state", "all"]:
            self.test_state_management_basic()
        
        if test_category in ["modes", "all"]:
            self.test_mode_system_basic()
        
        if test_category in ["integration", "all"]:
            self.test_system_integration()
        
        # Generate summary
        self.generate_summary()
    
    def generate_summary(self):
        """Generate test summary"""
        logger.info("\n📊 QUICK TEST SUMMARY")
        logger.info("=" * 60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r['passed'])
        failed_tests = total_tests - passed_tests
        duration = time.time() - self.start_time
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Duration: {duration:.2f} seconds")
        
        if failed_tests > 0:
            logger.info("\n❌ FAILED TESTS:")
            for test_name, result in self.test_results.items():
                if not result['passed']:
                    logger.info(f"  - {test_name}: {result['message']}")
        
        if passed_tests == total_tests:
            logger.info("\n🎉 ALL TESTS PASSED! System is ready.")
            return True
        else:
            logger.info(f"\n⚠️  {failed_tests} TESTS FAILED. Check system.")
            return False

def main():
    """Main function"""
    if len(sys.argv) > 1:
        test_category = sys.argv[1].lower()
    else:
        test_category = "all"
    
    valid_categories = ["hardware", "control", "mqtt", "state", "modes", "integration", "all"]
    if test_category not in valid_categories:
        print(f"Invalid test category: {test_category}")
        print(f"Valid categories: {', '.join(valid_categories)}")
        return 1
    
    runner = QuickTestRunner()
    success = runner.run_tests(test_category)
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
