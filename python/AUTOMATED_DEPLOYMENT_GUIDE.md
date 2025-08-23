# Automated Deployment Guide

## 🚀 **One-Command Deployment for Raspberry Pi Zero 2W**

This guide shows you how to use the automated deployment script to set up your solar heating system with a single command.

## 📋 **Prerequisites**

### **Before Running the Script:**
1. **Flash Raspberry Pi OS** to your microSD card
2. **Configure initial settings** (SSH, WiFi, hostname)
3. **Boot your Raspberry Pi** and connect via SSH
4. **Update the repository URL** in the script (see below)

## 🔧 **Setup the Automated Script**

### **Step 1: Download the Script**

```bash
# On your Raspberry Pi, download the script
wget https://raw.githubusercontent.com/DonHugo/sun_heat_and_ftx/main/python/automated_deployment.sh

# Or copy it from your development machine
scp automated_deployment.sh pi@192.168.0.17:~/
```

### **Step 2: Update Configuration**

```bash
# Edit the script to update your repository URL
nano automated_deployment.sh
```


```bash
REPO_URL="https://github.com/DonHugo/sun_heat_and_ftx.git"
```


```bash
REPO_URL="https://github.com/DonHugo/sun_heat_and_ftx.git"
```

### **Step 3: Make Script Executable**

```bash
chmod +x automated_deployment.sh
```

## 🎯 **Run the Automated Deployment**

### **Single Command Deployment:**

```bash
# Run the automated deployment script
./automated_deployment.sh
```

### **What the Script Does:**

The script automatically performs all these steps:

1. ✅ **System Check** - Verifies Raspberry Pi
2. ✅ **System Update** - Updates all packages
3. ✅ **Install Dependencies** - Installs essential packages
4. ✅ **Enable I2C** - Configures I2C interface
5. ✅ **Install Hardware Libraries** - Sequent Microsystems libraries
6. ✅ **Verify Libraries** - Tests all hardware libraries
7. ✅ **Clone Repository** - Downloads your code
8. ✅ **Setup v1 System** - Configures original system
9. ✅ **Setup v3 System** - Configures new system
10. ✅ **Install Scripts** - System switching and updates
11. ✅ **Create Utilities** - Health check and sensor test
12. ✅ **Configure Services** - Auto-start and logging
13. ✅ **Test Connections** - MQTT and hardware
14. ✅ **Final Verification** - Complete system check

## 📊 **Expected Output**

The script provides colored, timestamped output:

```
🚀 Automated Solar Heating System Deployment
============================================
This script will deploy both v1 and v3 systems
on your Raspberry Pi Zero 2W

Continue with deployment? (y/N): y

[2025-08-22 18:30:00] Checking if running on Raspberry Pi...
[2025-08-22 18:30:01] ✅ Raspberry Pi detected
[2025-08-22 18:30:02] Updating system packages...
[2025-08-22 18:30:15] ✅ System updated
[2025-08-22 18:30:16] Installing essential packages...
[2025-08-22 18:30:25] ✅ Essential packages installed
...
[2025-08-22 18:35:00] ✅ All hardware libraries verified
...
[2025-08-22 18:40:00] 🎉 AUTOMATED DEPLOYMENT COMPLETED!
```

## 🔌 **After Deployment**

### **Step 1: Connect Hardware**
```bash
# Power off the Pi
sudo shutdown -h now

# Connect your hardware boards:
# - RTD Data Acquisition board
# - Building Automation V4 board  
# - Four Relays four HV Inputs board

# Power on the Pi
```

### **Step 2: Reboot System**
```bash
# SSH back into Pi
ssh pi@your-pi-ip-address

# Reboot to enable I2C
sudo reboot

# SSH back in after reboot
ssh pi@your-pi-ip-address
```

### **Step 3: Test Systems**
```bash
# Test v1 system
sudo systemctl start temperature_monitoring.service
sudo systemctl status temperature_monitoring.service

# Test v3 system
cd /home/pi/solar_heating/python/v3
source venv/bin/activate
python3 main.py

# Test system switching
system_switch.py status
system_switch.py v1
system_switch.py v3
```

## 🔧 **Useful Commands After Deployment**

### **System Management:**
```bash
system_switch.py status    # Check which system is running
system_switch.py v1        # Switch to v1 system
system_switch.py v3        # Switch to v3 system
system_switch.py logs      # View logs for active system
```

### **Health Monitoring:**
```bash
/home/pi/health_check.sh   # Complete system health check
/home/pi/test_sensors.py   # Test temperature sensors
```

### **Updates:**
```bash
/home/pi/update_solar_heating.sh  # Update from Git repository
```

### **Logs:**
```bash
sudo journalctl -u temperature_monitoring.service -f  # v1 logs
sudo journalctl -u solar_heating_v3.service -f        # v3 logs
```

## 🚨 **Troubleshooting**

### **If the Script Fails:**

**1. Check Error Messages**
```bash
# Look for specific error messages in the output
# The script will show exactly what failed
```

**2. Common Issues:**
- **Network connectivity** - Check WiFi/network
- **Repository URL** - Verify the URL is correct
- **Permissions** - Make sure script is executable
- **Disk space** - Ensure enough free space

**3. Manual Recovery:**
```bash
# If script fails, you can run individual steps manually
# See FRESH_PI_DEPLOYMENT_STEPS.md for detailed instructions
```

### **If Services Don't Start:**

**1. Check Service Status:**
```bash
sudo systemctl status temperature_monitoring.service
sudo systemctl status solar_heating_v3.service
```

**2. Check Logs:**
```bash
sudo journalctl -u temperature_monitoring.service -n 50
sudo journalctl -u solar_heating_v3.service -n 50
```

**3. Check Dependencies:**
```bash
python3 -c "import librtd, megabas, lib4relind"
```

## 📈 **Monitoring and Maintenance**

### **Daily Health Check:**
```bash
/home/pi/health_check.sh
```

### **Weekly Updates:**
```bash
/home/pi/update_solar_heating.sh
```

### **Monthly Maintenance:**
```bash
# Check disk space
df -h

# Check system resources
htop

# Check for system updates
sudo apt update && sudo apt upgrade -y
```

## 🎉 **Success Indicators**

Your deployment is successful when:

✅ **All services start without errors**  
✅ **MQTT connection works**  
✅ **Temperature sensors respond**  
✅ **Pump control functions**  
✅ **System switching works**  
✅ **Health check passes**  

## 🚀 **Next Steps After Successful Deployment**

1. **Monitor the system** for 24-48 hours
2. **Set up Home Assistant** dashboard
3. **Configure alerts** for temperature/pump issues
4. **Set up backup** strategy
5. **Integrate TaskMaster AI** features

---

**The automated deployment script makes setting up your solar heating system as simple as running one command!** 🎯
