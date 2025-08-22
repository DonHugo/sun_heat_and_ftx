#!/usr/bin/env python3
"""
MQTT Connection Test for Solar Heating System v3
Tests connection to the existing MQTT broker
"""

import asyncio
import logging
import sys
import time

from mqtt_handler import MQTTHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

async def test_mqtt_connection():
    """Test MQTT connection to the broker"""
    logger.info("🔌 Testing MQTT Connection")
    logger.info("=" * 40)
    
    # Create MQTT handler
    mqtt = MQTTHandler()
    
    logger.info(f"Broker: {mqtt.broker}:{mqtt.port}")
    logger.info(f"Username: {mqtt.username}")
    logger.info(f"Client ID: {mqtt.client_id}")
    
    try:
        # Attempt to connect
        logger.info("📡 Attempting to connect to MQTT broker...")
        connected = mqtt.connect()
        
        if connected:
            logger.info("✅ Successfully connected to MQTT broker!")
            
            # Wait a moment for connection to stabilize
            await asyncio.sleep(2)
            
            # Test publishing a message
            logger.info("📤 Testing message publishing...")
            test_message = {
                "test": True,
                "timestamp": time.time(),
                "message": "Solar Heating System v3 MQTT test"
            }
            
            success = mqtt.publish("solar_heating_v3/test", test_message)
            if success:
                logger.info("✅ Message published successfully!")
            else:
                logger.warning("⚠️  Failed to publish message")
            
            # Wait a moment
            await asyncio.sleep(3)
            
            # Disconnect
            logger.info("🔌 Disconnecting from MQTT broker...")
            mqtt.disconnect()
            logger.info("✅ Disconnected successfully!")
            
            return True
            
        else:
            logger.error("❌ Failed to connect to MQTT broker")
            return False
            
    except Exception as e:
        logger.error(f"❌ MQTT connection test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🧪 MQTT Connection Test")
    logger.info("=" * 50)
    
    try:
        success = await test_mqtt_connection()
        
        if success:
            logger.info("🎉 MQTT connection test PASSED!")
            logger.info("✅ The v3 system can communicate with your MQTT broker")
            return 0
        else:
            logger.error("❌ MQTT connection test FAILED!")
            logger.error("Please check your MQTT broker configuration")
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
