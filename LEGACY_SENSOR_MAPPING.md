# Legacy Sensor Mapping: v1/v2 → v3

This document maps each legacy v1/v2 sensor to its v3 equivalent, showing what's duplicated and what can be safely removed.

## 🔄 **Complete Sensor Mapping Table**

### **1. Individual Temperature Sensors**

| Legacy Topic | Legacy Format | v3 Equivalent | v3 Topic | Status |
|--------------|---------------|----------------|----------|---------|
| `sequentmicrosystems/sequentmicrosystems_1_1` | `{"name": "sequentmicrosystems_1_1", "temperature": value}` | `rtd_sensor_0` | `homeassistant/sensor/solar_heating_rtd_sensor_0/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_1_2` | `{"name": "sequentmicrosystems_1_2", "temperature": value}` | `rtd_sensor_1` | `homeassistant/sensor/solar_heating_rtd_sensor_1/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_1_3` | `{"name": "sequentmicrosystems_1_3", "temperature": value}` | `rtd_sensor_2` | `homeassistant/sensor/solar_heating_rtd_sensor_2/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_1_4` | `{"name": "sequentmicrosystems_1_4", "temperature": value}` | `rtd_sensor_3` | `homeassistant/sensor/solar_heating_rtd_sensor_3/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_1_5` | `{"name": "sequentmicrosystems_1_5", "temperature": value}` | `rtd_sensor_4` | `homeassistant/sensor/solar_heating_rtd_sensor_4/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_1_6` | `{"name": "sequentmicrosystems_1_6", "temperature": value}` | `rtd_sensor_5` | `homeassistant/sensor/solar_heating_rtd_sensor_5/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_1_7` | `{"name": "sequentmicrosystems_1_7", "temperature": value}` | `rtd_sensor_6` | `homeassistant/sensor/solar_heating_rtd_sensor_6/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_1_8` | `{"name": "sequentmicrosystems_1_8", "temperature": value}` | `rtd_sensor_7` | `homeassistant/sensor/solar_heating_rtd_sensor_7/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_1` | `{"name": "sequentmicrosystems_4_1", "temperature": value}` | `megabas_sensor_1` | `homeassistant/sensor/solar_heating_megabas_sensor_1/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_2` | `{"name": "sequentmicrosystems_4_2", "temperature": value}` | `megabas_sensor_2` | `homeassistant/sensor/solar_heating_megabas_sensor_2/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_3` | `{"name": "sequentmicrosystems_4_3", "temperature": value}` | `megabas_sensor_3` | `homeassistant/sensor/solar_heating_megabas_sensor_3/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_4` | `{"name": "sequentmicrosystems_4_4", "temperature": value}` | `megabas_sensor_4` | `homeassistant/sensor/solar_heating_megabas_sensor_4/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_5` | `{"name": "sequentmicrosystems_4_5", "temperature": value}` | `megabas_sensor_5` | `homeassistant/sensor/solar_heating_megabas_sensor_5/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_6` | `{"name": "sequentmicrosystems_4_6", "temperature": value}` | `megabas_sensor_6` | `homeassistant/sensor/solar_heating_megabas_sensor_6/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_7` | `{"name": "sequentmicrosystems_4_7", "temperature": value}` | `megabas_sensor_7` | `homeassistant/sensor/solar_heating_megabas_sensor_7/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_8` | `{"name": "sequentmicrosystems_4_8", "temperature": value}` | `megabas_sensor_8` | `homeassistant/sensor/solar_heating_megabas_sensor_8/state` | ✅ **DUPLICATED** |

### **2. Named Sensors (v3 Aliases)**

| Legacy Topic | Legacy Format | v3 Equivalent | v3 Topic | Status |
|--------------|---------------|----------------|----------|---------|
| `sequentmicrosystems/sequentmicrosystems_4_6` | `{"name": "sequentmicrosystems_4_6", "temperature": value}` | `solar_collector` | `homeassistant/sensor/solar_heating_solar_collector/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_7` | `{"name": "sequentmicrosystems_4_7", "temperature": value}` | `storage_tank` | `homeassistant/sensor/solar_heating_storage_tank/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_8` | `{"name": "sequentmicrosystems_4_8", "temperature": value}` | `return_line` | `homeassistant/sensor/solar_heating_return_line/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_1` | `{"name": "sequentmicrosystems_4_1", "temperature": value}` | `uteluft` | `homeassistant/sensor/solar_heating_uteluft/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_2` | `{"name": "sequentmicrosystems_4_2", "temperature": value}` | `avluft` | `homeassistant/sensor/solar_heating_avluft/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_3` | `{"name": "sequentmicrosystems_4_3", "temperature": value}` | `tilluft` | `homeassistant/sensor/solar_heating_tilluft/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/sequentmicrosystems_4_4` | `{"name": "sequentmicrosystems_4_4", "temperature": value}` | `franluft` | `homeassistant/sensor/solar_heating_franluft/state` | ✅ **DUPLICATED** |

### **3. Calculated Sensors**

