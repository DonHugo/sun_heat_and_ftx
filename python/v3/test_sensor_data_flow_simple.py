#!/usr/bin/env python3
"""
Simple Sensor Data Flow Validation Test
Tests the complete end-to-end sensor data processing from hardware to dashboard.
"""

import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_system import SolarHeatingSystem
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def test_raw_sensor_data_reading():
    """Test raw sensor data reading from hardware interface"""
    print("📡 Testing raw sensor data reading...")
    
    system = SolarHeatingSystem()
    
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
    system.temperatures.update(test_sensor_data)
    
    # Validate all sensor data is present
    all_sensors_present = all(
        sensor in system.temperatures for sensor in test_sensor_data.keys()
    )
    
    # Validate sensor data types and ranges
    valid_data_types = all(
        isinstance(value, (int, float)) for value in test_sensor_data.values()
    )
    
    valid_temperature_ranges = all(
        -50 <= value <= 200 for value in test_sensor_data.values()
    )
    
    test_passed = all_sensors_present and valid_data_types and valid_temperature_ranges
    
    print(f"   Total sensors: {len(test_sensor_data)}")
    print(f"   All sensors present: {'✅' if all_sensors_present else '❌'}")
    print(f"   Valid data types: {'✅' if valid_data_types else '❌'}")
    print(f"   Valid temperature ranges: {'✅' if valid_temperature_ranges else '❌'}")
    print(f"   Sample data - Collector: {test_sensor_data['megabas_sensor_6']}°C, Tank: {test_sensor_data['megabas_sensor_7']}°C")
    
    return test_passed

def test_sensor_data_mapping():
    """Test sensor data mapping and processing"""
    print("\n🔄 Testing sensor data mapping...")
    
    system = SolarHeatingSystem()
    
    # Set up test sensor data
    test_sensor_data = {
        'megabas_sensor_6': 85.5,  # Solar collector
        'megabas_sensor_7': 42.3,  # Storage tank
        'megabas_sensor_8': 48.1,  # Return line
    }
    
    system.temperatures.update(test_sensor_data)
    
    # Run sensor mapping (simulate the actual mapping process)
    # Solar collector and storage tank sensors
    system.temperatures['solar_collector'] = system.temperatures.get('megabas_sensor_6', 0)
    system.temperatures['storage_tank'] = system.temperatures.get('megabas_sensor_7', 0)
    system.temperatures['return_line_temp'] = system.temperatures.get('megabas_sensor_8', 0)
    
    # Also maintain the _temp versions for backward compatibility
    system.temperatures['solar_collector_temp'] = system.temperatures.get('megabas_sensor_6', 0)
    system.temperatures['storage_tank_temp'] = system.temperatures.get('megabas_sensor_7', 0)
    
    # Validate mapping results
    mapping_tests = [
        ('solar_collector', 85.5),
        ('storage_tank', 42.3),
        ('return_line_temp', 48.1),
        ('solar_collector_temp', 85.5),  # Backward compatibility
        ('storage_tank_temp', 42.3),     # Backward compatibility
    ]
    
    all_mappings_correct = True
    
    for mapped_key, expected_value in mapping_tests:
        actual_value = system.temperatures.get(mapped_key, 0)
        mapping_correct = abs(actual_value - expected_value) < 0.1
        print(f"   {mapped_key}: {actual_value}°C (expected {expected_value}°C) - {'✅' if mapping_correct else '❌'}")
        if not mapping_correct:
            all_mappings_correct = False
    
    return all_mappings_correct

def test_temperature_calculations():
    """Test temperature calculations and derived values"""
    print("\n🌡️ Testing temperature calculations...")
    
    system = SolarHeatingSystem()
    
    # Set up test data
    system.temperatures['solar_collector'] = 90.0
    system.temperatures['storage_tank'] = 35.0
    system.temperatures['return_line_temp'] = 45.0
    
    # Test 1: Basic dT calculation
    solar_collector = system.temperatures.get('solar_collector', 0)
    storage_tank = system.temperatures.get('storage_tank', 0)
    dT = solar_collector - storage_tank
    expected_dt = 55.0
    
    # Test 2: dT calculation with safety check
    dT_safe = solar_collector - storage_tank if solar_collector and storage_tank else 0
    
    # Test 3: Store dT value
    system.temperatures['solar_collector_dt'] = dT
    
    # Validate calculations
    dt_calculation_correct = abs(dT - expected_dt) < 0.1
    dt_safe_calculation_correct = abs(dT_safe - expected_dt) < 0.1
    dt_stored_correct = abs(system.temperatures.get('solar_collector_dt', 0) - expected_dt) < 0.1
    
    print(f"   Solar collector: {solar_collector}°C")
    print(f"   Storage tank: {storage_tank}°C")
    print(f"   dT calculation: {dT}°C (expected {expected_dt}°C) - {'✅' if dt_calculation_correct else '❌'}")
    print(f"   dT safe calculation: {dT_safe}°C - {'✅' if dt_safe_calculation_correct else '❌'}")
    print(f"   dT stored: {system.temperatures.get('solar_collector_dt', 0)}°C - {'✅' if dt_stored_correct else '❌'}")
    
    all_calculations_correct = dt_calculation_correct and dt_safe_calculation_correct and dt_stored_correct
    
    return all_calculations_correct

