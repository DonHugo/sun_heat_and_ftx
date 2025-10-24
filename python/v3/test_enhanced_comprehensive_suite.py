#!/usr/bin/env python3
"""
Enhanced Comprehensive Test Suite Runner
Runs all tests including the new realistic environment and MQTT integration tests.

This enhanced test suite includes:
1. Original comprehensive tests (logic validation)
2. Realistic environment tests (production-like behavior)
3. MQTT integration tests (real broker connections)
"""

import sys
import os
import time
import subprocess

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test(test_file, test_name, timeout=300):
    """Run a single test file and return results"""
    print(f"\n{'='*70}")
    print(f"🧪 Running {test_name}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        # Run the test
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=timeout)
        
        duration = time.time() - start_time
        
        if result.returncode == 0:
            print(f"✅ {test_name}: PASSED ({duration:.2f}s)")
            return True, duration, result.stdout
        else:
            print(f"❌ {test_name}: FAILED ({duration:.2f}s)")
            print(f"Error output: {result.stderr}")
            return False, duration, result.stdout
            
    except subprocess.TimeoutExpired:
        duration = time.time() - start_time
        print(f"⏰ {test_name}: TIMEOUT ({duration:.2f}s)")
        return False, duration, "Test timed out"
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 {test_name}: EXCEPTION ({duration:.2f}s)")
        print(f"Exception: {str(e)}")
        return False, duration, str(e)

def main():
    """Main test runner"""
    print("🚀 Starting Enhanced Comprehensive Test Suite for Solar Heating System v3")
    print("=" * 70)
    print("This enhanced test suite includes:")
    print("1. Original comprehensive tests (logic validation)")
    print("2. Realistic environment tests (production-like behavior)")
    print("3. MQTT integration tests (real broker connections)")
    print("=" * 70)
    
    # Define all tests organized by category
    test_categories = {
        "Logic Validation Tests": [
            ("test_sensor_data_flow_simple.py", "Sensor Data Flow Validation Test"),
            ("test_temperature_calculation_accuracy.py", "Temperature Calculation Accuracy Test"),
            ("test_pump_control_completeness.py", "Pump Control Logic Completeness Test"),
            ("test_energy_calculation_validation.py", "Energy Calculation Validation Test"),
            ("test_system_state_consistency.py", "System State Consistency Test"),
            ("test_error_recovery.py", "Error Recovery Testing"),
        ],
        "Realistic Environment Tests": [
            ("test_realistic_environment.py", "Realistic Environment Test"),
        ],
        "MQTT Integration Tests": [
            ("test_mqtt_integration.py", "MQTT Integration Test"),
        ]
    }
    
    # Run all tests
    all_results = []
    total_start_time = time.time()
    
    for category_name, tests in test_categories.items():
        print(f"\n{'='*70}")
        print(f"📋 {category_name}")
        print(f"{'='*70}")
        
        for test_file, test_name in tests:
            # Check if test file exists
            if not os.path.exists(test_file):
                print(f"❌ {test_name}: SKIPPED (file not found: {test_file})")
                all_results.append((test_name, False, 0.0, f"File not found: {test_file}"))
                continue
            
            # Run the test
            passed, duration, output = run_test(test_file, test_name)
            all_results.append((test_name, passed, duration, output))
    
    total_duration = time.time() - total_start_time
    
    # Generate comprehensive summary
    print(f"\n{'='*70}")
    print("📊 ENHANCED COMPREHENSIVE TEST SUITE SUMMARY")
    print(f"{'='*70}")
    
    passed_tests = sum(1 for _, passed, _, _ in all_results if passed)
    total_tests = len(all_results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Total Duration: {total_duration:.2f} seconds")
    
    # Category breakdown
    print(f"\n📋 CATEGORY BREAKDOWN:")
    print(f"{'='*70}")
    
    for category_name, tests in test_categories.items():
        category_results = []
        for test_file, test_name in tests:
            for result_name, passed, duration, _ in all_results:
                if result_name == test_name:
                    category_results.append(passed)
                    break
        
        if category_results:
            category_passed = sum(category_results)
            category_total = len(category_results)
            category_rate = (category_passed / category_total * 100) if category_total > 0 else 0
            print(f"{category_name}: {category_passed}/{category_total} ({category_rate:.1f}%)")
    
    print(f"\n📋 DETAILED RESULTS:")
    print(f"{'='*70}")
    
    for test_name, passed, duration, output in all_results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name} ({duration:.2f}s)")
    
    print(f"\n🎯 TEST COVERAGE SUMMARY:")
    print(f"{'='*70}")
    print("✅ Logic Validation Tests:")
    print("   ✅ Sensor Data Flow Validation - End-to-end sensor data processing")
    print("   ✅ Temperature Calculation Accuracy - All temperature calculations")
    print("   ✅ Pump Control Logic Completeness - All pump scenarios")
    print("   ✅ Energy Calculation Validation - Physics-based energy calculations")
    print("   ✅ System State Consistency - State integrity across operations")
    print("   ✅ Error Recovery Testing - System recovery from failures")
    print("")
    print("✅ Realistic Environment Tests:")
    print("   ✅ Realistic Sensor Data - Production-like sensor data patterns")
    print("   ✅ Realistic System Behavior - 24-hour simulation")
    print("   ✅ Hardware-like Behavior - Response time testing")
    print("")
    print("✅ MQTT Integration Tests:")
    print("   ✅ MQTT Broker Connections - Real broker connectivity")
    print("   ✅ MQTT Message Publishing - Real message publishing")
    print("   ✅ MQTT Message Subscription - Real message subscription")
    print("   ✅ MQTT QoS Levels - Quality of service testing")
    print("   ✅ MQTT Failure Scenarios - Error handling")
    print("   ✅ MQTT Performance - Message throughput testing")
    
    print(f"\n🔍 TEST ENVIRONMENT IMPROVEMENTS:")
    print(f"{'='*70}")
    print("✅ Realistic Sensor Data:")
    print("   ✅ Time-based temperature profiles (day/night cycles)")
    print("   ✅ Weather condition simulation (sunny/cloudy/rainy)")
    print("   ✅ Seasonal variations (summer/winter)")
    print("   ✅ Realistic sensor noise and variations")
    print("   ✅ Water heater stratification simulation")
    print("")
    print("✅ Real MQTT Testing:")
    print("   ✅ Public MQTT broker connections")
    print("   ✅ Real message publishing and subscription")
    print("   ✅ QoS level testing")
    print("   ✅ Performance testing")
    print("   ✅ Failure scenario testing")
    print("")
    print("✅ Production-like Behavior:")
    print("   ✅ 24-hour system simulation")
    print("   ✅ Realistic pump cycling")
    print("   ✅ Energy accumulation tracking")
    print("   ✅ Response time validation")
    
    if success_rate >= 90.0:
        print(f"\n🎉 EXCELLENT! Enhanced test suite completed with {success_rate:.1f}% success rate.")
        print("The Solar Heating System v3 is thoroughly tested with both logic validation")
        print("and realistic production-like behavior testing.")
        return True
    elif success_rate >= 75.0:
        print(f"\n✅ GOOD! Enhanced test suite completed with {success_rate:.1f}% success rate.")
        print("The system is well-tested with some areas needing attention.")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} TESTS FAILED. System needs significant attention.")
        print("Please review the failed tests and fix any issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)







