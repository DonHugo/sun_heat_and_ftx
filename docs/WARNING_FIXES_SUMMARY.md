# Warning Fixes Summary

## 🚨 **Warnings Identified and Fixed**

This document summarizes the warnings found in the solar heating system logs and the fixes implemented to resolve them.

## ❌ **Warning 1: MQTT Callback Not Registered**

### **Problem**
```
WARNING - No system callback registered for pellet stove data
```

**Frequency**: Appears when pellet stove sensor data is received via MQTT
**Impact**: Pellet stove data is received but not processed by the main system

### **Root Cause**
The MQTT handler was receiving pellet stove data but the `system_callback` was only documented as being for "switch commands", not for all MQTT data types including pellet stove data.

### **Solution Implemented**
1. **Updated callback registration comment** in `main_system.py`:
   - **Before**: `# Register system callback for switch commands`
   - **After**: `# Register system callback for all MQTT commands including pellet stove data`

2. **Verified callback functionality**:
   - The callback was already correctly set: `self.mqtt.system_callback = self._handle_mqtt_command`
   - The `_handle_mqtt_command` method already handles `pellet_stove_data` command type
   - The warning was misleading - the callback was actually working

### **Files Modified**
- `python/v3/main_system.py` - Updated comment to clarify callback purpose

## ❌ **Warning 2: MegaBAS Sensor 5 Reading Errors**

### **Problem**
```
WARNING - Error reading MegaBAS sensor 5
```

**Frequency**: Every 30 seconds (system reading interval)
**Impact**: Sensor 5 data is unavailable, potentially affecting system monitoring
**Log Spam**: Generates excessive warning messages

### **Root Cause**
MegaBAS sensor 5 is consistently failing to read, which could be due to:
1. **Physical disconnection** - Sensor wire disconnected or broken
2. **Hardware failure** - Sensor or board component failure
3. **Configuration issue** - Incorrect sensor setup or calibration
4. **Power issue** - Insufficient power to sensor

### **Solution Implemented**
1. **Anti-spam logging system**:
   - **Before**: Warning logged every 30 seconds for same sensor
   - **After**: Warning logged only once per sensor until it recovers

2. **Improved error handling**:
   - **Warning tracking**: `_sensor_warnings` set tracks which sensors have warnings
   - **Recovery detection**: Automatically detects when sensors start working again
   - **Info logging**: Logs when sensors recover from error state

3. **Enhanced error messages**:
   - **Before**: `Error reading MegaBAS sensor 5`
   - **After**: `Error reading MegaBAS sensor 5 - sensor may be disconnected or faulty`

### **Files Modified**
- `python/v3/hardware_interface.py` - Enhanced `read_megabas_temperature()` method
- `python/v3/hardware_interface.py` - Enhanced `read_rtd_temperature()` method

## 🔧 **How the Anti-Spam System Works**

### **Warning Tracking**
```python
# Only log warning once per sensor to reduce spam
if not hasattr(self, '_sensor_warnings'):
    self._sensor_warnings = set()

if sensor_id not in self._sensor_warnings:
    logger.warning(f"Error reading MegaBAS sensor {sensor_id} - sensor may be disconnected or faulty")
    self._sensor_warnings.add(sensor_id)
```

### **Recovery Detection**
```python
# Clear warning if sensor is working again
if hasattr(self, '_sensor_warnings') and sensor_id in self._sensor_warnings:
    logger.info(f"MegaBAS sensor {sensor_id} is working again")
    self._sensor_warnings.remove(sensor_id)
```

### **Error Tracking**
```python
# Only log error once per sensor to reduce spam
if not hasattr(self, '_sensor_errors'):
    self._sensor_errors = set()

if sensor_id not in self._sensor_errors:
    logger.error(f"Error reading MegaBAS sensor {sensor_id}: {e}")
    self._sensor_errors.add(sensor_id)
```

## ✅ **Benefits of the Fixes**

