# Solar Heating System v3 Watchdog System

The watchdog system provides comprehensive monitoring of your solar heating system's health, including network connectivity, MQTT communication, and system service status.

## 🐕 **What the Watchdog Monitors**

### 1. **Network Connectivity**
- **Ping Tests**: Monitors connectivity to multiple hosts
  - `8.8.8.8` (Google DNS) - Internet connectivity
  - `1.1.1.1` (Cloudflare DNS) - Internet connectivity  
  - `192.168.0.1` (Local router) - Local network connectivity
- **Check Interval**: Every 30 seconds
- **Timeout**: 10 seconds per ping

### 2. **MQTT Communication**
- **Heartbeat Monitoring**: Listens to `solar_heating_v3/heartbeat` topic
- **Connection Status**: Verifies MQTT broker connectivity
- **Message Validation**: Ensures heartbeat messages are received regularly
- **Check Interval**: Every 60 seconds
- **Timeout**: 30 seconds without heartbeat

### 3. **System Service Health**
- **Service Status**: Checks if `solar_heating_v3.service` is running
- **Systemd Integration**: Uses `systemctl is-active` command
- **Check Interval**: Every 60 seconds

## 🚨 **Alert System**

### **Failure Thresholds**
- **Max Failures**: 3 consecutive failures before alert
- **Alert Interval**: 5 minutes between alerts (prevents spam)

### **Alert Topics**
- **MQTT Alert**: `solar_heating_v3/heartbeat/alert`
- **Log Files**: `/var/log/solar_heating_watchdog.log`
- **Systemd Journal**: `journalctl -u solar_heating_watchdog`

### **Alert Message Format**
```json
{
  "type": "watchdog_alert",
  "timestamp": 1703123456.789,
  "status": {
    "network": false,
    "mqtt": true,
    "system": true
  },
  "consecutive_failures": 3,
  "uptime": 3600.0
}
```

## 🛠️ **Installation & Setup**

### **Prerequisites**
- Python 3.7+
- `paho-mqtt` library
- Systemd (for service management)
- Sudo access (for service installation)

### **Quick Setup**
```bash
cd /home/pi/solar_heating/python/v3
./setup_watchdog.sh
```

### **Manual Setup**
```bash
# 1. Copy service file
sudo cp solar_heating_watchdog.service /etc/systemd/system/

# 2. Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable solar_heating_watchdog.service
sudo systemctl start solar_heating_watchdog.service

# 3. Check status
sudo systemctl status solar_heating_watchdog.service
```

## 📊 **Configuration**

### **Default Configuration**
```python
@dataclass
class WatchdogConfig:
    # Network monitoring
    ping_hosts: List[str] = ["8.8.8.8", "1.1.1.1", "192.168.0.1"]
    ping_interval: int = 30  # seconds
    ping_timeout: int = 10   # seconds
    
    # MQTT monitoring
    mqtt_broker: str = "192.168.0.110"
    mqtt_port: int = 1883
    mqtt_username: str = "mqtt_beaches"
    mqtt_password: str = "uQX6NiZ.7R"
    mqtt_heartbeat_topic: str = "solar_heating_v3/heartbeat"
    mqtt_check_interval: int = 60  # seconds
    mqtt_timeout: int = 30  # seconds
    
    # System monitoring
    system_check_interval: int = 60  # seconds
    service_name: str = "solar_heating_v3"
    
    # Alerting
    max_failures: int = 3
    alert_interval: int = 300  # 5 minutes
```

### **Customizing Configuration**
Edit the `WatchdogConfig` class in `watchdog.py` to modify:
- Ping hosts and intervals
- MQTT broker settings
- Service names
- Alert thresholds

## 🔍 **Monitoring & Troubleshooting**

### **Service Commands**
```bash
# Check service status
sudo systemctl status solar_heating_watchdog

# View real-time logs
sudo journalctl -u solar_heating_watchdog -f

# View log file
tail -f /var/log/solar_heating_watchdog.log

# Restart service
sudo systemctl restart solar_heating_watchdog

# Stop service
sudo systemctl stop solar_heating_watchdog
```

### **Testing the Watchdog**
```bash
# Run comprehensive test
python3 test_watchdog.py

# Test individual components
python3 -c "
import asyncio
from watchdog import NetworkMonitor, WatchdogConfig
async def test():
    config = WatchdogConfig()
    monitor = NetworkMonitor(config)
    result = await monitor.check_network()
    print(f'Network: {\"OK\" if result else \"FAILED\"}')
asyncio.run(test())
"
```

