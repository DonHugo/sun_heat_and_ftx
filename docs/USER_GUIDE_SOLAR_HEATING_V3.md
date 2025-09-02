# User Guide: Solar Heating System v3

## 🎯 **How to Use the System**

This guide explains how to use your Solar Heating v3 system, from initial setup to daily operation and troubleshooting.

## 🚀 **Getting Started**

### **Quick Start (5 Minutes)**

1. **Navigate to the system directory**:
   ```bash
   cd python/v3
   ```

2. **Activate the virtual environment**:
   ```bash
   source venv/bin/activate
   ```

3. **Start the system**:
   ```bash
   python main_system.py
   ```

4. **Check the dashboard**: Open your Home Assistant dashboard to see live data

5. **Monitor the logs**: Watch the console output for system status

### **First-Time Setup (30 Minutes)**

1. **Copy configuration template**:
   ```bash
   cp ../../config/env.example .env
   ```

2. **Edit configuration**:
   ```bash
   nano .env
   ```

3. **Set your MQTT broker details**:
   ```bash
   SOLAR_MQTT_BROKER=192.168.1.100
   SOLAR_MQTT_USERNAME=your_username
   SOLAR_MQTT_PASSWORD=your_password
   ```

4. **Configure temperature thresholds**:
   ```bash
   SOLAR_SET_TEMP_TANK_1=70.0
   SOLAR_DTSTART_TANK_1=8.0
   SOLAR_DTSTOP_TANK_1=4.0
   ```

5. **Start the system**:
   ```bash
   python main_system.py
   ```

## 🎛️ **Daily Operation**

### **Monitoring Your System**

#### **Home Assistant Dashboard**

Your system automatically creates a comprehensive dashboard in Home Assistant:

- **Temperature Sensors**: Real-time temperature readings from all sensors
- **Pump Status**: Current pump operation state
- **System Status**: Overall system health and mode
- **Energy Metrics**: Energy consumption and efficiency data

#### **System Logs**

Monitor system operation through logs:

```bash
# View real-time logs
tail -f solar_heating_v3.log

# View recent logs
tail -n 100 solar_heating_v3.log

# Search for specific events
grep "PUMP STARTED" solar_heating_v3.log
grep "EMERGENCY" solar_heating_v3.log
```

#### **MQTT Topics**

Monitor system data directly via MQTT:

```bash
# Subscribe to all temperature data
mosquitto_sub -h your_broker -t "solar_heating_v3/temperature/#"

# Subscribe to pump status
mosquitto_sub -h your_broker -t "solar_heating_v3/status/pump/#"

# Subscribe to system alerts
mosquitto_sub -h your_broker -t "solar_heating_v3/alerts/#"
```

### **Manual Control**

#### **Via Home Assistant**

1. **Open your Home Assistant dashboard**
2. **Navigate to the Solar Heating section**
3. **Use the control switches**:
   - **Primary Pump**: Manually start/stop the main pump
   - **Cartridge Heater**: Manually control the backup heater
   - **System Mode**: Switch between automatic and manual modes

#### **Via MQTT Commands**

Send manual control commands via MQTT:

```bash
# Start primary pump
mosquitto_pub -h your_broker -t "control/pump" -m '{"action": "start", "pump_id": "primary", "reason": "manual_override"}'

# Stop primary pump
mosquitto_pub -h your_broker -t "control/pump" -m '{"action": "stop", "pump_id": "primary", "reason": "manual_override"}'

# Set system mode
mosquitto_pub -h your_broker -t "control/system" -m '{"action": "set_mode", "mode": "manual"}'
```

#### **Via API (if enabled)**

```bash
# Get system status
curl -X GET "http://localhost:8000/api/v1/status"

# Control pump
curl -X POST "http://localhost:8000/api/v1/control/pump" \
  -H "Content-Type: application/json" \
  -d '{"action": "start", "pump_id": "primary"}'
```

## 🔧 **Configuration and Customization**

