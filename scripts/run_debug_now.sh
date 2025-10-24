#!/bin/bash

# Ready-to-run debug script for your Raspberry Pi (192.168.0.18)
# This script will immediately start debugging the cartridge heater issue

echo "🔍 Starting Cartridge Heater Debug on 192.168.0.18"
echo "=================================================="
echo ""

# Test SSH connection first
echo "📡 Testing SSH connection to pi@192.168.0.18..."
if ! ssh -o ConnectTimeout=5 pi@192.168.0.18 "echo 'Connected successfully'" 2>/dev/null; then
    echo "❌ Cannot connect to Raspberry Pi at 192.168.0.18"
    echo ""
    echo "Please check:"
    echo "1. Raspberry Pi is powered on and connected to network"
    echo "2. SSH is enabled on the Pi"
    echo "3. You can connect manually: ssh pi@192.168.0.18"
    echo ""
    echo "To enable SSH on Pi:"
    echo "sudo systemctl enable ssh"
    echo "sudo systemctl start ssh"
    exit 1
fi

echo "✅ SSH connection successful"
echo ""

# Run debugging commands
echo "📋 Running debugging commands..."
echo ""

# 1. Service status
echo "1. Service Status:"
ssh pi@192.168.0.18 "systemctl status solar_heating_main.service --no-pager -l"
echo ""

# 2. Recent logs
echo "2. Recent Logs (last 20 lines):"
ssh pi@192.168.0.18 "journalctl -u solar_heating_main.service -n 20 --no-pager"
echo ""

# 3. MQTT test
echo "3. MQTT Test:"
ssh pi@192.168.0.18 "timeout 3 mosquitto_pub -h localhost -t 'test/heater_debug' -m 'Test message' -q 1 && echo '✅ MQTT working' || echo '❌ MQTT failed'"
echo ""

# 4. System temperatures
echo "4. System Temperatures:"
ssh pi@192.168.0.18 "cd sun_heat_and_ftx/python/v3 && python3 -c \"
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
\""
echo ""

# 5. System state (heater-related)
echo "5. System State (Heater-related):"
ssh pi@192.168.0.18 "cd sun_heat_and_ftx/python/v3 && python3 -c \"
import sys
sys.path.append('.')
try:
    from main_system import SolarHeatingSystem
    system = SolarHeatingSystem()
    print('Heater-related system state:')
    for key, value in system.system_state.items():
        if 'heater' in key.lower() or 'cartridge' in key.lower():
            print(f'  {key}: {value}')
    print('All system state:')
    for key, value in system.system_state.items():
        print(f'  {key}: {value}')
except Exception as e:
    print(f'Error checking system state: {e}')
\""
echo ""

# 6. MQTT monitoring (10 seconds)
echo "6. MQTT Messages (10 seconds - look for heater messages):"
echo "   (Press Ctrl+C to stop early if needed)"
ssh pi@192.168.0.18 "timeout 10 mosquitto_sub -h localhost -t 'solar_heating/+' -v" || echo "MQTT monitoring completed"
echo ""

# 7. Emergency check
echo "7. Emergency Check:"
echo "If you suspect the heater is stuck on, run this command:"
echo "ssh pi@192.168.0.18 'sudo systemctl stop solar_heating_main.service'"
echo ""

echo "🔧 Summary:"
echo "==========="
echo "1. Check the output above for any errors"
echo "2. Look for MQTT messages about the heater"
echo "3. Check if heater state is being published"
echo "4. If heater is stuck on, stop the service immediately"
echo "5. Update GitHub issue #5 with your findings"
echo ""
echo "🔗 GitHub Issue: https://github.com/DonHugo/sun_heat_and_ftx/issues/5"
echo ""
echo "⚠️  SAFETY: If you see the heater is on but not in Home Assistant,"
echo "    stop the service immediately for safety!"
