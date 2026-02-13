# Solar Heating System & TaskMaster AI

A comprehensive solar heating system with intelligent task management and real-time energy monitoring.

## 📋 **Product Requirements Document (PRD)**

**📄 [Complete PRD Documentation](docs/getting-started/PRD.md)** - Comprehensive 741-line Product Requirements Document  
**🎫 [GitHub Issue #23](https://github.com/DonHugo/sun_heat_and_ftx/issues/23)** - PRD Summary and Overview

### **Project Overview**
- **Name**: Sun Heat and FTX - Solar Heating System with AI Integration
- **Version**: 2.0
- **Status**: Active Development
- **Architecture**: Raspberry Pi + Sequent Microsystems hardware + TaskMaster AI

## 🏗️ **Project Structure**

```
/
├── 📚 docs/           - System documentation and Home Assistant configs
├── 🚀 python/         - Python implementation (v1, v2, v3, deployment)
├── ⚡ taskmaster/     - TaskMaster AI integration system
├── ⚙️ config/         - Configuration files and examples
├── 🏠 .vscode/        - VS Code development settings
├── 🖱️ .cursor/        - Cursor IDE settings
└── 🐍 .venv/          - Python virtual environment
```

## 🎯 **Quick Start**

### **Solar Heating System (v3 - Recommended):**
```bash
cd python/v3
source venv/bin/activate  # If virtual environment exists
python3 main_system.py
```

### **TaskMaster AI Integration:**
```bash
cd taskmaster
pip install -r ../config/requirements.txt
python taskmaster_demo.py
```

### **Deployment to Raspberry Pi:**
```bash
cd python/deployment
chmod +x deploy_to_pi.sh
./deploy_to_pi.sh
```

## 📚 **Documentation**

## 🤖 OpenCode Agents

This project uses unified OpenCode agents. See [`.opencode/README.md`](.opencode/README.md) for:
- Available agents and their capabilities
- How to invoke agents
- Project-specific usage patterns
- Link to comprehensive agent guide

### **🚀 Start Here (New Users)**
- **[Complete System Overview](docs/SYSTEM_OVERVIEW.md)** - Master guide to everything
- **[Component Map](docs/COMPONENT_MAP.md)** - Visual navigation guide
- **[Quick Start](docs/SYSTEM_OVERVIEW.md#quick-start-guide)** - Get running in 5 minutes

### **🔧 Component-Specific Guides**
- **System Setup**: See `docs/HOME_ASSISTANT_SETUP.md`
- **Real-time Energy**: See `docs/REALTIME_ENERGY_SENSOR_SETUP.md`
- **TaskMaster AI**: See `taskmaster/README_TASKMASTER.md`
- **Python Implementation**: See `python/README.md`
- **Deployment**: See `python/deployment/README.md`

### **📊 Advanced Features**
- **Rate of Change Sensors**: See `docs/RATE_OF_CHANGE_SENSORS_SUMMARY.md`
- **Monitoring Options**: See `docs/MONITORING_OPTIONS.md`
- **Watchdog System**: See `docs/WATCHDOG_SYSTEM.md`

## 🔧 **Hardware Requirements**

### **Sequent Microsystems Boards:**
- **RTD Data Acquisition**: Temperature sensors
- **Building Automation V4**: MegaBAS control
- **Four Relays + HV Inputs**: Relay control

### **Installation Commands:**
```bash
# RTD Data Acquisition
sudo apt-get install build-essential python-pip python-dev python-smbus git
git clone https://github.com/SequentMicrosystems/rtd-rpi.git
cd rtd-rpi/python/rtd/
sudo python3 setup.py install

# Building Automation V4
sudo apt-get install build-essential python3-pip python3-dev python3-smbus git
git clone https://github.com/SequentMicrosystems/megabas-rpi.git
cd megabas-rpi/python/
sudo python3 setup.py install

# Four Relays + HV Inputs
sudo apt-get install build-essential python3-pip python3-dev python3-smbus git
git clone https://github.com/SequentMicrosystems/4relind-rpi.git
cd 4relind-rpi/python/4relind/
sudo python3 setup.py install
```

## 📦 **Python Dependencies**

```bash
pip3 install statistics numpy paho-mqtt
```

## 🚀 **System Status**

- **v1 System**: ❌ DEPRECATED (moved to `python/v1/`)
- **v2 System**: ❌ DEPRECATED (moved to `python/v2/`)
- **v3 System**: ✅ ACTIVE (production ready)
- **TaskMaster AI**: ✅ ACTIVE (integrated)
- **Home Assistant**: ✅ FULLY INTEGRATED
- **Real-time Energy**: ✅ IMPLEMENTED

## 🔄 **Recent Updates**

- ✅ **Legacy sensors removed** (32 sensors eliminated)
- ✅ **Repository reorganized** (clear folder structure)
- ✅ **v3 system optimized** (clean, focused codebase)
- ✅ **Documentation updated** (comprehensive guides)
- ✅ **Deployment scripts** (organized and updated)

## 📖 **Getting Started**

1. **Read the documentation** in `docs/` folder
2. **Set up configuration** from `config/` examples
3. **Deploy v3 system** using `python/deployment/` scripts
4. **Configure Home Assistant** using `docs/` configurations
5. **Integrate TaskMaster AI** from `taskmaster/` folder

## 🆘 **Support**

- **Solar Heating**: See `python/v3/README.md`
- **TaskMaster AI**: See `taskmaster/README_TASKMASTER.md`
- **Deployment**: See `python/deployment/README.md`
- **Documentation**: See `docs/README.md`
