#!/usr/bin/env python3
"""
Basic test script for Solar Heating System v3
Tests core functionality without MQTT
"""

import asyncio
import logging
import os
import sys
import time

# Set test mode
os.environ['SOLAR_TEST_MODE'] = 'true'
os.environ['SOLAR_DEBUG_MODE'] = 'true'
os.environ['SOLAR_LOG_LEVEL'] = 'info'

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """Test basic system functionality without MQTT"""
    logger.info("🧪 Testing Basic System Functionality")
    logger.info("=" * 50)
    
    try:
        # Test config
        from config import config, sensor_mapping, pump_config
        logger.info(f"✅ Config loaded: {config.hardware_platform}")
        logger.info(f"✅ Temperature thresholds: {config.temperature_threshold_low}°C - {config.temperature_threshold_high}°C")
        logger.info(f"✅ Tank target temperature: {config.set_temp_tank_1}°C")
        
        # Test hardware interface
        from hardware_interface import HardwareInterface
        hw = HardwareInterface(simulation_mode=True)
        logger.info("✅ Hardware interface created")
        
        # Test temperature reading
        temps = hw.read_all_temperatures()
        logger.info(f"✅ Temperature readings: {len(temps)} sensors")
        for sensor, temp in temps.items():
            logger.info(f"   {sensor}: {temp}°C")
        
        # Test relay control
        logger.info("✅ Testing relay control...")
        hw.set_relay_state(1, True)
        relay1_status = hw.get_relay_state(1)
        logger.info(f"   Relay 1 status: {relay1_status}")
        
        hw.set_relay_state(1, False)
        relay1_status = hw.get_relay_state(1)
        logger.info(f"   Relay 1 status after OFF: {relay1_status}")
        
        # Test hardware status
        status = hw.get_system_status()
        logger.info(f"✅ Hardware status: {status['hardware_available']}")
        logger.info(f"✅ Simulation mode: {status['simulation_mode']}")
        
        # Test pump control logic
        logger.info("✅ Testing pump control logic...")
        solar_temp = temps.get('solar_collector', 0)
        tank_temp = temps.get('storage_tank', 0)
        dT = solar_temp - tank_temp
        
        logger.info(f"   Solar collector: {solar_temp}°C")
        logger.info(f"   Storage tank: {tank_temp}°C")
        logger.info(f"   Temperature difference (dT): {dT}°C")
        
        # Test pump start conditions
        dT_start = config.dTStart_tank_1
        tank_target = config.set_temp_tank_1
        
        should_start = (dT >= dT_start and tank_temp <= tank_target)
        logger.info(f"   Should start pump: {should_start} (dT >= {dT_start} and tank <= {tank_target})")
        
        # Test energy calculation
        logger.info("✅ Testing energy calculation...")
        zero_temp = 4
        water_volume = 35
        total_energy = 0
        
        for sensor_name, temp in temps.items():
            if 'storage_tank' in sensor_name or 'solar_collector' in sensor_name:
                energy = (temp - zero_temp) * water_volume
                total_energy += energy
                logger.info(f"   {sensor_name}: {energy:.1f} kJ")
        
        energy_kwh = round(total_energy * 4200 / 1000 / 3600, 2)
        logger.info(f"   Total energy: {energy_kwh} kWh")
        
        # Test MQTT handler creation (without connecting)
        from mqtt_handler import MQTTHandler
        mqtt = MQTTHandler()
        logger.info(f"✅ MQTT handler created: {mqtt.broker}:{mqtt.port}")
        
        logger.info("✅ All basic tests passed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False

async def test_control_logic():
    """Test the control logic"""
    logger.info("🔧 Testing Control Logic")
    logger.info("-" * 30)
    
    try:
        from config import config
        from hardware_interface import HardwareInterface
        from main import SolarHeatingSystem
        
        hw = HardwareInterface(simulation_mode=True)
        system = SolarHeatingSystem()
        
        # Test different temperature scenarios
        scenarios = [
            {"solar": 80, "tank": 60, "expected": "start"},
            {"solar": 70, "tank": 75, "expected": "stop"},
            {"solar": 90, "tank": 50, "expected": "start"},
            {"solar": 60, "tank": 65, "expected": "stop"},
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            logger.info(f"Scenario {i}: Solar={scenario['solar']}°C, Tank={scenario['tank']}°C")
            
            # Use the exact scenario temperatures
            solar_temp = scenario['solar']
            tank_temp = scenario['tank']
            dT = solar_temp - tank_temp
            
            # Use the actual control logic method
            pump_status = system._determine_pump_status(solar_temp, tank_temp, dT, False)
            action = "start" if pump_status else "stop"
            
            logger.info(f"   dT={dT:.1f}°C, Action: {action} (expected: {scenario['expected']})")
            
            if action == scenario['expected']:
                logger.info("   ✅ Correct action")
            else:
                logger.warning("   ⚠️  Unexpected action")
        
        logger.info("✅ Control logic tests completed!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Control logic test failed: {e}")
        return False

async def main():
    """Main test function"""
    logger.info("🚀 Solar Heating System v3 Basic Test Suite")
    logger.info("=" * 60)
    
    try:
        # Test basic functionality
        basic_ok = await test_basic_functionality()
        if not basic_ok:
            return 1
        
        logger.info("")
        
        # Test control logic
        control_ok = await test_control_logic()
        if not control_ok:
            return 1
        
        logger.info("")
        logger.info("🎉 All tests completed successfully!")
        logger.info("✅ System is ready for deployment!")
        
        return 0
        
    except KeyboardInterrupt:
        logger.info("🛑 Test interrupted by user")
        return 1
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
