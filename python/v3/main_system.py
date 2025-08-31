#!/usr/bin/env python3
"""
Main Application for Solar Heating System v3 - System-Wide Version
Entry point for the intelligent solar heating system (no virtual environment required)

V1 COMPATIBILITY: This version includes parallel MQTT messages that match v1 format
for backward compatibility. See comments in _publish_v1_parallel_messages() for details.
"""

import asyncio
import json
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
            'last_update': time.time(),
            'pump_runtime_hours': 0.0,
            'heating_cycles_count': 0,
            'last_pump_start': None,
            'total_heating_time': 0.0
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
            else:
                # Register system callback for switch commands
                self.mqtt.system_callback = self._handle_mqtt_command
            
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
            
            # Add named sensors with improved naming
            named_sensors = [
                # Key system temperatures
                {
                    'name': 'Solar Collector Outlet Temperature',
                    'entity_id': 'solar_collector_temp',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Storage Tank Main Temperature',
                    'entity_id': 'storage_tank_temp',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Solar Return Line Temperature',
                    'entity_id': 'return_line_temp',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                # Water heater stratification sensors (all heights)
                {
                    'name': 'Water Heater Bottom Temperature',
                    'entity_id': 'water_heater_bottom',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Water Heater 20cm Temperature',
                    'entity_id': 'water_heater_20cm',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Water Heater 40cm Temperature',
                    'entity_id': 'water_heater_40cm',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Water Heater 60cm Temperature',
                    'entity_id': 'water_heater_60cm',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Water Heater 80cm Temperature',
                    'entity_id': 'water_heater_80cm',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Water Heater 100cm Temperature',
                    'entity_id': 'water_heater_100cm',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Water Heater 120cm Temperature',
                    'entity_id': 'water_heater_120cm',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Water Heater 140cm Temperature',
                    'entity_id': 'water_heater_140cm',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Water Heater Top Temperature (Legacy)',
                    'entity_id': 'water_heater_top',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                # FTX air temperatures
                {
                    'name': 'Outdoor Air Temperature',
                    'entity_id': 'outdoor_air_temp',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Exhaust Air Temperature',
                    'entity_id': 'exhaust_air_temp',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Supply Air Temperature',
                    'entity_id': 'supply_air_temp',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Return Air Temperature',
                    'entity_id': 'return_air_temp',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                # Heat exchanger sensors
                {
                    'name': 'Heat Exchanger Input Temperature',
                    'entity_id': 'heat_exchanger_in',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Heat Exchanger Output Temperature',
                    'entity_id': 'heat_exchanger_out',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                # Backward compatibility aliases
                {
                    'name': 'Solar Collector Temperature (Legacy)',
                    'entity_id': 'solar_collector',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Storage Tank Temperature (Legacy)',
                    'entity_id': 'storage_tank',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Return Line Temperature (Legacy)',
                    'entity_id': 'return_line',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Storage Tank Top Temperature (Legacy)',
                    'entity_id': 'storage_tank_top',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Storage Tank Bottom Temperature (Legacy)',
                    'entity_id': 'storage_tank_bottom',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Outside Air Temperature (Legacy)',
                    'entity_id': 'uteluft',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Exhaust Air Temperature (Legacy)',
                    'entity_id': 'avluft',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Supply Air Temperature (Legacy)',
                    'entity_id': 'tilluft',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Return Air Temperature (Legacy)',
                    'entity_id': 'franluft',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Heat Exchanger Efficiency',
                    'entity_id': 'heat_exchanger_efficiency',
                    'device_class': None,
                    'unit_of_measurement': '%'
                },
                {
                    'name': 'System Mode',
                    'entity_id': 'system_mode',
                    'device_class': None,
                    'unit_of_measurement': None
                },
                # Solar Collector sensors
                {
                    'name': 'Solar Collector dT Running',
                    'entity_id': 'solar_collector_dt_running',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Solar Collector dT',
                    'entity_id': 'solar_collector_dt',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                },
                {
                    'name': 'Solar Collector Pump Status',
                    'entity_id': 'solar_collector_pump',
                    'device_class': None,
                    'unit_of_measurement': None
                },
                {
                    'name': 'Solar Collector Mode',
                    'entity_id': 'solar_collector_mode',
                    'device_class': None,
                    'unit_of_measurement': None
                },
                {
                    'name': 'Solar Collector State',
                    'entity_id': 'solar_collector_state',
                    'device_class': None,
                    'unit_of_measurement': None
                },
                {
                    'name': 'Solar Collector Sub State',
                    'entity_id': 'solar_collector_sub_state',
                    'device_class': None,
                    'unit_of_measurement': None
                },
                {
                    'name': 'Solar Collector Overheated',
                    'entity_id': 'solar_collector_overheated',
                    'device_class': None,
                    'unit_of_measurement': None
                },
                # New calculated values and metrics
                {
                    'name': 'Water Heater Stratification Quality',
                    'entity_id': 'water_heater_stratification',
                    'device_class': None,
                    'unit_of_measurement': '°C/cm'
                },
                {
                    'name': 'Water Heater Temperature Gradient',
                    'entity_id': 'water_heater_gradient_cm',
                    'device_class': None,
                    'unit_of_measurement': '°C/cm'
                },
                {
                    'name': 'Sensor Health Score',
                    'entity_id': 'sensor_health_score',
                    'device_class': None,
                    'unit_of_measurement': '%'
                },
                {
                    'name': 'Overheating Risk',
                    'entity_id': 'overheating_risk',
                    'device_class': None,
                    'unit_of_measurement': '%'
                },
                {
                    'name': 'Pump Runtime Hours',
                    'entity_id': 'pump_runtime_hours',
                    'device_class': None,
                    'unit_of_measurement': 'hours'
                },
                {
                    'name': 'Heating Cycles Count',
                    'entity_id': 'heating_cycles_count',
                    'device_class': None,
                    'unit_of_measurement': 'cycles'
                },
                {
                    'name': 'Average Heating Duration',
                    'entity_id': 'average_heating_duration',
                    'device_class': None,
                    'unit_of_measurement': 'hours'
                },
                # Stored Energy sensors
                {
                    'name': 'Stored Energy Total',
                    'entity_id': 'stored_energy_kwh',
                    'device_class': 'energy',
                    'unit_of_measurement': 'kWh'
                },
                {
                    'name': 'Stored Energy Top',
                    'entity_id': 'stored_energy_top_kwh',
                    'device_class': 'energy',
                    'unit_of_measurement': 'kWh'
                },
                {
                    'name': 'Stored Energy Bottom',
                    'entity_id': 'stored_energy_bottom_kwh',
                    'device_class': 'energy',
                    'unit_of_measurement': 'kWh'
                },
                {
                    'name': 'Average Temperature',
                    'entity_id': 'average_temperature',
                    'device_class': 'temperature',
                    'unit_of_measurement': '°C'
                }
            ]
            
            sensors.extend(named_sensors)
            
            # Publish discovery configuration for each sensor
            for sensor in sensors:
                config = {
                    "name": sensor['name'],
                    "unique_id": f"solar_heating_v3_{sensor['entity_id']}",
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
                
                # Add state_class for energy sensors
                if sensor['device_class'] == 'energy':
                    config["state_class"] = "total"
                elif sensor['device_class'] == 'temperature':
                    config["state_class"] = "measurement"
                
                # No value_template needed since we're sending raw values
                
                # Debug: Log the discovery config
                logger.debug(f"Discovery config for {sensor['name']}: {config}")
                
                topic = f"homeassistant/sensor/solar_heating_{sensor['entity_id']}/config"
                success = self.mqtt.publish(topic, config, retain=True)
                if success:
                    logger.info(f"Published HA discovery for {sensor['name']} to {topic}")
                else:
                    logger.error(f"Failed to publish HA discovery for {sensor['name']} to {topic}")
            
            # Publish switch discovery configurations
            switches = [
                {
                    'name': 'Primary Pump',
                    'entity_id': 'primary_pump',
                    'icon': 'mdi:pump'
                },
                {
                    'name': 'Secondary Pump', 
                    'entity_id': 'secondary_pump',
                    'icon': 'mdi:pump'
                },
                {
                    'name': 'Cartridge Heater',
                    'entity_id': 'cartridge_heater',
                    'icon': 'mdi:heating-coil'
                }
            ]
            
            for switch in switches:
                config = {
                    "name": switch['name'],
                    "unique_id": f"solar_heating_v3_{switch['entity_id']}",
                    "state_topic": f"homeassistant/switch/solar_heating_{switch['entity_id']}/state",
                    "command_topic": f"homeassistant/switch/solar_heating_{switch['entity_id']}/set",
                    "icon": switch['icon'],
                    "device": {
                        "name": "Solar Heating System v3",
                        "identifiers": ["solar_heating_v3"],
                        "manufacturer": "Custom",
                        "model": "Solar Heating System v3"
                    }
                }
                
                topic = f"homeassistant/switch/solar_heating_{switch['entity_id']}/config"
                self.mqtt.publish(topic, config, retain=True)
                logger.info(f"Published HA discovery for {switch['name']}")
            
            # Publish number discovery configurations for config variables
            numbers = [
                {
                    'name': 'Set Tank Temperature',
                    'entity_id': 'set_temp_tank_1',
                    'unit_of_measurement': '°C',
                    'min_value': 15,
                    'max_value': 90,
                    'step': 1,
                    'icon': 'mdi:thermometer'
                },
                {
                    'name': 'Delta Temperature Start',
                    'entity_id': 'dTStart_tank_1',
                    'unit_of_measurement': '°C',
                    'min_value': 3,
                    'max_value': 40,
                    'step': 1,
                    'icon': 'mdi:thermometer-plus'
                },
                {
                    'name': 'Delta Temperature Stop',
                    'entity_id': 'dTStop_tank_1',
                    'unit_of_measurement': '°C',
                    'min_value': 2,
                    'max_value': 20,
                    'step': 1,
                    'icon': 'mdi:thermometer-minus'
                },
                {
                    'name': 'Cooling Collector Temperature',
                    'entity_id': 'kylning_kollektor',
                    'unit_of_measurement': '°C',
                    'min_value': 70,
                    'max_value': 120,
                    'step': 1,
                    'icon': 'mdi:thermometer-high'
                },
                {
                    'name': 'Boiling Temperature',
                    'entity_id': 'temp_kok',
                    'unit_of_measurement': '°C',
                    'min_value': 100,
                    'max_value': 200,
                    'step': 5,
                    'icon': 'mdi:thermometer-high'
                }
            ]
            
            for number in numbers:
                config = {
                    "name": number['name'],
                    "unique_id": f"solar_heating_v3_{number['entity_id']}",
                    "state_topic": f"homeassistant/number/solar_heating_{number['entity_id']}/state",
                    "command_topic": f"homeassistant/number/solar_heating_{number['entity_id']}/set",
                    "unit_of_measurement": number['unit_of_measurement'],
                    "min": number['min_value'],
                    "max": number['max_value'],
                    "step": number['step'],
                    "icon": number['icon'],
                    "device": {
                        "name": "Solar Heating System v3",
                        "identifiers": ["solar_heating_v3"],
                        "manufacturer": "Custom",
                        "model": "Solar Heating System v3"
                    }
                }
                
                topic = f"homeassistant/number/solar_heating_{number['entity_id']}/config"
                self.mqtt.publish(topic, config, retain=True)
                logger.info(f"Published HA discovery for {number['name']}")
                
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
            
            # MegaBAS sensors with improved naming (based on v1 mapping)
            # FTX sensors (MegaBAS inputs 1-4) - CORRECTED to match v1
            self.temperatures['outdoor_air_temp'] = self.temperatures.get('megabas_sensor_1', 0)      # Outdoor air intake
            self.temperatures['exhaust_air_temp'] = self.temperatures.get('megabas_sensor_2', 0)     # Air leaving heat exchanger
            self.temperatures['supply_air_temp'] = self.temperatures.get('megabas_sensor_3', 0)      # Air entering heat exchanger
            self.temperatures['return_air_temp'] = self.temperatures.get('megabas_sensor_4', 0)     # Air returning from heat exchanger
            
            # Solar collector and storage tank sensors (MegaBAS inputs 6-8) - CORRECTED to match v1
            self.temperatures['solar_collector_temp'] = self.temperatures.get('megabas_sensor_6', 0)  # T1 - Solar panel outlet
            self.temperatures['storage_tank_temp'] = self.temperatures.get('megabas_sensor_7', 0)     # T2 - Main storage tank
            self.temperatures['return_line_temp'] = self.temperatures.get('megabas_sensor_8', 0)      # T3 - Return line to solar collector
            
            # All water heater RTD sensors with height-based naming
            self.temperatures['water_heater_bottom'] = self.temperatures.get('rtd_sensor_0', 0)    # RTD sensor 0 - 0cm from bottom (coldest)
            self.temperatures['water_heater_20cm'] = self.temperatures.get('rtd_sensor_1', 0)     # RTD sensor 1 - 20cm from bottom
            self.temperatures['water_heater_40cm'] = self.temperatures.get('rtd_sensor_2', 0)     # RTD sensor 2 - 40cm from bottom
            self.temperatures['water_heater_60cm'] = self.temperatures.get('rtd_sensor_3', 0)     # RTD sensor 3 - 60cm from bottom
            self.temperatures['water_heater_80cm'] = self.temperatures.get('rtd_sensor_4', 0)     # RTD sensor 4 - 80cm from bottom
            self.temperatures['water_heater_100cm'] = self.temperatures.get('rtd_sensor_5', 0)    # RTD sensor 5 - 100cm from bottom
            self.temperatures['water_heater_120cm'] = self.temperatures.get('rtd_sensor_6', 0)    # RTD sensor 6 - 120cm from bottom
            self.temperatures['water_heater_140cm'] = self.temperatures.get('rtd_sensor_7', 0)    # RTD sensor 7 - 140cm from bottom (hottest)
            
            # Legacy aliases for backward compatibility
            self.temperatures['water_heater_top'] = self.temperatures['water_heater_100cm']  # Keep top alias
            
            # Keep backward compatibility aliases
            self.temperatures['uteluft'] = self.temperatures['outdoor_air_temp']
            self.temperatures['avluft'] = self.temperatures['exhaust_air_temp']
            self.temperatures['tilluft'] = self.temperatures['supply_air_temp']
            self.temperatures['franluft'] = self.temperatures['return_air_temp']
            self.temperatures['solar_collector'] = self.temperatures['solar_collector_temp']
            self.temperatures['storage_tank'] = self.temperatures['storage_tank_temp']
            self.temperatures['return_line'] = self.temperatures['return_line_temp']
            self.temperatures['storage_tank_top'] = self.temperatures['water_heater_top']
            self.temperatures['storage_tank_bottom'] = self.temperatures['water_heater_bottom']
            
            # Heat exchanger sensors (using MegaBAS sensors 1-2)
            self.temperatures['heat_exchanger_in'] = self.temperatures.get('megabas_sensor_1', 0)
            self.temperatures['heat_exchanger_out'] = self.temperatures.get('megabas_sensor_2', 0)
            
            # Calculate heat exchanger efficiency
            avluft = self.temperatures.get('avluft', 0)
            franluft = self.temperatures.get('franluft', 0)
            if franluft > 0:  # Avoid division by zero
                effekt_varmevaxlare = round(100 - (avluft/franluft*100), 1)
                self.temperatures['heat_exchanger_efficiency'] = effekt_varmevaxlare
                logger.debug(f"heat_exchanger_efficiency: {effekt_varmevaxlare}%")
            
            # Calculate water heater stratification metrics
            water_heater_140cm = self.temperatures.get('water_heater_140cm', 0)  # Top sensor
            water_heater_bottom = self.temperatures.get('water_heater_bottom', 0)  # Bottom sensor (0cm)
            if water_heater_140cm and water_heater_bottom:
                stratification_quality = round((water_heater_140cm - water_heater_bottom) / 140, 2)  # 140cm height
                gradient_per_cm = round((water_heater_140cm - water_heater_bottom) / 140, 3)
                self.temperatures['water_heater_stratification'] = stratification_quality
                self.temperatures['water_heater_gradient_cm'] = gradient_per_cm
                logger.debug(f"Stratification quality: {stratification_quality}, Gradient: {gradient_per_cm}°C/cm")
            
            # Calculate sensor health score
            valid_sensors = 0
            total_sensors = 0
            for sensor_name, temp in self.temperatures.items():
                if 'rtd_sensor_' in sensor_name or 'megabas_sensor_' in sensor_name:
                    total_sensors += 1
                    if temp is not None and temp > 0:
                        valid_sensors += 1
            
            if total_sensors > 0:
                sensor_health_score = round((valid_sensors / total_sensors) * 100, 1)
                self.temperatures['sensor_health_score'] = sensor_health_score
                logger.debug(f"Sensor health score: {sensor_health_score}%")
            
            # Calculate overheating risk
            solar_collector_temp = self.temperatures.get('solar_collector_temp', 0)
            max_safe_temp = 90  # Configurable maximum safe temperature
            if solar_collector_temp > max_safe_temp:
                overheating_risk = round(((solar_collector_temp - max_safe_temp) / max_safe_temp) * 100, 1)
                self.temperatures['overheating_risk'] = overheating_risk
                logger.warning(f"Overheating risk: {overheating_risk}% (collector: {solar_collector_temp}°C)")
            else:
                self.temperatures['overheating_risk'] = 0
            
            # Add system mode to temperatures for Home Assistant
            self.temperatures['system_mode'] = self.system_state.get('mode', 'unknown')
            logger.debug(f"system_mode: {self.temperatures['system_mode']}")
            
            # Add operational metrics to temperatures
            self.temperatures['pump_runtime_hours'] = self.system_state.get('pump_runtime_hours', 0.0)
            self.temperatures['heating_cycles_count'] = self.system_state.get('heating_cycles_count', 0)
            
            # Calculate average heating duration
            if self.system_state.get('heating_cycles_count', 0) > 0:
                avg_heating_duration = round(self.system_state.get('total_heating_time', 0) / self.system_state.get('heating_cycles_count', 1), 2)
                self.temperatures['average_heating_duration'] = avg_heating_duration
            else:
                self.temperatures['average_heating_duration'] = 0.0
            
            # Calculate solar collector dT values
            solar_collector = self.temperatures.get('solar_collector', 0)
            storage_tank = self.temperatures.get('storage_tank', 0)
            dT = solar_collector - storage_tank if solar_collector and storage_tank else 0
            
            self.temperatures['solar_collector_dt_running'] = dT
            self.temperatures['solar_collector_dt'] = dT
            self.temperatures['solar_collector_pump'] = "ON" if self.system_state.get('primary_pump', False) else "OFF"
            self.temperatures['solar_collector_mode'] = self.system_state.get('mode', 'unknown')
            self.temperatures['solar_collector_state'] = self.system_state.get('mode', 'unknown')
            self.temperatures['solar_collector_sub_state'] = "0"
            self.temperatures['solar_collector_overheated'] = "true" if self.system_state.get('overheated', False) else "false"
            
            # Calculate stored energy values (matching v1 logic)
            zero_value = 4  # Temperature of water coming from well
            stored_energy = [0] * 10
            
            # Use RTD sensors (stack 0) for energy calculations
            for i in range(8):
                temp = self.temperatures.get(f'rtd_sensor_{i}', 0)
                if temp is not None:
                    stored_energy[i] = ((temp - zero_value) * 35)
                else:
                    stored_energy[i] = 0
            
            # Add MegaBAS input 5 (sensor 5) - handle None value
            megabas_5 = self.temperatures.get('megabas_sensor_5', 0)
            if megabas_5 is not None:
                stored_energy[8] = ((megabas_5 - zero_value) * 35)
            else:
                stored_energy[8] = 0
            
            # Calculate energy values
            stored_energy_kwh = [
                round(sum(stored_energy) * 4200 / 1000 / 3600, 2),  # Total
                round(sum(stored_energy[:5]) * 4200 / 1000 / 3600, 2),  # Bottom
                round(sum(stored_energy[5:]) * 4200 / 1000 / 3600, 2),  # Top
                round(sum([self.temperatures.get(f'rtd_sensor_{i}', 0) or 0 for i in range(8)]) / 8, 1)  # Average temp
            ]
            
            self.temperatures['stored_energy_kwh'] = stored_energy_kwh[0]
            self.temperatures['stored_energy_top_kwh'] = stored_energy_kwh[2]
            self.temperatures['stored_energy_bottom_kwh'] = stored_energy_kwh[1]
            self.temperatures['average_temperature'] = stored_energy_kwh[3]
            
            # Debug logging for stored energy values
            logger.info(f"Stored Energy - Total: {stored_energy_kwh[0]} kWh, Top: {stored_energy_kwh[2]} kWh, Bottom: {stored_energy_kwh[1]} kWh, Avg Temp: {stored_energy_kwh[3]}°C")
            logger.debug(f"RTD sensor values: {[self.temperatures.get(f'rtd_sensor_{i}', 0) for i in range(8)]}")
            logger.debug(f"MegaBAS sensor 5: {self.temperatures.get('megabas_sensor_5', 0)}")
                
        except Exception as e:
            logger.error(f"Error reading temperatures: {e}")
    
    async def _process_control_logic(self):
        """Process control logic based on temperatures"""
        try:
            # Get key temperatures
            solar_collector = self.temperatures.get('solar_collector', 0)
            storage_tank = self.temperatures.get('storage_tank', 0)
            
            # Update system mode based on current state
            self._update_system_mode()
            
            # Basic control logic (simplified version)
            if solar_collector > storage_tank + self.control_params['dTStart_tank_1']:
                if not self.system_state['primary_pump']:
                    self.hardware.set_relay_state(1, True)  # Primary pump relay
                    self.system_state['primary_pump'] = True
                    self.system_state['last_pump_start'] = time.time()
                    self.system_state['heating_cycles_count'] += 1
                    logger.info("Primary pump started")
            elif solar_collector < storage_tank + self.control_params['dTStop_tank_1']:
                if self.system_state['primary_pump']:
                    self.hardware.set_relay_state(1, False)  # Primary pump relay
                    self.system_state['primary_pump'] = False
                    # Calculate runtime for this cycle
                    if self.system_state['last_pump_start']:
                        cycle_runtime = (time.time() - self.system_state['last_pump_start']) / 3600  # Convert to hours
                        self.system_state['total_heating_time'] += cycle_runtime
                        self.system_state['pump_runtime_hours'] = round(self.system_state['total_heating_time'], 2)
                        logger.info(f"Primary pump stopped. Cycle runtime: {cycle_runtime:.2f}h, Total runtime: {self.system_state['pump_runtime_hours']}h")
                    
        except Exception as e:
            logger.error(f"Error in control logic: {e}")
    
    def _update_system_mode(self):
        """Update system mode based on current state"""
        try:
            if self.system_state.get('test_mode', False):
                self.system_state['mode'] = 'test'
            elif self.system_state.get('manual_control', False):
                self.system_state['mode'] = 'manual'
            elif self.system_state.get('overheated', False):
                self.system_state['mode'] = 'overheated'
            elif self.system_state.get('primary_pump', False):
                self.system_state['mode'] = 'heating'
            else:
                self.system_state['mode'] = 'standby'
                
        except Exception as e:
            logger.error(f"Error updating system mode: {e}")
    
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
                        # For efficiency, send the raw number
                        message = str(value) if value is not None else "0"
                        logger.debug(f"Published {sensor_name}: {value}% to {topic}")
                    elif sensor_name == 'system_mode':
                        # For system mode, send the string value
                        message = str(value) if value is not None else "unknown"
                        logger.debug(f"Published {sensor_name}: {value} to {topic}")
                    elif sensor_name in ['stored_energy_kwh', 'stored_energy_top_kwh', 'stored_energy_bottom_kwh']:
                        # For energy sensors, send the raw number
                        message = str(value) if value is not None else "0"
                        logger.info(f"Published {sensor_name}: {value} kWh to {topic}")
                    elif sensor_name == 'average_temperature':
                        # For average temperature, send the raw number
                        message = str(value) if value is not None else "0"
                        logger.info(f"Published {sensor_name}: {value}°C to {topic}")
                    else:
                        # For temperature sensors, send the raw number
                        message = str(value) if value is not None else "0"
                        logger.debug(f"Published {sensor_name}: {value}°C to {topic}")
                    
                    # Send raw number, not quoted string
                    self.mqtt.publish_raw(topic, message)
            
            # ===== V1 COMPATIBILITY SECTION - START =====
            # This section publishes v1-style messages for backward compatibility
            # These messages can be safely removed when v1 is no longer needed
            # To remove: Delete this line and the entire _publish_v1_parallel_messages method below
            await self._publish_v1_parallel_messages()
            # ===== V1 COMPATIBILITY SECTION - END =====
            
            # Publish switch states
            if self.mqtt and self.mqtt.is_connected():
                self._publish_switch_state('primary_pump', self.system_state['primary_pump'])
                self._publish_switch_state('secondary_pump', self.system_state['secondary_pump'])
                self._publish_switch_state('cartridge_heater', self.system_state['cartridge_heater'])
            
            # Publish number states
            if self.mqtt and self.mqtt.is_connected():
                self._publish_number_state('set_temp_tank_1', self.control_params['set_temp_tank_1'])
                self._publish_number_state('dTStart_tank_1', self.control_params['dTStart_tank_1'])
                self._publish_number_state('dTStop_tank_1', self.control_params['dTStop_tank_1'])
                self._publish_number_state('kylning_kollektor', self.control_params['kylning_kollektor'])
                self._publish_number_state('temp_kok', self.control_params['temp_kok'])
            
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
    
    # ===== V1 COMPATIBILITY METHOD - START =====
    # This method publishes v1-style MQTT messages for backward compatibility
    # 
    # V1 MQTT Topics being replicated:
    # - sequentmicrosystems/sequentmicrosystems_{stack}_{sensor} (individual sensors)
    # - sequentmicrosystems/stored_energy (energy calculations)
    # - sequentmicrosystems/ftx (heat exchanger efficiency)
    # - sequentmicrosystems/suncollector (solar collector temperature)
    # - sequentmicrosystems/cartridge_heater (relay 1 status)
    # - sequentmicrosystems/test_switch (test mode status)
    #
    # To remove this method:
    # 1. Delete this entire method (from this comment to the end of the method)
    # 2. Remove the call to this method in _publish_status above
    # 3. Remove the "V1 COMPATIBILITY SECTION" comments in _publish_status
    async def _publish_v1_parallel_messages(self):
        """Publish v1-style parallel messages for compatibility"""
        try:
            if not self.mqtt or not self.mqtt.is_connected():
                return
                
            # 1. Individual sensor messages (sequentmicrosystems/sequentmicrosystems_{stack}_{sensor})
            for stack in range(4):  # 4 stacks
                for sensor in range(8):  # 8 sensors per stack
                    if stack == 0:  # RTD stack
                        temp = self.temperatures.get(f'rtd_sensor_{sensor}', 0)
                    elif stack == 3:  # MegaBAS stack
                        temp = self.temperatures.get(f'megabas_sensor_{sensor + 1}', 0)
                    else:
                        temp = 0  # Other stacks not used
                    
                    if temp != 0 and temp is not None:  # Only publish if we have a valid temperature
                        sensor_name = f"sequentmicrosystems_{stack + 1}_{sensor + 1}"
                        topic = f"sequentmicrosystems/{sensor_name}"
                        msg_dict = {
                            "name": sensor_name,
                            "temperature": round(temp, 1)
                        }
                        self.mqtt.publish(topic, json.dumps(msg_dict))
            
            # 2. Stored energy calculation (matching v1 logic)
            zero_value = 4  # Temperature of water coming from well
            stored_energy = [0] * 10
            
            # Use RTD sensors (stack 0) for energy calculations
            for i in range(8):
                temp = self.temperatures.get(f'rtd_sensor_{i}', 0)
                if temp is not None:
                    stored_energy[i] = ((temp - zero_value) * 35)
                else:
                    stored_energy[i] = 0
            
            # Add MegaBAS input 5 (sensor 5) - handle None value
            megabas_5 = self.temperatures.get('megabas_sensor_5', 0)
            if megabas_5 is not None:
                stored_energy[8] = ((megabas_5 - zero_value) * 35)
            else:
                stored_energy[8] = 0
            
            # Calculate energy values
            stored_energy_kwh = [
                round(sum(stored_energy) * 4200 / 1000 / 3600, 2),  # Total
                round(sum(stored_energy[:5]) * 4200 / 1000 / 3600, 2),  # Bottom
                round(sum(stored_energy[5:]) * 4200 / 1000 / 3600, 2),  # Top
                round(sum([self.temperatures.get(f'rtd_sensor_{i}', 0) or 0 for i in range(8)]) / 8, 1)  # Average temp
            ]
            
            # Publish stored energy
            stored_energy_msg = {
                "name": "stored_energy",
                "stored_energy_kwh": stored_energy_kwh[0],
                "stored_energy_top_kwh": stored_energy_kwh[2],
                "stored_energy_bottom_kwh": stored_energy_kwh[1],
                "average_temperature": stored_energy_kwh[3]
            }
            self.mqtt.publish("sequentmicrosystems/stored_energy", json.dumps(stored_energy_msg))
            
            # 3. FTX (Heat Exchanger) message - match v1 format exactl
            ftx_msg = {
                "uteluft": round(self.temperatures.get('uteluft', 0), 1),
                "avluft": round(self.temperatures.get('avluft', 0), 1),
                "tilluft": round(self.temperatures.get('tilluft', 0), 1),
                "franluft": round(self.temperatures.get('franluft', 0), 1),
                "effekt_varmevaxlare": round(self.temperatures.get('heat_exchanger_efficiency', 0), 1)
            }
            self.mqtt.publish("sequentmicrosystems/ftx", json.dumps(ftx_msg))
            
            # 4. Sun collector message - match v1 format exactly
            solar_collector = self.temperatures.get('solar_collector', 0)
            storage_tank = self.temperatures.get('storage_tank', 0)
            dT = solar_collector - storage_tank if solar_collector and storage_tank else 0
            
            suncollector_msg = {
                "dT_running": dT,
                "dT": dT,
                "pump": "ON" if self.system_state.get('primary_pump', False) else "OFF",
                "mode": self.system_state.get('mode', 'unknown'),
                "state": self.system_state.get('mode', 'unknown'),
                "sub_state": "0",
                "overheated": "true" if self.system_state.get('overheated', False) else "false"
            }
            self.mqtt.publish("sequentmicrosystems/suncollector", json.dumps(suncollector_msg))
            
            # 5. Test mode message - match v1 format exactly
            test_mode_msg = {
                "test_mode": "true" if self.system_state.get('test_mode', False) else "false",
                "log_level": config.log_level
            }
            self.mqtt.publish("sequentmicrosystems/test_mode", json.dumps(test_mode_msg))
            
            # 6. Test switch status - match v1 format exactly
            test_switch_msg = {
                "switch_status": "on" if self.system_state.get('test_mode', False) else "off"
            }
            self.mqtt.publish("sequentmicrosystems/test_switch", json.dumps(test_switch_msg))
            
        except Exception as e:
            logger.error(f"Error publishing v1 parallel messages: {e}")
    
    # ===== V1 COMPATIBILITY METHOD - END =====
    
    def _handle_mqtt_command(self, command_type: str, data: Dict[str, Any]):
        """Handle MQTT commands from Home Assistant"""
        try:
            if command_type == 'switch_command':
                switch_name = data['switch']
                relay_num = data['relay']
                state = data['state']
                
                # Set relay state
                self.hardware.set_relay_state(relay_num, state)
                
                # Update system state
                if switch_name == 'primary_pump':
                    self.system_state['primary_pump'] = state
                elif switch_name == 'secondary_pump':
                    self.system_state['secondary_pump'] = state
                elif switch_name == 'cartridge_heater':
                    self.system_state['cartridge_heater'] = state
                
                # Publish switch state back to Home Assistant
                self._publish_switch_state(switch_name, state)
                
                logger.info(f"Switch {switch_name} set to {'ON' if state else 'OFF'}")
                
            elif command_type == 'number_command':
                number_name = data['number']
                value = data['value']
                
                # Update control parameters
                if number_name == 'set_temp_tank_1':
                    self.control_params['set_temp_tank_1'] = value
                elif number_name == 'dTStart_tank_1':
                    self.control_params['dTStart_tank_1'] = value
                elif number_name == 'dTStop_tank_1':
                    self.control_params['dTStop_tank_1'] = value
                elif number_name == 'kylning_kollektor':
                    self.control_params['kylning_kollektor'] = value
                elif number_name == 'temp_kok':
                    self.control_params['temp_kok'] = value
                
                # Publish number state back to Home Assistant
                self._publish_number_state(number_name, value)
                
                logger.info(f"Number {number_name} set to {value}")
                
            elif command_type == 'v1_test_switch_command':
                state = data['state']
                
                # Update test mode state
                self.system_state['test_mode'] = state
                
                # Update system mode
                self._update_system_mode()
                
                logger.info(f"v1 test switch set to {'ON' if state else 'OFF'}")
                
        except Exception as e:
            logger.error(f"Error handling MQTT command: {e}")
    
    def _publish_switch_state(self, switch_name: str, state: bool):
        """Publish switch state to Home Assistant"""
        try:
            if not self.mqtt or not self.mqtt.is_connected():
                return
            
            topic = f"homeassistant/switch/solar_heating_{switch_name}/state"
            state_str = "ON" if state else "OFF"
            self.mqtt.publish_raw(topic, state_str)
            logger.debug(f"Published switch state: {switch_name} = {state_str}")
            
        except Exception as e:
            logger.error(f"Error publishing switch state: {e}")
    
    def _publish_number_state(self, number_name: str, value: float):
        """Publish number state to Home Assistant"""
        try:
            if not self.mqtt or not self.mqtt.is_connected():
                return
            
            topic = f"homeassistant/number/solar_heating_{number_name}/state"
            self.mqtt.publish_raw(topic, str(value))
            logger.debug(f"Published number state: {number_name} = {value}")
            
        except Exception as e:
            logger.error(f"Error publishing number state: {e}")
    
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
