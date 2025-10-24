# Comprehensive Troubleshooting Guide

## 🚨 **Emergency Troubleshooting Procedures**

This guide provides step-by-step troubleshooting procedures for the Solar Heating System, designed for collaboration between AI assistant and user.

## 🏗️ **System Architecture for Troubleshooting**

### **Environment Overview**
- **Local Development**: Mac/Linux (code development, testing)
- **Raspberry Pi**: Hardware interface, sensor data, services
- **Home Assistant**: Dashboard, MQTT broker, visualization
- **AI Assistant**: Analysis, guidance, solution planning

### **Communication Flow**
```
AI Assistant ←→ User ←→ Raspberry Pi ←→ Home Assistant
     ↓              ↓           ↓              ↓
  Analysis    Command      Hardware      Dashboard
  & Planning  Execution    Interface     & Control
```

## 🔍 **Troubleshooting Methodology**

### **Phase 1: Problem Identification**
1. **User describes the issue**
2. **AI analyzes the problem**
3. **AI provides diagnostic commands**
4. **User executes commands**
5. **AI interprets results**

### **Phase 2: Root Cause Analysis**
1. **AI identifies potential causes**
2. **AI provides targeted diagnostics**
3. **User executes specific tests**
4. **AI confirms root cause**

### **Phase 3: Solution Implementation**
1. **AI plans solution approach**
2. **AI provides implementation steps**
3. **User executes solution**
4. **AI validates results**

## 📋 **Common Issues and Solutions**

### **Issue 1: Service Not Running**

#### **Symptoms:**
- No data in Home Assistant
- Watchdog reporting service down
- No heartbeat messages

#### **Diagnostic Commands:**
```bash
# Check service status
sudo systemctl status solar_heating_v3.service

# Check if service is enabled
sudo systemctl is-enabled solar_heating_v3.service

# Check service logs
sudo journalctl -u solar_heating_v3.service --since "1 hour ago"

# Check for multiple instances
ps aux | grep -i solar
```

#### **Common Solutions:**
```bash
# Start service
sudo systemctl start solar_heating_v3.service

# Enable service
sudo systemctl enable solar_heating_v3.service

# Restart service
sudo systemctl restart solar_heating_v3.service

# Kill multiple instances
sudo pkill -f "main_system.py"
sudo systemctl start solar_heating_v3.service
```

### **Issue 2: MQTT Connectivity Problems**

#### **Symptoms:**
- No data in Home Assistant
- MQTT connection errors in logs
- Heartbeat messages not received

#### **Diagnostic Commands:**
```bash
# Test MQTT broker connectivity
mosquitto_sub -h 192.168.0.110 -t "solar_heating_v3/+/+" -C 5

# Check MQTT broker status
sudo systemctl status mosquitto

# Test MQTT publishing
mosquitto_pub -h 192.168.0.110 -t "test/topic" -m "test message"

# Check network connectivity
ping 192.168.0.110
telnet 192.168.0.110 1883
```

#### **Common Solutions:**
```bash
# Install MQTT broker (if missing)
sudo apt update
sudo apt install mosquitto mosquitto-clients
sudo systemctl enable mosquitto
sudo systemctl start mosquitto

# Restart MQTT broker
sudo systemctl restart mosquitto

# Restart Home Assistant (if MQTT broker is there)
# (Access Home Assistant web interface and restart)
```

### **Issue 3: Hardware Interface Problems**

#### **Symptoms:**
- No temperature readings
- Hardware errors in logs
- Sensor data missing

#### **Diagnostic Commands:**
```bash
# Test hardware interface
python3 /home/pi/solar_heating/python/v3/hardware_interface.py

# Check hardware connections
lsusb
lsmod | grep i2c

# Check sensor readings
python3 /home/pi/solar_heating/python/v3/main_system.py --test-sensors

# Check hardware logs
sudo journalctl -u solar_heating_v3.service | grep -i hardware
```

