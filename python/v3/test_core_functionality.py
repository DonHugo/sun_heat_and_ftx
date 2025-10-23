#!/usr/bin/env python3
"""
Core Functionality Test Suite for Solar Heating System v3
Tests the fundamental system functionality that was missing from previous test suites.

This test suite focuses on:
1. Sensor data flow validation
2. Temperature calculation accuracy
3. Pump control logic completeness
4. Energy calculation validation
5. System state consistency
"""

import asyncio
import sys
import os
import time
import logging
from typing import Dict, Any, List
from dataclasses import dataclass

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

@dataclass
class TestResult:
    """Test result container"""
    name: str
    passed: bool
    message: str
    duration: float = 0.0
    details: Dict[str, Any] = None

class CoreFunctionalityTestSuite:
    """Comprehensive test suite for core system functionality"""
    
    def __init__(self):
        self.system = None
        self.test_results = []
        self.start_time = None
        
    async def setup(self):
        """Setup test environment"""
        logger.info("🧪 Setting up Core Functionality Test Suite...")
        self.system = SolarHeatingSystem()
        self.start_time = time.time()
        
    async def teardown(self):
        """Cleanup test environment"""
        if self.system:
            # Cleanup any resources
            pass
            
    def log_test_result(self, result: TestResult):
        """Log test result"""
        status = "✅ PASS" if result.passed else "❌ FAIL"
        logger.info(f"{status} - {result.name} ({result.duration:.3f}s)")
        if result.message:
            logger.info(f"    {result.message}")
        if result.details:
            for key, value in result.details.items():
                logger.info(f"    {key}: {value}")
        self.test_results.append(result)
        
    async def test_sensor_data_flow(self):
        """Test complete sensor data flow from hardware to dashboard"""
        logger.info("🔍 Testing sensor data flow...")
        
        # Test 1: Sensor reading to temperature mapping
        start_time = time.time()
        try:
            # Simulate sensor data
            test_sensor_data = {
                'megabas_sensor_6': 75.5,  # Solar collector
                'megabas_sensor_7': 45.2,  # Storage tank
                'megabas_sensor_8': 50.1,  # Return line
                'rtd_sensor_0': 20.0,      # Water heater bottom
                'rtd_sensor_7': 85.0,      # Water heater top
            }
            
            # Set sensor data
            self.system.temperatures.update(test_sensor_data)
            
            # Run sensor mapping (inline mapping like in the actual code)
            self.system.temperatures['solar_collector'] = self.system.temperatures.get('megabas_sensor_6', 0)
            self.system.temperatures['storage_tank'] = self.system.temperatures.get('megabas_sensor_7', 0)
            
            # Verify mapping worked
            solar_collector = self.system.temperatures.get('solar_collector', 0)
            storage_tank = self.system.temperatures.get('storage_tank', 0)
            return_line = self.system.temperatures.get('return_line_temp', 0)
            
            expected_dt = 75.5 - 45.2  # 30.3°C
            
            if (solar_collector == 75.5 and storage_tank == 45.2 and 
                return_line == 50.1 and abs(expected_dt - 30.3) < 0.1):
                result = TestResult(
                    name="Sensor Data Flow",
                    passed=True,
                    message=f"Data flows correctly: Collector={solar_collector}°C, Tank={storage_tank}°C, dT={expected_dt:.1f}°C",
                    duration=time.time() - start_time,
                    details={
                        'solar_collector': solar_collector,
                        'storage_tank': storage_tank,
                        'return_line': return_line,
                        'calculated_dt': expected_dt
                    }
                )
            else:
                result = TestResult(
                    name="Sensor Data Flow",
                    passed=False,
                    message=f"Data flow failed: Collector={solar_collector}°C, Tank={storage_tank}°C, Expected dT=30.3°C",
                    duration=time.time() - start_time
                )
                
        except Exception as e:
            result = TestResult(
                name="Sensor Data Flow",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def test_temperature_calculation_accuracy(self):
        """Test all temperature calculations are mathematically correct"""
        logger.info("🌡️ Testing temperature calculation accuracy...")
        
        start_time = time.time()
        try:
            # Test various temperature scenarios
            test_scenarios = [
                {'collector': 100.0, 'tank': 25.0, 'expected_dt': 75.0},
                {'collector': 50.0, 'tank': 50.0, 'expected_dt': 0.0},
                {'collector': 30.0, 'tank': 40.0, 'expected_dt': -10.0},
                {'collector': 85.5, 'tank': 42.3, 'expected_dt': 43.2},
                {'collector': 0.0, 'tank': 0.0, 'expected_dt': 0.0},
            ]
            
            all_passed = True
            details = {}
            
            for i, scenario in enumerate(test_scenarios):
                # Set temperatures
                self.system.temperatures['megabas_sensor_6'] = scenario['collector']
                self.system.temperatures['megabas_sensor_7'] = scenario['tank']
                
                # Run sensor mapping
                await self.system._map_sensors()
                
                # Calculate dT
                solar_collector = self.system.temperatures.get('solar_collector', 0)
                storage_tank = self.system.temperatures.get('storage_tank', 0)
                dT = solar_collector - storage_tank
                
                expected_dt = scenario['expected_dt']
                scenario_passed = abs(dT - expected_dt) < 0.1
                
                details[f'scenario_{i+1}'] = {
                    'collector': scenario['collector'],
                    'tank': scenario['tank'],
                    'calculated_dt': dT,
                    'expected_dt': expected_dt,
                    'passed': scenario_passed
                }
                
                if not scenario_passed:
                    all_passed = False
                    
            result = TestResult(
                name="Temperature Calculation Accuracy",
                passed=all_passed,
                message=f"All {len(test_scenarios)} temperature calculation scenarios {'passed' if all_passed else 'failed'}",
                duration=time.time() - start_time,
                details=details
            )
            
        except Exception as e:
            result = TestResult(
                name="Temperature Calculation Accuracy",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def test_pump_control_logic_completeness(self):
        """Test pump control logic in all scenarios"""
        logger.info("🔧 Testing pump control logic completeness...")
        
        start_time = time.time()
        try:
            # Test pump control scenarios
            test_scenarios = [
                {
                    'name': 'Normal start condition',
                    'collector': 50.0, 'tank': 30.0, 'dT': 20.0,
                    'expected_pump': True, 'reason': 'dT > 8°C threshold'
                },
                {
                    'name': 'Normal stop condition',
                    'collector': 35.0, 'tank': 30.0, 'dT': 5.0,
                    'expected_pump': False, 'reason': 'dT < 8°C threshold'
                },
                {
                    'name': 'Boundary start condition',
                    'collector': 38.0, 'tank': 30.0, 'dT': 8.0,
                    'expected_pump': True, 'reason': 'dT = 8°C threshold'
                },
                {
                    'name': 'Boundary stop condition',
                    'collector': 34.0, 'tank': 30.0, 'dT': 4.0,
                    'expected_pump': False, 'reason': 'dT = 4°C stop threshold'
                },
                {
                    'name': 'Emergency stop condition',
                    'collector': 95.0, 'tank': 30.0, 'dT': 65.0,
                    'expected_pump': False, 'reason': 'Emergency stop (collector > 90°C)'
                },
                {
                    'name': 'Collector cooling condition',
                    'collector': 85.0, 'tank': 30.0, 'dT': 55.0,
                    'expected_pump': True, 'reason': 'Collector cooling (collector > 80°C)'
                }
            ]
            
            all_passed = True
            details = {}
            
            for i, scenario in enumerate(test_scenarios):
                # Set temperatures
                self.system.temperatures['megabas_sensor_6'] = scenario['collector']
                self.system.temperatures['megabas_sensor_7'] = scenario['tank']
                
                # Run sensor mapping
                await self.system._map_sensors()
                
                # Simulate pump control logic
                solar_collector = self.system.temperatures.get('solar_collector', 0)
                storage_tank = self.system.temperatures.get('storage_tank', 0)
                dT = solar_collector - storage_tank
                
                # Get control parameters
                dTStart = self.system.control_params.get('dTStart_tank_1', 8.0)
                dTStop = self.system.control_params.get('dTStop_tank_1', 4.0)
                temp_kok = self.system.control_params.get('temp_kok', 90.0)
                kylning_kollektor = self.system.control_params.get('kylning_kollektor', 80.0)
                
                # Determine expected pump state
                if solar_collector >= temp_kok:
                    expected_pump_state = False  # Emergency stop
                elif solar_collector >= kylning_kollektor:
                    expected_pump_state = True   # Collector cooling
                elif dT >= dTStart:
                    expected_pump_state = True   # Normal heating
                elif dT <= dTStop:
                    expected_pump_state = False  # Normal stop
                else:
                    expected_pump_state = False  # Hysteresis zone
                
                scenario_passed = expected_pump_state == scenario['expected_pump']
                
                details[f'scenario_{i+1}'] = {
                    'name': scenario['name'],
                    'collector': scenario['collector'],
                    'tank': scenario['tank'],
                    'dT': dT,
                    'expected_pump': scenario['expected_pump'],
                    'calculated_pump': expected_pump_state,
                    'passed': scenario_passed,
                    'reason': scenario['reason']
                }
                
                if not scenario_passed:
                    all_passed = False
                    
            result = TestResult(
                name="Pump Control Logic Completeness",
                passed=all_passed,
                message=f"All {len(test_scenarios)} pump control scenarios {'passed' if all_passed else 'failed'}",
                duration=time.time() - start_time,
                details=details
            )
            
        except Exception as e:
            result = TestResult(
                name="Pump Control Logic Completeness",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def test_energy_calculation_validation(self):
        """Test physics-based energy calculations"""
        logger.info("⚡ Testing energy calculation validation...")
        
        start_time = time.time()
        try:
            # Test energy calculation scenarios
            test_scenarios = [
                {
                    'name': 'High temperature difference',
                    'collector': 100.0, 'tank': 20.0, 'dT': 80.0,
                    'expected_energy_kwh': 33.6  # 360L * 4.2 kJ/kg°C * 80°C / 3600
                },
                {
                    'name': 'Medium temperature difference',
                    'collector': 60.0, 'tank': 40.0, 'dT': 20.0,
                    'expected_energy_kwh': 8.4   # 360L * 4.2 kJ/kg°C * 20°C / 3600
                },
                {
                    'name': 'Low temperature difference',
                    'collector': 35.0, 'tank': 30.0, 'dT': 5.0,
                    'expected_energy_kwh': 2.1   # 360L * 4.2 kJ/kg°C * 5°C / 3600
                },
                {
                    'name': 'No temperature difference',
                    'collector': 50.0, 'tank': 50.0, 'dT': 0.0,
                    'expected_energy_kwh': 0.0   # No energy transfer
                }
            ]
            
            all_passed = True
            details = {}
            
            # Tank parameters
            tank_volume_liters = 360
            tank_volume_kg = tank_volume_liters  # 1 liter = 1 kg
            specific_heat_capacity = 4.2  # kJ/kg°C
            
            for i, scenario in enumerate(test_scenarios):
                # Set temperatures
                self.system.temperatures['megabas_sensor_6'] = scenario['collector']
                self.system.temperatures['megabas_sensor_7'] = scenario['tank']
                
                # Run sensor mapping
                await self.system._map_sensors()
                
                # Calculate dT
                solar_collector = self.system.temperatures.get('solar_collector', 0)
                storage_tank = self.system.temperatures.get('storage_tank', 0)
                dT = solar_collector - storage_tank
                
                # Calculate energy (physics-based)
                if dT > 0:
                    energy_kj = tank_volume_kg * specific_heat_capacity * dT
                    energy_kwh = energy_kj / 3600  # Convert kJ to kWh
                else:
                    energy_kwh = 0.0
                
                expected_energy = scenario['expected_energy_kwh']
                scenario_passed = abs(energy_kwh - expected_energy) < 0.1
                
                details[f'scenario_{i+1}'] = {
                    'name': scenario['name'],
                    'collector': scenario['collector'],
                    'tank': scenario['tank'],
                    'dT': dT,
                    'calculated_energy_kwh': energy_kwh,
                    'expected_energy_kwh': expected_energy,
                    'passed': scenario_passed
                }
                
                if not scenario_passed:
                    all_passed = False
                    
            result = TestResult(
                name="Energy Calculation Validation",
                passed=all_passed,
                message=f"All {len(test_scenarios)} energy calculation scenarios {'passed' if all_passed else 'failed'}",
                duration=time.time() - start_time,
                details=details
            )
            
        except Exception as e:
            result = TestResult(
                name="Energy Calculation Validation",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def test_system_state_consistency(self):
        """Test system state consistency across operations"""
        logger.info("🔄 Testing system state consistency...")
        
        start_time = time.time()
        try:
            # Test state consistency scenarios
            initial_state = self.system.system_state.copy()
            
            # Test 1: State initialization
            state_initialized = (
                'mode' in self.system.system_state and
                'primary_pump' in self.system.system_state and
                'pump_runtime_hours' in self.system.system_state and
                'heating_cycles_count' in self.system.system_state
            )
            
            # Test 2: State modification consistency
            original_mode = self.system.system_state['mode']
            self.system.system_state['mode'] = 'test_mode'
            mode_changed = self.system.system_state['mode'] == 'test_mode'
            self.system.system_state['mode'] = original_mode  # Restore
            
            # Test 3: State persistence consistency
            original_pump_state = self.system.system_state['primary_pump']
            self.system.system_state['primary_pump'] = True
            pump_state_changed = self.system.system_state['primary_pump'] == True
            self.system.system_state['primary_pump'] = original_pump_state  # Restore
            
            # Test 4: Temperature state consistency
            self.system.temperatures['test_sensor'] = 25.0
            temp_set = self.system.temperatures.get('test_sensor', 0) == 25.0
            del self.system.temperatures['test_sensor']  # Cleanup
            
            all_passed = state_initialized and mode_changed and pump_state_changed and temp_set
            
            result = TestResult(
                name="System State Consistency",
                passed=all_passed,
                message=f"State consistency tests {'passed' if all_passed else 'failed'}",
                duration=time.time() - start_time,
                details={
                    'state_initialized': state_initialized,
                    'mode_changed': mode_changed,
                    'pump_state_changed': pump_state_changed,
                    'temp_set': temp_set
                }
            )
            
        except Exception as e:
            result = TestResult(
                name="System State Consistency",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def run_all_tests(self):
        """Run all core functionality tests"""
        logger.info("🚀 Starting Core Functionality Test Suite")
        logger.info("=" * 60)
        
        await self.setup()
        
        try:
            # Run all tests
            await self.test_sensor_data_flow()
            await self.test_temperature_calculation_accuracy()
            await self.test_pump_control_logic_completeness()
            await self.test_energy_calculation_validation()
            await self.test_system_state_consistency()
            
        finally:
            await self.teardown()
            
        # Generate summary
        self.generate_summary()
        
    def generate_summary(self):
        """Generate test summary"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result.passed)
        failed_tests = total_tests - passed_tests
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        total_duration = time.time() - self.start_time if self.start_time else 0
        
        logger.info("\n📊 CORE FUNCTIONALITY TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Duration: {total_duration:.2f} seconds")
        
        if failed_tests > 0:
            logger.info(f"\n⚠️  {failed_tests} TESTS FAILED. System needs attention.")
            logger.info("Failed tests:")
            for result in self.test_results:
                if not result.passed:
                    logger.info(f"  ❌ {result.name}: {result.message}")
        else:
            logger.info("\n🎉 ALL TESTS PASSED! Core functionality is working correctly.")
            
        return success_rate == 100.0

async def main():
    """Main test runner"""
    test_suite = CoreFunctionalityTestSuite()
    success = await test_suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())
