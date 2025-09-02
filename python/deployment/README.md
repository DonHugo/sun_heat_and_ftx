# Deployment Scripts and Guides

This folder contains all deployment-related scripts and documentation for the Solar Heating System.

## 📁 **Files in this folder**

### **Main Deployment Scripts**
- **`deploy_to_pi.sh`** - Main Raspberry Pi deployment script (5.0KB)
- **`automated_deployment.sh`** - Automated deployment script (20KB)
- **`continue_deployment.sh`** - Continue interrupted deployment (2.8KB)
- **`test_automated_deployment.sh`** - Test deployment script (9.3KB)

### **Deployment Guides**
- **`AUTOMATED_DEPLOYMENT_GUIDE.md`** - Guide for automated deployment (6.3KB)
- **`FRESH_PI_DEPLOYMENT_STEPS.md`** - Steps for fresh Raspberry Pi setup (9.9KB)
- **`deployment_guide.md`** - General deployment guide (7.7KB)
- **`git_deployment_guide.md`** - Git-based deployment guide (8.4KB)
- **`GIT_DEPLOYMENT_QUICK_REFERENCE.md`** - Quick reference for git deployment (2.8KB)

### **Testing and Validation**
- **`TESTING_GUIDE.md`** - Guide for testing deployments (6.4KB)

## 🎯 **Primary Deployment Script**

**`deploy_to_pi.sh`** is the main deployment script that:
- Sets up the v3 system on Raspberry Pi
- Installs required packages
- Creates virtual environment
- Configures systemd service
- Sets up MQTT and hardware connections

## 🚀 **Quick Start**

1. **Copy deployment scripts to Raspberry Pi:**
   ```bash
   scp -r python/deployment/ pi@raspberrypi:/home/pi/
   ```

2. **Run main deployment:**
   ```bash
   ssh pi@raspberrypi
   cd deployment
   chmod +x deploy_to_pi.sh
   ./deploy_to_pi.sh
   ```

## 📊 **File Sizes**

- **Total deployment files**: 10 files
- **Total size**: ~78KB
- **Status**: ACTIVE - Use for Raspberry Pi deployment

## 🔧 **System Requirements**

- Raspberry Pi (tested on Pi 4)
- Python 3.7+
- Git
- Internet connection
- I2C enabled
- MQTT broker access

## 📚 **Documentation Order**

1. **`FRESH_PI_DEPLOYMENT_STEPS.md`** - For new Raspberry Pi setup
2. **`deploy_to_pi.sh`** - Main deployment script
3. **`AUTOMATED_DEPLOYMENT_GUIDE.md`** - For automated deployments
4. **`TESTING_GUIDE.md`** - For testing deployments
5. **`git_deployment_guide.md`** - For git-based deployments

## 🎯 **Current Status**

- **v1 system**: DEPRECATED (moved to `python/v1/`)
- **v2 system**: DEPRECATED (moved to `python/v2/`)
- **v3 system**: ACTIVE (in `python/v3/`)
- **Deployment scripts**: UPDATED for v3-only deployment