### **Temperature Control Settings**

#### **Basic Temperature Configuration**

```bash
# Target tank temperature
SOLAR_SET_TEMP_TANK_1=70.0

# Start pump when temperature difference is this high
SOLAR_DTSTART_TANK_1=8.0

# Stop pump when temperature difference is this low
SOLAR_DTSTOP_TANK_1=4.0

# High temperature warning threshold
SOLAR_TEMPERATURE_THRESHOLD_HIGH=80.0

# Low temperature warning threshold
SOLAR_TEMPERATURE_THRESHOLD_LOW=20.0

# Boiling temperature (emergency shutdown)
SOLAR_TEMP_KOK=150.0
```

#### **Advanced Temperature Logic**

The system uses sophisticated temperature difference (dT) logic:

- **dT = Solar Collector Temperature - Tank Temperature**
- **Pump starts** when dT ≥ `dTStart_tank_1` AND tank < set temperature
- **Pump stops** when dT ≤ `dTStop_tank_1` OR tank ≥ set temperature
- **Emergency shutdown** when solar temperature > boiling temperature

#### **Temperature Update Frequency**

```bash
# How often to read sensors (seconds)
SOLAR_TEMPERATURE_UPDATE_INTERVAL=30
```

### **Hardware Configuration**

#### **Board Addresses**

```bash
# RTD temperature sensor board
SOLAR_RTD_BOARD_ADDRESS=0

# MegaBAS control board
SOLAR_MEGABAS_BOARD_ADDRESS=3

# Relay control board
SOLAR_RELAY_BOARD_ADDRESS=2
```

#### **Hardware Platform**

```bash
# Set your hardware platform
SOLAR_HARDWARE_PLATFORM=raspberry_pi_zero_2_w
```

### **MQTT Configuration**

#### **Broker Settings**

```bash
# MQTT broker address
SOLAR_MQTT_BROKER=192.168.1.100

# MQTT broker port
SOLAR_MQTT_PORT=1883

# MQTT username (if required)
SOLAR_MQTT_USERNAME=your_username

# MQTT password (if required)
SOLAR_MQTT_PASSWORD=your_password

# MQTT client ID
SOLAR_MQTT_CLIENT_ID=solar_heating_v3
```

#### **Home Assistant Integration**

```bash
# Enable Home Assistant integration
SOLAR_HASS_ENABLED=true

# Home Assistant discovery prefix
SOLAR_HASS_DISCOVERY_PREFIX=homeassistant
```

### **AI Integration Configuration**

#### **TaskMaster AI Setup**

```bash
# Enable TaskMaster AI
SOLAR_TASKMASTER_ENABLED=true

# Your TaskMaster AI API key
SOLAR_TASKMASTER_API_KEY=your_api_key_here

# TaskMaster AI base URL
SOLAR_TASKMASTER_BASE_URL=https://api.taskmaster.ai
```

## 🧪 **Testing and Simulation**

### **Simulation Mode**

Run the system without hardware for testing:

```bash
# Enable simulation mode
SOLAR_TEST_MODE=true python main_system.py
```

In simulation mode:
- Temperature sensors return simulated values
- Hardware control is simulated
- All system logic works normally
- Perfect for development and testing

### **Hardware Testing**

Test your hardware connections:

```bash
# Test hardware interface
python -c "
from hardware_interface import HardwareInterface
hw = HardwareInterface()
results = hw.test_hardware_connection()
print('Hardware test results:', results)
"
```

### **Individual Component Testing**

```bash
# Test RTD sensors
python -c "
from hardware_interface import HardwareInterface
hw = HardwareInterface()
for i in range(4):
    temp = hw.read_temperature(i)
    print(f'Sensor {i}: {temp}°C')
"

# Test relay control
python -c "
from hardware_interface import HardwareInterface
hw = HardwareInterface()
hw.set_relay_state(0, True)
print('Relay 0 turned ON')
import time
time.sleep(1)
hw.set_relay_state(0, False)
print('Relay 0 turned OFF')
"
```

