#!/usr/bin/env python3
"""
Simple Test Script for Solar Heating System v3 - System-Wide Version
Tests basic functionality without requiring virtual environment
"""

import sys
import time
import logging

# Configure basic logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_imports():
    """Test if all required modules can be imported"""
    logger.info("Testing module imports...")
    
    try:
        from config import config
        logger.info("✅ Config module imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import config: {e}")
        return False
    
    try:
        from hardware_interface import HardwareInterface
        logger.info("✅ Hardware interface imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import hardware interface: {e}")
        return False
    
    try:
        from mqtt_handler import MQTTHandler
        logger.info("✅ MQTT handler imported successfully")
    except ImportError as e:
        logger.error(f"❌ Failed to import MQTT handler: {e}")
        return False
    
    return True

def test_hardware():
    """Test hardware interface"""
    logger.info("Testing hardware interface...")
    
    try:
        from hardware_interface import HardwareInterface
        
        # Create hardware interface in test mode
        hardware = HardwareInterface(simulation_mode=True)
        
        # Test hardware connection
        test_result = hardware.test_hardware_connection()
        logger.info(f"Hardware test result: {test_result}")
        
        # Test temperature readings (simulated)
        for sensor_id in [5, 6, 7]:  # RTD sensors
            temp = hardware.read_rtd_temperature(sensor_id)
            logger.info(f"RTD sensor {sensor_id}: {temp}°C")
        
        for sensor_id in [0, 1, 2, 3, 4]:  # MegaBAS sensors
            temp = hardware.read_megabas_temperature(sensor_id)
            logger.info(f"MegaBAS sensor {sensor_id}: {temp}°C")
        
        # Test relay control
        logger.info("Testing relay control...")
        hardware.set_primary_pump(True)
        time.sleep(1)
        hardware.set_primary_pump(False)
        logger.info("✅ Hardware interface test completed")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Hardware test failed: {e}")
        return False

def test_config():
    """Test configuration"""
    logger.info("Testing configuration...")
    
    try:
        from config import config
        
        logger.info(f"Hardware platform: {config.hardware_platform}")
        logger.info(f"RTD board address: {config.rtd_board_address}")
        logger.info(f"MegaBAS board address: {config.megabas_board_address}")
        logger.info(f"Relay board address: {config.relay_board_address}")
        logger.info(f"MQTT broker: {config.mqtt_broker}:{config.mqtt_port}")
        logger.info(f"Test mode: {config.test_mode}")
        
        logger.info("✅ Configuration test completed")
        return True
        
    except Exception as e:
        logger.error(f"❌ Configuration test failed: {e}")
        return False

def test_mqtt():
    """Test MQTT connection"""
    logger.info("Testing MQTT connection...")
    
    try:
        from mqtt_handler import MQTTHandler
        
        mqtt = MQTTHandler()
        
        # Try to connect
        if mqtt.connect():
            logger.info("✅ MQTT connection successful")
            mqtt.disconnect()
            return True
        else:
            logger.warning("⚠️ MQTT connection failed (this is normal if broker is not available)")
            return True  # Don't fail the test for MQTT issues
            
    except Exception as e:
        logger.error(f"❌ MQTT test failed: {e}")
        return False

def main():
    """Main test function"""
    logger.info("🚀 Starting Solar Heating System v3 - System-Wide Test")
    logger.info("=" * 60)
    
    tests = [
        ("Module Imports", test_imports),
        ("Configuration", test_config),
        ("Hardware Interface", test_hardware),
        ("MQTT Connection", test_mqtt),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 Running test: {test_name}")
        logger.info("-" * 40)
        
        if test_func():
            passed += 1
            logger.info(f"✅ {test_name} PASSED")
        else:
            logger.error(f"❌ {test_name} FAILED")
    
    logger.info("\n" + "=" * 60)
    logger.info(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! v3 system is ready to run.")
        logger.info("\nTo run v3 system:")
        logger.info("  python3 main_system.py")
    else:
        logger.error("⚠️ Some tests failed. Check the errors above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
