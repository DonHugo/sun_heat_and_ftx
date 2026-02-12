"""
REST API Server for Solar Heating System v3
Integrated with main_system.py to provide clean API endpoints
Following TDD principles and design specifications

Issue #43: Added pydantic validation for input security
"""

import json
import logging
import threading
import time
from datetime import datetime
from typing import Dict, Any, Optional
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
import subprocess
import re

# Import pydantic models for validation (Issue #43)
from api_models import (
    ControlRequest,
    ModeRequest,
    validate_request,
    ValidationErrorResponse
)

logger = logging.getLogger(__name__)
class SolarHeatingAPI:
    """REST API server for Solar Heating System"""
    
    def __init__(self, solar_system_instance, host='0.0.0.0', port=5001):
        """
        Initialize API server with reference to main system instance
        
        Args:
            solar_system_instance: Reference to the main SolarHeatingSystem instance
            host: API server host (default: 0.0.0.0)
            port: API server port (default: 5001)
        """
        self.solar_system = solar_system_instance
        self.host = host
        self.port = port
        self.app = Flask(__name__)
        self.api = Api(self.app)
        self.lock = threading.Lock()
        
        # Setup API routes
        self._setup_routes()
        
        # CORS support for frontend
        self._setup_cors()
    
    def _setup_routes(self):
        """Setup all API routes"""
        self.api.add_resource(SystemStatusAPI, '/api/status')
        self.api.add_resource(ControlAPI, '/api/control')
        self.api.add_resource(ModeAPI, '/api/mode')
        self.api.add_resource(TemperaturesAPI, '/api/temperatures')
        self.api.add_resource(MQTTAPI, '/api/mqtt')
    
    def _setup_cors(self):
        """Setup CORS for frontend access"""
        @self.app.after_request
        def after_request(response):
            response.headers.add('Access-Control-Allow-Origin', '*')
            response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
            response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
            return response
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get complete system status"""
        with self.lock:
            try:
                # Get system state from main system
                system_state = self.solar_system.system_state.copy()
                
                # Get temperatures from main system
                # Get temperatures from main system
                temperatures = {}
                if hasattr(self.solar_system, 'get_temperatures'):
                    temperatures = self.solar_system.get_temperatures()
                    logger.info("Using get_temperatures() method")
                elif hasattr(self.solar_system, 'temperatures'):
                    # Read from system's temperatures dictionary
                    temps = self.solar_system.temperatures
                    logger.info(f"Reading from temperatures dict. Keys: {list(temps.keys())[:10]}")
                    logger.info(f"storage_tank_temp={temps.get('storage_tank_temp')}, solar_collector_temp={temps.get('solar_collector_temp')}")
                    
                    temperatures = {
                        "tank": round(temps.get('storage_tank_temp') or 0, 1),
                        "solar_collector": round(temps.get('solar_collector_temp') or 0, 1),
                        "ambient": round(temps.get('megabas_sensor_1') or 0, 1),
                        "heat_exchanger_in": round(temps.get('megabas_sensor_1') or 0, 1),
                        "collector_in": round(temps.get('megabas_sensor_5') or 0, 1),
                        "collector_out": round(temps.get('megabas_sensor_6') or 0, 1),
                        "tank_top": round(temps.get('megabas_sensor_7') or 0, 1),
                        "tank_middle": round(temps.get('megabas_sensor_8') or 0, 1),
                        "tank_bottom": round(temps.get('megabas_sensor_9') or 0, 1)
                    }
                else:
                    # Fallback temperature data
                    logger.info("No temperature source available, using fallback data")
                    temperatures = {
                        "tank": 65.5,
                        "solar_collector": 72.1,
                        "ambient": 15.0,
                        "heat_exchanger_in": 68.9
                    }

                # Get MQTT status
                mqtt_status = self._get_mqtt_status()
                
                # Get hardware status
                hardware_status = self._get_hardware_status()
                
                # Get service status
                service_status = self._get_service_status()
                
                return {
                    "system_state": system_state,
                    "temperatures": temperatures,
                    "mqtt_status": mqtt_status,
                    "hardware_status": hardware_status,
                    "service_status": service_status,
                    "timestamp": datetime.now().isoformat() + "Z"
                }
            except Exception as e:
                return {
                    "error": f"Failed to get system status: {str(e)}",
                    "timestamp": datetime.now().isoformat() + "Z"
                }
    
    def _get_mqtt_status(self) -> Dict[str, Any]:
        """Get MQTT connection status and last message"""
        try:
            # Check MQTT connection status
            connected = False
            broker_status = "Disconnected"
            last_message = {
                "topic": "No messages",
                "payload": "No data",
                "timestamp": "Never",
                "qos": 0
            }
            
            # Try to get MQTT status from main system
            if hasattr(self.solar_system, 'mqtt_client') and self.solar_system.mqtt_client:
                connected = self.solar_system.mqtt_client.is_connected()
                broker_status = "Connected" if connected else "Disconnected"
            
            # Get last MQTT message from logs
            last_message = self._get_last_mqtt_message()
            
            return {
                "connected": connected,
                "broker": broker_status,
                "last_message": last_message
            }
        except Exception as e:
            return {
                "connected": False,
                "broker": "Error",
                "last_message": {
                    "topic": "Error",
                    "payload": str(e),
                    "timestamp": "Error",
                    "qos": 0
                }
            }
    
    def _get_last_mqtt_message(self) -> Dict[str, Any]:
        """Get last MQTT message from logs"""
        try:
            # Use journalctl to get recent MQTT messages
            command = "journalctl -u solar_heating_v3.service --since '5 minutes ago' | grep 'mqtt_handler - INFO -' | tail -n 20"
            log_output = subprocess.check_output(command, shell=True, text=True).strip()
            
            if log_output:
                # Parse the last message
                lines = log_output.split('\n')
                last_line = lines[-1] if lines else ""
                
                # Extract topic and payload using regex
                mqtt_pattern = re.compile(
                    r'^(?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}),\d{3} - mqtt_handler - INFO - .*? (?P<topic>homeassistant/[^:]+): (?P<payload>.*)$'
                )
                
                match = mqtt_pattern.match(last_line)
                if match:
                    return {
                        "topic": match.group('topic'),
                        "payload": match.group('payload'),
                        "timestamp": match.group('timestamp'),
                        "qos": 0
                    }
            
            return {
                "topic": "No messages",
                "payload": "No data",
                "timestamp": "Never",
                "qos": 0
            }
        except Exception as e:
            return {
                "topic": "Error",
                "payload": str(e),
                "timestamp": "Error",
                "qos": 0
            }
    
    def _get_hardware_status(self) -> Dict[str, str]:
        """Get hardware status"""
        try:
            status = {
                "rtd_boards": "Unknown",
                "relays": "Unknown",
                "sensors": "Unknown"
            }
            
            if hasattr(self.solar_system, 'hardware') and self.solar_system.hardware:
                status["rtd_boards"] = "Connected"
                status["relays"] = "Connected"
                status["sensors"] = "Active"
            
            return status
        except Exception:
            return {
                "rtd_boards": "Error",
                "relays": "Error",
                "sensors": "Error"
            }
    
    def _get_service_status(self) -> Dict[str, str]:
        """Get systemd service status"""
        try:
            services = ["solar_heating_v3", "mqtt", "solar_heating_watchdog"]
            status = {}
            
            for service in services:
                try:
                    result = subprocess.run(
                        ["systemctl", "is-active", service],
                        capture_output=True, text=True, timeout=5
                    )
                    status[service] = result.stdout.strip() if result.returncode == 0 else "inactive"
                except:
                    status[service] = "unknown"
            
            return status
        except Exception:
            return {
                "solar_heating_v3": "unknown",
                "mqtt": "unknown",
                "solar_heating_watchdog": "unknown"
            }
    
    def control_system(self, action: str) -> Dict[str, Any]:
        """Control system actions"""
        with self.lock:
            try:
                if action == "pump_start":
                    if self.solar_system.system_state.get('manual_control', False):
                        # Control pump hardware
                        if hasattr(self.solar_system, 'hardware') and self.solar_system.hardware:
                            self.solar_system.hardware.set_relay_state(1, False)  # Assuming relay 1 for pump
                        
                        # Update system state
                        self.solar_system.system_state['primary_pump'] = True
                        self.solar_system.system_state['primary_pump_manual'] = True
                        
                        # Publish to MQTT
                        self._publish_mqtt("homeassistant/switch/solar_heating_pump/state", "ON")
                        
                        return {
                            "success": True,
                            "message": "Pump started successfully",
                            "system_state": {
                                "primary_pump": True,
                                "mode": "manual"
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Manual control not enabled",
                            "error_code": "MANUAL_CONTROL_REQUIRED"
                        }
                
                elif action == "pump_stop":
                    if self.solar_system.system_state.get('manual_control', False):
                        # Control pump hardware
                        if hasattr(self.solar_system, 'hardware') and self.solar_system.hardware:
                            self.solar_system.hardware.set_relay_state(1, True)  # Assuming relay 1 for pump
                        
                        # Update system state
                        self.solar_system.system_state['primary_pump'] = False
                        self.solar_system.system_state['primary_pump_manual'] = False
                        
                        # Publish to MQTT
                        self._publish_mqtt("homeassistant/switch/solar_heating_pump/state", "OFF")
                        
                        return {
                            "success": True,
                            "message": "Pump stopped successfully",
                            "system_state": {
                                "primary_pump": False
                            }
                        }
                    else:
                        return {
                            "success": False,
                            "error": "Manual control not enabled",
                            "error_code": "MANUAL_CONTROL_REQUIRED"
                        }
                
                elif action == "emergency_stop":
                    # Emergency stop should always work
                    if hasattr(self.solar_system, 'hardware') and self.solar_system.hardware:
                        self.solar_system.hardware.set_relay_state(1, True)  # Turn off pump
                    
                    # Update system state
                    self.solar_system.system_state['primary_pump'] = False
                    self.solar_system.system_state['cartridge_heater'] = False
                    self.solar_system.system_state['mode'] = 'auto'
                    self.solar_system.system_state['manual_control'] = False
                    
                    # Publish to MQTT
                    self._publish_mqtt("homeassistant/switch/solar_heating_pump/state", "OFF")
                    self._publish_mqtt("homeassistant/select/solar_heating_mode/state", "Auto")
                    
                    return {
                        "success": True,
                        "message": "Emergency stop activated",
                        "system_state": {
                            "primary_pump": False,
                            "cartridge_heater": False,
                            "mode": "auto"
                        }
                    }
                
                # Note: No else clause needed - pydantic validation ensures valid action
                # This code is unreachable due to enum validation (Issue #43)
            
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Control failed: {str(e)}",
                    "error_code": "SYSTEM_ERROR"
                }
    
    def set_system_mode(self, mode: str) -> Dict[str, Any]:
        """
        Set system mode
        
        Note: mode parameter is pre-validated by pydantic (Issue #43)
        Only valid modes (auto, manual) can reach this method
        """
        with self.lock:
            try:
                # No validation needed - pydantic ensures valid mode
                # Update system state
                self.solar_system.system_state['mode'] = mode
                self.solar_system.system_state['manual_control'] = (mode == 'manual')
                
                # Publish to MQTT
                mode_capitalized = mode.capitalize()
                self._publish_mqtt("homeassistant/select/solar_heating_mode/state", mode_capitalized)
                
                return {
                    "success": True,
                    "message": f"System mode set to {mode}",
                    "system_state": {
                        "mode": mode,
                        "manual_control": (mode == 'manual')
                    }
                }
            
            except Exception as e:
                return {
                    "success": False,
                    "error": f"Mode change failed: {str(e)}",
                    "error_code": "SYSTEM_ERROR"
                }
    
    def _publish_mqtt(self, topic: str, payload: str):
        """Publish message to MQTT"""
        try:
            subprocess.run([
                "mosquitto_pub", "-h", "localhost", "-t", topic, 
                "-m", payload, "-q", "0", "-r"
            ], timeout=5)
        except Exception as e:
            print(f"MQTT publish failed: {e}")
    
    def start_server(self):
        """Start the API server"""
        try:
            print(f"Starting Solar Heating API server on {self.host}:{self.port}")
            self.app.run(host=self.host, port=self.port, debug=False, threaded=True)
        except Exception as e:
            print(f"Failed to start API server: {e}")


# API Resource Classes
class SystemStatusAPI(Resource):
    def get(self):
        """GET /api/status"""
        api_server = getattr(SystemStatusAPI, '_api_server', None)
        if not api_server:
            return {"error": "API server not initialized"}, 500
        
        return api_server.get_system_status()


class ControlAPI(Resource):
    @validate_request(ControlRequest)
    def post(self, validated_data):
        """
        POST /api/control
        
        Validates control actions using pydantic (Issue #43)
        Only valid actions (pump_start, pump_stop, emergency_stop) are accepted
        """
        api_server = getattr(ControlAPI, '_api_server', None)
        if not api_server:
            return {"error": "API server not initialized"}, 500
        
        # validated_data is a ControlRequest pydantic model
        # action is already validated to be one of the enum values
        # In pydantic v2, enum fields return the string value directly
        return api_server.control_system(validated_data.action)


class ModeAPI(Resource):
    @validate_request(ModeRequest)
    def post(self, validated_data):
        """
        POST /api/mode
        
        Validates mode changes using pydantic (Issue #43)
        Only valid modes (auto, manual) are accepted
        """
        api_server = getattr(ModeAPI, '_api_server', None)
        if not api_server:
            return {"error": "API server not initialized"}, 500
        
        # validated_data is a ModeRequest pydantic model
        # mode is already validated to be one of the enum values
        # In pydantic v2, enum fields return the string value directly
        return api_server.set_system_mode(validated_data.mode)


class TemperaturesAPI(Resource):
    def get(self):
        """GET /api/temperatures"""
        api_server = getattr(TemperaturesAPI, '_api_server', None)
        if not api_server:
            return {"error": "API server not initialized"}, 500
        
        try:
            temperatures = {}
            if hasattr(api_server.solar_system, 'get_temperatures'):
                temperatures = api_server.solar_system.get_temperatures()
                logger.info("TemperaturesAPI: Using get_temperatures() method")
            elif hasattr(api_server.solar_system, 'temperatures'):
                # Read from system's temperatures dictionary
                temps = api_server.solar_system.temperatures
                logger.info(f"TemperaturesAPI: Reading from temperatures dict. Sample keys: {list(temps.keys())[:5]}")
                logger.info(f"TemperaturesAPI: storage_tank_temp={temps.get('storage_tank_temp')}, solar_collector_temp={temps.get('solar_collector_temp')}")
                
                temperatures = {
                    "tank": round(temps.get('storage_tank_temp') or 0, 1),
                    "solar_collector": round(temps.get('solar_collector_temp') or 0, 1),
                    "ambient": round(temps.get('megabas_sensor_1') or 0, 1),
                    "heat_exchanger_in": round(temps.get('megabas_sensor_1') or 0, 1),
                    "collector_in": round(temps.get('megabas_sensor_5') or 0, 1),
                    "collector_out": round(temps.get('megabas_sensor_6') or 0, 1),
                    "tank_top": round(temps.get('megabas_sensor_7') or 0, 1),
                    "tank_middle": round(temps.get('megabas_sensor_8') or 0, 1),
                    "tank_bottom": round(temps.get('megabas_sensor_9') or 0, 1)
                }
            else:
                # Fallback temperature data
                logger.info("TemperaturesAPI: No temperature source available, using fallback data")
                temperatures = {
                    "tank": 65.5,
                    "solar_collector": 72.1,
                    "ambient": 15.0,
                    "heat_exchanger_in": 68.9
                }

            
            return {
                "temperatures": temperatures,
                "timestamp": datetime.now().isoformat() + "Z"
            }
        except Exception as e:
            return {"error": f"Failed to get temperatures: {str(e)}"}, 500


class MQTTAPI(Resource):
    def get(self):
        """GET /api/mqtt"""
        api_server = getattr(MQTTAPI, '_api_server', None)
        if not api_server:
            return {"error": "API server not initialized"}, 500
        
        mqtt_status = api_server._get_mqtt_status()
        return {
            "mqtt_status": mqtt_status,
            "timestamp": datetime.now().isoformat() + "Z"
        }


def create_api_server(solar_system_instance, host='0.0.0.0', port=5001):
    """
    Factory function to create API server with proper initialization
    
    Args:
        solar_system_instance: Reference to the main SolarHeatingSystem instance
        host: API server host
        port: API server port
    
    Returns:
        SolarHeatingAPI: Configured API server instance
    """
    api_server = SolarHeatingAPI(solar_system_instance, host, port)
    
    # Set API server reference in resource classes
    SystemStatusAPI._api_server = api_server
    ControlAPI._api_server = api_server
    ModeAPI._api_server = api_server
    TemperaturesAPI._api_server = api_server
    MQTTAPI._api_server = api_server
    
    return api_server
