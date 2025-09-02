# Real-time Energy Sensor Setup Guide

This guide explains how to set up the new real-time energy sensor that shows kW, temperature change rate, and efficiency metrics compared to average temperature and stored energy total.

## Overview

The real-time energy sensor provides:
- **Real-time Energy Rate (kW)**: Current energy collection rate in kilowatts
- **Temperature Change Rate (°C/h)**: Rate of temperature change per hour
- **Energy Efficiency Index (%)**: Efficiency score from 0-100
- **System Performance Score (/100)**: Overall system performance rating
- **Trend Indicators**: Whether energy and temperature are increasing/decreasing/stable
- **Comparison Ratios**: Energy vs temperature, energy vs total stored energy, etc.

## MQTT Topic

The sensor data is published to:
```
solar_heating_v3/status/realtime_energy_sensor
```

## Home Assistant Configuration

Add the following to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    # Real-time Energy Rate Sensor
    - name: "Real-time Energy Rate"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.energy_rate_kw }}"
      unit_of_measurement: "kW"
      device_class: "power"
      state_class: "measurement"
      
    # Temperature Change Rate Sensor
    - name: "Real-time Temperature Rate"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.temp_rate_per_hour }}"
      unit_of_measurement: "°C/h"
      state_class: "measurement"
      
    # Energy Efficiency Index Sensor
    - name: "Energy Efficiency Index"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.efficiency_index }}"
      unit_of_measurement: "%"
      state_class: "measurement"
      
    # System Performance Score Sensor
    - name: "System Performance Score"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.performance_score }}"
      unit_of_measurement: "/100"
      state_class: "measurement"
      
    # Energy Trend Sensor
    - name: "Energy Trend"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.energy_trend }}"
      
    # Temperature Trend Sensor
    - name: "Temperature Trend"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.temperature_trend }}"
      
    # Energy/Temperature Ratio Sensor
    - name: "Energy Temperature Ratio"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.energy_temp_ratio }}"
      state_class: "measurement"
      
    # Energy/Total Ratio Sensor
    - name: "Energy Total Ratio"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.energy_total_ratio }}"
      state_class: "measurement"
      
    # Temperature Change Ratio Sensor
    - name: "Temperature Change Ratio"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.temp_change_ratio }}"
      state_class: "measurement"
      
    # Energy Efficiency Factor Sensor
    - name: "Energy Efficiency Factor"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.efficiency_factor }}"
      state_class: "measurement"
      
    # Water Usage Rate Sensor
    - name: "Water Usage Rate"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.water_usage_rate_kw }}"
      unit_of_measurement: "kW"
      state_class: "measurement"
      
    # Water Usage Intensity Sensor
    - name: "Water Usage Intensity"
      state_topic: "solar_heating_v3/status/realtime_energy_sensor"
      value_template: "{{ value_json.water_usage_intensity }}"
```

## Dashboard Cards

### Energy Rate Chart
```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Real-time Energy Rate
  show_states: true
  colorize_states: true
graph_span: 1h
series:
  - entity: sensor.realtime_energy_rate_kw
    name: Energy Rate (kW)
    color: "#ff6b6b"
    stroke_width: 3
apex_config:
  chart:
    height: 200
  yaxis:
    - min: 0
      max: 5
      decimals: 3
      title:
        text: "Energy Rate (kW)"
```

### Temperature Change Rate Chart
```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Temperature Change Rate
  show_states: true
  colorize_states: true
graph_span: 1h
series:
  - entity: sensor.realtime_temp_rate_per_hour
    name: Temp Change (°C/h)
    color: "#4ecdc4"
    stroke_width: 3
apex_config:
  chart:
    height: 200
  yaxis:
    - min: -10
      max: 10
      decimals: 2
      title:
        text: "Temperature Change (°C/h)"
```

### Efficiency Gauge
```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Energy Efficiency Index
graph_span: 1h
series:
  - entity: sensor.energy_efficiency_index
    name: Efficiency (%)
    color: "#45b7d1"
    stroke_width: 3
