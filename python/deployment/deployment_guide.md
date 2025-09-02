# Solar Heating System Deployment Guide

## 🎯 **Deployment Strategy: Dual System (v1 + v3)**

This guide helps you deploy both the original v1 system and the new v3 system on your Raspberry Pi Zero 2 W, allowing you to switch between them as needed.

## 📋 **System Overview**

### **v1 System (Original)**
- **File**: `python/temperature_monitoring.py`
- **Status**: ✅ **Proven and working**
- **Use Case**: Production fallback, stable operation
- **Features**: Direct hardware control, MQTT integration

### **v3 System (New)**
- **Directory**: `python/v3/`
- **Status**: ✅ **Tested in simulation, ready for hardware**
- **Use Case**: Enhanced features, better architecture
- **Features**: Modular design, Home Assistant integration, TaskMaster AI ready

## 🚀 **Deployment Steps**

### **Step 1: Prepare Raspberry Pi Zero 2 W**

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python dependencies
sudo apt install python3 python3-pip python3-venv git -y

# Install required system libraries
sudo apt install libi2c-dev i2c-tools -y
```

### **Step 2: Install Sequent Microsystems Libraries**

```bash
# Install required system packages
sudo apt-get update
sudo apt-get install build-essential python3-pip python3-dev python3-smbus git

# Install RTD Data Acquisition
git clone https://github.com/SequentMicrosystems/rtd-rpi.git
cd rtd-rpi/python/rtd/
sudo python3 setup.py install
cd ~

# Install Building Automation V4 (MegaBAS)
git clone https://github.com/SequentMicrosystems/megabas-rpi.git
cd megabas-rpi/python/
sudo python3 setup.py install
cd ~

# Install Four Relays four HV Inputs
git clone https://github.com/SequentMicrosystems/4relind-rpi.git
cd 4relind-rpi/python/4relind/
sudo python3 setup.py install
cd ~

# Clean up installation files
rm -rf rtd-rpi megabas-rpi 4relind-rpi

# Verify installation
python3 -c "import librtd; print('✅ RTD library installed')"
python3 -c "import megabas; print('✅ MegaBAS library installed')"
python3 -c "import lib4relind; print('✅ 4RELIND library installed')"
```

**Download Links:**
- **RTD Data Acquisition**: https://sequentmicrosystems.com/pages/rtd-data-acquisition-downloads
- **Building Automation V4**: https://sequentmicrosystems.com/pages/building-automation-downloads  
- **Four Relays four HV Inputs**: https://sequentmicrosystems.com/pages/four-relays-four-inputs-downloads

### **Step 3: Clone and Setup Project**

```bash
# Clone your repository
git clone <your-repo-url> /home/pi/solar_heating
cd /home/pi/solar_heating

# Create virtual environment for v3
cd python/v3
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### **Step 4: Configure v1 System**

```bash
# Copy v1 system to production location
sudo cp /home/pi/solar_heating/python/temperature_monitoring.py /usr/local/bin/
sudo cp /home/pi/solar_heating/python/temperature_monitoring.service /etc/systemd/system/

# Make executable
sudo chmod +x /usr/local/bin/temperature_monitoring.py

# Enable and start v1 service
sudo systemctl enable temperature_monitoring.service
sudo systemctl start temperature_monitoring.service
```

### **Step 5: Configure v3 System**

```bash
# Create v3 service file
sudo nano /etc/systemd/system/solar_heating_v3.service
```

**v3 Service File Content:**
```ini
[Unit]
Description=Solar Heating System v3
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/solar_heating/python/v3
Environment=PATH=/home/pi/solar_heating/python/v3/venv/bin
ExecStart=/home/pi/solar_heating/python/v3/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable v3 service (but don't start yet)
sudo systemctl enable solar_heating_v3.service
```

## 🔄 **System Switching**

### **Switch to v1 (Original System)**
```bash
# Stop v3 if running
sudo systemctl stop solar_heating_v3.service

# Start v1
sudo systemctl start temperature_monitoring.service

# Check status
sudo systemctl status temperature_monitoring.service
```

