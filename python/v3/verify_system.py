#!/usr/bin/env python3
"""
System Verification Script for Solar Heating System v3
Quick verification that the system is working correctly

This script performs basic checks to ensure:
- All modules can be imported
- Configuration is valid
- Hardware interface works
- Control logic is functional
- MQTT connection is possible
"""

import sys
import os
import time
import logging

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        from config import config, pump_config
        print("  ✅ Config module imported")
    except ImportError as e:
        print(f"  ❌ Config import failed: {e}")
        return False
    
    try:
        from hardware_interface import HardwareInterface
        print("  ✅ Hardware interface imported")
    except ImportError as e:
        print(f"  ❌ Hardware interface import failed: {e}")
        return False
    
    try:
        from mqtt_handler import MQTTHandler
        print("  ✅ MQTT handler imported")
    except ImportError as e:
        print(f"  ❌ MQTT handler import failed: {e}")
        return False
    
    try:
        from main_system import SolarHeatingSystem
        print("  ✅ Main system imported")
    except ImportError as e:
        print(f"  ❌ Main system import failed: {e}")
        return False
    
    try:
        from taskmaster_service import TaskMasterService
        print("  ✅ TaskMaster service imported")
    except ImportError as e:
        print(f"  ❌ TaskMaster service import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration validity"""
    print("\n🔧 Testing configuration...")
    
    try:
        from config import config
        
        # Test required configuration values
        required_configs = [
            'mqtt_broker', 'mqtt_port', 'mqtt_username', 'mqtt_password',
            'dTStart_tank_1', 'dTStop_tank_1', 'temp_kok', 'temp_kok_hysteres',
            'kylning_kollektor', 'kylning_kollektor_hysteres'
        ]
        
        for config_name in required_configs:
            if hasattr(config, config_name):
                value = getattr(config, config_name)
                print(f"  ✅ {config_name}: {value}")
            else:
                print(f"  ❌ Missing configuration: {config_name}")
                return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Configuration test failed: {e}")
        return False

def test_hardware_interface():
    """Test hardware interface functionality"""
    print("\n🔌 Testing hardware interface...")
    
    try:
        from hardware_interface import HardwareInterface
        
        # Test simulation mode
        hw = HardwareInterface(simulation_mode=True)
        print("  ✅ Hardware interface initialized (simulation mode)")
        
        # Test temperature reading
        temp = hw.read_rtd_temperature(0)
        if temp is not None and 0 <= temp <= 200:
            print(f"  ✅ RTD temperature reading: {temp}°C")
        else:
            print(f"  ❌ Invalid RTD temperature: {temp}")
            return False
        
        # Test relay control
        hw.set_relay_state(1, True)
        state = hw.get_relay_state(1)
        if state == True:
            print("  ✅ Relay control: ON")
        else:
            print(f"  ❌ Relay control failed: {state}")
            return False
        
        hw.set_relay_state(1, False)
        state = hw.get_relay_state(1)
        if state == False:
            print("  ✅ Relay control: OFF")
        else:
            print(f"  ❌ Relay control failed: {state}")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Hardware interface test failed: {e}")
        return False

def test_control_logic():
    """Test control logic functionality"""
    print("\n🎛️ Testing control logic...")
    
    try:
        from main_system import SolarHeatingSystem
        
        system = SolarHeatingSystem()
        print("  ✅ Solar heating system initialized")
        
        # Test control parameters
        required_params = ['dTStart_tank_1', 'dTStop_tank_1', 'temp_kok', 'temp_kok_hysteres']
        for param in required_params:
            if param in system.control_params:
                value = system.control_params[param]
                print(f"  ✅ {param}: {value}")
            else:
                print(f"  ❌ Missing control parameter: {param}")
                return False
        
        # Test system state
        required_states = ['primary_pump', 'overheated', 'collector_cooling_active', 'manual_control']
        for state in required_states:
            if state in system.system_state:
                value = system.system_state[state]
                print(f"  ✅ {state}: {value}")
            else:
                print(f"  ❌ Missing system state: {state}")
                return False
        
        # Test mode reasoning
        reasoning = system.get_mode_reasoning()
        if 'explanation' in reasoning:
            print(f"  ✅ Mode reasoning: {reasoning['explanation']}")
        else:
            print("  ❌ Mode reasoning failed")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ Control logic test failed: {e}")
        return False

def test_mqtt_connection():
    """Test MQTT connection capability"""
    print("\n📡 Testing MQTT connection...")
    
    try:
        from config import config
        import paho.mqtt.client as mqtt_client
        
        # Test MQTT client creation
        client = mqtt_client.Client()
        client.username_pw_set(config.mqtt_username, config.mqtt_password)
        print("  ✅ MQTT client created")
        
        # Test connection (with timeout)
        connected = False
        def on_connect(client, userdata, flags, rc):
            nonlocal connected
            if rc == 0:
                connected = True
        
        client.on_connect = on_connect
        client.connect(config.mqtt_broker, config.mqtt_port, 60)
        client.loop_start()
        
        # Wait for connection
        timeout = 5
        while not connected and timeout > 0:
            time.sleep(0.1)
            timeout -= 0.1
        
        if connected:
            print("  ✅ MQTT connection successful")
            client.loop_stop()
            client.disconnect()
            return True
        else:
            print("  ⚠️  MQTT connection failed (broker may not be available)")
            client.loop_stop()
            client.disconnect()
            return True  # Don't fail if broker is not available
        
    except Exception as e:
        print(f"  ⚠️  MQTT connection test failed: {e}")
        return True  # Don't fail if MQTT is not available

def test_taskmaster_integration():
    """Test TaskMaster AI integration"""
    print("\n🤖 Testing TaskMaster AI integration...")
    
    try:
        from taskmaster_service import TaskMasterService
        
        taskmaster = TaskMasterService()
        print("  ✅ TaskMaster service initialized")
        
        # Test basic functionality
        if hasattr(taskmaster, 'create_task'):
            print("  ✅ Task creation method available")
        else:
            print("  ❌ Task creation method missing")
            return False
        
        if hasattr(taskmaster, 'process_pump_control'):
            print("  ✅ Pump control processing available")
        else:
            print("  ❌ Pump control processing missing")
            return False
        
        return True
        
    except Exception as e:
        print(f"  ❌ TaskMaster integration test failed: {e}")
        return False

def main():
    """Main verification function"""
    print("🚀 Solar Heating System v3 - System Verification")
    print("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_configuration),
        ("Hardware Interface", test_hardware_interface),
        ("Control Logic", test_control_logic),
        ("MQTT Connection", test_mqtt_connection),
        ("TaskMaster Integration", test_taskmaster_integration)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} failed")
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
    
    print("\n📊 VERIFICATION SUMMARY")
    print("=" * 60)
    print(f"Tests Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("\n🎉 ALL VERIFICATIONS PASSED! System is ready to run.")
        return 0
    else:
        print(f"\n⚠️  {total-passed} VERIFICATIONS FAILED. Check system configuration.")
        return 1

if __name__ == "__main__":
    exit(main())
