# [Bug] MQTT Connection Showing Disconnected

## Problem

MQTT status showing as "Disconnected" in the web dashboard.

## Current Behavior

- **MQTT Status:** Disconnected (red badge)
- **System Mode:** Heating
- **Impact:** Unable to publish sensor data and system state to MQTT broker

## Expected Behavior

MQTT should be connected and actively publishing data.

## Context

From web dashboard screenshot - both MQTT and Home Assistant showing disconnected status.

## Investigation Needed

1. Check MQTT broker is running and accessible
2. Verify MQTT credentials in configuration
3. Check network connectivity to broker
4. Review MQTT handler logs for connection errors
5. Verify Issue #44 (MQTT Authentication) deployment is working

## Related Issues

- #44 - MQTT Authentication implementation (recently deployed)
- #20 - Improve MQTT Connection Stability
- #51 - MQTT Publish Failures (Phase 1 complete)

## Diagnostic Commands

```bash
# Check MQTT service status
systemctl status mosquitto

# Check solar heating logs for MQTT errors
journalctl -u solar_heating_v3.service --since "today" | grep -i mqtt

# Test MQTT connection manually
mosquitto_sub -h localhost -t "solar_heating/#" -v

# Check MQTT handler status via API
curl http://localhost:5000/api/system/status | jq '.mqtt_status'
```

## Priority

**High** - MQTT connectivity is critical for:
- Data publishing to Home Assistant
- System monitoring
- Remote diagnostics
- Historical data collection

## Labels

bug, mqtt, connectivity
