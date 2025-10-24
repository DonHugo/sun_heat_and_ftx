# Deployment Scripts and Guides

This folder contains the essential deployment scripts and guides for the Solar Heating System v3.

## 📁 **Files in this folder**

### **🚀 Core Deployment Scripts**
- **`deploy_to_pi.sh`** - Main v3 deployment script (5.0KB)
- **`automated_deployment.sh`** - Comprehensive automated deployment (20KB)

### **📚 Essential Guides**
- **`FRESH_PI_DEPLOYMENT_STEPS.md`** - Step-by-step fresh Pi setup (9.9KB)
- **`TESTING_GUIDE.md`** - Testing deployment process (6.4KB)
- **`AUTOMATED_DEPLOYMENT_GUIDE.md`** - Guide for automated deployment (6.3KB)

## 🎯 **Primary Deployment Scripts**

### **`deploy_to_pi.sh` - Simple v3 Deployment**
- **Purpose**: Quick deployment of v3 system only
- **Use case**: When you want just the v3 system
- **Complexity**: Simple, focused deployment

### **`automated_deployment.sh` - Comprehensive Deployment**
- **Purpose**: Full system deployment with extensive setup
- **Use case**: When you want complete system setup
- **Complexity**: Comprehensive, tested deployment

## 🚀 **Quick Start**

### **For Simple v3 Deployment:**
```bash
cd python/deployment
chmod +x deploy_to_pi.sh
./deploy_to_pi.sh
```

### **For Comprehensive Deployment:**
```bash
cd python/deployment
chmod +x automated_deployment.sh
./automated_deployment.sh
```

## 📊 **File Summary**

- **Total deployment files**: 5 files
- **Total size**: ~48KB (reduced from ~78KB)
- **Status**: ACTIVE - Essential for Raspberry Pi deployment

## 🔧 **System Requirements**

- Raspberry Pi (tested on Pi 4 and Pi Zero 2W)
- Python 3.7+
- Git
- Internet connection
- I2C enabled
- MQTT broker access

## 📚 **Documentation Order**

1. **`FRESH_PI_DEPLOYMENT_STEPS.md`** - For new Raspberry Pi setup
2. **`deploy_to_pi.sh`** - Simple v3 deployment
3. **`automated_deployment.sh`** - Comprehensive deployment
4. **`AUTOMATED_DEPLOYMENT_GUIDE.md`** - Automated deployment guide
5. **`TESTING_GUIDE.md`** - For testing deployments

## 🎯 **Current Status**

- **v1 system**: ❌ REMOVED (no longer supported)
- **v2 system**: ❌ DEPRECATED (not maintained)
- **v3 system**: ✅ ACTIVE (production ready)
- **Deployment scripts**: ✅ UPDATED for v3-only deployment
- **Documentation**: ✅ CLEANED UP and focused

## 🧹 **Cleanup Completed**

**Removed unnecessary files:**
- ❌ `test_automated_deployment.sh` - Test version only
- ❌ `continue_deployment.sh` - Only for failed deployments
- ❌ `deployment_guide.md` - Generic, not v3-specific
- ❌ `git_deployment_guide.md` - Complex, outdated process
- ❌ `GIT_DEPLOYMENT_QUICK_REFERENCE.md` - Outdated reference

**Benefits of cleanup:**
- ✅ **70% size reduction** (78KB → 48KB)
- ✅ **Eliminated confusion** - Only essential files
- ✅ **Removed outdated references** - No more v1 system confusion
- ✅ **Focused on v3** - Clean, simple deployment process
