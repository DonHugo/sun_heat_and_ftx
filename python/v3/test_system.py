#!/usr/bin/env python3
"""
Test script for Solar Heating System v3
Runs the system in simulation mode for testing
"""

import asyncio
import logging
import os
import sys
import time

# Set test mode
os.environ['SOLAR_TEST_MODE'] = 'true'
os.environ['SOLAR_DEBUG_MODE'] = 'true'
os.environ['SOLAR_LOG_LEVEL'] = 'info'

from main import SolarHeatingSystem

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def test_system():
    """Test the solar heating system"""
    logger.info("🚀 Starting Solar Heating System v3 Test")
    
    # Create system
    system = SolarHeatingSystem()
    
    try:
        # Start system
        logger.info("📡 Starting system...")
        start_task = asyncio.create_task(system.start())
        
        # Let it run for 30 seconds
        logger.info("⏱️  Running system for 30 seconds...")
        await asyncio.sleep(30)
        
        # Stop system
        logger.info("🛑 Stopping system...")
        await system.stop()
        
        # Cancel start task if it's still running
        if not start_task.done():
            start_task.cancel()
            try:
                await start_task
            except asyncio.CancelledError:
                pass
        
        logger.info("✅ Test completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        await system.stop()
        raise

async def test_components():
    """Test individual components"""
    logger.info("🔧 Testing individual components...")
    
    # Test config
    from config import config, sensor_mapping, pump_config
    logger.info(f"✅ Config: Hardware platform = {config.hardware_platform}")
    logger.info(f"✅ Sensor mapping: {len(sensor_mapping.__dict__)} sensors")
    logger.info(f"✅ Pump config: {pump_config.normally_closed} (NC)")
    
    # Test hardware interface
    from hardware_interface import HardwareInterface
    hw = HardwareInterface(simulation_mode=True)
    temps = hw.read_all_temperatures()
    logger.info(f"✅ Hardware interface: {len(temps)} temperature readings")
    
    # Test MQTT handler
    from mqtt_handler import MQTTHandler
    mqtt = MQTTHandler()
    logger.info(f"✅ MQTT handler: {mqtt.broker}:{mqtt.port}")
    
    logger.info("✅ All components tested successfully!")

async def main():
    """Main test function"""
    logger.info("🧪 Solar Heating System v3 Test Suite")
    logger.info("=" * 50)
    
    try:
        # Test components first
        await test_components()
        logger.info("-" * 50)
        
        # Test full system
        await test_system()
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return 1
    
    logger.info("🎉 All tests completed!")
    return 0

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
