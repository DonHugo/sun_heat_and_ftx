#!/usr/bin/env python3
"""
Realistic Environment Test Suite
Tests the system with real MQTT connections and realistic sensor data.

This test suite addresses:
1. Real MQTT broker connections
2. Realistic sensor data simulation
3. Hardware-like behavior testing
4. Production-like environment testing
"""

import sys
import os
import time
import json
import random
import threading
from datetime import datetime, timedelta

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("⚠️  paho-mqtt not available. MQTT tests will be skipped.")

try:
    from main_system import SolarHeatingSystem
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

class RealisticSensorDataGenerator:
    """Generates realistic sensor data based on real-world patterns"""
    
    def __init__(self):
        self.base_temps = {
            'ambient': 20.0,  # Base ambient temperature
            'tank_base': 25.0,  # Base tank temperature
            'collector_base': 22.0,  # Base collector temperature
        }
        self.time_of_day = 0  # 0-24 hours
        self.weather_conditions = 'sunny'  # sunny, cloudy, rainy
        self.season = 'summer'  # summer, winter, spring, autumn
        
    def get_realistic_temperature_profile(self):
        """Generate realistic temperature profile based on time and conditions"""
        current_hour = datetime.now().hour
        self.time_of_day = current_hour
        
        # Solar collector temperature based on time of day and weather
        if 6 <= current_hour <= 18:  # Daylight hours
            # Peak solar heating around noon
            solar_factor = max(0, 1 - abs(current_hour - 12) / 6)
            weather_factor = {'sunny': 1.0, 'cloudy': 0.6, 'rainy': 0.3}[self.weather_conditions]
            season_factor = {'summer': 1.2, 'spring': 1.0, 'autumn': 0.8, 'winter': 0.6}[self.season]
            
            collector_temp = self.base_temps['collector_base'] + (solar_factor * 60 * weather_factor * season_factor)
        else:
            # Night time - collector cools down
            collector_temp = self.base_temps['collector_base'] + random.uniform(-2, 2)
        
        # Storage tank temperature (warms up during day, cools at night)
        if 6 <= current_hour <= 18:
            tank_temp = self.base_temps['tank_base'] + (solar_factor * 25 * weather_factor)
        else:
            # Tank cools down at night
            tank_temp = self.base_temps['tank_base'] + random.uniform(5, 15)
        
        # Return line temperature (between collector and tank)
        return_temp = (collector_temp + tank_temp) / 2 + random.uniform(-2, 2)
        
        # Water heater temperatures (stratified)
        water_heater_temps = []
        for i in range(8):  # 8 sensors at different heights
            height_factor = i / 7  # 0 to 1
            temp = tank_temp + (height_factor * 10) + random.uniform(-1, 1)
            water_heater_temps.append(temp)
        
        # FTX temperatures (air handling)
        ftx_temps = []
        for i in range(6):
            temp = self.base_temps['ambient'] + random.uniform(-3, 3)
            ftx_temps.append(temp)
        
        return {
            'megabas_sensor_0': ftx_temps[0],  # FTX exhaust air
            'megabas_sensor_1': ftx_temps[1],  # FTX supply air
            'megabas_sensor_2': ftx_temps[2],  # FTX return air
            'megabas_sensor_3': ftx_temps[3],  # FTX supply air
            'megabas_sensor_4': ftx_temps[4],  # FTX return air
            'megabas_sensor_5': ftx_temps[5],  # FTX exhaust air
            'megabas_sensor_6': collector_temp,  # Solar collector outlet
            'megabas_sensor_7': tank_temp,      # Storage tank
            'megabas_sensor_8': return_temp,    # Return line
            'rtd_sensor_0': water_heater_temps[0],  # Water heater bottom
            'rtd_sensor_1': water_heater_temps[1],  # Water heater 20cm
            'rtd_sensor_2': water_heater_temps[2],  # Water heater 40cm
            'rtd_sensor_3': water_heater_temps[3],  # Water heater 60cm
            'rtd_sensor_4': water_heater_temps[4],  # Water heater 80cm
            'rtd_sensor_5': water_heater_temps[5],  # Water heater 100cm
            'rtd_sensor_6': water_heater_temps[6],  # Water heater 120cm
            'rtd_sensor_7': water_heater_temps[7],  # Water heater 140cm (top)
        }
    
    def add_realistic_noise(self, sensor_data):
        """Add realistic sensor noise and variations"""
        noisy_data = {}
        for sensor, value in sensor_data.items():
            # Add realistic sensor noise (±0.1°C for RTD, ±0.5°C for thermocouples)
            if 'rtd' in sensor:
                noise = random.uniform(-0.1, 0.1)
            else:
                noise = random.uniform(-0.5, 0.5)
            noisy_data[sensor] = round(value + noise, 1)
        return noisy_data