#### **Common Solutions:**
```bash
# Restart hardware interface
sudo systemctl restart solar_heating_v3.service

# Check hardware connections
# (Physical inspection of RTD boards, sensors)

# Test individual components
python3 /home/pi/solar_heating/python/v3/hardware_interface.py --test-rtd
python3 /home/pi/solar_heating/python/v3/hardware_interface.py --test-megabas
```

### **Issue 4: Home Assistant Integration Problems**

#### **Symptoms:**
- No sensors in Home Assistant
- MQTT discovery not working
- Dashboard not updating

#### **Diagnostic Commands:**
```bash
# Test MQTT message publishing
mosquitto_pub -h 192.168.0.110 -t "solar_heating_v3/test" -m "test"

# Check MQTT topics
mosquitto_sub -h 192.168.0.110 -t "solar_heating_v3/+/+" -C 10

# Check Home Assistant MQTT integration
# (Access Home Assistant web interface)
# Configuration > Integrations > MQTT
```

#### **Common Solutions:**
```bash
# Restart Home Assistant
# (Access Home Assistant web interface and restart)

# Check MQTT configuration in Home Assistant
# Configuration > Integrations > MQTT > Configure

# Restart MQTT broker
sudo systemctl restart mosquitto
```

### **Issue 5: Watchdog Service Problems**

#### **Symptoms:**
- False alerts
- Service monitoring not working
- Watchdog not detecting service status

#### **Diagnostic Commands:**
```bash
# Check watchdog status
sudo systemctl status solar_heating_watchdog.service

# Check watchdog logs
sudo journalctl -u solar_heating_watchdog.service --since "1 hour ago"

# Check service name consistency
sudo systemctl cat solar_heating_v3.service
sudo systemctl cat solar_heating_watchdog.service

# Check watchdog configuration
grep -n "service_name" /home/pi/solar_heating/python/v3/watchdog.py
```

#### **Common Solutions:**
```bash
# Restart watchdog
sudo systemctl restart solar_heating_watchdog.service

# Fix service name mismatch
sudo mv /etc/systemd/system/solar-heating-v3.service /etc/systemd/system/solar_heating_v3.service
sudo systemctl daemon-reload
sudo systemctl restart solar_heating_v3.service
sudo systemctl restart solar_heating_watchdog.service
```

## 🔧 **Diagnostic Command Reference**

### **Service Management**
```bash
# Service status
sudo systemctl status solar_heating_v3.service
sudo systemctl status solar_heating_watchdog.service
sudo systemctl status mosquitto

# Service control
sudo systemctl start solar_heating_v3.service
sudo systemctl stop solar_heating_v3.service
sudo systemctl restart solar_heating_v3.service
sudo systemctl enable solar_heating_v3.service
sudo systemctl disable solar_heating_v3.service

# Service logs
sudo journalctl -u solar_heating_v3.service --since "1 hour ago"
sudo journalctl -u solar_heating_watchdog.service --since "1 hour ago"
sudo journalctl -u mosquitto --since "1 hour ago"
```

### **MQTT Testing**
```bash
# Subscribe to messages
mosquitto_sub -h 192.168.0.110 -t "solar_heating_v3/+/+" -C 5
mosquitto_sub -h 192.168.0.110 -t "solar_heating_v3/heartbeat" -C 3
mosquitto_sub -h 192.168.0.110 -t "solar_heating_v3/temperature/+" -C 3

# Publish test messages
mosquitto_pub -h 192.168.0.110 -t "test/topic" -m "test message"
mosquitto_pub -h 192.168.0.110 -t "solar_heating_v3/test" -m "test"
```

### **Hardware Testing**
```bash
# Test hardware interface
python3 /home/pi/solar_heating/python/v3/hardware_interface.py
python3 /home/pi/solar_heating/python/v3/hardware_interface.py --test
python3 /home/pi/solar_heating/python/v3/hardware_interface.py --test-rtd
python3 /home/pi/solar_heating/python/v3/hardware_interface.py --test-megabas

# Test main system
python3 /home/pi/solar_heating/python/v3/main_system.py --test
python3 /home/pi/solar_heating/python/v3/main_system.py --test-sensors
```

