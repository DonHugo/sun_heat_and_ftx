# Home Assistant Integration for Solar Heating System v3

This guide explains how to integrate your v3 solar heating system with Home Assistant using MQTT.

## Overview

The v3 system publishes comprehensive sensor data and system status via MQTT, making it easy to monitor and control your solar heating system through Home Assistant.

## Prerequisites

1. **Home Assistant** installed and running
2. **MQTT Broker** configured (Mosquitto recommended)
3. **Solar Heating v3 System** running and connected to MQTT
4. **MQTT Integration** enabled in Home Assistant

## MQTT Configuration

### 1. MQTT Broker Setup

Ensure your MQTT broker is configured with these settings:
- **Broker**: `192.168.0.110` (or your broker IP)
- **Port**: `1883`
- **Username**: `mqtt_beaches`
- **Password**: `uQX6NiZ.7R`

### 2. Home Assistant MQTT Integration

Add the MQTT integration in Home Assistant:

```yaml
# configuration.yaml
mqtt:
  broker: 192.168.0.110
  port: 1883
  username: mqtt_beaches
  password: uQX6NiZ.7R
  discovery: true
  discovery_prefix: homeassistant
```

## Available Sensors

### Temperature Sensors

#### RTD Sensors (Water Heater Stratification)
- `sensor.solar_heating_v3_rtd_sensor_0` - Bottom of water heater (coldest)
- `sensor.solar_heating_v3_rtd_sensor_1` - 20cm from bottom
- `sensor.solar_heating_v3_rtd_sensor_2` - 40cm from bottom
- `sensor.solar_heating_v3_rtd_sensor_3` - 60cm from bottom
- `sensor.solar_heating_v3_rtd_sensor_4` - 80cm from bottom
- `sensor.solar_heating_v3_rtd_sensor_5` - 100cm from bottom
- `sensor.solar_heating_v3_rtd_sensor_6` - 120cm from bottom
- `sensor.solar_heating_v3_rtd_sensor_7` - 140cm from bottom (hottest)

#### Water Heater Height-Based Sensors
- `sensor.solar_heating_v3_water_heater_bottom` - Bottom (0cm)
- `sensor.solar_heating_v3_water_heater_20cm` - 20cm from bottom
- `sensor.solar_heating_v3_water_heater_40cm` - 40cm from bottom
- `sensor.solar_heating_v3_water_heater_60cm` - 60cm from bottom
- `sensor.solar_heating_v3_water_heater_80cm` - 80cm from bottom
- `sensor.solar_heating_v3_water_heater_100cm` - 100cm from bottom
- `sensor.solar_heating_v3_water_heater_120cm` - 120cm from bottom
- `sensor.solar_heating_v3_water_heater_140cm` - 140cm from bottom (Top)

#### FTX System Sensors
- `sensor.solar_heating_v3_outdoor_air_temp` - Outdoor air temperature
- `sensor.solar_heating_v3_exhaust_air_temp` - Exhaust air temperature
- `sensor.solar_heating_v3_supply_air_temp` - Supply air temperature
- `sensor.solar_heating_v3_return_air_temp` - Return air temperature

#### Solar System Sensors
- `sensor.solar_heating_v3_solar_collector_temp` - Solar collector temperature
- `sensor.solar_heating_v3_storage_tank_temp` - Storage tank temperature
- `sensor.solar_heating_v3_return_line_temp` - Return line temperature

#### MegaBAS Sensors (Raw)
- `sensor.solar_heating_v3_megabas_sensor_1` through `sensor.solar_heating_v3_megabas_sensor_8`

### Calculated Values

#### Energy Metrics
- `sensor.solar_heating_v3_stored_energy_kwh` - Total stored energy
- `sensor.solar_heating_v3_stored_energy_top_kwh` - Top section energy
- `sensor.solar_heating_v3_stored_energy_bottom_kwh` - Bottom section energy

#### Efficiency Metrics
- `sensor.solar_heating_v3_heat_exchanger_efficiency` - Heat exchanger efficiency (%)
- `sensor.solar_heating_v3_solar_collector_dt` - Solar collector delta T (°C)

#### System Health
- `sensor.solar_heating_v3_sensor_health_score` - Sensor health score (%)
- `sensor.solar_heating_v3_overheating_risk` - Overheating risk (%)

#### Operational Metrics
- `sensor.solar_heating_v3_pump_runtime_hours` - Pump runtime (hours)
- `sensor.solar_heating_v3_heating_cycles_count` - Heating cycles count
- `sensor.solar_heating_v3_average_heating_duration` - Average heating duration (hours)

#### Water Heater Analysis
- `sensor.solar_heating_v3_water_heater_stratification` - Stratification quality (°C/cm)
- `sensor.solar_heating_v3_water_heater_gradient_cm` - Temperature gradient (°C/cm)
- `sensor.solar_heating_v3_average_temperature` - Average temperature (°C)

### System State
- `sensor.solar_heating_v3_system_mode` - System mode (normal, manual, overheated, error, maintenance)
- `switch.solar_heating_v3_primary_pump` - Primary pump control

- `switch.solar_heating_v3_cartridge_heater` - Cartridge heater control
- `switch.solar_heating_v3_test_switch` - Test switch control

