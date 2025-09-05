# V3 Sensor Coverage Table

This table shows which v3 sensors cover each legacy v1/v2 sensor, organized by v3 sensor category.

## 🔄 **V3 Sensor → Legacy Sensor Coverage**

### **Temperature Sensors**

| v3 Sensor | v3 Topic | Covers Legacy Sensor | Legacy Topic | Legacy Format |
|-----------|----------|---------------------|--------------|---------------|
| `rtd_sensor_0` | `homeassistant/sensor/solar_heating_rtd_sensor_0/state` | `sequentmicrosystems_1_1` | `sequentmicrosystems/sequentmicrosystems_1_1` | `{"name": "sequentmicrosystems_1_1", "temperature": value}` |
| `rtd_sensor_1` | `homeassistant/sensor/solar_heating_rtd_sensor_1/state` | `sequentmicrosystems_1_2` | `sequentmicrosystems/sequentmicrosystems_1_2` | `{"name": "sequentmicrosystems_1_2", "temperature": value}` |
| `rtd_sensor_2` | `homeassistant/sensor/solar_heating_rtd_sensor_2/state` | `sequentmicrosystems_1_3` | `sequentmicrosystems/sequentmicrosystems_1_3` | `{"name": "sequentmicrosystems_1_3", "temperature": value}` |
| `rtd_sensor_3` | `homeassistant/sensor/solar_heating_rtd_sensor_3/state` | `sequentmicrosystems_1_4` | `sequentmicrosystems/sequentmicrosystems_1_4` | `{"name": "sequentmicrosystems_1_4", "temperature": value}` |
| `rtd_sensor_4` | `homeassistant/sensor/solar_heating_rtd_sensor_4/state` | `sequentmicrosystems_1_5` | `sequentmicrosystems/sequentmicrosystems_1_5` | `{"name": "sequentmicrosystems_1_5", "temperature": value}` |
| `rtd_sensor_5` | `homeassistant/sensor/solar_heating_rtd_sensor_5/state` | `sequentmicrosystems_1_6` | `sequentmicrosystems/sequentmicrosystems_1_6` | `{"name": "sequentmicrosystems_1_6", "temperature": value}` |
| `rtd_sensor_6` | `homeassistant/sensor/solar_heating_rtd_sensor_6/state` | `sequentmicrosystems_1_7` | `sequentmicrosystems/sequentmicrosystems_1_7` | `{"name": "sequentmicrosystems_1_7", "temperature": value}` |
| `rtd_sensor_7` | `homeassistant/sensor/solar_heating_rtd_sensor_7/state` | `sequentmicrosystems_1_8` | `sequentmicrosystems/sequentmicrosystems_1_8` | `{"name": "sequentmicrosystems_1_8", "temperature": value}` |
| `megabas_sensor_1` | `homeassistant/sensor/solar_heating_megabas_sensor_1/state` | `sequentmicrosystems_4_1` | `sequentmicrosystems/sequentmicrosystems_4_1` | `{"name": "sequentmicrosystems_4_1", "temperature": value}` |
| `megabas_sensor_2` | `homeassistant/sensor/solar_heating_megabas_sensor_2/state` | `sequentmicrosystems_4_2` | `sequentmicrosystems/sequentmicrosystems_4_2` | `{"name": "sequentmicrosystems_4_2", "temperature": value}` |
| `megabas_sensor_3` | `homeassistant/sensor/solar_heating_megabas_sensor_3/state` | `sequentmicrosystems_4_3` | `sequentmicrosystems/sequentmicrosystems_4_3` | `{"name": "sequentmicrosystems_4_3", "temperature": value}` |
| `megabas_sensor_4` | `homeassistant/sensor/solar_heating_megabas_sensor_4/state` | `sequentmicrosystems_4_4` | `sequentmicrosystems/sequentmicrosystems_4_4` | `{"name": "sequentmicrosystems_4_4", "temperature": value}` |
| `megabas_sensor_5` | `homeassistant/sensor/solar_heating_megabas_sensor_5/state` | `sequentmicrosystems_4_5` | `sequentmicrosystems/sequentmicrosystems_4_5` | `{"name": "sequentmicrosystems_4_5", "temperature": value}` |
| `megabas_sensor_6` | `homeassistant/sensor/solar_heating_megabas_sensor_6/state` | `sequentmicrosystems_4_6` | `sequentmicrosystems/sequentmicrosystems_4_6` | `{"name": "sequentmicrosystems_4_6", "temperature": value}` |
| `megabas_sensor_7` | `homeassistant/sensor/solar_heating_megabas_sensor_7/state` | `sequentmicrosystems_4_7` | `sequentmicrosystems/sequentmicrosystems_4_7` | `{"name": "sequentmicrosystems_4_7", "temperature": value}` |
| `megabas_sensor_8` | `homeassistant/sensor/solar_heating_megabas_sensor_8/state` | `sequentmicrosystems_4_8` | `sequentmicrosystems/sequentmicrosystems_4_8` | `{"name": "sequentmicrosystems_4_8", "temperature": value}` |

