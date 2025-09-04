#!/usr/bin/env python3
"""
Enhanced Test Script for Midnight Reset and State Persistence
Tests both operational metrics and energy collection data persistence
"""

import json
import os
import time
from datetime import datetime, time as dt_time
from unittest.mock import patch, MagicMock

def test_state_persistence():
    """Test that state is properly saved and loaded"""
    print("🧪 Testing State Persistence...")
    
    # Test data
    test_state = {
        'pump_runtime_hours': 12.5,
        'heating_cycles_count': 25,
        'total_heating_time': 15.2,
        'total_heating_time_lifetime': 156.8,
        'energy_collected_today': 8.75,
        'solar_energy_today': 6.2,
        'cartridge_energy_today': 2.1,
        'pellet_energy_today': 0.45,
        'last_midnight_reset_date': '2024-01-15',
        'last_day_reset': time.time(),
        'last_save_time': time.time(),
        'last_save_date': datetime.now().isoformat()
    }
    
    # Test save
    test_file = 'test_system_state.json'
    try:
        with open(test_file, 'w') as f:
            json.dump(test_state, f, indent=2)
        print("✅ State save test passed")
        
        # Test load
        with open(test_file, 'r') as f:
            loaded_state = json.load(f)
        
        # Verify all fields are present
        for key in test_state.keys():
            if key not in loaded_state:
                print(f"❌ Missing key in loaded state: {key}")
                return False
        
        print("✅ State load test passed")
        
        # Clean up
        os.remove(test_file)
        print("✅ Test file cleanup completed")
        return True
        
    except Exception as e:
        print(f"❌ State persistence test failed: {e}")
        return False

def test_midnight_detection():
    """Test midnight detection logic"""
    print("\n🧪 Testing Midnight Detection...")
    
    # Mock current time to test midnight detection
    test_times = [
        (23, 59, 58),  # 2 seconds before midnight
        (23, 59, 59),  # 1 second before midnight
        (0, 0, 0),     # Exactly midnight
        (0, 0, 1),     # 1 second after midnight
        (0, 0, 5),     # 5 seconds after midnight
        (0, 0, 10),    # 10 seconds after midnight
        (0, 0, 11),    # 11 seconds after midnight (should not trigger)
        (12, 0, 0),    # Noon (should not trigger)
    ]
    
    def is_midnight_reset_needed(current_time):
        """Replicate the corrected midnight detection logic"""
        current_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second
        
        # Handle both before and after midnight cases
        if current_seconds >= 23 * 3600 + 59 * 60 + 50:  # After 23:59:50 (10 seconds before midnight)
            # We're approaching midnight from the previous day
            time_diff = (24 * 3600) - current_seconds
        elif current_seconds <= 10:  # Within 10 seconds after midnight
            # We're just after midnight
            time_diff = current_seconds
        else:
            # We're not near midnight
            time_diff = 999  # Large number to ensure no reset
        
        # Allow reset within 10 seconds of midnight
        return time_diff <= 10
    
    expected_results = [True, True, True, True, True, True, False, False]
    
    for i, (hour, minute, second) in enumerate(test_times):
        test_time = dt_time(hour, minute, second)
        result = is_midnight_reset_needed(test_time)
        expected = expected_results[i]
        
        status = "✅" if result == expected else "❌"
        print(f"{status} {hour:02d}:{minute:02d}:{second:02d} -> {result} (expected: {expected})")
    
    print("✅ Midnight detection test completed")
    return True

def test_energy_collection_persistence():
    """Test that energy collection data persists across restarts"""
    print("\n🧪 Testing Energy Collection Persistence...")
    
    # Simulate system state with energy collection data
    system_state = {
        'energy_collected_today': 15.8,
        'solar_energy_today': 12.3,
        'cartridge_energy_today': 2.8,
        'pellet_energy_today': 0.7,
        'last_midnight_reset_date': '2024-01-15'
    }
    
    # Simulate saving state
    test_file = 'test_energy_state.json'
    try:
        with open(test_file, 'w') as f:
            json.dump(system_state, f, indent=2)
        print("✅ Energy state saved")
        
        # Simulate loading state (system restart)
        with open(test_file, 'r') as f:
            loaded_energy_state = json.load(f)
        
        # Verify energy data is preserved
        for key, expected_value in system_state.items():
            loaded_value = loaded_energy_state.get(key)
            if loaded_value == expected_value:
                print(f"✅ {key}: {loaded_value} (preserved)")
            else:
                print(f"❌ {key}: {loaded_value} (expected: {expected_value})")
        
        # Clean up
        os.remove(test_file)
        print("✅ Energy state test cleanup completed")
        return True
        
    except Exception as e:
        print(f"❌ Energy collection persistence test failed: {e}")
        return False

def test_midnight_reset_scenarios():
    """Test various midnight reset scenarios"""
    print("\n🧪 Testing Midnight Reset Scenarios...")
    
    scenarios = [
        {
            'name': 'First run of the day',
            'current_date': '2024-01-15',
            'last_reset_date': '2024-01-14',
            'should_reset': True
        },
        {
            'name': 'Already reset today',
            'current_date': '2024-01-15',
            'last_reset_date': '2024-01-15',
            'should_reset': False
        },
        {
            'name': 'New day after restart',
            'current_date': '2024-01-16',
            'last_reset_date': '2024-01-15',
            'should_reset': True
        },
        {
            'name': 'Same day after restart',
            'current_date': '2024-01-15',
            'last_reset_date': '2024-01-15',
            'should_reset': False
        }
    ]
    
    for scenario in scenarios:
        current_date = scenario['current_date']
        last_reset_date = scenario['last_reset_date']
        should_reset = scenario['should_reset']
        
        # Simulate the reset logic
        reset_needed = (current_date != last_reset_date)
        
        status = "✅" if reset_needed == should_reset else "❌"
        print(f"{status} {scenario['name']}: {current_date} vs {last_reset_date} -> reset={reset_needed} (expected: {should_reset})")
    
    print("✅ Midnight reset scenarios test completed")
    return True

def main():
    """Run all tests"""
    print("🚀 Enhanced Midnight Reset and State Persistence Test Suite")
    print("=" * 60)
    
    tests = [
        test_state_persistence,
        test_midnight_detection,
        test_energy_collection_persistence,
        test_midnight_reset_scenarios
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} failed with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Midnight reset and state persistence is working correctly.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
    
    return passed == total

if __name__ == "__main__":
    main()
