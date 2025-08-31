#!/usr/bin/env python3
"""
Main Application for Solar Heating System v3 - System-Wide Version
Entry point for the intelligent solar heating system (no virtual environment required)
"""

import asyncio
import logging
import signal
import sys
import time
from typing import Dict, Any

# Import system-wide packages
try:
    from config import config, pump_config
    from hardware_interface import HardwareInterface
    from mqtt_handler import MQTTHandler
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the v3 directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('solar_heating_v3.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SolarHeatingSystem:
    """Main solar heating system controller"""
    
    def __init__(self):
        self.running = False
        self.hardware = None
        self.mqtt = None
        
        # System state
        self.system_state = {
            'mode': 'startup',
            'primary_pump': False,
            'secondary_pump': False,
            'cartridge_heater': False,
            'test_mode': config.test_mode,
            'manual_control': False,
            'overheated': False,
            'last_update': time.time()
        }
        
        # Temperature data
        self.temperatures = {}
        
        # Control parameters (from config)
        self.control_params = {
            'set_temp_tank_1': config.set_temp_tank_1,
            'dTStart_tank_1': config.dTStart_tank_1,
            'dTStop_tank_1': config.dTStop_tank_1,
            'kylning_kollektor': config.kylning_kollektor,
            'temp_kok': config.temp_kok,
        }
        
        logger.info("Solar Heating System v3 (System-Wide) initialized")
    
    async def start(self):
        """Start the solar heating system"""
        logger.info("Solar Heating System v3 (System-Wide) starting...")
        
        try:
            # Initialize hardware interface
            from hardware_interface import HARDWARE_AVAILABLE
            simulation_mode = config.test_mode or not HARDWARE_AVAILABLE
            if not HARDWARE_AVAILABLE:
                logger.warning("Hardware libraries not available - forcing simulation mode")
            self.hardware = HardwareInterface(simulation_mode=simulation_mode)
            
            # Initialize MQTT handler
            self.mqtt = MQTTHandler()
            if not self.mqtt.connect():
                logger.warning("Failed to connect to MQTT broker - continuing without MQTT")
                self.mqtt = None
            
            # Publish Home Assistant discovery configuration
            if self.mqtt and self.mqtt.is_connected():
                await self._publish_hass_discovery()
            
            # Initialize system state
            self.system_state = {
                'primary_pump': False,
                'secondary_pump': False,
                'cartridge_heater': False,
                'test_mode': config.test_mode,
                'manual_control': False
            }
            
            # Initialize control parameters
            self.control_params = {
                'set_temp_tank_1': config.set_temp_tank_1,
                'dTStart_tank_1': config.dTStart_tank_1,
                'dTStop_tank_1': config.dTStop_tank_1,
                'kylning_kollektor': config.kylning_kollektor,
                'temp_kok': config.temp_kok
            }
            
            # Initialize temperature storage
            self.temperatures = {}
            
            # Test hardware
            hardware_test = self.hardware.test_hardware_connection()
            logger.info(f"Hardware test results: {hardware_test}")
            
            logger.info("Solar Heating System v3 (System-Wide) started successfully")
            logger.info("Starting main control loop...")
            
            # Start main control loop
            self.running = True
            while self.running:
                await self._read_temperatures()
                await self._process_control_logic()
                await self._publish_status()
                await asyncio.sleep(config.temperature_update_interval)
                
        except Exception as e:
            logger.error(f"Error starting system: {e}")
            raise
    
    async def _publish_hass_discovery(self):
        """Publish Home Assistant discovery configuration for all sensors"""
        try:
            # Define sensor configurations
            sensors = []
            
            # Add ALL RTD sensors (0-7, 8 total)
            for i in range(8):
                sensors.append({
                    'name': f'RTD Sensor {i}',
                    'entity_id': f'rtd_sensor_{i}',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                })
            
            # Add ALL MegaBAS sensors (1-8, 8 total)
            for i in range(1, 9):
                sensors.append({
                    'name': f'MegaBAS Sensor {i}',
                    'entity_id': f'megabas_sensor_{i}',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                })
            
            # Add named sensors for backward compatibility
            named_sensors = [
                {
                    'name': 'Solar Collector Temperature',
                    'entity_id': 'solar_collector',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Storage Tank Temperature',
                    'entity_id': 'storage_tank',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Return Line Temperature',
                    'entity_id': 'return_line',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Heat Exchanger In Temperature',
                    'entity_id': 'heat_exchanger_in',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Heat Exchanger Out Temperature',
                    'entity_id': 'heat_exchanger_out',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Storage Tank Top Temperature',
                    'entity_id': 'storage_tank_top',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Storage Tank Bottom Temperature',
                    'entity_id': 'storage_tank_bottom',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Outside Air Temperature',
                    'entity_id': 'uteluft',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Exhaust Air Temperature',
                    'entity_id': 'avluft',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Supply Air Temperature',
                    'entity_id': 'tilluft',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Return Air Temperature',
                    'entity_id': 'franluft',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Heat Exchanger Efficiency',
                    'entity_id': 'heat_exchanger_efficiency',
                    'device_class': None,
                    'unit_of_measurement': '%'
                }
            ]
            
            sensors.extend(named_sensors)
            
            # Publish discovery configuration for each sensor
            for sensor in sensors:
                config = {
                    "name": sensor['name'],
                    "unique_id": f"solar_heating_{sensor['entity_id']}",
                    "unit_of_measurement": sensor['unit_of_measurement'],
                    "state_topic": f"homeassistant/sensor/solar_heating_{sensor['entity_id']}/state",
                    "device": {
                        "name": "Solar Heating System v3",
                        "identifiers": ["solar_heating_v3"],
                        "manufacturer": "Custom",
                        "model": "Solar Heating System v3"
                    }
                }
                
                # Add device_class for temperature sensors
                if sensor['device_class']:
                    config["device_class"] = sensor['device_class']
                # No value_template needed since we're sending raw values
                
                topic = f"homeassistant/sensor/solar_heating_{sensor['entity_id']}/config"
                self.mqtt.publish(topic, config, retain=True)
                logger.info(f"Published HA discovery for {sensor['name']}")
                
        except Exception as e:
            logger.error(f"Error publishing Home Assistant discovery: {e}")
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    def _handle_system_event(self, event_type: str, data: Dict[str, Any]):
        """Handle system events from MQTT"""
        logger.info(f"System event: {event_type} - {data}")
        
        if event_type == "manual_control":
            self.system_state['manual_control'] = data.get('enabled', False)
        elif event_type == "test_mode":
            self.system_state['test_mode'] = data.get('enabled', False)
    
    async def _main_loop(self):
        """Main system control loop"""
        logger.info("Starting main control loop...")
        
        while self.running:
            try:
                # Read temperatures
                await self._read_temperatures()
                
                # Process control logic
                await self._process_control_logic()
                
                # Publish system status
                await self._publish_status()
                
                # Wait for next cycle
                await asyncio.sleep(config.temperature_update_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info("Main loop stopped")
    
    async def _read_temperatures(self):
        """Read all temperature sensors"""
        try:
            # Read ALL RTD sensors (0-7, 8 total sensors)
            for sensor_id in range(8):
                sensor_name = f'rtd_sensor_{sensor_id}'
                temp = self.hardware.read_rtd_temperature(sensor_id)
                self.temperatures[sensor_name] = temp
                logger.debug(f"{sensor_name}: {temp}°C")
            
            # Read ALL MegaBAS sensors (1-8, 8 total sensors)
            for sensor_id in range(1, 9):
                sensor_name = f'megabas_sensor_{sensor_id}'
                temp = self.hardware.read_megabas_temperature(sensor_id)
                self.temperatures[sensor_name] = temp
                logger.debug(f"{sensor_name}: {temp}°C")
            
            # Map specific sensors to meaningful names for backward compatibility
            # RTD sensors (based on existing mapping)
            self.temperatures['solar_collector'] = self.temperatures.get('rtd_sensor_5', 0)  # T1 - sensor marked I
            self.temperatures['storage_tank'] = self.temperatures.get('rtd_sensor_6', 0)     # T2 - sensor marked II
            self.temperatures['return_line'] = self.temperatures.get('rtd_sensor_7', 0)      # T3 - sensor marked III
            
            # MegaBAS sensors (based on existing mapping)
            self.temperatures['heat_exchanger_in'] = self.temperatures.get('megabas_sensor_1', 0)
            self.temperatures['heat_exchanger_out'] = self.temperatures.get('megabas_sensor_2', 0)
            self.temperatures['storage_tank_top'] = self.temperatures.get('megabas_sensor_3', 0)
            self.temperatures['storage_tank_bottom'] = self.temperatures.get('megabas_sensor_4', 0)
            
            # FTX sensors (MegaBAS inputs 1-4)
            self.temperatures['uteluft'] = self.temperatures.get('megabas_sensor_1', 0)      # sensor marked 4
            self.temperatures['avluft'] = self.temperatures.get('megabas_sensor_2', 0)       # sensor marked 5
            self.temperatures['tilluft'] = self.temperatures.get('megabas_sensor_3', 0)      # sensor marked 6
            self.temperatures['franluft'] = self.temperatures.get('megabas_sensor_4', 0)     # sensor marked 7
            
            # Calculate heat exchanger efficiency
            avluft = self.temperatures.get('avluft', 0)
            franluft = self.temperatures.get('franluft', 0)
            if franluft > 0:  # Avoid division by zero
                effekt_varmevaxlare = round(100 - (avluft/franluft*100), 1)
                self.temperatures['heat_exchanger_efficiency'] = effekt_varmevaxlare
                logger.debug(f"heat_exchanger_efficiency: {effekt_varmevaxlare}%")
                
        except Exception as e:
            logger.error(f"Error reading temperatures: {e}")
    
    async def _process_control_logic(self):
        """Process control logic based on temperatures"""
        try:
            # Get key temperatures
            solar_collector = self.temperatures.get('solar_collector', 0)
            storage_tank = self.temperatures.get('storage_tank', 0)
            
            # Basic control logic (simplified version)
            if solar_collector > storage_tank + self.control_params['dTStart_tank_1']:
                if not self.system_state['primary_pump']:
                    self.hardware.set_relay_state(1, True)  # Primary pump relay
                    self.system_state['primary_pump'] = True
                    logger.info("Primary pump started")
            elif solar_collector < storage_tank + self.control_params['dTStop_tank_1']:
                if self.system_state['primary_pump']:
                    self.hardware.set_relay_state(1, False)  # Primary pump relay
                    self.system_state['primary_pump'] = False
                    logger.info("Primary pump stopped")
                    
        except Exception as e:
            logger.error(f"Error in control logic: {e}")
    
    async def _publish_status(self):
        """Publish system status to MQTT"""
        try:
            # Publish individual sensors for Home Assistant
            for sensor_name, value in self.temperatures.items():
                if self.mqtt and self.mqtt.is_connected():
                    # Publish to Home Assistant compatible topic
                    topic = f"homeassistant/sensor/solar_heating_{sensor_name}/state"
                    
                    # Determine if this is a temperature sensor or other type
                    if sensor_name == 'heat_exchanger_efficiency':
                        # For efficiency, send the value directly
                        message = str(value)
                        logger.debug(f"Published {sensor_name}: {value}% to {topic}")
                    else:
                        # For temperature sensors, send the value directly
                        message = str(value)
                        logger.debug(f"Published {sensor_name}: {value}°C to {topic}")
                    
                    self.mqtt.publish(topic, message)
            
            # Publish system status
            status_data = {
                'system_state': self.system_state,
                'temperatures': self.temperatures,
                'timestamp': time.time()
            }
            
            if self.mqtt and self.mqtt.is_connected():
                self.mqtt.publish_status(status_data)
                
        except Exception as e:
            logger.error(f"Error publishing status: {e}")
    
    async def stop(self):
        """Stop the solar heating system"""
        logger.info("Stopping Solar Heating System v3...")
        
        self.running = False
        
        # Stop pumps
        if self.hardware:
            self.hardware.set_relay_state(1, False)  # Primary pump
            self.hardware.set_relay_state(2, False)  # Secondary pump
        
        # Disconnect MQTT
        if self.mqtt and self.mqtt.is_connected():
            self.mqtt.disconnect()
        
        logger.info("Solar Heating System v3 stopped")

async def main():
    """Main entry point"""
    system = SolarHeatingSystem()
    
    try:
        await system.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
    finally:
        await system.stop()

if __name__ == "__main__":
    # Run the system
    asyncio.run(main())
