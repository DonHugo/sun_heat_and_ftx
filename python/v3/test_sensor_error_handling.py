#!/usr/bin/env python3
"""
Test Suite for Sensor Error Handling (Issue #50 Fix)
Tests robust sensor reading with retry logic, health monitoring, and graceful degradation
"""

import sys
import time
from typing import Optional

# Mock hardware interface for testing
class MockHardwareInterface:
    """Mock hardware interface for testing sensor error handling"""
    
    def __init__(self):
        self.rtd_fail_count = {}  # sensor_id -> fail_count
        self.megabas_fail_count = {}
        self.rtd_scenario = "normal"  # normal, transient_error, permanent_error
        self.megabas_scenario = "normal"
    
    def set_rtd_scenario(self, sensor_id: int, scenario: str, fail_count: int = 0):
        """Set test scenario for RTD sensor"""
        self.rtd_scenario = scenario
        self.rtd_fail_count[sensor_id] = fail_count
    
    def set_megabas_scenario(self, sensor_id: int, scenario: str, fail_count: int = 0):
        """Set test scenario for MegaBAS sensor"""
        self.megabas_scenario = scenario
        self.megabas_fail_count[sensor_id] = fail_count
    
    def read_rtd_temperature(self, sensor_id: int, stack: int = None) -> Optional[float]:
        """Mock RTD sensor read with configurable failure scenarios"""
        # Check failure counter
        fail_count = self.rtd_fail_count.get(sensor_id, 0)
        
        if self.rtd_scenario == "permanent_error":
            return None
        elif self.rtd_scenario == "transient_error":
            if fail_count > 0:
                self.rtd_fail_count[sensor_id] = fail_count - 1
                return None
            else:
                # Success after retries
                return 25.0 + sensor_id * 5.0
        else:  # normal
            return 25.0 + sensor_id * 5.0
    
    def read_megabas_temperature(self, sensor_id: int, stack: int = None) -> Optional[float]:
        """Mock MegaBAS sensor read with configurable failure scenarios"""
        fail_count = self.megabas_fail_count.get(sensor_id, 0)
        
        if self.megabas_scenario == "permanent_error":
            return None
        elif self.megabas_scenario == "transient_error":
            if fail_count > 0:
                self.megabas_fail_count[sensor_id] = fail_count - 1
                return None
            else:
                return 20.0 + sensor_id * 3.0
        else:  # normal
            return 20.0 + sensor_id * 3.0


def test_1_sensor_health_monitor_basic():
    """Test 1: Basic sensor health monitoring"""
    print("\n" + "="*70)
    print("TEST 1: Basic Sensor Health Monitoring")
    print("="*70)
    
    from sensor_health_monitor import SensorHealthMonitor
    
    monitor = SensorHealthMonitor(stale_threshold_seconds=10)
    
    # Test successful reading
    value, status = monitor.record_reading('test_sensor_1', 25.5)
    assert value == 25.5, f"Expected 25.5, got {value}"
    assert status == monitor.STATUS_HEALTHY, f"Expected HEALTHY, got {status}"
    print("✅ Test 1.1: Successful reading recorded as HEALTHY")
    
    # Test failed reading with no last known good
    value, status = monitor.record_reading('test_sensor_2', None)
    assert value is None, f"Expected None, got {value}"
    assert status == monitor.STATUS_FAILED, f"Expected FAILED, got {status}"
    print("✅ Test 1.2: Failed reading with no history = FAILED")
    
    # Test failed reading with last known good (should use it)
    monitor.record_reading('test_sensor_3', 30.0)  # Establish good value
    time.sleep(0.1)
    value, status = monitor.record_reading('test_sensor_3', None)  # Fail
    assert value == 30.0, f"Expected 30.0 (last known good), got {value}"
    assert status == monitor.STATUS_DEGRADED, f"Expected DEGRADED, got {status}"
    print("✅ Test 1.3: Failed reading uses last known good = DEGRADED")
    
    # Test recovery
    value, status = monitor.record_reading('test_sensor_3', 32.0)  # Recover
    assert value == 32.0, f"Expected 32.0, got {value}"
    assert status == monitor.STATUS_HEALTHY, f"Expected HEALTHY, got {status}"
    print("✅ Test 1.4: Sensor recovery from DEGRADED to HEALTHY")
    
    print("\n✅ TEST 1 PASSED: Sensor health monitoring works correctly\n")
    return True