## 📊 **Monitoring and Diagnostics**

### **System Health Monitoring**

#### **Check System Status**

```bash
# View system status
python -c "
from main_system import MainSystem
system = MainSystem()
status = system.get_system_status()
print('System Status:', status)
"
```

#### **Monitor Performance Metrics**

```bash
# Check temperature update frequency
grep "Temperature update" solar_heating_v3.log | tail -10

# Check pump operation
grep "Pump" solar_heating_v3.log | tail -10

# Check MQTT communication
grep "MQTT" solar_heating_v3.log | tail -10
```

### **Temperature Sensor Calibration**

#### **Calibration Process**

1. **Prepare reference thermometer**
2. **Place sensors in known temperature environment**
3. **Record actual vs. measured temperatures**
4. **Calculate offset and scale factors**
5. **Update configuration**

#### **Calibration Configuration**

```bash
# Sensor 0 (Solar Collector) calibration
SOLAR_RTD_CALIBRATION_0_OFFSET=0.5
SOLAR_RTD_CALIBRATION_0_SCALE=1.0

# Sensor 1 (Storage Tank) calibration
SOLAR_RTD_CALIBRATION_1_OFFSET=-0.2
SOLAR_RTD_CALIBRATION_1_SCALE=1.0
```

### **Energy Monitoring**

#### **Energy Calculations**

The system automatically calculates:

- **Heat Energy**: Energy transferred to water
- **Pump Energy**: Energy consumed by pumps
- **Efficiency**: Overall system efficiency
- **Cost Savings**: Estimated cost savings vs. electric heating

#### **Energy Dashboard**

View energy metrics in Home Assistant:
- Real-time energy consumption
- Daily/monthly energy summaries
- Efficiency trends
- Cost analysis

## 🚨 **Safety and Emergency Procedures**

### **Safety Features**

Your system includes multiple safety layers:

1. **Hardware Limits**: Physical temperature and current limits
2. **Software Monitoring**: Configurable temperature thresholds
3. **Emergency Systems**: Automatic shutdown at critical conditions
4. **Manual Override**: Manual control capability

### **Emergency Shutdown**

#### **Automatic Triggers**

- **Boiling Temperature**: Solar temperature > 150°C
- **Hardware Failure**: Communication or sensor failures
- **System Error**: Critical system errors

#### **Emergency Response**

When emergency shutdown is triggered:

1. **All pumps stop immediately**
2. **All heaters are disabled**
3. **Emergency status is published**
4. **System waits for manual reset**
5. **Logs record the emergency**

#### **Manual Reset After Emergency**

1. **Check system logs** for emergency cause
2. **Verify hardware** is safe and functional
3. **Reset emergency state**:
   ```bash
   # Restart the system
   sudo systemctl restart solar_heating_v3
   
   # Or restart manually
   python main_system.py
   ```

### **Safety Monitoring**

#### **Temperature Alerts**

- **High Temperature**: Warning when > 80°C
- **Low Temperature**: Warning when < 20°C
- **Boiling Temperature**: Emergency shutdown at > 150°C

#### **Hardware Health Monitoring**

- **Sensor Communication**: Continuous sensor health checking
- **Pump Operation**: Monitoring pump response and status
- **Board Communication**: Checking hardware board health

## 🔄 **Maintenance and Updates**

### **Regular Maintenance**

#### **Daily Checks**

- [ ] Check Home Assistant dashboard for system status
- [ ] Review system logs for any errors
- [ ] Verify temperature readings are reasonable
- [ ] Check pump operation status

#### **Weekly Checks**

- [ ] Review energy consumption data
- [ ] Check system efficiency trends
- [ ] Verify safety systems are functioning
- [ ] Clean any visible debris from sensors

#### **Monthly Checks**

- [ ] Review system performance metrics
- [ ] Check hardware connections
- [ ] Verify configuration settings
- [ ] Update system if needed

### **System Updates**

