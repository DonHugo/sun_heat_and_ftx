# Solar Heating System Sensor Mapping: v1 → v3

This document provides a comprehensive mapping between the v1 system sensor names and the v3 system sensor names.

## Overview

The v3 system uses a more structured approach to sensor naming, with clear prefixes and consistent naming conventions. This mapping helps understand how sensors from the v1 system correspond to the v3 system.

## Hardware Configuration

| Component | Stack Address | Description |
|-----------|---------------|-------------|
| RTD Board | 0 | 8 temperature sensors (0-7) |
| MegaBAS Board | 3 | 8 temperature sensors (1-8) |
| 4RELIND Board | 2 | 4 relay outputs (1-4) |

## Sensor Mapping Table

### RTD Sensors (Stack 0)

| v1 Name | v3 Name | Sensor ID | Description | Notes |
|---------|---------|-----------|-------------|-------|
| RTD_1 | rtd_sensor_0 | 0 | RTD Sensor 1 | |
| RTD_2 | rtd_sensor_1 | 1 | RTD Sensor 2 | |
| RTD_3 | rtd_sensor_2 | 2 | RTD Sensor 3 | |
| RTD_4 | rtd_sensor_3 | 3 | RTD Sensor 4 | Storage Tank Bottom |
| RTD_5 | rtd_sensor_4 | 4 | RTD Sensor 5 | Storage Tank Top |
| RTD_6 | rtd_sensor_5 | 5 | RTD Sensor 6 | Solar Collector (T1) |
| RTD_7 | rtd_sensor_6 | 6 | RTD Sensor 7 | Storage Tank (T2) |
| RTD_8 | rtd_sensor_7 | 7 | RTD Sensor 8 | Return Line (T3) |

### MegaBAS Sensors (Stack 3)

| v1 Name | v3 Name | Sensor ID | Description | Notes |
|---------|---------|-----------|-------------|-------|
| - | megabas_sensor_1 | 1 | MegaBAS Input 1 | uteluft (FTX) |
| - | megabas_sensor_2 | 2 | MegaBAS Input 2 | avluft (FTX) |
| - | megabas_sensor_3 | 3 | MegaBAS Input 3 | tilluft (FTX) |
| - | megabas_sensor_4 | 4 | MegaBAS Input 4 | franluft (FTX) |
| - | megabas_sensor_5 | 5 | MegaBAS Input 5 | Ambient Air (disabled) |
| - | megabas_sensor_6 | 6 | MegaBAS Input 6 | Unused |
| - | megabas_sensor_7 | 7 | MegaBAS Input 7 | Unused |
| - | megabas_sensor_8 | 8 | MegaBAS Input 8 | Unused |

### Named Sensors (v3 Aliases)

| v1 Name | v3 Name | Source | Description |
|---------|---------|--------|-------------|
| T1 | solar_collector | rtd_sensor_5 | Solar Collector Temperature |
| T2 | storage_tank | rtd_sensor_6 | Storage Tank Temperature |
| T3 | return_line | rtd_sensor_7 | Return Line Temperature |
| - | storage_tank_top | rtd_sensor_4 | Storage Tank Top Temperature |
| - | storage_tank_bottom | rtd_sensor_3 | Storage Tank Bottom Temperature |
| - | heat_exchanger_in | megabas_sensor_1 | Heat Exchanger Input |
| - | heat_exchanger_out | megabas_sensor_2 | Heat Exchanger Output |
| - | uteluft | megabas_sensor_1 | Outdoor Air Temperature |
| - | avluft | megabas_sensor_2 | Exhaust Air Temperature |
| - | tilluft | megabas_sensor_3 | Supply Air Temperature |
| - | franluft | megabas_sensor_4 | Return Air Temperature |

### Calculated Values

| v1 Name | v3 Name | Calculation | Description |
|---------|---------|-------------|-------------|
| - | heat_exchanger_efficiency | 100 - (avluft/franluft*100) | Heat Exchanger Efficiency % |
| - | solar_collector_dt | solar_collector - storage_tank | Solar Collector Delta T |
| - | solar_collector_dt_running | solar_collector - storage_tank | Solar Collector Delta T (running) |
| - | average_temperature | Average of RTD sensors 0-7 | Average Temperature |
| - | stored_energy_kwh | Energy calculation from RTD sensors | Total Stored Energy |
| - | stored_energy_top_kwh | Energy calculation from RTD sensors 5-7 | Top Stored Energy |
| - | stored_energy_bottom_kwh | Energy calculation from RTD sensors 0-4 | Bottom Stored Energy |

### Relay Outputs (4RELIND Stack 2)

| v1 Name | v3 Name | Relay ID | Description |
|---------|---------|----------|-------------|
| - | primary_pump | 1 | Primary Pump Control |
| - | secondary_pump | 2 | Secondary Pump Control |
| - | cartridge_heater | 3 | Cartridge Heater Control |
| - | test_switch | 4 | Test Switch Control |

## MQTT Topic Mapping

### v1 MQTT Topics
- `sequentmicrosystems/sequentmicrosystems_0_X` (RTD sensors)
- `sequentmicrosystems/sequentmicrosystems_3_X` (MegaBAS sensors)
- `sequentmicrosystems/ftx` (FTX data)
- `sequentmicrosystems/suncollector` (Solar collector data)
- `sequentmicrosystems/stored_energy` (Energy calculations)
- `sequentmicrosystems/test_switch` (Test switch status)

### v3 MQTT Topics
- `homeassistant/sensor/solar_heating_v3_X/config` (Discovery)
- `homeassistant/sensor/solar_heating_v3_X/state` (State updates)
- `homeassistant/switch/solar_heating_v3_X/config` (Switch discovery)
- `homeassistant/switch/solar_heating_v3_X/state` (Switch state)
- `homeassistant/number/solar_heating_v3_X/config` (Number discovery)
- `homeassistant/number/solar_heating_v3_X/state` (Number state)

## Key Differences

1. **Sensor Naming**: v3 uses structured names with prefixes (`rtd_sensor_X`, `megabas_sensor_X`)
2. **Aliases**: v3 provides meaningful aliases for commonly used sensors
3. **Home Assistant Integration**: v3 includes automatic Home Assistant discovery
4. **Calculated Values**: v3 provides more calculated values and efficiency metrics
5. **Error Handling**: v3 includes better error handling and validation

## Migration Notes

- **v1 T1, T2, T3** → **v3 solar_collector, storage_tank, return_line** (now using RTD sensors instead of MegaBAS)
- **v1 RTD sensors** → **v3 rtd_sensor_X** (direct mapping)
- **v1 MegaBAS sensors** → **v3 megabas_sensor_X** (direct mapping)
- **v1 FTX sensors** → **v3 uteluft, avluft, tilluft, franluft** (same MegaBAS inputs)

## Testing

Use the debug script to verify sensor readings:
```bash
cd /home/pi/solar_heating/python/v3
source /opt/solar_heating_v3/bin/activate
python3 debug_sensors.py
```

This will show all sensor readings and help verify the mapping is correct.
