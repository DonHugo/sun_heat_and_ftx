# Fresh Raspberry Pi Zero 2W Deployment Steps

## 🎯 **Complete Step-by-Step Deployment Guide**

This guide walks you through deploying your solar heating system on a brand new Raspberry Pi Zero 2W from scratch.

## 📋 **Prerequisites**

### **Hardware Required:**
- Raspberry Pi Zero 2W
- MicroSD card (16GB or larger, Class 10 recommended)
- Power supply (5V, 2.5A minimum)
- Sequent Microsystems hardware boards:
  - RTD Data Acquisition board
  - Building Automation V4 board
  - Four Relays four HV Inputs board
- Network connection (WiFi or Ethernet)

### **Software Required:**
- Raspberry Pi Imager (download from raspberrypi.org)
- Your Git repository URL

## 🚀 **Step 1: Prepare Raspberry Pi OS**

### **1.1 Download and Flash OS**
```bash
# Download Raspberry Pi Imager from:
# https://www.raspberrypi.com/software/

# Insert microSD card into your computer
# Open Raspberry Pi Imager
# Select: Raspberry Pi OS Lite (64-bit) - No desktop
# Select your microSD card
# Click "Write" and wait for completion
```

### **1.2 Configure Initial Setup**
```bash
# Before ejecting the card, click the gear icon (⚙️) in Raspberry Pi Imager
# Configure these settings:

# Set hostname: solar-heating-pi
# Enable SSH: ✓
# Set username: pi
# Set password: [your-secure-password]
# Configure WiFi: [your-wifi-credentials]
# Set locale: [your-timezone]

# Click "Save" and eject the card
```

## 🔌 **Step 2: Initial Pi Setup**

### **2.1 Boot and Connect**
```bash
# Insert microSD card into Pi Zero 2W
# Connect power supply
# Wait 2-3 minutes for first boot

# Find your Pi's IP address:
# Option A: Check your router's admin panel
# Option B: Use nmap: nmap -sn 192.168.1.0/24
# Option C: Use Raspberry Pi Imager's "Advanced" menu

# SSH into your Pi:
ssh pi@your-pi-ip-address
# Password: [your-password]
```

### **2.2 Initial System Update**
```bash
# Update system packages
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git curl wget htop vim

# Set up SSH key (optional but recommended)
# On your development machine:
ssh-keygen -t ed25519 -C "your-email@example.com"
ssh-copy-id pi@your-pi-ip-address
```

## 🔧 **Step 3: Install Sequent Microsystems Libraries**

### **3.1 Install Dependencies**
```bash
# Install build tools and Python dependencies
sudo apt-get update
sudo apt-get install -y build-essential python3-pip python3-dev python3-smbus git

# Enable I2C interface
sudo raspi-config
# Navigate to: Interface Options → I2C → Enable
# Reboot when prompted
sudo reboot

# SSH back in after reboot
ssh pi@your-pi-ip-address
```

### **3.2 Install Hardware Libraries**
```bash
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
```

### **3.3 Verify Installation**
```bash
# Test all libraries
python3 -c "import librtd; print('✅ RTD library installed')"
python3 -c "import megabas; print('✅ MegaBAS library installed')"
python3 -c "import lib4relind; print('✅ 4RELIND library installed')"

# If all show ✅, proceed to next step
```

## 📥 **Step 4: Deploy Solar Heating System**

### **4.1 Clone Your Repository**
```bash
# Clone your solar heating repository
git clone https://github.com/yourusername/sun_heat_and_ftx.git /home/pi/solar_heating
cd /home/pi/solar_heating

# Verify files are present
ls -la python/
ls -la python/v3/
```

### **4.2 Run Deployment Script**
```bash
# Make deployment script executable
chmod +x python/deploy_to_pi.sh

# Run the deployment script
./python/deploy_to_pi.sh

# The script will:
# - Install Python dependencies
# - Set up systemd services
# - Configure v1 and v3 systems
# - Create backup directories
```

## 🔌 **Step 5: Connect Hardware**

### **5.1 Physical Connections**
```bash
# Power off the Pi
sudo shutdown -h now

# Connect hardware boards:
# 1. RTD Data Acquisition board (for temperature sensors)
# 2. Building Automation V4 board (for general I/O)
# 3. Four Relays four HV Inputs board (for pump control)

# Connect sensors and pumps according to your wiring diagram
# Power on the Pi
```

### **5.2 Verify Hardware Connections**
```bash
# SSH back into Pi
ssh pi@your-pi-ip-address

# Check I2C devices
i2cdetect -y 1

# You should see your boards at their configured addresses
```

## 🧪 **Step 6: Test Systems**

### **6.1 Test v1 System First**
```bash
# Start v1 system
sudo systemctl start temperature_monitoring.service

# Check status
sudo systemctl status temperature_monitoring.service

# View logs
sudo journalctl -u temperature_monitoring.service -f

# Test for 5-10 minutes to ensure it's working
# Look for temperature readings and pump control
```

