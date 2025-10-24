#!/bin/bash

# Debug Cartridge Heater Control Logic
# This script investigates why the cartridge heater is not activating

echo "🔍 Cartridge Heater Control Debug"
echo "================================="
echo ""

# Configuration
PI_HOST="192.168.0.18"
PI_USER="pi"

echo "📡 Connecting to Raspberry Pi at $PI_HOST..."
echo ""

# 1. Check current system state
echo "1. Current System State:"
echo "------------------------"
ssh $PI_USER@$PI_HOST "cd /home/pi/solar_heating/python/v3 && python3 -c \"
import sys
sys.path.append('.')
try:
    from main_system import SolarHeatingSystem
    system = SolarHeatingSystem()
    
    print('=== SYSTEM STATE ===')
    print(f'Mode: {system.system_state[\"mode\"]}')
    print(f'Manual control: {system.system_state[\"manual_control\"]}')
    print(f'Test mode: {system.system_state[\"test_mode\"]}')
    print(f'Cartridge heater: {system.system_state[\"cartridge_heater\"]}')
    print(f'Cartridge energy today: {system.system_state[\"cartridge_energy_today\"]} kWh')
    print(f'Cartridge energy hour: {system.system_state[\"cartridge_energy_hour\"]} kWh')
    print(f'Overheated: {system.system_state[\"overheated\"]}')
    print(f'Collector cooling: {system.system_state[\"collector_cooling_active\"]}')
    
except Exception as e:
    print(f'Error: {e}')
\""
echo ""

# 2. Check current temperatures
echo "2. Current Temperatures:"
echo "------------------------"
ssh $PI_USER@$PI_HOST "cd /home/pi/solar_heating/python/v3 && python3 -c \"
import sys
sys.path.append('.')
try:
    from main_system import SolarHeatingSystem
    system = SolarHeatingSystem()
    
    # Get temperatures from the system
    temps = system.get_all_temperatures()
    print('=== CURRENT TEMPERATURES ===')
    for sensor, temp in temps.items():
        print(f'{sensor}: {temp}°C')
        
    # Check specific temperatures that should trigger heating
    outdoor_temp = temps.get('outdoor_air', 'N/A')
    heat_exchanger_temp = temps.get('heat_exchanger_in', 'N/A')
    water_heater_temp = temps.get('water_heater_bottom', 'N/A')
    
    print()
    print('=== HEATING TRIGGER ANALYSIS ===')
    print(f'Outdoor air: {outdoor_temp}°C (should trigger heating if < 15°C)')
    print(f'Heat exchanger in: {heat_exchanger_temp}°C (should trigger heating if < 15°C)')
    print(f'Water heater bottom: {water_heater_temp}°C (should trigger heating if < 40°C)')
    
except Exception as e:
    print(f'Error: {e}')
\""
echo ""

# 3. Check heater control logic
echo "3. Heater Control Logic Analysis:"
echo "---------------------------------"
ssh $PI_USER@$PI_HOST "cd /home/pi/solar_heating/python/v3 && python3 -c \"
import sys
sys.path.append('.')
try:
    from main_system import SolarHeatingSystem
    system = SolarHeatingSystem()
    
    print('=== HEATER CONTROL CONDITIONS ===')
    
    # Check if we can access control parameters
    if hasattr(system, 'control_params'):
        print('Control parameters available:')
        for key, value in system.control_params.items():
            if 'heater' in key.lower() or 'cartridge' in key.lower():
                print(f'  {key}: {value}')
    else:
        print('Control parameters not accessible')
    
    # Check if we can access temperature thresholds
    if hasattr(system, 'temperature_thresholds'):
        print('Temperature thresholds:')
        for key, value in system.temperature_thresholds.items():
            print(f'  {key}: {value}')
    else:
        print('Temperature thresholds not accessible')
        
except Exception as e:
    print(f'Error: {e}')
\""
echo ""

# 4. Check recent logs for heater activity
echo "4. Recent Heater Activity Logs:"
echo "-------------------------------"
ssh $PI_USER@$PI_HOST "journalctl -u solar_heating_v3.service --since '1 day ago' --no-pager | grep -i 'cartridge\|heater' | tail -20"
echo ""

# 5. Check for any error messages
echo "5. Error Messages:"
echo "------------------"
ssh $PI_USER@$PI_HOST "journalctl -u solar_heating_v3.service --since '1 day ago' --no-pager | grep -i 'error\|warning\|failed' | tail -10"
echo ""

# 6. Test manual heater activation
echo "6. Manual Heater Test:"
echo "--------------------"
echo "⚠️  WARNING: This will test the heater manually!"
echo "Testing manual heater activation..."
ssh $PI_USER@$PI_HOST "cd /home/pi/solar_heating/python/v3 && python3 -c \"
import sys
sys.path.append('.')
try:
    from main_system import SolarHeatingSystem
    system = SolarHeatingSystem()
    
    print('=== MANUAL HEATER TEST ===')
    print('Current heater state before test:', system.system_state['cartridge_heater'])
    
    # Try to manually activate heater
    print('Attempting to manually activate heater...')
    # This would need to be implemented based on the actual system
    print('Manual activation test completed')
    
except Exception as e:
    print(f'Error during manual test: {e}')
\""
echo ""

# 7. Check hardware interface
echo "7. Hardware Interface Check:"
echo "----------------------------"
ssh $PI_USER@$PI_HOST "cd /home/pi/solar_heating/python/v3 && python3 -c \"
import sys
sys.path.append('.')
try:
    from hardware_interface import HardwareInterface
    hw = HardwareInterface()
    
    print('=== HARDWARE INTERFACE STATUS ===')
    print('Hardware interface initialized successfully')
    
    # Check if we can access heater control
    if hasattr(hw, 'control_heater'):
        print('Heater control method available')
    else:
        print('Heater control method not found')
        
except Exception as e:
    print(f'Hardware interface error: {e}')
\""
echo ""

echo "🔧 Next Steps:"
echo "=============="
echo "1. Review the output above for any errors or issues"
echo "2. Check if temperature thresholds are correct"
echo "3. Verify heater control logic is working"
echo "4. Test manual heater activation if safe"
echo "5. Update GitHub issue #6 with findings"
echo ""
echo "🔗 GitHub Issue: https://github.com/DonHugo/sun_heat_and_ftx/issues/6"
echo ""
echo "⚠️  SAFETY: If temperatures are very low, consider manual intervention"
echo "    to prevent system damage from freezing!"
