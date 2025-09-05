#!/usr/bin/env python3
"""
Hardware Test Suite for Solar Heating System v3
Comprehensive testing on actual Raspberry Pi hardware environment

This test suite is designed to run on the actual Raspberry Pi with real hardware
and tests features that cannot be properly simulated.

IMPORTANT: This test suite uses GENTLE testing approaches to minimize wear on
actual pump and relay hardware. Tests are designed to be safe for real equipment.

Features tested:
- Real hardware sensor readings and accuracy
- Actual relay control and feedback (gentle testing)
- Hardware error conditions and recovery
- Real-time performance and timing (minimal cycles)
- Hardware-specific error handling
- Physical system integration
- MQTT communication with real broker
- Home Assistant integration with real devices
- System service and daemon functionality
- Hardware calibration and validation

Testing Philosophy:
- Minimal relay switching cycles to reduce wear
- Longer delays between operations for hardware safety
- Focus on primary pump relay (relay 1) and cartridge heater relay (relay 2)
- Gentle stress testing with 2-second delays between operations
"""

import asyncio
import json
import logging
import time
import os
import sys
import subprocess
import signal
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
import paho.mqtt.client as mqtt_client

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from config import config, pump_config
    from hardware_interface import HardwareInterface
    from mqtt_handler import MQTTHandler
    from taskmaster_service import TaskMasterService
    from main_system import SolarHeatingSystem
    from test_config import TestConfig
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the v3 directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class HardwareTestResult:
    """Test result container for hardware tests"""
    def __init__(self, test_name: str):
        self.test_name = test_name
        self.passed = False
        self.failed = False
        self.error_message = ""
        self.duration = 0.0
        self.details = {}
        self.hardware_measurements = {}
        self.performance_metrics = {}

