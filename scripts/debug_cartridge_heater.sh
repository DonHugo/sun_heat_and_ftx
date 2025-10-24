#!/bin/bash

# Debug Cartridge Heater Issue
# This script helps troubleshoot why cartridge heater might be activated but not visible in Home Assistant

echo "🔍 Cartridge Heater Debug Script"
echo "================================"
echo ""

# Check if we're on Raspberry Pi
if [ -f /proc/device-tree/model ]; then
    echo "✅ Running on Raspberry Pi"
    cat /proc/device-tree/model
    echo ""
else
    echo "⚠️  Not running on Raspberry Pi - some checks may not work"
    echo ""
fi

# 1. Check systemd service status
echo "📋 1. Checking Solar Heating Service Status:"
echo "-------------------------------------------"
systemctl status solar_heating_main.service --no-pager -l
echo ""

# 2. Check recent logs for heater activity
echo "📋 2. Checking Recent Logs for Heater Activity:"
echo "---------------------------------------------"
echo "Last 50 lines of solar heating logs:"
journalctl -u solar_heating_main.service -n 50 --no-pager
echo ""

# 3. Check for MQTT connectivity
echo "📋 3. Checking MQTT Connectivity:"
echo "---------------------------------"
echo "Testing MQTT connection..."
if command -v mosquitto_pub &> /dev/null; then
    echo "✅ Mosquitto client available"
    echo "Testing MQTT publish (this will show if MQTT is working):"
    mosquitto_pub -h localhost -t "test/debug" -m "Cartridge heater debug test" -q 1
    if [ $? -eq 0 ]; then
        echo "✅ MQTT publish successful"
    else
        echo "❌ MQTT publish failed"
    fi
else
    echo "⚠️  Mosquitto client not available"
fi
echo ""

# 4. Check MQTT messages for heater
echo "📋 4. Checking MQTT Messages for Heater:"
echo "---------------------------------------"
echo "Looking for heater-related MQTT topics..."
echo "Run this command to monitor MQTT messages:"
echo "mosquitto_sub -h localhost -t 'solar_heating/#' -v"
echo ""
echo "Or check for specific heater topics:"
echo "mosquitto_sub -h localhost -t 'solar_heating/heater_#' -v"
echo ""

# 5. Check GPIO/Relay status
echo "📋 5. Checking GPIO/Relay Status:"
echo "---------------------------------"
if [ -f /sys/class/gpio/export ]; then
    echo "GPIO system available"
    echo "Checking for heater relay GPIO..."
    # This would need to be customized based on your GPIO setup
    echo "⚠️  GPIO check needs to be customized for your setup"
else
    echo "⚠️  GPIO system not accessible"
fi
echo ""

# 6. Check Home Assistant configuration
echo "📋 6. Home Assistant Configuration Check:"
echo "-----------------------------------------"
echo "Check these in Home Assistant:"
echo "1. Go to Settings > Devices & Services > MQTT"
echo "2. Check if MQTT integration is working"
echo "3. Look for 'solar_heating' devices"
echo "4. Check for any 'heater' or 'cartridge' entities"
echo ""

# 7. Check system temperature readings
echo "📋 7. Checking System Temperature Readings:"
echo "-----------------------------------------"
if [ -f "python/v3/main_system.py" ]; then
    echo "Running temperature check..."
    cd python/v3
    python3 -c "
import sys
sys.path.append('.')
try:
    from sensor_manager import SensorManager
    sm = SensorManager()
    print('Current temperatures:')
    for sensor, temp in sm.get_all_temperatures().items():
        print(f'  {sensor}: {temp}°C')
except Exception as e:
    print(f'Error reading temperatures: {e}')
"
    cd ../..
else
    echo "⚠️  Cannot find main system files"
fi
echo ""

# 8. Check for heater control logic
echo "📋 8. Checking Heater Control Logic:"
echo "------------------------------------"
echo "Looking for heater control in system state..."
if [ -f "python/v3/main_system.py" ]; then
    cd python/v3
    python3 -c "
import sys
sys.path.append('.')
try:
    from main_system import SolarHeatingSystem
    system = SolarHeatingSystem()
    print('System state:')
    for key, value in system.system_state.items():
        if 'heater' in key.lower() or 'cartridge' in key.lower():
            print(f'  {key}: {value}')
except Exception as e:
    print(f'Error checking system state: {e}')
"
    cd ../..
else
    echo "⚠️  Cannot find main system files"
fi
echo ""

# 9. Manual heater test
echo "📋 9. Manual Heater Test:"
echo "------------------------"
echo "⚠️  WARNING: This will test the heater manually!"
echo "Only run this if you're sure it's safe to do so."
echo ""
echo "To test heater manually, run:"
echo "cd python/v3"
echo "python3 -c \"from main_system import SolarHeatingSystem; s = SolarHeatingSystem(); s.manual_heater_test()\""
echo ""

# 10. Emergency stop check
echo "📋 10. Emergency Stop Check:"
echo "----------------------------"
echo "If heater is stuck on, you can:"
echo "1. Stop the service: sudo systemctl stop solar_heating_main.service"
echo "2. Check emergency stop: Check if emergency stop is activated"
echo "3. Manual GPIO control: Turn off heater relay manually"
echo ""

echo "🔧 Next Steps:"
echo "=============="
echo "1. Check the MQTT messages in real-time"
echo "2. Verify Home Assistant MQTT integration"
echo "3. Check system logs for heater activation events"
echo "4. Test heater control manually if safe"
echo "5. If heater is stuck on, use emergency stop procedures"
echo ""
echo "⚠️  SAFETY WARNING: If you suspect the heater is on but not showing in HA,"
echo "    check the physical system immediately for safety!"
