#!/bin/bash
# Setup script for preventing stale MQTT connections in the watchdog

set -e

echo "Setting up watchdog MQTT connection prevention system..."

# Make scripts executable
chmod +x /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh
chmod +x /home/pi/solar_heating/python/v3/setup_watchdog_prevention.sh

# Copy service files to systemd directory
sudo cp /home/pi/solar_heating/python/v3/solar_heating_watchdog_health.service /etc/systemd/system/
sudo cp /home/pi/solar_heating/python/v3/solar_heating_watchdog_health.timer /etc/systemd/system/

# Reload systemd
sudo systemctl daemon-reload

# Enable and start the timer
sudo systemctl enable solar_heating_watchdog_health.timer
sudo systemctl start solar_heating_watchdog_health.timer

# Check status
echo "Checking timer status..."
sudo systemctl status solar_heating_watchdog_health.timer

echo ""
echo "✅ Watchdog prevention system installed successfully!"
echo ""
echo "The system will now:"
echo "  • Check watchdog health every 5 minutes"
echo "  • Restart watchdog if MQTT connection is stale"
echo "  • Restart watchdog daily to prevent long-running stale connections"
echo "  • Log all activities to /var/log/solar_heating_watchdog_health.log"
echo ""
echo "To check the timer status: sudo systemctl status solar_heating_watchdog_health.timer"
echo "To check recent health checks: sudo journalctl -u solar_heating_watchdog_health.service"
echo "To view health log: tail -f /var/log/solar_heating_watchdog_health.log"
echo ""
echo "The enhanced watchdog is ready to prevent stale MQTT connections!"












