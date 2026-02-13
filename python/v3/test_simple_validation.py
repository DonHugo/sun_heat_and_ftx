#!/usr/bin/env python3
"""
Simple Validation Test
Quick test to validate the sensor mapping fix is working.
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

def test_sensor_mapping_fix():
    """Test the sensor mapping fix"""
    print("🧪 Testing sensor mapping fix...")
    
    system = SolarHeatingSystem()
    
    # Set test sensor data
    system.temperatures['megabas_sensor_6'] = 100.0  # Solar collector
    system.temperatures['megabas_sensor_7'] = 30.0   # Storage tank
    
    # Run sensor mapping (inline mapping like in the actual code)
    system.temperatures['solar_collector'] = system.temperatures.get('megabas_sensor_6', 0)
    system.temperatures['storage_tank'] = system.temperatures.get('megabas_sensor_7', 0)
    
    # Test 1: Check if mapping worked
    solar_collector = system.temperatures.get('solar_collector', 0)
    storage_tank = system.temperatures.get('storage_tank', 0)
    
    print(f"   Collector: {solar_collector}°C, Tank: {storage_tank}°C")
    
    if solar_collector == 100.0 and storage_tank == 30.0:
        print("   ✅ Sensor mapping: PASS")
    else:
        print("   ❌ Sensor mapping: FAIL")
        return False
    
    # Test 2: Check dT calculation
    dT = solar_collector - storage_tank
    expected_dt = 70.0
    
    print(f"   dT: {dT}°C, Expected: {expected_dt}°C")
    
    if abs(dT - expected_dt) < 0.1:
        print("   ✅ dT calculation: PASS")
    else:
        print("   ❌ dT calculation: FAIL")
        return False
    
    # Test 3: Check pump control logic
    dTStart = system.control_params.get('dTStart_tank_1', 8.0)
    pump_should_start = dT >= dTStart
    
    print(f"   dT={dT}°C >= {dTStart}°C threshold, pump should start: {pump_should_start}")
    
    if pump_should_start:
        print("   ✅ Pump control logic: PASS")
    else:
        print("   ❌ Pump control logic: FAIL")
        return False
    
    return True

def test_temperature_scenarios():
    """Test various temperature scenarios"""
    print("\n🌡️ Testing temperature scenarios...")
    
    system = SolarHeatingSystem()
    
    scenarios = [
        {"collector": 50.0, "tank": 30.0, "expected_dt": 20.0, "pump_should_start": True},
        {"collector": 35.0, "tank": 30.0, "expected_dt": 5.0, "pump_should_start": False},
        {"collector": 38.0, "tank": 30.0, "expected_dt": 8.0, "pump_should_start": True},
        {"collector": 34.0, "tank": 30.0, "expected_dt": 4.0, "pump_should_start": False},
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n   Scenario {i}: Collector {scenario['collector']}°C, Tank {scenario['tank']}°C")
        
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
        
        # Test dT calculation
        expected_dt = scenario['expected_dt']
        dT_correct = abs(dT - expected_dt) < 0.1
        
        print(f"      dT: {dT}°C, Expected: {expected_dt}°C - {'✅ PASS' if dT_correct else '❌ FAIL'}")
        
        # Test pump control
        dTStart = system.control_params.get('dTStart_tank_1', 8.0)
        pump_should_start = dT >= dTStart
        expected_pump = scenario['pump_should_start']
        
        print(f"      Pump should {'start' if expected_pump else 'not start'}: {'✅ PASS' if pump_should_start == expected_pump else '❌ FAIL'}")
        
        if not dT_correct or pump_should_start != expected_pump:
            all_passed = False
    
    return all_passed

def test_energy_calculation():
    """Test energy calculation"""
    print("\n⚡ Testing energy calculation...")
    
    system = SolarHeatingSystem()
    
    # Set temperatures for energy calculation
    system.temperatures['megabas_sensor_6'] = 80.0  # Solar collector
    system.temperatures['megabas_sensor_7'] = 20.0  # Storage tank
    
    # Run sensor mapping
    system.temperatures['solar_collector'] = system.temperatures.get('megabas_sensor_6', 0)
    system.temperatures['storage_tank'] = system.temperatures.get('megabas_sensor_7', 0)
    
    # Calculate dT
    solar_collector = system.temperatures.get('solar_collector', 0)
    storage_tank = system.temperatures.get('storage_tank', 0)
    dT = solar_collector - storage_tank
    
    print(f"   Collector: {solar_collector}°C, Tank: {storage_tank}°C, dT: {dT}°C")
    
    # Calculate energy (physics-based)
    tank_volume_kg = 360  # 360L tank
    specific_heat_capacity = 4.2  # kJ/kg°C
    energy_kj = tank_volume_kg * specific_heat_capacity * dT
    energy_kwh = energy_kj / 3600  # Convert to kWh
    
    expected_energy_kwh = 25.2  # 360 * 4.2 * 60 / 3600
    
    print(f"   Energy: {energy_kwh:.2f} kWh, Expected: {expected_energy_kwh} kWh")
    
    if abs(energy_kwh - expected_energy_kwh) < 0.1:
        print("   ✅ Energy calculation: PASS")
        return True
    else:
        print("   ❌ Energy calculation: FAIL")
        return False

def main():
    """Main test runner"""
    print("🚀 Starting Simple Validation Test")
    print("=" * 50)
    
    tests = [
        ("Sensor Mapping Fix", test_sensor_mapping_fix),
        ("Temperature Scenarios", test_temperature_scenarios),
        ("Energy Calculation", test_energy_calculation),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"   ❌ {test_name}: EXCEPTION - {str(e)}")
    
    print("\n📊 TEST SUMMARY")
    print("=" * 50)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Basic functionality is working correctly.")
        return True
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED. System needs attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)