### **Log Analysis**
```bash
# Check for alerts
grep -i "alert" /var/log/solar_heating_watchdog.log

# Check network issues
grep -i "network.*failed" /var/log/solar_heating_watchdog.log

# Check MQTT issues
grep -i "mqtt.*failed" /var/log/solar_heating_watchdog.log

# Check system issues
grep -i "system.*failed" /var/log/solar_heating_watchdog.log
```

## 🔧 **Integration with Uptime Kuma**

### **Primary Monitoring**
- **MQTT Heartbeat**: `solar_heating_v3/heartbeat` (main uptime)
- **Watchdog Alerts**: `solar_heating_v3/heartbeat/alert` (system health)

### **Recommended Setup**
1. **Main Monitor**: MQTT topic `solar_heating_v3/heartbeat`
2. **Health Monitor**: MQTT topic `solar_heating_v3/heartbeat/alert`
3. **Service Monitor**: Command `systemctl is-active solar_heating_v3`

## 📈 **Performance & Resource Usage**

### **Resource Impact**
- **CPU**: < 1% additional usage
- **Memory**: ~10-15 MB
- **Network**: Minimal ping traffic + MQTT overhead
- **Disk**: Log file growth (~1MB/day)

### **Check Frequencies**
- **Overall Health**: Every 10 seconds
- **Network**: Every 30 seconds
- **MQTT**: Every 60 seconds
- **System**: Every 60 seconds
- **Status Logging**: Every 5 minutes

## 🚨 **Common Issues & Solutions**

### **Network Connectivity Issues**
```bash
# Test ping manually
ping -c 3 8.8.8.8
ping -c 3 192.168.0.1

# Check DNS resolution
nslookup google.com

# Check network interfaces
ip addr show
```

### **MQTT Connection Issues**
```bash
# Test MQTT connection
mosquitto_pub -h 192.168.0.110 -t "test" -m "test" -u mqtt_beaches -P uQX6NiZ.7R

# Check MQTT broker status
sudo systemctl status mosquitto
```

### **Service Issues**
```bash
# Check service status
sudo systemctl status solar_heating_v3

# Check service logs
sudo journalctl -u solar_heating_v3 -f

# Restart service
sudo systemctl restart solar_heating_v3
```

## 🔄 **Recovery & Maintenance**

### **Automatic Recovery**
- **Service Restart**: Systemd automatically restarts failed services
- **Network Recovery**: Watchdog detects when connectivity returns
- **MQTT Reconnection**: Automatic reconnection attempts

### **Manual Recovery**
```bash
# Restart watchdog
sudo systemctl restart solar_heating_watchdog

# Restart main service
sudo systemctl restart solar_heating_v3

# Check all services
sudo systemctl status solar_heating_v3 solar_heating_watchdog
```

### **Log Rotation**
```bash
# Create logrotate config
sudo tee /etc/logrotate.d/solar_heating_watchdog << EOF
/var/log/solar_heating_watchdog.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
    create 644 pi pi
}
EOF
```

## 📋 **Best Practices**

### **Monitoring Strategy**
1. **Use Uptime Kuma** for external monitoring
2. **Enable watchdog alerts** for internal health monitoring
3. **Monitor both heartbeat and alerts** for comprehensive coverage
4. **Set up log rotation** to prevent disk space issues

### **Alert Management**
1. **Don't set alerts too sensitive** (use 3+ failures)
2. **Use alert intervals** to prevent notification spam
3. **Monitor alert topics** in addition to heartbeat topics
4. **Set up escalation** for critical failures

### **Maintenance**
1. **Regular log review** (weekly)
2. **Service status checks** (daily)
3. **Configuration updates** (as needed)
4. **Performance monitoring** (monthly)

## 🎯 **Next Steps**

1. **Install the watchdog**: Run `./setup_watchdog.sh`
2. **Test the system**: Run `python3 test_watchdog.py`
3. **Monitor the logs**: Check `/var/log/solar_heating_watchdog.log`
4. **Set up Uptime Kuma**: Monitor both heartbeat and alert topics
5. **Customize configuration**: Adjust settings as needed

The watchdog system provides a robust foundation for monitoring your solar heating system's health and ensuring reliable operation! 🚀
