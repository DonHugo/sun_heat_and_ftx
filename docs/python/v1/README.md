# Solar Heating System v1

This folder contains the legacy v1 system files that have been superseded by the v3 system.

## ⚠️ **DEPRECATED - Use v3 Instead**

**All v1 functionality has been replaced by the v3 system. These files are kept for reference only.**

## 📁 **Files in this folder**

### **Core System Files**
- **`temperature_monitoring.py`** - Legacy v1 temperature monitoring system (42KB)
- **`system_switch.py`** - Legacy system switch control (5.5KB)
- **`temperature_monitoring.service`** - Systemd service file for v1 (1.1KB)

### **Service Scripts**
- **`fix_v1_service.sh`** - Script to fix v1 service issues (682B)

### **Update Scripts**
- **`update_solar_heating.sh`** - Legacy update script for v1 (3.0KB)

### **Documentation**
- **`ESSENTIAL_FILES_GUIDE.md`** - Guide to essential v1 files (3.9KB)
- **`notes.md`** - Development notes for v1 (1.1KB)

## 🔄 **Migration to v3**

All v1 functionality has been successfully migrated to the v3 system:

- ✅ **Temperature monitoring** → `python/v3/main_system.py`
- ✅ **MQTT communication** → `python/v3/mqtt_handler.py`
- ✅ **Hardware interface** → `python/v3/hardware_interface.py`
- ✅ **Configuration** → `python/v3/config.py`
- ✅ **Service management** → `python/v3/solar_heating_v3.service`

## 🚫 **Why v1 is Deprecated**

1. **Legacy sensors removed** - All 32 legacy sensors eliminated
2. **Better architecture** - v3 has cleaner, more maintainable code
3. **Enhanced features** - Real-time energy monitoring, better error handling
4. **Improved performance** - Single publishing system, reduced MQTT traffic
5. **Better documentation** - Comprehensive guides and examples

## 📊 **File Sizes**

- **Total v1 files**: 8 files
- **Total size**: ~58KB
- **Status**: DEPRECATED - Reference only

## 🎯 **Recommendation**

**Use the v3 system instead.** The v3 system provides:
- 100% backward compatibility
- Enhanced functionality
- Better performance
- Cleaner codebase
- Comprehensive documentation

For active development and deployment, see the `python/v3/` folder.
