# Watchdog MQTT Connection Prevention

## Overview

This document describes the enhanced monitoring and prevention system for stale MQTT connections in the Solar Heating System v3 watchdog service.

## Problem

The watchdog service can develop stale MQTT connections over time, leading to:
- False "MQTT unhealthy" warnings
- Inability to receive heartbeat messages
- Loss of system monitoring capabilities

## Solution

A comprehensive prevention system with multiple layers of protection:

### 1. Enhanced Watchdog with Auto-Recovery

**File**: `watchdog_enhanced.py`

**Features**:
- Automatic MQTT reconnection on failures
- Daily scheduled restart to prevent stale connections
- Enhanced connection validation
- Better error handling and logging
- Connection attempt tracking

**Key Settings**:
```python
mqtt_check_interval: int = 30  # Check every 30 seconds
mqtt_timeout: int = 60  # 60 seconds timeout for heartbeat
max_mqtt_failures: int = 3  # Max failures before restart
watchdog_restart_interval: int = 86400  # Daily restart (24 hours)
```

### 2. Health Monitor Script

**File**: `watchdog_health_monitor.sh`

**Functions**:
- Checks watchdog service status
- Validates MQTT connectivity
- Monitors heartbeat reception
- Tracks service uptime
- Automatic restart when issues detected

**Checks Performed**:
- Service running status
- MQTT broker connectivity
- Heartbeat message reception
- Service uptime (restarts after 24 hours)

### 3. Scheduled Monitoring

**Files**: 
- `solar_heating_watchdog_health.service`
- `solar_heating_watchdog_health.timer`

**Schedule**: Every 5 minutes

**Actions**:
- Runs health monitor script
- Logs all activities
- Triggers automatic recovery

## Installation

### Quick Setup

```bash
# Run the setup script
sudo /home/pi/solar_heating/python/v3/setup_watchdog_prevention.sh
```

### Manual Setup

```bash
# 1. Make scripts executable
chmod +x /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh

# 2. Copy service files
sudo cp /home/pi/solar_heating/python/v3/solar_heating_watchdog_health.service /etc/systemd/system/
sudo cp /home/pi/solar_heating/python/v3/solar_heating_watchdog_health.timer /etc/systemd/system/

# 3. Reload systemd
sudo systemctl daemon-reload

# 4. Enable and start timer
sudo systemctl enable solar_heating_watchdog_health.timer
sudo systemctl start solar_heating_watchdog_health.timer
```

## Monitoring

### Check Timer Status
```bash
sudo systemctl status solar_heating_watchdog_health.timer
```

### View Health Check Logs
```bash
# Recent health checks
sudo journalctl -u solar_heating_watchdog_health.service

# Health monitor log file
tail -f /var/log/solar_heating_watchdog_health.log
```

### Manual Health Check
```bash
sudo /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh
```

## Configuration

### Health Monitor Settings

Edit `watchdog_health_monitor.sh` to modify:
- Check intervals
- MQTT broker settings
- Restart thresholds
- Log file locations

### Enhanced Watchdog Settings

Edit `watchdog_enhanced.py` to modify:
- MQTT connection parameters
- Auto-recovery settings
- Restart intervals
- Failure thresholds

## Troubleshooting

### Timer Not Running
```bash
# Check timer status
sudo systemctl status solar_heating_watchdog_health.timer

# Restart timer
sudo systemctl restart solar_heating_watchdog_health.timer
```

### Health Checks Failing
```bash
# Check service logs
sudo journalctl -u solar_heating_watchdog_health.service

# Check health monitor log
cat /var/log/solar_heating_watchdog_health.log
```

### Manual Watchdog Restart
```bash
# Restart watchdog service
sudo systemctl restart solar_heating_watchdog.service

# Check status
sudo systemctl status solar_heating_watchdog.service
```

## Prevention Strategies

### 1. Proactive Monitoring
- Continuous health checks every 5 minutes
- Early detection of connection issues
- Automatic recovery before problems escalate

### 2. Scheduled Restarts
- Daily watchdog restart to prevent stale connections
- Configurable restart intervals
- Graceful restart procedures

### 3. Connection Validation
- MQTT connectivity testing
- Heartbeat message verification
- Connection state monitoring

### 4. Enhanced Logging
- Detailed connection tracking
- Failure pattern analysis
- Performance monitoring

## Benefits

1. **Reliability**: Prevents stale connections from causing false alarms
2. **Automation**: No manual intervention required
3. **Monitoring**: Comprehensive logging and status tracking
4. **Recovery**: Automatic problem resolution
5. **Prevention**: Proactive measures to avoid issues

## Maintenance

### Regular Checks
- Monitor health check logs weekly
- Verify timer is running
- Check for any recurring issues

### Updates
- Review and update configuration as needed
- Monitor system performance
- Adjust thresholds based on usage patterns

## Integration

This prevention system works alongside:
- Existing watchdog service
- Home Assistant monitoring
- System health checks
- Alerting systems

The enhanced monitoring provides an additional layer of protection without interfering with normal operations.





