#!/usr/bin/env python3
"""
Hardware Connection Test Script for Solar Heating System v3
Tests and displays information about hardware connections
"""

import sys
import time
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports() -> Dict[str, bool]:
    """Test if hardware libraries can be imported"""
    results = {}
    
    print("=== Testing Hardware Library Imports ===")
    
    # Test megabas
    try:
        import megabas
        results['megabas'] = True
        print("✅ megabas library imported successfully")
    except ImportError as e:
        results['megabas'] = False
        print(f"❌ megabas library import failed: {e}")
    
    # Test librtd
    try:
        import librtd
        results['librtd'] = True
        print("✅ librtd library imported successfully")
    except ImportError as e:
        results['librtd'] = False
        print(f"❌ librtd library import failed: {e}")
    
    # Test lib4relind
    try:
        import lib4relind
        results['lib4relind'] = True
        print("✅ lib4relind library imported successfully")
    except ImportError as e:
        results['lib4relind'] = False
        print(f"❌ lib4relind library import failed: {e}")
    
    return results

def test_hardware_boards() -> Dict[str, Dict[str, Any]]:
    """Test individual hardware boards"""
    results = {}
    
    print("\n=== Testing Hardware Boards ===")
    
    # Test MegaBAS on stack 3
    print("Testing MegaBAS on stack 3...")
    try:
        import megabas
        for input_id in range(1, 9):
            try:
                value = megabas.getRIn1K(3, input_id)
                if value != 60:  # 60 is error value
                    print(f"  Input {input_id}: {value}")
                else:
                    print(f"  Input {input_id}: Error (60)")
            except Exception as e:
                print(f"  Input {input_id}: Error - {e}")
        results['megabas'] = {'stack': 3, 'status': 'tested'}
    except Exception as e:
        print(f"❌ MegaBAS test failed: {e}")
        results['megabas'] = {'stack': 3, 'status': 'failed', 'error': str(e)}
    
    # Test RTD on stack 0
    print("\nTesting RTD on stack 0...")
    try:
        import librtd
        for sensor_id in range(1, 5):
            try:
                temp = librtd.get(0, sensor_id)
                print(f"  Sensor {sensor_id}: {temp}°C")
            except Exception as e:
                print(f"  Sensor {sensor_id}: Error - {e}")
        results['rtd'] = {'stack': 0, 'status': 'tested'}
    except Exception as e:
        print(f"❌ RTD test failed: {e}")
        results['rtd'] = {'stack': 0, 'status': 'failed', 'error': str(e)}
    
    # Test 4RELIND on stack 2
    print("\nTesting 4RELIND on stack 2...")
    try:
        import lib4relind
        for relay_id in range(1, 5):
            try:
                state = lib4relind.get_relay(2, relay_id)
                print(f"  Relay {relay_id}: {'ON' if state else 'OFF'}")
            except Exception as e:
                print(f"  Relay {relay_id}: Error - {e}")
        results['4relind'] = {'stack': 2, 'status': 'tested'}
    except Exception as e:
        print(f"❌ 4RELIND test failed: {e}")
        results['4relind'] = {'stack': 2, 'status': 'failed', 'error': str(e)}
    
    return results

def test_hardware_interface() -> Dict[str, Any]:
    """Test the hardware interface class"""
    print("\n=== Testing Hardware Interface ===")
    
    try:
        from hardware_interface import HardwareInterface
        
        # Test hardware mode
        print("Testing hardware interface in hardware mode...")
        hw = HardwareInterface(simulation_mode=False)
        
        # Test hardware connection
        test_results = hw.test_hardware_connection()
        print(f"Hardware test results: {test_results}")
        
        # Test reading temperatures
        print("\nTesting temperature readings...")
        temperatures = hw.read_all_temperatures()
        for sensor, temp in temperatures.items():
            print(f"  {sensor}: {temp}°C")
        
        # Test relay control
        print("\nTesting relay control...")
        for relay_id in range(1, 5):
            current_state = hw.get_relay_state(relay_id)
            print(f"  Relay {relay_id}: {'ON' if current_state else 'OFF'}")
        
        return {
            'status': 'success',
            'test_results': test_results,
            'temperatures': temperatures
        }
        
    except Exception as e:
        print(f"❌ Hardware interface test failed: {e}")
        return {'status': 'failed', 'error': str(e)}

def check_i2c_buses():
    """Check I2C bus availability"""
    print("\n=== Checking I2C Buses ===")
    
    import os
    
    # Check I2C device files
    i2c_buses = []
    for i in range(10):  # Check buses 0-9
        bus_path = f"/dev/i2c-{i}"
        if os.path.exists(bus_path):
            i2c_buses.append(i)
            print(f"✅ I2C bus {i} found: {bus_path}")
        else:
            print(f"❌ I2C bus {i} not found")
    
    return i2c_buses

def main():
    """Main test function"""
    print("=== Solar Heating System v3 - Hardware Connection Test ===")
    print(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # Check I2C buses
    i2c_buses = check_i2c_buses()
    
    # Test imports
    import_results = test_imports()
    
    # Test hardware boards
    board_results = test_hardware_boards()
    
    # Test hardware interface
    interface_results = test_hardware_interface()
    
    # Summary
    print("\n" + "="*60)
    print("=== TEST SUMMARY ===")
    print(f"I2C buses available: {i2c_buses}")
    print(f"Libraries imported: {sum(import_results.values())}/{len(import_results)}")
    print(f"Hardware interface: {interface_results.get('status', 'unknown')}")
    
    if interface_results.get('status') == 'success':
        test_results = interface_results.get('test_results', {})
        print(f"Hardware test results: {test_results}")
        
        if test_results.get('overall', False):
            print("🎉 All hardware tests passed!")
        else:
            print("⚠️ Some hardware tests failed")
    
    print("\nTest completed!")

if __name__ == "__main__":
    main()
