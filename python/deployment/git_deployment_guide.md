# Git-Based Deployment Guide for Solar Heating System

## 🎯 **Git Deployment Strategy**

This guide shows you how to deploy both v1 and v3 systems to your Raspberry Pi using Git for easy updates and version control.

## 📋 **Prerequisites**

### **On Your Development Machine:**
- Git repository with your solar heating system
- All v1 and v3 code committed and pushed
- Repository accessible from Raspberry Pi

### **On Raspberry Pi:**
- Git installed
- SSH key set up (optional, for secure access)
- Internet connection

## 🚀 **Initial Deployment**

### **Step 1: Clone Repository on Raspberry Pi**

```bash
# SSH into your Raspberry Pi
ssh pi@your-pi-ip-address

# Clone your repository
git clone https://github.com/yourusername/sun_heat_and_ftx.git /home/pi/solar_heating
cd /home/pi/solar_heating
```

### **Step 2: Run Deployment Script**

```bash
# Make deployment script executable
chmod +x python/deploy_to_pi.sh

# Run deployment script
./python/deploy_to_pi.sh
```

### **Step 3: Install Sequent Microsystems Libraries**

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

## 🔄 **Update Workflow**

### **Development Workflow:**

1. **Make changes** on your development machine
2. **Test changes** locally
3. **Commit and push** to Git repository
4. **Deploy to Raspberry Pi** (see below)

### **Deployment Commands:**

```bash
# SSH into Raspberry Pi
ssh pi@your-pi-ip-address

# Navigate to project directory
cd /home/pi/solar_heating

# Pull latest changes
git pull origin main

# Restart services if needed
sudo systemctl restart temperature_monitoring.service  # v1
sudo systemctl restart solar_heating_v3.service        # v3
```

## 🔧 **Automated Deployment Script**

Create an update script for easy deployment:

```bash
# Create update script
nano /home/pi/update_solar_heating.sh
```

**Update Script Content:**
```bash
#!/bin/bash
# Solar Heating System Update Script

set -e

PROJECT_DIR="/home/pi/solar_heating"
BRANCH="main"

echo "🔄 Updating Solar Heating System..."
echo "=================================="

# Navigate to project directory
cd "$PROJECT_DIR"

# Check if there are changes to pull
git fetch origin
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ $LOCAL = $REMOTE ]; then
    echo "✅ System is up to date"
    exit 0
fi

echo "📥 Pulling latest changes..."
git pull origin $BRANCH

echo "🔧 Updating v3 dependencies..."
cd "$PROJECT_DIR/python/v3"
source venv/bin/activate
pip install -r requirements.txt

echo "🔄 Restarting services..."
sudo systemctl restart temperature_monitoring.service
sudo systemctl restart solar_heating_v3.service

echo "✅ Update completed successfully!"
echo "📊 Service status:"
sudo systemctl status temperature_monitoring.service --no-pager
sudo systemctl status solar_heating_v3.service --no-pager
```

```bash
# Make update script executable
chmod +x /home/pi/update_solar_heating.sh
```

## 🔐 **Secure Git Access (Optional)**

### **Set up SSH Key Authentication:**

```bash
# On your development machine, generate SSH key
ssh-keygen -t ed25519 -C "your-email@example.com"

# Copy public key to Raspberry Pi
ssh-copy-id pi@your-pi-ip-address

# Test SSH access
ssh pi@your-pi-ip-address
```

### **Use SSH for Git Repository:**

```bash
# On Raspberry Pi, change repository URL to SSH
cd /home/pi/solar_heating
git remote set-url origin git@github.com:yourusername/sun_heat_and_ftx.git
```

## 📊 **Version Management**

### **Check Current Version:**

```bash
# On Raspberry Pi
cd /home/pi/solar_heating
git log --oneline -5
git status
```

### **Rollback to Previous Version:**

```bash
# If you need to rollback
git log --oneline -10  # Find the commit hash
git reset --hard <commit-hash>
sudo systemctl restart temperature_monitoring.service
sudo systemctl restart solar_heating_v3.service
```

## 🔄 **Branch Strategy**

### **Development Branches:**

```bash
# Create feature branch for development
git checkout -b feature/new-feature

# Work on features
# Test locally
# Push to remote
git push origin feature/new-feature

# Merge to main when ready
git checkout main
git merge feature/new-feature
git push origin main
```

### **Stable Releases:**

```bash
# Create release tag
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# On Raspberry Pi, checkout specific version
git checkout v1.0.0
```

## 📋 **Deployment Checklist**

### **Before Deployment:**
- [ ] All changes tested locally
- [ ] Code committed and pushed to Git
- [ ] Dependencies updated in requirements.txt
- [ ] Configuration files updated
- [ ] Documentation updated

### **After Deployment:**
- [ ] Services start successfully
- [ ] MQTT communication working
- [ ] Hardware sensors responding
- [ ] Pump control working
- [ ] Logs show no errors

## 🚨 **Emergency Rollback**

If something goes wrong:

```bash
# Quick rollback to previous working version
cd /home/pi/solar_heating
git reset --hard HEAD~1

# Restart services
sudo systemctl restart temperature_monitoring.service
sudo systemctl restart solar_heating_v3.service

# Or switch to v1 system only
sudo systemctl stop solar_heating_v3.service
sudo systemctl start temperature_monitoring.service
```

## 📈 **Monitoring Deployment**

### **Check Deployment Status:**

```bash
# Check which version is running
cd /home/pi/solar_heating
git log --oneline -1

# Check service status
sudo systemctl status temperature_monitoring.service
sudo systemctl status solar_heating_v3.service

# Check logs
sudo journalctl -u temperature_monitoring.service -f
sudo journalctl -u solar_heating_v3.service -f
```

### **Automated Health Check:**

```bash
# Create health check script
nano /home/pi/health_check.sh
```

**Health Check Script:**
```bash
#!/bin/bash
# Health check for solar heating system

echo "🏥 Solar Heating System Health Check"
echo "===================================="

# Check v1 service
if systemctl is-active --quiet temperature_monitoring.service; then
    echo "✅ v1 service: RUNNING"
else
    echo "❌ v1 service: STOPPED"
fi

# Check v3 service
if systemctl is-active --quiet solar_heating_v3.service; then
    echo "✅ v3 service: RUNNING"
else
    echo "❌ v3 service: STOPPED"
fi

# Check MQTT connection
if mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "health_check" -m "test" 2>/dev/null; then
    echo "✅ MQTT: CONNECTED"
else
    echo "❌ MQTT: DISCONNECTED"
fi

# Check disk space
DISK_USAGE=$(df /home/pi | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 90 ]; then
    echo "✅ Disk space: OK ($DISK_USAGE%)"
else
    echo "⚠️  Disk space: LOW ($DISK_USAGE%)"
fi

echo "===================================="
```

```bash
chmod +x /home/pi/health_check.sh
```

## 🎯 **Best Practices**

1. **Always test locally** before pushing to Git
2. **Use meaningful commit messages** for easy tracking
3. **Create tags for stable releases**
4. **Keep backup of working configurations**
5. **Monitor logs after deployment**
6. **Have rollback plan ready**

## ✅ **Success Criteria**

- [ ] Git repository accessible from Raspberry Pi
- [ ] Initial deployment successful
- [ ] Update workflow working
- [ ] Rollback procedure tested
- [ ] Health monitoring in place
- [ ] Both v1 and v3 systems working

---

**This Git-based deployment strategy provides easy updates, version control, and rollback capabilities for your solar heating system.**
