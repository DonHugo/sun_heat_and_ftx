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
import os
from datetime import datetime, time as dt_time
from typing import Dict, Any

# Import system-wide packages
try:
    from config import config, pump_config
    from hardware_interface import HardwareInterface
    from mqtt_handler import MQTTHandler
    from taskmaster_service import taskmaster_service
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
            'primary_pump_manual': False,
            'cartridge_heater': False,
            'test_mode': config.test_mode,
            'manual_control': False,
            'overheated': False,
            'last_update': time.time(),
            'pump_runtime_hours': 0.0,
            'heating_cycles_count': 0,
            'last_pump_start': None,
            'total_heating_time': 0.0,  # Daily heating time (resets at midnight)
            'total_heating_time_lifetime': 0.0,  # Lifetime cumulative heating time (never resets)
            # Energy collection tracking
            'energy_collected_today': 0.0,  # kWh collected today
            'energy_collected_hour': 0.0,   # kWh collected this hour
            'last_energy_calculation': time.time(),
            'last_hour_reset': time.time(),
            'last_day_reset': time.time(),
            # Heat source tracking
            'solar_energy_today': 0.0,      # kWh from solar today
            'cartridge_energy_today': 0.0,  # kWh from cartridge heater today
            'pellet_energy_today': 0.0,     # kWh from pellet furnace today
            'solar_energy_hour': 0.0,       # kWh from solar this hour
            'cartridge_energy_hour': 0.0,   # kWh from cartridge heater this hour
            'pellet_energy_hour': 0.0,      # kWh from pellet furnace this hour
            # Pellet stove data
            'pellet_stove_power': 0.0,      # Current power output (kW)
            'pellet_stove_burn_time': 0.0,  # Hours of operation
            'pellet_stove_daily_consumption': 0.0,  # Daily consumption percentage
            'pellet_stove_storage_level': 0,  # Storage level
            'pellet_stove_storage_percentage': 0.0,  # Storage percentage
            'pellet_stove_storage_energy': 0.0,  # Storage energy (kWh)
            'pellet_stove_storage_weight': 0.0,  # Storage weight (kg)
            'pellet_stove_electric_consumption': 0.0,  # Electrical consumption (W)
            'pellet_stove_hall_sensor': False,  # Hall sensor detecting pellet screw rotation
            'pellet_stove_pulse_counter_60s': 0.0,  # Pulse counter for hall sensor (60s window)
            'pellet_stove_energy_today': 0.0,  # Energy today (kWh)
            'pellet_stove_energy_hour': 0.0,  # Energy this hour (kWh)
            'pellet_stove_bags_until_cleaning': 0,  # Bags left until cleaning
            'pellet_stove_status': False,  # ON/OFF status
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
        
        # Load persistent operational metrics
        self._load_system_state()
    
    def _save_system_state(self):
        """Save operational metrics to persistent storage"""
        try:
            state_file = 'system_operational_state.json'
            operational_metrics = {
                'pump_runtime_hours': self.system_state.get('pump_runtime_hours', 0.0),
                'heating_cycles_count': self.system_state.get('heating_cycles_count', 0),
                'total_heating_time': self.system_state.get('total_heating_time', 0.0),
                'total_heating_time_lifetime': self.system_state.get('total_heating_time_lifetime', 0.0),
                'last_save_time': time.time(),
                'last_save_date': datetime.now().isoformat()
            }
            
            with open(state_file, 'w') as f:
                json.dump(operational_metrics, f, indent=2)
            
            logger.info(f"✅ Operational state saved: pump_runtime={operational_metrics['pump_runtime_hours']:.2f}h, cycles={operational_metrics['heating_cycles_count']}, daily_time={operational_metrics['total_heating_time']:.2f}h, lifetime={operational_metrics['total_heating_time_lifetime']:.2f}h")
            
        except Exception as e:
            logger.error(f"❌ Failed to save operational state: {e}")
    
    def _load_system_state(self):
        """Load operational metrics from persistent storage"""
        try:
            state_file = 'system_operational_state.json'
            if os.path.exists(state_file):
                with open(state_file, 'r') as f:
                    saved_state = json.load(f)
                
                # Restore operational metrics
                self.system_state['pump_runtime_hours'] = saved_state.get('pump_runtime_hours', 0.0)
                self.system_state['heating_cycles_count'] = saved_state.get('heating_cycles_count', 0)
                self.system_state['total_heating_time'] = saved_state.get('total_heating_time', 0.0)
                self.system_state['total_heating_time_lifetime'] = saved_state.get('total_heating_time_lifetime', 0.0)
                
                last_save_date = saved_state.get('last_save_date', 'Unknown')
                logger.info(f"✅ Operational state loaded: pump_runtime={self.system_state['pump_runtime_hours']:.2f}h, cycles={self.system_state['heating_cycles_count']}, daily_time={self.system_state['total_heating_time']:.2f}h, lifetime={self.system_state['total_heating_time_lifetime']:.2f}h (last saved: {last_save_date})")
            else:
                logger.info("ℹ️  No saved operational state found - starting with fresh counters")
                
        except Exception as e:
            logger.error(f"❌ Failed to load operational state: {e}")
            logger.info("ℹ️  Continuing with default values")
    
    def _is_midnight_reset_needed(self):
        """Check if we need to reset daily counters at midnight"""
        now = datetime.now()
        current_time = now.time()
        
        # Check if we're within a few seconds of midnight (00:00:00)
        midnight = dt_time(0, 0, 0)
        time_diff = abs((current_time.hour * 3600 + current_time.minute * 60 + current_time.second) - 
                       (midnight.hour * 3600 + midnight.minute * 60 + midnight.second))
        
        # Allow reset within 5 seconds of midnight
        if time_diff <= 5:
            # Check if we haven't already reset today
            last_reset_date = self.system_state.get('last_midnight_reset_date', '')
            today = now.date().isoformat()
            
            if last_reset_date != today:
                return True
        
        return False
    
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
                'mode': 'startup',
                'primary_pump': False,
                'primary_pump_manual': False,
                'cartridge_heater': False,
                'test_mode': config.test_mode,
                'manual_control': False,
                'overheated': False,
                'last_update': time.time(),
                'pump_runtime_hours': 0.0,
                'heating_cycles_count': 0,
                'last_pump_start': None,
                'total_heating_time': 0.0,  # Daily heating time (resets at midnight)
                'total_heating_time_lifetime': 0.0,  # Lifetime cumulative heating time (never resets)
                # Energy collection tracking
                'energy_collected_today': 0.0,  # kWh collected today
                'energy_collected_hour': 0.0,   # kWh collected this hour
                'last_energy_calculation': time.time(),
                'last_hour_reset': time.time(),
                'last_day_reset': time.time(),
                # Heat source tracking
                'solar_energy_today': 0.0,      # kWh from solar today
                'cartridge_energy_today': 0.0,  # kWh from cartridge heater today
                'pellet_energy_today': 0.0,     # kWh from pellet furnace today
                'solar_energy_hour': 0.0,       # kWh from solar this hour
                'cartridge_energy_hour': 0.0,   # kWh from cartridge heater this hour
                'pellet_energy_hour': 0.0,      # kWh from pellet furnace this hour
                # Pellet stove data
                'pellet_stove_power': 0.0,      # Current power output (kW)
                'pellet_stove_burn_time': 0.0,  # Hours of operation
                'pellet_stove_daily_consumption': 0.0,  # Daily consumption percentage
                'pellet_stove_storage_level': 0,  # Storage level
                'pellet_stove_storage_percentage': 0.0,  # Storage percentage
                'pellet_stove_storage_energy': 0.0,  # Storage energy (kWh)
                'pellet_stove_storage_weight': 0.0,  # Storage weight (kg)
                'pellet_stove_electric_consumption': 0.0,  # Electrical consumption (W)
                'pellet_stove_hall_sensor': False,  # Hall sensor detecting pellet screw rotation
                'pellet_stove_pulse_counter_60s': 0.0,  # Pulse counter for hall sensor (60s window)
                'pellet_stove_energy_today': 0.0,  # Energy today (kWh)
                'pellet_stove_energy_hour': 0.0,  # Energy this hour (kWh)
                'pellet_stove_bags_until_cleaning': 0,  # Bags left until cleaning
                'pellet_stove_status': False,  # ON/OFF status
                # Midnight reset tracking
                'last_midnight_reset_date': datetime.now().date().isoformat(),
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
            
            # Initialize TaskMaster AI service (FR-008)
            if config.taskmaster_enabled:
                try:
                    await taskmaster_service.initialize()
                    logger.info("TaskMaster AI service initialized successfully")
                except Exception as e:
                    logger.error(f"Failed to initialize TaskMaster AI service: {str(e)}")
            else:
                logger.info("TaskMaster AI service disabled in configuration")
            
            logger.info("Solar Heating System v3 (System-Wide) started successfully")
            logger.info("Starting background tasks...")
            
            # Start background tasks
            self.running = True
            await self._start_background_tasks()
            
            # Main control loop (simplified since background tasks handle the rest)
            state_save_counter = 0
            while self.running:
                await self._process_control_logic()
                
                # Save operational state periodically (every 5 minutes)
                state_save_counter += 1
                if state_save_counter >= 60:  # Assuming temperature_update_interval is 5 seconds
                    self._save_system_state()
                    state_save_counter = 0
                
                await asyncio.sleep(config.temperature_update_interval)
                
        except Exception as e:
            logger.error(f"Error starting system: {e}")
            raise
    
    async def _publish_hass_discovery(self):
        """Publish Home Assistant discovery configuration for all sensors"""
        try:
            logger.info("=== HOME ASSISTANT DISCOVERY STARTED ===")
            logger.info("Starting Home Assistant discovery configuration...")
            
            # Check MQTT connection
            if not self.mqtt:
                logger.error("MQTT handler is None - cannot publish discovery")
                return
            if not self.mqtt.is_connected():
                logger.error("MQTT not connected - cannot publish discovery")
                return
            logger.info("MQTT connection verified - proceeding with discovery")
            
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
                {
                    'name': 'System Heating Status',
                    'entity_id': 'is_heating',
                    'device_class': 'heat',
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
                    'name': 'Pump Runtime Hours (Real-time)',
                    'entity_id': 'pump_runtime_hours_realtime',
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
                {
                    'name': 'Energy Collection Rate',
                    'entity_id': 'energy_collection_rate_kwh_per_hour',
                    'device_class': None,
                    'unit_of_measurement': 'kWh/hour'
                },
                {
                    'name': 'Energy Collected Today',
                    'entity_id': 'energy_collected_today_kwh',
                    'device_class': None,
                    'unit_of_measurement': 'kWh'
                },
                {
                    'name': 'Energy Collected This Hour',
                    'entity_id': 'energy_collected_hour_kwh',
                    'device_class': None,
                    'unit_of_measurement': 'kWh'
                },
                # Heat source specific energy sensors
                {
                    'name': 'Solar Energy Today',
                    'entity_id': 'solar_energy_today_kwh',
                    'device_class': None,
                    'unit_of_measurement': 'kWh'
                },
                {
                    'name': 'Cartridge Heater Energy Today',
                    'entity_id': 'cartridge_energy_today_kwh',
                    'device_class': None,
                    'unit_of_measurement': 'kWh'
                },
                {
                    'name': 'Pellet Furnace Energy Today',
                    'entity_id': 'pellet_energy_today_kwh',
                    'device_class': None,
                    'unit_of_measurement': 'kWh'
                },
                {
                    'name': 'Solar Energy This Hour',
                    'entity_id': 'solar_energy_hour_kwh',
                    'device_class': None,
                    'unit_of_measurement': 'kWh'
                },
                {
                    'name': 'Cartridge Heater Energy This Hour',
                    'entity_id': 'cartridge_energy_hour_kwh',
                    'device_class': None,
                    'unit_of_measurement': 'kWh'
                },
                {
                    'name': 'Pellet Furnace Energy This Hour',
                    'entity_id': 'pellet_energy_hour_kwh',
                    'device_class': None,
                    'unit_of_measurement': 'kWh'
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
            
            # Separate binary sensors from regular sensors
            binary_sensors = []
            regular_sensors = []
            
            for sensor in sensors:
                if sensor['entity_id'] == 'is_heating':
                    binary_sensors.append(sensor)
                else:
                    regular_sensors.append(sensor)
            

            
            logger.info(f"Total sensors configured: {len(sensors)} (regular: {len(regular_sensors)}, binary: {len(binary_sensors)})")
            logger.info(f"Publishing discovery for {len(regular_sensors)} regular sensors...")
            
            # Publish discovery configuration for each regular sensor
            discovery_count = 0
            logger.info("Starting regular sensor discovery loop...")
            for sensor in regular_sensors:
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
                logger.info(f"Attempting to publish discovery for {sensor['name']} to {topic}")
                success = self.mqtt.publish(topic, config, retain=True)
                logger.info(f"MQTT publish result for {sensor['name']}: {success}")
                if success:
                    logger.info(f"Published HA discovery for {sensor['name']} to {topic}")
                    discovery_count += 1
                else:
                    logger.error(f"Failed to publish HA discovery for {sensor['name']} to {topic}")
            
            logger.info(f"Published discovery for {discovery_count} regular sensors successfully")
            
            # Publish binary sensor discovery configurations
            logger.info(f"Publishing discovery for {len(binary_sensors)} binary sensors...")
            binary_discovery_count = 0
            for sensor in binary_sensors:
                config = {
                    "name": sensor['name'],
                    "unique_id": f"solar_heating_v3_{sensor['entity_id']}",
                    "device_class": sensor['device_class'],
                    "state_topic": f"homeassistant/binary_sensor/solar_heating_{sensor['entity_id']}/state",
                    "device": {
                        "name": "Solar Heating System v3",
                        "identifiers": ["solar_heating_v3"],
                        "manufacturer": "Custom",
                        "model": "Solar Heating System v3"
                    }
                }
                
                topic = f"homeassistant/binary_sensor/solar_heating_{sensor['entity_id']}/config"
                logger.info(f"Attempting to publish binary sensor discovery for {sensor['name']} to {topic}")
                success = self.mqtt.publish(topic, config, retain=True)
                logger.info(f"MQTT publish result for binary sensor {sensor['name']}: {success}")
                if success:
                    logger.info(f"Published HA discovery for binary sensor {sensor['name']} to {topic}")
                    binary_discovery_count += 1
                else:
                    logger.error(f"Failed to publish HA discovery for binary sensor {sensor['name']} to {topic}")
            
            logger.info(f"Published discovery for {binary_discovery_count} binary sensors successfully")
            
            # Publish switch discovery configurations
            switches = [
                {
                    'name': 'Primary Pump',
                    'entity_id': 'primary_pump',
                    'icon': 'mdi:pump'
                },
                {
                    'name': 'Primary Pump Manual Control',
                    'entity_id': 'primary_pump_manual',
                    'icon': 'mdi:pump-off'
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
            import traceback
            logger.error(f"Discovery error traceback: {traceback.format_exc()}")
        finally:
            logger.info("=== HOME ASSISTANT DISCOVERY COMPLETED ===")
    
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
        logger.debug("Starting _read_temperatures method")
        try:
            # Read ALL RTD sensors (0-7, 8 total sensors)
            for sensor_id in range(8):
                sensor_name = f'rtd_sensor_{sensor_id}'
                temp = self.hardware.read_rtd_temperature(sensor_id)
                self.temperatures[sensor_name] = temp
                logger.debug(f"{sensor_name}: {temp}°C")
            
            logger.info(f"RTD sensors read: {[self.temperatures.get(f'rtd_sensor_{i}', 'None') for i in range(8)]}")
            
            # Read ALL MegaBAS sensors (1-8, 8 total sensors)
            for sensor_id in range(1, 9):
                sensor_name = f'megabas_sensor_{sensor_id}'
                temp = self.hardware.read_megabas_temperature(sensor_id)
                self.temperatures[sensor_name] = temp
                logger.debug(f"{sensor_name}: {temp}°C")
            
            logger.info(f"MegaBAS sensors read: {[self.temperatures.get(f'megabas_sensor_{i}', 'None') for i in range(1, 9)]}")
            logger.debug("Starting sensor mapping and calculations...")
            logger.info("About to start MegaBAS sensor mapping...")
            
            # MegaBAS sensors with improved naming (based on v1 mapping)
            # FTX sensors (MegaBAS inputs 1-4) - CORRECTED to match v1
            self.temperatures['outdoor_air_temp'] = self.temperatures.get('megabas_sensor_1', 0)      # Outdoor air intake
            self.temperatures['exhaust_air_temp'] = self.temperatures.get('megabas_sensor_2', 0)     # Air leaving heat exchanger
            self.temperatures['supply_air_temp'] = self.temperatures.get('megabas_sensor_3', 0)      # Air entering heat exchanger
            self.temperatures['return_air_temp'] = self.temperatures.get('megabas_sensor_4', 0)     # Air returning from heat exchanger
            logger.info("FTX sensors mapped successfully")
            
            # Solar collector and storage tank sensors (MegaBAS inputs 6-8) - CORRECTED to match v1
            self.temperatures['solar_collector_temp'] = self.temperatures.get('megabas_sensor_6', 0)  # T1 - Solar panel outlet
            self.temperatures['storage_tank_temp'] = self.temperatures.get('megabas_sensor_7', 0)     # T2 - Main storage tank
            self.temperatures['return_line_temp'] = self.temperatures.get('megabas_sensor_8', 0)      # T3 - Return line to solar collector
            logger.info("Solar collector sensors mapped successfully")
            
            logger.debug("Starting water heater sensor mapping...")
            logger.info("About to map water heater sensors...")
            # All water heater RTD sensors with height-based naming
            self.temperatures['water_heater_bottom'] = self.temperatures.get('rtd_sensor_0', 0)    # RTD sensor 0 - 0cm from bottom (coldest)
            self.temperatures['water_heater_20cm'] = self.temperatures.get('rtd_sensor_1', 0)     # RTD sensor 1 - 20cm from bottom
            self.temperatures['water_heater_40cm'] = self.temperatures.get('rtd_sensor_2', 0)     # RTD sensor 2 - 40cm from bottom
            self.temperatures['water_heater_60cm'] = self.temperatures.get('rtd_sensor_3', 0)     # RTD sensor 3 - 60cm from bottom
            self.temperatures['water_heater_80cm'] = self.temperatures.get('rtd_sensor_4', 0)     # RTD sensor 4 - 80cm from bottom
            self.temperatures['water_heater_100cm'] = self.temperatures.get('rtd_sensor_5', 0)    # RTD sensor 5 - 100cm from bottom
            self.temperatures['water_heater_120cm'] = self.temperatures.get('rtd_sensor_6', 0)    # RTD sensor 6 - 120cm from bottom
            self.temperatures['water_heater_140cm'] = self.temperatures.get('rtd_sensor_7', 0)    # RTD sensor 7 - 140cm from bottom (hottest)
            logger.info("Water heater RTD sensors mapped successfully")
            
            # Debug logging for water heater sensors
            logger.debug(f"Water heater sensors: bottom={self.temperatures['water_heater_bottom']}, 20cm={self.temperatures['water_heater_20cm']}, 40cm={self.temperatures['water_heater_40cm']}, 60cm={self.temperatures['water_heater_60cm']}, 80cm={self.temperatures['water_heater_80cm']}, 100cm={self.temperatures['water_heater_100cm']}, 120cm={self.temperatures['water_heater_120cm']}, 140cm={self.temperatures['water_heater_140cm']}")
            logger.info("Water heater debug logging completed")
            
            # Legacy aliases for backward compatibility
            self.temperatures['water_heater_top'] = self.temperatures['water_heater_100cm']  # Keep top alias
            logger.info("Legacy aliases mapped successfully")
            
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
            logger.info("Backward compatibility aliases mapped successfully")
            
            # Heat exchanger sensors (using MegaBAS sensors 1-2)
            self.temperatures['heat_exchanger_in'] = self.temperatures.get('megabas_sensor_1', 0)
            self.temperatures['heat_exchanger_out'] = self.temperatures.get('megabas_sensor_2', 0)
            logger.info("Heat exchanger sensors mapped successfully")
            
            # Calculate heat exchanger efficiency
            avluft = self.temperatures.get('avluft', 0)
            franluft = self.temperatures.get('franluft', 0)
            if franluft > 0:  # Avoid division by zero
                effekt_varmevaxlare = round(100 - (avluft/franluft*100), 1)
                self.temperatures['heat_exchanger_efficiency'] = effekt_varmevaxlare
                logger.debug(f"heat_exchanger_efficiency: {effekt_varmevaxlare}%")
            logger.info("Heat exchanger efficiency calculated successfully")
            
            # Calculate water heater stratification metrics
            water_heater_140cm = self.temperatures.get('water_heater_140cm', 0)  # Top sensor
            water_heater_bottom = self.temperatures.get('water_heater_bottom', 0)  # Bottom sensor (0cm)
            if water_heater_140cm and water_heater_bottom:
                stratification_quality = round((water_heater_140cm - water_heater_bottom) / 140, 2)  # 140cm height
                gradient_per_cm = round((water_heater_140cm - water_heater_bottom) / 140, 3)
                self.temperatures['water_heater_stratification'] = stratification_quality
                self.temperatures['water_heater_gradient_cm'] = gradient_per_cm
                logger.debug(f"Stratification quality: {stratification_quality}, Gradient: {gradient_per_cm}°C/cm")
            logger.info("Water heater stratification calculated successfully")
            
            # Calculate sensor health score
            valid_sensors = 0
            total_sensors = 0
            
            # Process temperature data with TaskMaster AI (FR-008)
            if config.taskmaster_enabled:
                try:
                    # Create a clean temperature data dictionary for TaskMaster
                    taskmaster_temp_data = {
                        'solar_collector': self.temperatures.get('solar_collector_temp', 0),
                        'storage_tank': self.temperatures.get('storage_tank_temp', 0),
                        'return_line': self.temperatures.get('return_line_temp', 0),
                        'water_heater_bottom': self.temperatures.get('water_heater_bottom', 0),
                        'water_heater_top': self.temperatures.get('water_heater_top', 0),
                        'outdoor_air': self.temperatures.get('outdoor_air_temp', 0),
                        'heat_exchanger_in': self.temperatures.get('heat_exchanger_in', 0),
                        'heat_exchanger_out': self.temperatures.get('heat_exchanger_out', 0)
                    }
                    
                    await taskmaster_service.process_temperature_data(taskmaster_temp_data)
                    logger.debug("Temperature data processed by TaskMaster AI service")
                except Exception as e:
                    logger.error(f"Error processing temperature data with TaskMaster AI: {str(e)}")
            for sensor_name, temp in self.temperatures.items():
                if 'rtd_sensor_' in sensor_name or 'megabas_sensor_' in sensor_name:
                    total_sensors += 1
                    if temp is not None and temp > 0:
                        valid_sensors += 1
            
            if total_sensors > 0:
                sensor_health_score = round((valid_sensors / total_sensors) * 100, 1)
                self.temperatures['sensor_health_score'] = sensor_health_score
                logger.debug(f"Sensor health score: {sensor_health_score}%")
            logger.info("Sensor health score calculated successfully")
            
            # Calculate overheating risk
            solar_collector_temp = self.temperatures.get('solar_collector_temp', 0)
            max_safe_temp = 90  # Configurable maximum safe temperature
            if solar_collector_temp > max_safe_temp:
                overheating_risk = round(((solar_collector_temp - max_safe_temp) / max_safe_temp) * 100, 1)
                self.temperatures['overheating_risk'] = overheating_risk
                logger.warning(f"Overheating risk: {overheating_risk}% (collector: {solar_collector_temp}°C)")
            else:
                self.temperatures['overheating_risk'] = 0
            logger.info("Overheating risk calculated successfully")
            
            # Add system mode to temperatures for Home Assistant
            self.temperatures['system_mode'] = self.system_state.get('mode', 'unknown')
            logger.debug(f"system_mode: {self.temperatures['system_mode']}")
            logger.info("System mode added successfully")
            
            # Calculate heating status boolean
            is_heating = self.system_state.get('primary_pump', False) and self.system_state.get('mode') == 'heating'
            self.temperatures['is_heating'] = is_heating
            logger.debug(f"is_heating: {is_heating}")
            logger.info("Heating status calculated successfully")
            
            # Add operational metrics to temperatures
            self.temperatures['pump_runtime_hours'] = self.system_state.get('pump_runtime_hours', 0.0)
            self.temperatures['heating_cycles_count'] = self.system_state.get('heating_cycles_count', 0)
            self.temperatures['total_heating_time_lifetime'] = self.system_state.get('total_heating_time_lifetime', 0.0)
            
            # Calculate real-time pump runtime (including current cycle if pump is running)
            real_time_runtime = self.system_state.get('pump_runtime_hours', 0.0)
            if self.system_state.get('primary_pump', False) and self.system_state.get('last_pump_start'):
                current_cycle_runtime = (time.time() - self.system_state['last_pump_start']) / 3600  # Convert to hours
                real_time_runtime += current_cycle_runtime
            
            self.temperatures['pump_runtime_hours_realtime'] = round(real_time_runtime, 2)
            
            # Calculate average heating duration
            if self.system_state.get('heating_cycles_count', 0) > 0:
                avg_heating_duration = round(self.system_state.get('total_heating_time', 0) / self.system_state.get('heating_cycles_count', 1), 2)
                self.temperatures['average_heating_duration'] = avg_heating_duration
            else:
                self.temperatures['average_heating_duration'] = 0.0
            
            # Debug logging for operational metrics
            logger.debug(f"Operational metrics: pump_runtime={self.temperatures['pump_runtime_hours']}h, cycles={self.temperatures['heating_cycles_count']}, avg_duration={self.temperatures['average_heating_duration']}h, lifetime={self.temperatures['total_heating_time_lifetime']}h")
            logger.info(f"System state operational metrics: pump_runtime={self.system_state.get('pump_runtime_hours', 0)}h, cycles={self.system_state.get('heating_cycles_count', 0)}, daily_time={self.system_state.get('total_heating_time', 0)}h, lifetime={self.system_state.get('total_heating_time_lifetime', 0)}h, last_start={self.system_state.get('last_pump_start', 'None')}")
            logger.info("Operational metrics added successfully")
            
            # Calculate solar collector dT values
            solar_collector = self.temperatures.get('solar_collector', 0)
            storage_tank = self.temperatures.get('storage_tank', 0)
            dT = solar_collector - storage_tank if solar_collector and storage_tank else 0
            logger.info("Solar collector dT calculation started")
            
            self.temperatures['solar_collector_dt_running'] = dT
            self.temperatures['solar_collector_dt'] = dT
            self.temperatures['solar_collector_pump'] = "ON" if self.system_state.get('primary_pump', False) else "OFF"
            self.temperatures['solar_collector_mode'] = self.system_state.get('mode', 'unknown')
            self.temperatures['solar_collector_state'] = self.system_state.get('mode', 'unknown')
            self.temperatures['solar_collector_sub_state'] = "0"
            self.temperatures['solar_collector_overheated'] = "true" if self.system_state.get('overheated', False) else "false"
            logger.info("Solar collector dT values calculated successfully")
            
            # Calculate stored energy values (matching v1 logic)
            zero_value = 4  # Temperature of water coming from well
            stored_energy = [0] * 10
            logger.info("Stored energy calculation started")
            
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
            logger.info("Stored energy values assigned successfully")
            
            # Debug logging for stored energy values
            logger.info(f"Stored Energy - Total: {stored_energy_kwh[0]} kWh, Top: {stored_energy_kwh[2]} kWh, Bottom: {stored_energy_kwh[1]} kWh, Avg Temp: {stored_energy_kwh[3]}°C")
            logger.debug(f"RTD sensor values: {[self.temperatures.get(f'rtd_sensor_{i}', 0) for i in range(8)]}")
            logger.debug(f"MegaBAS sensor 5: {self.temperatures.get('megabas_sensor_5', 0)}")
            logger.info("Stored energy debug logging completed")
            
            # Calculate energy collection rate and daily/hourly totals
            current_time = time.time()
            current_stored_energy = stored_energy_kwh[0]  # Total stored energy
            
            # Check if we need to reset hourly/daily counters
            if current_time - self.system_state.get('last_hour_reset', 0) >= 3600:  # 1 hour
                self.system_state['energy_collected_hour'] = 0.0
                self.system_state['solar_energy_hour'] = 0.0
                self.system_state['cartridge_energy_hour'] = 0.0
                self.system_state['pellet_energy_hour'] = 0.0
                self.system_state['last_hour_reset'] = current_time
                logger.info("Hourly energy collection counter reset")
            
            # Check for midnight reset of daily counters and operational metrics
            if self._is_midnight_reset_needed():
                # Reset daily energy counters
                self.system_state['energy_collected_today'] = 0.0
                self.system_state['solar_energy_today'] = 0.0
                self.system_state['cartridge_energy_today'] = 0.0
                self.system_state['pellet_energy_today'] = 0.0
                
                # Reset daily operational metrics
                self.system_state['pump_runtime_hours'] = 0.0
                self.system_state['heating_cycles_count'] = 0
                self.system_state['total_heating_time'] = 0.0
                # Note: total_heating_time_lifetime is NOT reset - it accumulates lifetime total
                
                # Update reset tracking
                self.system_state['last_midnight_reset_date'] = datetime.now().date().isoformat()
                self.system_state['last_day_reset'] = current_time
                
                logger.info("🕛 MIDNIGHT RESET: Daily counters and operational metrics reset")
                logger.info(f"  📊 Energy: {self.system_state['energy_collected_today']:.2f} kWh, Solar: {self.system_state['solar_energy_today']:.2f} kWh, Cartridge: {self.system_state['cartridge_energy_today']:.2f} kWh, Pellet: {self.system_state['pellet_energy_today']:.2f} kWh")
                logger.info(f"  ⚙️  Pump Runtime: {self.system_state['pump_runtime_hours']:.2f}h, Heating Cycles: {self.system_state['heating_cycles_count']}, Daily Time: {self.system_state['total_heating_time']:.2f}h, Lifetime: {self.system_state['total_heating_time_lifetime']:.2f}h")
                
                # Save the reset state immediately
                self._save_system_state()
            
            # Calculate energy collected since last calculation
            last_energy = self.system_state.get('last_energy_calculation', current_time)
            if self.system_state.get('last_energy_calculation'):
                time_diff = current_time - last_energy
                if time_diff > 0:
                    # Calculate energy collection rate (kWh/hour)
                    energy_diff = current_stored_energy - self.system_state.get('last_stored_energy', current_stored_energy)
                    if energy_diff > 0:  # Only count positive energy gains
                        energy_rate_per_hour = (energy_diff / time_diff) * 3600  # Convert to per hour
                        
                        # Determine which heat source is active and allocate energy
                        active_heat_sources = []
                        source_contributions = {}
                        
                        # Check solar heating (pump running and collector hotter than tank)
                        solar_active = (self.system_state.get('primary_pump', False) and 
                                      self.temperatures.get('solar_collector_temp', 0) > self.temperatures.get('storage_tank_temp', 0) + 5)
                        if solar_active:
                            active_heat_sources.append('solar')
                            # Estimate solar contribution based on temperature difference and flow
                            solar_dt = self.temperatures.get('solar_collector_temp', 0) - self.temperatures.get('storage_tank_temp', 0)
                            # Rough estimate: higher dT = higher contribution
                            source_contributions['solar'] = min(1.0, max(0.1, solar_dt / 20.0))  # 0.1 to 1.0 based on dT
                            logger.info(f"Solar heating detected: dT={solar_dt:.1f}°C, contribution={source_contributions['solar']:.2f}")
                        
                        # Check cartridge heater (relay state)
                        cartridge_active = self.system_state.get('cartridge_heater', False)
                        if cartridge_active:
                            active_heat_sources.append('cartridge')
                            # Cartridge heater typically provides consistent heating
                            source_contributions['cartridge'] = 0.8  # Assume 80% of energy when active
                            logger.info(f"Cartridge heater detected: ON, contribution={source_contributions['cartridge']:.2f}")
                        
                        # Check pellet furnace (we'll need to add a sensor for this)
                        # For now, assume pellet furnace if no other source is active but energy is increasing
                        pellet_active = (not active_heat_sources and energy_diff > 0)
                        if pellet_active:
                            active_heat_sources.append('pellet')
                            source_contributions['pellet'] = 1.0  # Assume 100% when no other source
                            logger.info(f"Pellet furnace detected: assumed active, contribution={source_contributions['pellet']:.2f}")
                        
                        # Log heat source detection
                        if active_heat_sources:
                            logger.info(f"Active heat sources: {active_heat_sources}")
                        else:
                            logger.info("No active heat sources detected")
                        
                        # If multiple sources active, use weighted allocation
                        if len(active_heat_sources) > 1:
                            total_weight = sum(source_contributions.get(source, 0.5) for source in active_heat_sources)
                            for source in active_heat_sources:
                                weight = source_contributions.get(source, 0.5)
                                source_contributions[source] = weight / total_weight
                        elif len(active_heat_sources) == 1:
                            source_contributions[active_heat_sources[0]] = 1.0
                        
                        # Allocate energy to active heat sources using weighted contributions
                        if active_heat_sources:
                            hourly_contribution_total = energy_diff / (time_diff / 3600)
                            
                            for source in active_heat_sources:
                                source_weight = source_contributions.get(source, 0.5)
                                source_contribution = hourly_contribution_total * source_weight
                                
                                if source == 'solar':
                                    self.system_state['solar_energy_hour'] += source_contribution
                                    self.system_state['solar_energy_today'] += source_contribution
                                elif source == 'cartridge':
                                    self.system_state['cartridge_energy_hour'] += source_contribution
                                    self.system_state['cartridge_energy_today'] += source_contribution
                                elif source == 'pellet':
                                    self.system_state['pellet_energy_hour'] += source_contribution
                                    self.system_state['pellet_energy_today'] += source_contribution
                            
                            logger.info(f"Energy collected: {energy_diff:.3f} kWh in {time_diff/3600:.2f} hours, Rate: {energy_rate_per_hour:.2f} kWh/hour, Sources: {active_heat_sources}")
                        
                        # Add to total hourly and daily totals
                        hourly_contribution = energy_rate_per_hour * (time_diff / 3600)
                        self.system_state['energy_collected_hour'] += hourly_contribution
                        self.system_state['energy_collected_today'] += hourly_contribution
            
            # Update last calculation values
            self.system_state['last_energy_calculation'] = current_time
            self.system_state['last_stored_energy'] = current_stored_energy
            
            # Add energy collection metrics to temperatures
            self.temperatures['energy_collection_rate_kwh_per_hour'] = round(energy_rate_per_hour if 'energy_rate_per_hour' in locals() else 0.0, 2)
            self.temperatures['energy_collected_today_kwh'] = round(self.system_state.get('energy_collected_today', 0.0), 2)
            self.temperatures['energy_collected_hour_kwh'] = round(self.system_state.get('energy_collected_hour', 0.0), 2)
            
            # Add heat source specific energy metrics
            self.temperatures['solar_energy_today_kwh'] = round(self.system_state.get('solar_energy_today', 0.0), 2)
            self.temperatures['cartridge_energy_today_kwh'] = round(self.system_state.get('cartridge_energy_today', 0.0), 2)
            self.temperatures['pellet_energy_today_kwh'] = round(self.system_state.get('pellet_energy_today', 0.0), 2)
            self.temperatures['solar_energy_hour_kwh'] = round(self.system_state.get('solar_energy_hour', 0.0), 2)
            self.temperatures['cartridge_energy_hour_kwh'] = round(self.system_state.get('cartridge_energy_hour', 0.0), 2)
            self.temperatures['pellet_energy_hour_kwh'] = round(self.system_state.get('pellet_energy_hour', 0.0), 2)
            
            # Calculate real-time energy rate sensor (kW) and comparison metrics
            self._calculate_realtime_energy_sensor()
                
        except Exception as e:
            logger.error(f"Error reading temperatures: {e}")
        finally:
            logger.debug("Completed _read_temperatures method")
    
    def _calculate_realtime_energy_sensor(self):
        """Calculate real-time energy rate sensor with comparison metrics"""
        try:
            current_time = time.time()
            current_stored_energy = self.temperatures.get('stored_energy_kwh', 0)
            current_avg_temp = self.temperatures.get('average_temperature', 0)
            
            # Get historical data for rate calculations
            last_time = self.system_state.get('last_energy_rate_calculation', current_time)
            last_stored_energy = self.system_state.get('last_stored_energy_for_rate', current_stored_energy)
            last_avg_temp = self.system_state.get('last_avg_temp_for_rate', current_avg_temp)
            
            # Calculate time difference (minimum 30 seconds to avoid division by zero)
            time_diff = max(current_time - last_time, 30)
            
            # Calculate energy rate (kW) - energy change per second converted to kW
            energy_diff = current_stored_energy - last_stored_energy
            energy_rate_kw = (energy_diff / time_diff) * 3600  # Convert to kW (kWh/hour)
            
            # Calculate temperature change rate (°C/hour)
            temp_diff = current_avg_temp - last_avg_temp
            temp_rate_per_hour = (temp_diff / time_diff) * 3600  # °C/hour
            
            # Calculate efficiency metrics
            # Efficiency = energy gained / (average temperature * time)
            efficiency_factor = 0
            if current_avg_temp > 0 and time_diff > 0:
                # Normalize efficiency based on temperature and time
                efficiency_factor = energy_rate_kw / max(current_avg_temp, 1)  # kW/°C
            
            # Calculate comparison metrics
            # 1. Energy rate vs average temperature ratio
            energy_temp_ratio = energy_rate_kw / max(current_avg_temp, 1) if current_avg_temp > 0 else 0
            
            # 2. Energy rate vs total stored energy ratio
            energy_total_ratio = energy_rate_kw / max(current_stored_energy, 1) if current_stored_energy > 0 else 0
            
            # 3. Temperature change vs average temperature ratio
            temp_change_ratio = temp_rate_per_hour / max(current_avg_temp, 1) if current_avg_temp > 0 else 0
            
            # 4. Energy efficiency index (0-100 scale)
            # Based on how much energy is gained relative to current temperature
            efficiency_index = min(100, max(0, efficiency_factor * 10))  # Scale to 0-100
            
            # Store calculated values
            self.temperatures['realtime_energy_rate_kw'] = round(energy_rate_kw, 3)
            self.temperatures['realtime_temp_rate_per_hour'] = round(temp_rate_per_hour, 2)
            self.temperatures['energy_efficiency_factor'] = round(efficiency_factor, 4)
            self.temperatures['energy_temp_ratio'] = round(energy_temp_ratio, 4)
            self.temperatures['energy_total_ratio'] = round(energy_total_ratio, 4)
            self.temperatures['temp_change_ratio'] = round(temp_change_ratio, 4)
            self.temperatures['energy_efficiency_index'] = round(efficiency_index, 1)
            
            # Calculate trend indicators
            # Positive trend = energy increasing (heating), negative = decreasing (water usage/cooling)
            if energy_rate_kw > 0.01:
                energy_trend = "heating"
            elif energy_rate_kw < -0.01:
                energy_trend = "water_usage"
            else:
                energy_trend = "stable"
                
            if temp_rate_per_hour > 0.1:
                temp_trend = "heating"
            elif temp_rate_per_hour < -0.1:
                temp_trend = "cooling"
            else:
                temp_trend = "stable"
            
            self.temperatures['energy_trend'] = energy_trend
            self.temperatures['temperature_trend'] = temp_trend
            
            # Calculate water usage metrics
            water_usage_rate_kw = abs(energy_rate_kw) if energy_rate_kw < 0 else 0
            water_usage_intensity = "none"
            if water_usage_rate_kw > 0:
                if water_usage_rate_kw < 0.5:
                    water_usage_intensity = "light"
                elif water_usage_rate_kw < 1.5:
                    water_usage_intensity = "moderate"
                elif water_usage_rate_kw < 3.0:
                    water_usage_intensity = "heavy"
                else:
                    water_usage_intensity = "very_heavy"
            
            self.temperatures['water_usage_rate_kw'] = round(water_usage_rate_kw, 3)
            self.temperatures['water_usage_intensity'] = water_usage_intensity
            
            # Calculate performance score (0-100)
            # Based on energy rate, efficiency, and temperature stability
            performance_score = 0
            
            if energy_rate_kw > 0:  # Positive energy gain (heating)
                performance_score += 40  # Base score for positive energy
                performance_score += min(30, energy_rate_kw * 10)  # Bonus for higher rate (max 30)
                performance_score += min(20, efficiency_index / 5)  # Bonus for efficiency (max 20)
                performance_score += min(10, 10 - abs(temp_rate_per_hour))  # Bonus for stable temperature (max 10)
            elif energy_rate_kw < 0:  # Negative energy (water usage)
                # Water usage is normal - score based on usage rate and system recovery
                usage_rate = abs(energy_rate_kw)
                if usage_rate < 1.0:  # Light usage
                    performance_score = 70  # Good - normal light usage
                elif usage_rate < 2.5:  # Moderate usage
                    performance_score = 60  # Normal - moderate usage
                else:  # Heavy usage
                    performance_score = 50  # Acceptable - heavy usage
                
                # Bonus for efficient water usage (not too rapid cooling)
                if abs(temp_rate_per_hour) < 2.0:
                    performance_score += 10  # Bonus for controlled usage
            else:  # Stable (no change)
                performance_score = 50  # Neutral - system stable
            
            self.temperatures['system_performance_score'] = round(performance_score, 1)
            
            # Update historical data for next calculation
            self.system_state['last_energy_rate_calculation'] = current_time
            self.system_state['last_stored_energy_for_rate'] = current_stored_energy
            self.system_state['last_avg_temp_for_rate'] = current_avg_temp
            
            logger.info(f"Real-time energy sensor: {energy_rate_kw:.3f} kW, temp rate: {temp_rate_per_hour:.2f}°C/h, efficiency: {efficiency_index:.1f}%, performance: {performance_score:.1f}")
            
        except Exception as e:
            logger.error(f"Error calculating real-time energy sensor: {e}")
            # Set default values on error
            self.temperatures['realtime_energy_rate_kw'] = 0.0
            self.temperatures['realtime_temp_rate_per_hour'] = 0.0
            self.temperatures['energy_efficiency_factor'] = 0.0
            self.temperatures['energy_temp_ratio'] = 0.0
            self.temperatures['energy_total_ratio'] = 0.0
            self.temperatures['temp_change_ratio'] = 0.0
            self.temperatures['energy_efficiency_index'] = 0.0
            self.temperatures['energy_trend'] = "unknown"
            self.temperatures['temperature_trend'] = "unknown"
            self.temperatures['system_performance_score'] = 0.0
    
    async def _process_control_logic(self):
        """Process control logic based on temperatures"""
        try:
            # Get key temperatures
            solar_collector = self.temperatures.get('solar_collector', 0)
            storage_tank = self.temperatures.get('storage_tank', 0)
            
            # Update system mode based on current state
            self._update_system_mode()
            
            # Enhanced control logic with proper temperature difference handling
            dT = solar_collector - storage_tank
            
            # Emergency stop conditions
            if solar_collector >= self.control_params['temp_kok']:
                if self.system_state['primary_pump']:
                    self.hardware.set_relay_state(1, False)  # Primary pump relay
                    self.system_state['primary_pump'] = False
                    self.system_state['overheated'] = True
                    logger.warning(f"Emergency pump stop: Collector temperature {solar_collector}°C >= {self.control_params['temp_kok']}°C")
            
            # Detect unexpected heating at night (cartridge heater running when it shouldn't be)
            if (not self.system_state.get('primary_pump', False) and  # Pump not running
                dT > 10 and  # Significant temperature difference
                self.system_state.get('cartridge_heater', False)):  # Cartridge heater is on
                logger.warning(f"Cartridge heater running at night: dT={dT:.1f}°C, collector={solar_collector}°C, tank={storage_tank}°C")
                logger.info("This explains the unexpected heat source - cartridge heater is active")
            
            # Normal control logic
            elif dT >= self.control_params['dTStart_tank_1']:  # dT >= 8°C
                if not self.system_state['primary_pump']:
                    self.hardware.set_relay_state(1, True)  # Primary pump relay
                    self.system_state['primary_pump'] = True
                    self.system_state['last_pump_start'] = time.time()
                    self.system_state['heating_cycles_count'] += 1
                    logger.info(f"Primary pump started. dT={dT:.1f}°C >= {self.control_params['dTStart_tank_1']}°C. Cycle #{self.system_state['heating_cycles_count']}")
                    
                    # Save operational state after cycle count increment
                    self._save_system_state()
                    
                    # Create TaskMaster AI task for pump control (FR-008)
                    if config.taskmaster_enabled:
                        try:
                            await taskmaster_service.process_pump_control("start", {
                                "reason": "temperature_difference",
                                "dT": dT,
                                "threshold": self.control_params['dTStart_tank_1'],
                                "cycle_number": self.system_state['heating_cycles_count']
                            })
                        except Exception as e:
                            logger.error(f"Error creating TaskMaster AI pump control task: {str(e)}")
            
            elif dT <= self.control_params['dTStop_tank_1']:  # dT <= 4°C
                if self.system_state['primary_pump']:
                    self.hardware.set_relay_state(1, False)  # Primary pump relay
                    self.system_state['primary_pump'] = False
                    # Calculate runtime for this cycle
                    if self.system_state['last_pump_start']:
                        cycle_runtime = (time.time() - self.system_state['last_pump_start']) / 3600  # Convert to hours
                        self.system_state['total_heating_time'] += cycle_runtime
                        self.system_state['total_heating_time_lifetime'] += cycle_runtime  # Add to lifetime total
                        self.system_state['pump_runtime_hours'] = round(self.system_state['total_heating_time'], 2)
                        logger.info(f"Primary pump stopped. dT={dT:.1f}°C <= {self.control_params['dTStop_tank_1']}°C. Cycle runtime: {cycle_runtime:.2f}h, Daily runtime: {self.system_state['pump_runtime_hours']}h, Lifetime: {self.system_state['total_heating_time_lifetime']:.2f}h")
                        
                        # Save operational state after runtime update
                        self._save_system_state()
                        
                        # Create TaskMaster AI task for pump control (FR-008)
                        if config.taskmaster_enabled:
                            try:
                                await taskmaster_service.process_pump_control("stop", {
                                    "reason": "temperature_difference",
                                    "dT": dT,
                                    "threshold": self.control_params['dTStop_tank_1'],
                                    "cycle_runtime": cycle_runtime,
                                    "total_runtime": self.system_state['pump_runtime_hours']
                                })
                            except Exception as e:
                                logger.error(f"Error creating TaskMaster AI pump control task: {str(e)}")
                    else:
                        logger.warning("Primary pump stopped but last_pump_start was None - runtime not calculated")
            
            # Keep current state when 4°C < dT < 8°C (hysteresis zone)
            else:
                logger.debug(f"Pump state unchanged. dT={dT:.1f}°C (hysteresis zone: {self.control_params['dTStop_tank_1']}°C < dT < {self.control_params['dTStart_tank_1']}°C)")
                    
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
            logger.info("Starting MQTT status publishing...")
            # Publish individual sensors for Home Assistant
            sensor_count = 0
            total_sensors = len(self.temperatures)
            logger.info(f"Starting to publish {total_sensors} sensors to Home Assistant")
            for sensor_name, value in self.temperatures.items():
                if self.mqtt and self.mqtt.is_connected():
                    # Publish to Home Assistant compatible topic
                    topic = f"homeassistant/sensor/solar_heating_{sensor_name}/state"
                    
                    # Determine if this is a temperature sensor or other type
                    if sensor_name == 'heat_exchanger_efficiency':
                        # For efficiency, send the raw number
                        message = str(value) if value is not None else "0"
                        logger.debug(f"Published {sensor_name}: {value}% to {topic}")
                        sensor_count += 1
                        logger.info(f"Published efficiency sensor: {sensor_name} = {value}")
                    elif sensor_name == 'system_mode':
                        # For system mode, send the string value
                        message = str(value) if value is not None else "unknown"
                        logger.debug(f"Published {sensor_name}: {value} to {topic}")
                        sensor_count += 1
                        logger.info(f"Published system mode sensor: {sensor_name} = {value}")
                    elif sensor_name == 'is_heating':
                        # For heating status, send the boolean value as string
                        message = str(value).lower() if value is not None else "false"
                        logger.debug(f"Published {sensor_name}: {value} to {topic}")
                        sensor_count += 1
                        logger.info(f"Published heating status sensor: {sensor_name} = {value}")
                        
                        # Also publish to binary_sensor topic with proper ON/OFF format
                        binary_topic = f"homeassistant/binary_sensor/solar_heating_{sensor_name}/state"
                        binary_message = "ON" if value else "OFF"
                        self.mqtt.publish_raw(binary_topic, binary_message)
                        logger.info(f"Published binary sensor {sensor_name} = {binary_message} to {binary_topic}")
                    elif sensor_name in ['stored_energy_kwh', 'stored_energy_top_kwh', 'stored_energy_bottom_kwh']:
                        # For energy sensors, send the raw number
                        message = str(value) if value is not None else "0"
                        logger.info(f"Published {sensor_name}: {value} kWh to {topic}")
                        sensor_count += 1
                        logger.info(f"Published energy sensor: {sensor_name} = {value}")
                    elif sensor_name == 'average_temperature':
                        # For average temperature, send the raw number
                        message = str(value) if value is not None else "0"
                        logger.info(f"Published {sensor_name}: {value}°C to {topic}")
                        sensor_count += 1
                        logger.info(f"Published average temperature sensor: {sensor_name} = {value}")
                    else:
                        # For temperature sensors, send the raw number
                        message = str(value) if value is not None else "0"
                        logger.debug(f"Published {sensor_name}: {value}°C to {topic}")
                        sensor_count += 1
                        logger.info(f"Published temperature sensor: {sensor_name} = {value}")
                    
                    # Send raw number, not quoted string
                    self.mqtt.publish_raw(topic, message)
            
            logger.info(f"Published {sensor_count} sensors to Home Assistant")
            
            # ===== V1 COMPATIBILITY SECTION - START =====
            # Legacy v1 compatibility removed - system now uses v3 sensors only
            
            # Publish switch states
            if self.mqtt and self.mqtt.is_connected():
                logger.info("Publishing switch states...")
                self._publish_switch_state('primary_pump', self.system_state['primary_pump'])
                self._publish_switch_state('primary_pump_manual', self.system_state['primary_pump_manual'])
                self._publish_switch_state('cartridge_heater', self.system_state['cartridge_heater'])
                logger.info("Switch states published successfully")
            
            # Publish number states
            if self.mqtt and self.mqtt.is_connected():
                logger.info("Publishing number states...")
                self._publish_number_state('set_temp_tank_1', self.control_params['set_temp_tank_1'])
                self._publish_number_state('dTStart_tank_1', self.control_params['dTStart_tank_1'])
                self._publish_number_state('dTStop_tank_1', self.control_params['dTStop_tank_1'])
                self._publish_number_state('kylning_kollektor', self.control_params['kylning_kollektor'])
                self._publish_number_state('temp_kok', self.control_params['temp_kok'])
                logger.info("Number states published successfully")
            

            
            # Publish system status
            status_data = {
                'system_state': self.system_state,
                'temperatures': self.temperatures,
                'timestamp': time.time()
            }
            
            if self.mqtt and self.mqtt.is_connected():
                logger.info("Publishing system status...")
                self.mqtt.publish_status(status_data)
                logger.info("System status published successfully")
                
                # Publish real-time energy sensor data
                logger.info("Publishing real-time energy sensor...")
                self.mqtt.publish_realtime_energy_sensor(self.temperatures)
                logger.info("Real-time energy sensor published successfully")
                
                # Process system status with TaskMaster AI (FR-008)
                if config.taskmaster_enabled:
                    try:
                        system_status = {
                            'mode': self.system_state.get('mode', 'unknown'),
                            'primary_pump': self.system_state.get('primary_pump', False),
                            'pump_runtime_hours': self.system_state.get('pump_runtime_hours', 0),
                            'heating_cycles_count': self.system_state.get('heating_cycles_count', 0),
                            'uptime': time.time() - self.system_state.get('last_update', time.time()),
                            'temperatures': self.temperatures
                        }
                        await taskmaster_service.process_system_status(system_status)
                    except Exception as e:
                        logger.error(f"Error processing system status with TaskMaster AI: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error publishing status: {e}")
    



    
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
                
                elif switch_name == 'primary_pump_manual':
                    self.system_state['primary_pump_manual'] = state
                    # When manual control is enabled, override automatic control
                    if state:
                        # Manual control ON - force pump to stay ON
                        self.system_state['primary_pump'] = True
                        logger.info("Primary pump manual control ON - pump forced ON")
                    else:
                        # Manual control OFF - force pump to stay OFF
                        self.system_state['primary_pump'] = False
                        logger.info("Primary pump manual control OFF - pump forced OFF")
                
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
                

            
            elif command_type == 'pellet_stove_data':
                sensor = data['sensor']
                value = data['value']
                
                # Update pellet stove data in system state
                if sensor in self.system_state:
                    self.system_state[sensor] = value
                    logger.info(f"Updated pellet stove data: {sensor} = {value}")
                else:
                    logger.warning(f"Unknown pellet stove sensor: {sensor}")
                
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
        
        # Cleanup TaskMaster AI service (FR-008)
        if config.taskmaster_enabled:
            try:
                await taskmaster_service.cleanup()
                logger.info("TaskMaster AI service cleaned up")
            except Exception as e:
                logger.error(f"Error cleaning up TaskMaster AI service: {str(e)}")
        
        # Save final operational state before shutdown
        logger.info("Saving final operational state...")
        self._save_system_state()
        
        logger.info("Solar Heating System v3 stopped")

    async def _start_background_tasks(self):
        """Start background tasks"""
        logger.info("Starting background tasks...")
        
        # Start temperature monitoring task
        self.temperature_task = asyncio.create_task(self._temperature_monitoring_loop())
        
        # Start status publishing task
        self.status_task = asyncio.create_task(self._status_publishing_loop())
        
        # Start heartbeat task for uptime monitoring
        self.heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        
        logger.info("Background tasks started successfully")
    
    async def _temperature_monitoring_loop(self):
        """Temperature monitoring loop"""
        while self.running:
            try:
                await self._read_temperatures()
                await asyncio.sleep(config.temperature_update_interval)
            except Exception as e:
                logger.error(f"Error in temperature monitoring loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _status_publishing_loop(self):
        """Status publishing loop"""
        while self.running:
            try:
                await self._publish_status()
                await asyncio.sleep(60)  # Publish status every minute
            except Exception as e:
                logger.error(f"Error in status publishing loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying
    
    async def _heartbeat_loop(self):
        """Heartbeat loop for uptime monitoring"""
        while self.running:
            try:
                if self.mqtt and self.mqtt.is_connected():
                    # Get basic system info for heartbeat
                    system_info = {
                        "system_state": self.system_state.get('mode', 'unknown'),
                        "primary_pump": self.system_state.get('primary_pump', False),
                        "cartridge_heater": self.system_state.get('cartridge_heater', False),
                        "temperature_count": len(self.temperatures),
                        "last_update": time.time()
                    }
                    
                    self.mqtt.publish_heartbeat(system_info)
                    logger.debug("Heartbeat published successfully")
                else:
                    logger.warning("Cannot publish heartbeat: MQTT not connected")
                
                await asyncio.sleep(30)  # Send heartbeat every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in heartbeat loop: {e}")
                await asyncio.sleep(10)  # Wait before retrying

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

