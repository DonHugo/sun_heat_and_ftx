#!/bin/bash

# Solar Heating System v3 - Folder Cleanup Script
# This script removes unnecessary files while keeping essential ones

set -e  # Exit on any error

echo "🧹 Cleaning up v3 folder..."
echo "============================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to safely remove files
safe_remove() {
    if [ -f "$1" ]; then
        echo -e "${YELLOW}🗑️  Removing: $1${NC}"
        rm "$1"
        echo -e "${GREEN}✅ Removed: $1${NC}"
    else
        echo -e "${BLUE}ℹ️  File not found: $1${NC}"
    fi
}

# Function to safely remove directories
safe_remove_dir() {
    if [ -d "$1" ]; then
        echo -e "${YELLOW}🗑️  Removing directory: $1${NC}"
        rm -rf "$1"
        echo -e "${GREEN}✅ Removed directory: $1${NC}"
    else
        echo -e "${BLUE}ℹ️  Directory not found: $1${NC}"
    fi
}

echo -e "${BLUE}📋 Files to be removed:${NC}"

# Test files (development only)
echo "• Test files (development only)"
safe_remove "test_realtime_energy_sensor.py"
safe_remove "test_hall_sensor.py"
safe_remove "test_pellet_stove_data.py"
safe_remove "manual_control_test.py"
safe_remove "test_controls.py"
safe_remove "test_hardware_connection.py"
safe_remove "test_basic.py"
safe_remove "test_simple_mqtt.py"
safe_remove "test_mqtt_integration.py"
safe_remove "test_full_system.py"
safe_remove "test_mqtt.py"
safe_remove "test_system.py"
safe_remove "test_v3.sh"
safe_remove "test_system_simple.py"

# Duplicate/Alternative files
echo -e "${BLUE}• Duplicate/Alternative files${NC}"
safe_remove "main.py"  # Conflicts with main_system.py
safe_remove "main_system_simple.py"  # Redundant
safe_remove "test_system_simple.py"  # Redundant

# Development tools
echo -e "${BLUE}• Development tools${NC}"
safe_remove "debug_sensors.py"
safe_remove "mqtt_topic_monitor.py"
safe_remove "simple_mqtt_monitor.py"

# Documentation that can be removed
echo -e "${BLUE}• Documentation that can be removed${NC}"
safe_remove "TEST_RESULTS.md"
safe_remove "PELLET_STOVE_VERIFICATION.md"

# Log files (should not be in repo)
echo -e "${BLUE}• Log files (should not be in repo)${NC}"
safe_remove "solar_heating_v3.log"

# Virtual environment (should not be in repo)
echo -e "${BLUE}• Virtual environment (should not be in repo)${NC}"
safe_remove_dir "venv"

# Python cache
echo -e "${BLUE}• Python cache files${NC}"
safe_remove_dir "__pycache__"

echo -e "${GREEN}✅ Cleanup completed!${NC}"
echo
echo -e "${BLUE}📋 Essential files kept:${NC}"
echo "• main_system.py (main system)"
echo "• mqtt_handler.py (MQTT communication)"
echo "• config.py (configuration)"
echo "• hardware_interface.py (hardware interface)"
echo "• connect_hardware.sh (deployment script)"
echo "• run_v3.sh (run script)"
echo "• monitor_v3.sh (monitoring script)"
echo "• solar_heating_v3.service (systemd service)"
echo "• README.md (documentation)"
echo "• requirements.txt (dependencies)"
echo "• SENSOR_MAPPING.md (sensor documentation)"
echo "• CONTROL_SETUP_GUIDE.md (control setup)"

echo
echo -e "${GREEN}🎯 Result: Clean, focused v3 folder with only essential files!${NC}"
