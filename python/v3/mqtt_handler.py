"""
MQTT Handler Module for Solar Heating System v3
Handles MQTT communication with Home Assistant and other systems
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Callable
from paho.mqtt import client as mqtt_client
import random

from config import config, mqtt_topics

logger = logging.getLogger(__name__)

class MQTTHandler:
    """MQTT handler for system communication"""
    
    def __init__(self):
        self.client = None
        self.connected = False
        self.message_handlers: Dict[str, Callable] = {}
        self.last_messages: Dict[str, Any] = {}
        
        # MQTT connection parameters
        self.broker = config.mqtt_broker
        self.port = config.mqtt_port
        self.username = config.mqtt_username
        self.password = config.mqtt_password
        self.client_id = f"{config.mqtt_client_id}_{random.randint(0, 1000)}"
        
        # Connection retry parameters
        self.first_reconnect_delay = 1
        self.reconnect_rate = 2
        self.max_reconnect_count = 12
        self.max_reconnect_delay = 60
        
        logger.info(f"MQTT handler initialized for broker: {self.broker}:{self.port}")
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client = mqtt_client.Client(self.client_id)
            self.client.username_pw_set(self.username, self.password)
            self.client.on_connect = self._on_connect
            self.client.on_disconnect = self._on_disconnect
            self.client.on_message = self._on_message
            
            self.client.connect(self.broker, self.port, keepalive=60)
            self.client.loop_start()
            
            # Wait for connection
            timeout = 10
            while not self.connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            return self.connected
            
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client:
            self.client.loop_stop()
            self.client.disconnect()
            self.connected = False
            logger.info("Disconnected from MQTT broker")
    
    def _on_connect(self, client, userdata, flags, rc):
        """MQTT connection callback"""
        if rc == 0 and client.is_connected():
            self.connected = True
            logger.info("Connected to MQTT broker successfully")
            
            # Subscribe to topics
            self._subscribe_to_topics()
        else:
            self.connected = False
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        logger.info(f"Disconnected from MQTT broker with result code: {rc}")
        
        # Attempt reconnection
        self._reconnect()
    
    def _reconnect(self):
        """Reconnect to MQTT broker with exponential backoff"""
        reconnect_count = 0
        reconnect_delay = self.first_reconnect_delay
        
        while reconnect_count < self.max_reconnect_count:
            logger.info(f"Reconnecting to MQTT broker in {reconnect_delay} seconds...")
            time.sleep(reconnect_delay)
            
            try:
                self.client.reconnect()
                logger.info("Reconnected to MQTT broker successfully")
                return
            except Exception as err:
                logger.error(f"Reconnect failed: {err}")
            
            reconnect_delay *= self.reconnect_rate
            reconnect_delay = min(reconnect_delay, self.max_reconnect_delay)
            reconnect_count += 1
        
        logger.error(f"Failed to reconnect after {self.max_reconnect_count} attempts")
    
    def _subscribe_to_topics(self):
        """Subscribe to MQTT topics"""
        topics = [
            # Home Assistant control topics
            f"{mqtt_topics.hass_base}/+/control",
            f"{mqtt_topics.hass_base}/+/set",
            
            # System control topics
            f"{mqtt_topics.control_base}/+",
            
            # Configuration topics
            f"{mqtt_topics.base_topic}/config/+",
            
            # TaskMaster AI topics
            f"{mqtt_topics.taskmaster_base}/+",
        ]
        
        for topic in topics:
            self.client.subscribe(topic, 0)
            logger.debug(f"Subscribed to topic: {topic}")
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            logger.debug(f"Received message on topic {topic}: {payload}")
            
            # Store last message for each topic
            self.last_messages[topic] = payload
            
            # Parse JSON payload
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                logger.warning(f"Invalid JSON payload on topic {topic}: {payload}")
                return
            
            # Handle message based on topic
            self._handle_message(topic, data)
            
        except Exception as e:
            logger.error(f"Error handling MQTT message: {e}")
    
    def _handle_message(self, topic: str, data: Dict[str, Any]):
        """Handle incoming MQTT messages"""
        
        # Home Assistant control messages
        if topic.startswith(f"{mqtt_topics.hass_base}/"):
            self._handle_hass_message(topic, data)
        
        # System control messages
        elif topic.startswith(f"{mqtt_topics.control_base}/"):
            self._handle_control_message(topic, data)
        
        # Configuration messages
        elif topic.startswith(f"{mqtt_topics.base_topic}/config/"):
            self._handle_config_message(topic, data)
        
        # TaskMaster AI messages
        elif topic.startswith(f"{mqtt_topics.taskmaster_base}/"):
            self._handle_taskmaster_message(topic, data)
        
        # Call registered message handlers
        if topic in self.message_handlers:
            try:
                self.message_handlers[topic](data)
            except Exception as e:
                logger.error(f"Error in message handler for topic {topic}: {e}")
    
    def _handle_hass_message(self, topic: str, data: Dict[str, Any]):
        """Handle Home Assistant messages"""
        logger.info(f"Handling Home Assistant message: {topic}")
        
        # Extract entity from topic
        entity = topic.split('/')[1]
        
        if 'state' in data:
            # Handle state changes
            self._handle_hass_state_change(entity, data['state'])
        elif 'command' in data:
            # Handle commands
            self._handle_hass_command(entity, data['command'])
    
    def _handle_hass_state_change(self, entity: str, state: Any):
        """Handle Home Assistant state changes"""
        logger.info(f"Home Assistant state change: {entity} = {state}")
        
        # Map entity names to system controls
        entity_mapping = {
            'pump': 'primary_pump',
            'heater': 'cartridge_heater',
            'test_mode': 'test_mode',
            'manual_control': 'manual_control',
            'set_temp_tank': 'set_temp_tank_1',
            'delta_temp_start': 'dTStart_tank_1',
            'delta_temp_stop': 'dTStop_tank_1',
            'cooling_collector': 'kylning_kollektor',
            'boiling_temp': 'temp_kok',
        }
        
        if entity in entity_mapping:
            system_control = entity_mapping[entity]
            # Emit event for system to handle
            self._emit_system_event(f"hass_{system_control}_change", {
                'entity': entity,
                'system_control': system_control,
                'value': state
            })
    
    def _handle_hass_command(self, entity: str, command: str):
        """Handle Home Assistant commands"""
        logger.info(f"Home Assistant command: {entity} -> {command}")
        
        # Map commands to system actions
        command_mapping = {
            'pump_on': {'action': 'set_pump', 'state': True},
            'pump_off': {'action': 'set_pump', 'state': False},
            'heater_on': {'action': 'set_heater', 'state': True},
            'heater_off': {'action': 'set_heater', 'state': False},
            'emergency_stop': {'action': 'emergency_stop'},
            'reset_system': {'action': 'reset_system'},
        }
        
        if command in command_mapping:
            action_data = command_mapping[command]
            self._emit_system_event(f"hass_command_{command}", action_data)
    
    def _handle_control_message(self, topic: str, data: Dict[str, Any]):
        """Handle system control messages"""
        logger.info(f"Handling control message: {topic}")
        
        control_type = topic.split('/')[-1]
        
        if control_type == 'pump':
            self._emit_system_event('control_pump', data)
        elif control_type == 'heater':
            self._emit_system_event('control_heater', data)
        elif control_type == 'system':
            self._emit_system_event('control_system', data)
    
    def _handle_config_message(self, topic: str, data: Dict[str, Any]):
        """Handle configuration messages"""
        logger.info(f"Handling config message: {topic}")
        
        config_type = topic.split('/')[-1]
        self._emit_system_event(f"config_{config_type}", data)
    
    def _handle_taskmaster_message(self, topic: str, data: Dict[str, Any]):
        """Handle TaskMaster AI messages"""
        logger.info(f"Handling TaskMaster message: {topic}")
        
        message_type = topic.split('/')[-1]
        self._emit_system_event(f"taskmaster_{message_type}", data)
    
    def _emit_system_event(self, event_type: str, data: Dict[str, Any]):
        """Emit system event for other components to handle"""
        # This would typically use an event system or callback mechanism
        logger.debug(f"Emitting system event: {event_type} with data: {data}")
        
        # For now, we'll use a simple callback mechanism
        if hasattr(self, 'system_event_callback'):
            try:
                self.system_event_callback(event_type, data)
            except Exception as e:
                logger.error(f"Error in system event callback: {e}")
    
    def publish(self, topic: str, message: Dict[str, Any], retain: bool = False) -> bool:
        """
        Publish message to MQTT topic
        
        Args:
            topic: MQTT topic
            message: Message data (will be converted to JSON)
            retain: Whether to retain the message
            
        Returns:
            True if successful, False otherwise
        """
        if not self.connected:
            logger.warning("Cannot publish: MQTT not connected")
            return False
        
        try:
            payload = json.dumps(message)
            result = self.client.publish(topic, payload, retain=retain)
            
            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic}: {payload}")
                return True
            else:
                logger.error(f"Failed to publish to {topic}: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")
            return False
    
    def publish_temperature(self, sensor_name: str, temperature: float):
        """Publish temperature reading"""
        topic = f"{mqtt_topics.temperature_base}/{sensor_name}"
        message = {
            "sensor": sensor_name,
            "temperature": temperature,
            "unit": "celsius",
            "timestamp": time.time()
        }
        return self.publish(topic, message)
    
    def publish_system_status(self, status: Dict[str, Any]):
        """Publish system status"""
        topic = mqtt_topics.status_system
        message = {
            "status": status,
            "timestamp": time.time()
        }
        return self.publish(topic, message)
    
    def publish_pump_status(self, pump_id: str, status: bool, mode: str = "auto"):
        """Publish pump status"""
        topic = f"{mqtt_topics.status_pump}/{pump_id}"
        message = {
            "pump_id": pump_id,
            "status": "on" if status else "off",
            "mode": mode,
            "timestamp": time.time()
        }
        return self.publish(topic, message)
    
    def publish_energy_status(self, energy_data: Dict[str, Any]):
        """Publish energy status"""
        topic = mqtt_topics.status_energy
        message = {
            "energy": energy_data,
            "timestamp": time.time()
        }
        return self.publish(topic, message)
    
    def publish_hass_discovery(self, entity_type: str, entity_id: str, config: Dict[str, Any]):
        """Publish Home Assistant discovery configuration"""
        topic = f"{mqtt_topics.hass_discovery_prefix}/{entity_type}/{entity_id}/config"
        return self.publish(topic, config, retain=True)
    
    def register_message_handler(self, topic: str, handler: Callable):
        """Register a message handler for a specific topic"""
        self.message_handlers[topic] = handler
        logger.debug(f"Registered message handler for topic: {topic}")
    
    def get_last_message(self, topic: str) -> Optional[Any]:
        """Get the last message received on a topic"""
        return self.last_messages.get(topic)
    
    def is_connected(self) -> bool:
        """Check if MQTT is connected"""
        return self.connected and self.client and self.client.is_connected()
    
    def set_system_event_callback(self, callback: Callable):
        """Set callback for system events"""
        self.system_event_callback = callback
