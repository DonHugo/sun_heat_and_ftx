# Solar Heating System v3 - Test Suite

Comprehensive test suite for validating all system functionality and ensuring reliability after changes.

## 🎯 **Overview**

This test suite provides multiple levels of testing for the Solar Heating System v3:

- **System Verification** - Quick checks to ensure system is ready
- **Simulation Tests** - Full logic testing without hardware (development/CI)
- **Hardware Tests** - Real hardware testing on Raspberry Pi
- **Quick Tests** - Essential functionality tests for development
- **Comprehensive Tests** - Full test suite covering all features
- **Category Tests** - Specific test categories for targeted testing

## 🔍 **Environment Detection**

The test suite automatically detects your environment and runs the appropriate tests:

- **Simulation Environment**: Development machine, CI/CD, no hardware
- **Hardware Environment**: Raspberry Pi with actual hardware components

## 📁 **Test Files**

### **Core Test Files**
- **`test.py`** - Simple test runner (recommended)
- **`verify_system.py`** - System verification script (run first)
- **`simulation_test_suite.py`** - Simulation environment tests
- **`hardware_test_suite.py`** - Hardware environment tests
- **`quick_test_runner.py`** - Quick essential tests
- **`comprehensive_test_suite.py`** - Full comprehensive test suite
- **`run_tests.py`** - Main test runner with options
- **`detect_environment.py`** - Environment detection
- **`test_config.py`** - Test configuration and data
- **`test_manual_controls.py`** - Manual control verification

### **Test Categories**
- **Hardware Interface** - Sensor reading, relay control, error handling
- **Control Logic** - Pump control, emergency stops, hysteresis
- **MQTT Integration** - Publishing, subscribing, Home Assistant
- **State Management** - Persistence, midnight reset, energy tracking
- **Mode System** - Auto, manual, eco, collector cooling modes
- **TaskMaster AI** - AI integration and task processing
- **Integration** - Full system integration tests

## 🚀 **Quick Start**

### **1. Simple Test Runner (Recommended)**
```bash
cd /home/pi/solar_heating/python/v3

# Auto-detect environment and run appropriate tests
python3 test.py

# Force simulation tests (development machine)
python3 test.py --simulation

# Force hardware tests (Raspberry Pi)
python3 test.py --hardware

# Run quick tests only
python3 test.py --quick

# Run system verification only
python3 test.py --verify
```

### **2. System Verification (Run First)**
```bash
python3 verify_system.py
```

### **3. Environment Detection**
```bash
# Check what environment is detected
python3 detect_environment.py
```

### **4. Simulation Tests (Development/CI)**
```bash
# Run simulation tests (no hardware required)
python3 simulation_test_suite.py

# Or use the test runner
python3 run_tests.py --simulation
```

### **5. Hardware Tests (Raspberry Pi)**
```bash
# Run hardware tests (requires actual hardware)
python3 hardware_test_suite.py

# Or use the test runner
python3 run_tests.py --hardware
```

### **6. Advanced Test Runner**
```bash
# Auto-detect environment
python3 run_tests.py

# Run specific test suites
python3 run_tests.py --simulation
python3 run_tests.py --hardware
python3 run_tests.py --comprehensive

# Run with reports
python3 run_tests.py --simulation --report
python3 run_tests.py --hardware --report

# Run in CI mode
python3 run_tests.py --ci --auto
```

## 🧪 **Test Categories**

### **Simulation Tests (No Hardware Required)**
- **Control Logic** - All control algorithms and logic
- **State Management** - Persistence, midnight reset, energy calculations
- **Mode System** - Mode transitions and reasoning
- **TaskMaster AI** - AI integration and task processing
- **Error Handling** - Software error handling and recovery
- **Configuration** - Configuration validation and management

### **Hardware Tests (Requires Actual Hardware)**
- **Real Sensor Readings** - Actual temperature sensor accuracy and stability
- **Relay Control** - Real relay switching and feedback
- **Hardware Error Handling** - Physical hardware error conditions
- **Performance Testing** - Real-time performance and timing
- **MQTT Integration** - Real MQTT broker communication
- **Home Assistant Integration** - Actual device integration
- **System Service** - Service functionality and logs

### **Hardware Interface Tests**
- Hardware initialization (simulation and hardware modes)
- Temperature sensor reading (RTD and MegaBAS)
- Relay control (ON/OFF, state reading)
- Error handling (invalid sensors, relays)

### **Control Logic Tests**
- Control parameter initialization
- Emergency stop logic with hysteresis
- Collector cooling logic with hysteresis
- Pump control logic (start/stop conditions)
- Temperature difference calculations

### **MQTT Integration Tests**
- MQTT connection establishment
- Message publishing and subscription
- Home Assistant integration
- Topic structure validation

### **State Management Tests**
- State persistence (save/load)
- Midnight reset logic
- Energy tracking calculations
- Data validation and integrity

### **Mode System Tests**
- Mode initialization and transitions
- Manual control mode
- Mode reasoning and explanations
- System state updates