### **Named Sensors (v3 Aliases) - FTX Only**

| v3 Sensor | v3 Topic | Covers Legacy Sensor | Legacy Topic | Legacy Format |
|-----------|----------|---------------------|--------------|---------------|
| `uteluft` | `homeassistant/sensor/solar_heating_uteluft/state` | `sequentmicrosystems_4_1` | `sequentmicrosystems/sequentmicrosystems_4_1` | `{"name": "sequentmicrosystems_4_1", "temperature": value}` |
| `avluft` | `homeassistant/sensor/solar_heating_avluft/state` | `sequentmicrosystems_4_2` | `sequentmicrosystems/sequentmicrosystems_4_2` | `{"name": "sequentmicrosystems_4_2", "temperature": value}` |
| `tilluft` | `homeassistant/sensor/solar_heating_tilluft/state` | `sequentmicrosystems_4_3` | `sequentmicrosystems/sequentmicrosystems_4_3` | `{"name": "sequentmicrosystems_4_3", "temperature": value}` |
| `franluft` | `homeassistant/sensor/solar_heating_franluft/state` | `sequentmicrosystems_4_4` | `sequentmicrosystems/sequentmicrosystems_4_4` | `{"name": "sequentmicrosystems_4_4", "temperature": value}` |

**Note:** Legacy aliases `solar_collector`, `storage_tank`, and `return_line` have been removed. Use the modern sensor names `solar_collector_temp`, `storage_tank_temp`, and `return_line_temp` instead.

### **Energy Sensors**

| v3 Sensor | v3 Topic | Covers Legacy Sensor | Legacy Topic | Legacy Format |
|-----------|----------|---------------------|--------------|---------------|
| `stored_energy_kwh` | `homeassistant/sensor/solar_heating_stored_energy_kwh/state` | `stored_energy_kwh` | `sequentmicrosystems/stored_energy` | `{"name": "stored_energy", "stored_energy_kwh": value, ...}` |
| `stored_energy_top_kwh` | `homeassistant/sensor/solar_heating_stored_energy_top_kwh/state` | `stored_energy_top_kwh` | `sequentmicrosystems/stored_energy` | `{"name": "stored_energy", "stored_energy_top_kwh": value, ...}` |
| `stored_energy_bottom_kwh` | `homeassistant/sensor/solar_heating_stored_energy_bottom_kwh/state` | `stored_energy_bottom_kwh` | `sequentmicrosystems/stored_energy` | `{"name": "stored_energy", "stored_energy_bottom_kwh": value, ...}` |
| `average_temperature` | `homeassistant/sensor/solar_heating_average_temperature/state` | `average_temperature` | `sequentmicrosystems/stored_energy` | `{"name": "stored_energy", "average_temperature": value, ...}` |

### **FTX (Heat Exchanger) Sensors**

| v3 Sensor | v3 Topic | Covers Legacy Sensor | Legacy Topic | Legacy Format |
|-----------|----------|---------------------|--------------|---------------|
| `uteluft` | `homeassistant/sensor/solar_heating_uteluft/state` | `uteluft` | `sequentmicrosystems/ftx` | `{"uteluft": value, "avluft": value, ...}` |
| `avluft` | `homeassistant/sensor/solar_heating_avluft/state` | `avluft` | `sequentmicrosystems/ftx` | `{"uteluft": value, "avluft": value, ...}` |
| `tilluft` | `homeassistant/sensor/solar_heating_tilluft/state` | `tilluft` | `sequentmicrosystems/ftx` | `{"uteluft": value, "avluft": value, ...}` |
| `franluft` | `homeassistant/sensor/solar_heating_franluft/state` | `franluft` | `sequentmicrosystems/ftx` | `{"uteluft": value, "avluft": value, ...}` |
| `heat_exchanger_efficiency` | `homeassistant/sensor/solar_heating_heat_exchanger_efficiency/state` | `effekt_varmevaxlare` | `sequentmicrosystems/ftx` | `{"uteluft": value, "avluft": value, ...}` |

