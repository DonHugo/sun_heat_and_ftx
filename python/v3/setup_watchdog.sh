#!/bin/bash
# Setup script for Solar Heating System v3 Watchdog

set -e

echo "=== Solar Heating System v3 Watchdog Setup ==="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root. Please run as pi user."
   exit 1
fi

# Check if we're in the right directory
if [[ ! -f "watchdog.py" ]]; then
    echo "Error: watchdog.py not found. Please run this script from the python/v3 directory."
    exit 1
fi

echo "Installing watchdog system..."

# Create log directory
sudo mkdir -p /var/log
sudo touch /var/log/solar_heating_watchdog.log
sudo chown pi:pi /var/log/solar_heating_watchdog.log
sudo chmod 644 /var/log/solar_heating_watchdog.log

echo "✓ Log directory created"

# Install systemd service
if [[ -f "solar_heating_watchdog.service" ]]; then
    sudo cp solar_heating_watchdog.service /etc/systemd/system/
    sudo systemctl daemon-reload
    sudo systemctl enable solar_heating_watchdog.service
    echo "✓ Systemd service installed and enabled"
else
    echo "✗ Service file not found"
    exit 1
fi

# Test the watchdog
echo "Testing watchdog functionality..."
python3 test_watchdog.py

if [[ $? -eq 0 ]]; then
    echo "✓ Watchdog test passed"
else
    echo "⚠️  Watchdog test had issues - check output above"
fi

# Start the service
echo "Starting watchdog service..."
sudo systemctl start solar_heating_watchdog.service

# Check status
echo "Checking service status..."
sudo systemctl status solar_heating_watchdog.service --no-pager -l

echo ""
echo "=== Watchdog Setup Complete ==="
echo ""
echo "Service commands:"
echo "  Start:   sudo systemctl start solar_heating_watchdog"
echo "  Stop:    sudo systemctl stop solar_heating_watchdog"
echo "  Status:  sudo systemctl status solar_heating_watchdog"
echo "  Logs:    sudo journalctl -u solar_heating_watchdog -f"
echo "  Test:    python3 test_watchdog.py"
echo ""
echo "The watchdog will now monitor:"
echo "  - Network connectivity (ping 8.8.8.8, 1.1.1.1, 192.168.0.1)"
echo "  - MQTT communication (heartbeat on solar_heating_v3/heartbeat)"
echo "  - System service status (solar_heating_v3.service)"
echo ""
echo "Alerts will be sent to MQTT topic: solar_heating_v3/heartbeat/alert"
echo "Logs are written to: /var/log/solar_heating_watchdog.log"
