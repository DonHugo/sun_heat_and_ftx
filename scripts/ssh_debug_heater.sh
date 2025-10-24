#!/bin/bash

# SSH Debug Script for Cartridge Heater Issue
# This script connects to Raspberry Pi and runs debugging commands

# Configuration - UPDATE THESE VALUES
PI_HOST="your-pi-ip-address"  # Replace with your Raspberry Pi IP
PI_USER="pi"                  # Replace with your username
PI_PATH="/home/pi/sun_heat_and_ftx"  # Path to project on Pi

echo "🔍 SSH Debug Script for Cartridge Heater"
echo "========================================="
echo ""

# Check if SSH is available
if ! command -v ssh &> /dev/null; then
    echo "❌ SSH not found. Please install SSH client."
    exit 1
fi

# Check if we can connect to the Pi
echo "📡 Testing SSH connection to $PI_USER@$PI_HOST..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $PI_USER@$PI_HOST "echo 'SSH connection successful'" 2>/dev/null; then
    echo "❌ Cannot connect to Raspberry Pi via SSH"
    echo ""
    echo "Please check:"
    echo "1. Raspberry Pi IP address: $PI_HOST"
    echo "2. Username: $PI_USER"
    echo "3. SSH is enabled on the Pi"
    echo "4. SSH key authentication is set up"
    echo ""
    echo "To enable SSH on Pi:"
    echo "sudo systemctl enable ssh"
    echo "sudo systemctl start ssh"
    echo ""
    echo "To set up SSH key authentication:"
    echo "ssh-copy-id $PI_USER@$PI_HOST"
    exit 1
fi

echo "✅ SSH connection successful"
echo ""

# Function to run command on Pi
run_on_pi() {
    local cmd="$1"
    local description="$2"
    
    echo "📋 $description"
    echo "----------------------------------------"
    ssh $PI_USER@$PI_HOST "cd $PI_PATH && $cmd"
    echo ""
}

# 1. Check service status
run_on_pi "systemctl status solar_heating_main.service --no-pager -l" "1. Solar Heating Service Status"

# 2. Check recent logs
run_on_pi "journalctl -u solar_heating_main.service -n 30 --no-pager" "2. Recent Service Logs"

# 3. Check if MQTT is working
run_on_pi "systemctl status mosquitto --no-pager" "3. MQTT Service Status"

# 4. Test MQTT connectivity
run_on_pi "timeout 5 mosquitto_pub -h localhost -t 'test/debug' -m 'Heater debug test' -q 1 && echo 'MQTT publish successful' || echo 'MQTT publish failed'" "4. MQTT Connectivity Test"

# 5. Check system temperatures
run_on_pi "python3 -c \"
import sys
sys.path.append('python/v3')
try:
    from sensor_manager import SensorManager
    sm = SensorManager()
    print('Current temperatures:')
    for sensor, temp in sm.get_all_temperatures().items():
        print(f'  {sensor}: {temp}°C')
except Exception as e:
    print(f'Error reading temperatures: {e}')
\"" "5. Current System Temperatures"

# 6. Check system state for heater
run_on_pi "python3 -c \"
import sys
sys.path.append('python/v3')
try:
    from main_system import SolarHeatingSystem
    system = SolarHeatingSystem()
    print('System state (heater-related):')
    for key, value in system.system_state.items():
        if 'heater' in key.lower() or 'cartridge' in key.lower():
            print(f'  {key}: {value}')
    print('All system state:')
    for key, value in system.system_state.items():
        print(f'  {key}: {value}')
except Exception as e:
    print(f'Error checking system state: {e}')
\"" "6. System State (Heater-related)"

# 7. Check MQTT messages in real-time (run for 10 seconds)
echo "📋 7. Real-time MQTT Messages (10 seconds)"
echo "----------------------------------------"
echo "Monitoring MQTT messages for 10 seconds..."
ssh $PI_USER@$PI_HOST "timeout 10 mosquitto_sub -h localhost -t 'solar_heating/+' -v" || echo "MQTT monitoring completed or failed"
echo ""

# 8. Check Home Assistant MQTT integration
echo "📋 8. Home Assistant MQTT Check"
echo "-------------------------------"
echo "Please check in Home Assistant:"
echo "1. Go to Settings > Devices & Services > MQTT"
echo "2. Check if MQTT integration is working"
echo "3. Look for 'solar_heating' devices"
echo "4. Check for any 'heater' or 'cartridge' entities"
echo ""

# 9. Emergency procedures
echo "📋 9. Emergency Procedures"
echo "--------------------------"
echo "If heater is stuck on:"
echo "1. Stop service: sudo systemctl stop solar_heating_main.service"
echo "2. Check emergency stop procedures"
echo "3. Verify physical heater status"
echo ""

# 10. Manual heater test (if safe)
echo "📋 10. Manual Heater Test (SAFETY WARNING)"
echo "------------------------------------------"
echo "⚠️  WARNING: Only run this if you're sure it's safe!"
echo "To test heater manually, run on Pi:"
echo "cd $PI_PATH/python/v3"
echo "python3 -c \"from main_system import SolarHeatingSystem; s = SolarHeatingSystem(); s.manual_heater_test()\""
echo ""

echo "🔧 Summary and Next Steps:"
echo "=========================="
echo "1. Review the output above for any errors"
echo "2. Check if MQTT messages are being sent"
echo "3. Verify Home Assistant MQTT integration"
echo "4. If heater is stuck on, use emergency procedures"
echo "5. Update GitHub issue #5 with findings"
echo ""
echo "🔗 GitHub Issue: https://github.com/DonHugo/sun_heat_and_ftx/issues/5"
