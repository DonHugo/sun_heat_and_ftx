# Solar Heating System v3

Intelligent solar heating system with TaskMaster AI integration, Home Assistant support, and enhanced monitoring capabilities.

## 🚀 Features

- **Intelligent Temperature Monitoring**: Continuous monitoring with configurable thresholds
- **Home Assistant Integration**: Full MQTT-based integration for smart home control
- **TaskMaster AI Ready**: Framework for AI-powered optimization and task management
- **Hardware Abstraction**: Clean interface to Sequent Microsystems hardware
- **Real-time MQTT Communication**: Live status updates and remote control
- **Emergency Safety Systems**: Automatic shutdown for critical conditions
- **Simulation Mode**: Test system without hardware
- **Comprehensive Logging**: Detailed logging and monitoring

## 📋 Requirements

### Hardware
- Raspberry Pi Zero 2 W (or similar)
- Sequent Microsystems RTD Data Acquisition board
- Sequent Microsystems Building Automation V4 board
- Sequent Microsystems Four Relays four HV Inputs board
- Temperature sensors (RTD type)
- Water circulation pumps
- Storage tanks

### Software
- Python 3.8+
- MQTT broker (Mosquitto recommended)
- Home Assistant (optional)

## 🛠️ Installation

1. **Clone the repository**:
   ```bash
   cd python/v3
   ```

2. **Install dependencies**:
   ```bash
   # For production use
   pip install -r requirements.txt
   
   # For development and testing
   pip install -r requirements-dev.txt
   ```

3. **Install Sequent Microsystems libraries**:
   ```bash
   # RTD Data Acquisition
   git clone https://github.com/SequentMicrosystems/rtd-rpi.git
   cd rtd-rpi/python/rtd/
   sudo python3 setup.py install
   
   # Building Automation V4
   git clone https://github.com/SequentMicrosystems/megabas-rpi.git
   cd megabas-rpi/python/
   sudo python3 setup.py install
   
   # Four Relays four HV Inputs
   git clone https://github.com/SequentMicrosystems/4relind-rpi.git
   cd 4relind-rpi/python/4relind/
   sudo python3 setup.py install
   ```

4. **Configure environment**:
   ```bash
   cp ../../env.example .env
   # Edit .env with your settings
   ```

## ⚙️ Configuration

### Environment Variables

Create a `.env` file with the following variables:

```bash
# Hardware Configuration
SOLAR_HARDWARE_PLATFORM=raspberry_pi_zero_2_w
SOLAR_RTD_BOARD_ADDRESS=0
SOLAR_MEGABAS_BOARD_ADDRESS=3
SOLAR_RELAY_BOARD_ADDRESS=2

# Temperature Monitoring
SOLAR_TEMPERATURE_UPDATE_INTERVAL=30
SOLAR_TEMPERATURE_THRESHOLD_HIGH=80.0
SOLAR_TEMPERATURE_THRESHOLD_LOW=20.0

# Solar Collector Configuration
SOLAR_SET_TEMP_TANK_1=70.0
SOLAR_SET_TEMP_TANK_1_HYSTERES=2.0
SOLAR_DTSTART_TANK_1=8.0
SOLAR_DTSTOP_TANK_1=4.0
SOLAR_KYLNING_KOLLEKTOR=90.0
SOLAR_TEMP_KOK=150.0

# MQTT Configuration
SOLAR_MQTT_BROKER=192.168.0.110
SOLAR_MQTT_PORT=1883
SOLAR_MQTT_USERNAME=mqtt_beaches
SOLAR_MQTT_PASSWORD=uQX6NiZ.7R

# Home Assistant Integration
SOLAR_HASS_ENABLED=true
SOLAR_HASS_DISCOVERY_PREFIX=homeassistant

# TaskMaster AI Configuration
SOLAR_TASKMASTER_ENABLED=true
SOLAR_TASKMASTER_API_KEY=your_api_key_here

# System Operation
SOLAR_TEST_MODE=false
SOLAR_DEBUG_MODE=false
SOLAR_LOG_LEVEL=info
```

## 🏃‍♂️ Usage

### Basic Usage

1. **Start the system**:
   ```bash
   python main.py
   ```

2. **Run in test mode**:
   ```bash
   SOLAR_TEST_MODE=true python main.py
   ```

3. **Run with debug logging**:
   ```bash
   SOLAR_DEBUG_MODE=true python main.py
   ```

### Home Assistant Integration

The system automatically publishes MQTT topics for Home Assistant integration:

#### Temperature Sensors
- `temperature/solar_collector`
- `temperature/storage_tank`
- `temperature/return_line`
- `temperature/heat_exchanger`

#### Control Entities
- `control/pump` - Control primary pump
- `control/heater` - Control cartridge heater

#### Status Entities
- `status/system` - System status
- `status/pump` - Pump status
- `status/energy` - Energy calculations

### MQTT Topics

#### Published Topics
- `solar_heating_v3/temperature/*` - Temperature readings
- `solar_heating_v3/status/*` - System status
- `solar_heating_v3/control/*` - Control commands
- `homeassistant/*` - Home Assistant discovery

#### Subscribed Topics
- `hass/*/control` - Home Assistant control
- `hass/*/set` - Home Assistant state changes
- `control/*` - System control commands
- `taskmaster/*` - TaskMaster AI messages

## 🏗️ Architecture

### Core Components

1. **Hardware Interface** (`hardware_interface.py`)
   - Abstracts Sequent Microsystems hardware
   - Supports simulation mode for testing
   - Handles temperature reading and relay control

2. **MQTT Handler** (`mqtt_handler.py`)
   - Manages MQTT communication
   - Handles Home Assistant integration
   - Processes incoming commands and state changes

