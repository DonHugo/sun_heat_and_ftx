#!/usr/bin/env python3
"""
Test script for hall sensor and pulse counter integration
"""

import time
from mqtt_handler import MQTTHandler
from config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class HallSensorTester:
    def __init__(self):
        self.mqtt = MQTTHandler()
        self.received_data = {}
        self.data_count = 0
        
    def handle_pellet_stove_data(self, command_type, data):
        """Handle pellet stove data from MQTT"""
        if command_type == 'pellet_stove_data':
            sensor = data['sensor']
            value = data['value']
            topic = data['original_topic']
            payload = data['original_payload']
            
            self.received_data[sensor] = {
                'value': value,
                'topic': topic,
                'payload': payload,
                'timestamp': time.time()
            }
            self.data_count += 1
            
            logger.info(f"✅ Received pellet stove data: {sensor} = {value}")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   Raw payload: {payload}")
            logger.info(f"   Total data points: {self.data_count}")
            logger.info("-" * 50)
    
    def connect_and_test(self):
        """Connect to MQTT and test hall sensor data reception"""
        try:
            logger.info("🔌 Connecting to MQTT broker...")
            self.mqtt.system_callback = self.handle_pellet_stove_data
            self.mqtt.connect()
            
            if self.mqtt.is_connected():
                logger.info("✅ Connected to MQTT broker successfully!")
                logger.info("📡 Subscribed to hall sensor topics:")
                logger.info("   - homeassistant/binary_sensor/hall_sensor/state")
                logger.info("   - homeassistant/sensor/pulse_counter_60s/state")
                logger.info("")
                logger.info("⏳ Waiting for hall sensor data from Home Assistant...")
                logger.info("   (Make sure your pellet stove is active and feeding pellets)")
                logger.info("")
                
                # Monitor for 60 seconds
                start_time = time.time()
                while time.time() - start_time < 60:
                    if self.data_count > 0:
                        logger.info(f"🎉 Success! Received {self.data_count} data points")
                        self.print_summary()
                        break
                    time.sleep(1)
                
                if self.data_count == 0:
                    logger.warning("⚠️  No hall sensor data received in 60 seconds")
                    logger.info("   Possible reasons:")
                    logger.info("   - Pellet stove is not feeding pellets")
                    logger.info("   - Hall sensor is not connected")
                    logger.info("   - Home Assistant is not publishing data")
                    logger.info("   - MQTT topics don't match")
                
            else:
                logger.error("❌ Failed to connect to MQTT broker")
                
        except Exception as e:
            logger.error(f"❌ Error during testing: {e}")
        finally:
            if self.mqtt:
                self.mqtt.disconnect()
                logger.info("🔌 Disconnected from MQTT broker")
    
    def print_summary(self):
        """Print summary of received data"""
        logger.info("")
        logger.info("📊 HALL SENSOR DATA SUMMARY:")
        logger.info("=" * 50)
        
        for sensor, data in self.received_data.items():
            logger.info(f"🔸 {sensor}:")
            logger.info(f"   Value: {data['value']}")
            logger.info(f"   Topic: {data['topic']}")
            logger.info(f"   Raw: {data['payload']}")
            logger.info("")
        
        logger.info(f"📈 Total data points received: {self.data_count}")
        logger.info("✅ Hall sensor integration is working!")

def main():
    """Main test function"""
    logger.info("🧪 HALL SENSOR INTEGRATION TEST")
    logger.info("=" * 50)
    
    tester = HallSensorTester()
    tester.connect_and_test()

if __name__ == "__main__":
    main()