### **TaskMaster AI Integration Tests**
- TaskMaster service initialization
- Task creation and processing
- AI integration functionality
- Task priority and execution

### **Integration Tests**
- Full system component interaction
- End-to-end workflow validation
- Hardware-software integration
- Real-time operation simulation

## 📊 **Test Results**

### **Test Output Format**
```
🚀 Running Quick Tests
==================================================
🔧 Testing Hardware Interface...
✅ PASS - Hardware Initialization (0.05s)
✅ PASS - Temperature Reading (0.02s)
✅ PASS - Relay Control (0.03s)

📊 QUICK TEST SUMMARY
==================================================
Total Tests: 15
Passed: 15 ✅
Failed: 0 ❌
Success Rate: 100.0%
Duration: 2.34 seconds

🎉 ALL TESTS PASSED! System is ready.
```

### **Test Reports**
When using `--report` option, detailed JSON reports are generated:
```bash
python3 run_tests.py --comprehensive --report
# Generates: /tmp/solar_heating_tests/solar_heating_test_report_YYYYMMDD_HHMMSS.json
```

## 🔧 **Configuration**

### **Test Configuration**
Edit `test_config.py` to customize:
- Test categories and scenarios
- Test data and expected results
- Output settings and report formats
- Validation thresholds and limits

### **Environment Variables**
```bash
# Test environment
export SOLAR_HEATING_TEST_MODE=true
export SOLAR_HEATING_SIMULATION_MODE=true
export SOLAR_HEATING_LOG_LEVEL=INFO
```

## 🚨 **Troubleshooting**

### **Common Issues**

#### **Import Errors**
```bash
# Error: Module not found
# Solution: Run from v3 directory
cd /home/pi/solar_heating/python/v3
python3 verify_system.py
```

#### **MQTT Connection Failed**
```bash
# Error: MQTT connection failed
# Solution: Check MQTT broker is running
sudo systemctl status mosquitto
sudo systemctl start mosquitto
```

#### **Hardware Interface Errors**
```bash
# Error: Hardware libraries not found
# Solution: Install Sequent Microsystems libraries
# See README.md for installation instructions
```

#### **Permission Errors**
```bash
# Error: Permission denied
# Solution: Check file permissions
chmod +x *.py
sudo chown pi:pi *.py
```

### **Test Debugging**

#### **Verbose Output**
```bash
python3 run_tests.py --verbose --category hardware
```

#### **Specific Test Debugging**
```bash
# Run individual test functions
python3 -c "
from comprehensive_test_suite import ComprehensiveTestSuite
suite = ComprehensiveTestSuite()
suite.test_hardware_interface_initialization(TestResult('test'))
"
```

## 🔄 **Continuous Integration**

### **GitHub Actions Example**
```yaml
name: Solar Heating System Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: |
          cd python/v3
          pip install -r requirements.txt
      - name: Run tests
        run: |
          cd python/v3
          python3 run_tests.py --ci --category all
```

### **Local CI Script**
```bash
#!/bin/bash
# ci_test.sh
cd /home/pi/solar_heating/python/v3
python3 verify_system.py
python3 run_tests.py --ci --category all --report
```

## 📈 **Performance Metrics**

### **Test Execution Times**
- **System Verification**: ~5 seconds
- **Quick Tests**: ~10-30 seconds
- **Comprehensive Tests**: ~2-5 minutes
- **Full Test Suite**: ~5-10 minutes

### **Resource Usage**
- **Memory**: ~50-100MB during tests
- **CPU**: Moderate usage during simulation
- **Disk**: ~1-10MB for logs and reports

## 🎯 **Best Practices**

### **Before Making Changes**
1. Run system verification: `python3 verify_system.py`
2. Run quick tests: `python3 quick_test_runner.py`
3. Make your changes
4. Run tests again to verify

### **After Making Changes**
1. Run comprehensive tests: `python3 run_tests.py --comprehensive`
2. Check test reports for any regressions
3. Fix any failing tests
4. Re-run tests until all pass

### **Regular Testing**
- Run quick tests daily during development
- Run comprehensive tests before releases
- Run full test suite weekly
- Monitor test performance and reliability

## 📚 **Additional Resources**

- **Main System Documentation**: `README.md`
- **Configuration Guide**: `config.py`
- **Hardware Setup**: `HARDWARE_SETUP.md`
- **Home Assistant Integration**: `HOME_ASSISTANT_SETUP.md`
- **TaskMaster AI**: `TASKMASTER_INTEGRATION.md`

## 🆘 **Support**

If you encounter issues with the test suite:

1. **Check the logs** in `/home/pi/solar_heating/logs/`
2. **Run system verification** first: `python3 verify_system.py`
3. **Check configuration** in `config.py`
4. **Review test output** for specific error messages
5. **Check hardware connections** if hardware tests fail

---

**Remember**: Always run tests after making changes to ensure system reliability and functionality! 🧪✅
