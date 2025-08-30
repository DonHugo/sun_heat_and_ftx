#!/bin/bash
# Convenience script to run Solar Heating System v3
# Automatically activates the virtual environment

echo "🚀 Starting Solar Heating System v3..."

# Activate virtual environment
source /opt/solar_heating_v3/bin/activate

# Change to v3 directory
cd "$(dirname "$0")"

# Run the system
python3 main_system.py