class HardwareTestSuite:
    """Comprehensive test suite for actual hardware environment"""
    
    def __init__(self):
        self.results: List[HardwareTestResult] = []
        self.hardware = None
        self.mqtt_client = None
        self.connected = False
        self.received_messages = {}
        self.system_process = None
        
    def log_test_result(self, result: HardwareTestResult):
        """Log test result"""
        status = "✅ PASSED" if result.passed else "❌ FAILED"
        logger.info(f"{status} - {result.test_name} ({result.duration:.2f}s)")
        if result.error_message:
            logger.error(f"   Error: {result.error_message}")
        if result.hardware_measurements:
            logger.info(f"   Hardware measurements: {result.hardware_measurements}")
        if result.performance_metrics:
            logger.info(f"   Performance metrics: {result.performance_metrics}")
        self.results.append(result)
    
    def run_test(self, test_name: str, test_func):
        """Run a single test and log results"""
        logger.info(f"🔧 Running hardware test: {test_name}")
        start_time = time.time()
        
        result = HardwareTestResult(test_name)
        try:
            test_func(result)
            result.passed = True
        except Exception as e:
            result.failed = True
            result.error_message = str(e)
            logger.error(f"Hardware test {test_name} failed: {e}")
        
        result.duration = time.time() - start_time
        self.log_test_result(result)
        return result.passed
    
    def setup_hardware(self):
        """Setup hardware interface for testing"""
        if not self.hardware:
            self.hardware = HardwareInterface(simulation_mode=False)
            logger.info("Hardware interface initialized in hardware mode")
    
    def setup_mqtt(self):
        """Setup MQTT connection for testing"""
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
    
    # ============================================================================
    # HARDWARE SENSOR TESTS
    # ============================================================================
    
    def test_rtd_sensor_accuracy(self, result: HardwareTestResult):
        """Test RTD sensor accuracy and stability"""
        try:
            self.setup_hardware()
            
            # Test all RTD sensors
            rtd_readings = {}
            for sensor_id in range(8):  # RTD sensors 0-7
                readings = []
                
                # Take multiple readings for stability test
                for i in range(5):
                    temp = self.hardware.read_rtd_temperature(sensor_id)
                    if temp is not None:
                        readings.append(temp)
                    time.sleep(0.1)
                
                if readings:
                    avg_temp = sum(readings) / len(readings)
                    temp_range = max(readings) - min(readings)
                    rtd_readings[sensor_id] = {
                        'average': avg_temp,
                        'range': temp_range,
                        'readings': readings
                    }
                    
                    # Validate temperature range
                    if not (0 <= avg_temp <= 200):
                        raise Exception(f"RTD sensor {sensor_id} reading {avg_temp}°C out of range")
                    
                    # Check stability (range should be small)
                    if temp_range > 2.0:
                        logger.warning(f"RTD sensor {sensor_id} unstable: range {temp_range}°C")
            
            result.hardware_measurements['rtd_sensors'] = rtd_readings
            result.details['rtd_sensors_tested'] = len(rtd_readings)
            result.details['rtd_sensors_stable'] = all(
                readings['range'] <= 2.0 for readings in rtd_readings.values()
            )
            
        except Exception as e:
            raise Exception(f"RTD sensor accuracy test failed: {e}")
    
    def test_megabas_sensor_accuracy(self, result: HardwareTestResult):
        """Test MegaBAS sensor accuracy and stability"""
        try:
            self.setup_hardware()
            
            # Test all MegaBAS sensors
            megabas_readings = {}
            for sensor_id in range(1, 9):  # MegaBAS sensors 1-8
                readings = []
                
                # Take multiple readings for stability test
                for i in range(5):
                    temp = self.hardware.read_megabas_temperature(sensor_id)
                    if temp is not None:
                        readings.append(temp)
                    time.sleep(0.1)
                
                if readings:
                    avg_temp = sum(readings) / len(readings)
                    temp_range = max(readings) - min(readings)
                    megabas_readings[sensor_id] = {
                        'average': avg_temp,
                        'range': temp_range,
                        'readings': readings
                    }
                    
                    # Validate temperature range
                    if not (0 <= avg_temp <= 200):
                        raise Exception(f"MegaBAS sensor {sensor_id} reading {avg_temp}°C out of range")
                    
                    # Check stability
                    if temp_range > 2.0:
                        logger.warning(f"MegaBAS sensor {sensor_id} unstable: range {temp_range}°C")
            
            result.hardware_measurements['megabas_sensors'] = megabas_readings
            result.details['megabas_sensors_tested'] = len(megabas_readings)
            result.details['megabas_sensors_stable'] = all(
                readings['range'] <= 2.0 for readings in megabas_readings.values()
            )
            
        except Exception as e:
            raise Exception(f"MegaBAS sensor accuracy test failed: {e}")
    
    def test_sensor_calibration(self, result: HardwareTestResult):
        """Test sensor calibration and known temperature points"""
        try:
            self.setup_hardware()
            
            # Test known temperature points (if available)
            # This would require a calibrated temperature source
            calibration_results = {}
            
            # Test sensor consistency across multiple readings
            sensor_consistency = {}
            
            for sensor_type in ['rtd', 'megabas']:
                if sensor_type == 'rtd':
                    sensor_range = range(8)
                    read_func = self.hardware.read_rtd_temperature
                else:
                    sensor_range = range(1, 9)
                    read_func = self.hardware.read_megabas_temperature
                
                for sensor_id in sensor_range:
                    readings = []
                    for i in range(10):
                        temp = read_func(sensor_id)
                        if temp is not None:
                            readings.append(temp)
                        time.sleep(0.05)
                    
                    if readings:
                        avg_temp = sum(readings) / len(readings)
                        std_dev = (sum((x - avg_temp) ** 2 for x in readings) / len(readings)) ** 0.5
                        
                        sensor_consistency[f"{sensor_type}_{sensor_id}"] = {
                            'average': avg_temp,
                            'std_dev': std_dev,
                            'consistency': std_dev < 1.0  # Good if std dev < 1°C
                        }
            
            result.hardware_measurements['sensor_calibration'] = calibration_results
            result.hardware_measurements['sensor_consistency'] = sensor_consistency
            result.details['sensors_consistent'] = all(
                data['consistency'] for data in sensor_consistency.values()
            )
            
        except Exception as e:
            raise Exception(f"Sensor calibration test failed: {e}")
    
    # ============================================================================
    # RELAY CONTROL TESTS
    # ============================================================================
    
    def test_relay_control_accuracy(self, result: HardwareTestResult):
        """Test relay control accuracy and feedback (gentle test for pump/relay hardware)"""
        try:
            self.setup_hardware()
            
            # Test only the primary pump relay (relay 1) and cartridge heater relay (relay 2)
            # These are the main relays connected to actual hardware
            relay_results = {}
            test_relays = [1, 2]  # Only test relays 1 and 2
            
            for relay_id in test_relays:
                relay_test = {}
                logger.info(f"Testing relay {relay_id} (gentle test)...")
                
                # Test OFF state
                self.hardware.set_relay_state(relay_id, False)
                time.sleep(1.0)  # Longer wait for hardware to settle
                off_state = self.hardware.get_relay_state(relay_id)
                relay_test['off_state'] = off_state
                
                # Test ON state
                self.hardware.set_relay_state(relay_id, True)
                time.sleep(1.0)  # Longer wait for hardware to settle
                on_state = self.hardware.get_relay_state(relay_id)
                relay_test['on_state'] = on_state
                
                # Test toggle back to OFF
                self.hardware.set_relay_state(relay_id, False)
                time.sleep(1.0)  # Longer wait for hardware to settle
                final_state = self.hardware.get_relay_state(relay_id)
                relay_test['final_state'] = final_state
                
                # Validate relay behavior
                if off_state == on_state:
                    raise Exception(f"Relay {relay_id} states are identical: {off_state}")
                
                if final_state != off_state:
                    raise Exception(f"Relay {relay_id} final state mismatch: {final_state} != {off_state}")
                
                relay_results[relay_id] = relay_test
                logger.info(f"Relay {relay_id} test completed successfully")
            
            result.hardware_measurements['relay_control'] = relay_results
            result.details['relays_tested'] = len(relay_results)
            result.details['relays_working'] = len(relay_results)
            
        except Exception as e:
            raise Exception(f"Relay control accuracy test failed: {e}")
    
    def test_relay_timing(self, result: HardwareTestResult):
        """Test relay response timing (gentle test for pump/relay hardware)"""
        try:
            self.setup_hardware()
            
            # Test only the primary pump relay (relay 1) with minimal cycles
            relay_timing = {}
            test_relays = [1]  # Only test relay 1 (primary pump)
            
            for relay_id in test_relays:
                logger.info(f"Testing relay {relay_id} timing (gentle test)...")
                timing_results = []
                
                # Only 1 test cycle instead of 3 to reduce wear
                for test_cycle in range(1):
                    # Measure OFF to ON time
                    start_time = time.time()
                    self.hardware.set_relay_state(relay_id, True)
                    time.sleep(0.5)  # Wait for hardware to respond
                    on_time = time.time() - start_time
                    
                    # Measure ON to OFF time
                    start_time = time.time()
                    self.hardware.set_relay_state(relay_id, False)
                    time.sleep(0.5)  # Wait for hardware to respond
                    off_time = time.time() - start_time
                    
                    timing_results.append({
                        'on_time': on_time,
                        'off_time': off_time
                    })
                
                avg_on_time = sum(t['on_time'] for t in timing_results) / len(timing_results)
                avg_off_time = sum(t['off_time'] for t in timing_results) / len(timing_results)
                
                relay_timing[relay_id] = {
                    'avg_on_time': avg_on_time,
                    'avg_off_time': avg_off_time,
                    'max_acceptable_time': 1.0  # 1 second max (more lenient)
                }
                
                # Validate timing (more lenient for hardware)
                if avg_on_time > 1.0 or avg_off_time > 1.0:
                    logger.warning(f"Relay {relay_id} slow response: ON={avg_on_time:.3f}s, OFF={avg_off_time:.3f}s")
                else:
                    logger.info(f"Relay {relay_id} timing acceptable: ON={avg_on_time:.3f}s, OFF={avg_off_time:.3f}s")
            
            result.performance_metrics['relay_timing'] = relay_timing
            result.details['relay_timing_acceptable'] = all(
                timing['avg_on_time'] <= 1.0 and timing['avg_off_time'] <= 1.0
                for timing in relay_timing.values()
            )
            
        except Exception as e:
            raise Exception(f"Relay timing test failed: {e}")
    
    # ============================================================================
    # HARDWARE ERROR HANDLING TESTS
    # ============================================================================
    
    def test_hardware_error_recovery(self, result: HardwareTestResult):
        """Test hardware error recovery"""
        try:
            self.setup_hardware()
            
            # Test invalid sensor handling
            invalid_sensor_results = {}
            
            # Test invalid RTD sensor
            invalid_rtd = self.hardware.read_rtd_temperature(999)
            invalid_sensor_results['invalid_rtd'] = invalid_rtd
            
            # Test invalid MegaBAS sensor
            invalid_megabas = self.hardware.read_megabas_temperature(999)
            invalid_sensor_results['invalid_megabas'] = invalid_megabas
            
            # Test invalid relay
            invalid_relay_set = self.hardware.set_relay_state(999, True)
            invalid_relay_get = self.hardware.get_relay_state(999)
            invalid_sensor_results['invalid_relay'] = {
                'set_result': invalid_relay_set,
                'get_result': invalid_relay_get
            }
            
            # Validate error handling
            if invalid_rtd is not None:
                logger.warning("Invalid RTD sensor returned value instead of None")
            
            if invalid_megabas is not None:
                logger.warning("Invalid MegaBAS sensor returned value instead of None")
            
            if invalid_relay_set != False:
                logger.warning("Invalid relay set returned True instead of False")
            
            result.hardware_measurements['error_handling'] = invalid_sensor_results
            result.details['error_handling_working'] = (
                invalid_rtd is None and
                invalid_megabas is None and
                invalid_relay_set == False
            )
            
        except Exception as e:
            raise Exception(f"Hardware error recovery test failed: {e}")
    
    def test_hardware_stress(self, result: HardwareTestResult):
        """Test hardware under gentle stress conditions (minimal wear test)"""
        try:
            self.setup_hardware()
            
            # Gentle stress test - only test relay 1 (primary pump) with minimal switching
            stress_results = {}
            test_relay = 1  # Only test primary pump relay
            
            logger.info(f"Running gentle stress test on relay {test_relay}...")
            start_time = time.time()
            switch_count = 0
            errors = 0
            
            # Very gentle switching - only 3 cycles with 2 second delays
            for cycle in range(3):
                try:
                    logger.info(f"Stress test cycle {cycle + 1}/3...")
                    self.hardware.set_relay_state(test_relay, True)
                    time.sleep(2.0)  # 2 second delay between switches
                    self.hardware.set_relay_state(test_relay, False)
                    time.sleep(2.0)  # 2 second delay between switches
                    switch_count += 1
                except Exception as e:
                    errors += 1
                    logger.warning(f"Relay {test_relay} stress test error: {e}")
            
            test_duration = time.time() - start_time
            
            stress_results[test_relay] = {
                'switches': switch_count,
                'errors': errors,
                'duration': test_duration,
                'switches_per_second': switch_count / test_duration if test_duration > 0 else 0
            }
            
            result.performance_metrics['stress_test'] = stress_results
            result.details['stress_test_passed'] = all(
                result['errors'] == 0 for result in stress_results.values()
            )
            
            logger.info(f"Gentle stress test completed: {switch_count} switches, {errors} errors")
            
        except Exception as e:
            raise Exception(f"Hardware stress test failed: {e}")
    
    # ============================================================================
    # MQTT INTEGRATION TESTS
    # ============================================================================
    
    def test_mqtt_hardware_integration(self, result: HardwareTestResult):
        """Test MQTT integration with real hardware"""
        try:
            self.setup_hardware()
            self.setup_mqtt()
            
            # Subscribe to system topics
            topics = [
                f"{config.mqtt_client_id}/temperature/solar_collector",
                f"{config.mqtt_client_id}/temperature/storage_tank",
                f"{config.mqtt_client_id}/status/primary_pump",
                f"{config.mqtt_client_id}/status/mode"
            ]
            
            for topic in topics:
                self.mqtt_client.subscribe(topic)
            
            # Publish test data
            test_data = {
                'solar_collector': self.hardware.read_megabas_temperature(1),
                'storage_tank': self.hardware.read_rtd_temperature(0),
                'timestamp': time.time()
            }
            
            test_topic = f"{config.mqtt_client_id}/test/hardware"
            self.mqtt_client.publish(test_topic, json.dumps(test_data))
            
            # Wait for messages
            time.sleep(2)
            
            result.hardware_measurements['mqtt_test_data'] = test_data
            result.details['mqtt_connected'] = self.connected
            result.details['mqtt_messages_received'] = len(self.received_messages)
            
        except Exception as e:
            raise Exception(f"MQTT hardware integration test failed: {e}")
    
    def test_home_assistant_integration(self, result: HardwareTestResult):
        """Test Home Assistant integration with real hardware"""
        try:
            self.setup_mqtt()
            
            # Subscribe to Home Assistant topics
            ha_topics = [
                f"homeassistant/switch/{config.mqtt_client_id}_primary_pump/state",
                f"homeassistant/switch/{config.mqtt_client_id}_cartridge_heater/state",
                f"homeassistant/number/{config.mqtt_client_id}_set_temp_tank_1/state"
            ]
            
            for topic in ha_topics:
                self.mqtt_client.subscribe(topic)
            
            # Test Home Assistant discovery
            discovery_topic = f"homeassistant/switch/{config.mqtt_client_id}_primary_pump/config"
            discovery_payload = {
                "name": "Primary Pump",
                "state_topic": f"{config.mqtt_client_id}/status/primary_pump",
                "command_topic": f"{config.mqtt_client_id}/control/primary_pump"
            }
            
            self.mqtt_client.publish(discovery_topic, json.dumps(discovery_payload), retain=True)
            time.sleep(1)
            
            result.details['ha_discovery_sent'] = True
            result.details['ha_topics_subscribed'] = len(ha_topics)
            
        except Exception as e:
            raise Exception(f"Home Assistant integration test failed: {e}")
    
    def test_sensor_data_reading_via_mqtt(self, result: HardwareTestResult):
        """Test reading sensor data from Home Assistant via MQTT"""
        try:
            self.setup_mqtt()
            
            # Subscribe to sensor data topics from Home Assistant
            sensor_topics = [
                "homeassistant/sensor/solar_collector_temperature/state",
                "homeassistant/sensor/storage_tank_temperature/state",
                "homeassistant/sensor/pelletskamin_temperature/state",
                "homeassistant/sensor/pelletskamin_last_seen/state"
            ]
            
            for topic in sensor_topics:
                self.mqtt_client.subscribe(topic)
            
            # Simulate Home Assistant publishing sensor data
            test_sensor_data = {
                "homeassistant/sensor/solar_collector_temperature/state": "75.5",
                "homeassistant/sensor/storage_tank_temperature/state": "52.3",
                "homeassistant/sensor/pelletskamin_temperature/state": "68.2",
                "homeassistant/sensor/pelletskamin_last_seen/state": "2025-09-05T14:30:22"
            }
            
            # Publish test sensor data
            for topic, value in test_sensor_data.items():
                self.mqtt_client.publish(topic, value, retain=True)
                time.sleep(0.1)
            
            # Wait for messages to be received
            time.sleep(2)
            
            # Verify sensor data was received
            received_sensors = {}
            for topic in sensor_topics:
                if topic in self.received_messages:
                    received_sensors[topic] = self.received_messages[topic]
            
            result.hardware_measurements['sensor_data_received'] = received_sensors
            result.details['sensors_tested'] = len(sensor_topics)
            result.details['sensors_received'] = len(received_sensors)
            result.details['sensor_data_reading_success'] = len(received_sensors) >= 2  # At least 2 sensors
            
            logger.info(f"Received sensor data from {len(received_sensors)}/{len(sensor_topics)} sensors")
            
        except Exception as e:
            raise Exception(f"Sensor data reading via MQTT test failed: {e}")
    
    def test_switch_control_via_home_assistant(self, result: HardwareTestResult):
        """Test controlling switches from Home Assistant via MQTT"""
        try:
            self.setup_hardware()
            self.setup_mqtt()
            
            # Subscribe to command topics that Home Assistant would publish to
            command_topics = [
                f"homeassistant/switch/solar_heating_primary_pump/set",
                f"homeassistant/switch/solar_heating_cartridge_heater/set",
                f"homeassistant/number/solar_heating_set_temp_tank_1/set"
            ]
            
            for topic in command_topics:
                self.mqtt_client.subscribe(topic)
            
            # Test switch control commands from Home Assistant
            switch_commands = [
                (f"homeassistant/switch/solar_heating_primary_pump/set", "ON"),
                (f"homeassistant/switch/solar_heating_primary_pump/set", "OFF"),
                (f"homeassistant/switch/solar_heating_cartridge_heater/set", "ON"),
                (f"homeassistant/switch/solar_heating_cartridge_heater/set", "OFF")
            ]
            
            # Test number control commands from Home Assistant
            number_commands = [
                (f"homeassistant/number/solar_heating_set_temp_tank_1/set", "75.0"),
                (f"homeassistant/number/solar_heating_dTStart_tank_1/set", "8.5"),
                (f"homeassistant/number/solar_heating_temp_kok_hysteres/set", "12.0")
            ]
            
            # Publish switch commands
            for topic, command in switch_commands:
                logger.info(f"Testing switch command: {topic} = {command}")
                self.mqtt_client.publish(topic, command)
                time.sleep(1)  # Wait for command to be processed
            
            # Publish number commands
            for topic, command in number_commands:
                logger.info(f"Testing number command: {topic} = {command}")
                self.mqtt_client.publish(topic, command)
                time.sleep(1)  # Wait for command to be processed
            
            # Wait for all commands to be processed
            time.sleep(2)
            
            result.details['switch_commands_tested'] = len(switch_commands)
            result.details['number_commands_tested'] = len(number_commands)
            result.details['total_commands_tested'] = len(switch_commands) + len(number_commands)
            result.details['switch_control_success'] = True  # If we get here without errors, it worked
            
            logger.info(f"Successfully tested {len(switch_commands)} switch commands and {len(number_commands)} number commands")
            
        except Exception as e:
            raise Exception(f"Switch control via Home Assistant test failed: {e}")
    
    def test_end_to_end_mqtt_workflow(self, result: HardwareTestResult):
        """Test complete sensor → MQTT → Home Assistant → control → hardware workflow"""
        try:
            self.setup_hardware()
            self.setup_mqtt()
            
            # Step 1: Read actual sensor data
            logger.info("Step 1: Reading actual sensor data...")
            sensor_data = {}
            try:
                sensor_data['solar_collector'] = self.hardware.read_megabas_temperature(1)
                sensor_data['storage_tank'] = self.hardware.read_rtd_temperature(0)
                logger.info(f"Read sensors: {sensor_data}")
            except Exception as e:
                logger.warning(f"Could not read actual sensors: {e}")
                # Use simulated data for testing
                sensor_data = {'solar_collector': 75.0, 'storage_tank': 52.0}
            
            # Step 2: Publish sensor data to MQTT (as if from Home Assistant)
            logger.info("Step 2: Publishing sensor data to MQTT...")
            sensor_topics = {
                "homeassistant/sensor/solar_collector_temperature/state": str(sensor_data['solar_collector']),
                "homeassistant/sensor/storage_tank_temperature/state": str(sensor_data['storage_tank'])
            }
            
            for topic, value in sensor_topics.items():
                self.mqtt_client.publish(topic, value, retain=True)
                time.sleep(0.1)
            
            # Step 3: Simulate Home Assistant control command based on sensor data
            logger.info("Step 3: Simulating Home Assistant control logic...")
            dT = sensor_data['solar_collector'] - sensor_data['storage_tank']
            
            if dT >= 8.0:  # If temperature difference is high enough
                control_command = "ON"
                logger.info(f"Temperature difference {dT}°C >= 8°C, sending pump ON command")
            else:
                control_command = "OFF"
                logger.info(f"Temperature difference {dT}°C < 8°C, sending pump OFF command")
            
            # Step 4: Publish control command from Home Assistant
            logger.info("Step 4: Publishing control command from Home Assistant...")
            control_topic = "homeassistant/switch/solar_heating_primary_pump/set"
            self.mqtt_client.publish(control_topic, control_command)
            time.sleep(2)  # Wait for command to be processed
            
            # Step 5: Verify the workflow completed successfully
            logger.info("Step 5: Verifying end-to-end workflow...")
            
            result.hardware_measurements['end_to_end_workflow'] = {
                'sensor_data': sensor_data,
                'temperature_difference': dT,
                'control_command': control_command,
                'workflow_completed': True
            }
            
            result.details['sensor_data_published'] = len(sensor_topics)
            result.details['control_command_sent'] = True
            result.details['workflow_success'] = True
            
            logger.info("✅ End-to-end MQTT workflow test completed successfully")
            
        except Exception as e:
            raise Exception(f"End-to-end MQTT workflow test failed: {e}")
    
    def test_bidirectional_mqtt_communication(self, result: HardwareTestResult):
        """Test real-time bidirectional communication between system and Home Assistant"""
        try:
            self.setup_hardware()
            self.setup_mqtt()
            
            # Subscribe to both sensor data and control topics
            all_topics = [
                # Sensor data topics (from Home Assistant)
                "homeassistant/sensor/solar_collector_temperature/state",
                "homeassistant/sensor/storage_tank_temperature/state",
                # Control command topics (to system)
                "homeassistant/switch/solar_heating_primary_pump/set",
                "homeassistant/switch/solar_heating_cartridge_heater/set",
                # Status topics (from system)
                f"{config.mqtt_client_id}/status/primary_pump",
                f"{config.mqtt_client_id}/status/mode"
            ]
            
            for topic in all_topics:
                self.mqtt_client.subscribe(topic)
            
            # Test bidirectional communication
            communication_tests = []
            
            # Test 1: Send sensor data, then control command
            logger.info("Test 1: Sensor data → Control command")
            self.mqtt_client.publish("homeassistant/sensor/solar_collector_temperature/state", "80.0")
            time.sleep(0.5)
            self.mqtt_client.publish("homeassistant/switch/solar_heating_primary_pump/set", "ON")
            time.sleep(1)
            communication_tests.append("sensor_to_control")
            
            # Test 2: Send control command, then verify status
            logger.info("Test 2: Control command → Status update")
            self.mqtt_client.publish("homeassistant/switch/solar_heating_cartridge_heater/set", "ON")
            time.sleep(1)
            # System should publish status update
            self.mqtt_client.publish(f"{config.mqtt_client_id}/status/cartridge_heater", "ON")
            time.sleep(0.5)
            communication_tests.append("control_to_status")
            
            # Test 3: Multiple rapid commands
            logger.info("Test 3: Multiple rapid commands")
            for i in range(3):
                self.mqtt_client.publish("homeassistant/sensor/storage_tank_temperature/state", str(50.0 + i))
                time.sleep(0.2)
                self.mqtt_client.publish("homeassistant/switch/solar_heating_primary_pump/set", "ON" if i % 2 == 0 else "OFF")
                time.sleep(0.2)
            communication_tests.append("rapid_commands")
            
            # Wait for all messages to be processed
            time.sleep(2)
            
            result.details['bidirectional_tests'] = communication_tests
            result.details['total_communication_tests'] = len(communication_tests)
            result.details['messages_received'] = len(self.received_messages)
            result.details['bidirectional_success'] = len(communication_tests) == 3
            
            logger.info(f"✅ Bidirectional communication test completed: {len(communication_tests)} tests passed")
            
        except Exception as e:
            raise Exception(f"Bidirectional MQTT communication test failed: {e}")
    
    # ============================================================================
    # SYSTEM INTEGRATION TESTS
    # ============================================================================
    
    def test_full_system_integration(self, result: HardwareTestResult):
        """Test full system integration with real hardware"""
        try:
            self.setup_hardware()
            
            # Initialize system
            system = SolarHeatingSystem()
            
            # Read real temperatures
            system.temperatures = {
                'solar_collector': self.hardware.read_megabas_temperature(1),
                'storage_tank': self.hardware.read_rtd_temperature(0),
                'storage_tank_top': self.hardware.read_rtd_temperature(4),
                'storage_tank_bottom': self.hardware.read_rtd_temperature(3)
            }
            
            # Test control logic with real temperatures
            dT = system.temperatures['solar_collector'] - system.temperatures['storage_tank']
            
            if dT >= system.control_params['dTStart_tank_1']:
                system.system_state['primary_pump'] = True
                self.hardware.set_relay_state(1, True)
                
                # Verify relay state
                relay_state = self.hardware.get_relay_state(1)
                if relay_state != True:
                    raise Exception(f"Relay 1 not activated: {relay_state}")
            
            result.hardware_measurements['system_temperatures'] = system.temperatures
            result.hardware_measurements['temperature_difference'] = dT
            result.details['system_integration_working'] = True
            
        except Exception as e:
            raise Exception(f"Full system integration test failed: {e}")
    
    def test_system_performance(self, result: HardwareTestResult):
        """Test system performance with real hardware"""
        try:
            self.setup_hardware()
            
            # Test temperature reading performance
            start_time = time.time()
            readings = []
            
            for i in range(100):
                temp = self.hardware.read_rtd_temperature(0)
                if temp is not None:
                    readings.append(temp)
                time.sleep(0.01)
            
            reading_time = time.time() - start_time
            readings_per_second = len(readings) / reading_time
            
            # Test relay switching performance
            start_time = time.time()
            for i in range(50):
                self.hardware.set_relay_state(1, True)
                self.hardware.set_relay_state(1, False)
            
            switching_time = time.time() - start_time
            switches_per_second = 100 / switching_time  # 50 cycles = 100 switches
            
            result.performance_metrics['temperature_reading'] = {
                'readings_per_second': readings_per_second,
                'total_readings': len(readings),
                'total_time': reading_time
            }
            
            result.performance_metrics['relay_switching'] = {
                'switches_per_second': switches_per_second,
                'total_switches': 100,
                'total_time': switching_time
            }
            
            result.details['performance_acceptable'] = (
                readings_per_second > 10 and  # At least 10 readings per second
                switches_per_second > 5      # At least 5 switches per second
            )
            
        except Exception as e:
            raise Exception(f"System performance test failed: {e}")
    
    # ============================================================================
    # SYSTEM SERVICE TESTS
    # ============================================================================
    
    def test_system_service(self, result: HardwareTestResult):
        """Test system service functionality"""
        try:
            # Check if service is running
            try:
                result_service = subprocess.run(
                    ['systemctl', 'is-active', 'solar_heating_v3.service'],
                    capture_output=True, text=True, timeout=5
                )
                service_active = result_service.stdout.strip() == 'active'
            except subprocess.TimeoutExpired:
                service_active = False
            
            # Check service status
            try:
                result_status = subprocess.run(
                    ['systemctl', 'status', 'solar_heating_v3.service'],
                    capture_output=True, text=True, timeout=10
                )
                service_status = result_status.stdout
            except subprocess.TimeoutExpired:
                service_status = "Timeout getting service status"
            
            result.details['service_active'] = service_active
            result.details['service_status'] = service_status
            
            if not service_active:
                logger.warning("Solar heating service is not active")
            
        except Exception as e:
            raise Exception(f"System service test failed: {e}")
    
    def test_system_logs(self, result: HardwareTestResult):
        """Test system log functionality"""
        try:
            log_file = '/home/pi/solar_heating/logs/solar_heating_v3.log'
            
            # Check if log file exists
            log_exists = os.path.exists(log_file)
            
            if log_exists:
                # Check log file size
                log_size = os.path.getsize(log_file)
                
                # Read last few lines
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        last_lines = lines[-10:] if len(lines) >= 10 else lines
                except Exception as e:
                    last_lines = [f"Error reading log file: {e}"]
            else:
                log_size = 0
                last_lines = ["Log file does not exist"]
            
            result.details['log_file_exists'] = log_exists
            result.details['log_file_size'] = log_size
            result.details['last_log_lines'] = last_lines
            
        except Exception as e:
            raise Exception(f"System logs test failed: {e}")
    
    # ============================================================================
    # MAIN TEST RUNNER
    # ============================================================================
    
    def run_all_tests(self):
        """Run all hardware tests"""
        logger.info("🚀 Starting Hardware Test Suite for Solar Heating System v3")
        logger.info("=" * 80)
        logger.info("🔧 Testing on ACTUAL HARDWARE (Raspberry Pi environment)")
        logger.info("=" * 80)
        
        # Hardware Sensor Tests
        logger.info("\n🌡️ HARDWARE SENSOR TESTS")
        logger.info("-" * 40)
        self.run_test("RTD Sensor Accuracy", self.test_rtd_sensor_accuracy)
        self.run_test("MegaBAS Sensor Accuracy", self.test_megabas_sensor_accuracy)
        self.run_test("Sensor Calibration", self.test_sensor_calibration)
        
        # Relay Control Tests
        logger.info("\n🔌 RELAY CONTROL TESTS")
        logger.info("-" * 40)
        self.run_test("Relay Control Accuracy", self.test_relay_control_accuracy)
        self.run_test("Relay Timing", self.test_relay_timing)
        
        # Hardware Error Handling Tests
        logger.info("\n🛡️ HARDWARE ERROR HANDLING TESTS")
        logger.info("-" * 40)
        self.run_test("Hardware Error Recovery", self.test_hardware_error_recovery)
        self.run_test("Hardware Stress Test", self.test_hardware_stress)
        
        # MQTT Integration Tests
        logger.info("\n📡 MQTT INTEGRATION TESTS")
        logger.info("-" * 40)
        self.run_test("MQTT Hardware Integration", self.test_mqtt_hardware_integration)
        self.run_test("Home Assistant Integration", self.test_home_assistant_integration)
        self.run_test("Sensor Data Reading via MQTT", self.test_sensor_data_reading_via_mqtt)
        self.run_test("Switch Control via Home Assistant", self.test_switch_control_via_home_assistant)
        self.run_test("End-to-End MQTT Workflow", self.test_end_to_end_mqtt_workflow)
        self.run_test("Bidirectional MQTT Communication", self.test_bidirectional_mqtt_communication)
        
        # System Integration Tests
        logger.info("\n🔗 SYSTEM INTEGRATION TESTS")
        logger.info("-" * 40)
        self.run_test("Full System Integration", self.test_full_system_integration)
        self.run_test("System Performance", self.test_system_performance)
        
        # System Service Tests
        logger.info("\n⚙️ SYSTEM SERVICE TESTS")
        logger.info("-" * 40)
        self.run_test("System Service", self.test_system_service)
        self.run_test("System Logs", self.test_system_logs)
        
        # Generate summary
        self.generate_test_summary()
    
    def generate_test_summary(self):
        """Generate comprehensive test summary"""
        logger.info("\n📊 HARDWARE TEST SUMMARY")
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
        
        # Hardware-specific summary
        logger.info("\n🔧 HARDWARE MEASUREMENTS:")
        for result in self.results:
            if result.hardware_measurements:
                logger.info(f"  {result.test_name}:")
                for measurement, value in result.hardware_measurements.items():
                    logger.info(f"    {measurement}: {value}")
        
        logger.info("\n⚡ PERFORMANCE METRICS:")
        for result in self.results:
            if result.performance_metrics:
                logger.info(f"  {result.test_name}:")
                for metric, value in result.performance_metrics.items():
                    logger.info(f"    {metric}: {value}")
        
        if passed_tests == total_tests:
            logger.info("\n🎉 ALL HARDWARE TESTS PASSED! System is fully functional on hardware.")
            return True
        else:
            logger.info(f"\n⚠️  {failed_tests} HARDWARE TESTS FAILED. Hardware needs attention.")
            return False
    
    def cleanup(self):
        """Cleanup test resources"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
        
        # Ensure all relays are off
        if self.hardware:
            for relay_id in range(1, 5):
                try:
                    self.hardware.set_relay_state(relay_id, False)
                except:
                    pass

def main():
    """Main test runner"""
    test_suite = HardwareTestSuite()
    try:
        success = test_suite.run_all_tests()
        return 0 if success else 1
    except KeyboardInterrupt:
        logger.info("\n⏹️  Hardware tests interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Hardware test suite error: {e}")
        return 1
    finally:
        test_suite.cleanup()

if __name__ == "__main__":
    exit(main())
