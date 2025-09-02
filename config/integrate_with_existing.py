#!/usr/bin/env python3
"""
Integration Example: TaskMaster AI with Existing Temperature Monitoring System
This file shows how to integrate TaskMaster AI with your existing solar heating system.
"""

import asyncio
import logging
from typing import Dict, Any
import sys
import os

# Add the python/v2 directory to the path to import existing modules
sys.path.append(os.path.join(os.path.dirname(__file__), 'python', 'v2'))

from taskmaster_service import taskmaster_service
from taskmaster_config import config

# Import your existing modules (adjust paths as needed)
try:
    from python.v2.sensor_manager import SensorManager
    from python.v2.hardware_interface import HardwareInterface
    from python.v2.controller import Controller
    EXISTING_MODULES_AVAILABLE = True
except ImportError:
    print("Warning: Existing modules not found. Running in demo mode.")
    EXISTING_MODULES_AVAILABLE = False

logger = logging.getLogger(__name__)

class TaskMasterIntegration:
    """Integration class that connects TaskMaster AI with existing system"""
    
    def __init__(self):
        self.taskmaster_service = taskmaster_service
        self.sensor_manager = None
        self.hardware_interface = None
        self.controller = None
        
        if EXISTING_MODULES_AVAILABLE:
            self.initialize_existing_modules()
    
    def initialize_existing_modules(self):
        """Initialize existing system modules"""
        try:
            self.sensor_manager = SensorManager()
            self.hardware_interface = HardwareInterface()
            self.controller = Controller()
            logger.info("Existing modules initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize existing modules: {e}")
    
    async def start_integration(self):
        """Start the TaskMaster AI integration"""
        logger.info("Starting TaskMaster AI integration...")
        
        # Initialize TaskMaster AI service
        success = await self.taskmaster_service.initialize()
        if not success:
            logger.error("Failed to initialize TaskMaster AI service")
            return False
        
        # Start periodic optimization
        asyncio.create_task(self.taskmaster_service.run_periodic_optimization())
        
        logger.info("TaskMaster AI integration started successfully")
        return True
    
    async def process_sensor_data(self):
        """Process sensor data from existing system"""
        if not self.sensor_manager:
            logger.warning("Sensor manager not available, using demo data")
            return await self.process_demo_data()
        
        try:
            # Get temperature data from existing sensors
            temperature_data = {}
            
            # Read from your existing temperature sensors
            # Adjust these calls based on your actual sensor implementation
            sensors = self.sensor_manager.get_all_sensors()
            
            for sensor_id, sensor in sensors.items():
                if sensor.type == "temperature":
                    temp = sensor.read_value()
                    temperature_data[sensor_id] = temp
            
            # Process through TaskMaster AI
            await self.taskmaster_service.process_temperature_data(temperature_data)
            
            logger.info(f"Processed temperature data: {temperature_data}")
            
        except Exception as e:
            logger.error(f"Error processing sensor data: {e}")
    
    async def process_demo_data(self):
        """Process demo temperature data"""
        demo_data = {
            "solar_collector": 75.2,
            "storage_tank": 62.8,
            "heat_exchanger": 58.9
        }
        
        await self.taskmaster_service.process_temperature_data(demo_data)
        logger.info(f"Processed demo temperature data: {demo_data}")
    
    async def execute_hardware_control(self, task_type: str, parameters: Dict[str, Any]):
        """Execute hardware control based on TaskMaster AI tasks"""
        if not self.hardware_interface:
            logger.warning("Hardware interface not available")
            return
        
        try:
            if task_type == "pump_control":
                await self.execute_pump_control(parameters)
            elif task_type == "valve_control":
                await self.execute_valve_control(parameters)
            else:
                logger.warning(f"Unknown task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Error executing hardware control: {e}")
    
    async def execute_pump_control(self, parameters: Dict[str, Any]):
        """Execute pump control commands"""
        action = parameters.get("action")
        
        if action == "increase_flow":
            # Turn on primary pump
            self.hardware_interface.set_relay_state(1, True)
            logger.info("Primary pump activated")
        elif action == "decrease_flow":
            # Turn off primary pump
            self.hardware_interface.set_relay_state(1, False)
            logger.info("Primary pump deactivated")
        elif action == "emergency_stop":
            # Emergency stop all pumps
            self.hardware_interface.set_relay_state(1, False)
            self.hardware_interface.set_relay_state(2, False)
            logger.warning("Emergency stop: All pumps deactivated")
    
    async def execute_valve_control(self, parameters: Dict[str, Any]):
        """Execute valve control commands"""
        action = parameters.get("action")
        position = parameters.get("position", 0.5)
        
        if action == "open_collector_valve":
            # Open collector valve
            self.hardware_interface.set_analog_output(1, position)
            logger.info(f"Collector valve opened to {position}")
        elif action == "close_collector_valve":
            # Close collector valve
            self.hardware_interface.set_analog_output(1, 0.0)
            logger.info("Collector valve closed")
        elif action == "optimize_distribution":
            # Optimize valve distribution
            self.hardware_interface.set_analog_output(1, position)
            self.hardware_interface.set_analog_output(2, 1.0 - position)
            logger.info(f"Valve distribution optimized: {position}")
    
    async def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        taskmaster_status = await self.taskmaster_service.get_system_status()
        
        status = {
            "taskmaster_ai": taskmaster_status,
            "hardware_available": EXISTING_MODULES_AVAILABLE,
            "sensors_available": self.sensor_manager is not None,
            "hardware_control_available": self.hardware_interface is not None
        }
        
        if self.sensor_manager:
            try:
                sensors = self.sensor_manager.get_all_sensors()
                status["sensor_count"] = len(sensors)
                status["sensor_types"] = list(set(s.type for s in sensors.values()))
            except Exception as e:
                status["sensor_error"] = str(e)
        
        return status
    
    async def run_monitoring_loop(self, interval: int = 30):
        """Run continuous monitoring loop"""
        logger.info(f"Starting monitoring loop with {interval}s interval")
        
        while True:
            try:
                # Process sensor data
                await self.process_sensor_data()
                
                # Get and log system status
                status = await self.get_system_status()
                logger.info(f"System status: {status['taskmaster_ai']['active_tasks']} active tasks")
                
                # Wait for next cycle
                await asyncio.sleep(interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    async def shutdown(self):
        """Shutdown the integration"""
        logger.info("Shutting down TaskMaster AI integration...")
        await self.taskmaster_service.shutdown()

async def main():
    """Main integration function"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    integration = TaskMasterIntegration()
    
    try:
        # Start integration
        success = await integration.start_integration()
        if not success:
            logger.error("Failed to start integration")
            return
        
        # Run monitoring loop
        await integration.run_monitoring_loop()
        
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    except Exception as e:
        logger.error(f"Integration error: {e}")
    finally:
        await integration.shutdown()

if __name__ == "__main__":
    asyncio.run(main())