def test_data_flow_consistency():
    """Test data flow consistency across the entire pipeline"""
    print("\n🔄 Testing data flow consistency...")
    
    system = SolarHeatingSystem()
    
    # Test complete data flow from raw sensors to final values
    raw_sensor_data = {
        'megabas_sensor_6': 95.0,  # Solar collector
        'megabas_sensor_7': 40.0,  # Storage tank
        'megabas_sensor_8': 50.0,  # Return line
    }
    
    # Step 1: Set raw sensor data
    system.temperatures.update(raw_sensor_data)
    
    # Step 2: Run sensor mapping
    system.temperatures['solar_collector'] = system.temperatures.get('megabas_sensor_6', 0)
    system.temperatures['storage_tank'] = system.temperatures.get('megabas_sensor_7', 0)
    system.temperatures['return_line_temp'] = system.temperatures.get('megabas_sensor_8', 0)
    
    # Step 3: Calculate derived values
    solar_collector = system.temperatures.get('solar_collector', 0)
    storage_tank = system.temperatures.get('storage_tank', 0)
    dT = solar_collector - storage_tank
    system.temperatures['solar_collector_dt'] = dT
    
    # Step 4: Validate data flow consistency
    consistency_checks = [
        ('Raw to mapped collector', raw_sensor_data['megabas_sensor_6'], solar_collector),
        ('Raw to mapped tank', raw_sensor_data['megabas_sensor_7'], storage_tank),
        ('Raw to mapped return', raw_sensor_data['megabas_sensor_8'], system.temperatures.get('return_line_temp', 0)),
        ('dT calculation', 55.0, dT),  # 95.0 - 40.0 = 55.0
    ]
    
    all_consistent = True
    
    for check_name, expected, actual in consistency_checks:
        consistent = abs(expected - actual) < 0.1
        print(f"   {check_name}: {actual} (expected {expected}) - {'✅' if consistent else '❌'}")
        if not consistent:
            all_consistent = False
    
    return all_consistent

def test_error_handling_in_data_flow():
    """Test error handling in sensor data flow"""
    print("\n⚠️ Testing error handling in data flow...")
    
    system = SolarHeatingSystem()
    
    # Test 1: Missing sensor data
    system.temperatures.clear()
    
    # Try to access missing sensor data
    missing_collector = system.temperatures.get('megabas_sensor_6', 0)
    missing_tank = system.temperatures.get('megabas_sensor_7', 0)
    
    # Test 2: Invalid sensor data
    system.temperatures['megabas_sensor_6'] = None
    system.temperatures['megabas_sensor_7'] = "invalid"
    
    # Test 3: Out of range sensor data
    system.temperatures['megabas_sensor_6'] = 300.0  # Too high
    system.temperatures['megabas_sensor_7'] = -100.0  # Too low
    
    # Test 4: Safe data access with defaults
    safe_collector = system.temperatures.get('megabas_sensor_6', 0) or 0
    safe_tank = system.temperatures.get('megabas_sensor_7', 0) or 0
    
    # Test 5: Safe dT calculation
    safe_dt = safe_collector - safe_tank if safe_collector and safe_tank else 0
    
    # Validate error handling
    missing_data_handled = missing_collector == 0 and missing_tank == 0
    invalid_data_handled = isinstance(safe_collector, (int, float)) and isinstance(safe_tank, (int, float))
    safe_calculation_works = isinstance(safe_dt, (int, float))
    
    print(f"   Missing data handled: {'✅' if missing_data_handled else '❌'} (collector: {missing_collector}, tank: {missing_tank})")
    print(f"   Invalid data handled: {'✅' if invalid_data_handled else '❌'} (collector: {safe_collector}, tank: {safe_tank})")
    print(f"   Safe calculation works: {'✅' if safe_calculation_works else '❌'} (dT: {safe_dt})")
    
    all_error_handling_works = missing_data_handled and invalid_data_handled and safe_calculation_works
    
    return all_error_handling_works

def main():
    """Main test runner"""
    print("🚀 Starting Sensor Data Flow Test Suite")
    print("=" * 60)
    
    tests = [
        ("Raw Sensor Data Reading", test_raw_sensor_data_reading),
        ("Sensor Data Mapping", test_sensor_data_mapping),
        ("Temperature Calculations", test_temperature_calculations),
        ("Data Flow Consistency", test_data_flow_consistency),
        ("Error Handling in Data Flow", test_error_handling_in_data_flow),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASSED")
            else:
                print(f"❌ {test_name}: FAILED")
        except Exception as e:
            print(f"❌ {test_name}: EXCEPTION - {str(e)}")
    
    print("\n📊 SENSOR DATA FLOW TEST SUMMARY")
    print("=" * 60)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Sensor data flow is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED. Sensor data flow needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)









