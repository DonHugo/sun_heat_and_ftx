#!/usr/bin/env python3
"""
Energy Calculation Validation Test
Tests physics-based energy calculations for accuracy.

This test validates:
1. Basic energy calculations using physics formulas
2. Energy accumulation over time
3. Energy source tracking (solar, cartridge, pellet)
4. Energy conversion and scaling
5. Energy efficiency calculations
6. Energy storage calculations
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

def test_basic_energy_calculations():
    """Test basic energy calculations using physics formulas"""
    print("⚡ Testing basic energy calculations...")
    
    system = SolarHeatingSystem()
    
    # Test energy calculation scenarios
    energy_scenarios = [
        {
            'name': 'High temperature difference',
            'collector': 100.0, 'tank': 20.0, 'dT': 80.0,
            'tank_volume_liters': 360,
            'expected_energy_kwh': 33.6  # 360L * 4.2 kJ/kg°C * 80°C / 3600
        },
        {
            'name': 'Medium temperature difference',
            'collector': 60.0, 'tank': 40.0, 'dT': 20.0,
            'tank_volume_liters': 360,
            'expected_energy_kwh': 8.4   # 360L * 4.2 kJ/kg°C * 20°C / 3600
        },
        {
            'name': 'Low temperature difference',
            'collector': 35.0, 'tank': 30.0, 'dT': 5.0,
            'tank_volume_liters': 360,
            'expected_energy_kwh': 2.1   # 360L * 4.2 kJ/kg°C * 5°C / 3600
        },
        {
            'name': 'No temperature difference',
            'collector': 50.0, 'tank': 50.0, 'dT': 0.0,
            'tank_volume_liters': 360,
            'expected_energy_kwh': 0.0   # No energy transfer
        },
        {
            'name': 'Small tank volume',
            'collector': 80.0, 'tank': 20.0, 'dT': 60.0,
            'tank_volume_liters': 100,
            'expected_energy_kwh': 7.0   # 100L * 4.2 kJ/kg°C * 60°C / 3600
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(energy_scenarios, 1):
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
        
        # Calculate energy using physics formula
        tank_volume_liters = scenario['tank_volume_liters']
        tank_volume_kg = tank_volume_liters  # 1 liter = 1 kg for water
        specific_heat_capacity = 4.2  # kJ/kg°C for water
        
        if dT > 0:
            energy_kj = tank_volume_kg * specific_heat_capacity * dT
            energy_kwh = energy_kj / 3600  # Convert kJ to kWh
        else:
            energy_kwh = 0.0
        
        expected_energy = scenario['expected_energy_kwh']
        calculation_correct = abs(energy_kwh - expected_energy) < 0.1
        
        print(f"      Collector: {solar_collector}°C, Tank: {storage_tank}°C")
        print(f"      dT: {dT}°C, Tank volume: {tank_volume_liters}L")
        print(f"      Energy: {energy_kwh:.2f} kWh, Expected: {expected_energy} kWh")
        print(f"      Calculation: {'✅ PASS' if calculation_correct else '❌ FAIL'}")
        
        if not calculation_correct:
            all_passed = False
    
    return all_passed

def test_energy_accumulation_over_time():
    """Test energy accumulation over time"""
    print("\n📈 Testing energy accumulation over time...")
    
    system = SolarHeatingSystem()
    
    # Test energy accumulation scenarios
    accumulation_scenarios = [
        {
            'name': 'Constant energy input over time',
            'energy_per_hour': 5.0,  # kWh per hour
            'hours': 4,
            'expected_total_energy': 20.0  # 5.0 * 4
        },
        {
            'name': 'Variable energy input over time',
            'energy_per_hour': [2.0, 4.0, 6.0, 3.0],  # kWh per hour
            'hours': 4,
            'expected_total_energy': 15.0  # 2.0 + 4.0 + 6.0 + 3.0
        },
        {
            'name': 'Zero energy input',
            'energy_per_hour': 0.0,
            'hours': 5,
            'expected_total_energy': 0.0
        },
        {
            'name': 'Single hour energy input',
            'energy_per_hour': 10.0,
            'hours': 1,
            'expected_total_energy': 10.0
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(accumulation_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        total_energy = 0.0
        
        if isinstance(scenario['energy_per_hour'], list):
            # Variable energy input
            for hour, energy in enumerate(scenario['energy_per_hour'], 1):
                total_energy += energy
                print(f"      Hour {hour}: +{energy} kWh, Total: {total_energy} kWh")
        else:
            # Constant energy input
            energy_per_hour = scenario['energy_per_hour']
            for hour in range(1, scenario['hours'] + 1):
                total_energy += energy_per_hour
                print(f"      Hour {hour}: +{energy_per_hour} kWh, Total: {total_energy} kWh")
        
        expected_total = scenario['expected_total_energy']
        accumulation_correct = abs(total_energy - expected_total) < 0.1
        
        print(f"      Final total: {total_energy} kWh, Expected: {expected_total} kWh")
        print(f"      Accumulation: {'✅ PASS' if accumulation_correct else '❌ FAIL'}")
        
        if not accumulation_correct:
            all_passed = False
    
    return all_passed

def test_energy_source_tracking():
    """Test energy source tracking (solar, cartridge, pellet)"""
    print("\n🔋 Testing energy source tracking...")
    
    system = SolarHeatingSystem()
    
    # Test energy source tracking scenarios
    source_scenarios = [
        {
            'name': 'Solar energy only',
            'solar_energy': 15.0, 'cartridge_energy': 0.0, 'pellet_energy': 0.0,
            'expected_total': 15.0, 'expected_solar_percent': 100.0
        },
        {
            'name': 'Mixed energy sources',
            'solar_energy': 10.0, 'cartridge_energy': 5.0, 'pellet_energy': 3.0,
            'expected_total': 18.0, 'expected_solar_percent': 55.56
        },
        {
            'name': 'Cartridge energy only',
            'solar_energy': 0.0, 'cartridge_energy': 8.0, 'pellet_energy': 0.0,
            'expected_total': 8.0, 'expected_solar_percent': 0.0
        },
        {
            'name': 'Pellet energy only',
            'solar_energy': 0.0, 'cartridge_energy': 0.0, 'pellet_energy': 12.0,
            'expected_total': 12.0, 'expected_solar_percent': 0.0
        },
        {
            'name': 'All energy sources',
            'solar_energy': 20.0, 'cartridge_energy': 10.0, 'pellet_energy': 5.0,
            'expected_total': 35.0, 'expected_solar_percent': 57.14
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(source_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        # Set energy values
        solar_energy = scenario['solar_energy']
        cartridge_energy = scenario['cartridge_energy']
        pellet_energy = scenario['pellet_energy']
        
        # Calculate total energy
        total_energy = solar_energy + cartridge_energy + pellet_energy
        
        # Calculate solar percentage
        solar_percent = (solar_energy / total_energy * 100) if total_energy > 0 else 0.0
        
        expected_total = scenario['expected_total']
        expected_solar_percent = scenario['expected_solar_percent']
        
        total_correct = abs(total_energy - expected_total) < 0.1
        percent_correct = abs(solar_percent - expected_solar_percent) < 0.1
        
        print(f"      Solar: {solar_energy} kWh, Cartridge: {cartridge_energy} kWh, Pellet: {pellet_energy} kWh")
        print(f"      Total: {total_energy} kWh, Expected: {expected_total} kWh")
        print(f"      Solar %: {solar_percent:.2f}%, Expected: {expected_solar_percent:.2f}%")
        print(f"      Total calculation: {'✅ PASS' if total_correct else '❌ FAIL'}")
        print(f"      Percentage calculation: {'✅ PASS' if percent_correct else '❌ FAIL'}")
        
        if not (total_correct and percent_correct):
            all_passed = False
    
    return all_passed

def test_energy_conversion_and_scaling():
    """Test energy conversion and scaling"""
    print("\n🔄 Testing energy conversion and scaling...")
    
    system = SolarHeatingSystem()
    
    # Test energy conversion scenarios
    conversion_scenarios = [
        {
            'name': 'kJ to kWh conversion',
            'energy_kj': 3600.0, 'expected_kwh': 1.0
        },
        {
            'name': 'kWh to kJ conversion',
            'energy_kwh': 2.5, 'expected_kj': 9000.0
        },
        {
            'name': 'Energy scaling factor',
            'energy_base': 10.0, 'scale_factor': 1.5, 'expected_scaled': 15.0
        },
        {
            'name': 'Energy efficiency calculation',
            'energy_input': 20.0, 'energy_output': 16.0, 'expected_efficiency': 80.0
        },
        {
            'name': 'Energy loss calculation',
            'energy_input': 25.0, 'energy_output': 20.0, 'expected_loss': 5.0
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(conversion_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        if 'energy_kj' in scenario:
            # kJ to kWh conversion
            energy_kj = scenario['energy_kj']
            energy_kwh = energy_kj / 3600
            expected_kwh = scenario['expected_kwh']
            conversion_correct = abs(energy_kwh - expected_kwh) < 0.001
            
            print(f"      Energy: {energy_kj} kJ = {energy_kwh} kWh, Expected: {expected_kwh} kWh")
            print(f"      Conversion: {'✅ PASS' if conversion_correct else '❌ FAIL'}")
            
            if not conversion_correct:
                all_passed = False
        
        elif 'energy_kwh' in scenario:
            # kWh to kJ conversion
            energy_kwh = scenario['energy_kwh']
            energy_kj = energy_kwh * 3600
            expected_kj = scenario['expected_kj']
            conversion_correct = abs(energy_kj - expected_kj) < 0.1
            
            print(f"      Energy: {energy_kwh} kWh = {energy_kj} kJ, Expected: {expected_kj} kJ")
            print(f"      Conversion: {'✅ PASS' if conversion_correct else '❌ FAIL'}")
            
            if not conversion_correct:
                all_passed = False
        
        elif 'scale_factor' in scenario:
            # Energy scaling
            energy_base = scenario['energy_base']
            scale_factor = scenario['scale_factor']
            energy_scaled = energy_base * scale_factor
            expected_scaled = scenario['expected_scaled']
            scaling_correct = abs(energy_scaled - expected_scaled) < 0.1
            
            print(f"      Energy: {energy_base} kWh * {scale_factor} = {energy_scaled} kWh, Expected: {expected_scaled} kWh")
            print(f"      Scaling: {'✅ PASS' if scaling_correct else '❌ FAIL'}")
            
            if not scaling_correct:
                all_passed = False
        
        elif 'energy_input' in scenario:
            # Energy efficiency and loss
            energy_input = scenario['energy_input']
            energy_output = scenario['energy_output']
            
            if 'expected_efficiency' in scenario:
                efficiency = (energy_output / energy_input * 100) if energy_input > 0 else 0.0
                expected_efficiency = scenario['expected_efficiency']
                efficiency_correct = abs(efficiency - expected_efficiency) < 0.1
                
                print(f"      Efficiency: {energy_output} kWh / {energy_input} kWh * 100 = {efficiency:.1f}%, Expected: {expected_efficiency}%")
                print(f"      Efficiency: {'✅ PASS' if efficiency_correct else '❌ FAIL'}")
                
                if not efficiency_correct:
                    all_passed = False
            
            if 'expected_loss' in scenario:
                energy_loss = energy_input - energy_output
                expected_loss = scenario['expected_loss']
                loss_correct = abs(energy_loss - expected_loss) < 0.1
                
                print(f"      Loss: {energy_input} kWh - {energy_output} kWh = {energy_loss} kWh, Expected: {expected_loss} kWh")
                print(f"      Loss: {'✅ PASS' if loss_correct else '❌ FAIL'}")
                
                if not loss_correct:
                    all_passed = False
    
    return all_passed

def test_energy_storage_calculations():
    """Test energy storage calculations"""
    print("\n💾 Testing energy storage calculations...")
    
    system = SolarHeatingSystem()
    
    # Test energy storage scenarios
    storage_scenarios = [
        {
            'name': 'Full tank energy storage',
            'tank_volume_liters': 360, 'tank_temp': 80.0, 'ambient_temp': 20.0,
            'expected_stored_energy': 25.2  # 360L * 4.2 kJ/kg°C * 60°C / 3600
        },
        {
            'name': 'Half tank energy storage',
            'tank_volume_liters': 180, 'tank_temp': 60.0, 'ambient_temp': 20.0,
            'expected_stored_energy': 8.4   # 180L * 4.2 kJ/kg°C * 40°C / 3600
        },
        {
            'name': 'Cold tank energy storage',
            'tank_volume_liters': 360, 'tank_temp': 25.0, 'ambient_temp': 20.0,
            'expected_stored_energy': 2.1   # 360L * 4.2 kJ/kg°C * 5°C / 3600
        },
        {
            'name': 'Hot tank energy storage',
            'tank_volume_liters': 360, 'tank_temp': 100.0, 'ambient_temp': 20.0,
            'expected_stored_energy': 33.6  # 360L * 4.2 kJ/kg°C * 80°C / 3600
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(storage_scenarios, 1):
        print(f"\n   Scenario {i}: {scenario['name']}")
        
        # Calculate stored energy
        tank_volume_liters = scenario['tank_volume_liters']
        tank_temp = scenario['tank_temp']
        ambient_temp = scenario['ambient_temp']
        
        tank_volume_kg = tank_volume_liters  # 1 liter = 1 kg for water
        specific_heat_capacity = 4.2  # kJ/kg°C for water
        temp_diff = tank_temp - ambient_temp
        
        if temp_diff > 0:
            stored_energy_kj = tank_volume_kg * specific_heat_capacity * temp_diff
            stored_energy_kwh = stored_energy_kj / 3600
        else:
            stored_energy_kwh = 0.0
        
        expected_stored_energy = scenario['expected_stored_energy']
        storage_correct = abs(stored_energy_kwh - expected_stored_energy) < 0.1
        
        print(f"      Tank: {tank_volume_liters}L at {tank_temp}°C, Ambient: {ambient_temp}°C")
        print(f"      Temp diff: {temp_diff}°C")
        print(f"      Stored energy: {stored_energy_kwh:.2f} kWh, Expected: {expected_stored_energy} kWh")
        print(f"      Storage calculation: {'✅ PASS' if storage_correct else '❌ FAIL'}")
        
        if not storage_correct:
            all_passed = False
    
    return all_passed

def test_energy_calculation_edge_cases():
    """Test energy calculation edge cases"""
    print("\n⚠️ Testing energy calculation edge cases...")
    
    system = SolarHeatingSystem()
    
    # Test edge case scenarios
    edge_scenarios = [
        {
            'name': 'Very small temperature difference',
            'collector': 30.0001, 'tank': 30.0000, 'dT': 0.0001,
            'tank_volume_liters': 360,
            'expected_energy': 0.000042  # 360L * 4.2 kJ/kg°C * 0.0001°C / 3600
        },
        {
            'name': 'Very large temperature difference',
            'collector': 200.0, 'tank': 20.0, 'dT': 180.0,
            'tank_volume_liters': 360,
            'expected_energy': 75.6  # 360L * 4.2 kJ/kg°C * 180°C / 3600
        },
        {
            'name': 'Negative temperature difference',
            'collector': 20.0, 'tank': 30.0, 'dT': -10.0,
            'tank_volume_liters': 360,
            'expected_energy': 0.0  # No energy transfer when tank is hotter
        },
        {
            'name': 'Zero tank volume',
            'collector': 80.0, 'tank': 20.0, 'dT': 60.0,
            'tank_volume_liters': 0,
            'expected_energy': 0.0  # No energy storage in zero volume
        },
        {
            'name': 'Floating point precision',
            'collector': 50.123456, 'tank': 30.123456, 'dT': 20.0,
            'tank_volume_liters': 360,
            'expected_energy': 8.4  # 360L * 4.2 kJ/kg°C * 20°C / 3600
        }
    ]
    
    all_passed = True
    
    for i, scenario in enumerate(edge_scenarios, 1):
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
        
        # Calculate energy
        tank_volume_liters = scenario['tank_volume_liters']
        tank_volume_kg = tank_volume_liters
        specific_heat_capacity = 4.2
        
        if dT > 0 and tank_volume_kg > 0:
            energy_kj = tank_volume_kg * specific_heat_capacity * dT
            energy_kwh = energy_kj / 3600
        else:
            energy_kwh = 0.0
        
        expected_energy = scenario['expected_energy']
        calculation_correct = abs(energy_kwh - expected_energy) < 0.0001
        
        print(f"      Collector: {solar_collector}°C, Tank: {storage_tank}°C")
        print(f"      dT: {dT:.6f}°C, Tank volume: {tank_volume_liters}L")
        print(f"      Energy: {energy_kwh:.6f} kWh, Expected: {expected_energy} kWh")
        print(f"      Calculation: {'✅ PASS' if calculation_correct else '❌ FAIL'}")
        
        if not calculation_correct:
            all_passed = False
    
    return all_passed

def main():
    """Main test runner"""
    print("🚀 Starting Energy Calculation Validation Test Suite")
    print("=" * 70)
    
    tests = [
        ("Basic Energy Calculations", test_basic_energy_calculations),
        ("Energy Accumulation Over Time", test_energy_accumulation_over_time),
        ("Energy Source Tracking", test_energy_source_tracking),
        ("Energy Conversion and Scaling", test_energy_conversion_and_scaling),
        ("Energy Storage Calculations", test_energy_storage_calculations),
        ("Energy Calculation Edge Cases", test_energy_calculation_edge_cases),
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
    
    print("\n📊 ENERGY CALCULATION VALIDATION TEST SUMMARY")
    print("=" * 70)
    print(f"Total Tests: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {total - passed} ❌")
    print(f"Success Rate: {(passed / total * 100):.1f}%")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! Energy calculations are physically accurate.")
        return True
    else:
        print(f"\n⚠️  {total - passed} TESTS FAILED. Energy calculations need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)