apex_config:
  chart:
    height: 200
    type: radialBar
  plotOptions:
    radialBar:
      startAngle: -135
      endAngle: 135
      hollow:
        margin: 15
        size: 70%
      track:
        background: "#e7e7e7"
        strokeWidth: 97%
        margin: 5
        dropShadow:
          enabled: true
          top: 2
          left: 0
          blur: 4
          opacity: 0.15
      dataLabels:
        name:
          show: true
          fontSize: 16
          fontFamily: "Helvetica, Arial, sans-serif"
          fontWeight: 600
          offsetY: -10
        value:
          show: true
          fontSize: 22
          fontFamily: "Helvetica, Arial, sans-serif"
          fontWeight: 600
          offsetY: 16
          formatter: function(val) {
            return val + "%"
          }
```

### Performance Score Gauge
```yaml
type: custom:apexcharts-card
header:
  show: true
  title: System Performance Score
graph_span: 1h
series:
  - entity: sensor.system_performance_score
    name: Performance
    color: "#96ceb4"
    stroke_width: 3
apex_config:
  chart:
    height: 200
    type: radialBar
  plotOptions:
    radialBar:
      startAngle: -135
      endAngle: 135
      hollow:
        margin: 15
        size: 70%
      track:
        background: "#e7e7e7"
        strokeWidth: 97%
        margin: 5
        dropShadow:
          enabled: true
          top: 2
          left: 0
          blur: 4
          opacity: 0.15
      dataLabels:
        name:
          show: true
          fontSize: 16
          fontFamily: "Helvetica, Arial, sans-serif"
          fontWeight: 600
          offsetY: -10
        value:
          show: true
          fontSize: 22
          fontFamily: "Helvetica, Arial, sans-serif"
          fontWeight: 600
          offsetY: 16
          formatter: function(val) {
            return val + "/100"
          }
```

### Trend Indicators
```yaml
type: entities
title: System Trends
entities:
  - entity: sensor.energy_trend
    name: Energy Trend
  - entity: sensor.temperature_trend
    name: Temperature Trend
```

### Comparison Metrics Chart
```yaml
type: custom:apexcharts-card
header:
  show: true
  title: Energy Ratios & Comparisons
graph_span: 1h
series:
  - entity: sensor.energy_temp_ratio
    name: Energy/Temp Ratio
    color: "#ffa726"
    stroke_width: 2
  - entity: sensor.energy_total_ratio
    name: Energy/Total Ratio
    color: "#ab47bc"
    stroke_width: 2
  - entity: sensor.temp_change_ratio
    name: Temp Change Ratio
    color: "#26a69a"
    stroke_width: 2
apex_config:
  chart:
    height: 200
  yaxis:
    - min: 0
      max: 1
      decimals: 4
      title:
        text: "Ratio Values"
```

### Current Values Summary
```yaml
type: entities
title: Current Energy Metrics
entities:
  - entity: sensor.realtime_energy_rate_kw
    name: Current Energy Rate
    unit_of_measurement: kW
  - entity: sensor.realtime_temp_rate_per_hour
    name: Current Temp Rate
    unit_of_measurement: °C/h
  - entity: sensor.energy_efficiency_index
    name: Efficiency Index
    unit_of_measurement: "%"
  - entity: sensor.system_performance_score
    name: Performance Score
    unit_of_measurement: "/100"
  - entity: sensor.energy_efficiency_factor
    name: Efficiency Factor
```

## Automation Examples

### Alert on Low Efficiency
```yaml
automation:
  - alias: "Alert Low Energy Efficiency"
    description: "Send notification when energy efficiency drops below 30%"
    trigger:
      platform: numeric_state
      entity_id: sensor.energy_efficiency_index
      below: 30
    condition:
      - condition: time
        after: "08:00:00"
        before: "22:00:00"
    action:
      - service: notify.mobile_app
        data:
          title: "Low Energy Efficiency Alert"
          message: "Energy efficiency has dropped to {{ states('sensor.energy_efficiency_index') }}%. Check system performance."