### **Solar Collector Sensors**

| v3 Sensor | v3 Topic | Covers Legacy Sensor | Legacy Topic | Legacy Format |
|-----------|----------|---------------------|--------------|---------------|
| `solar_collector_dt_running` | `homeassistant/sensor/solar_heating_solar_collector_dt_running/state` | `dT_running` | `sequentmicrosystems/suncollector` | `{"dT_running": value, "dT": value, ...}` |
| `solar_collector_dt` | `homeassistant/sensor/solar_heating_solar_collector_dt/state` | `dT` | `sequentmicrosystems/suncollector` | `{"dT_running": value, "dT": value, ...}` |
| `primary_pump` | `homeassistant/switch/solar_heating_primary_pump/state` | `pump` | `sequentmicrosystems/suncollector` | `{"dT_running": value, "pump": "ON"/"OFF", ...}` |
| `system_mode` | `homeassistant/sensor/solar_heating_system_mode/state` | `mode` | `sequentmicrosystems/suncollector` | `{"dT_running": value, "mode": value, ...}` |

**Note:** Redundant sensors `solar_collector_mode`, `solar_collector_state`, and `solar_collector_overheated` have been removed. Use `system_mode` for all mode information.

### **Test Mode Sensors**

| v3 Sensor | v3 Topic | Covers Legacy Sensor | Legacy Topic | Legacy Format |
|-----------|----------|---------------------|--------------|---------------|
| `test_mode` | `homeassistant/binary_sensor/solar_heating_test_mode/state` | `test_mode` | `sequentmicrosystems/test_mode` | `{"test_mode": "true"/"false", "log_level": value}` |
| `test_mode` | `homeassistant/binary_sensor/solar_heating_test_mode/state` | `switch_status` | `sequentmicrosystems/test_switch` | `{"switch_status": "on"/"off"}` |
| `log_level` | `homeassistant/sensor/solar_heating_log_level/state` | `log_level` | `sequentmicrosystems/test_mode` | `{"test_mode": "true"/"false", "log_level": value}` |

### **Switch Sensors**

| v3 Sensor | v3 Topic | Covers Legacy Sensor | Legacy Topic | Legacy Format |
|-----------|----------|---------------------|--------------|---------------|
| `primary_pump` | `homeassistant/switch/solar_heating_primary_pump/state` | `solar_pump` | `homeassistant/switch/solar_pump/config` | Discovery config for pump |
| `cartridge_heater` | `homeassistant/switch/solar_heating_cartridge_heater/state` | `solar_heater` | `homeassistant/switch/solar_heater/config` | Discovery config for heater |

### **V2 Discovery Sensors**

| v3 Sensor | v3 Topic | Covers Legacy Sensor | Legacy Topic | Legacy Format |
|-----------|----------|---------------------|--------------|---------------|
| `solar_collector_temp` | `homeassistant/sensor/solar_heating_solar_collector_temp/state` | `solar_t1` | `homeassistant/sensor/solar_t1/config` | Discovery config for T1 |
| `storage_tank_temp` | `homeassistant/sensor/solar_heating_storage_tank_temp/state` | `solar_t2` | `homeassistant/sensor/solar_t2/config` | Discovery config for T2 |

**Note:** Legacy aliases `solar_collector` and `storage_tank` have been removed. Use the modern sensor names `solar_collector_temp` and `storage_tank_temp` instead.

## 🆕 **New v3 Sensors (No Legacy Coverage)**

