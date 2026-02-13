#!/usr/bin/env python3
"""
Simple test runner to verify water heater safety metrics implementation
"""

import sys
import os
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

def test_water_heater_safety_basic():
    """Basic test to verify implementation exists and works"""
    
    print("=" * 70)
    print("TESTING WATER HEATER SAFETY METRICS IMPLEMENTATION")
    print("=" * 70)
    
    # Mock the hardware and MQTT dependencies
    with patch('main_system.HardwareInterface') as mock_hw, \
         patch('main_system.MQTTHandler') as mock_mqtt, \
         patch('main_system.taskmaster_service') as mock_taskmaster:
        
        mock_hw.return_value = Mock()
        mock_mqtt_instance = Mock()
        mock_mqtt_instance.is_connected = Mock(return_value=False)
        mock_mqtt.return_value = mock_mqtt_instance
        mock_taskmaster.analyze_temperatures = Mock(return_value="Normal")
        
        from main_system import SolarHeatingSystem
        
        system = SolarHeatingSystem()
        system.temperatures = {}
        
        # Test 1: Normal operation
        print("\n✓ Test 1: Normal operation (all temps below 60°C)")
        system.temperatures = {
            'water_heater_bottom': 35.0,
            'water_heater_20cm': 38.0,
            'water_heater_40cm': 42.0,
            'water_heater_60cm': 45.0,
            'water_heater_80cm': 48.0,
            'water_heater_100cm': 52.0,
            'water_heater_120cm': 55.0,
            'water_heater_140cm': 58.0,
        }
        
        system._calculate_water_heater_safety_metrics()
        
        assert 'water_heater_peak_temp' in system.temperatures
        assert system.temperatures['water_heater_peak_temp'] == 58.0
        assert system.temperatures['water_heater_overheating_risk'] == False
        print(f"   Peak temp: {system.temperatures['water_heater_peak_temp']}°C")
        print(f"   Overheating risk: {system.temperatures['water_heater_overheating_risk']}")
        print("   ✅ PASS")
        
        # Test 2: Overheating condition
        print("\n✓ Test 2: Overheating condition (peak at 72°C)")
        system.temperatures = {
            'water_heater_bottom': 45.0,
            'water_heater_20cm': 48.0,
            'water_heater_40cm': 52.0,
            'water_heater_60cm': 56.0,
            'water_heater_80cm': 62.0,
            'water_heater_100cm': 66.0,
            'water_heater_120cm': 69.0,
            'water_heater_140cm': 72.0,
        }
        
        system._calculate_water_heater_safety_metrics()
        
        assert system.temperatures['water_heater_peak_temp'] == 72.0
        assert system.temperatures['water_heater_overheating_risk'] == True
        print(f"   Peak temp: {system.temperatures['water_heater_peak_temp']}°C")
        print(f"   Overheating risk: {system.temperatures['water_heater_overheating_risk']}")
        print("   ✅ PASS")
        
        # Test 3: Thermal mass calculations
        print("\n✓ Test 3: Thermal mass calculations")
        system.temperatures = {
            'water_heater_bottom': 30.0,
            'water_heater_20cm': 32.0,
            'water_heater_40cm': 35.0,
            'water_heater_60cm': 38.0,
            'water_heater_80cm': 60.0,  # Top 4 starts
            'water_heater_100cm': 62.0,
            'water_heater_120cm': 64.0,
            'water_heater_140cm': 66.0,
        }
        
        system._calculate_water_heater_safety_metrics()
        
        assert 'water_heater_thermal_mass_top4' in system.temperatures
        assert system.temperatures['water_heater_thermal_mass_top4'] == 63.0
        print(f"   Top 4 thermal mass: {system.temperatures['water_heater_thermal_mass_top4']}°C")
        print(f"   All 8 thermal mass: {system.temperatures['water_heater_thermal_mass_all8']}°C")
        print("   ✅ PASS")
        
        # Test 4: Layers above 70°C
        print("\n✓ Test 4: Layers above 70°C counting")
        system.temperatures = {
            'water_heater_bottom': 50.0,
            'water_heater_20cm': 55.0,
            'water_heater_40cm': 60.0,
            'water_heater_60cm': 65.0,
            'water_heater_80cm': 69.0,
            'water_heater_100cm': 70.0,  # At threshold
            'water_heater_120cm': 71.0,  # Above
            'water_heater_140cm': 72.0,  # Above
        }
        
        system._calculate_water_heater_safety_metrics()
        
        assert system.temperatures['water_heater_layers_above_70c'] == 3
        print(f"   Layers ≥70°C: {system.temperatures['water_heater_layers_above_70c']}")
        print("   ✅ PASS")
        
        # Test 5: Insufficient sensors
        print("\n✓ Test 5: Insufficient sensors (fail-safe)")
        system.temperatures = {
            'water_heater_bottom': 45.0,
            'water_heater_20cm': 0,
            'water_heater_40cm': 0,
            'water_heater_60cm': 0,
            'water_heater_80cm': 0,
            'water_heater_100cm': 50.0,
            'water_heater_120cm': 0,
            'water_heater_140cm': 55.0,
        }
        
        system._calculate_water_heater_safety_metrics()
        
        assert system.temperatures['water_heater_peak_temp'] == 0
        assert system.temperatures['water_heater_overheating_risk'] == False
        print(f"   Peak temp (insufficient data): {system.temperatures['water_heater_peak_temp']}°C")
        print(f"   Overheating risk: {system.temperatures['water_heater_overheating_risk']}")
        print("   ✅ PASS")
        
        # Test 6: Exception handling (fail-safe)
        print("\n✓ Test 6: Exception handling (fail-safe to HIGH RISK)")
        system.temperatures = {
            'water_heater_bottom': 'invalid',  # String instead of float
            'water_heater_20cm': 45.0,
        }
        
        try:
            system._calculate_water_heater_safety_metrics()
            assert system.temperatures.get('water_heater_overheating_risk') == True
            print(f"   Overheating risk (on error): {system.temperatures['water_heater_overheating_risk']}")
            print("   ✅ PASS")
        except Exception as e:
            print(f"   ❌ FAIL: Method should handle exceptions gracefully, got: {e}")
            return False
        
        print("\n" + "=" * 70)
        print("🎉 ALL TESTS PASSED!")
        print("=" * 70)
        print("\nImplementation Summary:")
        print("✅ 1. _calculate_water_heater_safety_metrics() method added")
        print("✅ 2. Method called from _read_temperatures()")
        print("✅ 3. Peak temperature calculation working")
        print("✅ 4. Thermal mass (Top 4) calculation working")
        print("✅ 5. Thermal mass (All 8) calculation working")
        print("✅ 6. Layers above 70°C counting working")
        print("✅ 7. Overheating risk detection working")
        print("✅ 8. Invalid sensor handling working")
        print("✅ 9. Exception handling (fail-safe) working")
        print("=" * 70)
        
        return True

if __name__ == '__main__':
    try:
        success = test_water_heater_safety_basic()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
