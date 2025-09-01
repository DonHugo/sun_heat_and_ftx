# Pellet Stove Data Verification Guide

This guide helps you verify that Home Assistant is providing pellet stove data to your solar heating system.

## 🔍 Verification Methods

### Method 1: Test Script (Recommended)
Run the dedicated test script to check data reception:

```bash
cd python/v3
python test_pellet_stove_data.py
```

**Expected Output:**
- ✅ Connected to MQTT broker successfully!
- 📡 Subscribed to pellet stove topics
- ⏳ Waiting for pellet stove data...
- 🎉 Success! Received X data points

### Method 2: MQTT Topic Monitor
Monitor all MQTT topics to see what Home Assistant is publishing:

```bash
cd python/v3
python mqtt_topic_monitor.py
```

**Expected Output:**
- 🔥 PELLET STOVE DATA:
- Topic: homeassistant/sensor/pelletskamin_power/state
- Payload: 3.0

### Method 3: Check System Logs
Run your main system and check for pellet stove data logs:

```bash
cd python/v3
python main_system.py
```

Look for these log messages:
- "Handling pellet stove data: homeassistant/sensor/pelletskamin_power/state = 3.0"
- "Updated pellet stove data: pellet_stove_power = 3.0"

## 🔧 Troubleshooting

### If No Data is Received:

1. **Check Pellet Stove Status**
   - Ensure your pellet stove is active and running
   - Verify it's connected to Home Assistant

2. **Check Home Assistant MQTT Integration**
   - Go to Home Assistant → Settings → Devices & Services
   - Verify MQTT integration is active
   - Check if pellet stove sensors are visible

3. **Check MQTT Topics**
   - Use the topic monitor to see what's being published
   - Verify topic names match our expectations

4. **Check Network Connectivity**
   - Ensure your system can reach the MQTT broker
   - Verify MQTT credentials are correct

### Expected MQTT Topics:
Based on your pellet stove information, we expect these topics:

```
homeassistant/sensor/pelletskamin_power/state
homeassistant/sensor/pelletskamin_brinntid/state
homeassistant/sensor/pelletskamin_dagens_förbrukning/state
homeassistant/sensor/pelletskamin_storage_level/state
homeassistant/sensor/pelletskamin_storage_percentage/state
homeassistant/sensor/pelletskamin_storage_energy/state
homeassistant/sensor/pelletskamin_storage_weight/state
homeassistant/sensor/pelletskamin_electric_consumption/state
homeassistant/sensor/pelletskamin_bags_until_cleaning/state
homeassistant/binary_sensor/pelletskamin_status/state
```

## 📊 Data Mapping

When data is received, it's mapped to these system variables:

| Home Assistant Sensor | System Variable | Example Value |
|----------------------|-----------------|---------------|
| pelletskamin_power | pellet_stove_power | 3.0 kW |
| pelletskamin_brinntid | pellet_stove_burn_time | 0.11 h |
| pelletskamin_dagens_förbrukning | pellet_stove_daily_consumption | 0.56% |
| pelletskamin_storage_level | pellet_stove_storage_level | 21 |
| pelletskamin_storage_percentage | pellet_stove_storage_percentage | 5.9% |
| pelletskamin_storage_energy | pellet_stove_storage_energy | 4.7 kWh |
| pelletskamin_storage_weight | pellet_stove_storage_weight | 0.94 kg |
| pelletskamin_electric_consumption | pellet_stove_electric_consumption | 12 W |
| pelletskamin_bags_until_cleaning | pellet_stove_bags_until_cleaning | 10 |
| pelletskamin_status | pellet_stove_status | true/false |

## ✅ Success Indicators

Your integration is working when you see:

1. **Test Script Success:**
   ```
   🎉 Success! Received X data points
   ✅ Home Assistant integration is working!
   ```

2. **System Logs:**
   ```
   INFO: Updated pellet stove data: pellet_stove_power = 3.0
   ```

3. **Real-time Data:**
   - Values update when pellet stove status changes
   - Data flows continuously while pellet stove is active

## 🚀 Next Steps

Once verification is successful:
1. Your system has real-time pellet stove data
2. Ready for AI optimization implementation
3. Can make intelligent heat source decisions
4. Ready for TaskMaster AI integration
