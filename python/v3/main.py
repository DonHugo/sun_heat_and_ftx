#!/usr/bin/env python3
"""
Main Application for Solar Heating System v3
Entry point for the intelligent solar heating system
"""

import asyncio
import logging
import signal
import sys
import time
from typing import Dict, Any

from config import config, pump_config
from hardware_interface import HardwareInterface
from mqtt_handler import MQTTHandler

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
        
        logger.info("Solar Heating System v3 initialized")
    
    async def start(self):
        """Start the solar heating system"""
        logger.info("Starting Solar Heating System v3...")
        
        try:
            # Initialize hardware interface
            self.hardware = HardwareInterface(simulation_mode=config.test_mode)
            
            # Test hardware connections
            hardware_test = self.hardware.test_hardware_connection()
            logger.info(f"Hardware test results: {hardware_test}")
            
            # Initialize MQTT handler
            self.mqtt = MQTTHandler()
            self.mqtt.set_system_event_callback(self._handle_system_event)
            
            # Connect to MQTT broker
            if not self.mqtt.connect():
                logger.error("Failed to connect to MQTT broker")
                return False
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.running = True
            logger.info("Solar Heating System v3 started successfully")
            
            # Start main system loop
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"Error starting system: {e}")
            return False
        
        return True
    
    async def stop(self):
        """Stop the solar heating system"""
        logger.info("Stopping Solar Heating System v3...")
        
        self.running = False
        
        if self.mqtt:
            self.mqtt.disconnect()
        
        logger.info("Solar Heating System v3 stopped")
    
    def _signal_handler(self, signum, frame):
        """Handle system signals for graceful shutdown"""
        logger.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(self.stop())
    
    async def _main_loop(self):
        """Main system control loop"""
        logger.info("Starting main control loop")
        
        while self.running:
            try:
                # Read temperature sensors
                await self._read_temperatures()
                
                # Process temperature data
                await self._process_temperatures()
                
                # Control pumps based on temperature logic
                await self._control_pumps()
                
                # Control cartridge heater
                await self._control_heater()
                
                # Publish system status
                await self._publish_status()
                
                # Wait for next cycle
                await asyncio.sleep(config.temperature_update_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
    
    async def _read_temperatures(self):
        """Read all temperature sensors"""
        try:
            self.temperatures = self.hardware.read_all_temperatures()
            logger.debug(f"Temperature readings: {self.temperatures}")
        except Exception as e:
            logger.error(f"Error reading temperatures: {e}")
    
    async def _process_temperatures(self):
        """Process temperature data and check thresholds"""
        try:
            # Publish individual temperature readings
            for sensor_name, temperature in self.temperatures.items():
                if self.mqtt and self.mqtt.is_connected():
                    self.mqtt.publish_temperature(sensor_name, temperature)
            
            # Check for temperature alerts
            await self._check_temperature_alerts()
            
        except Exception as e:
            logger.error(f"Error processing temperatures: {e}")
    
    async def _check_temperature_alerts(self):
        """Check for temperature threshold violations"""
        try:
            for sensor_name, temperature in self.temperatures.items():
                # Check high temperature threshold
                if temperature > config.temperature_threshold_high:
                    logger.warning(f"High temperature alert: {sensor_name} = {temperature}°C")
                    await self._handle_high_temperature(sensor_name, temperature)
                
                # Check low temperature threshold
                elif temperature < config.temperature_threshold_low:
                    logger.warning(f"Low temperature alert: {sensor_name} = {temperature}°C")
                    await self._handle_low_temperature(sensor_name, temperature)
                    
        except Exception as e:
            logger.error(f"Error checking temperature alerts: {e}")
    
    async def _handle_high_temperature(self, sensor_name: str, temperature: float):
        """Handle high temperature conditions"""
        if sensor_name == 'solar_collector' and temperature >= self.control_params['temp_kok']:
            # Emergency shutdown for boiling conditions
            logger.critical(f"Boiling temperature detected: {temperature}°C")
            await self._emergency_shutdown()
    
    async def _handle_low_temperature(self, sensor_name: str, temperature: float):
        """Handle low temperature conditions"""
        # Could trigger heating or other protective measures
        logger.info(f"Low temperature detected: {sensor_name} = {temperature}°C")
    
    async def _control_pumps(self):
        """Control pumps based on temperature logic"""
        try:
            if self.system_state['manual_control']:
                # Manual control mode - pumps controlled via MQTT commands
                return
            
            # Get key temperatures
            solar_collector = self.temperatures.get('solar_collector', 0)
            storage_tank = self.temperatures.get('storage_tank', 0)
            
            # Calculate temperature difference
            dT = solar_collector - storage_tank
            
            # Get current pump status
            current_pump_status = self.hardware.get_relay_state(pump_config.primary_pump_relay)
            
            # Pump control logic (based on existing v2 system)
            new_pump_status = self._determine_pump_status(
                solar_collector, storage_tank, dT, current_pump_status
            )
            
            # Set pump status if it changed
            if new_pump_status != current_pump_status:
                success = self.hardware.set_relay_state(
                    pump_config.primary_pump_relay, new_pump_status
                )
                if success:
                    self.system_state['primary_pump'] = new_pump_status
                    logger.info(f"Primary pump {'started' if new_pump_status else 'stopped'}")
                    
                    # Publish pump status
                    if self.mqtt and self.mqtt.is_connected():
                        self.mqtt.publish_pump_status('primary', new_pump_status)
            
        except Exception as e:
            logger.error(f"Error controlling pumps: {e}")
    
    def _determine_pump_status(self, solar_collector: float, storage_tank: float, 
                             dT: float, current_status: bool) -> bool:
        """Determine pump status based on temperature logic"""
        
        # Manual control override
        if self.system_state['manual_control']:
            return current_status
        
        # Emergency shutdown conditions
        if self.system_state['overheated'] or solar_collector >= self.control_params['temp_kok']:
            return False
        
        # CRITICAL FIX: Stop pump if tank is hotter than collector (negative dT)
        # This prevents reverse heat flow and protects the system
        if dT < 0:
            return False
        
        # Pump start conditions
        if not current_status:
            # Start pump if temperature difference is sufficient and tank not full
            if (dT >= self.control_params['dTStart_tank_1'] and 
                storage_tank <= self.control_params['set_temp_tank_1']):
                return True
            
            # Start pump if collector is too hot (cooling mode)
            if solar_collector >= self.control_params['kylning_kollektor']:
                return True
        
        # Pump stop conditions
        elif current_status:
            # Stop pump if temperature difference is too low
            if dT <= self.control_params['dTStop_tank_1']:
                return False
            
            # Stop pump if tank is full and collector not too hot
            if (storage_tank >= self.control_params['set_temp_tank_1'] and 
                solar_collector < self.control_params['kylning_kollektor']):
                return False
        
        return current_status
    
    async def _control_heater(self):
        """Control cartridge heater"""
        try:
            # Get current heater status
            current_heater_status = self.hardware.get_relay_state(pump_config.cartridge_heater_relay)
            
            # Heater control logic (simplified for now)
            # Could be enhanced with more sophisticated logic
            new_heater_status = self.system_state['cartridge_heater']
            
            if new_heater_status != current_heater_status:
                success = self.hardware.set_relay_state(
                    pump_config.cartridge_heater_relay, new_heater_status
                )
                if success:
                    logger.info(f"Cartridge heater {'started' if new_heater_status else 'stopped'}")
                    
        except Exception as e:
            logger.error(f"Error controlling heater: {e}")
    
    async def _publish_status(self):
        """Publish system status to MQTT"""
        try:
            if self.mqtt and self.mqtt.is_connected():
                # Update system state
                self.system_state['last_update'] = time.time()
                
                # Publish system status
                self.mqtt.publish_system_status(self.system_state)
                
                # Publish energy calculations
                energy_data = self._calculate_energy()
                self.mqtt.publish_energy_status(energy_data)
                
        except Exception as e:
            logger.error(f"Error publishing status: {e}")
    
    def _calculate_energy(self) -> Dict[str, Any]:
        """Calculate energy metrics"""
        try:
            # Simple energy calculation (based on existing v2 system)
            zero_temp = 4  # Base temperature for calculations
            water_volume = 35  # Liters per sensor
            
            total_energy = 0
            for sensor_name, temp in self.temperatures.items():
                if 'storage_tank' in sensor_name or 'solar_collector' in sensor_name:
                    energy = (temp - zero_temp) * water_volume
                    total_energy += energy
            
            # Convert to kWh
            energy_kwh = round(total_energy * 4200 / 1000 / 3600, 2)
            
            return {
                'total_energy_kwh': energy_kwh,
                'average_temperature': round(sum(self.temperatures.values()) / len(self.temperatures), 1),
                'sensor_count': len(self.temperatures)
            }
            
        except Exception as e:
            logger.error(f"Error calculating energy: {e}")
            return {'error': str(e)}
    
    async def _emergency_shutdown(self):
        """Emergency shutdown procedure"""
        logger.critical("Executing emergency shutdown")
        
        try:
            # Stop all pumps
            self.hardware.set_relay_state(pump_config.primary_pump_relay, False)
            self.hardware.set_relay_state(pump_config.secondary_pump_relay, False)
            
            # Stop heater
            self.hardware.set_relay_state(pump_config.cartridge_heater_relay, False)
            
            # Update system state
            self.system_state['primary_pump'] = False
            self.system_state['secondary_pump'] = False
            self.system_state['cartridge_heater'] = False
            self.system_state['overheated'] = True
            self.system_state['mode'] = 'emergency'
            
            # Publish emergency status
            if self.mqtt and self.mqtt.is_connected():
                self.mqtt.publish_system_status(self.system_state)
            
            logger.critical("Emergency shutdown completed")
            
        except Exception as e:
            logger.error(f"Error during emergency shutdown: {e}")
    
    def _handle_system_event(self, event_type: str, data: Dict[str, Any]):
        """Handle system events from MQTT"""
        try:
            logger.info(f"Handling system event: {event_type}")
            
            if event_type == 'hass_primary_pump_change':
                # Handle Home Assistant pump control
                self.system_state['primary_pump'] = data.get('value', False)
                self.hardware.set_relay_state(pump_config.primary_pump_relay, self.system_state['primary_pump'])
                
            elif event_type == 'hass_cartridge_heater_change':
                # Handle Home Assistant heater control
                self.system_state['cartridge_heater'] = data.get('value', False)
                self.hardware.set_relay_state(pump_config.cartridge_heater_relay, self.system_state['cartridge_heater'])
                
            elif event_type == 'hass_manual_control_change':
                # Handle manual control mode
                self.system_state['manual_control'] = data.get('value', False)
                
            elif event_type == 'hass_command_emergency_stop':
                # Handle emergency stop command
                asyncio.create_task(self._emergency_shutdown())
                
        except Exception as e:
            logger.error(f"Error handling system event {event_type}: {e}")

async def main():
    """Main application entry point"""
    logger.info("Solar Heating System v3 starting...")
    
    # Create and start system
    system = SolarHeatingSystem()
    
    try:
        await system.start()
    except KeyboardInterrupt:
        logger.info("Received keyboard interrupt")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        await system.stop()

if __name__ == "__main__":
    asyncio.run(main())
