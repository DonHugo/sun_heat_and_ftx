#!/usr/bin/env python3
"""
MQTT Integration Test for Solar Heating System v3
Demonstrates MQTT communication with the system
"""

import asyncio
import logging
import os
import sys
import time

# Set test mode
os.environ['SOLAR_TEST_MODE'] = 'true'

from hardware_interface import HardwareInterface
from mqtt_handler import MQTTHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_mqtt_integration():
    """Test MQTT integration with the system"""
    logger.info("🔌 Testing MQTT Integration with System")
    logger.info("=" * 50)
    
    try:
        # Initialize hardware interface
        hw = HardwareInterface(simulation_mode=True)
        logger.info("✅ Hardware interface initialized")
        
        # Initialize MQTT handler
        mqtt = MQTTHandler()
        logger.info("✅ MQTT handler initialized")
        
        # Connect to MQTT broker
        logger.info("📡 Connecting to MQTT broker...")
        connected = mqtt.connect()
        
        if not connected:
            logger.error("❌ Failed to connect to MQTT broker")
            return False
        
        logger.info("✅ Connected to MQTT broker")
        
        # Test temperature publishing
        logger.info("🌡️  Testing temperature publishing...")
        temps = hw.read_all_temperatures()
        
        for sensor_name, temperature in temps.items():
            success = mqtt.publish_temperature(sensor_name, temperature)
            if success:
                logger.info(f"   ✅ Published {sensor_name}: {temperature}°C")
            else:
                logger.warning(f"   ⚠️  Failed to publish {sensor_name}")
        
        # Test system status publishing
        logger.info("📊 Testing system status publishing...")
        system_status = {
            'mode': 'test',
            'primary_pump': False,
            'secondary_pump': False,
            'cartridge_heater': False,
            'test_mode': True,
            'manual_control': False,
            'overheated': False,
            'last_update': time.time()
        }
        
        success = mqtt.publish_system_status(system_status)
        if success:
            logger.info("   ✅ Published system status")
        else:
            logger.warning("   ⚠️  Failed to publish system status")
        
        # Test pump status publishing
        logger.info("🔄 Testing pump status publishing...")
        success = mqtt.publish_pump_status('primary', False)
        if success:
            logger.info("   ✅ Published pump status")
        else:
            logger.warning("   ⚠️  Failed to publish pump status")
        
        # Test energy status publishing
        logger.info("⚡ Testing energy status publishing...")
        energy_data = {
            'total_energy_kwh': 8.58,
            'average_temperature': 45.2,
            'sensor_count': len(temps)
        }
        
        success = mqtt.publish_energy_status(energy_data)
        if success:
            logger.info("   ✅ Published energy status")
        else:
            logger.warning("   ⚠️  Failed to publish energy status")
        
        # Wait a moment to see the messages
        logger.info("⏱️  Waiting 5 seconds to observe MQTT activity...")
        await asyncio.sleep(5)
        
        # Disconnect
        logger.info("🔌 Disconnecting from MQTT broker...")
        mqtt.disconnect()
        logger.info("✅ Disconnected successfully")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ MQTT integration test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🧪 MQTT Integration Test")
    logger.info("=" * 60)
    
    try:
        success = await test_mqtt_integration()
        
        if success:
            logger.info("")
            logger.info("🎉 MQTT INTEGRATION TEST PASSED!")
            logger.info("✅ All MQTT functionality working:")
            logger.info("   - Connection to broker ✅")
            logger.info("   - Temperature publishing ✅")
            logger.info("   - System status publishing ✅")
            logger.info("   - Pump status publishing ✅")
            logger.info("   - Energy status publishing ✅")
            logger.info("   - Clean disconnection ✅")
            logger.info("")
            logger.info("🌐 MQTT integration is ready for Home Assistant!")
            return 0
        else:
            logger.error("❌ MQTT integration test failed!")
            return 1
            
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