### **Switch to v3 (New System)**
```bash
# Stop v1 if running
sudo systemctl stop temperature_monitoring.service

# Start v3
sudo systemctl start solar_heating_v3.service

# Check status
sudo systemctl status solar_heating_v3.service
```

### **Check Which System is Running**
```bash
# Check v1 status
sudo systemctl is-active temperature_monitoring.service

# Check v3 status
sudo systemctl is-active solar_heating_v3.service
```

## 🧪 **Testing Strategy**

### **Phase 1: Test v1 First**
```bash
# Ensure v1 works on hardware
sudo systemctl start temperature_monitoring.service
sudo systemctl status temperature_monitoring.service

# Monitor logs
sudo journalctl -u temperature_monitoring.service -f
```

### **Phase 2: Test v3**
```bash
# Stop v1
sudo systemctl stop temperature_monitoring.service

# Test v3 in simulation mode first
cd /home/pi/solar_heating/python/v3
source venv/bin/activate
SOLAR_TEST_MODE=true python3 main.py

# If simulation works, test with real hardware
python3 main.py
```

### **Phase 3: Production Deployment**
```bash
# Once v3 is tested and working
sudo systemctl start solar_heating_v3.service
```

## 📊 **Monitoring and Logs**

### **View v1 Logs**
```bash
sudo journalctl -u temperature_monitoring.service -f
```

### **View v3 Logs**
```bash
sudo journalctl -u solar_heating_v3.service -f
```

### **Check MQTT Messages**
```bash
# Install mosquitto client
sudo apt install mosquitto-clients

# Subscribe to v1 topics
mosquitto_sub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "rtd/#"

# Subscribe to v3 topics
mosquitto_sub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "solar_heating_v3/#"
```

## 🔧 **Troubleshooting**

### **Common Issues**

**1. Hardware Libraries Not Found**
```bash
# Check if libraries are installed
ls -la /usr/local/lib/ | grep -E "(megabas|librtd|lib4relind)"

# Check library path
echo $LD_LIBRARY_PATH
```

**2. MQTT Connection Issues**
```bash
# Test MQTT connection
mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "test" -m "hello"
```

**3. Service Won't Start**
```bash
# Check service configuration
sudo systemctl status solar_heating_v3.service

# Check logs
sudo journalctl -u solar_heating_v3.service -n 50
```

## 📈 **Performance Monitoring**

### **System Resources**
```bash
# Monitor CPU and memory
htop

# Monitor disk usage
df -h

# Monitor network
iftop
```

### **Temperature Monitoring**
```bash
# Check CPU temperature
vcgencmd measure_temp

# Check system load
uptime
```

## 🔄 **Backup and Recovery**

### **Backup Configuration**
```bash
# Backup v1 configuration
sudo cp /usr/local/bin/temperature_monitoring.py /home/pi/backup/

# Backup v3 configuration
cp /home/pi/solar_heating/python/v3/config.py /home/pi/backup/
```

### **Recovery Procedure**
```bash
# If v3 fails, quickly switch back to v1
sudo systemctl stop solar_heating_v3.service
sudo systemctl start temperature_monitoring.service
```

## ✅ **Success Criteria**

- [ ] v1 system runs successfully on Raspberry Pi
- [ ] v3 system runs successfully in simulation mode
- [ ] v3 system runs successfully with real hardware
- [ ] MQTT communication works for both systems
- [ ] System switching works reliably
- [ ] Monitoring and logging work correctly
- [ ] Backup and recovery procedures tested

## 🎯 **Next Steps After Deployment**

1. **Test v1 thoroughly** - Ensure it works as expected
2. **Test v3 in simulation** - Validate all features
3. **Test v3 with hardware** - Gradual transition
4. **Set up Home Assistant** - Create monitoring dashboard
5. **Integrate TaskMaster AI** - Add intelligent features
6. **Performance optimization** - Fine-tune for production

---

**Note**: This deployment strategy ensures you always have a working system while testing the new v3 features. The v1 system serves as your reliable fallback option.