### **6.2 Test v3 System**
```bash
# Stop v1 system
sudo systemctl stop temperature_monitoring.service

# Test v3 in simulation mode first
cd /home/pi/solar_heating/python/v3
source venv/bin/activate
SOLAR_TEST_MODE=true python3 main.py

# If simulation works, test with real hardware
python3 main.py

# Check MQTT communication
mosquitto_sub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "solar_heating_v3/#"
```

### **6.3 Test System Switching**
```bash
# Test the system switch script
system_switch.py status
system_switch.py v1
system_switch.py v3
system_switch.py logs
```

## 🔧 **Step 7: Configure for Production**

### **7.1 Set Up Auto-Start**
```bash
# Enable services to start on boot
sudo systemctl enable temperature_monitoring.service
sudo systemctl enable solar_heating_v3.service

# By default, v1 will start on boot
# You can change this by editing the service files
```

### **7.2 Configure Network**
```bash
# Set static IP (optional but recommended)
sudo nano /etc/dhcpcd.conf

# Add at the end:
# interface wlan0
# static ip_address=192.168.1.100/24
# static routers=192.168.1.1
# static domain_name_servers=8.8.8.8

# Reboot to apply
sudo reboot
```

### **7.3 Set Up Monitoring**
```bash
# Create health check script
nano /home/pi/health_check.sh

# Copy the health check script from git_deployment_guide.md
# Make it executable
chmod +x /home/pi/health_check.sh

# Test it
/home/pi/health_check.sh
```

## 📊 **Step 8: Verify Everything Works**

### **8.1 Final System Check**
```bash
# Check all services
sudo systemctl status temperature_monitoring.service
sudo systemctl status solar_heating_v3.service

# Check MQTT communication
mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "test" -m "hello"

# Check hardware
python3 -c "import librtd, megabas, lib4relind; print('All hardware libraries working')"

# Check disk space
df -h

# Check system resources
htop
```

### **8.2 Test Temperature Sensors**
```bash
# Create a quick test script
nano /home/pi/test_sensors.py
```

**Test Script Content:**
```python
#!/usr/bin/env python3
import librtd
import megabas
import lib4relind
import time

print("Testing temperature sensors...")

# Test RTD sensors
try:
    rtd = librtd.RTD()
    for i in range(8):
        temp = rtd.readTemp(0, i)
        print(f"RTD {i}: {temp:.1f}°C")
except Exception as e:
    print(f"RTD error: {e}")

# Test MegaBAS sensors
try:
    mb = megabas.MegaBAS()
    for i in range(8):
        temp = mb.readTemp(3, i)
        print(f"MegaBAS {i}: {temp:.1f}°C")
except Exception as e:
    print(f"MegaBAS error: {e}")

print("Sensor test completed")
```

```bash
# Run sensor test
python3 /home/pi/test_sensors.py
```

## 🔄 **Step 9: Set Up Updates**

### **9.1 Create Update Script**
```bash
# Copy the update script
cp /home/pi/solar_heating/python/update_solar_heating.sh /home/pi/
chmod +x /home/pi/update_solar_heating.sh

# Test update process
cd /home/pi/solar_heating
./python/update_solar_heating.sh
```

### **9.2 Set Up Cron Job (Optional)**
```bash
# Edit crontab
crontab -e

# Add line to check for updates daily at 2 AM:
# 0 2 * * * /home/pi/update_solar_heating.sh >> /home/pi/update.log 2>&1
```

## ✅ **Step 10: Final Verification**

### **10.1 Production Test**
```bash
# Start v1 system for production
system_switch.py v1

# Monitor for 24 hours
# Check logs periodically
sudo journalctl -u temperature_monitoring.service -f

# Test v3 system
system_switch.py v3
sudo journalctl -u solar_heating_v3.service -f
```

### **10.2 Documentation**
```bash
# Document your setup
nano /home/pi/SETUP_NOTES.txt

# Include:
# - IP address
# - Hardware configuration
# - Sensor mappings
# - Any custom settings
# - Troubleshooting notes
```

## 🎉 **Deployment Complete!**

Your Raspberry Pi Zero 2W is now fully configured with:
- ✅ Raspberry Pi OS Lite
- ✅ Sequent Microsystems libraries
- ✅ v1 system (proven and working)
- ✅ v3 system (new features)
- ✅ System switching capability
- ✅ MQTT communication
- ✅ Auto-start services
- ✅ Update mechanism
- ✅ Health monitoring

## 📞 **Troubleshooting**

### **Common Issues:**

**1. Hardware Not Detected**
```bash
# Check I2C
i2cdetect -y 1
# Check connections and addresses
```

**2. MQTT Connection Failed**
```bash
# Test MQTT manually
mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "test" -m "hello"
```

**3. Service Won't Start**
```bash
# Check logs
sudo journalctl -u service-name -n 50
# Check dependencies
python3 -c "import librtd, megabas, lib4relind"
```

**4. Temperature Readings Wrong**
```bash
# Check sensor connections
# Verify board addresses
# Test individual sensors
```

## 🚀 **Next Steps**

1. **Monitor the system** for 24-48 hours
2. **Set up Home Assistant** dashboard
3. **Configure alerts** for temperature/pump issues
4. **Set up backup** strategy
5. **Integrate TaskMaster AI** features

---

**Your solar heating system is now ready for production use!** 🎯