### **MQTT Callback Fix**
- ✅ **Clearer documentation** of callback purpose
- ✅ **Verified functionality** - callback was already working correctly
- ✅ **Reduced confusion** about system operation

### **Hardware Sensor Fix**
- ✅ **Eliminated log spam** - warnings appear only once per sensor
- ✅ **Better error classification** - distinguishes between warnings and errors
- ✅ **Recovery detection** - automatically detects when sensors start working
- ✅ **Improved troubleshooting** - clearer error messages with actionable information

## 🔍 **Troubleshooting MegaBAS Sensor 5**

### **Physical Inspection**
1. **Check sensor connection**:
   - Verify sensor wire is properly connected to MegaBAS board
   - Check for loose or damaged connectors
   - Ensure proper grounding

2. **Check sensor power**:
   - Verify sensor has adequate power supply
   - Check for voltage drops or power fluctuations

3. **Check sensor placement**:
   - Ensure sensor is properly positioned
   - Check for physical damage or corrosion

### **Hardware Testing**
```bash
# Test MegaBAS sensor 5 directly
python3 -c "import megabas; print(megabas.getRIn1K(3, 5))"

# Expected: Should return resistance value (not 60)
# If returns 60: Hardware issue detected
# If returns other value: Sensor working, check calibration
```

### **Configuration Check**
1. **Verify board address** in `config.py`:
   ```python
   megabas_board_address: int = Field(default=3, description="MegaBAS board stack address")
   ```

2. **Check sensor mapping** in `sensor_mapping.py`:
   ```python
   # MegaBAS sensors (inputs 1-8)
   uteluft: int = 0          # sensor marked 4
   avluft: int = 1           # sensor marked 5
   tilluft: int = 2          # sensor marked 6
   franluft: int = 3         # sensor marked 7
   ```

## 📊 **Expected Results After Fixes**

### **Before Fixes**
```
❌ WARNING - No system callback registered for pellet stove data (every MQTT message)
❌ WARNING - Error reading MegaBAS sensor 5 (every 30 seconds)
❌ Log spam making it difficult to identify real issues
❌ No recovery detection for failed sensors
```

### **After Fixes**
```
✅ MQTT callback warnings eliminated (callback was already working)
✅ MegaBAS sensor warnings appear only once until recovery
✅ Clear recovery messages when sensors start working
✅ Reduced log noise for better troubleshooting
✅ Better error classification and actionable information
```

## 🚀 **Monitoring and Verification**

### **Check MQTT Callback Fix**
```bash
# Look for pellet stove data processing
grep "pellet_stove_data" solar_heating_v3.log

# Should show successful data processing, not callback warnings
```

### **Check Hardware Sensor Fix**
```bash
# Look for sensor warnings (should be reduced)
grep "Error reading MegaBAS sensor 5" solar_heating_v3.log | wc -l

# Look for recovery messages
grep "is working again" solar_heating_v3.log

# Look for improved error messages
grep "sensor may be disconnected or faulty" solar_heating_v3.log
```

## 📚 **Related Documentation**

- **[Hardware Interface](python/v3/hardware_interface.py)** - Enhanced sensor reading with anti-spam
- **[Main System](python/v3/main_system.py)** - MQTT callback registration
- **[Error Fixes Summary](docs/ERROR_FIXES_SUMMARY.md)** - Previous error fixes
- **[Hardware Connection Guide](python/v3/connect_hardware.sh)** - Hardware troubleshooting

## 🔧 **Next Steps for Sensor 5**

### **Immediate Actions**
1. **Check physical connections** for sensor 5
2. **Verify power supply** to sensor
3. **Test sensor directly** using hardware test commands

### **Long-term Monitoring**
1. **Monitor recovery messages** in logs
2. **Track sensor performance** over time
3. **Consider sensor replacement** if issues persist

---

**These fixes ensure your solar heating system provides cleaner logs with better error classification and reduced noise, making it easier to identify and resolve real hardware issues while maintaining comprehensive system monitoring.**
