# [Bug] Home Assistant Connection Showing Disconnected

## Problem

Home Assistant (HA) status showing as "Disconnected" in the web dashboard.

## Current Behavior

- **HA Status:** Disconnected (red badge)
- **System Mode:** Heating
- **Impact:** System cannot integrate with Home Assistant for automation, monitoring, and control

## Expected Behavior

Home Assistant connection should be active, allowing:
- Entity updates in HA
- Dashboard integration
- Automation triggers
- Voice assistant control

## Context

From web dashboard screenshot - both MQTT and Home Assistant showing disconnected status.

## Possible Causes

1. **MQTT Dependency:** HA integration likely uses MQTT for communication
   - If MQTT is down, HA will also show disconnected
   - Need to fix MQTT first (see related issue)

2. **Home Assistant Configuration:**
   - HA server may not be running
   - Integration not configured in HA
   - Authentication credentials invalid
   - Network connectivity issues

3. **Integration Setup:**
   - MQTT discovery not working
   - Entities not auto-discovered
   - Manual configuration needed

## Investigation Needed

1. Check if Home Assistant server is running
2. Verify MQTT connection (prerequisite)
3. Check Home Assistant MQTT integration status
4. Review HA logs for solar heating entities
5. Verify MQTT discovery messages are being sent
6. Check network connectivity to HA instance

## Diagnostic Commands

```bash
# Check Home Assistant status (if running on same Pi)
systemctl status home-assistant

# Check for solar heating entities in HA
# (via HA UI: Settings -> Devices & Services -> Entities)

# Check MQTT discovery messages
mosquitto_sub -h localhost -t "homeassistant/#" -v

# Check if system is publishing HA discovery messages
journalctl -u solar_heating_v3.service --since "today" | grep -i "home.*assistant\|discovery"
```

## Dependencies

**Blocked by:** MQTT connection issue (see related issue)
- HA integration requires MQTT to be working
- Fix MQTT first, then reassess HA status

## Related Issues

- MQTT disconnection issue (to be created)
- #44 - MQTT Authentication (may affect HA connection)
- #20 - MQTT Connection Stability

## Priority

**Medium-High** - Important for home automation integration, but:
- Blocked by MQTT connectivity issue
- System can still operate locally without HA
- Should be resolved after MQTT is fixed

## Setup Checklist (if not configured)

- [ ] Home Assistant server running
- [ ] MQTT integration enabled in HA
- [ ] MQTT discovery enabled in solar heating system
- [ ] Entities appearing in HA
- [ ] Test automation/control from HA

## Labels

bug, home-assistant, connectivity, integration