3. **Configuration** (`config.py`)
   - Centralized configuration management
   - Environment variable support
   - Hardware mapping and constants

4. **Main Controller** (`main.py`)
   - Orchestrates system operation
   - Implements control logic
   - Manages system state

### System Flow

1. **Initialization**: Load configuration, initialize hardware and MQTT
2. **Temperature Reading**: Read all sensors at configured intervals
3. **Control Logic**: Apply temperature-based control algorithms
4. **Status Publishing**: Publish system status to MQTT
5. **Command Processing**: Handle incoming MQTT commands
6. **Safety Monitoring**: Monitor for critical conditions

## 🔧 Control Logic

### Pump Control

The system uses sophisticated temperature-based logic for pump control:

- **Start Conditions**:
  - Temperature difference (dT) ≥ `dTStart_tank_1`
  - Storage tank temperature < `set_temp_tank_1`
  - Solar collector temperature ≥ `kylning_kollektor` (cooling mode)

- **Stop Conditions**:
  - Temperature difference (dT) ≤ `dTStop_tank_1`
  - Storage tank temperature ≥ `set_temp_tank_1`
  - Emergency conditions (boiling temperature)

### Safety Features

- **Emergency Shutdown**: Automatic shutdown at boiling temperature
- **Temperature Alerts**: High/low temperature warnings
- **Manual Override**: Manual control via Home Assistant
- **Hardware Monitoring**: Continuous hardware status checking

## 📊 Monitoring

### Log Files
- `solar_heating_v3.log` - Main system log
- Configurable log levels (DEBUG, INFO, WARNING, ERROR)

### MQTT Status
- Real-time system status via MQTT
- Temperature readings and energy calculations
- Pump and heater status
- System mode and alerts

### Home Assistant Dashboard
- Temperature graphs and history
- Pump and heater controls
- System status overview
- Energy consumption metrics

## 🧪 Testing

### Simulation Mode
Run the system without hardware for testing:

```bash
SOLAR_TEST_MODE=true python main.py
```

### Hardware Testing
Test hardware connections:

```python
from hardware_interface import HardwareInterface

hw = HardwareInterface()
test_results = hw.test_hardware_connection()
print(test_results)
```

## 🔌 Integration

### Home Assistant Configuration

Add to your `configuration.yaml`:

```yaml
mqtt:
  sensor:
    - name: "Solar Collector Temperature"
      state_topic: "solar_heating_v3/temperature/solar_collector"
      value_template: "{{ value_json.temperature }}"
      unit_of_measurement: "°C"
    
    - name: "Storage Tank Temperature"
      state_topic: "solar_heating_v3/temperature/storage_tank"
      value_template: "{{ value_json.temperature }}"
      unit_of_measurement: "°C"

  switch:
    - name: "Primary Pump"
      state_topic: "solar_heating_v3/status/pump/primary"
      command_topic: "solar_heating_v3/control/pump"
      value_template: "{{ value_json.status }}"
      payload_on: '{"pump_id": "primary", "action": "on"}'
      payload_off: '{"pump_id": "primary", "action": "off"}'
```

### TaskMaster AI Integration

The system is designed for TaskMaster AI integration:

```python
# Example TaskMaster AI integration
from taskmaster_integration import TaskMasterAI

taskmaster = TaskMasterAI()
await taskmaster.create_task("temperature_monitoring", {
    "sensor": "solar_collector",
    "temperature": 85.5,
    "threshold": 80.0
})
```

## 🚨 Troubleshooting

### Common Issues

1. **MQTT Connection Failed**
   - Check broker address and credentials
   - Verify network connectivity
   - Check firewall settings

2. **Hardware Not Detected**
   - Verify Sequent Microsystems libraries installed
   - Check board addresses in configuration
   - Run hardware test: `python -c "from hardware_interface import HardwareInterface; print(HardwareInterface().test_hardware_connection())"`

3. **Temperature Readings Invalid**
   - Check sensor wiring
   - Verify sensor calibration
   - Check board connections

4. **Pump Not Responding**
   - Check relay wiring
   - Verify relay board address
   - Test relay manually

### Debug Mode

Enable debug logging for detailed troubleshooting:

```bash
SOLAR_DEBUG_MODE=true SOLAR_LOG_LEVEL=debug python main.py
```

## 📈 Performance

### System Requirements
- **CPU**: Minimal (Raspberry Pi Zero 2 W sufficient)
- **Memory**: 512MB RAM minimum
- **Storage**: 1GB free space
- **Network**: Stable MQTT connection

### Performance Metrics
- **Temperature Update Rate**: Configurable (default: 30 seconds)
- **MQTT Latency**: < 1 second
- **Control Response Time**: < 5 seconds
- **System Uptime**: > 99.9%

## 🔄 Updates

### Version History
- **v3.0.0**: Initial release with Home Assistant integration
- Based on v2 system with enhanced architecture
- Added TaskMaster AI framework
- Improved MQTT handling and safety features

### Future Enhancements
- TaskMaster AI integration
- Advanced energy optimization
- Predictive maintenance
- Cloud data analytics
- Mobile application

## 📄 License

This project is part of the Solar Heating System and follows the same licensing terms.

## 🤝 Support

For support and questions:
1. Check the troubleshooting section
2. Review system logs
3. Test in simulation mode
4. Verify configuration settings

## 🔗 Related Documentation

- [PRD Document](../prd.txt) - Product Requirements Document
- [TaskMaster AI Integration](../../README_TASKMASTER.md) - AI integration guide
- [Hardware Setup](../../README.md) - Hardware installation guide
