#!/usr/bin/env python3
"""
Test script for Home Assistant switch and number controls
This script tests the MQTT message handling for switches and numbers
"""

import asyncio
import json
import logging
import sys
import time
from typing import Dict, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import system modules
try:
    from config import config, mqtt_topics
    from mqtt_handler import MQTTHandler
    from hardware_interface import HardwareInterface
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the v3 directory")
    sys.exit(1)

class ControlTester:
    """Test class for switch and number controls"""
    
    def __init__(self):
        self.mqtt = None
        self.hardware = None
        self.test_results = {
            'switch_commands': [],
            'number_commands': [],
            'errors': []
        }
    
    async def start(self):
        """Start the test system"""
        logger.info("Starting control test system...")
        
        try:
            # Initialize hardware interface (simulation mode)
            self.hardware = HardwareInterface()
            
            # Initialize MQTT handler
            self.mqtt = MQTTHandler()
            
            # Register system callback
            self.mqtt.system_callback = self._handle_system_command
            
            # Connect to MQTT
            self.mqtt.connect()
            
            logger.info("Control test system started successfully")
            
        except Exception as e:
            logger.error(f"Error starting test system: {e}")
            raise
    
    def _handle_system_command(self, command_type: str, data: Dict[str, Any]):
        """Handle system commands from MQTT"""
        logger.info(f"Received system command: {command_type} - {data}")
        
        if command_type == 'switch_command':
            self.test_results['switch_commands'].append(data)
            logger.info(f"✅ Switch command received: {data['switch']} = {'ON' if data['state'] else 'OFF'}")
            
            # Simulate hardware control
            if self.hardware:
                relay_num = data['relay']
                state = data['state']
                self.hardware.set_relay_state(relay_num, state)
                logger.info(f"🔧 Hardware relay {relay_num} set to {'ON' if state else 'OFF'}")
        
        elif command_type == 'number_command':
            self.test_results['number_commands'].append(data)
            logger.info(f"✅ Number command received: {data['number']} = {data['value']}")
        
        elif command_type == 'v1_test_switch_command':
            logger.info(f"✅ v1 test switch command received: {'ON' if data['state'] else 'OFF'}")
    
    async def test_switch_commands(self):
        """Test switch commands by publishing MQTT messages"""
        logger.info("🧪 Testing switch commands...")
        
        # Test primary pump
        await self._test_switch('primary_pump', 'ON')
        await asyncio.sleep(1)
        await self._test_switch('primary_pump', 'OFF')
        await asyncio.sleep(1)
        
        # Test primary pump manual control
        await self._test_switch('primary_pump_manual', 'ON')
        await asyncio.sleep(1)
        await self._test_switch('primary_pump_manual', 'OFF')
        await asyncio.sleep(1)
        

        
        # Test cartridge heater
        await self._test_switch('cartridge_heater', 'ON')
        await asyncio.sleep(1)
        await self._test_switch('cartridge_heater', 'OFF')
        await asyncio.sleep(1)
    
    async def test_number_commands(self):
        """Test number commands by publishing MQTT messages"""
        logger.info("🧪 Testing number commands...")
        
        # Test set tank temperature
        await self._test_number('set_temp_tank_1', 75.0)
        await asyncio.sleep(1)
        
        # Test delta temperature start
        await self._test_number('dTStart_tank_1', 10.0)
        await asyncio.sleep(1)
        
        # Test delta temperature stop
        await self._test_number('dTStop_tank_1', 5.0)
        await asyncio.sleep(1)
        
        # Test cooling collector temperature
        await self._test_number('kylning_kollektor', 95.0)
        await asyncio.sleep(1)
        
        # Test boiling temperature
        await self._test_number('temp_kok', 160.0)
        await asyncio.sleep(1)
    
    async def _test_switch(self, switch_name: str, state: str):
        """Test a specific switch command"""
        topic = f"homeassistant/switch/solar_heating_{switch_name}/set"
        logger.info(f"📤 Publishing switch command: {topic} = {state}")
        self.mqtt.publish_raw(topic, state)
    
    async def _test_number(self, number_name: str, value: float):
        """Test a specific number command"""
        topic = f"homeassistant/number/solar_heating_{number_name}/set"
        logger.info(f"📤 Publishing number command: {topic} = {value}")
        self.mqtt.publish_raw(topic, str(value))
    
    def print_results(self):
        """Print test results"""
        logger.info("📊 Test Results:")
        logger.info(f"Switch commands received: {len(self.test_results['switch_commands'])}")
        for cmd in self.test_results['switch_commands']:
            logger.info(f"  - {cmd['switch']}: {'ON' if cmd['state'] else 'OFF'} (relay {cmd['relay']})")
        
        logger.info(f"Number commands received: {len(self.test_results['number_commands'])}")
        for cmd in self.test_results['number_commands']:
            logger.info(f"  - {cmd['number']}: {cmd['value']}")
        
        if self.test_results['errors']:
            logger.error(f"Errors: {len(self.test_results['errors'])}")
            for error in self.test_results['errors']:
                logger.error(f"  - {error}")
    
    async def stop(self):
        """Stop the test system"""
        logger.info("Stopping control test system...")
        
        if self.mqtt:
            self.mqtt.disconnect()
        
        logger.info("Control test system stopped")

async def main():
    """Main test function"""
    tester = ControlTester()
    
    try:
        await tester.start()
        
        # Wait a moment for MQTT to settle
        await asyncio.sleep(2)
        
        # Run tests
        await tester.test_switch_commands()
        await asyncio.sleep(2)
        await tester.test_number_commands()
        
        # Wait for all commands to be processed
        await asyncio.sleep(3)
        
        # Print results
        tester.print_results()
        
    except KeyboardInterrupt:
        logger.info("Test interrupted by user")
    except Exception as e:
        logger.error(f"Test error: {e}")
    finally:
        await tester.stop()

if __name__ == "__main__":
    asyncio.run(main())
