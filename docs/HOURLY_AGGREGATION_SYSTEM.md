# Hourly Aggregation System for Solar Heating v3

## 🎯 **System Overview**

The Solar Heating System v3 now implements an **intelligent hourly aggregation system** that collects energy and sensor data throughout each hour and publishes the complete hour's data at the end of the hour. This provides more accurate, efficient, and meaningful data representation.

## 🔄 **How It Works**

### **During Each Hour (0:00-59:59)**
- **Data Collection**: System continuously collects energy and sensor data
- **Local Storage**: Data is stored locally but NOT published to MQTT
- **Basic Status**: Only basic system status (temperatures, switches, etc.) is published
- **Update Frequency**: Basic status published every 5 minutes during the hour

### **At End of Hour (Last 10 seconds)**
- **Complete Aggregation**: All hourly energy data is published
- **Full Sensor Data**: Complete sensor dataset including hourly energy totals
- **Hourly Summary**: Detailed logging of the complete hour's energy collection
- **Data Reset**: Hourly counters reset for the next hour

## 📊 **Data Flow Timeline**

```
Hour 1: 00:00 - 00:59
├─ 00:00-00:04: Basic status published (no hourly energy)
├─ 00:05-00:09: Basic status published (no hourly energy)
├─ 00:10-00:14: Basic status published (no hourly energy)
├─ ... (every 5 minutes)
├─ 00:55-00:59: Basic status published (no hourly energy)
└─ 00:59:50-00:59:59: 🕐 COMPLETE HOURLY AGGREGATION PUBLISHED

Hour 2: 01:00 - 01:59
├─ 01:00-01:04: Basic status published (no hourly energy)
├─ 01:05-01:09: Basic status published (no hourly energy)
├─ ... (every 5 minutes)
└─ 01:59:50-01:59:59: 🕐 COMPLETE HOURLY AGGREGATION PUBLISHED
```

## 🔧 **Technical Implementation**

### **1. Status Publishing Loop**
```python
async def _status_publishing_loop(self):
    """Status publishing loop with hourly aggregation"""
    while self.running:
        current_time = time.time()
        current_hour = int(current_time // 3600)
        
        # Check if we're at the end of an hour (last 10 seconds)
        seconds_into_hour = current_time % 3600
        is_end_of_hour = seconds_into_hour >= 3590  # Last 10 seconds
        
        if is_end_of_hour:
            # End of hour - publish aggregated hourly data
            await self._publish_hourly_aggregation()
            logger.info(f"🕐 End of hour {current_hour} - published hourly aggregation")
            await asyncio.sleep(10)  # Wait for hour boundary
        else:
            # During the hour - just publish basic status
            await self._publish_basic_status()
            
            # Calculate time until next hour
            time_until_next_hour = 3600 - seconds_into_hour
            sleep_time = min(300, time_until_next_hour - 10)  # 5 minutes or until end of hour
            await asyncio.sleep(sleep_time)
```

### **2. Hourly Aggregation Method**
```python
async def _publish_hourly_aggregation(self):
    """Publish complete hourly energy aggregation at end of hour"""
    # Publishes ALL sensors including hourly energy data
    # Includes detailed hourly energy summary logging
    # Marks data as hourly aggregation for downstream processing
```

### **3. Basic Status Method**
```python
async def _publish_basic_status(self):
    """Publish basic system status (no hourly energy data)"""
    # Skips hourly energy sensors during the hour
    # Publishes temperatures, switches, numbers, etc.
    # Updates every 5 minutes during the hour
```

## 📈 **Energy Data Handling**

### **Hourly Energy Sensors**
- `energy_collected_hour_kwh` - Total energy collected this hour
- `solar_energy_hour_kwh` - Solar energy collected this hour
- `cartridge_energy_hour_kwh` - Cartridge heater energy this hour
- `pellet_energy_hour_kwh` - Pellet stove energy this hour

