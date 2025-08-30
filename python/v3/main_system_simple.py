#!/usr/bin/env python3
"""
Simplified Main Application for Solar Heating System v3
Entry point for testing without MQTT dependencies
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
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the v3 directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=getattr(logging, config.log_level.upper()),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('solar_heating_v3_simple.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class SolarHeatingSystemSimple:
    """Simplified solar heating system controller (no MQTT)"""
    
    def __init__(self):
        self.running = False
        self.hardware = None
        
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
        
        logger.info("Solar Heating System v3 (Simplified) initialized")
    
    async def start(self):
        """Start the solar heating system"""
        logger.info("Starting Solar Heating System v3 (Simplified)...")
        
        try:
            # Initialize hardware interface
            self.hardware = HardwareInterface(simulation_mode=config.test_mode)
            
            # Test hardware connections
            hardware_test = self.hardware.test_hardware_connection()
            logger.info(f"Hardware test results: {hardware_test}")
            
            # Set up signal handlers for graceful shutdown
            signal.signal(signal.SIGINT, self._signal_handler)
            signal.signal(signal.SIGTERM, self._signal_handler)
            
            self.running = True
            logger.info("Solar Heating System v3 (Simplified) started successfully")
            
            # Start main system loop
            await self._main_loop()
            
        except Exception as e:
            logger.error(f"Error starting system: {e}")
            return False
        
        return True
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        logger.info(f"Received signal {signum}, shutting down...")
        self.running = False
    
    async def _main_loop(self):
        """Main system control loop"""
        logger.info("Starting main control loop...")
        
        while self.running:
            try:
                # Read temperatures
                await self._read_temperatures()
                
                # Process control logic
                await self._process_control_logic()
                
                # Display status
                await self._display_status()
                
                # Wait for next cycle
                await asyncio.sleep(config.temperature_update_interval)
                
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                await asyncio.sleep(5)  # Wait before retrying
        
        logger.info("Main loop stopped")
    
    async def _read_temperatures(self):
        """Read all temperature sensors"""
        try:
            # Read RTD sensors
            for sensor_name, sensor_id in [
                ('solar_collector', 5),
                ('storage_tank', 6),
                ('return_line', 7)
            ]:
                temp = self.hardware.read_rtd_temperature(sensor_id)
                self.temperatures[sensor_name] = temp
                logger.debug(f"{sensor_name}: {temp}°C")
            
            # Read MegaBAS sensors
            for sensor_name, sensor_id in [
                ('heat_exchanger_in', 0),
                ('heat_exchanger_out', 1),
                ('storage_tank_top', 2),
                ('storage_tank_bottom', 3),
                ('ambient_air', 4)
            ]:
                temp = self.hardware.read_megabas_temperature(sensor_id)
                self.temperatures[sensor_name] = temp
                logger.debug(f"{sensor_name}: {temp}°C")
                
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
    
    async def _display_status(self):
        """Display system status"""
        try:
            logger.info("=" * 60)
            logger.info("SYSTEM STATUS")
            logger.info("=" * 60)
            logger.info(f"Mode: {self.system_state['mode']}")
            logger.info(f"Primary Pump: {'ON' if self.system_state['primary_pump'] else 'OFF'}")
            logger.info(f"Secondary Pump: {'ON' if self.system_state['secondary_pump'] else 'OFF'}")
            logger.info("")
            logger.info("TEMPERATURES:")
            for name, temp in self.temperatures.items():
                logger.info(f"  {name}: {temp}°C")
            logger.info("=" * 60)
                
        except Exception as e:
            logger.error(f"Error displaying status: {e}")
    
    async def stop(self):
        """Stop the solar heating system"""
        logger.info("Stopping Solar Heating System v3...")
        
        self.running = False
        
        # Stop pumps
        if self.hardware:
            self.hardware.set_relay_state(1, False)  # Primary pump
            self.hardware.set_relay_state(2, False)  # Secondary pump
        
        logger.info("Solar Heating System v3 stopped")

async def main():
    """Main entry point"""
    system = SolarHeatingSystemSimple()
    
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