def test_2_robust_sensor_reader_retry():
    """Test 2: Robust sensor reader with retry logic"""
    print("\n" + "="*70)
    print("TEST 2: Robust Sensor Reader with Retry Logic")
    print("="*70)
    
    from sensor_reader_robust import RobustSensorReader
    
    hardware = MockHardwareInterface()
    reader = RobustSensorReader(hardware, max_retries=3, initial_backoff_ms=10)
    
    # Test 2.1: Success on first attempt
    temp, attempts = reader.read_rtd_temperature_with_retry(0)
    assert temp == 25.0, f"Expected 25.0, got {temp}"
    assert attempts == 1, f"Expected 1 attempt, got {attempts}"
    print("✅ Test 2.1: Success on first attempt")
    
    # Test 2.2: Transient error - success after 2 failures
    hardware.set_rtd_scenario(1, "transient_error", fail_count=2)
    temp, attempts = reader.read_rtd_temperature_with_retry(1)
    assert temp == 30.0, f"Expected 30.0, got {temp}"
    assert attempts == 3, f"Expected 3 attempts, got {attempts}"
    print("✅ Test 2.2: Success after 2 retries (transient error)")
    
    # Test 2.3: Permanent error - all retries fail
    hardware.set_rtd_scenario(2, "permanent_error")
    temp, attempts = reader.read_rtd_temperature_with_retry(2)
    assert temp is None, f"Expected None, got {temp}"
    assert attempts == 3, f"Expected 3 attempts, got {attempts}"
    print("✅ Test 2.3: All retries fail (permanent error)")
    
    # Test 2.4: MegaBAS sensor retry
    hardware.megabas_scenario = "normal"
    temp, attempts = reader.read_megabas_temperature_with_retry(1)
    assert temp == 23.0, f"Expected 23.0, got {temp}"
    assert attempts == 1, f"Expected 1 attempt, got {attempts}"
    print("✅ Test 2.4: MegaBAS sensor read success")
    
    print("\n✅ TEST 2 PASSED: Retry logic with exponential backoff works\n")
    return True


def test_3_integrated_error_handling():
    """Test 3: Integrated error handling (reader + monitor)"""
    print("\n" + "="*70)
    print("TEST 3: Integrated Error Handling")
    print("="*70)
    
    from sensor_health_monitor import SensorHealthMonitor
    from sensor_reader_robust import RobustSensorReader
    
    hardware = MockHardwareInterface()
    reader = RobustSensorReader(hardware, max_retries=3, initial_backoff_ms=10)
    monitor = SensorHealthMonitor(stale_threshold_seconds=2)
    
    # Scenario: Sensor works, then fails, then recovers
    
    # Step 1: Normal operation
    temp, attempts = reader.read_rtd_temperature_with_retry(0)
    value, status = monitor.record_reading('rtd_sensor_0', temp)
    assert status == monitor.STATUS_HEALTHY, "Expected HEALTHY"
    print("✅ Test 3.1: Normal operation - HEALTHY")
    
    # Step 2: Sensor fails (but we have last known good)
    hardware.set_rtd_scenario(0, "permanent_error")
    temp, attempts = reader.read_rtd_temperature_with_retry(0)
    value, status = monitor.record_reading('rtd_sensor_0', temp)
    assert status == monitor.STATUS_DEGRADED, "Expected DEGRADED"
    assert value == 25.0, "Expected last known good value"
    print("✅ Test 3.2: Sensor failure - DEGRADED (using last known good)")
    
    # Step 3: Wait for value to become stale
    time.sleep(2.1)
    temp, attempts = reader.read_rtd_temperature_with_retry(0)
    value, status = monitor.record_reading('rtd_sensor_0', temp)
    assert status == monitor.STATUS_FAILED, "Expected FAILED (stale)"
    assert value is None, "Expected None for stale value"
    print("✅ Test 3.3: Value becomes stale - FAILED")
    
    # Step 4: Sensor recovers
    hardware.set_rtd_scenario(0, "normal")
    temp, attempts = reader.read_rtd_temperature_with_retry(0)
    value, status = monitor.record_reading('rtd_sensor_0', temp)
    assert status == monitor.STATUS_HEALTHY, "Expected HEALTHY (recovered)"
    assert value == 25.0, "Expected fresh value"
    print("✅ Test 3.4: Sensor recovers - HEALTHY")
    
    print("\n✅ TEST 3 PASSED: Integrated error handling works correctly\n")
    return True


