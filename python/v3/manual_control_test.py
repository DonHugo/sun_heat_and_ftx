#!/usr/bin/env python3
"""
Manual Control Test Script for Solar Heating System v3
This script allows you to manually test switches and numbers
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

class ManualControlTester:
    """Manual control tester for switches and numbers"""
    
    def __init__(self):
        self.mqtt = None
        self.hardware = None
        self.running = False
    
    async def start(self):
        """Start the manual control tester"""
        logger.info("Starting manual control tester...")
        
        try:
            # Initialize hardware interface (simulation mode)
            self.hardware = HardwareInterface()
            
            # Initialize MQTT handler
            self.mqtt = MQTTHandler()
            
            # Register system callback
            self.mqtt.system_callback = self._handle_system_command
            
            # Connect to MQTT
            self.mqtt.connect()
            
            self.running = True
            logger.info("Manual control tester started successfully")
            
        except Exception as e:
            logger.error(f"Error starting manual control tester: {e}")
            raise
    
    def _handle_system_command(self, command_type: str, data: Dict[str, Any]):
        """Handle system commands from MQTT"""
        logger.info(f"🎯 Received system command: {command_type} - {data}")
        
        if command_type == 'switch_command':
            logger.info(f"✅ Switch command: {data['switch']} = {'ON' if data['state'] else 'OFF'}")
            
            # Simulate hardware control
            if self.hardware:
                relay_num = data['relay']
                state = data['state']
                self.hardware.set_relay_state(relay_num, state)
                logger.info(f"🔧 Hardware relay {relay_num} set to {'ON' if state else 'OFF'}")
        
        elif command_type == 'number_command':
            logger.info(f"✅ Number command: {data['number']} = {data['value']}")
        
        elif command_type == 'v1_test_switch_command':
            logger.info(f"✅ v1 test switch command: {'ON' if data['state'] else 'OFF'}")
    
    async def test_switch(self, switch_name: str, state: str):
        """Test a specific switch"""
        topic = f"homeassistant/switch/solar_heating_{switch_name}/set"
        logger.info(f"📤 Testing switch: {topic} = {state}")
        self.mqtt.publish_raw(topic, state)
    
    async def test_number(self, number_name: str, value: float):
        """Test a specific number"""
        topic = f"homeassistant/number/solar_heating_{number_name}/set"
        logger.info(f"📤 Testing number: {topic} = {value}")
        self.mqtt.publish_raw(topic, str(value))
    
    def print_menu(self):
        """Print the control menu"""
        print("\n" + "="*50)
        print("🔧 MANUAL CONTROL TESTER")
        print("="*50)
        print("Available switches:")
        print("  1. Primary Pump")
        print("  2. Secondary Pump") 
        print("  3. Cartridge Heater")
        print("\nAvailable numbers:")
        print("  4. Set Tank Temperature")
        print("  5. Delta Temperature Start")
        print("  6. Delta Temperature Stop")
        print("  7. Cooling Collector Temperature")
        print("  8. Boiling Temperature")
        print("\nOther options:")
        print("  9. Test all switches")
        print("  10. Test all numbers")
        print("  11. Show current relay states")
        print("  0. Exit")
        print("="*50)
    
    async def run_interactive(self):
        """Run interactive control tester"""
        logger.info("Starting interactive control tester...")
        
        switch_mapping = {
            '1': 'primary_pump',
            '2': 'secondary_pump', 
            '3': 'cartridge_heater'
        }
        
        number_mapping = {
            '4': ('set_temp_tank_1', 70.0),
            '5': ('dTStart_tank_1', 8.0),
            '6': ('dTStop_tank_1', 4.0),
            '7': ('kylning_kollektor', 90.0),
            '8': ('temp_kok', 150.0)
        }
        
        while self.running:
            try:
                self.print_menu()
                choice = input("\nEnter your choice (0-11): ").strip()
                
                if choice == '0':
                    logger.info("Exiting manual control tester...")
                    break
                
                elif choice in switch_mapping:
                    switch_name = switch_mapping[choice]
                    state = input(f"Enter state for {switch_name} (ON/OFF): ").strip().upper()
                    if state in ['ON', 'OFF']:
                        await self.test_switch(switch_name, state)
                        await asyncio.sleep(1)
                    else:
                        print("❌ Invalid state. Use ON or OFF.")
                
                elif choice in number_mapping:
                    number_name, default_value = number_mapping[choice]
                    value_input = input(f"Enter value for {number_name} (default: {default_value}): ").strip()
                    try:
                        value = float(value_input) if value_input else default_value
                        await self.test_number(number_name, value)
                        await asyncio.sleep(1)
                    except ValueError:
                        print("❌ Invalid number value.")
                
                elif choice == '9':
                    logger.info("Testing all switches...")
                    for switch_name in switch_mapping.values():
                        await self.test_switch(switch_name, 'ON')
                        await asyncio.sleep(0.5)
                        await self.test_switch(switch_name, 'OFF')
                        await asyncio.sleep(0.5)
                
                elif choice == '10':
                    logger.info("Testing all numbers...")
                    for number_name, default_value in number_mapping.values():
                        await self.test_number(number_name, default_value)
                        await asyncio.sleep(0.5)
                
                elif choice == '11':
                    if self.hardware:
                        logger.info("Current relay states:")
                        for relay in range(1, 5):
                            state = self.hardware.get_relay_state(relay)
                            logger.info(f"  Relay {relay}: {'ON' if state else 'OFF'}")
                    else:
                        print("❌ Hardware interface not available")
                
                else:
                    print("❌ Invalid choice. Please enter 0-11.")
                
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info("Interrupted by user")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
    
    async def stop(self):
        """Stop the manual control tester"""
        logger.info("Stopping manual control tester...")
        
        self.running = False
        
        if self.mqtt:
            self.mqtt.disconnect()
        
        logger.info("Manual control tester stopped")

async def main():
    """Main function"""
    tester = ManualControlTester()
    
    try:
        await tester.start()
        
        # Wait a moment for MQTT to settle
        await asyncio.sleep(2)
        
        # Run interactive mode
        await tester.run_interactive()
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        await tester.stop()

if __name__ == "__main__":
    asyncio.run(main())
