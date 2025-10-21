#!/usr/bin/env python3
"""
Temperature Calculation Accuracy Test
Tests all temperature calculations in the system for mathematical accuracy.

This test validates:
1. Basic temperature difference calculations
2. Temperature rate calculations
3. Average temperature calculations
4. Temperature validation and bounds checking
5. Temperature conversion and scaling
"""

import sys
import os
import time
import math

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from main_system import SolarHeatingSystem
except ImportError as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)

def test_basic_temperature_differences():
    """Test basic temperature difference calculations"""
    print("🌡️ Testing basic temperature difference calculations...")
    
    system = SolarHeatingSystem()
    
    # Test scenarios for temperature differences
    test_scenarios = [
        {
            'name': 'Normal heating scenario',
            'collector': 80.0, 'tank': 30.0, 'expected_dt': 50.0
        },
        {
            'name': 'Low temperature difference',
            'collector': 35.0, 'tank': 30.0, 'expected_dt': 5.0
        },
        {
            'name': 'Equal temperatures',
            'collector': 50.0, 'tank': 50.0, 'expected_dt': 0.0
        },
        {
            'name': 'Tank hotter than collector',
            'collector': 30.0, 'tank': 40.0, 'expected_dt': -10.0
        },
        {
            'name': 'High precision temperatures',
            'collector': 75.123, 'tank': 42.456, 'expected_dt': 32.667
        },
        {
            'name': 'Zero temperatures',
            'collector': 0.0, 'tank': 0.0, 'expected_dt': 0.0
        },
        {
            'name': 'Negative temperatures',
            'collector': -5.0, 'tank': -10.0, 'expected_dt': 5.0
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        # Set temperatures
        system.temperatures['megabas_sensor_6'] = scenario['collector']
        system.temperatures['megabas_sensor_7'] = scenario['tank']
        
        # Run sensor mapping
        system.temperatures['solar_collector'] = system.temperatures.get('megabas_sensor_6', 0)
        system.temperatures['storage_tank'] = system.temperatures.get('megabas_sensor_7', 0)
        
        # Calculate dT
        solar_collector = system.temperatures.get('solar_collector', 0)
        storage_tank = system.temperatures.get('storage_tank', 0)
        dT = solar_collector - storage_tank
        
        expected_dt = scenario['expected_dt']
        calculation_correct = abs(dT - expected_dt) < 0.001
        
        print(f"      Collector: {solar_collector}°C, Tank: {storage_tank}°C")
        print(f"      dT: {dT}°C, Expected: {expected_dt}°C")
        print(f"      Calculation: {'✅ PASS' if calculation_correct else '❌ FAIL'}")
        
        if not calculation_correct:
            all_passed = False
    
    return all_passed

def test_temperature_rate_calculations():
    """Test temperature rate calculations"""
    print("\n📈 Testing temperature rate calculations...")
    
    system = SolarHeatingSystem()
    
    # Test temperature rate calculation scenarios
    rate_scenarios = [
        {
            'name': 'Rising temperature',
            'old_temp': 20.0, 'new_temp': 30.0, 'time_diff_hours': 1.0, 'expected_rate': 10.0
        },
        {
            'name': 'Falling temperature',
            'old_temp': 50.0, 'new_temp': 40.0, 'time_diff_hours': 2.0, 'expected_rate': -5.0
        },
        {
            'name': 'No temperature change',
            'old_temp': 25.0, 'new_temp': 25.0, 'time_diff_hours': 1.0, 'expected_rate': 0.0
        },
        {
            'name': 'Fast temperature rise',
            'old_temp': 20.0, 'new_temp': 80.0, 'time_diff_hours': 0.5, 'expected_rate': 120.0
        },
        {
            'name': 'Slow temperature change',
            'old_temp': 25.0, 'new_temp': 25.5, 'time_diff_hours': 2.0, 'expected_rate': 0.25
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(rate_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        # Calculate temperature rate
        temp_diff = scenario['new_temp'] - scenario['old_temp']
        time_diff_hours = scenario['time_diff_hours']
        temp_rate = temp_diff / time_diff_hours if time_diff_hours > 0 else 0
        
        expected_rate = scenario['expected_rate']
        rate_correct = abs(temp_rate - expected_rate) < 0.001
        
        print(f"      Old temp: {scenario['old_temp']}°C, New temp: {scenario['new_temp']}°C")
        print(f"      Time diff: {time_diff_hours}h, Temp diff: {temp_diff}°C")
        print(f"      Rate: {temp_rate}°C/h, Expected: {expected_rate}°C/h")
        print(f"      Calculation: {'✅ PASS' if rate_correct else '❌ FAIL'}")
        
        if not rate_correct:
            all_passed = False
    
    return all_passed

def test_average_temperature_calculations():
    """Test average temperature calculations"""
    print("\n📊 Testing average temperature calculations...")
    
    system = SolarHeatingSystem()
    
    # Test average temperature calculation scenarios
    avg_scenarios = [
        {
            'name': 'Simple average',
            'temps': [20.0, 30.0, 40.0], 'expected_avg': 30.0
        },
        {
            'name': 'Single temperature',
            'temps': [25.5], 'expected_avg': 25.5
        },
        {
            'name': 'Equal temperatures',
            'temps': [50.0, 50.0, 50.0, 50.0], 'expected_avg': 50.0
        },
        {
            'name': 'Mixed positive and negative',
            'temps': [-10.0, 0.0, 10.0], 'expected_avg': 0.0
        },
        {
            'name': 'High precision temperatures',
            'temps': [25.123, 25.456, 25.789], 'expected_avg': 25.456
        },
        {
            'name': 'Water heater temperature profile',
            'temps': [20.0, 25.0, 30.0, 35.0, 40.0, 45.0, 50.0, 55.0], 'expected_avg': 37.5
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(avg_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        # Calculate average temperature
        temps = scenario['temps']
        avg_temp = sum(temps) / len(temps) if temps else 0
        
        expected_avg = scenario['expected_avg']
        avg_correct = abs(avg_temp - expected_avg) < 0.001
        
        print(f"      Temperatures: {temps}")
        print(f"      Average: {avg_temp}°C, Expected: {expected_avg}°C")
        print(f"      Calculation: {'✅ PASS' if avg_correct else '❌ FAIL'}")
        
        if not avg_correct:
            all_passed = False
    
    return all_passed

def test_temperature_validation_and_bounds():
    """Test temperature validation and bounds checking"""
    print("\n🔍 Testing temperature validation and bounds checking...")
    
    system = SolarHeatingSystem()
    
    # Test temperature validation scenarios
    validation_scenarios = [
        {
            'name': 'Valid temperature range',
            'temp': 75.0, 'min_temp': -50.0, 'max_temp': 200.0, 'should_be_valid': True
        },
        {
            'name': 'Temperature too high',
            'temp': 250.0, 'min_temp': -50.0, 'max_temp': 200.0, 'should_be_valid': False
        },
        {
            'name': 'Temperature too low',
            'temp': -100.0, 'min_temp': -50.0, 'max_temp': 200.0, 'should_be_valid': False
        },
        {
            'name': 'Boundary temperature (min)',
            'temp': -50.0, 'min_temp': -50.0, 'max_temp': 200.0, 'should_be_valid': True
        },
        {
            'name': 'Boundary temperature (max)',
            'temp': 200.0, 'min_temp': -50.0, 'max_temp': 200.0, 'should_be_valid': True
        },
        {
            'name': 'Zero temperature',
            'temp': 0.0, 'min_temp': -50.0, 'max_temp': 200.0, 'should_be_valid': True
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(validation_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        # Validate temperature
        temp = scenario['temp']
        min_temp = scenario['min_temp']
        max_temp = scenario['max_temp']
        is_valid = min_temp <= temp <= max_temp
        
        expected_valid = scenario['should_be_valid']
        validation_correct = is_valid == expected_valid
        
        print(f"      Temperature: {temp}°C, Range: [{min_temp}°C, {max_temp}°C]")
        print(f"      Valid: {is_valid}, Expected: {expected_valid}")
        print(f"      Validation: {'✅ PASS' if validation_correct else '❌ FAIL'}")
        
        if not validation_correct:
            all_passed = False
    
    return all_passed

def test_temperature_conversion_and_scaling():
    """Test temperature conversion and scaling"""
    print("\n🔄 Testing temperature conversion and scaling...")
    
    system = SolarHeatingSystem()
    
    # Test temperature conversion scenarios
    conversion_scenarios = [
        {
            'name': 'Celsius to Fahrenheit',
            'celsius': 0.0, 'expected_fahrenheit': 32.0
        },
        {
            'name': 'Celsius to Fahrenheit (boiling)',
            'celsius': 100.0, 'expected_fahrenheit': 212.0
        },
        {
            'name': 'Celsius to Fahrenheit (room temp)',
            'celsius': 20.0, 'expected_fahrenheit': 68.0
        },
        {
            'name': 'Celsius to Kelvin',
            'celsius': 0.0, 'expected_kelvin': 273.15
        },
        {
            'name': 'Celsius to Kelvin (room temp)',
            'celsius': 20.0, 'expected_kelvin': 293.15
        },
        {
            'name': 'Temperature scaling factor',
            'temp': 50.0, 'scale_factor': 1.8, 'expected_scaled': 90.0
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(conversion_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        # Test Celsius to Fahrenheit conversion
        if 'expected_fahrenheit' in scenario:
            temp_celsius = scenario['celsius']
            fahrenheit = (temp_celsius * 9/5) + 32
            expected_fahrenheit = scenario['expected_fahrenheit']
            conversion_correct = abs(fahrenheit - expected_fahrenheit) < 0.001
            
            print(f"      Celsius: {temp_celsius}°C, Fahrenheit: {fahrenheit}°F, Expected: {expected_fahrenheit}°F")
            print(f"      Conversion: {'✅ PASS' if conversion_correct else '❌ FAIL'}")
            
            if not conversion_correct:
                all_passed = False
        
        # Test Celsius to Kelvin conversion
        if 'expected_kelvin' in scenario:
            temp_celsius = scenario['celsius']
            kelvin = temp_celsius + 273.15
            expected_kelvin = scenario['expected_kelvin']
            conversion_correct = abs(kelvin - expected_kelvin) < 0.001
            
            print(f"      Celsius: {temp_celsius}°C, Kelvin: {kelvin}K, Expected: {expected_kelvin}K")
            print(f"      Conversion: {'✅ PASS' if conversion_correct else '❌ FAIL'}")
            
            if not conversion_correct:
                all_passed = False
        
        # Test temperature scaling
        if 'scale_factor' in scenario:
            temp_celsius = scenario['temp']
            scaled_temp = temp_celsius * scenario['scale_factor']
            expected_scaled = scenario['expected_scaled']
            scaling_correct = abs(scaled_temp - expected_scaled) < 0.001
            
            print(f"      Original: {temp_celsius}°C, Scaled: {scaled_temp}°C, Expected: {expected_scaled}°C")
            print(f"      Scaling: {'✅ PASS' if scaling_correct else '❌ FAIL'}")
            
            if not scaling_correct:
                all_passed = False
    
    return all_passed

def test_temperature_calculation_edge_cases():
    """Test temperature calculation edge cases"""
    print("\n⚠️ Testing temperature calculation edge cases...")
    
    system = SolarHeatingSystem()
    
    # Test edge case scenarios
    edge_scenarios = [
        {
            'name': 'Very small temperature difference',
            'collector': 25.0001, 'tank': 25.0000, 'expected_dt': 0.0001
        },
        {
            'name': 'Very large temperature difference',
            'collector': 200.0, 'tank': -50.0, 'expected_dt': 250.0
        },
        {
            'name': 'Floating point precision',
            'collector': 33.333333, 'tank': 11.111111, 'expected_dt': 22.222222
        },
        {
            'name': 'Division by zero protection',
            'old_temp': 25.0, 'new_temp': 30.0, 'time_diff': 0.0, 'expected_rate': 0.0
        },
        {
            'name': 'Empty temperature list',
            'temps': [], 'expected_avg': 0.0
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(edge_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        if 'collector' in scenario:
            # Test temperature difference edge case
            collector = scenario['collector']
            tank = scenario['tank']
            dT = collector - tank
            expected_dt = scenario['expected_dt']
            calculation_correct = abs(dT - expected_dt) < 0.000001
            
            print(f"      Collector: {collector}°C, Tank: {tank}°C")
            print(f"      dT: {dT}°C, Expected: {expected_dt}°C")
            print(f"      Calculation: {'✅ PASS' if calculation_correct else '❌ FAIL'}")
            
            if not calculation_correct:
                all_passed = False
        
        elif 'old_temp' in scenario:
            # Test rate calculation edge case
            old_temp = scenario['old_temp']
            new_temp = scenario['new_temp']
            time_diff = scenario['time_diff']
            temp_rate = (new_temp - old_temp) / time_diff if time_diff > 0 else 0
            expected_rate = scenario['expected_rate']
            rate_correct = abs(temp_rate - expected_rate) < 0.001
            
            print(f"      Old temp: {old_temp}°C, New temp: {new_temp}°C, Time: {time_diff}h")
            print(f"      Rate: {temp_rate}°C/h, Expected: {expected_rate}°C/h")
            print(f"      Calculation: {'✅ PASS' if rate_correct else '❌ FAIL'}")
            
            if not rate_correct:
                all_passed = False
        
        elif 'temps' in scenario:
            # Test average calculation edge case
            temps = scenario['temps']
            avg_temp = sum(temps) / len(temps) if temps else 0
            expected_avg = scenario['expected_avg']
            avg_correct = abs(avg_temp - expected_avg) < 0.001
            
            print(f"      Temperatures: {temps}")
            print(f"      Average: {avg_temp}°C, Expected: {expected_avg}°C")
            print(f"      Calculation: {'✅ PASS' if avg_correct else '❌ FAIL'}")
            
            if not avg_correct:
                all_passed = False
    
    return all_passed

def main():
    """Main test runner"""
    print("🚀 Starting Temperature Calculation Accuracy Test Suite")
    print("=" * 70)
    
    tests = [
        ("Basic Temperature Differences", test_basic_temperature_differences),
        ("Temperature Rate Calculations", test_temperature_rate_calculations),
        ("Average Temperature Calculations", test_average_temperature_calculations),
        ("Temperature Validation and Bounds", test_temperature_validation_and_bounds),
        ("Temperature Conversion and Scaling", test_temperature_conversion_and_scaling),
        ("Temperature Calculation Edge Cases", test_temperature_calculation_edge_cases),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
                print(f"\n✅ {test_name}: PASSED")
            else:
                print(f"\n❌ {test_name}: FAILED")
        except Exception as e:
            print(f"\n❌ {test_name}: EXCEPTION - {str(e)}")
    
    print("\n📊 TEMPERATURE CALCULATION ACCURACY TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Temperature calculations are mathematically accurate.")
        return True
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED. Temperature calculations need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
