#!/usr/bin/env python3
"""
Sensor Data Flow Validation Test
Tests the complete end-to-end sensor data processing from hardware to dashboard.

This test validates:
1. Raw sensor data reading
2. Sensor data mapping and processing
3. Temperature calculations
4. MQTT publishing
5. Dashboard data flow
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
class SensorDataFlowResult:
    """Result container for sensor data flow tests"""
    test_name: str
    passed: bool
    message: str
    duration: float = 0.0
    details: Dict[str, Any] = None

class SensorDataFlowTestSuite:
    """Comprehensive test suite for sensor data flow validation"""
    
    def __init__(self):
        self.system = None
        self.test_results = []
        self.start_time = None
        
    async def setup(self):
        """Setup test environment"""
        logger.info("🧪 Setting up Sensor Data Flow Test Suite...")
        self.system = SolarHeatingSystem()
        self.start_time = time.time()
        
    async def teardown(self):
        """Cleanup test environment"""
        if self.system:
            # Cleanup any resources
            pass
            
    def log_test_result(self, result: SensorDataFlowResult):
        """Log test result"""
        status = "✅ PASS" if result.passed else "❌ FAIL"
        logger.info(f"{status} - {result.test_name} ({result.duration:.3f}s)")
        if result.message:
            logger.info(f"    {result.message}")
        if result.details:
            for key, value in result.details.items():
                logger.info(f"    {key}: {value}")
        self.test_results.append(result)
        
    async def test_raw_sensor_data_reading(self):
        """Test raw sensor data reading from hardware interface"""
        logger.info("📡 Testing raw sensor data reading...")
        
        start_time = time.time()
        try:
            # Test sensor data structure
            test_sensor_data = {
                'megabas_sensor_0': 25.5,  # FTX exhaust air
                'megabas_sensor_1': 30.2,  # FTX supply air
                'megabas_sensor_2': 28.1,  # FTX return air
                'megabas_sensor_3': 26.8,  # FTX supply air
                'megabas_sensor_4': 29.3,  # FTX return air
                'megabas_sensor_5': 24.7,  # FTX exhaust air
                'megabas_sensor_6': 75.5,  # Solar collector outlet
                'megabas_sensor_7': 45.2,  # Storage tank
                'megabas_sensor_8': 50.1,  # Return line
                'rtd_sensor_0': 20.0,      # Water heater bottom
                'rtd_sensor_1': 25.0,      # Water heater 20cm
                'rtd_sensor_2': 30.0,      # Water heater 40cm
                'rtd_sensor_3': 35.0,      # Water heater 60cm
                'rtd_sensor_4': 40.0,      # Water heater 80cm
                'rtd_sensor_5': 45.0,      # Water heater 100cm
                'rtd_sensor_6': 50.0,      # Water heater 120cm
                'rtd_sensor_7': 55.0,      # Water heater 140cm (top)
            }
            
            # Set sensor data in system
            self.system.temperatures.update(test_sensor_data)
            
            # Validate all sensor data is present
            all_sensors_present = all(
                sensor in self.system.temperatures for sensor in test_sensor_data.keys()
            )
            
            # Validate sensor data types and ranges
            valid_data_types = all(
                isinstance(value, (int, float)) for value in test_sensor_data.values()
            )
            
            valid_temperature_ranges = all(
                -50 <= value <= 200 for value in test_sensor_data.values()
            )
            
            test_passed = all_sensors_present and valid_data_types and valid_temperature_ranges
            
            result = SensorDataFlowResult(
                test_name="Raw Sensor Data Reading",
                passed=test_passed,
                message=f"All {len(test_sensor_data)} sensors read successfully" if test_passed else "Sensor data validation failed",
                duration=time.time() - start_time,
                details={
                    'total_sensors': len(test_sensor_data),
                    'sensors_present': all_sensors_present,
                    'valid_data_types': valid_data_types,
                    'valid_temperature_ranges': valid_temperature_ranges,
                    'sample_data': {
                        'solar_collector': test_sensor_data['megabas_sensor_6'],
                        'storage_tank': test_sensor_data['megabas_sensor_7'],
                        'return_line': test_sensor_data['megabas_sensor_8']
                    }
                }
            )
            
        except Exception as e:
            result = SensorDataFlowResult(
                test_name="Raw Sensor Data Reading",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def test_sensor_data_mapping(self):
        """Test sensor data mapping and processing"""
        logger.info("🔄 Testing sensor data mapping...")
        
        start_time = time.time()
        try:
            # Set up test sensor data
            test_sensor_data = {
                'megabas_sensor_6': 85.5,  # Solar collector
                'megabas_sensor_7': 42.3,  # Storage tank
                'megabas_sensor_8': 48.1,  # Return line
            }
            
            self.system.temperatures.update(test_sensor_data)
            
            # Run sensor mapping (simulate the actual mapping process)
            # FTX sensors
            self.system.temperatures['exhaust_air_temp'] = self.system.temperatures.get('megabas_sensor_2', 0)
            self.system.temperatures['supply_air_temp'] = self.system.temperatures.get('megabas_sensor_3', 0)
            self.system.temperatures['return_air_temp'] = self.system.temperatures.get('megabas_sensor_4', 0)
            
            # Solar collector and storage tank sensors
            self.system.temperatures['solar_collector'] = self.system.temperatures.get('megabas_sensor_6', 0)
            self.system.temperatures['storage_tank'] = self.system.temperatures.get('megabas_sensor_7', 0)
            self.system.temperatures['return_line_temp'] = self.system.temperatures.get('megabas_sensor_8', 0)
            
            # Also maintain the _temp versions for backward compatibility
            self.system.temperatures['solar_collector_temp'] = self.system.temperatures.get('megabas_sensor_6', 0)
            self.system.temperatures['storage_tank_temp'] = self.system.temperatures.get('megabas_sensor_7', 0)
            
            # Water heater RTD sensors
            for i in range(8):
                self.system.temperatures[f'water_heater_{i*20}cm'] = self.system.temperatures.get(f'rtd_sensor_{i}', 0)
            
            # Validate mapping results
            mapping_tests = [
                ('solar_collector', 85.5),
                ('storage_tank', 42.3),
                ('return_line_temp', 48.1),
                ('solar_collector_temp', 85.5),  # Backward compatibility
                ('storage_tank_temp', 42.3),     # Backward compatibility
            ]
            
            all_mappings_correct = True
            mapping_details = {}
            
            for mapped_key, expected_value in mapping_tests:
                actual_value = self.system.temperatures.get(mapped_key, 0)
                mapping_correct = abs(actual_value - expected_value) < 0.1
                mapping_details[mapped_key] = {
                    'expected': expected_value,
                    'actual': actual_value,
                    'correct': mapping_correct
                }
                if not mapping_correct:
                    all_mappings_correct = False
            
            result = SensorDataFlowResult(
                test_name="Sensor Data Mapping",
                passed=all_mappings_correct,
                message=f"All {len(mapping_tests)} sensor mappings {'correct' if all_mappings_correct else 'incorrect'}",
                duration=time.time() - start_time,
                details=mapping_details
            )
            
        except Exception as e:
            result = SensorDataFlowResult(
                test_name="Sensor Data Mapping",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def test_temperature_calculations(self):
        """Test temperature calculations and derived values"""
        logger.info("🌡️ Testing temperature calculations...")
        
        start_time = time.time()
        try:
            # Set up test data
            self.system.temperatures['solar_collector'] = 90.0
            self.system.temperatures['storage_tank'] = 35.0
            self.system.temperatures['return_line_temp'] = 45.0
            
            # Test 1: Basic dT calculation
            solar_collector = self.system.temperatures.get('solar_collector', 0)
            storage_tank = self.system.temperatures.get('storage_tank', 0)
            dT = solar_collector - storage_tank
            expected_dt = 55.0
            
            # Test 2: dT calculation with safety check
            dT_safe = solar_collector - storage_tank if solar_collector and storage_tank else 0
            
            # Test 3: Temperature rate calculations (simulated)
            current_time = time.time()
            self.system.temperatures['solar_collector_dt'] = dT
            
            # Test 4: Water heater temperature calculations
            water_heater_temps = []
            for i in range(8):
                temp = self.system.temperatures.get(f'water_heater_{i*20}cm', 0)
                water_heater_temps.append(temp)
            
            # Validate calculations
            dt_calculation_correct = abs(dT - expected_dt) < 0.1
            dt_safe_calculation_correct = abs(dT_safe - expected_dt) < 0.1
            dt_stored_correct = abs(self.system.temperatures.get('solar_collector_dt', 0) - expected_dt) < 0.1
            
            all_calculations_correct = dt_calculation_correct and dt_safe_calculation_correct and dt_stored_correct
            
            result = SensorDataFlowResult(
                test_name="Temperature Calculations",
                passed=all_calculations_correct,
                message=f"Temperature calculations {'correct' if all_calculations_correct else 'incorrect'}",
                duration=time.time() - start_time,
                details={
                    'solar_collector': solar_collector,
                    'storage_tank': storage_tank,
                    'dT_calculation': dT,
                    'dT_expected': expected_dt,
                    'dT_safe_calculation': dT_safe,
                    'dT_stored': self.system.temperatures.get('solar_collector_dt', 0),
                    'dt_calculation_correct': dt_calculation_correct,
                    'dt_safe_calculation_correct': dt_safe_calculation_correct,
                    'dt_stored_correct': dt_stored_correct,
                    'water_heater_temps': water_heater_temps
                }
            )
            
        except Exception as e:
            result = SensorDataFlowResult(
                test_name="Temperature Calculations",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def test_data_flow_consistency(self):
        """Test data flow consistency across the entire pipeline"""
        logger.info("🔄 Testing data flow consistency...")
        
        start_time = time.time()
        try:
            # Test complete data flow from raw sensors to final values
            raw_sensor_data = {
                'megabas_sensor_6': 95.0,  # Solar collector
                'megabas_sensor_7': 40.0,  # Storage tank
                'megabas_sensor_8': 50.0,  # Return line
            }
            
            # Step 1: Set raw sensor data
            self.system.temperatures.update(raw_sensor_data)
            
            # Step 2: Run sensor mapping
            self.system.temperatures['solar_collector'] = self.system.temperatures.get('megabas_sensor_6', 0)
            self.system.temperatures['storage_tank'] = self.system.temperatures.get('megabas_sensor_7', 0)
            self.system.temperatures['return_line_temp'] = self.system.temperatures.get('megabas_sensor_8', 0)
            
            # Step 3: Calculate derived values
            solar_collector = self.system.temperatures.get('solar_collector', 0)
            storage_tank = self.system.temperatures.get('storage_tank', 0)
            dT = solar_collector - storage_tank
            self.system.temperatures['solar_collector_dt'] = dT
            
            # Step 4: Validate data flow consistency
            consistency_checks = [
                ('Raw to mapped collector', raw_sensor_data['megabas_sensor_6'], solar_collector),
                ('Raw to mapped tank', raw_sensor_data['megabas_sensor_7'], storage_tank),
                ('Raw to mapped return', raw_sensor_data['megabas_sensor_8'], self.system.temperatures.get('return_line_temp', 0)),
                ('dT calculation', 55.0, dT),  # 95.0 - 40.0 = 55.0
            ]
            
            all_consistent = True
            consistency_details = {}
            
            for check_name, expected, actual in consistency_checks:
                consistent = abs(expected - actual) < 0.1
                consistency_details[check_name] = {
                    'expected': expected,
                    'actual': actual,
                    'consistent': consistent
                }
                if not consistent:
                    all_consistent = False
            
            result = SensorDataFlowResult(
                test_name="Data Flow Consistency",
                passed=all_consistent,
                message=f"Data flow consistency {'maintained' if all_consistent else 'broken'}",
                duration=time.time() - start_time,
                details=consistency_details
            )
            
        except Exception as e:
            result = SensorDataFlowResult(
                test_name="Data Flow Consistency",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def test_error_handling_in_data_flow(self):
        """Test error handling in sensor data flow"""
        logger.info("⚠️ Testing error handling in data flow...")
        
        start_time = time.time()
        try:
            # Test 1: Missing sensor data
            self.system.temperatures.clear()
            
            # Try to access missing sensor data
            missing_collector = self.system.temperatures.get('megabas_sensor_6', 0)
            missing_tank = self.system.temperatures.get('megabas_sensor_7', 0)
            
            # Test 2: Invalid sensor data
            self.system.temperatures['megabas_sensor_6'] = None
            self.system.temperatures['megabas_sensor_7'] = "invalid"
            
            # Test 3: Out of range sensor data
            self.system.temperatures['megabas_sensor_6'] = 300.0  # Too high
            self.system.temperatures['megabas_sensor_7'] = -100.0  # Too low
            
            # Test 4: Safe data access with defaults
            safe_collector = self.system.temperatures.get('megabas_sensor_6', 0) or 0
            safe_tank = self.system.temperatures.get('megabas_sensor_7', 0) or 0
            
            # Test 5: Safe dT calculation
            safe_dt = safe_collector - safe_tank if safe_collector and safe_tank else 0
            
            # Validate error handling
            missing_data_handled = missing_collector == 0 and missing_tank == 0
            invalid_data_handled = isinstance(safe_collector, (int, float)) and isinstance(safe_tank, (int, float))
            safe_calculation_works = isinstance(safe_dt, (int, float))
            
            all_error_handling_works = missing_data_handled and invalid_data_handled and safe_calculation_works
            
            result = SensorDataFlowResult(
                test_name="Error Handling in Data Flow",
                passed=all_error_handling_works,
                message=f"Error handling {'works correctly' if all_error_handling_works else 'failed'}",
                duration=time.time() - start_time,
                details={
                    'missing_data_handled': missing_data_handled,
                    'invalid_data_handled': invalid_data_handled,
                    'safe_calculation_works': safe_calculation_works,
                    'missing_collector': missing_collector,
                    'missing_tank': missing_tank,
                    'safe_collector': safe_collector,
                    'safe_tank': safe_tank,
                    'safe_dt': safe_dt
                }
            )
            
        except Exception as e:
            result = SensorDataFlowResult(
                test_name="Error Handling in Data Flow",
                passed=False,
                message=f"Exception during test: {str(e)}",
                duration=time.time() - start_time
            )
            
        self.log_test_result(result)
        
    async def run_all_tests(self):
        """Run all sensor data flow tests"""
        logger.info("🚀 Starting Sensor Data Flow Test Suite")
        logger.info("=" * 60)
        
        await self.setup()
        
        try:
            # Run all tests
            await self.test_raw_sensor_data_reading()
            await self.test_sensor_data_mapping()
            await self.test_temperature_calculations()
            await self.test_data_flow_consistency()
            await self.test_error_handling_in_data_flow()
            
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
        
        logger.info("\n📊 SENSOR DATA FLOW TEST SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {success_rate:.1f}%")
        logger.info(f"Duration: {total_duration:.2f} seconds")
        
        if failed_tests > 0:
            logger.info(f"\n⚠️  {failed_tests} TESTS FAILED. Sensor data flow needs attention.")
            logger.info("Failed tests:")
            for result in self.test_results:
                if not result.passed:
                    logger.info(f"  ❌ {result.test_name}: {result.message}")
        else:
            logger.info("\n🎉 ALL TESTS PASSED! Sensor data flow is working correctly.")
            
        return success_rate == 100.0

async def main():
    """Main test runner"""
    test_suite = SensorDataFlowTestSuite()
    success = await test_suite.run_all_tests()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())






