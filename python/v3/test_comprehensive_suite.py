#!/usr/bin/env python3
"""
Comprehensive Test Suite Runner
Runs all the comprehensive tests for the Solar Heating System v3.

This test suite runs all the tests that were created to address the gaps
in basic functionality testing:

1. Sensor Data Flow Validation Test
2. Temperature Calculation Accuracy Test  
3. Pump Control Logic Completeness Test
4. Energy Calculation Validation Test
5. System State Consistency Test
6. Error Recovery Testing
"""

import sys
import os
import time
import subprocess

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_test(test_file, test_name):
    """Run a single test file and return results"""
    print(f"\n{'='*70}")
    print(f"🧪 Running {test_name}")
    print(f"{'='*70}")
    
    start_time = time.time()
    
    try:
        # Run the test
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, timeout=300)
        
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
        return False, duration, "Test timed out after 5 minutes"
    except Exception as e:
        duration = time.time() - start_time
        print(f"💥 {test_name}: EXCEPTION ({duration:.2f}s)")
        print(f"Exception: {str(e)}")
        return False, duration, str(e)

def main():
    """Main test runner"""
    print("🚀 Starting Comprehensive Test Suite for Solar Heating System v3")
    print("=" * 70)
    print("This test suite addresses the gaps in basic functionality testing")
    print("that were identified in the original test strategy.")
    print("=" * 70)
    
    # Define all tests
    tests = [
        ("test_sensor_data_flow_simple.py", "Sensor Data Flow Validation Test"),
        ("test_temperature_calculation_accuracy.py", "Temperature Calculation Accuracy Test"),
        ("test_pump_control_completeness.py", "Pump Control Logic Completeness Test"),
        ("test_energy_calculation_validation.py", "Energy Calculation Validation Test"),
        ("test_system_state_consistency.py", "System State Consistency Test"),
        ("test_error_recovery.py", "Error Recovery Testing"),
    ]
    
    # Run all tests
    results = []
    total_start_time = time.time()
    
    for test_file, test_name in tests:
        # Check if test file exists
        if not os.path.exists(test_file):
            print(f"❌ {test_name}: SKIPPED (file not found: {test_file})")
            results.append((test_name, False, 0.0, f"File not found: {test_file}"))
            continue
        
        # Run the test
        passed, duration, output = run_test(test_file, test_name)
        results.append((test_name, passed, duration, output))
    
    total_duration = time.time() - total_start_time
    
    # Generate comprehensive summary
    print(f"\n{'='*70}")
    print("📊 COMPREHENSIVE TEST SUITE SUMMARY")
    print(f"{'='*70}")
    
    passed_tests = sum(1 for _, passed, _, _ in results if passed)
    total_tests = len(results)
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests} ✅")
    print(f"Failed: {total_tests - passed_tests} ❌")
    print(f"Success Rate: {success_rate:.1f}%")
    print(f"Total Duration: {total_duration:.2f} seconds")
    
    print(f"\n📋 DETAILED RESULTS:")
    print(f"{'='*70}")
    
    for test_name, passed, duration, output in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {test_name} ({duration:.2f}s)")
    
    print(f"\n🎯 TEST COVERAGE SUMMARY:")
    print(f"{'='*70}")
    print("✅ Sensor Data Flow Validation - End-to-end sensor data processing")
    print("✅ Temperature Calculation Accuracy - All temperature calculations")
    print("✅ Pump Control Logic Completeness - All pump scenarios")
    print("✅ Energy Calculation Validation - Physics-based energy calculations")
    print("✅ System State Consistency - State integrity across operations")
    print("✅ Error Recovery Testing - System recovery from failures")
    
    if success_rate == 100.0:
        print(f"\n🎉 ALL TESTS PASSED! Comprehensive test suite completed successfully.")
        print("The Solar Heating System v3 basic functionality is thoroughly tested.")
        return True
    else:
        print(f"\n⚠️  {total_tests - passed_tests} TESTS FAILED. System needs attention.")
        print("Please review the failed tests and fix any issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)





