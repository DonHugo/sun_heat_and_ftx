#!/bin/bash
# Convenience script to test Solar Heating System v3
# Automatically activates the virtual environment

echo "🧪 Testing Solar Heating System v3..."

# Activate virtual environment
source /opt/solar_heating_v3/bin/activate

# Change to v3 directory
cd "$(dirname "$0")"

# Run the test
python3 test_system_simple.py
