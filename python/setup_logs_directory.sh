#!/bin/bash
# Setup script for centralized logging directory

set -e

echo "=== Setting up centralized logging directory ==="

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   echo "This script should not be run as root. Please run as pi user."
   exit 1
fi

# Create logs directory
echo "Creating logs directory..."
mkdir -p /home/pi/solar_heating/logs

# Set proper permissions
echo "Setting permissions..."
sudo chown -R pi:pi /home/pi/solar_heating/logs
sudo chmod -R 755 /home/pi/solar_heating/logs

# Create log rotation configuration
echo "Setting up log rotation..."
sudo tee /etc/logrotate.d/solar_heating > /dev/null <<EOF
/home/pi/solar_heating/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 pi pi
    postrotate
        systemctl reload solar_heating_v3.service 2>/dev/null || true
        systemctl reload temperature_monitoring.service 2>/dev/null || true
    endscript
}
EOF

# Create initial log files with proper permissions
echo "Creating initial log files..."
touch /home/pi/solar_heating/logs/solar_heating_v3.log
touch /home/pi/solar_heating/logs/temperature_monitoring_v1.log
touch /home/pi/solar_heating/logs/temperature_monitoring_v2.log

# Set permissions on log files
sudo chown pi:pi /home/pi/solar_heating/logs/*.log
sudo chmod 644 /home/pi/solar_heating/logs/*.log

echo "✅ Log directory setup complete!"
echo ""
echo "📁 Log directory: /home/pi/solar_heating/logs/"
echo "📋 Log files:"
echo "   - solar_heating_v3.log"
echo "   - temperature_monitoring_v1.log"
echo "   - temperature_monitoring_v2.log"
echo "   - /var/log/solar_heating_watchdog.log (watchdog)"
echo ""
echo "🔄 Log rotation: Configured for daily rotation with 7-day retention"
echo "📊 Monitor logs with: tail -f /home/pi/solar_heating/logs/*.log"
