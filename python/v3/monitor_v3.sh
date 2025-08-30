#!/bin/bash

# Solar Heating System v3 Monitor Script
# This script helps monitor the v3 system status

echo "=== Solar Heating System v3 Monitor ==="
echo "Timestamp: $(date)"
echo

# Check if service is running
echo "1. Service Status:"
if systemctl is-active --quiet solar_heating_v3.service; then
    echo "✅ Service is RUNNING"
    systemctl status solar_heating_v3.service --no-pager -l | head -10
else
    echo "❌ Service is NOT RUNNING"
fi
echo

# Check if process is running
echo "2. Process Status:"
if pgrep -f "main_system.py" > /dev/null; then
    echo "✅ Process is RUNNING"
    ps aux | grep main_system | grep -v grep
else
    echo "❌ Process is NOT RUNNING"
fi
echo

# Check log file
echo "3. Recent Log Entries:"
if [ -f "solar_heating_v3.log" ]; then
    echo "📄 Log file size: $(ls -lh solar_heating_v3.log | awk '{print $5}')"
    echo "📄 Last modified: $(ls -l solar_heating_v3.log | awk '{print $6, $7, $8}')"
    echo
    echo "Last 5 log entries:"
    tail -5 solar_heating_v3.log
else
    echo "❌ Log file not found"
fi
echo

# Check for errors
echo "4. Recent Errors:"
if [ -f "solar_heating_v3.log" ]; then
    error_count=$(grep -i "error" solar_heating_v3.log | wc -l)
    echo "Total errors in log: $error_count"
    if [ $error_count -gt 0 ]; then
        echo "Last 3 errors:"
        grep -i "error" solar_heating_v3.log | tail -3
    fi
else
    echo "❌ Log file not found"
fi
echo

# Check virtual environment
echo "5. Virtual Environment:"
if [ -d "/opt/solar_heating_v3" ]; then
    echo "✅ Virtual environment exists"
    echo "Python version: $(/opt/solar_heating_v3/bin/python3 --version)"
else
    echo "❌ Virtual environment not found"
fi
echo

# Quick temperature check (if system is running)
echo "6. Temperature Status:"
if pgrep -f "main_system.py" > /dev/null; then
    echo "System is running - check log for temperature data"
    echo "Recent temperatures:"
    grep "temperature" solar_heating_v3.log | tail -3 2>/dev/null || echo "No temperature data found"
else
    echo "System not running - cannot check temperatures"
fi
echo

echo "=== Monitor Complete ==="
