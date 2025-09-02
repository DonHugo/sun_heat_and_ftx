# Changelog: Solar Heating System v3

## [Unreleased] - Latest Development

### 🔧 **Fixed**
- **Energy Calculation Bug**: Fixed unrealistic energy values (800+ kWh) in dashboard
  - **Root Cause**: Incorrect calculation multiplier (`* 35`) in stored energy calculation
  - **Solution**: Replaced arbitrary multiplier with proper physics calculations for 360L tank
  - **Result**: Energy values now show realistic range (0-36 kWh) based on actual tank volume
  - **Files Modified**: `python/v3/main_system.py`
  - **Documentation Updated**: USER_GUIDE, IMPLEMENTATION, and SUMMARY documents

### ✨ **Added**
- **Energy Range Validation**: System now validates energy calculations against realistic limits
- **Physics-Based Calculations**: Proper energy calculation using water mass, specific heat capacity, and temperature difference
- **Enhanced Logging**: Better energy calculation logging with validation warnings

### 📚 **Documentation**
- Updated USER_GUIDE_SOLAR_HEATING_V3.md with corrected energy calculation information
- Added energy calculation implementation details to IMPLEMENTATION_SOLAR_HEATING_V3.md
- Updated SUMMARY_SOLAR_HEATING_V3.md with recent fix information
- Created this CHANGELOG.md for tracking system changes

## [v3.0.0] - Initial Release

### ✨ **Features**
- Complete solar heating automation system
- Home Assistant integration with MQTT
- TaskMaster AI integration
- Comprehensive temperature monitoring
- Automated pump control
- Safety systems and emergency shutdown
- Watchdog system for reliability
- Docker containerization support

### 🔧 **Technical**
- Modular Python architecture
- Hardware abstraction layer
- Real-time monitoring and logging
- Configuration management
- Comprehensive error handling

---

**Note**: This changelog tracks significant changes to the Solar Heating System v3. For detailed implementation information, see the IMPLEMENTATION document.
