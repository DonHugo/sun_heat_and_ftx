# Watchdog MQTT Prevention System - Deployment Guide

## Quick Deployment

### Option 1: Automated Deployment (Recommended)

```bash
# Make the deployment script executable
chmod +x deploy_watchdog_prevention.sh

# Run the deployment script
./deploy_watchdog_prevention.sh
```

### Option 2: Manual Deployment

If you prefer to deploy manually or need to customize the process:

#### Step 1: Copy Files to Raspberry Pi

```bash
# Set your Pi's details
RPI_USER="pi"
RPI_HOST="rpi-solfangare-2"  # Your Pi's hostname or IP
REMOTE_DIR="/home/pi/solar_heating/python/v3"

# Copy all prevention system files
scp watchdog_enhanced.py $RPI_USER@$RPI_HOST:$REMOTE_DIR/
scp watchdog_health_monitor.sh $RPI_USER@$RPI_HOST:$REMOTE_DIR/
scp solar_heating_watchdog_health.service $RPI_USER@$RPI_HOST:$REMOTE_DIR/
scp solar_heating_watchdog_health.timer $RPI_USER@$RPI_HOST:$REMOTE_DIR/
scp setup_watchdog_prevention.sh $RPI_USER@$RPI_HOST:$REMOTE_DIR/
```

#### Step 2: Setup on Raspberry Pi

```bash
# SSH into your Pi
ssh pi@rpi-solfangare-2

# Make scripts executable
chmod +x /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh
chmod +x /home/pi/solar_heating/python/v3/setup_watchdog_prevention.sh

# Run the setup script
sudo /home/pi/solar_heating/python/v3/setup_watchdog_prevention.sh
```

## Configuration

### Update Pi Connection Details

Edit `deploy_watchdog_prevention.sh` and update these variables:

```bash
RPI_USER="pi"                    # Your Pi username
RPI_HOST="rpi-solfangare-2"      # Your Pi's hostname or IP address
```

### Customize Health Monitor Settings

Edit `watchdog_health_monitor.sh` to modify:

```bash
LOG_FILE="/var/log/solar_heating_watchdog_health.log"
WATCHDOG_SERVICE="solar_heating_watchdog.service"
MQTT_BROKER="192.168.0.110"      # Your MQTT broker IP
MQTT_USER="mqtt_beaches"         # Your MQTT username
MQTT_PASS="uQX6NiZ.7R"          # Your MQTT password
HEARTBEAT_TOPIC="solar_heating_v3/heartbeat"
```

## Verification

### Check Deployment Status

```bash
# SSH into your Pi
ssh pi@rpi-solfangare-2

# Check if timer is running
sudo systemctl status solar_heating_watchdog_health.timer

# Check if files are in place
ls -la /home/pi/solar_heating/python/v3/watchdog_*
ls -la /home/pi/solar_heating/python/v3/solar_heating_watchdog_health.*

# Run a test health check
sudo /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh
```

### Monitor the System

```bash
# Watch health check logs in real-time
sudo journalctl -u solar_heating_watchdog_health.service -f

# Check health monitor log file
tail -f /var/log/solar_heating_watchdog_health.log

# Check timer status
sudo systemctl list-timers solar_heating_watchdog_health.timer
```

## Troubleshooting

### Deployment Issues

#### SSH Connection Problems
```bash
# Test SSH connection
ssh pi@rpi-solfangare-2

# If using key authentication, ensure your key is added
ssh-add ~/.ssh/id_rsa
```

#### File Copy Issues
```bash
# Check if files exist locally
ls -la watchdog_*

# Check remote directory permissions
ssh pi@rpi-solfangare-2 "ls -la /home/pi/solar_heating/python/v3/"
```

#### Permission Issues
```bash
# Fix file permissions on Pi
ssh pi@rpi-solfangare-2 "chmod +x /home/pi/solar_heating/python/v3/*.sh"
```

### System Issues

#### Timer Not Starting
```bash
# Check systemd status
sudo systemctl status solar_heating_watchdog_health.timer

# Reload systemd and restart
sudo systemctl daemon-reload
sudo systemctl restart solar_heating_watchdog_health.timer
```

#### Health Checks Failing
```bash
# Check service logs
sudo journalctl -u solar_heating_watchdog_health.service

# Run manual health check
sudo /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh

# Check MQTT connectivity
mosquitto_sub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "solar_heating_v3/heartbeat" -C 1
```

## Post-Deployment

### Regular Monitoring

Set up monitoring to ensure the system is working:

```bash
# Create a monitoring script
cat > monitor_prevention_system.sh << 'EOF'
#!/bin/bash
echo "=== Watchdog Prevention System Status ==="
echo "Timer Status:"
sudo systemctl is-active solar_heating_watchdog_health.timer
echo ""
echo "Recent Health Checks:"
sudo journalctl -u solar_heating_watchdog_health.service --since "1 hour ago" --no-pager | tail -5
echo ""
echo "Health Log:"
tail -5 /var/log/solar_heating_watchdog_health.log
EOF

chmod +x monitor_prevention_system.sh
```

### Integration with Existing Monitoring

The prevention system integrates with your existing monitoring:

- **Home Assistant**: Will receive alerts if watchdog issues occur
- **System Logs**: All activities are logged to systemd journal
- **Health Logs**: Detailed logs in `/var/log/solar_heating_watchdog_health.log`

## Maintenance

### Regular Checks

- **Weekly**: Check health logs for any recurring issues
- **Monthly**: Verify timer is still running and active
- **As Needed**: Update configuration if MQTT settings change

### Updates

To update the prevention system:

1. Modify files locally
2. Re-run the deployment script
3. The system will automatically restart with new configuration

### Removal

If you need to remove the prevention system:

```bash
# Stop and disable timer
sudo systemctl stop solar_heating_watchdog_health.timer
sudo systemctl disable solar_heating_watchdog_health.timer

# Remove service files
sudo rm /etc/systemd/system/solar_heating_watchdog_health.service
sudo rm /etc/systemd/system/solar_heating_watchdog_health.timer

# Reload systemd
sudo systemctl daemon-reload

# Remove files
rm /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh
rm /home/pi/solar_heating/python/v3/solar_heating_watchdog_health.*
```

## Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review logs: `sudo journalctl -u solar_heating_watchdog_health.service`
3. Run manual health check: `sudo /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh`
4. Verify MQTT connectivity manually

The system is designed to be robust and self-healing, but these steps will help diagnose any issues.