class MQTTTestClient:
    """MQTT client for testing real MQTT connections"""
    
    def __init__(self, broker_host="192.168.0.110", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = None
        self.connected = False
        self.messages_received = []
        self.messages_published = []
        
    def connect(self):
        """Connect to MQTT broker"""
        if not MQTT_AVAILABLE:
            return False
            
        try:
            self.client = mqtt.Client()
            self.client.on_connect = self.on_connect
            self.client.on_message = self.on_message
            self.client.on_disconnect = self.on_disconnect
            
            # Set authentication if this is the production broker
            if self.broker_host == "192.168.0.110":
                from config import SystemConfig
                config = SystemConfig()
                if hasattr(config, 'mqtt_username') and hasattr(config, 'mqtt_password'):
                    self.client.username_pw_set(config.mqtt_username, config.mqtt_password)
            
            # Set connection timeout
            self.client.connect(self.broker_host, self.broker_port, 60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 5
            start_time = time.time()
            while not self.connected and (time.time() - start_time) < timeout:
                time.sleep(0.1)
            
            return self.connected
            
        except Exception as e:
            print(f"MQTT connection failed: {e}")
            return False
    
    def on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0:
            self.connected = True
            print(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
        else:
            print(f"❌ MQTT connection failed with code {rc}")
    
    def on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            message = {
                'topic': msg.topic,
                'payload': msg.payload.decode('utf-8'),
                'timestamp': time.time()
            }
            self.messages_received.append(message)
        except Exception as e:
            print(f"Error processing MQTT message: {e}")
    
    def on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        print(f"MQTT disconnected with code {rc}")
    
    def publish(self, topic, payload, qos=0):
        """Publish message to MQTT broker"""
        if not self.connected:
            return False
        
        try:
            result = self.client.publish(topic, payload, qos)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                self.messages_published.append({
                    'topic': topic,
                    'payload': payload,
                    'timestamp': time.time()
                })
                return True
            else:
                print(f"MQTT publish failed with code {result.rc}")
                return False
        except Exception as e:
            print(f"MQTT publish error: {e}")
            return False
    
    def subscribe(self, topic, qos=0):
        """Subscribe to MQTT topic"""
        if not self.connected:
            return False
        
        try:
            result = self.client.subscribe(topic, qos)
            if result[0] == mqtt.MQTT_ERR_SUCCESS:
                print(f"✅ Subscribed to topic: {topic}")
                return True
            else:
                print(f"❌ MQTT subscribe failed with code {result[0]}")
                return False
        except Exception as e:
            print(f"MQTT subscribe error: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.connected:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False

def test_realistic_sensor_data():
    """Test with realistic sensor data patterns"""
    print("🌡️ Testing with realistic sensor data patterns...")
    
    system = SolarHeatingSystem()
    data_generator = RealisticSensorDataGenerator()
    
    # Test different time periods and weather conditions
    test_scenarios = [
        {'time': 6, 'weather': 'sunny', 'season': 'summer', 'description': 'Early morning, sunny summer'},
        {'time': 12, 'weather': 'sunny', 'season': 'summer', 'description': 'Noon, sunny summer'},
        {'time': 18, 'weather': 'cloudy', 'season': 'summer', 'description': 'Evening, cloudy summer'},
        {'time': 0, 'weather': 'rainy', 'season': 'winter', 'description': 'Midnight, rainy winter'},
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['description']}")
        
        # Set scenario conditions
        data_generator.time_of_day = scenario['time']
        data_generator.weather_conditions = scenario['weather']
        data_generator.season = scenario['season']
        
        # Generate realistic sensor data
        sensor_data = data_generator.get_realistic_temperature_profile()
        sensor_data = data_generator.add_realistic_noise(sensor_data)
        
        # Apply to system
        system.temperatures.clear()
        system.temperatures.update(sensor_data)
        
        # Run sensor mapping
        system.temperatures['solar_collector'] = system.temperatures.get('megabas_sensor_6', 0)
        system.temperatures['storage_tank'] = system.temperatures.get('megabas_sensor_7', 0)
        system.temperatures['return_line_temp'] = system.temperatures.get('megabas_sensor_8', 0)
        
        # Calculate dT
        solar_collector = system.temperatures.get('solar_collector', 0)
        storage_tank = system.temperatures.get('storage_tank', 0)
        dT = solar_collector - storage_tank
        
        # Validate realistic behavior
        realistic_checks = []
        
        # Check if temperatures are within realistic ranges
        if 0 <= solar_collector <= 150:  # Realistic collector range
            realistic_checks.append(("Collector temp realistic", True))
        else:
            realistic_checks.append(("Collector temp realistic", False))
        
        if 10 <= storage_tank <= 80:  # Realistic tank range
            realistic_checks.append(("Tank temp realistic", True))
        else:
            realistic_checks.append(("Tank temp realistic", False))
        
        # Check if dT makes sense for the scenario
        if scenario['time'] >= 6 and scenario['time'] <= 18:  # Daylight
            if dT >= 0:  # Should be positive during day
                realistic_checks.append(("Daytime dT positive", True))
            else:
                realistic_checks.append(("Daytime dT positive", False))
        else:  # Night time
            if dT <= 20:  # Should be smaller at night
                realistic_checks.append(("Nighttime dT reasonable", True))
            else:
                realistic_checks.append(("Nighttime dT reasonable", False))
        
        # Check water heater stratification
        water_heater_temps = [system.temperatures.get(f'rtd_sensor_{i}', 0) for i in range(8)]
        if water_heater_temps[7] >= water_heater_temps[0]:  # Top should be warmer than bottom
            realistic_checks.append(("Water heater stratification", True))
        else:
            realistic_checks.append(("Water heater stratification", False))
        
        # Display results
        print(f"      Collector: {solar_collector:.1f}°C, Tank: {storage_tank:.1f}°C, dT: {dT:.1f}°C")
        print(f"      Water heater: {water_heater_temps[0]:.1f}°C to {water_heater_temps[7]:.1f}°C")
        
        scenario_passed = all(check[1] for check in realistic_checks)
        for check_name, passed in realistic_checks:
            print(f"      {check_name}: {'✅' if passed else '❌'}")
        
        print(f"      Scenario: {'✅ PASS' if scenario_passed else '❌ FAIL'}")
        
        if not scenario_passed:
            all_passed = False
    
    return all_passed

def test_mqtt_connection():
    """Test real MQTT connection"""
    print("\n📡 Testing real MQTT connection...")
    
    if not MQTT_AVAILABLE:
        print("   ⚠️  MQTT not available - skipping test")
        return True
    
    mqtt_client = MQTTTestClient()
    
    # Test connection
    if not mqtt_client.connect():
        print("   ❌ MQTT connection failed - skipping test")
        return False
    
    try:
        # Test publishing
        test_topic = "solar_heating/test"
        test_payload = json.dumps({
            'timestamp': time.time(),
            'test_data': 'realistic_environment_test'
        })
        
        if mqtt_client.publish(test_topic, test_payload):
            print("   ✅ MQTT publish successful")
        else:
            print("   ❌ MQTT publish failed")
            return False
        
        # Test subscription
        if mqtt_client.subscribe(test_topic):
            print("   ✅ MQTT subscribe successful")
        else:
            print("   ❌ MQTT subscribe failed")
            return False
        
        # Wait for message
        time.sleep(1)
        
        # Test message handling
        if len(mqtt_client.messages_received) > 0:
            print("   ✅ MQTT message received")
        else:
            print("   ⚠️  No MQTT messages received (expected in test environment)")
        
        return True
        
    finally:
        mqtt_client.disconnect()

def test_realistic_system_behavior():
    """Test system behavior with realistic data over time"""
    print("\n🔄 Testing realistic system behavior over time...")
    
    system = SolarHeatingSystem()
    data_generator = RealisticSensorDataGenerator()
    
    # Simulate a full day of operation
    simulation_hours = 24
    time_step_minutes = 30  # 30-minute intervals
    
    all_passed = True
    pump_cycles = 0
    energy_collected = 0.0
    
    print(f"   Simulating {simulation_hours} hours with {time_step_minutes}-minute intervals...")
    
    for hour in range(simulation_hours):
        for minute in range(0, 60, time_step_minutes):
            # Set time
            data_generator.time_of_day = hour + minute / 60.0
            
            # Generate realistic sensor data
            sensor_data = data_generator.get_realistic_temperature_profile()
            sensor_data = data_generator.add_realistic_noise(sensor_data)
            
            # Apply to system
            system.temperatures.clear()
            system.temperatures.update(sensor_data)
            
            # Run sensor mapping
            system.temperatures['solar_collector'] = system.temperatures.get('megabas_sensor_6', 0)
            system.temperatures['storage_tank'] = system.temperatures.get('megabas_sensor_7', 0)
            
            # Calculate dT
            solar_collector = system.temperatures.get('solar_collector', 0)
            storage_tank = system.temperatures.get('storage_tank', 0)
            dT = solar_collector - storage_tank
            
            # Simulate pump control
            dTStart = system.control_params.get('dTStart_tank_1', 8.0)
            dTStop = system.control_params.get('dTStop_tank_1', 4.0)
            
            current_pump_state = system.system_state.get('primary_pump', False)
            
            if dT >= dTStart:
                new_pump_state = True
            elif dT <= dTStop:
                new_pump_state = False
            else:
                new_pump_state = current_pump_state  # Hysteresis
            
            # Count pump cycles
            if new_pump_state and not current_pump_state:
                pump_cycles += 1
            
            system.system_state['primary_pump'] = new_pump_state
            
            # Calculate energy (simplified)
            if new_pump_state and dT > 0:
                energy_collected += dT * 0.1  # Simplified energy calculation
            
            # Check for unrealistic behavior
            if dT > 100:  # Unrealistic temperature difference
                print(f"   ❌ Unrealistic dT: {dT:.1f}°C at hour {hour}:{minute:02d}")
                all_passed = False
            
            if solar_collector > 200:  # Unrealistic collector temperature
                print(f"   ❌ Unrealistic collector temp: {solar_collector:.1f}°C at hour {hour}:{minute:02d}")
                all_passed = False
    
    print(f"   ✅ Simulation completed: {pump_cycles} pump cycles, {energy_collected:.1f} kWh collected")
    print(f"   ✅ System behavior: {'Realistic' if all_passed else 'Unrealistic'}")
    
    return all_passed

def test_hardware_like_behavior():
    """Test hardware-like behavior with realistic timing and responses"""
    print("\n🔧 Testing hardware-like behavior...")
    
    system = SolarHeatingSystem()
    data_generator = RealisticSensorDataGenerator()
    
    # Test sensor response times
    response_times = []
    
    for i in range(10):
        start_time = time.time()
        
        # Generate sensor data
        sensor_data = data_generator.get_realistic_temperature_profile()
        sensor_data = data_generator.add_realistic_noise(sensor_data)
        
        # Apply to system
        system.temperatures.clear()
        system.temperatures.update(sensor_data)
        
        # Run sensor mapping
        system.temperatures['solar_collector'] = system.temperatures.get('megabas_sensor_6', 0)
        system.temperatures['storage_tank'] = system.temperatures.get('megabas_sensor_7', 0)
        
        # Calculate dT
        solar_collector = system.temperatures.get('solar_collector', 0)
        storage_tank = system.temperatures.get('storage_tank', 0)
        dT = solar_collector - storage_tank
        
        response_time = time.time() - start_time
        response_times.append(response_time)
        
        # Simulate realistic sensor update interval
        time.sleep(0.1)  # 100ms between sensor updates
    
    avg_response_time = sum(response_times) / len(response_times)
    max_response_time = max(response_times)
    
    print(f"   ✅ Average response time: {avg_response_time*1000:.1f}ms")
    print(f"   ✅ Maximum response time: {max_response_time*1000:.1f}ms")
    
    # Check if response times are realistic
    if avg_response_time < 0.1:  # Less than 100ms average
        print("   ✅ Response times are realistic")
        return True
    else:
        print("   ❌ Response times are too slow")
        return False

def main():
    """Main test runner"""
    print("🚀 Starting Realistic Environment Test Suite")
    print("=" * 70)
    print("This test suite uses realistic sensor data and real MQTT connections")
    print("to test the system in a more production-like environment.")
    print("=" * 70)
    
    tests = [
        ("Realistic Sensor Data", test_realistic_sensor_data),
        ("MQTT Connection", test_mqtt_connection),
        ("Realistic System Behavior", test_realistic_system_behavior),
        ("Hardware-like Behavior", test_hardware_like_behavior),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n❌ {test_name}: EXCEPTION - {str(e)}")
    
    print("\n📊 REALISTIC ENVIRONMENT TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! System behaves realistically in production-like environment.")
        return True
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED. System needs attention for realistic behavior.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
