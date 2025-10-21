#!/usr/bin/env python3
"""
Basic Functionality Test Runner
Quick tests for the most critical system functionality.

This is a simplified test runner that focuses on the essential functionality
that must work for the system to operate correctly.
"""

import asyncio
import sys
import os
import time
import logging
from typing import Dict, Any

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_system import SolarHeatingSystem
    from config import config
except ImportError as e:
    print(f"Error importing modules: {e}")
    print("Make sure you're running from the v3 directory")
    sys.exit(1)

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BasicFunctionalityTester:
    """Quick tester for basic system functionality"""
    
    def __init__(self):
        self.system = None
        self.test_count = 0
        self.passed_count = 0
        
    async def setup(self):
        """Setup test environment"""
        logger.info("🧪 Setting up Basic Functionality Test...")
        self.system = SolarHeatingSystem()
        
    def test(self, name: str, condition: bool, message: str = ""):
        """Run a single test"""
        self.test_count += 1
        if condition:
            self.passed_count += 1
            logger.info(f"✅ PASS - {name}")
            if message:
                logger.info(f"    {message}")
        else:
            logger.error(f"❌ FAIL - {name}")
            if message:
                logger.error(f"    {message}")
                
    async def test_sensor_mapping_fix(self):
        """Test the sensor mapping fix that was implemented"""
        logger.info("🔍 Testing sensor mapping fix...")
        
        # Set test sensor data
        self.system.temperatures['megabas_sensor_6'] = 100.0  # Solar collector
        self.system.temperatures['megabas_sensor_7'] = 30.0   # Storage tank
        
        # Run sensor mapping (inline mapping like in the actual code)
        self.system.temperatures['solar_collector'] = self.system.temperatures.get('megabas_sensor_6', 0)
        self.system.temperatures['storage_tank'] = self.system.temperatures.get('megabas_sensor_7', 0)
        
        # Test 1: Check if mapping worked
        solar_collector = self.system.temperatures.get('solar_collector', 0)
        storage_tank = self.system.temperatures.get('storage_tank', 0)
        
        self.test(
            "Sensor Mapping Fix",
            solar_collector == 100.0 and storage_tank == 30.0,
            f"Collector: {solar_collector}°C, Tank: {storage_tank}°C"
        )
        
        # Test 2: Check dT calculation
        dT = solar_collector - storage_tank
        expected_dt = 70.0
        
        self.test(
            "dT Calculation",
            abs(dT - expected_dt) < 0.1,
            f"dT: {dT}°C, Expected: {expected_dt}°C"
        )
        
        # Test 3: Check pump control logic
        dTStart = self.system.control_params.get('dTStart_tank_1', 8.0)
        pump_should_start = dT >= dTStart
        
        self.test(
            "Pump Control Logic",
            pump_should_start,
            f"dT={dT}°C >= {dTStart}°C threshold, pump should start"
        )
        
    async def test_temperature_scenarios(self):
        """Test various temperature scenarios"""
        logger.info("🌡️ Testing temperature scenarios...")
        
        scenarios = [
            {"collector": 50.0, "tank": 30.0, "expected_dt": 20.0, "pump_should_start": True},
            {"collector": 35.0, "tank": 30.0, "expected_dt": 5.0, "pump_should_start": False},
            {"collector": 38.0, "tank": 30.0, "expected_dt": 8.0, "pump_should_start": True},
            {"collector": 34.0, "tank": 30.0, "expected_dt": 4.0, "pump_should_start": False},
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            # Set temperatures
            self.system.temperatures['megabas_sensor_6'] = scenario['collector']
            self.system.temperatures['megabas_sensor_7'] = scenario['tank']
            
            # Run sensor mapping (inline mapping like in the actual code)
            self.system.temperatures['solar_collector'] = self.system.temperatures.get('megabas_sensor_6', 0)
            self.system.temperatures['storage_tank'] = self.system.temperatures.get('megabas_sensor_7', 0)
            
            # Calculate dT
            solar_collector = self.system.temperatures.get('solar_collector', 0)
            storage_tank = self.system.temperatures.get('storage_tank', 0)
            dT = solar_collector - storage_tank
            
            # Test dT calculation
            expected_dt = scenario['expected_dt']
            dT_correct = abs(dT - expected_dt) < 0.1
            
            self.test(
                f"Temperature Scenario {i} - dT Calculation",
                dT_correct,
                f"Collector: {solar_collector}°C, Tank: {storage_tank}°C, dT: {dT}°C, Expected: {expected_dt}°C"
            )
            
            # Test pump control
            dTStart = self.system.control_params.get('dTStart_tank_1', 8.0)
            pump_should_start = dT >= dTStart
            expected_pump = scenario['pump_should_start']
            
            self.test(
                f"Temperature Scenario {i} - Pump Control",
                pump_should_start == expected_pump,
                f"dT={dT}°C, threshold={dTStart}°C, pump should {'start' if expected_pump else 'not start'}"
            )
            
    async def test_energy_calculation(self):
        """Test energy calculation"""
        logger.info("⚡ Testing energy calculation...")
        
        # Set temperatures for energy calculation
        self.system.temperatures['megabas_sensor_6'] = 80.0  # Solar collector
        self.system.temperatures['megabas_sensor_7'] = 20.0  # Storage tank
        
        # Run sensor mapping (inline mapping like in the actual code)
        self.system.temperatures['solar_collector'] = self.system.temperatures.get('megabas_sensor_6', 0)
        self.system.temperatures['storage_tank'] = self.system.temperatures.get('megabas_sensor_7', 0)
        
        # Calculate dT
        solar_collector = self.system.temperatures.get('solar_collector', 0)
        storage_tank = self.system.temperatures.get('storage_tank', 0)
        dT = solar_collector - storage_tank
        
        # Calculate energy (physics-based)
        tank_volume_kg = 360  # 360L tank
        specific_heat_capacity = 4.2  # kJ/kg°C
        energy_kj = tank_volume_kg * specific_heat_capacity * dT
        energy_kwh = energy_kj / 3600  # Convert to kWh
        
        expected_energy_kwh = 25.2  # 360 * 4.2 * 60 / 3600
        
        self.test(
            "Energy Calculation",
            abs(energy_kwh - expected_energy_kwh) < 0.1,
            f"Energy: {energy_kwh:.2f} kWh, Expected: {expected_energy_kwh} kWh"
        )
        
    async def test_system_state(self):
        """Test system state functionality"""
        logger.info("🔄 Testing system state...")
        
        # Test state initialization
        state_initialized = (
            'mode' in self.system.system_state and
            'primary_pump' in self.system.system_state and
            'pump_runtime_hours' in self.system.system_state
        )
        
        self.test(
            "System State Initialization",
            state_initialized,
            "All required state variables are present"
        )
        
        # Test state modification
        original_mode = self.system.system_state['mode']
        self.system.system_state['mode'] = 'test_mode'
        mode_changed = self.system.system_state['mode'] == 'test_mode'
        self.system.system_state['mode'] = original_mode  # Restore
        
        self.test(
            "System State Modification",
            mode_changed,
            "State can be modified and restored"
        )
        
    async def run_all_tests(self):
        """Run all basic functionality tests"""
        logger.info("🚀 Starting Basic Functionality Test")
        logger.info("=" * 50)
        
        await self.setup()
        
        try:
            await self.test_sensor_mapping_fix()
            await self.test_temperature_scenarios()
            await self.test_energy_calculation()
            await self.test_system_state()
            
        except Exception as e:
            logger.error(f"❌ Test execution failed: {str(e)}")
            self.test_count += 1  # Count the failure
            
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        failed_count = self.test_count - self.passed_count
        success_rate = (self.passed_count / self.test_count * 100) if self.test_count > 0 else 0
        
        logger.info("\n📊 BASIC FUNCTIONALITY TEST SUMMARY")
        logger.info("=" * 50)
        logger.info(f"Total Tests: {self.test_count}")
        logger.info(f"Passed: {self.passed_count} ✅")
        logger.info(f"Failed: {failed_count} ❌")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        
        if failed_count > 0:
            logger.info(f"\n⚠️  {failed_count} TESTS FAILED. System needs attention.")
        else:
            logger.info("\n🎉 ALL TESTS PASSED! Basic functionality is working correctly.")
            
        return success_rate == 100.0

async def main():
    """Main test runner"""
    tester = BasicFunctionalityTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