### Legacy Aliases (Backward Compatibility)
- `sensor.solar_heating_v3_uteluft` - Outdoor air (legacy name)
- `sensor.solar_heating_v3_avluft` - Exhaust air (legacy name)
- `sensor.solar_heating_v3_tilluft` - Supply air (legacy name)
- `sensor.solar_heating_v3_franluft` - Return air (legacy name)
- `sensor.solar_heating_v3_solar_collector` - Solar collector (T1)
- `sensor.solar_heating_v3_storage_tank` - Storage tank (T2)
- `sensor.solar_heating_v3_return_line` - Return line (T3)

## Dashboard Installation

### Option 1: Simple Dashboard (Recommended)

1. Copy the contents of `home_assistant_dashboard_v3_simple.yaml`
2. In Home Assistant, go to **Configuration** → **Dashboards**
3. Click **+ Add Dashboard**
4. Choose **YAML** mode
5. Paste the YAML content
6. Save the dashboard

### Option 2: Advanced Dashboard (Requires Custom Cards)

1. Install HACS (Home Assistant Community Store)
2. Add these custom repositories:
   - https://github.com/custom-cards/button-card
   - https://github.com/RomRider/apexcharts-card
   - https://github.com/thomasloven/lovelace-grid-layout
3. Install the custom cards
4. Copy the contents of `home_assistant_dashboard_v3.yaml`
5. Follow the same dashboard creation steps as above

## MQTT Topics

The v3 system publishes to these topics:

### Temperature Data
```
solar_heating_v3/temperature/{sensor_name}
```

### System Status
```
solar_heating_v3/status/system
```

### Control Commands
```
solar_heating_v3/control/{component}
```

### Home Assistant Discovery
```
homeassistant/sensor/solar_heating_v3_{sensor_name}/config
homeassistant/switch/solar_heating_v3_{component}/config
```

## Automation Examples

### 1. High Temperature Alert

```yaml
automation:
  - alias: "Solar Collector High Temperature Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.solar_heating_v3_solar_collector_temp
      above: 80
    action:
      - service: notify.mobile_app
        data:
          title: "Solar Heating Alert"
          message: "Solar collector temperature is {{ states('sensor.solar_heating_v3_solar_collector_temp') }}°C"
```

### 2. Pump Runtime Monitoring

```yaml
automation:
  - alias: "Pump Maintenance Reminder"
    trigger:
      platform: numeric_state
      entity_id: sensor.solar_heating_v3_pump_runtime_hours
      above: 1000
    action:
      - service: notify.mobile_app
        data:
          title: "Pump Maintenance Due"
          message: "Primary pump has run for {{ states('sensor.solar_heating_v3_pump_runtime_hours') }} hours"
```

### 3. System Mode Change Notification

```yaml
automation:
  - alias: "System Mode Change Alert"
    trigger:
      platform: state
      entity_id: sensor.solar_heating_v3_system_mode
    action:
      - service: notify.mobile_app
        data:
          title: "Solar Heating System Mode Changed"
          message: "System is now in {{ states('sensor.solar_heating_v3_system_mode') }} mode"
```

### 4. Energy Level Monitoring

```yaml
automation:
  - alias: "Low Energy Alert"
    trigger:
      platform: numeric_state
      entity_id: sensor.solar_heating_v3_stored_energy_kwh
      below: 10
    action:
      - service: notify.mobile_app
        data:
          title: "Low Energy Storage"
          message: "Stored energy is {{ states('sensor.solar_heating_v3_stored_energy_kwh') }} kWh"
```

## Troubleshooting

### Sensors Not Appearing

1. **Check MQTT Connection**: Verify the v3 system is connected to MQTT
2. **Check Topics**: Ensure Home Assistant is subscribed to the correct topics
3. **Check Discovery**: Verify MQTT discovery is enabled
4. **Check Logs**: Look for MQTT-related errors in Home Assistant logs

### Data Not Updating

1. **Check v3 System**: Ensure the v3 system is running and publishing data
2. **Check MQTT Broker**: Verify the broker is receiving messages
3. **Check Network**: Ensure network connectivity between all components
4. **Check Configuration**: Verify MQTT credentials and topics

### Dashboard Issues

1. **YAML Syntax**: Check for YAML syntax errors
2. **Entity Names**: Ensure entity names match the actual sensor names
3. **Custom Cards**: If using advanced dashboard, ensure custom cards are installed
4. **Permissions**: Check file permissions for dashboard configuration

## Monitoring Tips

### Key Metrics to Watch

1. **Solar Collector ΔT**: Should be positive when system is active
2. **Stored Energy**: Monitor daily energy production
3. **Sensor Health**: Should be above 90% for reliable operation
4. **Pump Runtime**: Track for maintenance scheduling
5. **Water Heater Stratification**: Should show clear temperature gradient

### Performance Optimization

1. **Temperature Thresholds**: Adjust based on your climate and usage
2. **Pump Control**: Monitor efficiency and adjust timing
3. **Energy Storage**: Optimize for your daily usage patterns
4. **System Health**: Regular monitoring prevents issues

## Support

For issues with the v3 system itself, check the system logs:
```bash
sudo journalctl -u solar_heating_v3 -f
```

For Home Assistant issues, check the Home Assistant logs in the web interface.

## Version History

- **v3.0**: Initial release with comprehensive sensor mapping
- **v3.1**: Added calculated efficiency metrics
- **v3.2**: Enhanced water heater stratification analysis
- **v3.3**: Improved MQTT discovery and Home Assistant integration