```

### Alert on High Energy Rate
```yaml
automation:
  - alias: "Alert High Energy Rate"
    description: "Send notification when energy rate exceeds 3 kW"
    trigger:
      platform: numeric_state
      entity_id: sensor.realtime_energy_rate_kw
      above: 3
    action:
      - service: notify.mobile_app
        data:
          title: "High Energy Rate Alert"
          message: "Energy rate is {{ states('sensor.realtime_energy_rate_kw') }} kW. System is collecting energy efficiently!"
```

### Alert on Heavy Water Usage
```yaml
automation:
  - alias: "Alert Heavy Water Usage"
    description: "Send notification when water usage becomes heavy"
    trigger:
      platform: state
      entity_id: sensor.water_usage_intensity
      to: "heavy"
    action:
      - service: notify.mobile_app
        data:
          title: "Heavy Water Usage Alert"
          message: "Heavy water usage detected: {{ states('sensor.water_usage_rate_kw') }} kW. Monitor system performance."
```

### Alert on Very Heavy Water Usage
```yaml
automation:
  - alias: "Alert Very Heavy Water Usage"
    description: "Send notification when water usage becomes very heavy"
    trigger:
      platform: state
      entity_id: sensor.water_usage_intensity
      to: "very_heavy"
    action:
      - service: notify.mobile_app
        data:
          title: "Very Heavy Water Usage Alert"
          message: "Very heavy water usage detected: {{ states('sensor.water_usage_rate_kw') }} kW. Check for leaks or excessive usage."
```

## Script Examples

### Reset Energy Metrics
```yaml
script:
  reset_energy_metrics:
    alias: "Reset Energy Metrics"
    sequence:
      - service: mqtt.publish
        data:
          topic: "solar_heating_v3/control/reset_metrics"
          payload: '{"action": "reset_energy_metrics"}'
```

## Understanding the Metrics

### Energy Rate (kW)
- **Positive values**: System is gaining energy (solar heating active)
- **Negative values**: System is losing energy (water being used - showers, heating, etc.)
- **Typical range**: -3 to +5 kW (negative during water usage, positive during heating)

### Temperature Change Rate (°C/h)
- **Positive values**: Temperature is increasing (solar heating)
- **Negative values**: Temperature is decreasing (water usage, heat loss)
- **Typical range**: -10 to +10 °C/h (negative during water usage, positive during heating)

### Energy Efficiency Index (%)
- **0-30%**: Poor efficiency, check system
- **30-60%**: Moderate efficiency
- **60-80%**: Good efficiency
- **80-100%**: Excellent efficiency

### System Performance Score (/100)
- **0-20**: Poor performance
- **20-40**: Below average
- **40-60**: Average
- **60-80**: Good
- **80-100**: Excellent

### Trend Indicators
- **heating**: System is gaining energy (positive energy rate)
- **water_usage**: System is losing energy due to water consumption
- **cooling**: Temperature is decreasing (heat loss)
- **stable**: Values are relatively constant

### Water Usage Metrics
- **water_usage_rate_kw**: Rate of energy loss due to water consumption (always positive)
- **water_usage_intensity**: 
  - **none**: No water usage
  - **light**: < 0.5 kW usage rate
  - **moderate**: 0.5-1.5 kW usage rate
  - **heavy**: 1.5-3.0 kW usage rate
  - **very_heavy**: > 3.0 kW usage rate

## Troubleshooting

### Sensor Not Updating
1. Check MQTT connection in the main system
2. Verify the topic `solar_heating_v3/status/realtime_energy_sensor` is being published
3. Check Home Assistant MQTT integration is working

### Incorrect Values
1. Verify temperature sensors are working correctly
2. Check stored energy calculations
3. Ensure system has been running for at least 30 seconds (minimum calculation interval)

### Performance Issues
1. The sensor calculates every 30 seconds minimum
2. Historical data is stored in system state
3. First few readings may be zero until historical data is established

## Integration with Existing System

The real-time energy sensor integrates seamlessly with the existing v3 system:
- Uses existing temperature sensors
- Leverages current stored energy calculations
- Publishes via existing MQTT infrastructure
- Compatible with current Home Assistant setup

No additional hardware or major system changes are required.
