#!/usr/bin/env python3
"""
Simple MQTT topic monitor to see what Home Assistant is publishing
"""

import paho.mqtt.client as mqtt_client
import time
import json
from config import config
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTTopicMonitor:
    def __init__(self):
        self.client = mqtt_client.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.on_disconnect = self.on_disconnect
        
        # Set credentials if provided
        if config.mqtt_username and config.mqtt_password:
            self.client.username_pw_set(config.mqtt_username, config.mqtt_password)
    
    def on_connect(self, client, userdata, flags, rc):
        """Called when connected to MQTT broker"""
        if rc == 0:
            logger.info("✅ Connected to MQTT broker successfully!")
            
            # Subscribe to all pellet stove related topics
            topics = [
                "homeassistant/sensor/pelletskamin_+/state",
                "homeassistant/binary_sensor/pelletskamin_+/state",
                "homeassistant/sensor/pellet_stove_+/state",
                "homeassistant/binary_sensor/pellet_stove_+/state",
                "homeassistant/sensor/pellet_stove_monitoring_+/state",
                "homeassistant/binary_sensor/pellet_stove_monitoring_+/state",
                # Also subscribe to broader topics to see what's available
                "homeassistant/sensor/+/state",
                "homeassistant/binary_sensor/+/state"
            ]
            
            for topic in topics:
                client.subscribe(topic)
                logger.info(f"📡 Subscribed to: {topic}")
            
            logger.info("")
            logger.info("🔍 Monitoring MQTT topics for pellet stove data...")
            logger.info("   (Press Ctrl+C to stop)")
            logger.info("")
            
        else:
            logger.error(f"❌ Failed to connect to MQTT broker, return code: {rc}")
    
    def on_message(self, client, userdata, msg):
        """Called when a message is received"""
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        
        # Check if this is pellet stove related
        is_pellet_stove = any(keyword in topic.lower() for keyword in [
            'pelletskamin', 'pellet_stove', 'pellet'
        ])
        
        if is_pellet_stove:
            logger.info(f"🔥 PELLET STOVE DATA:")
            logger.info(f"   Topic: {topic}")
            logger.info(f"   Payload: {payload}")
            logger.info("-" * 50)
        else:
            logger.debug(f"📡 Other topic: {topic} = {payload}")
    
    def on_disconnect(self, client, userdata, rc):
        """Called when disconnected from MQTT broker"""
        if rc != 0:
            logger.warning(f"⚠️  Unexpected disconnection, return code: {rc}")
        else:
            logger.info("🔌 Disconnected from MQTT broker")
    
    def connect_and_monitor(self):
        """Connect to MQTT broker and monitor topics"""
        try:
            logger.info("🔌 Connecting to MQTT broker...")
            self.client.connect(config.mqtt_broker, config.mqtt_port, 60)
            
            # Start the loop
            self.client.loop_forever()
            
        except KeyboardInterrupt:
            logger.info("")
            logger.info("🛑 Stopping MQTT monitor...")
            self.client.disconnect()
        except Exception as e:
            logger.error(f"❌ Error: {e}")
            self.client.disconnect()

def main():
    """Main function"""
    logger.info("🔍 MQTT TOPIC MONITOR")
    logger.info("=" * 50)
    logger.info("This will show all MQTT topics being published")
    logger.info("Focusing on pellet stove related data")
    logger.info("")
    
    monitor = MQTTTopicMonitor()
    monitor.connect_and_monitor()

if __name__ == "__main__":
    main()
