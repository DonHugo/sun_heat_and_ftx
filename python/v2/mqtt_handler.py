import json
import logging
import random
import time
from typing import Callable, Dict, Any
from paho.mqtt import client as mqtt_client
from config import MQTTConfig

class MQTTHandler:
    def __init__(self, config: MQTTConfig, message_callback: Callable[[str, Dict], None]):
        self.config = config
        self.message_callback = message_callback
        self.client = None
        self.is_connected = False
    
    def connect(self) -> mqtt_client.Client:
        """Establish MQTT connection"""
        try:
            client_id = f"{self.config.client_id_prefix}-{random.randint(0, 1000)}"
            client = mqtt_client.Client(client_id)
            client.username_pw_set(self.config.username, self.config.password)
            client.on_connect = self._on_connect
            client.on_message = self._on_message
            client.on_disconnect = self._on_disconnect
            client.connect(self.config.broker, self.config.port, keepalive=3)
            self.client = client
            return client
        except Exception as e:
            logging.error(f"MQTT connection failed: {e}")
            raise
    
    def _on_connect(self, client, userdata, flags, rc):
        """Handle MQTT connection"""
        try:
            if rc == 0 and client.is_connected():
                self.is_connected = True
                logging.info("Connected to MQTT Broker!")
                # Subscribe to topics
                topics = [(topic, 0) for topic in self.config.sub_topics]
                client.subscribe(topics)
            else:
                logging.error(f'Failed to connect, return code {rc}')
        except Exception as e:
            logging.error(f"Error in on_connect: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Handle MQTT disconnection with reconnection logic"""
        self.is_connected = False
        logging.info(f"Disconnected with result code: {rc}")
        # Add reconnection logic here if needed
    
    def _on_message(self, client, userdata, msg):
        """Handle incoming MQTT messages"""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode())
            self.message_callback(topic, payload)
        except Exception as e:
            logging.error(f"Error processing message from {msg.topic}: {e}")
    
    def publish(self, topic: str, message: Dict[str, Any]) -> bool:
        """Publish message to MQTT broker"""
        try:
            if not self.is_connected:
                logging.error("MQTT client is not connected!")
                return False
            
            msg = json.dumps(message)
            result = self.client.publish(topic, msg)
            
            if result[0] == 0:
                logging.debug(f'Published to {topic}: {msg}')
                return True
            else:
                logging.error(f'Failed to publish to {topic}')
                return False
        except Exception as e:
            logging.error(f'Error publishing to {topic}: {e}')
            return False
