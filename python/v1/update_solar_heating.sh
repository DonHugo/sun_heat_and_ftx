#!/bin/bash
# Solar Heating System Update Script
# This script updates the system from Git and restarts services

set -e

PROJECT_DIR="/home/pi/solar_heating"
BRANCH="main"

echo "🔄 Updating Solar Heating System..."
echo "=================================="

# Navigate to project directory
cd "$PROJECT_DIR"

# Check if there are changes to pull
echo "📡 Checking for updates..."
git fetch origin
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL = $REMOTE ]; then
    echo "✅ System is up to date"
    echo "Current version: $(git log --oneline -1)"
    exit 0
fi

echo "📥 Pulling latest changes..."
git pull origin $BRANCH

echo "🔄 Updated to version: $(git log --oneline -1)"

# Update v3 dependencies if v3 directory exists
if [ -d "$PROJECT_DIR/python/v3" ]; then
    echo "🔧 Updating v3 dependencies..."
    cd "$PROJECT_DIR/python/v3"
    
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
        pip install -r requirements.txt
        echo "✅ v3 dependencies updated"
    else
        echo "⚠️  v3 virtual environment not found"
    fi
fi

# Restart services
echo "🔄 Restarting services..."

# Stop both services first
sudo systemctl stop temperature_monitoring.service 2>/dev/null || true
sudo systemctl stop solar_heating_v3.service 2>/dev/null || true

# Wait a moment
sleep 2

# Start services
echo "🚀 Starting v1 service..."
sudo systemctl start temperature_monitoring.service

echo "🚀 Starting v3 service..."
sudo systemctl start solar_heating_v3.service

# Wait for services to start
sleep 3

echo "✅ Update completed successfully!"
echo ""
echo "📊 Service status:"
echo "=================="

# Check v1 service
if systemctl is-active --quiet temperature_monitoring.service; then
    echo "✅ v1 service: RUNNING"
else
    echo "❌ v1 service: FAILED TO START"
    echo "   Check logs: sudo journalctl -u temperature_monitoring.service -n 20"
fi

# Check v3 service
if systemctl is-active --quiet solar_heating_v3.service; then
    echo "✅ v3 service: RUNNING"
else
    echo "❌ v3 service: FAILED TO START"
    echo "   Check logs: sudo journalctl -u solar_heating_v3.service -n 20"
fi

echo ""
echo "🔍 Quick health check:"
echo "======================"

# Check MQTT connection
if mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "health_check" -m "test" 2>/dev/null; then
    echo "✅ MQTT: CONNECTED"
else
    echo "❌ MQTT: DISCONNECTED"
fi

# Check disk space
DISK_USAGE=$(df /home/pi | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 90 ]; then
    echo "✅ Disk space: OK ($DISK_USAGE%)"
else
    echo "⚠️  Disk space: LOW ($DISK_USAGE%)"
fi

echo ""
echo "📋 Useful commands:"
echo "==================="
echo "  system_switch.py status    # Check which system is active"
echo "  system_switch.py v1        # Switch to v1 system"
echo "  system_switch.py v3        # Switch to v3 system"
echo "  system_switch.py logs      # View logs for active system"
echo ""
echo "🎉 Update completed!"