### **Network Testing**
```bash
# Network connectivity
ping 192.168.0.110
ping 8.8.8.8
ping 1.1.1.1

# Port testing
telnet 192.168.0.110 1883
nmap -p 1883 192.168.0.110

# Network interfaces
ip addr show
ip route show
```

### **System Information**
```bash
# System status
uptime
free -h
df -h
ps aux | grep -i solar

# Hardware information
lsusb
lsmod | grep i2c
i2cdetect -y 1

# Service files
sudo systemctl cat solar_heating_v3.service
sudo systemctl cat solar_heating_watchdog.service
sudo systemctl cat mosquitto
```

## 🚨 **Emergency Procedures**

### **Complete System Restart**
```bash
# Stop all services
sudo systemctl stop solar_heating_v3.service
sudo systemctl stop solar_heating_watchdog.service
sudo systemctl stop mosquitto

# Kill any remaining processes
sudo pkill -f "main_system.py"
sudo pkill -f "watchdog.py"

# Start services in order
sudo systemctl start mosquitto
sleep 5
sudo systemctl start solar_heating_v3.service
sleep 10
sudo systemctl start solar_heating_watchdog.service

# Check status
sudo systemctl status solar_heating_v3.service
sudo systemctl status solar_heating_watchdog.service
sudo systemctl status mosquitto
```

### **Service Recovery**
```bash
# If service keeps failing
sudo systemctl stop solar_heating_v3.service
sudo systemctl disable solar_heating_v3.service
sudo systemctl daemon-reload
sudo systemctl enable solar_heating_v3.service
sudo systemctl start solar_heating_v3.service
```

### **Configuration Reset**
```bash
# Reset to default configuration
sudo systemctl stop solar_heating_v3.service
sudo cp /home/pi/solar_heating/python/v3/config.py.backup /home/pi/solar_heating/python/v3/config.py
sudo systemctl start solar_heating_v3.service
```

## 📊 **Troubleshooting Checklist**

### **Before Starting Troubleshooting**
- [ ] Identify the specific problem
- [ ] Check if it's a new issue or recurring
- [ ] Note any recent changes
- [ ] Check system uptime

### **Basic Health Checks**
- [ ] Service status (all services running)
- [ ] Network connectivity (ping tests)
- [ ] MQTT connectivity (mosquitto tests)
- [ ] Hardware interface (sensor readings)
- [ ] Home Assistant integration (dashboard)

### **Advanced Diagnostics**
- [ ] Service logs (error messages)
- [ ] Hardware logs (connection issues)
- [ ] MQTT logs (message flow)
- [ ] System logs (kernel messages)
- [ ] Network logs (connectivity issues)

### **Solution Validation**
- [ ] Service restarts successfully
- [ ] MQTT messages flowing
- [ ] Hardware responding
- [ ] Home Assistant updating
- [ ] No error messages in logs

## 🎯 **AI Assistant Guidelines**

### **For AI Assistant (Claude):**
1. **Always ask for diagnostic output** before suggesting solutions
2. **Provide specific commands** for user to execute
3. **Interpret results** based on command output
4. **Suggest targeted solutions** based on analysis
5. **Guide step-by-step implementation**
6. **Validate results** through testing

### **For User:**
1. **Execute diagnostic commands** exactly as provided
2. **Share complete output** with AI assistant
3. **Follow solution steps** carefully
4. **Test results** after implementation
5. **Report any issues** encountered

## 📝 **Documentation Updates**

This troubleshooting guide should be updated whenever:
- New issues are discovered
- New solutions are found
- System architecture changes
- New diagnostic tools are added
- Procedures are improved

---

**Remember: Always start with basic health checks before diving into complex diagnostics!**






