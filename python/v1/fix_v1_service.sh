#!/bin/bash

# Fix v1 temperature monitoring service
echo "🔧 Fixing v1 temperature monitoring service..."

# Copy the corrected service file
sudo cp /home/pi/solar_heating/python/temperature_monitoring.service /etc/systemd/system/

# Reload systemd daemon
sudo systemctl daemon-reload

# Disable and re-enable the service
sudo systemctl disable temperature_monitoring.service
sudo systemctl enable temperature_monitoring.service

echo "✅ Service file updated and reloaded"
echo "📋 Testing the service..."

# Test the service
sudo systemctl start temperature_monitoring.service
sleep 2
sudo systemctl status temperature_monitoring.service

echo "🎯 Service fix completed!"