### **Data Collection During Hour**
```python
# Energy is continuously collected and added to hourly totals
self.system_state['energy_collected_hour'] += hourly_contribution
self.system_state['solar_energy_hour'] += source_contribution
self.system_state['cartridge_energy_hour'] += source_contribution
self.system_state['pellet_energy_hour'] += source_contribution
```

### **Data Publishing at End of Hour**
```python
# Complete hour's data is published with detailed logging
logger.info("🕐 Hourly Energy Summary:")
logger.info(f"  📊 Total Energy: {energy_collected_hour_kwh:.3f} kWh")
logger.info(f"  ☀️  Solar Energy: {solar_energy_hour_kwh:.3f} kWh")
logger.info(f"  🔥 Cartridge Energy: {cartridge_energy_hour_kwh:.3f} kWh")
logger.info(f"  🌲 Pellet Energy: {pellet_energy_hour_kwh:.3f} kWh")
```

## 🕐 **Timing and Synchronization**

### **Hour Boundary Detection**
- **Precision**: Detects end of hour within last 10 seconds
- **Synchronization**: Waits for exact hour boundary before proceeding
- **Reliability**: Handles system delays and processing time

### **Update Frequencies**
- **Basic Status**: Every 5 minutes during the hour
- **Hourly Aggregation**: Once per hour at end of hour
- **Real-time Data**: Continuously collected but not published

### **Time Calculation**
```python
current_time = time.time()
current_hour = int(current_time // 3600)  # Current hour since epoch
seconds_into_hour = current_time % 3600   # Seconds into current hour
is_end_of_hour = seconds_into_hour >= 3590  # Last 10 seconds
```

## 📡 **MQTT Publishing Strategy**

### **During Hour (Basic Status)**
```
Topic: homeassistant/sensor/solar_heating_temperature/state
Data: 25.6 (temperature value)

Topic: homeassistant/sensor/solar_heating_system_mode/state  
Data: heating (system status)

Topic: homeassistant/sensor/solar_heating_primary_pump/state
Data: ON (pump status)

# Note: Hourly energy sensors are NOT published during the hour
```

### **End of Hour (Complete Aggregation)**
```
Topic: homeassistant/sensor/solar_heating_temperature/state
Data: 25.6 (temperature value)

Topic: homeassistant/sensor/solar_heating_energy_collected_hour_kwh/state
Data: 2.847 (complete hour's energy collection)

Topic: homeassistant/sensor/solar_heating_solar_energy_hour_kwh/state
Data: 1.923 (complete hour's solar energy)

Topic: homeassistant/sensor/solar_heating_cartridge_energy_hour_kwh/state
Data: 0.924 (complete hour's cartridge energy)

Topic: homeassistant/sensor/solar_heating_pellet_energy_hour_kwh/state
Data: 0.000 (complete hour's pellet energy)
```

## 🎯 **Benefits of Hourly Aggregation**

### **1. Data Accuracy**
- **Complete Hour Data**: Represents full hour's collection, not partial updates
- **No Interpolation**: Real collected data, not estimated values
- **Consistent Timing**: Data always represents complete hour periods

### **2. Efficiency**
- **Reduced MQTT Traffic**: Hourly energy data sent once per hour instead of every minute
- **Lower Network Load**: Fewer messages during normal operation
- **Better Performance**: Less frequent heavy data publishing

### **3. Data Quality**
- **Meaningful Values**: Each data point represents a complete hour
- **Historical Analysis**: Better for trend analysis and reporting
- **Dashboard Accuracy**: Home Assistant displays accurate hourly totals

### **4. System Monitoring**
- **Clear Hourly Boundaries**: Easy to identify when hours start/end
- **Detailed Logging**: Comprehensive hourly summaries for troubleshooting
- **Performance Tracking**: Better understanding of hourly system performance

## 🔍 **Monitoring and Verification**