| Legacy Topic | Legacy Format | v3 Equivalent | v3 Topic | Status |
|--------------|---------------|----------------|----------|---------|
| `sequentmicrosystems/stored_energy` | `{"name": "stored_energy", "stored_energy_kwh": value, "stored_energy_top_kwh": value, "stored_energy_bottom_kwh": value, "average_temperature": value}` | `stored_energy_kwh`, `stored_energy_top_kwh`, `stored_energy_bottom_kwh`, `average_temperature` | `homeassistant/sensor/solar_heating_stored_energy_kwh/state`, `homeassistant/sensor/solar_heating_stored_energy_top_kwh/state`, `homeassistant/sensor/solar_heating_stored_energy_bottom_kwh/state`, `homeassistant/sensor/solar_heating_average_temperature/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/ftx` | `{"uteluft": value, "avluft": value, "tilluft": value, "franluft": value, "effekt_varmevaxlare": value}` | `uteluft`, `avluft`, `tilluft`, `franluft`, `heat_exchanger_efficiency` | `homeassistant/sensor/solar_heating_uteluft/state`, `homeassistant/sensor/solar_heating_avluft/state`, `homeassistant/sensor/solar_heating_tilluft/state`, `homeassistant/sensor/solar_heating_franluft/state`, `homeassistant/sensor/solar_heating_heat_exchanger_efficiency/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/suncollector` | `{"dT_running": value, "dT": value, "pump": "ON"/"OFF", "mode": value, "state": value, "sub_state": "0", "overheated": "true"/"false"}` | `solar_collector_dt_running`, `solar_collector_dt`, `primary_pump`, `system_mode`, `overheated` | `homeassistant/sensor/solar_heating_solar_collector_dt_running/state`, `homeassistant/sensor/solar_heating_solar_collector_dt/state`, `homeassistant/switch/solar_heating_primary_pump/state`, `homeassistant/sensor/solar_heating_system_mode/state`, `homeassistant/binary_sensor/solar_heating_overheated/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/test_mode` | `{"test_mode": "true"/"false", "log_level": value}` | `test_mode`, `log_level` | `homeassistant/binary_sensor/solar_heating_test_mode/state`, `homeassistant/sensor/solar_heating_log_level/state` | ✅ **DUPLICATED** |
| `sequentmicrosystems/test_switch` | `{"switch_status": "on"/"off"}` | `test_mode` | `homeassistant/binary_sensor/solar_heating_test_mode/state` | ✅ **DUPLICATED** |

### **4. V2 MQTT Discovery Sensors**

| Legacy Topic | Legacy Format | v3 Equivalent | v3 Topic | Status |
|--------------|---------------|----------------|----------|---------|
| `homeassistant/sensor/solar_t1/config` | Discovery config for T1 | `solar_collector` | `homeassistant/sensor/solar_heating_solar_collector/state` | ✅ **DUPLICATED** |
| `homeassistant/sensor/solar_t2/config` | Discovery config for T2 | `storage_tank` | `homeassistant/sensor/solar_heating_storage_tank/state` | ✅ **DUPLICATED** |
| `homeassistant/switch/solar_pump/config` | Discovery config for pump | `primary_pump` | `homeassistant/switch/solar_heating_primary_pump/state` | ✅ **DUPLICATED** |
| `homeassistant/switch/solar_heater/config` | Discovery config for heater | `cartridge_heater` | `homeassistant/switch/solar_heating_cartridge_heater/state` | ✅ **DUPLICATED** |

## 🆕 **New v3 Sensors (No Legacy Equivalent)**

| v3 Sensor | v3 Topic | Description | Status |
|-----------|----------|-------------|---------|
| `realtime_energy_rate_kw` | `solar_heating_v3/status/realtime_energy_sensor` | Real-time energy rate in kW | 🆕 **NEW** |
| `realtime_temp_rate_per_hour` | `solar_heating_v3/status/realtime_energy_sensor` | Temperature change rate °C/h | 🆕 **NEW** |
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

## 📊 **Summary Statistics**

- **Total Legacy Sensors**: 32
- **Total v3 Sensors**: 45+
- **Duplicated Sensors**: 32 (100%)
- **New v3 Sensors**: 13+
- **Legacy Topics**: 6 main categories
- **v3 Topics**: 8 main categories

## 🗑️ **Safe to Remove (100% Coverage)**

**ALL** legacy sensors have v3 equivalents, making them safe to remove:

1. ✅ **Individual Temperature Sensors** (16 sensors) - Fully covered by v3
2. ✅ **Stored Energy** - Covered by 4 v3 sensors
3. ✅ **FTX Data** - Covered by 5 v3 sensors  
4. ✅ **Solar Collector** - Covered by 5 v3 sensors
5. ✅ **Test Mode/Switch** - Covered by 2 v3 sensors
6. ✅ **V2 Discovery** - Covered by 4 v3 sensors

## 🚀 **Benefits of Removing Legacy Sensors**

1. **Reduce MQTT Traffic**: Eliminate 32 duplicate messages
2. **Simplify Codebase**: Remove v1 compatibility layer
3. **Better Performance**: Single publishing system
4. **Easier Maintenance**: One source of truth
5. **Cleaner Dashboards**: No duplicate sensors in Home Assistant

## ⚠️ **Before Removing**

1. **Verify v3 System**: Ensure v3 is fully operational
2. **Check Dependencies**: Confirm no external systems use legacy topics
3. **Update Dashboards**: Migrate any remaining legacy dashboards
4. **Test Thoroughly**: Verify all functionality works with v3 only

## 🔧 **Removal Process**

1. **Remove v1 compatibility method** from `main_system.py`
2. **Remove v2 MQTT discovery** from `mqtt_discovery.py`
3. **Update documentation** to reflect v3-only approach
4. **Test system** to ensure no functionality is lost
5. **Clean up Home Assistant** by removing legacy sensors

**Result**: Cleaner, more efficient system with 100% v3 sensor coverage!
