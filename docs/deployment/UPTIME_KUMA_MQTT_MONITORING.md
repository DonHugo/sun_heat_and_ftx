# Uptime Kuma MQTT Monitoring Setup

This document explains how to set up Uptime Kuma to monitor the Solar Heating System v3 using MQTT heartbeat messages.

## Overview

The Solar Heating System v3 now publishes heartbeat messages every 30 seconds to the MQTT topic `solar_heating_v3/heartbeat`. This allows external monitoring systems like Uptime Kuma to verify that the application is running and healthy.

## MQTT Heartbeat Details

- **Topic**: `solar_heating_v3/heartbeat`
- **Frequency**: Every 30 seconds
- **Payload**: JSON with system status information
- **Retention**: Not retained (real-time only)

### Heartbeat Message Format

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

## Uptime Kuma Configuration

### Option 1: MQTT Monitor (Recommended)

1. **Add New Monitor** in Uptime Kuma
2. **Monitor Type**: Select "MQTT"
3. **Configuration**:
   - **Hostname**: Your MQTT broker IP/hostname
   - **Port**: MQTT broker port (usually 1883)
   - **Username**: MQTT username
   - **Password**: MQTT password
   - **Topic**: `solar_heating_v3/heartbeat`
   - **Check Interval**: 60 seconds (or as desired)

### Option 2: HTTP Monitor with MQTT Bridge

If your MQTT broker doesn't support direct MQTT monitoring in Uptime Kuma, you can use an MQTT-to-HTTP bridge:

1. **Install MQTT-to-HTTP bridge** (e.g., Node-RED, Home Assistant, or custom script)
2. **Configure bridge** to listen to `solar_heating_v3/heartbeat`
3. **Set up HTTP endpoint** that responds when heartbeat is received
4. **Monitor HTTP endpoint** in Uptime Kuma

### Option 3: File-based Monitoring

As an alternative, you can monitor a heartbeat file:

1. **Configure system** to write timestamp to `/tmp/solar_heating_heartbeat`
2. **Set up file monitor** in Uptime Kuma
3. **Monitor file modification time**

## Alerting Configuration

### Heartbeat Failure Scenarios

- **No heartbeat received**: Application stopped or MQTT disconnected
- **Heartbeat too old**: Application running but not sending heartbeats
- **System state errors**: Application running but in error state

### Recommended Alerts

1. **Critical**: No heartbeat for > 2 minutes
2. **Warning**: No heartbeat for > 1 minute
3. **Info**: System state changed to error/maintenance

## Testing the Setup

### Manual MQTT Test

Use an MQTT client to subscribe to the heartbeat topic:

```bash
# Using mosquitto_sub
mosquitto_sub -h YOUR_BROKER_IP -t "solar_heating_v3/heartbeat" -u USERNAME -P PASSWORD

# Using mqtt-cli
mqtt sub -h YOUR_BROKER_IP -t "solar_heating_v3/heartbeat" -u USERNAME -p PASSWORD
```

### Expected Output

You should see a JSON message every 30 seconds:

```json
{"status":"alive","timestamp":1703123456.789,"version":"v3","uptime":3600.0,"system_state":"normal","primary_pump":false,"cartridge_heater":false,"temperature_count":16,"last_update":1703123456.789}
```

## Troubleshooting

### Common Issues

1. **No heartbeat messages**:
   - Check MQTT connection in system logs
   - Verify MQTT broker is accessible
   - Check system is running and not in error state

2. **Heartbeat too frequent**:
   - Adjust heartbeat interval in `_heartbeat_loop()` method
   - Current setting: 30 seconds

3. **MQTT connection issues**:
   - Check broker credentials and network connectivity
   - Verify MQTT client ID is unique

### Log Monitoring

Monitor system logs for heartbeat-related messages:

```bash
# Check for heartbeat success/failure
grep -i heartbeat /var/log/solar_heating_v3.log

# Check MQTT connection status
grep -i "mqtt.*connect" /var/log/solar_heating_v3.log
```

## Performance Considerations

- **Heartbeat frequency**: 30 seconds provides good balance between responsiveness and system load
- **MQTT overhead**: Minimal - small JSON payload (~200 bytes)
- **Network impact**: Negligible for local network monitoring

## Security Notes

- Heartbeat messages contain system status information
- Consider if this information should be restricted
- MQTT authentication is required for access
- Heartbeat topic is not retained (no historical data stored)
