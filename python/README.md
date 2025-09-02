# Solar Heating System - Python Implementation

This directory contains the Python implementation of the Solar Heating System, organized by version and purpose.

## 📁 **Directory Structure**

### **🟢 v3/ - ACTIVE SYSTEM (Recommended)**
- **Status**: Production-ready, actively maintained
- **Features**: Real-time energy monitoring, enhanced MQTT, clean architecture
- **Size**: ~150KB (core files only)
- **Use**: **Use this for all new deployments and development**

### **🔴 v1/ - DEPRECATED SYSTEM**
- **Status**: Legacy system, superseded by v3
- **Features**: Basic temperature monitoring, legacy sensors
- **Size**: ~58KB
- **Use**: Reference only - all functionality migrated to v3

### **🟡 v2/ - DEPRECATED SYSTEM**
- **Status**: Legacy system, superseded by v3
- **Features**: Intermediate version, not fully developed
- **Size**: ~40KB
- **Use**: Reference only - all functionality migrated to v3

### **🚀 deployment/ - DEPLOYMENT SCRIPTS**
- **Status**: Active, updated for v3 deployment
- **Features**: Raspberry Pi deployment, automated setup, guides
- **Size**: ~78KB
- **Use**: **Use this for deploying v3 to Raspberry Pi**

## 🎯 **Quick Start**

### **For Development:**
```bash
cd python/v3
source venv/bin/activate  # If virtual environment exists
python3 main_system.py
```

### **For Deployment:**
```bash
cd python/deployment
chmod +x deploy_to_pi.sh
./deploy_to_pi.sh
```

## 📊 **System Comparison**

| Feature | v1 | v2 | v3 |
|---------|----|----|----|
| **Status** | ❌ Deprecated | ❌ Deprecated | ✅ Active |
| **Legacy Sensors** | ❌ 32 sensors | ❌ 32 sensors | ✅ 0 sensors |
| **Real-time Energy** | ❌ No | ❌ No | ✅ Yes |
| **Code Quality** | ❌ Legacy | ❌ Legacy | ✅ Modern |
| **Documentation** | ❌ Basic | ❌ Basic | ✅ Comprehensive |
| **Maintenance** | ❌ No updates | ❌ No updates | ✅ Active |

## 🔄 **Migration Path**

- **v1 → v3**: ✅ Complete (all functionality migrated)
- **v2 → v3**: ✅ Complete (all functionality migrated)
- **Legacy sensors**: ✅ Removed (32 sensors eliminated)

## 🚫 **What's Been Removed**

1. **Legacy sensors**: All 32 v1/v2 sensors removed
2. **Node-RED flows**: Legacy flows removed
3. **Duplicate files**: Redundant versions cleaned up
4. **Test files**: Development-only files removed
5. **System files**: Cache, logs, virtual environments removed

## 🎯 **Recommendation**

**Use v3 for everything:**
- ✅ **100% backward compatibility**
- ✅ **Enhanced functionality**
- ✅ **Better performance**
- ✅ **Cleaner codebase**
- ✅ **Comprehensive documentation**

## 📚 **Documentation**

- **v3 System**: See `python/v3/README.md`
- **Deployment**: See `python/deployment/README.md`
- **Legacy Systems**: See `python/v1/README.md` and `python/v2/README.md`

## 🔧 **Maintenance**

- **v3**: Actively maintained and updated
- **v1/v2**: Archived for reference only
- **Deployment**: Updated for v3-only deployment
- **Cleanup**: Regular cleanup scripts available
