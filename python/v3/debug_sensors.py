#!/usr/bin/env python3
"""
Debug script to test all sensor readings
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from hardware_interface import HardwareInterface
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_all_sensors():
    """Test all RTD and MegaBAS sensors"""
    print("=== Testing All Sensors ===")
    
    # Create hardware interface
    hardware = HardwareInterface(simulation_mode=False)
    
    print("\n=== RTD Sensors (Stack 0) ===")
    for sensor_id in range(8):
        temp = hardware.read_rtd_temperature(sensor_id)
        print(f"RTD Sensor {sensor_id}: {temp}°C")
    
    print("\n=== MegaBAS Sensors (Stack 3) ===")
    for sensor_id in range(1, 9):
        temp = hardware.read_megabas_temperature(sensor_id)
        print(f"MegaBAS Sensor {sensor_id}: {temp}°C")
    
    print("\n=== Key Sensor Mappings ===")
    # Test the specific sensors we're using
    solar_collector = hardware.read_megabas_temperature(6)  # MegaBAS sensor 6
    storage_tank = hardware.read_megabas_temperature(7)     # MegaBAS sensor 7
    return_line = hardware.read_megabas_temperature(8)      # MegaBAS sensor 8
    
    storage_tank_top = hardware.read_rtd_temperature(5)     # RTD sensor 5
    storage_tank_bottom = hardware.read_rtd_temperature(4)  # RTD sensor 4
    
    print(f"Solar Collector (MegaBAS 6): {solar_collector}°C")
    print(f"Storage Tank (MegaBAS 7): {storage_tank}°C")
    print(f"Return Line (MegaBAS 8): {return_line}°C")
    print(f"Storage Tank Top (RTD 5): {storage_tank_top}°C")
    print(f"Storage Tank Bottom (RTD 4): {storage_tank_bottom}°C")
    
    # Compare with RTD sensors that might be the same physical sensors
    print(f"\n=== Comparison with RTD sensors ===")
    print(f"RTD 5 vs MegaBAS 6: {storage_tank_top}°C vs {solar_collector}°C")
    print(f"RTD 6 vs MegaBAS 7: {hardware.read_rtd_temperature(6)}°C vs {storage_tank}°C")
    print(f"RTD 7 vs MegaBAS 8: {hardware.read_rtd_temperature(7)}°C vs {return_line}°C")

if __name__ == "__main__":
    test_all_sensors()
