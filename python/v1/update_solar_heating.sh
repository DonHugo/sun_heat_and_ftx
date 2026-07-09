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

# ---------------------------------------------------------------------------
# CRITICAL: sync v3 code to the runtime directory (/opt/solar_heating_v3).
# The systemd service runs from /opt (a root-owned copy), NOT from this git
# repo. A `git pull` alone does not change what runs — the files must be
# copied into /opt or the service keeps executing the old code after restart.
# ---------------------------------------------------------------------------
OPT_DIR="/opt/solar_heating_v3"
if [ -d "$OPT_DIR" ]; then
    echo "🔧 Syncing v3 code to runtime dir: $OPT_DIR ..."
    # Back up the current runtime main file (rollback point)
    if [ -f "$OPT_DIR/main_system.py" ]; then
        sudo cp -p "$OPT_DIR/main_system.py" \
            "$OPT_DIR/main_system.py.bak-$(date +%Y%m%d_%H%M%S)"
    fi
    # Copy all v3 python modules from repo -> /opt (preserve root ownership)
    sudo cp "$PROJECT_DIR"/python/v3/*.py "$OPT_DIR"/
    sudo chown root:root "$OPT_DIR"/*.py
    echo "✅ v3 code synced to $OPT_DIR"
else
    echo "⚠️  Runtime dir $OPT_DIR not found - skipping /opt sync"
    echo "    (If the service runs from the repo venv instead, this is expected.)"
fi

# Update v3 dependencies in the PRODUCTION venv (/opt/solar_heating_v3/bin).
# NOTE: the repo-local python/v3/venv is legacy and generally unused.
if [ -f "$OPT_DIR/bin/pip3" ] && [ -f "$PROJECT_DIR/python/v3/requirements.txt" ]; then
    echo "🔧 Updating v3 dependencies in production venv..."
    sudo "$OPT_DIR/bin/pip3" install -r "$PROJECT_DIR/python/v3/requirements.txt" --break-system-packages
    echo "✅ v3 dependencies updated"
elif [ -d "$PROJECT_DIR/python/v3" ]; then
    echo "🔧 Updating v3 dependencies (legacy repo venv)..."
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