#### **Code Updates**

```bash
# Pull latest code
git pull origin main

# Restart the system
sudo systemctl restart solar_heating_v3
```

#### **Configuration Updates**

```bash
# Edit configuration
nano .env

# Restart to apply changes
sudo systemctl restart solar_heating_v3
```

### **Backup and Recovery**

#### **Configuration Backup**

```bash
# Backup configuration
cp .env .env.backup.$(date +%Y%m%d)

# Backup logs
cp solar_heating_v3.log solar_heating_v3.log.backup.$(date +%Y%m%d)
```

#### **System Recovery**

```bash
# Restore configuration
cp .env.backup.20240115 .env

# Restart system
sudo systemctl restart solar_heating_v3
```

## 🆘 **Troubleshooting**

### **Common Issues**

#### **System Won't Start**

1. **Check configuration**:
   ```bash
   python -c "from config import Config; Config()"
   ```

2. **Check dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Check hardware libraries**:
   ```bash
   python -c "import rtd; print('RTD library OK')"
   ```

#### **Temperature Readings Invalid**

1. **Check sensor connections**
2. **Verify board addresses**
3. **Test hardware interface**:
   ```bash
   python -c "
   from hardware_interface import HardwareInterface
   hw = HardwareInterface()
   print(hw.test_hardware_connection())
   "
   ```

#### **Pump Not Responding**

1. **Check relay wiring**
2. **Verify relay board address**
3. **Test relay manually**:
   ```bash
   python -c "
   from hardware_interface import HardwareInterface
   hw = HardwareInterface()
   hw.test_relay(0)
   "
   ```

#### **MQTT Connection Failed**

1. **Check broker address and credentials**
2. **Verify network connectivity**
3. **Check firewall settings**
4. **Test MQTT connection**:
   ```bash
   mosquitto_pub -h your_broker -t "test" -m "test"
   ```

### **Debug Mode**

Enable detailed logging for troubleshooting:

```bash
# Enable debug mode
SOLAR_DEBUG_MODE=true SOLAR_LOG_LEVEL=debug python main_system.py
```

### **Log Analysis**

#### **Error Patterns**

```bash
# Find all errors
grep "ERROR" solar_heating_v3.log

# Find warnings
grep "WARNING" solar_heating_v3.log

# Find critical events
grep "CRITICAL" solar_heating_v3.log
```

#### **Performance Issues**

```bash
# Check response times
grep "Response time" solar_heating_v3.log

# Check update frequency
grep "Temperature update" solar_heating_v3.log | tail -20
```

## 📱 **Mobile and Remote Access**

### **Home Assistant Mobile App**

1. **Install Home Assistant app** on your mobile device
2. **Connect to your Home Assistant instance**
3. **Access Solar Heating dashboard** from anywhere
4. **Receive notifications** for alerts and status changes

### **Remote Monitoring**

#### **MQTT Monitoring**

Monitor your system remotely via MQTT:

```bash
# Monitor from remote location
mosquitto_sub -h your_broker -t "solar_heating_v3/#" -u username -P password
```

#### **Web Dashboard**

Access your Home Assistant dashboard from any web browser:
- Navigate to `http://your-home-assistant-ip:8123`
- Log in with your credentials
- Access the Solar Heating dashboard

## 🔗 **Related Documentation**

- **[Requirements Document](REQUIREMENTS_SOLAR_HEATING_V3.md)** - What we built and why
- **[Design Document](DESIGN_SOLAR_HEATING_V3.md)** - How the system works
- **[Implementation Guide](IMPLEMENTATION_SOLAR_HEATING_V3.md)** - Technical implementation details
- **[System Overview](../SYSTEM_OVERVIEW.md)** - Complete system understanding
- **[Component Map](../COMPONENT_MAP.md)** - System component relationships

---

**This guide explains how to use your Solar Heating v3 system for daily operation, configuration, monitoring, and troubleshooting. For technical details, refer to the Design and Implementation documents.**