def test_4_sensor_health_summary():
    """Test 4: Sensor health summary generation"""
    print("\n" + "="*70)
    print("TEST 4: Sensor Health Summary")
    print("="*70)
    
    from sensor_health_monitor import SensorHealthMonitor
    
    monitor = SensorHealthMonitor(stale_threshold_seconds=5)
    
    # Create a mix of sensor states
    monitor.record_reading('sensor_healthy_1', 25.0)
    monitor.record_reading('sensor_healthy_2', 30.0)
    
    monitor.record_reading('sensor_degraded_1', 35.0)  # Establish value
    monitor.record_reading('sensor_degraded_1', None)  # Fail (will use last known good)
    
    monitor.record_reading('sensor_failed_1', None)  # No history, immediate fail
    
    # Get summary
    summary = monitor.get_sensor_health_summary()
    
    assert summary['statistics']['healthy'] == 2, "Expected 2 healthy sensors"
    assert summary['statistics']['degraded'] == 1, "Expected 1 degraded sensor"
    assert summary['statistics']['failed'] == 1, "Expected 1 failed sensor"
    print("✅ Test 4.1: Statistics correct (2 healthy, 1 degraded, 1 failed)")
    
    # Check failed/degraded sensor lists
    failed = monitor.get_failed_sensors()
    degraded = monitor.get_degraded_sensors()
    assert len(failed) == 1 and 'sensor_failed_1' in failed, "Failed sensor list incorrect"
    assert len(degraded) == 1 and 'sensor_degraded_1' in degraded, "Degraded sensor list incorrect"
    print("✅ Test 4.2: Failed and degraded sensor lists correct")
    
    # Check alert threshold
    monitor._error_counts['sensor_alert_test'] = 5
    assert monitor.should_alert('sensor_alert_test', alert_threshold=5), "Should alert at threshold"
    print("✅ Test 4.3: Alert threshold detection works")
    
    print("\n✅ TEST 4 PASSED: Health summary and alerting work correctly\n")
    return True


def test_5_bulk_sensor_reading():
    """Test 5: Bulk sensor reading (all RTD and MegaBAS sensors)"""
    print("\n" + "="*70)
    print("TEST 5: Bulk Sensor Reading")
    print("="*70)
    
    from sensor_reader_robust import RobustSensorReader
    
    hardware = MockHardwareInterface()
    reader = RobustSensorReader(hardware, max_retries=2, initial_backoff_ms=10)
    
    # Read all RTD sensors
    rtd_temps, rtd_attempts = reader.read_all_rtd_sensors()
    assert len(rtd_temps) == 8, f"Expected 8 RTD sensors, got {len(rtd_temps)}"
    assert all(temp is not None for temp in rtd_temps.values()), "Some RTD sensors failed"
    print(f"✅ Test 5.1: Read all 8 RTD sensors successfully")
    
    # Read all MegaBAS sensors
    megabas_temps, megabas_attempts = reader.read_all_megabas_sensors()
    assert len(megabas_temps) == 8, f"Expected 8 MegaBAS sensors, got {len(megabas_temps)}"
    assert all(temp is not None for temp in megabas_temps.values()), "Some MegaBAS sensors failed"
    print(f"✅ Test 5.2: Read all 8 MegaBAS sensors successfully")
    
    # Test with some failures
    hardware.set_rtd_scenario(3, "permanent_error")
    hardware.set_megabas_scenario(5, "permanent_error")
    
    rtd_temps, rtd_attempts = reader.read_all_rtd_sensors()
    megabas_temps, megabas_attempts = reader.read_all_megabas_sensors()
    
    assert rtd_temps['rtd_sensor_3'] is None, "RTD sensor 3 should be None"
    assert megabas_temps['megabas_sensor_5'] is None, "MegaBAS sensor 5 should be None"
    print(f"✅ Test 5.3: Failed sensors properly return None")
    
    print("\n✅ TEST 5 PASSED: Bulk sensor reading works correctly\n")
    return True


def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*70)
    print("SENSOR ERROR HANDLING TEST SUITE (Issue #50)")
    print("Testing: Retry logic, health monitoring, graceful degradation")
    print("="*70)
    
    tests = [
        ("Sensor Health Monitor Basic", test_1_sensor_health_monitor_basic),
        ("Robust Sensor Reader Retry", test_2_robust_sensor_reader_retry),
        ("Integrated Error Handling", test_3_integrated_error_handling),
        ("Sensor Health Summary", test_4_sensor_health_summary),
        ("Bulk Sensor Reading", test_5_bulk_sensor_reading),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, "PASSED", None))
        except AssertionError as e:
            results.append((test_name, "FAILED", str(e)))
            print(f"\n❌ TEST FAILED: {test_name}")
            print(f"   Error: {e}\n")
        except Exception as e:
            results.append((test_name, "ERROR", str(e)))
            print(f"\n❌ TEST ERROR: {test_name}")
            print(f"   Error: {e}\n")
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, status, _ in results if status == "PASSED")
    failed = sum(1 for _, status, _ in results if status == "FAILED")
    errors = sum(1 for _, status, _ in results if status == "ERROR")
    
    for test_name, status, error in results:
        if status == "PASSED":
            print(f"✅ {test_name}: {status}")
        else:
            print(f"❌ {test_name}: {status}")
            if error:
                print(f"   {error}")
    
    print(f"\nTotal: {len(results)} tests")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Errors: {errors}")
    
    if failed == 0 and errors == 0:
        print("\n🎉 ALL TESTS PASSED! Issue #50 fix validated successfully.")
        return 0
    else:
        print("\n⚠️  Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
