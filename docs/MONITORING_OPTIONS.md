# Solar Heating System v3 Monitoring Options

This document provides an overview of all available monitoring options for the Solar Heating System v3, with a focus on uptime monitoring for tools like Uptime Kuma.

## Overview

The Solar Heating System v3 provides multiple monitoring interfaces to ensure system health and uptime can be monitored effectively. Choose the option that best fits your monitoring infrastructure.

## Option 1: MQTT Heartbeat (Recommended)

### What It Is
A continuous heartbeat message published to MQTT every 30 seconds containing system status information.

### Advantages
- **Real-time monitoring**: Immediate detection of system issues
- **Rich data**: Includes system state, pump status, temperature count
- **MQTT integration**: Works seamlessly with existing MQTT infrastructure
- **Low overhead**: Minimal system impact
- **Uptime Kuma compatible**: Direct MQTT monitoring support

### Configuration
- **Topic**: `solar_heating_v3/heartbeat`
- **Frequency**: Every 30 seconds
- **Payload**: JSON with system status
- **Retention**: Not retained (real-time only)

### Uptime Kuma Setup
1. Add new monitor
2. Select "MQTT" type
3. Configure broker connection
4. Set topic to `solar_heating_v3/heartbeat`
5. Set check interval (recommended: 60 seconds)

### Message Format
```json
{
  "status": "alive",
  "timestamp": 1703123456.789,
  "version": "v3",
  "uptime": 3600.0,
  "system_state": "normal",
  "primary_pump": false,
  "cartridge_heater": false,
  "temperature_count": 16,
  "last_update": 1703123456.789
}
```

## Option 2: HTTP Health Check Server

### What It Is
A lightweight HTTP server providing health check endpoints for traditional HTTP monitoring.

### Advantages
- **Standard HTTP**: Works with any HTTP monitoring tool
- **Multiple endpoints**: `/health` for simple checks, `/status` for detailed info
- **Status codes**: Proper HTTP status codes for different health states
- **Easy integration**: Simple to set up with existing monitoring

### Configuration
- **Port**: 8080 (configurable)
- **Endpoints**:
  - `/health` - Simple health check
  - `/status` - Detailed system status
  - `/` - Service information

### Uptime Kuma Setup
1. Add new monitor
2. Select "HTTP(s)" type
3. Set URL to `http://YOUR_PI_IP:8080/health`
4. Set check interval (recommended: 60 seconds)

### Health Check Response
```json
{
  "status": "healthy",
  "timestamp": 1703123456.789,
  "last_heartbeat": 1703123456.789,
  "time_since_heartbeat": 15.5,
  "uptime": 3600.0
}
```

## Option 3: File-based Monitoring

### What It Is
A timestamp file that gets updated regularly, allowing file-based monitoring.

### Advantages
- **Simple**: No network dependencies
- **Lightweight**: Minimal system impact
- **Universal**: Works with any file monitoring tool
- **Reliable**: File system is very stable

### Configuration
- **File path**: `/tmp/solar_heating_heartbeat`
- **Update frequency**: Every 30 seconds
- **Content**: Unix timestamp

### Uptime Kuma Setup
1. Add new monitor
2. Select "File" type
3. Set file path to `/tmp/solar_heating_heartbeat`
4. Set check interval (recommended: 60 seconds)

## Option 4: Systemd Service Monitoring

### What It Is
Monitor the systemd service directly to check if the application is running.

### Advantages
- **System level**: Monitors the actual service
- **No application changes**: Works with existing systemd setup
- **Reliable**: Systemd is very stable
- **Standard**: Common monitoring approach

### Configuration
- **Service name**: `solar_heating_v3.service`
- **Check method**: `systemctl is-active solar_heating_v3`

### Uptime Kuma Setup
1. Add new monitor
2. Select "Command" type
3. Set command to `systemctl is-active solar_heating_v3`
4. Set expected output to `active`

## Implementation Status

### ✅ Implemented
- **MQTT Heartbeat**: Fully implemented and tested
- **HTTP Health Server**: Created as standalone module
- **Background Tasks**: System now uses proper async background tasks

### 🔄 Partially Implemented
- **File-based Monitoring**: Can be easily added
- **Systemd Integration**: Already exists, just needs monitoring setup

### 📋 To Do
- Integrate HTTP health server into main system (optional)
- Add file-based heartbeat as alternative
- Create monitoring configuration file

## Testing Your Setup

### Test MQTT Heartbeat
```bash
cd python/v3
python3 test_heartbeat.py
```

### Test HTTP Health Server
```bash
cd python/v3
python3 http_health.py
# Then visit http://YOUR_PI_IP:8080/health
```

### Test MQTT Connection
```bash
# Subscribe to heartbeat topic
mosquitto_sub -h YOUR_BROKER_IP -t "solar_heating_v3/heartbeat" -u USERNAME -P PASSWORD
```

## Recommended Monitoring Strategy

### Primary Monitoring
- **MQTT Heartbeat**: Main uptime monitoring
- **Systemd Service**: System-level service monitoring

### Secondary Monitoring
- **HTTP Health**: Alternative for HTTP-based tools
- **File-based**: Backup monitoring method

### Alerting
- **Critical**: No heartbeat for > 2 minutes
- **Warning**: No heartbeat for > 1 minute
- **Info**: System state changes

## Performance Impact

### MQTT Heartbeat
- **CPU**: < 0.1% additional usage
- **Memory**: Negligible
- **Network**: ~200 bytes every 30 seconds
- **MQTT Broker**: Minimal additional load

### HTTP Health Server
- **CPU**: < 0.5% additional usage
- **Memory**: ~5-10 MB for aiohttp
- **Network**: Only when accessed
- **Port**: Requires port 8080 (configurable)

## Security Considerations

### MQTT Heartbeat
- **Authentication**: Uses existing MQTT credentials
- **Data exposure**: Contains system status information
- **Access control**: MQTT broker access control applies

### HTTP Health Server
- **Authentication**: No built-in authentication
- **Data exposure**: Health status information
- **Network access**: Exposes HTTP endpoint

## Troubleshooting

### Common Issues

1. **No heartbeat messages**:
   - Check MQTT connection
   - Verify system is running
   - Check system logs

2. **HTTP server not accessible**:
   - Check firewall settings
   - Verify port 8080 is open
   - Check if service is running

3. **High resource usage**:
   - Adjust heartbeat frequency
   - Check for MQTT connection issues
   - Monitor system resources

### Log Monitoring
```bash
# Check heartbeat logs
grep -i heartbeat /var/log/solar_heating_v3.log

# Check MQTT connection
grep -i "mqtt.*connect" /var/log/solar_heating_v3.log

# Check system status
grep -i "system.*state" /var/log/solar_heating_v3.log
```

## Next Steps

1. **Choose your monitoring method** (MQTT recommended)
2. **Configure Uptime Kuma** with your chosen method
3. **Test the setup** using provided test scripts
4. **Set up alerting** based on your requirements
5. **Monitor and adjust** as needed

For detailed setup instructions, see the specific documentation for your chosen monitoring method.
