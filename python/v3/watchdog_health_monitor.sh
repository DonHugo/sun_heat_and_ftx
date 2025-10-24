#!/bin/bash
# Watchdog Health Monitor and Auto-Recovery Script
# Prevents stale MQTT connections by monitoring and restarting when needed

LOG_FILE="/var/log/solar_heating_watchdog_health.log"
WATCHDOG_SERVICE="solar_heating_watchdog.service"
MQTT_BROKER="192.168.0.110"
MQTT_USER="mqtt_beaches"
MQTT_PASS="uQX6NiZ.7R"
HEARTBEAT_TOPIC="solar_heating_v3/heartbeat"

# Logging function
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Check if watchdog service is running
check_watchdog_service() {
    if systemctl is-active --quiet "$WATCHDOG_SERVICE"; then
        return 0
    else
        log_message "ERROR: Watchdog service is not running"
        return 1
    fi
}

# Check MQTT connectivity
check_mqtt_connectivity() {
    # Test MQTT connection with timeout
    timeout 10 mosquitto_sub -h "$MQTT_BROKER" -u "$MQTT_USER" -P "$MQTT_PASS" -t "$HEARTBEAT_TOPIC" -C 1 >/dev/null 2>&1
    return $?
}

# Check if heartbeats are being received
check_heartbeat_reception() {
    # Get recent watchdog logs
    local recent_logs=$(journalctl -u "$WATCHDOG_SERVICE" --since "2 minutes ago" --no-pager)
    
    # Check for heartbeat received messages
    if echo "$recent_logs" | grep -q "Heartbeat received"; then
        return 0
    else
        # Check for MQTT unhealthy warnings
        if echo "$recent_logs" | grep -q "MQTT unhealthy"; then
            log_message "WARNING: MQTT unhealthy detected in logs"
            return 1
        fi
        return 1
    fi
}

# Restart watchdog service
restart_watchdog() {
    log_message "INFO: Restarting watchdog service to prevent stale connections"
    
    if systemctl restart "$WATCHDOG_SERVICE"; then
        log_message "INFO: Watchdog service restarted successfully"
        
        # Wait for service to start
        sleep 5
        
        # Verify restart was successful
        if systemctl is-active --quiet "$WATCHDOG_SERVICE"; then
            log_message "INFO: Watchdog service is running after restart"
            return 0
        else
            log_message "ERROR: Watchdog service failed to start after restart"
            return 1
        fi
    else
        log_message "ERROR: Failed to restart watchdog service"
        return 1
    fi
}

# Check watchdog uptime
check_watchdog_uptime() {
    local uptime=$(systemctl show "$WATCHDOG_SERVICE" --property=ActiveEnterTimestamp --value)
    local uptime_seconds=$(date -d "$uptime" +%s)
    local current_time=$(date +%s)
    local uptime_hours=$(( (current_time - uptime_seconds) / 3600 ))
    
    log_message "INFO: Watchdog uptime: ${uptime_hours} hours"
    
    # Restart if uptime is more than 24 hours
    if [ $uptime_hours -gt 24 ]; then
        log_message "INFO: Watchdog uptime exceeds 24 hours, scheduling restart"
        return 1
    fi
    
    return 0
}

# Main health check function
main_health_check() {
    log_message "INFO: Starting watchdog health check"
    
    # Check if watchdog service is running
    if ! check_watchdog_service; then
        log_message "ERROR: Watchdog service is not running, attempting to start"
        systemctl start "$WATCHDOG_SERVICE"
        return 1
    fi
    
    # Check watchdog uptime
    if ! check_watchdog_uptime; then
        restart_watchdog
        return 0
    fi
    
    # Check MQTT connectivity
    if ! check_mqtt_connectivity; then
        log_message "WARNING: MQTT connectivity check failed"
        restart_watchdog
        return 0
    fi
    
    # Check heartbeat reception
    if ! check_heartbeat_reception; then
        log_message "WARNING: No heartbeats received recently"
        restart_watchdog
        return 0
    fi
    
    log_message "INFO: All health checks passed"
    return 0
}

# Run the health check
main_health_check
exit $?





