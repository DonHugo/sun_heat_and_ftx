#!/bin/bash

# Quick SSH Debug for Cartridge Heater
# Customize the variables below for your setup

# ===== CONFIGURATION - UPDATE THESE =====
PI_HOST="192.168.0.18"  # Your Raspberry Pi IP address
PI_USER="pi"             # Replace with your username
# ========================================

echo "🔍 Quick SSH Debug for Cartridge Heater"
echo "======================================="
echo ""

# Test SSH connection
echo "📡 Testing SSH connection to $PI_USER@$PI_HOST..."
if ! ssh -o ConnectTimeout=5 $PI_USER@$PI_HOST "echo 'Connected successfully'" 2>/dev/null; then
    echo "❌ Cannot connect to Raspberry Pi"
    echo "Please update the PI_HOST and PI_USER variables in this script"
    echo "Current settings:"
    echo "  PI_HOST: $PI_HOST"
    echo "  PI_USER: $PI_USER"
    exit 1
fi

echo "✅ SSH connection successful"
echo ""

# Run debugging commands
echo "📋 Running debugging commands on Raspberry Pi..."
echo ""

# 1. Service status
echo "1. Service Status:"
ssh $PI_USER@$PI_HOST "systemctl status solar_heating_main.service --no-pager -l"
echo ""

# 2. Recent logs
echo "2. Recent Logs:"
ssh $PI_USER@$PI_HOST "journalctl -u solar_heating_main.service -n 20 --no-pager"
echo ""

# 3. MQTT test
echo "3. MQTT Test:"
ssh $PI_USER@$PI_HOST "timeout 3 mosquitto_pub -h localhost -t 'test/heater_debug' -m 'Test message' -q 1 && echo 'MQTT working' || echo 'MQTT failed'"
echo ""

# 4. System temperatures
echo "4. System Temperatures:"
ssh $PI_USER@$PI_HOST "cd sun_heat_and_ftx/python/v3 && python3 -c \"
import sys
sys.path.append('.')
try:
    from sensor_manager import SensorManager
    sm = SensorManager()
    for sensor, temp in sm.get_all_temperatures().items():
        print(f'{sensor}: {temp}°C')
except Exception as e:
    print(f'Error: {e}')
\""
echo ""

# 5. System state
echo "5. System State:"
ssh $PI_USER@$PI_HOST "cd sun_heat_and_ftx/python/v3 && python3 -c \"
import sys
sys.path.append('.')
try:
    from main_system import SolarHeatingSystem
    system = SolarHeatingSystem()
    for key, value in system.system_state.items():
        if 'heater' in key.lower():
            print(f'{key}: {value}')
except Exception as e:
    print(f'Error: {e}')
\""
echo ""

# 6. MQTT monitoring (5 seconds)
echo "6. MQTT Messages (5 seconds):"
ssh $PI_USER@$PI_HOST "timeout 5 mosquitto_sub -h localhost -t 'solar_heating/+' -v" || echo "MQTT monitoring completed"
echo ""

echo "🔧 Next Steps:"
echo "1. Check if MQTT messages are being sent"
echo "2. Verify Home Assistant MQTT integration"
echo "3. If heater is stuck on, stop service: sudo systemctl stop solar_heating_main.service"
echo "4. Update GitHub issue #5 with findings"
