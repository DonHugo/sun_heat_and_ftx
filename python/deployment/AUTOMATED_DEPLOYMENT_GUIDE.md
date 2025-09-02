# Automated Deployment Guide

## 🚀 **One-Command Deployment for Raspberry Pi**

This guide shows you how to use the automated deployment script to set up your solar heating system v3 with a single command.

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
wget https://raw.githubusercontent.com/DonHugo/sun_heat_and_ftx/main/python/deployment/deploy_to_pi.sh

# Or copy it from your development machine
scp deploy_to_pi.sh pi@192.168.0.17:~/
```

### **Step 2: Update Configuration**

```bash
# Edit the script to update your repository URL
nano deploy_to_pi.sh
```

**Find and update this line:**
```bash
# git clone https://github.com/yourusername/sun_heat_and_ftx.git "$PROJECT_DIR"
```

**Change to your actual repository:**
```bash
git clone https://github.com/DonHugo/sun_heat_and_ftx.git "$PROJECT_DIR"
```

### **Step 3: Make Script Executable**

```bash
chmod +x deploy_to_pi.sh
```

## 🎯 **Run the Automated Deployment**

### **Single Command Deployment:**

```bash
# Run the automated deployment script
./deploy_to_pi.sh
```

### **What the Script Does:**

The script automatically performs all these steps:

1. ✅ **System Check** - Verifies Raspberry Pi
2. ✅ **System Update** - Updates all packages
3. ✅ **Install Dependencies** - Installs essential packages and Python libraries
4. ✅ **Clone Repository** - Downloads your code
5. ✅ **Setup v3 System** - Configures the active v3 system
6. ✅ **Create Virtual Environment** - Sets up Python virtual environment
7. ✅ **Install Python Dependencies** - Installs required Python packages
8. ✅ **Configure Systemd Service** - Creates auto-start service
9. ✅ **Enable Service** - Configures service to start on boot

## 📊 **Expected Output**

The script provides clear, informative output:

```
🚀 Solar Heating System Deployment Script
==========================================
📦 Updating system packages...
📦 Installing required packages...
📁 Setting up project directory: /home/pi/solar_heating
📥 Cloning repository...
🔧 Setting up v3 system...
🐍 Creating Python virtual environment...
📦 Installing Python dependencies...
🔧 Creating v3 service file...
✅ v3 system configured
```

## 🔧 **Post-Deployment Steps**

### **1. Verify Installation:**

```bash
# Check service status
sudo systemctl status solar_heating_v3.service

# Check if service is enabled
sudo systemctl is-enabled solar_heating_v3.service
```

### **2. Start the Service:**

```bash
# Start the service
sudo systemctl start solar_heating_v3.service

# Check logs
sudo journalctl -u solar_heating_v3.service -f
```

### **3. Test the System:**

```bash
# Navigate to the project directory
cd /home/pi/solar_heating/python/v3

# Activate virtual environment
source venv/bin/activate

# Test the system
python3 main_system.py
```

## 🚨 **Troubleshooting**

### **Common Issues:**

1. **Service won't start:**
   ```bash
   sudo journalctl -u solar_heating_v3.service -n 50
   ```

2. **Python dependencies missing:**
   ```bash
   cd /home/pi/solar_heating/python/v3
   source venv/bin/activate
   pip install -r requirements.txt
   ```

3. **Permission issues:**
   ```bash
   sudo chown -R pi:pi /home/pi/solar_heating
   ```

## 📚 **Additional Resources**

- **Fresh Pi Setup**: See `FRESH_PI_DEPLOYMENT_STEPS.md`
- **Testing Guide**: See `TESTING_GUIDE.md`
- **Main README**: See `README.md`

## 🎯 **Current Status**

- **v1 System**: ❌ REMOVED (no longer supported)
- **v2 System**: ❌ DEPRECATED (not maintained)
- **v3 System**: ✅ ACTIVE (production ready)
- **Deployment**: ✅ AUTOMATED (single command)

## 🚀 **Quick Start Summary**

```bash
# 1. Download script
wget https://raw.githubusercontent.com/DonHugo/sun_heat_and_ftx/main/python/deployment/deploy_to_pi.sh

# 2. Make executable
chmod +x deploy_to_pi.sh

# 3. Edit repository URL (if needed)
nano deploy_to_pi.sh

# 4. Run deployment
./deploy_to_pi.sh

# 5. Verify installation
sudo systemctl status solar_heating_v3.service
```

**That's it! Your solar heating system v3 will be automatically deployed and configured.**
