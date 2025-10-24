#!/bin/bash

# One-liner SSH debug commands for cartridge heater issue
# Replace PI_IP with your Raspberry Pi's IP address

PI_IP="192.168.1.100"  # UPDATE THIS WITH YOUR PI'S IP

echo "🔍 One-liner SSH Debug Commands"
echo "==============================="
echo ""
echo "Run these commands one by one:"
echo ""

echo "1. Check service status:"
echo "ssh pi@$PI_IP 'systemctl status solar_heating_main.service'"
echo ""

echo "2. Check recent logs:"
echo "ssh pi@$PI_IP 'journalctl -u solar_heating_main.service -n 20'"
echo ""

echo "3. Test MQTT:"
echo "ssh pi@$PI_IP 'mosquitto_pub -h localhost -t test/debug -m test'"
echo ""

echo "4. Check temperatures:"
echo "ssh pi@$PI_IP 'cd sun_heat_and_ftx/python/v3 && python3 -c \"from sensor_manager import SensorManager; sm = SensorManager(); print(sm.get_all_temperatures())\"'"
echo ""

echo "5. Check system state:"
echo "ssh pi@$PI_IP 'cd sun_heat_and_ftx/python/v3 && python3 -c \"from main_system import SolarHeatingSystem; s = SolarHeatingSystem(); print(s.system_state)\"'"
echo ""

echo "6. Monitor MQTT (run this and let it run for a while):"
echo "ssh pi@$PI_IP 'mosquitto_sub -h localhost -t solar_heating/+ -v'"
echo ""

echo "7. Emergency stop (if heater is stuck on):"
echo "ssh pi@$PI_IP 'sudo systemctl stop solar_heating_main.service'"
echo ""

echo "⚠️  Remember to update PI_IP with your actual Raspberry Pi IP address!"