| v3 Sensor | v3 Topic | Description | Status |
|-----------|----------|-------------|---------|
| `realtime_energy_rate_kw` | `solar_heating_v3/status/realtime_energy_sensor` | Real-time energy rate in kW | 🆕 **NEW** |
| `realtime_temp_rate_per_hour` | `solar_heating_v3/status/realtime_energy_sensor` | Temperature change rate °C/h | 🆕 **NEW** |
| `energy_change_rate_kw` | `homeassistant/sensor/solar_heating_energy_change_rate_kw/state` | Energy change rate (kW) | 🆕 **NEW** |
| `temperature_change_rate_c_h` | `homeassistant/sensor/solar_heating_temperature_change_rate_c_h/state` | Temperature change rate (°C/h) | 🆕 **NEW** |
| `energy_efficiency_index` | `solar_heating_v3/status/realtime_energy_sensor` | Energy efficiency index % | 🆕 **NEW** |
| `system_performance_score` | `solar_heating_v3/status/realtime_energy_sensor` | System performance score /100 | 🆕 **NEW** |
| `water_usage_rate_kw` | `solar_heating_v3/status/realtime_energy_sensor` | Water usage rate in kW | 🆕 **NEW** |
| `water_usage_intensity` | `solar_heating_v3/status/realtime_energy_sensor` | Water usage intensity level | 🆕 **NEW** |
| `energy_collection_rate_kwh_per_hour` | `homeassistant/sensor/solar_heating_energy_collection_rate_kwh_per_hour/state` | Energy collection rate | 🆕 **NEW** |
| `energy_collected_today_kwh` | `homeassistant/sensor/solar_heating_energy_collected_today_kwh/state` | Daily energy collected | 🆕 **NEW** |
| `energy_collected_hour_kwh` | `homeassistant/sensor/solar_heating_energy_collected_hour_kwh/state` | Hourly energy collected | 🆕 **NEW** |
| `solar_energy_today_kwh` | `homeassistant/sensor/solar_heating_solar_energy_today_kwh/state` | Daily solar energy | 🆕 **NEW** |
| `cartridge_energy_today_kwh` | `homeassistant/sensor/solar_heating_cartridge_energy_today_kwh/state` | Daily cartridge energy | 🆕 **NEW** |
| `pellet_energy_today_kwh` | `homeassistant/sensor/solar_heating_pellet_energy_today_kwh/state` | Daily pellet energy | 🆕 **NEW** |
| `pump_runtime_hours` | `homeassistant/sensor/solar_heating_pump_runtime_hours/state` | Pump runtime hours | 🆕 **NEW** |
| `heating_cycles_count` | `homeassistant/sensor/solar_heating_heating_cycles_count/state` | Heating cycles count | 🆕 **NEW** |
| `average_heating_duration` | `homeassistant/sensor/solar_heating_average_heating_duration/state` | Average heating duration | 🆕 **NEW** |

## 📊 **Coverage Summary by v3 Sensor Category**

### **Temperature Sensors (16 sensors)**
- **Coverage**: 100% of legacy temperature sensors
- **Legacy Sensors Covered**: 16 individual temperature sensors
- **Status**: ✅ **FULLY COVERED**

### **Named Sensors (4 sensors)**
- **Coverage**: 100% of legacy named sensors (FTX only)
- **Legacy Sensors Covered**: 4 FTX named temperature sensors
- **Status**: ✅ **FULLY COVERED**
- **Note**: Legacy aliases `solar_collector`, `storage_tank`, and `return_line` removed

### **Energy Sensors (4 sensors)**
- **Coverage**: 100% of legacy energy sensors
- **Legacy Sensors Covered**: 4 energy calculation sensors
- **Status**: ✅ **FULLY COVERED**

### **FTX Sensors (5 sensors)**
- **Coverage**: 100% of legacy FTX sensors
- **Legacy Sensors Covered**: 5 heat exchanger sensors
- **Status**: ✅ **FULLY COVERED**

### **Solar Collector Sensors (4 sensors)**
- **Coverage**: 100% of legacy solar collector sensors
- **Legacy Sensors Covered**: 4 solar collector sensors
- **Status**: ✅ **FULLY COVERED**
- **Note**: Redundant sensors `solar_collector_mode`, `solar_collector_state`, and `solar_collector_overheated` removed

### **Test Mode Sensors (2 sensors)**
- **Coverage**: 100% of legacy test mode sensors
- **Legacy Sensors Covered**: 2 test mode sensors
- **Status**: ✅ **FULLY COVERED**

### **Switch Sensors (4 sensors)**
- **Coverage**: 100% of legacy switch sensors
- **Legacy Sensors Covered**: 4 switch sensors
- **Status**: ✅ **FULLY COVERED**

### **New v3 Sensors (15+ sensors)**
- **Coverage**: 0% (these are new capabilities)
- **Legacy Sensors Covered**: None
- **Status**: 🆕 **NEW FUNCTIONALITY**

## 🎯 **Key Takeaway**

**Every single legacy v1/v2 sensor has a v3 equivalent**, plus 15+ new sensors that provide additional functionality. This means:

1. **Zero functionality loss** when removing legacy sensors
2. **Enhanced capabilities** with new v3 sensors
3. **Better data structure** and naming conventions
4. **Cleaner MQTT traffic** without duplicates
5. **Future-proof architecture** for new features

The v3 system is a complete superset of the legacy system!