### **Log Messages to Look For**
```
🕐 End of hour 123456 - published hourly aggregation
🕐 Publishing hourly energy aggregation...
🕐 Published hourly energy sensor: energy_collected_hour_kwh = 2.847 kWh (complete hour)
🕐 Hourly Energy Summary:
  📊 Total Energy: 2.847 kWh
  ☀️  Solar Energy: 1.923 kWh
  🔥 Cartridge Energy: 0.924 kWh
  🌲 Pellet Energy: 0.000 kWh
```

### **MQTT Topic Verification**
```bash
# Check that hourly energy is published at end of hour
mosquitto_sub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "homeassistant/sensor/solar_heating_energy_collected_hour_kwh/state"

# Should show data every hour, not every minute
```

### **Home Assistant Integration**
- **Sensor Updates**: Hourly energy sensors update once per hour
- **History Graph**: Shows complete hour's data, not partial updates
- **Automation**: Can trigger actions based on complete hourly data

## ⚙️ **Configuration and Customization**

### **Timing Adjustments**
```python
# Adjust end-of-hour detection window (currently 10 seconds)
is_end_of_hour = seconds_into_hour >= 3590  # Last 10 seconds

# Adjust basic status frequency (currently 5 minutes)
sleep_time = min(300, time_until_next_hour - 10)  # 5 minutes
```

### **Sensor Selection**
```python
# Add/remove sensors from hourly aggregation
hourly_energy_sensors = [
    'energy_collected_hour_kwh',
    'solar_energy_hour_kwh', 
    'cartridge_energy_hour_kwh',
    'pellet_energy_hour_kwh'
]
```

### **Logging Levels**
```python
# Adjust logging verbosity for hourly aggregation
logger.info("🕐 Publishing hourly energy aggregation...")  # Info level
logger.debug("Hourly aggregation details...")              # Debug level
```

## 🚀 **Implementation Timeline**

### **Phase 1: Core System (Complete)**
- ✅ **Hourly aggregation logic** implemented
- ✅ **End-of-hour detection** working
- ✅ **Basic status publishing** during hour
- ✅ **Complete aggregation** at end of hour

### **Phase 2: Enhanced Features (Future)**
- 🔄 **Customizable timing** for different sensor types
- 🔄 **Advanced aggregation** (min/max/avg during hour)
- 🔄 **Historical data** storage and retrieval
- 🔄 **Performance optimization** for large datasets

## 🔧 **Troubleshooting**

### **Common Issues**

#### **1. Hourly Data Not Publishing**
- **Check**: End-of-hour detection timing
- **Verify**: System clock synchronization
- **Debug**: Look for "🕐 End of hour" log messages

#### **2. Data Missing During Hour**
- **Check**: Basic status publishing frequency
- **Verify**: MQTT connection status
- **Debug**: Look for "Published basic system status" messages

#### **3. Incomplete Hourly Data**
- **Check**: Sensor data collection during hour
- **Verify**: Energy calculation logic
- **Debug**: Look for hourly energy summary logs

### **Debug Commands**
```bash
# Monitor logs for hourly aggregation
tail -f /home/pi/solar_heating/logs/solar_heating_v3.log | grep "🕐"

# Check MQTT publishing frequency
grep "Published.*energy.*hour" solar_heating_v3.log | tail -20

# Verify timing accuracy
grep "End of hour" solar_heating_v3.log | tail -10
```

## 📚 **Related Documentation**

- **`COMPREHENSIVE_ERROR_FIXES.md`** - All system error fixes
- **`WARNING_REDUCTION_SUMMARY.md`** - MQTT warning elimination
- **`IMPLEMENTATION_SOLAR_HEATING_V3.md`** - Core system implementation
- **`USER_GUIDE_SOLAR_HEATING_V3.md`** - User operation guide

---

**The hourly aggregation system transforms your solar heating system from real-time data updates to meaningful hourly data collection, providing more accurate and efficient monitoring while maintaining real-time system status updates.**

**This system ensures that your "Energy Collected This Hour" sensor shows complete, accurate data representing the full hour's collection rather than partial updates throughout the hour.**
