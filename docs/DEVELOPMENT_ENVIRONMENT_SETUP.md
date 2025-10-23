# Development Environment Setup Guide

## 🏗️ **System Architecture Overview**

This document describes the complete development environment setup for the Solar Heating System project, including local development, Raspberry Pi deployment, and Home Assistant integration.

## 📋 **Environment Components**

### **1. Local Development Environment (Mac/Linux)**
- **Location**: `/Users/hafs/Documents/Github/sun_heat_and_ftx/`
- **Purpose**: Code development, testing, and documentation
- **Capabilities**: 
  - ✅ Code editing and version control
  - ✅ Python script development
  - ✅ Test execution (limited - no hardware access)
  - ✅ Documentation creation
  - ❌ Hardware interface testing
  - ❌ Systemd service management
  - ❌ MQTT broker access
  - ❌ Real sensor data

### **2. Raspberry Pi Production Environment**
- **Location**: Remote Raspberry Pi (IP: 192.168.0.110)
- **Purpose**: Hardware interface, sensor data, and service execution
- **Capabilities**:
  - ✅ Hardware interface (RTD, MegaBAS, Relay boards)
  - ✅ Temperature sensor reading
  - ✅ Pump and heater control
  - ✅ Systemd service management
  - ✅ MQTT message publishing
  - ✅ Real-time data processing
  - ✅ Service monitoring and recovery

### **3. Home Assistant Server**
- **Location**: Separate server (different from Raspberry Pi)
- **Purpose**: Smart home integration and dashboard
- **Capabilities**:
  - ✅ MQTT broker (built-in)
  - ✅ Sensor data visualization
  - ✅ Dashboard and controls
  - ✅ Automation and alerts
  - ✅ Historical data storage

## 🔧 **Local Development Environment Setup**

### **Prerequisites**
```bash
# Python 3.8+ required
python3 --version

# Git for version control
git --version

# Text editor (VS Code, Vim, etc.)
code --version
```

### **Project Structure**
```
/Users/hafs/Documents/Github/sun_heat_and_ftx/
├── python/v3/                    # Main application code
│   ├── main_system.py            # Core system controller
│   ├── watchdog.py               # Service monitoring
│   ├── hardware_interface.py     # Hardware abstraction
│   ├── mqtt_handler.py           # MQTT communication
│   └── test_*.py                 # Test suites
├── docs/                         # Documentation
├── config/                       # Configuration files
└── README.md                     # Project overview
```

### **Local Development Capabilities**

#### **✅ What Can Be Done Locally:**
- Code development and editing
- Python script testing (without hardware)
- Documentation creation and updates
- Git version control
- Test suite execution (limited scope)
- Configuration file management
- Service file creation and editing

#### **❌ What Cannot Be Done Locally:**
- Hardware interface testing
- Real sensor data reading
- Systemd service management
- MQTT broker connectivity
- Pump and heater control
- Service monitoring and recovery
- Real-time data processing

### **Local Testing Limitations**
```python
# Example: Local test limitations
def test_hardware_interface():
    """This test will fail locally - no hardware access"""
    # ❌ Cannot access RTD boards
    # ❌ Cannot read temperature sensors
    # ❌ Cannot control pumps/heaters
    # ✅ Can test logic and data structures
    # ✅ Can test configuration parsing
    # ✅ Can test MQTT message formatting
```

## 🍓 **Raspberry Pi Environment Setup**

### **System Information**
- **OS**: Raspberry Pi OS (Linux)
- **Architecture**: ARM64
- **Python**: 3.11+ (system Python)
- **Services**: systemd managed
- **Network**: 192.168.0.110

### **Service Architecture**
```bash
# Main services running on Raspberry Pi
solar_heating_v3.service          # Main system controller
solar_heating_watchdog.service    # Service monitoring
mosquitto.service                 # MQTT broker (if installed)
```

### **File Locations**
```bash
# Service files
/etc/systemd/system/solar_heating_v3.service
/etc/systemd/system/solar_heating_watchdog.service

# Application code
/home/pi/solar_heating/python/v3/
/opt/solar_heating_v3/bin/python3

# Logs
/var/log/solar_heating_v3.log
/var/log/solar_heating_watchdog.log
/var/log/mosquitto/mosquitto.log

# Configuration
/home/pi/solar_heating/python/v3/config.py
```

### **Remote Access Procedures**

#### **For AI Assistant (Claude):**
- **Cannot directly access**: Raspberry Pi system
- **Requires user execution**: All commands must be run by user
- **Communication method**: User provides command output
- **Troubleshooting**: User runs diagnostic commands

#### **For User:**
```bash
# SSH access to Raspberry Pi
ssh pi@192.168.0.110

# Service management
sudo systemctl status solar_heating_v3.service
sudo systemctl restart solar_heating_v3.service
sudo journalctl -u solar_heating_v3.service --since "1 hour ago"

# MQTT testing
mosquitto_sub -h 192.168.0.110 -t "solar_heating_v3/+/+" -C 5
mosquitto_pub -h 192.168.0.110 -t "test/topic" -m "test message"

# Hardware testing
python3 /home/pi/solar_heating/python/v3/hardware_interface.py
```

