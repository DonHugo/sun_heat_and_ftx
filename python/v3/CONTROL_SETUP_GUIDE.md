# Home Assistant Switch and Number Controls Setup Guide

## Overview

Your Solar Heating System v3 includes comprehensive Home Assistant integration with switches and number controls. This guide will help you set up, test, and troubleshoot these controls.

## Available Controls

### Manual Control Mode
The **Primary Pump Manual Control** switch allows you to override the automatic control system:
- **ON**: Forces the primary pump to turn ON, overriding automatic control
- **OFF**: Returns control to the automatic system

When manual control is enabled, the system will ignore temperature-based automatic control and keep the pump running until you turn off manual control.

### Switches (On/Off Controls)
1. **Primary Pump** - Controls the main circulation pump (Relay 1)
2. **Primary Pump Manual Control** - Manual override for the primary pump (Relay 1)
3. **Cartridge Heater** - Controls the electric heating element (Relay 2)

### Numbers (Adjustable Values)
1. **Set Tank Temperature** - Target temperature for storage tank (15-90°C)
2. **Delta Temperature Start** - Temperature difference to start heating (3-40°C)
3. **Delta Temperature Stop** - Temperature difference to stop heating (2-20°C)
4. **Cooling Collector Temperature** - Temperature for collector cooling (70-120°C)
5. **Boiling Temperature** - Boiling point setting (100-200°C)

## Setup Steps

### 1. Start the Main System
```bash
cd /Users/hafs/Documents/Github/sun_heat_and_ftx/python/v3
source venv/bin/activate
python3 main_system.py
```

### 2. Verify MQTT Connection
The system should automatically:
- Connect to your MQTT broker (192.168.0.110:1883)
- Publish Home Assistant discovery messages
- Subscribe to control topics

### 3. Check Home Assistant Discovery
In Home Assistant, go to **Settings > Devices & Services** and look for:
- **Solar Heating System v3** device
- All switches and numbers should appear automatically

## Testing the Controls

### Option 1: Automated Test
Run the automated test script:
```bash
source venv/bin/activate
python3 test_controls.py
```

This will test all switches and numbers automatically.

### Option 2: Manual Test
Run the interactive test script:
```bash
source venv/bin/activate
python3 manual_control_test.py
```

This allows you to test individual controls manually.

### Option 3: Home Assistant Testing
1. Go to **Settings > Devices & Services**
2. Find **Solar Heating System v3**
3. Click on the device
4. Test each switch and number control

## Troubleshooting

### Problem: Controls don't respond in Home Assistant

**Possible Causes:**
1. MQTT connection issues
2. Topic subscription problems
3. Hardware interface issues
4. System not running

**Solutions:**

#### 1. Check MQTT Connection
```bash
# Test MQTT connection
mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "test/topic" -m "test message"
```

#### 2. Check System Logs
```bash
# View system logs
tail -f solar_heating_v3.log
```

Look for:
- MQTT connection messages
- Switch/number command messages
- Error messages

#### 3. Verify Topic Subscriptions
The system subscribes to these topics:
- `homeassistant/switch/solar_heating_+/set`
- `homeassistant/number/solar_heating_+/set`
- `hass/test_switch`

#### 4. Test MQTT Messages Manually
```bash
# Test switch command
mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "homeassistant/switch/solar_heating_primary_pump/set" -m "ON"

# Test number command
mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "homeassistant/number/solar_heating_set_temp_tank_1/set" -m "75"
```

### Problem: Controls work but hardware doesn't respond

**Possible Causes:**
1. Hardware libraries not available
2. Incorrect relay mapping
3. Hardware connection issues

**Solutions:**

#### 1. Check Hardware Availability
Look for this message in logs:
```
WARNING:root:Sequent Microsystems libraries not available. Running in simulation mode.
```

If you see this, the system is running in simulation mode.

#### 2. Verify Relay Mapping
Current relay mapping:
- Primary Pump: Relay 1
- Primary Pump Manual Control: Relay 1 (override)
- Cartridge Heater: Relay 2

#### 3. Test Hardware Interface
```bash
source venv/bin/activate
python3 test_hardware_connection.py
```

### Problem: Home Assistant doesn't discover devices

**Possible Causes:**
1. Discovery messages not published
2. MQTT broker issues
3. Home Assistant MQTT integration not configured

**Solutions:**

#### 1. Check Discovery Messages
```bash
# Monitor MQTT discovery topics
mosquitto_sub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "homeassistant/+/solar_heating_+/config"
```

#### 2. Restart Home Assistant MQTT Integration
1. Go to **Settings > Devices & Services**
2. Find MQTT integration
3. Click **Configure**
4. Click **Reload**

#### 3. Check MQTT Integration Settings
Ensure MQTT integration is configured with:
- Broker: 192.168.0.110
- Port: 1883
- Username: mqtt_beaches
- Password: uQX6NiZ.7R

## Configuration

### MQTT Settings
Edit `config.py` to modify MQTT settings:
```python
mqtt_broker: str = "192.168.0.110"
mqtt_port: int = 1883
mqtt_username: str = "mqtt_beaches"
mqtt_password: str = "uQX6NiZ.7R"
```

### Control Parameters
Edit `config.py` to modify default values:
```python
set_temp_tank_1: float = 70.0
dTStart_tank_1: float = 8.0
dTStop_tank_1: float = 4.0
kylning_kollektor: float = 90.0
temp_kok: float = 150.0
```

## Monitoring

### View Control States
```bash
# Monitor switch states
mosquitto_sub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "homeassistant/switch/solar_heating_+/state"

# Monitor number states
mosquitto_sub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "homeassistant/number/solar_heating_+/state"
```

### System Status
The system publishes status information to:
- `solar_heating_v3/status/system`
- `solar_heating_v3/status/pump`
- `solar_heating_v3/status/energy`

## Common Issues and Solutions

### Issue: "No system callback registered"
**Solution:** Ensure the MQTT handler is properly connected to the main system.

### Issue: "Invalid number value"
**Solution:** Check that number values are within the configured ranges.

### Issue: "Switch not found in mapping"
**Solution:** Verify switch names match the expected format.

### Issue: "Hardware interface not available"
**Solution:** Install Sequent Microsystems libraries or run in simulation mode.

## Support

If you continue to have issues:
1. Check the system logs: `tail -f solar_heating_v3.log`
2. Run the test scripts to isolate the problem
3. Verify MQTT connectivity
4. Check Home Assistant MQTT integration settings

## Files Modified

The following files were updated to fix control issues:
- `mqtt_handler.py` - Added missing topic subscriptions
- `main_system.py` - Fixed cartridge heater relay mapping
- `test_controls.py` - New automated test script
- `manual_control_test.py` - New interactive test script
