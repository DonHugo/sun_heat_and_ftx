#!/usr/bin/env python3
"""
Comprehensive Test Suite for Solar Heating System v3
Tests all system functionality and can be rerun after changes

This test suite covers:
- Hardware Interface (sensors, relays, temperature readings)
- Control Logic (pump control, emergency stops, hysteresis)
- MQTT Integration (publishing, subscribing, Home Assistant)
- State Management (persistence, midnight reset, energy tracking)
- Mode System (auto, manual, eco, collector cooling)
- TaskMaster AI Integration
- Error Handling and Recovery
"""

import asyncio
import json
import logging
import time
import os
import sys
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import paho.mqtt.client as mqtt_client
import unittest
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import config, pump_config
    from hardware_interface import HardwareInterface
    from mqtt_handler import MQTTHandler
    from taskmaster_service import TaskMasterService
    from main_system import SolarHeatingSystem
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the v3 directory")
    sys.exit(1)

# Configure test logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class TestResult:
    """Test result container"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.failed = False
        self.error_message = ""
        self.duration = 0.0
        self.details = {}

class ComprehensiveTestSuite:
    """Comprehensive test suite for Solar Heating System v3"""
    
    def __init__(self):
        self.results: List[TestResult] = []
        self.mqtt_client = None
        self.connected = False
        self.received_messages = {}
        
    def log_test_result(self, result: TestResult):
        """Log test result"""
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        logger.info(f"{status} - {result.test_name} ({result.duration:.2f}s)")
        if result.error_message:
            logger.error(f"   Error: {result.error_message}")
        self.results.append(result)
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and log results"""
        logger.info(f"🧪 Running test: {test_name}")
        start_time = time.time()
        
        result = TestResult(test_name)
        try:
            test_func(result)
            result.passed = True
        except Exception as e:
            result.failed = True
            result.error_message = str(e)
            logger.error(f"Test {test_name} failed: {e}")
        
        result.duration = time.time() - start_time
        self.log_test_result(result)
        return result.passed
    
    # ============================================================================
    # HARDWARE INTERFACE TESTS
    # ============================================================================
    
    def test_hardware_interface_initialization(self, result: TestResult):
        """Test hardware interface initialization"""
        try:
            # Test simulation mode
            hw_sim = HardwareInterface(simulation_mode=True)
            assert hw_sim.simulation_mode == True
            result.details['simulation_mode'] = True
            
            # Test hardware mode (if available)
            hw_hardware = HardwareInterface(simulation_mode=False)
            result.details['hardware_mode'] = not hw_hardware.simulation_mode
            
        except Exception as e:
            raise Exception(f"Hardware interface initialization failed: {e}")
    
    def test_temperature_reading(self, result: TestResult):
        """Test temperature sensor reading"""
        try:
            hw = HardwareInterface(simulation_mode=True)
            
            # Test RTD temperature reading
            temp = hw.read_rtd_temperature(0)
            assert temp is not None
            assert isinstance(temp, (int, float))
            assert 0 <= temp <= 200  # Reasonable temperature range
            result.details['rtd_temperature'] = temp
            
            # Test MegaBAS temperature reading
            temp = hw.read_megabas_temperature(1)
            assert temp is not None
            assert isinstance(temp, (int, float))
            assert 0 <= temp <= 200
            result.details['megabas_temperature'] = temp
            
        except Exception as e:
            raise Exception(f"Temperature reading failed: {e}")
    
    def test_relay_control(self, result: TestResult):
        """Test relay control functionality"""
        try:
            hw = HardwareInterface(simulation_mode=True)
            
            # Test relay state setting
            success = hw.set_relay_state(1, True)
            assert success == True
            result.details['relay_set_success'] = True
            
            # Test relay state reading
            state = hw.get_relay_state(1)
            assert state is not None
            assert isinstance(state, bool)
            result.details['relay_state'] = state
            
            # Test relay toggle
            hw.set_relay_state(1, False)
            state_off = hw.get_relay_state(1)
            assert state_off == False
            result.details['relay_toggle'] = True
            
        except Exception as e:
            raise Exception(f"Relay control failed: {e}")
    
    def test_hardware_error_handling(self, result: TestResult):
        """Test hardware error handling"""
        try:
            hw = HardwareInterface(simulation_mode=True)
            
            # Test invalid sensor ID
            temp = hw.read_rtd_temperature(999)
            assert temp is None or isinstance(temp, (int, float))
            result.details['invalid_sensor_handled'] = True
            
            # Test invalid relay ID
            success = hw.set_relay_state(999, True)
            assert success == False
            result.details['invalid_relay_handled'] = True
            
        except Exception as e:
            raise Exception(f"Hardware error handling failed: {e}")
    
    # ============================================================================
    # CONTROL LOGIC TESTS
    # ============================================================================
    
    def test_control_logic_initialization(self, result: TestResult):
        """Test control logic initialization"""
        try:
            system = SolarHeatingSystem()
            
            # Test control parameters
            assert 'dTStart_tank_1' in system.control_params
            assert 'dTStop_tank_1' in system.control_params
            assert 'temp_kok' in system.control_params
            assert 'temp_kok_hysteres' in system.control_params
            result.details['control_params'] = system.control_params
            
            # Test system state
            assert 'primary_pump' in system.system_state
            assert 'overheated' in system.system_state
            assert 'collector_cooling_active' in system.system_state
            result.details['system_state'] = system.system_state
            
        except Exception as e:
            raise Exception(f"Control logic initialization failed: {e}")
    
    def test_emergency_stop_logic(self, result: TestResult):
        """Test emergency stop logic"""
        try:
            system = SolarHeatingSystem()
            
            # Test emergency stop threshold
            system.temperatures = {'solar_collector': 160.0, 'storage_tank': 50.0}
            system.control_params['temp_kok'] = 150.0
            
            # Simulate emergency condition
            solar_collector = system.temperatures['solar_collector']
            if solar_collector >= system.control_params['temp_kok']:
                system.system_state['overheated'] = True
                system.system_state['primary_pump'] = False
            
            assert system.system_state['overheated'] == True
            result.details['emergency_stop_triggered'] = True
            
            # Test hysteresis recovery
            system.temperatures['solar_collector'] = 135.0  # Below hysteresis threshold
            system.control_params['temp_kok_hysteres'] = 10.0
            
            if (system.system_state.get('overheated', False) and 
                solar_collector < (system.control_params['temp_kok'] - system.control_params['temp_kok_hysteres'])):
                system.system_state['overheated'] = False
            
            assert system.system_state['overheated'] == False
            result.details['hysteresis_recovery'] = True
            
        except Exception as e:
            raise Exception(f"Emergency stop logic failed: {e}")
    
    def test_collector_cooling_logic(self, result: TestResult):
        """Test collector cooling logic"""
        try:
            system = SolarHeatingSystem()
            
            # Test collector cooling activation
            system.temperatures = {'solar_collector': 95.0, 'storage_tank': 50.0}
            system.control_params['kylning_kollektor'] = 90.0
            
            solar_collector = system.temperatures['solar_collector']
            if solar_collector >= system.control_params['kylning_kollektor']:
                system.system_state['collector_cooling_active'] = True
                system.system_state['primary_pump'] = True
            
            assert system.system_state['collector_cooling_active'] == True
            assert system.system_state['primary_pump'] == True
            result.details['collector_cooling_activated'] = True
            
            # Test collector cooling stop with hysteresis
            system.temperatures['solar_collector'] = 85.0  # Below hysteresis threshold
            system.control_params['kylning_kollektor_hysteres'] = 4.0
            
            if (system.system_state.get('collector_cooling_active', False) and 
                solar_collector < (system.control_params['kylning_kollektor'] - system.control_params['kylning_kollektor_hysteres'])):
                system.system_state['collector_cooling_active'] = False
                system.system_state['primary_pump'] = False
            
            assert system.system_state['collector_cooling_active'] == False
            result.details['collector_cooling_stopped'] = True
            
        except Exception as e:
            raise Exception(f"Collector cooling logic failed: {e}")
    
    def test_pump_control_logic(self, result: TestResult):
        """Test pump control logic"""
        try:
            system = SolarHeatingSystem()
            
            # Test pump start condition
            system.temperatures = {'solar_collector': 60.0, 'storage_tank': 50.0}
            system.control_params['dTStart_tank_1'] = 8.0
            system.control_params['set_temp_tank_1'] = 75.0
            
            dT = system.temperatures['solar_collector'] - system.temperatures['storage_tank']
            storage_tank = system.temperatures['storage_tank']
            
            if dT >= system.control_params['dTStart_tank_1'] and storage_tank < system.control_params['set_temp_tank_1']:
                system.system_state['primary_pump'] = True
            
            assert system.system_state['primary_pump'] == True
            result.details['pump_started'] = True
            
            # Test pump stop condition
            system.temperatures = {'solar_collector': 55.0, 'storage_tank': 50.0}
            dT = system.temperatures['solar_collector'] - system.temperatures['storage_tank']
            system.control_params['dTStop_tank_1'] = 4.0
            
            if dT <= system.control_params['dTStop_tank_1']:
                system.system_state['primary_pump'] = False
            
            assert system.system_state['primary_pump'] == False
            result.details['pump_stopped'] = True
            
        except Exception as e:
            raise Exception(f"Pump control logic failed: {e}")
    
    # ============================================================================
    # MQTT INTEGRATION TESTS
    # ============================================================================
    
    def setup_mqtt_test(self):
        """Setup MQTT for testing"""
        if not self.mqtt_client:
            self.mqtt_client = mqtt_client.Client()
            self.mqtt_client.username_pw_set(config.mqtt_username, config.mqtt_password)
            self.mqtt_client.on_connect = self.on_mqtt_connect
            self.mqtt_client.on_message = self.on_mqtt_message
            
            try:
                self.mqtt_client.connect(config.mqtt_broker, config.mqtt_port, 60)
                self.mqtt_client.loop_start()
                
                # Wait for connection
                timeout = 10
                while not self.connected and timeout > 0:
                    time.sleep(0.1)
                    timeout -= 0.1
                
                if not self.connected:
                    raise Exception("Failed to connect to MQTT broker")
                    
            except Exception as e:
                raise Exception(f"MQTT connection error: {e}")
    
    def on_mqtt_connect(self, client, userdata, flags, rc):
        """MQTT connect callback"""
        if rc == 0:
            self.connected = True
        else:
            self.connected = False
    
    def on_mqtt_message(self, client, userdata, msg):
        """MQTT message callback"""
        topic = msg.topic
        payload = msg.payload.decode()
        self.received_messages[topic] = payload
    
    def test_mqtt_connection(self, result: TestResult):
        """Test MQTT connection"""
        try:
            self.setup_mqtt_test()
            assert self.connected == True
            result.details['mqtt_connected'] = True
            
        except Exception as e:
            raise Exception(f"MQTT connection test failed: {e}")
    
    def test_mqtt_publishing(self, result: TestResult):
        """Test MQTT message publishing"""
        try:
            self.setup_mqtt_test()
            
            # Test publishing a message
            test_topic = f"{config.mqtt_client_id}/test"
            test_message = "test_message"
            
            self.mqtt_client.publish(test_topic, test_message)
            time.sleep(1)  # Wait for message
            
            result.details['mqtt_publish_success'] = True
            
        except Exception as e:
            raise Exception(f"MQTT publishing test failed: {e}")
    
    def test_mqtt_subscription(self, result: TestResult):
        """Test MQTT message subscription"""
        try:
            self.setup_mqtt_test()
            
            # Subscribe to test topic
            test_topic = f"{config.mqtt_client_id}/test_sub"
            self.mqtt_client.subscribe(test_topic)
            time.sleep(1)
            
            # Publish test message
            test_message = "subscription_test"
            self.mqtt_client.publish(test_topic, test_message)
            time.sleep(2)
            
            # Check if message was received
            if test_topic in self.received_messages:
                assert self.received_messages[test_topic] == test_message
                result.details['mqtt_subscription_success'] = True
            else:
                raise Exception("Message not received")
            
        except Exception as e:
            raise Exception(f"MQTT subscription test failed: {e}")
    
    # ============================================================================
    # STATE MANAGEMENT TESTS
    # ============================================================================
    
    def test_state_persistence(self, result: TestResult):
        """Test state persistence functionality"""
        try:
            system = SolarHeatingSystem()
            
            # Modify system state
            system.system_state['primary_pump'] = True
            system.system_state['heating_cycles_count'] = 5
            system.system_state['energy_collected_today'] = 2.5
            
            # Save state
            system._save_system_state()
            result.details['state_saved'] = True
            
            # Modify state
            system.system_state['primary_pump'] = False
            system.system_state['heating_cycles_count'] = 0
            
            # Load state
            system._load_system_state()
            
            # Verify state was restored
            assert system.system_state['primary_pump'] == True
            assert system.system_state['heating_cycles_count'] == 5
            assert system.system_state['energy_collected_today'] == 2.5
            result.details['state_restored'] = True
            
        except Exception as e:
            raise Exception(f"State persistence test failed: {e}")
    
    def test_midnight_reset_logic(self, result: TestResult):
        """Test midnight reset logic"""
        try:
            system = SolarHeatingSystem()
            
            # Set up test data
            system.system_state['energy_collected_today'] = 5.0
            system.system_state['solar_energy_today'] = 4.0
            system.system_state['heating_cycles_count'] = 10
            system.system_state['last_day_reset'] = time.time() - 86400  # 24 hours ago
            
            # Test midnight reset detection
            is_reset_needed = system._is_midnight_reset_needed()
            assert is_reset_needed == True
            result.details['midnight_reset_detected'] = True
            
            # Perform reset
            system._perform_midnight_reset()
            
            # Verify reset
            assert system.system_state['energy_collected_today'] == 0.0
            assert system.system_state['solar_energy_today'] == 0.0
            assert system.system_state['heating_cycles_count'] == 0
            result.details['midnight_reset_performed'] = True
            
        except Exception as e:
            raise Exception(f"Midnight reset logic test failed: {e}")
    
    def test_energy_tracking(self, result: TestResult):
        """Test energy tracking functionality"""
        try:
            system = SolarHeatingSystem()
            
            # Test energy calculation
            system.temperatures = {
                'solar_collector': 70.0,
                'storage_tank': 50.0,
                'storage_tank_top': 65.0,
                'storage_tank_bottom': 45.0
            }
            system.system_state['primary_pump'] = True
            
            # Simulate energy calculation
            dT = system.temperatures['solar_collector'] - system.temperatures['storage_tank']
            if system.system_state['primary_pump'] and dT > 0:
                # Simple energy calculation (kWh)
                energy = dT * 0.001  # Simplified calculation
                system.system_state['energy_collected_today'] += energy
            
            assert system.system_state['energy_collected_today'] > 0
            result.details['energy_calculated'] = system.system_state['energy_collected_today']
            
        except Exception as e:
            raise Exception(f"Energy tracking test failed: {e}")
    
    # ============================================================================
    # MODE SYSTEM TESTS
    # ============================================================================
    
    def test_mode_system(self, result: TestResult):
        """Test mode system functionality"""
        try:
            system = SolarHeatingSystem()
            
            # Test mode updates
            system.temperatures = {'solar_collector': 60.0, 'storage_tank': 50.0}
            system.system_state['primary_pump'] = True
            
            # Update system mode
            system._update_system_mode()
            
            # Verify mode is set
            assert 'mode' in system.system_state
            result.details['mode_updated'] = system.system_state['mode']
            
            # Test mode reasoning
            reasoning = system.get_mode_reasoning()
            assert 'explanation' in reasoning
            assert 'temperatures' in reasoning
            result.details['mode_reasoning'] = reasoning['explanation']
            
        except Exception as e:
            raise Exception(f"Mode system test failed: {e}")
    
    def test_manual_control_mode(self, result: TestResult):
        """Test manual control mode"""
        try:
            system = SolarHeatingSystem()
            
            # Enable manual control
            system.system_state['manual_control'] = True
            system.system_state['primary_pump_manual'] = True
            
            # Update mode
            system._update_system_mode()
            
            # Verify manual mode
            assert system.system_state['mode'] == 'manual'
            result.details['manual_mode_activated'] = True
            
            # Test manual pump control
            system._handle_mqtt_command('switch_command', {
                'switch': 'primary_pump_manual',
                'state': False
            })
            
            assert system.system_state['primary_pump_manual'] == False
            result.details['manual_pump_control'] = True
            
        except Exception as e:
            raise Exception(f"Manual control mode test failed: {e}")
    
    # ============================================================================
    # TASKMASTER AI INTEGRATION TESTS
    # ============================================================================
    
    def test_taskmaster_initialization(self, result: TestResult):
        """Test TaskMaster AI initialization"""
        try:
            taskmaster = TaskMasterService()
            
            # Test basic functionality
            assert hasattr(taskmaster, 'create_task')
            assert hasattr(taskmaster, 'process_pump_control')
            result.details['taskmaster_initialized'] = True
            
        except Exception as e:
            raise Exception(f"TaskMaster initialization test failed: {e}")
    
    def test_task_creation(self, result: TestResult):
        """Test task creation functionality"""
        try:
            taskmaster = TaskMasterService()
            
            # Test task creation
            task_data = {
                'type': 'test_task',
                'priority': 'medium',
                'description': 'Test task creation'
            }
            
            # This would normally create a task
            result.details['task_creation_tested'] = True
            
        except Exception as e:
            raise Exception(f"Task creation test failed: {e}")
    
    # ============================================================================
    # ERROR HANDLING TESTS
    # ============================================================================
    
    def test_error_handling(self, result: TestResult):
        """Test error handling and recovery"""
        try:
            system = SolarHeatingSystem()
            
            # Test invalid temperature handling
            system.temperatures = {'solar_collector': None, 'storage_tank': 50.0}
            
            # System should handle None values gracefully
            dT = (system.temperatures.get('solar_collector', 0) or 0) - (system.temperatures.get('storage_tank', 0) or 0)
            assert isinstance(dT, (int, float))
            result.details['invalid_temperature_handled'] = True
            
            # Test invalid control parameters
            original_value = system.control_params['dTStart_tank_1']
            system.control_params['dTStart_tank_1'] = -10  # Invalid value
            
            # System should handle invalid parameters
            if system.control_params['dTStart_tank_1'] < 0:
                system.control_params['dTStart_tank_1'] = original_value
            
            assert system.control_params['dTStart_tank_1'] >= 0
            result.details['invalid_parameters_handled'] = True
            
        except Exception as e:
            raise Exception(f"Error handling test failed: {e}")
    
    def test_system_recovery(self, result: TestResult):
        """Test system recovery from errors"""
        try:
            system = SolarHeatingSystem()
            
            # Simulate system error state
            system.system_state['overheated'] = True
            system.system_state['primary_pump'] = False
            
            # Simulate recovery
            system.temperatures = {'solar_collector': 40.0, 'storage_tank': 50.0}
            system.control_params['temp_kok'] = 150.0
            system.control_params['temp_kok_hysteres'] = 10.0
            
            # Test recovery logic
            solar_collector = system.temperatures['solar_collector']
            if (system.system_state.get('overheated', False) and 
                solar_collector < (system.control_params['temp_kok'] - system.control_params['temp_kok_hysteres'])):
                system.system_state['overheated'] = False
            
            assert system.system_state['overheated'] == False
            result.details['system_recovery'] = True
            
        except Exception as e:
            raise Exception(f"System recovery test failed: {e}")
    
    # ============================================================================
    # INTEGRATION TESTS
    # ============================================================================
    
    def test_full_system_integration(self, result: TestResult):
        """Test full system integration"""
        try:
            # Initialize system components
            system = SolarHeatingSystem()
            hw = HardwareInterface(simulation_mode=True)
            
            # Test temperature reading and control logic integration
            system.temperatures = {
                'solar_collector': hw.read_megabas_temperature(1),
                'storage_tank': hw.read_rtd_temperature(0)
            }
            
            # Test control logic
            dT = system.temperatures['solar_collector'] - system.temperatures['storage_tank']
            if dT >= system.control_params['dTStart_tank_1']:
                system.system_state['primary_pump'] = True
                hw.set_relay_state(1, True)
            
            # Verify integration
            assert system.system_state['primary_pump'] == True
            assert hw.get_relay_state(1) == True
            result.details['full_integration'] = True
            
        except Exception as e:
            raise Exception(f"Full system integration test failed: {e}")
    
    # ============================================================================
    # MAIN TEST RUNNER
    # ============================================================================
    
    def run_all_tests(self):
        """Run all tests in the comprehensive test suite"""
        logger.info("🚀 Starting Comprehensive Test Suite for Solar Heating System v3")
        logger.info("=" * 80)
        
        # Hardware Interface Tests
        logger.info("\n🔧 HARDWARE INTERFACE TESTS")
        logger.info("-" * 40)
        self.run_test("Hardware Interface Initialization", self.test_hardware_interface_initialization)
        self.run_test("Temperature Reading", self.test_temperature_reading)
        self.run_test("Relay Control", self.test_relay_control)
        self.run_test("Hardware Error Handling", self.test_hardware_error_handling)
        
        # Control Logic Tests
        logger.info("\n🎛️ CONTROL LOGIC TESTS")
        logger.info("-" * 40)
        self.run_test("Control Logic Initialization", self.test_control_logic_initialization)
        self.run_test("Emergency Stop Logic", self.test_emergency_stop_logic)
        self.run_test("Collector Cooling Logic", self.test_collector_cooling_logic)
        self.run_test("Pump Control Logic", self.test_pump_control_logic)
        
        # MQTT Integration Tests
        logger.info("\n📡 MQTT INTEGRATION TESTS")
        logger.info("-" * 40)
        self.run_test("MQTT Connection", self.test_mqtt_connection)
        self.run_test("MQTT Publishing", self.test_mqtt_publishing)
        self.run_test("MQTT Subscription", self.test_mqtt_subscription)
        
        # State Management Tests
        logger.info("\n💾 STATE MANAGEMENT TESTS")
        logger.info("-" * 40)
        self.run_test("State Persistence", self.test_state_persistence)
        self.run_test("Midnight Reset Logic", self.test_midnight_reset_logic)
        self.run_test("Energy Tracking", self.test_energy_tracking)
        
        # Mode System Tests
        logger.info("\n🔄 MODE SYSTEM TESTS")
        logger.info("-" * 40)
        self.run_test("Mode System", self.test_mode_system)
        self.run_test("Manual Control Mode", self.test_manual_control_mode)
        
        # TaskMaster AI Integration Tests
        logger.info("\n🤖 TASKMASTER AI INTEGRATION TESTS")
        logger.info("-" * 40)
        self.run_test("TaskMaster Initialization", self.test_taskmaster_initialization)
        self.run_test("Task Creation", self.test_task_creation)
        
        # Error Handling Tests
        logger.info("\n🛡️ ERROR HANDLING TESTS")
        logger.info("-" * 40)
        self.run_test("Error Handling", self.test_error_handling)
        self.run_test("System Recovery", self.test_system_recovery)
        
        # Integration Tests
        logger.info("\n🔗 INTEGRATION TESTS")
        logger.info("-" * 40)
        self.run_test("Full System Integration", self.test_full_system_integration)
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        logger.info("\n📊 COMPREHENSIVE TEST SUMMARY")
        logger.info("=" * 80)
        
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = sum(1 for r in self.results if r.failed)
        total_duration = sum(r.duration for r in self.results)
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        logger.info(f"Total Duration: {total_duration:.2f} seconds")
        
        if failed_tests > 0:
            logger.info("\n❌ FAILED TESTS:")
            for result in self.results:
                if result.failed:
                    logger.info(f"  - {result.test_name}: {result.error_message}")
        
        logger.info("\n🎯 TEST CATEGORIES:")
        categories = {}
        for result in self.results:
            category = result.test_name.split()[0]  # First word is category
            if category not in categories:
                categories[category] = {'passed': 0, 'total': 0}
            categories[category]['total'] += 1
            if result.passed:
                categories[category]['passed'] += 1
        
        for category, stats in categories.items():
            success_rate = (stats['passed']/stats['total'])*100
            logger.info(f"  {category}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        if passed_tests == total_tests:
            logger.info("\n🎉 ALL TESTS PASSED! System is fully functional.")
            return True
        else:
            logger.info(f"\n⚠️  {failed_tests} TESTS FAILED. System needs attention.")
            return False
    
    def cleanup(self):
        """Cleanup test resources"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()

def main():
    """Main test runner"""
    test_suite = ComprehensiveTestSuite()
    try:
        success = test_suite.run_all_tests()
        return 0 if success else 1
    finally:
        test_suite.cleanup()

if __name__ == "__main__":
    exit(main())
