#!/bin/bash

# Monitor MQTT messages for cartridge heater
# This script helps you see what MQTT messages are being sent about the heater

echo "🔍 MQTT Heater Monitor"
echo "======================"
echo ""

# Check if mosquitto_sub is available
if ! command -v mosquitto_sub &> /dev/null; then
    echo "❌ mosquitto_sub not found. Install with:"
    echo "   sudo apt-get install mosquitto-clients"
    exit 1
fi

echo "📡 Monitoring MQTT messages for heater..."
echo "Press Ctrl+C to stop"
echo ""

# Monitor all solar heating MQTT messages
echo "Monitoring all solar_heating MQTT topics:"
echo "----------------------------------------"
mosquitto_sub -h localhost -t "solar_heating/+" -v

# Alternative: Monitor specific heater topics
# echo "Monitoring heater-specific topics:"
# echo "---------------------------------"
# mosquitto_sub -h localhost -t "solar_heating/heater_+" -v
