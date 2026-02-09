#!/usr/bin/env python3
"""
Fixed MQTT Handler for Solar Heating System v3
Resolves "Invalid subscription filter" errors by correcting MQTT topic patterns

Issue #44 - MQTT Authentication Security:
- Credentials loaded from environment variables
- Comprehensive connection logging
- Authentication failure handling
- No hardcoded credentials
"""

import json
import logging
import time
from typing import Dict, Any, Optional, Callable
from paho.mqtt import client as mqtt_client
from config import mqtt_topics, SystemConfig
from mqtt_authenticator import MQTTAuthenticator

logger = logging.getLogger(__name__)

class MQTTHandler:
    """MQTT handler for system communication"""
    
    def __init__(self, config: SystemConfig):
        """
        Initialize MQTT handler with secure configuration
        
        Args:
            config: SystemConfig instance with MQTT credentials
        
        Raises:
            ValueError: If MQTT credentials are invalid
        
        Security Note:
            Validates credentials immediately at initialization.
            System will fail to start if credentials are missing/invalid.
        """
        self.client = None
        self.connected = False
        
        # Create authenticator (validates credentials)
        self.authenticator = MQTTAuthenticator(config)
        
        # Validate credentials at initialization (fail fast)
        if not self.authenticator.validate_credentials():
            raise ValueError(
                "Invalid MQTT credentials. Set MQTT_USERNAME and MQTT_PASSWORD "
                "environment variables."
            )
        
        # Store connection parameters from validated config
        self.broker = config.mqtt_broker
        self.port = config.mqtt_port
        self.username = config.mqtt_username
        self.password = config.mqtt_password
        self.client_id = f"{config.mqtt_client_id}_{int(time.time())}"
        
        # Reconnection settings
        self.first_reconnect_delay = 1
        self.reconnect_rate = 2
        self.max_reconnect_count = 5
        self.max_reconnect_delay = 60
        
        # Message storage
        self.last_messages: Dict[str, str] = {}
        
        # Callbacks
        self.system_callback: Optional[Callable] = None
        
        # Message handlers
        self.message_handlers: Dict[str, Callable] = {}
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        try:
            self.client = mqtt_client.Client(client_id=self.client_id)
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
        """
        MQTT connection callback with enhanced security logging
        
        Issue #44: Enhanced authentication logging and return code interpretation
        """
        # Interpret return code using authenticator
        status, reason, severity = self.authenticator.interpret_return_code(rc)
        
        # Log connection attempt with security context
        self.authenticator.log_connection_attempt(
            rc=rc,
            client_id=self.client_id,
            success=(rc == 0)
        )
        
        if rc == 0 and client.is_connected():
            self.connected = True
            logger.info(
                f"✅ MQTT Connection Successful - "
                f"ClientID: {self.client_id}, "
                f"Broker: {self.broker}:{self.port}, "
                f"User: {self.username}"
            )
            
            # Subscribe to topics
            self._subscribe_to_topics()
            
            # Optional: Verify broker security
            try:
                if not self.authenticator.verify_broker_security(client):
                    logger.warning(
                        "⚠️  SECURITY WARNING: Broker may allow anonymous connections. "
                        "Verify broker configuration (allow_anonymous false)"
                    )
            except Exception as e:
                logger.debug(f"Broker security check failed: {e}")
                
        else:
            self.connected = False
            
            # Enhanced error logging based on return code
            if rc == 4:  # Bad username/password
                logger.error(
                    f"❌ MQTT Authentication Failed - "
                    f"ClientID: {self.client_id}, "
                    f"RC: {rc}, "
                    f"Reason: {reason}. "
                    f"Check MQTT_USERNAME and MQTT_PASSWORD environment variables."
                )
            elif rc == 5:  # Not authorized
                logger.error(
                    f"❌ MQTT Authorization Failed - "
                    f"ClientID: {self.client_id}, "
                    f"RC: {rc}, "
                    f"Reason: {reason}. "
                    f"User '{self.username}' not authorized for this broker. "
                    f"Check broker ACL configuration."
                )
            else:
                logger.error(
                    f"❌ MQTT Connection Failed - "
                    f"ClientID: {self.client_id}, "
                    f"RC: {rc}, "
                    f"Reason: {reason}"
                )
    
    def _on_disconnect(self, client, userdata, rc):
        """MQTT disconnection callback"""
        self.connected = False
        logger.info(f"Disconnected from MQTT broker with result code: {rc}")
        
        # Attempt reconnection
        self._reconnect()
    
    def _reconnect(self):
        """
        Reconnect to MQTT broker with exponential backoff
        
        Issue #44: Re-validates credentials before each reconnection attempt
        """
        reconnect_count = 0
        reconnect_delay = self.first_reconnect_delay
        
        while reconnect_count < self.max_reconnect_count:
            logger.info(
                f"MQTT Reconnection Attempt {reconnect_count + 1}/{self.max_reconnect_count} "
                f"in {reconnect_delay} seconds..."
            )
            time.sleep(reconnect_delay)
            
            try:
                # Re-validate credentials before reconnecting (security check)
                if not self.authenticator.validate_credentials():
                    logger.error("Cannot reconnect: Invalid credentials")
                    return
                
                # Properly disconnect and cleanup before reconnecting
                if self.client:
                    self.client.loop_stop()
                    self.client.disconnect()
                
                # Create a new client to avoid connection leaks
                self.client = mqtt_client.Client(client_id=f"{self.client_id}_reconnect_{int(time.time())}")
                self.client.username_pw_set(self.username, self.password)
                self.client.on_connect = self._on_connect
                self.client.on_disconnect = self._on_disconnect
                self.client.on_message = self._on_message
                
                # Connect with new client
                self.client.connect(self.broker, self.port, keepalive=60)
                self.client.loop_start()
                
                # Wait for connection
                timeout = 10
                while not self.connected and timeout > 0:
                    time.sleep(0.1)
                    timeout -= 0.1
                
                if self.connected:
                    logger.info(
                        f"✅ MQTT Reconnection Successful after {reconnect_count + 1} attempts"
                    )
                    return
                else:
                    logger.error("Reconnect failed - connection timeout")
                    
            except Exception as err:
                logger.error(f"Reconnect failed: {err}")
            
            reconnect_delay *= self.reconnect_rate
            reconnect_delay = min(reconnect_delay, self.max_reconnect_delay)
            reconnect_count += 1
        
        logger.error(
            f"❌ MQTT Reconnection Failed after {self.max_reconnect_count} attempts. "
            f"Manual intervention required."
        )
    
    def _subscribe_to_topics(self):
        """Subscribe to MQTT topics with corrected patterns"""
        # Debug logging for topic variables
        logger.debug(f"MQTT topic variables:")
        logger.debug(f"  hass_base: {mqtt_topics.hass_base}")
        logger.debug(f"  control_base: {mqtt_topics.control_base}")
        logger.debug(f"  base_topic: {mqtt_topics.base_topic}")
        logger.debug(f"  taskmaster_base: {mqtt_topics.taskmaster_base}")
        
        topics = [
            # Home Assistant control topics (both old and new format)
            f"{mqtt_topics.hass_base}/+/control",
            f"{mqtt_topics.hass_base}/+/set",
            
            # Home Assistant discovery format topics
            "homeassistant/switch/+/set",
            "homeassistant/number/+/set",
            
            # Pellet stove data from Home Assistant (CORRECTED patterns)
            # Fixed: + wildcard must be a complete level, cannot combine with _
            "homeassistant/sensor/+/state",
            "homeassistant/binary_sensor/+/state",
            
            # Hall sensor and pulse counter (specific topics)
            "homeassistant/binary_sensor/hall_sensor/state",
            "homeassistant/sensor/pulse_counter_60s/state",
            
            # System control topics
            f"{mqtt_topics.control_base}/+",
            
            # Configuration topics
            f"{mqtt_topics.base_topic}/config/+",
            
            # TaskMaster AI topics
            f"{mqtt_topics.taskmaster_base}/+",
            
            # v1 compatibility topics
            "hass/test_switch",
        ]
        
        # Debug logging for constructed topics
        logger.debug(f"Constructed topics:")
        for i, topic in enumerate(topics):
            logger.debug(f"  {i}: {topic}")
        
        for topic in topics:
            try:
                self.client.subscribe(topic, 0)
                logger.debug(f"Subscribed to topic: {topic}")
            except Exception as e:
                logger.error(f"Failed to subscribe to topic {topic}: {e}")
    
    def _is_valid_mqtt_topic(self, topic: str) -> bool:
        """Validate MQTT topic format"""
        if not topic or not isinstance(topic, str):
            return False
        
        # Check for basic MQTT topic rules
        # Topics cannot be empty, cannot start with $, and should not contain null characters
        if topic.startswith('$') or '\x00' in topic:
            return False
        
        # Check for valid characters (basic validation)
        valid_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/+-_')
        if not all(c in valid_chars for c in topic):
            return False
        
        return True
    
    def _on_message(self, client, userdata, msg):
        """MQTT message callback"""
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            
            logger.debug(f"Received message on topic {topic}: {payload}")
            
            # Store last message for each topic
            self.last_messages[topic] = payload
            
            # Handle Home Assistant switch commands (raw string payload)
            if topic.startswith("homeassistant/switch/solar_heating_") and topic.endswith("/set"):
                self._handle_switch_command(topic, payload)
                return
            
            # Handle Home Assistant number commands (raw string payload)
            if topic.startswith("homeassistant/number/solar_heating_") and topic.endswith("/set"):
                self._handle_number_command(topic, payload)
                return
            
            # Handle v1 test switch command (raw string payload)
            if topic == "hass/test_switch":
                self._handle_v1_test_switch_command(topic, payload)
                return
            
            # Handle pellet stove data from Home Assistant (CORRECTED logic)
            # Now we subscribe to all sensor/binary_sensor topics and filter by content
            if (topic.startswith("homeassistant/sensor/") and topic.endswith("/state") or
                topic.startswith("homeassistant/binary_sensor/") and topic.endswith("/state")):
                
                # Check if this is a pellet stove related sensor
                if (self._is_pellet_stove_sensor(topic)):
                    self._handle_pellet_stove_data(topic, payload)
                    return
                
                # For non-pellet stove sensors, just store the data without warnings
                # These are normal Home Assistant sensor values (strings, not JSON)
                return
            
            # Parse JSON payload for other messages (only for non-sensor topics)
            try:
                data = json.loads(payload)
            except json.JSONDecodeError:
                # Only warn for topics that should contain JSON
                if not topic.startswith("homeassistant/sensor/") and not topic.startswith("homeassistant/binary_sensor/"):
                    logger.warning(f"Invalid JSON payload on topic {topic}: {payload}")
                return
            
            # Handle other message types
            self._handle_json_message(topic, data)
            
        except Exception as e:
            logger.error(f"Error handling MQTT message: {e}")
    
    def _is_pellet_stove_sensor(self, topic: str) -> bool:
        """Check if a topic is related to pellet stove sensors"""
        # Extract the sensor name from the topic
        # Format: homeassistant/sensor/SENSOR_NAME/state
        # Format: homeassistant/binary_sensor/SENSOR_NAME/state
        
        try:
            parts = topic.split('/')
            if len(parts) >= 3:
                sensor_name = parts[2]  # Get the sensor name part
                
                # Check if it's a pellet stove related sensor
                pellet_keywords = [
                    'pelletskamin',
                    'pellet_stove',
                    'pellet_stove_monitoring',
                    'hall_sensor',
                    'pulse_counter_60s'
                ]
                
                return any(keyword in sensor_name for keyword in pellet_keywords)
        except Exception as e:
            logger.debug(f"Error parsing pellet stove sensor topic {topic}: {e}")
        
        return False
    
    def _handle_pellet_stove_data(self, topic: str, payload: str):
        """Handle pellet stove sensor data"""
        try:
            # Parse the payload
            if payload.lower() in ['on', 'off', 'true', 'false', '1', '0']:
                # Binary sensor
                value = payload.lower() in ['on', 'true', '1']
                logger.info(f"Pellet stove binary sensor {topic}: {value}")
            else:
                # Check if it's a timestamp (common for pellet stove sensors)
                if payload.startswith('20') and ('T' in payload or '-' in payload):
                    # This is a timestamp, not a numeric value - store as string
                    value = payload
                    logger.debug(f"Pellet stove timestamp sensor {topic}: {value}")
                else:
                    # Try to parse as numeric sensor
                    try:
                        value = float(payload)
                        logger.info(f"Pellet stove numeric sensor {topic}: {value}")
                    except ValueError:
                        # Not numeric, not timestamp - store as string value
                        value = payload
                        logger.debug(f"Pellet stove string sensor {topic}: {value}")
            
            # Store the data for system use
            self.last_messages[topic] = payload
            
            # Call system callback if available
            if self.system_callback:
                try:
                    # Extract sensor name from topic for the main system
                    sensor_name = topic.split('/')[2]  # Get sensor name from topic
                    self.system_callback('pellet_stove_data', {
                        'sensor': sensor_name,
                        'value': value,
                        'payload': payload
                    })
                except Exception as e:
                    logger.error(f"Error calling system callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling pellet stove data from {topic}: {e}")
    
    def _handle_switch_command(self, topic: str, payload: str):
        """Handle Home Assistant switch commands"""
        try:
            # Extract switch name from topic
            # Format: homeassistant/switch/solar_heating_SWITCH_NAME/set
            switch_name = topic.split('/')[2].replace('solar_heating_', '')
            
            # Parse payload
            if payload.lower() in ['on', 'true', '1']:
                state = True
            elif payload.lower() in ['off', 'false', '0']:
                state = False
            else:
                logger.warning(f"Invalid switch payload: {payload}")
                return
            
            # Map switch names to relay numbers
            switch_mapping = {
                'primary_pump': 1,
                'primary_pump_manual': 1,  # Manual control also uses relay 1
                'cartridge_heater': 2  # Cartridge heater uses relay 2
            }
            
            if switch_name not in switch_mapping:
                logger.warning(f"Switch '{switch_name}' not found in mapping: {list(switch_mapping.keys())}")
                return
            
            relay_num = switch_mapping[switch_name]
            logger.info(f"Switch command: {switch_name} = {state} (relay {relay_num})")
            
            # Call system callback if available
            if self.system_callback:
                try:
                    self.system_callback('switch_command', {
                        'switch': switch_name,
                        'relay': relay_num,
                        'state': state
                    })
                except Exception as e:
                    logger.error(f"Error calling system callback: {e}")
            else:
                logger.warning("No system callback registered for switch commands")
                    
        except Exception as e:
            logger.error(f"Error handling switch command: {e}")
    
    def _handle_number_command(self, topic: str, payload: str):
        """Handle Home Assistant number commands"""
        try:
            # Extract number name from topic
            # Format: homeassistant/number/solar_heating_NUMBER_NAME/set
            number_name = topic.split('/')[2].replace('solar_heating_', '')
            
            # Parse payload
            try:
                value = float(payload)
            except ValueError:
                logger.warning(f"Invalid number payload: {payload}")
                return
            
            logger.info(f"Number command: {number_name} = {value}")
            
            # Call system callback if available
            if self.system_callback:
                try:
                    self.system_callback('number_command', {
                        'number': number_name,
                        'value': value
                    })
                except Exception as e:
                    logger.error(f"Error calling system callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling number command: {e}")
    
    def _handle_v1_test_switch_command(self, topic: str, payload: str):
        """Handle v1 test switch command"""
        try:
            # Parse payload
            if payload.lower() in ['on', 'true', '1']:
                state = True
            elif payload.lower() in ['off', 'false', '0']:
                state = False
            else:
                logger.warning(f"Invalid v1 test switch payload: {payload}")
                return
            
            logger.info(f"V1 test switch command: {state}")
            
            # Call system callback if available
            if self.system_callback:
                try:
                    self.system_callback('v1_test_switch', {
                        'state': state
                    })
                except Exception as e:
                    logger.error(f"Error calling system callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling v1 test switch command: {e}")
    
    def _handle_json_message(self, topic: str, data: Dict[str, Any]):
        """Handle JSON messages"""
        try:
            # Handle different message types based on topic structure
            if topic.startswith(f"{mqtt_topics.hass_base}/"):
                self._handle_hass_message(topic, data)
            elif topic.startswith(f"{mqtt_topics.control_base}/"):
                self._handle_control_message(topic, data)
            elif topic.startswith(f"{mqtt_topics.taskmaster_base}/"):
                self._handle_taskmaster_message(topic, data)
            else:
                logger.debug(f"Unhandled JSON message on topic {topic}: {data}")
                
        except Exception as e:
            logger.error(f"Error handling JSON message: {e}")
    
    def _handle_hass_message(self, topic: str, data: Dict[str, Any]):
        """Handle Home Assistant messages"""
        try:
            # Extract command type from topic
            # Format: hass/COMMAND_TYPE
            command_type = topic.split('/')[1]
            
            logger.info(f"Home Assistant command: {command_type} = {data}")
            
            # Call system callback if available
            if self.system_callback:
                try:
                    self.system_callback('hass_command', {
                        'command_type': command_type,
                        'data': data
                    })
                except Exception as e:
                    logger.error(f"Error calling system callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling Home Assistant message: {e}")
    
    def _handle_control_message(self, topic: str, data: Dict[str, Any]):
        """Handle control messages"""
        try:
            # Extract control type from topic
            # Format: control/CONTROL_TYPE
            control_type = topic.split('/')[1]
            
            logger.info(f"Control command: {control_type} = {data}")
            
            # Call system callback if available
            if self.system_callback:
                try:
                    self.system_callback('control_command', {
                        'control_type': control_type,
                        'data': data
                    })
                except Exception as e:
                    logger.error(f"Error calling system callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling control message: {e}")
    
    def _handle_taskmaster_message(self, topic: str, data: Dict[str, Any]):
        """Handle TaskMaster AI messages"""
        try:
            # Extract task type from topic
            # Format: taskmaster/TASK_TYPE
            task_type = topic.split('/')[1]
            
            logger.info(f"TaskMaster AI command: {task_type} = {data}")
            
            # Call system callback if available
            if self.system_callback:
                try:
                    self.system_callback('taskmaster_command', {
                        'task_type': task_type,
                        'data': data
                    })
                except Exception as e:
                    logger.error(f"Error calling system callback: {e}")
                    
        except Exception as e:
            logger.error(f"Error handling TaskMaster AI message: {e}")
    
    def publish(self, topic: str, message: Dict[str, Any], retain: bool = False) -> bool:
        """Publish JSON message to MQTT topic"""
        try:
            if not self.connected or not self.client:
                logger.warning("MQTT not connected, cannot publish")
                return False
            
            payload = json.dumps(message)
            result = self.client.publish(topic, payload, retain=retain)
            
            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic}: {message} (retain: {retain})")
                return True
            else:
                logger.error(f"Failed to publish to {topic}: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")
            return False
    
    def publish_raw(self, topic: str, message: str) -> bool:
        """Publish raw string message to MQTT topic"""
        try:
            if not self.connected or not self.client:
                logger.warning("MQTT not connected, cannot publish")
                return False
            
            result = self.client.publish(topic, message)
            
            if result.rc == mqtt_client.MQTT_ERR_SUCCESS:
                logger.debug(f"Published raw to {topic}: {message}")
                return True
            else:
                logger.error(f"Failed to publish raw to {topic}: {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"Error publishing raw to {topic}: {e}")
            return False
    
    def publish_status(self, status_data: Dict[str, Any]) -> bool:
        """Publish system status"""
        try:
            topic = f"{mqtt_topics.base_topic}/status"
            message = {
                "timestamp": time.time(),
                "version": "v3",
                **status_data
            }
            return self.publish(topic, message)
        except Exception as e:
            logger.error(f"Error publishing status: {e}")
            return False
    
    def publish_system_status(self, status_data: Dict[str, Any]) -> bool:
        """Publish system status (alias for publish_status)"""
        return self.publish_status(status_data)
    
    def publish_pump_status(self, pump_id: str, status: bool, mode: str = "auto") -> bool:
        """Publish pump status"""
        try:
            topic = f"{mqtt_topics.base_topic}/status/pump/{pump_id}"
            message = {
                "pump_id": pump_id,
                "status": "on" if status else "off",
                "mode": mode,
                "timestamp": time.time()
            }
            return self.publish(topic, message)
        except Exception as e:
            logger.error(f"Error publishing pump status: {e}")
            return False
    
    def publish_energy_status(self, energy_data: Dict[str, Any]) -> bool:
        """Publish energy status"""
        try:
            topic = f"{mqtt_topics.base_topic}/status/energy"
            message = {
                "energy": energy_data,
                "timestamp": time.time()
            }
            return self.publish(topic, message)
        except Exception as e:
            logger.error(f"Error publishing energy status: {e}")
            return False
    
    def publish_realtime_energy_sensor(self, sensor_data: Dict[str, Any]) -> bool:
        """Publish real-time energy sensor data"""
        try:
            topic = f"{mqtt_topics.base_topic}/sensor/realtime_energy"
            message = {
                "sensor_data": sensor_data,
                "timestamp": time.time()
            }
            return self.publish(topic, message)
        except Exception as e:
            logger.error(f"Error publishing real-time energy sensor: {e}")
            return False
    
    def publish_heartbeat(self, system_info: Dict[str, Any]) -> bool:
        """Publish system heartbeat"""
        try:
            topic = f"{mqtt_topics.base_topic}/heartbeat"
            message = {
                "status": "alive",
                "timestamp": time.time(),
                "version": "v3",
                **system_info
            }
            return self.publish(topic, message)
        except Exception as e:
            logger.error(f"Error publishing heartbeat: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if MQTT is connected"""
        return self.connected and self.client and self.client.is_connected()
    
    def get_last_message(self, topic: str) -> Optional[str]:
        """Get last message for a topic"""
        return self.last_messages.get(topic)
    
    def get_all_messages(self) -> Dict[str, str]:
        """Get all last messages"""
        return self.last_messages.copy()