## 🏠 **Home Assistant Environment Setup**

### **System Information**
- **Location**: Separate server (not on Raspberry Pi)
- **MQTT Broker**: Built-in (Mosquitto)
- **Integration**: MQTT-based sensor discovery
- **Dashboard**: Web-based interface

### **MQTT Configuration**
```yaml
# Home Assistant MQTT configuration
mqtt:
  broker: 192.168.0.110  # Raspberry Pi IP
  port: 1883
  username: mqtt_beaches
  password: uQX6NiZ.7R
  discovery: true
```

### **Sensor Topics**
```bash
# Temperature sensors
solar_heating_v3/temperature/solar_collector
solar_heating_v3/temperature/storage_tank
solar_heating_v3/temperature/heat_exchanger_in
solar_heating_v3/temperature/heat_exchanger_out

# System status
solar_heating_v3/heartbeat
solar_heating_v3/status
solar_heating_v3/control
```

## 🔄 **Development Workflow**

### **1. Local Development**
```bash
# Edit code locally
code python/v3/main_system.py

# Run tests locally (limited scope)
python3 python/v3/test_solution_validation.py

# Commit changes
git add .
git commit -m "Fix service monitoring issue"
git push
```

### **2. Raspberry Pi Deployment**
```bash
# SSH to Raspberry Pi
ssh pi@192.168.0.110

# Pull latest changes
cd /home/pi/solar_heating
git pull

# Restart services
sudo systemctl restart solar_heating_v3.service
sudo systemctl restart solar_heating_watchdog.service

# Check status
sudo systemctl status solar_heating_v3.service
```

### **3. Home Assistant Integration**
```bash
# Test MQTT connectivity from Raspberry Pi
mosquitto_pub -h 192.168.0.110 -t "solar_heating_v3/test" -m "test"

# Check Home Assistant logs
# (Access Home Assistant web interface)
# Configuration > Logs > MQTT
```

## 🚨 **Troubleshooting Procedures**

### **For AI Assistant (Claude):**
1. **Analyze the problem** based on user description
2. **Provide diagnostic commands** for user to execute
3. **Interpret command output** provided by user
4. **Suggest solutions** based on analysis
5. **Guide implementation** through user execution

### **For User:**
1. **Execute diagnostic commands** provided by AI
2. **Share command output** with AI
3. **Implement solutions** guided by AI
4. **Verify fixes** through testing
5. **Report results** back to AI

### **Common Diagnostic Commands**
```bash
# Service status
sudo systemctl status solar_heating_v3.service
sudo systemctl status solar_heating_watchdog.service

# Service logs
sudo journalctl -u solar_heating_v3.service --since "1 hour ago"
sudo journalctl -u solar_heating_watchdog.service --since "1 hour ago"

# MQTT testing
mosquitto_sub -h 192.168.0.110 -t "solar_heating_v3/+/+" -C 5
mosquitto_pub -h 192.168.0.110 -t "test/topic" -m "test message"

# Hardware testing
python3 /home/pi/solar_heating/python/v3/hardware_interface.py
python3 /home/pi/solar_heating/python/v3/main_system.py --test

# Network connectivity
ping 192.168.0.110
telnet 192.168.0.110 1883
```

## 📊 **Environment Comparison**

| Capability | Local Dev | Raspberry Pi | Home Assistant |
|------------|-----------|--------------|----------------|
| Code Development | ✅ | ❌ | ❌ |
| Hardware Access | ❌ | ✅ | ❌ |
| Service Management | ❌ | ✅ | ❌ |
| MQTT Broker | ❌ | ✅ | ✅ |
| Dashboard | ❌ | ❌ | ✅ |
| Sensor Data | ❌ | ✅ | ✅ |
| Real-time Control | ❌ | ✅ | ✅ |
| Historical Data | ❌ | ❌ | ✅ |

## 🎯 **Best Practices**

### **Development**
- Develop and test code locally first
- Use comprehensive test suites
- Document all changes
- Follow TDD principles

### **Deployment**
- Test on Raspberry Pi before production
- Monitor service logs during deployment
- Verify MQTT connectivity
- Check Home Assistant integration

### **Troubleshooting**
- Start with service status checks
- Check logs for error messages
- Test MQTT connectivity
- Verify hardware connections
- Check Home Assistant integration

## 🔧 **Quick Reference Commands**

### **Service Management**
```bash
# Check service status
sudo systemctl status solar_heating_v3.service

# Restart service
sudo systemctl restart solar_heating_v3.service

# View logs
sudo journalctl -u solar_heating_v3.service --since "1 hour ago"
```

### **MQTT Testing**
```bash
# Subscribe to all messages
mosquitto_sub -h 192.168.0.110 -t "solar_heating_v3/+/+" -C 5

# Publish test message
mosquitto_pub -h 192.168.0.110 -t "test/topic" -m "test message"
```

### **Hardware Testing**
```bash
# Test hardware interface
python3 /home/pi/solar_heating/python/v3/hardware_interface.py

# Test main system
python3 /home/pi/solar_heating/python/v3/main_system.py --test
```

---

**This document should be updated whenever the environment setup changes or new procedures are discovered.**




