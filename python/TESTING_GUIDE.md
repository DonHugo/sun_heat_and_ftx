# Testing Guide for Automated Deployment Script

## 🧪 **How to Test the Automated Deployment Script**

Yes, you can test the automated deployment script! Here are several safe ways to test it.

## 🎯 **Testing Options**

### **Option 1: Test Script (Recommended)**
Use the dedicated test script that checks everything without making changes.

### **Option 2: Dry Run Mode**
Run the actual script with modifications to prevent changes.

### **Option 3: Virtual Machine Testing**
Test on a virtual Raspberry Pi environment.

## 🧪 **Option 1: Test Script (Safest)**

### **Run the Test Script:**
```bash
# On your Raspberry Pi
./test_automated_deployment.sh
```

### **What the Test Script Does:**
✅ **Checks system compatibility** without installing anything  
✅ **Tests repository access** without cloning  
✅ **Verifies MQTT connection** without configuring  
✅ **Checks hardware libraries** without installing  
✅ **Tests Python environment** without creating virtual environments  
✅ **Validates disk space** and network connectivity  
✅ **Shows what would happen** in real deployment  

### **Expected Output:**
```
🧪 Testing Automated Solar Heating System Deployment
====================================================
This script tests the deployment process without making changes
TEST MODE: No actual installation or configuration will be performed

Continue with deployment test? (y/N): y

[2025-08-22 18:30:00] TEST: Checking if running on Raspberry Pi...
[2025-08-22 18:30:01] ✅ Raspberry Pi detected
[2025-08-22 18:30:02] TEST: Testing system package availability...
[2025-08-22 18:30:03] ✅ apt package manager available
[2025-08-22 18:30:04] ✅ git available
[2025-08-22 18:30:05] ✅ python3 available
...
[2025-08-22 18:30:30] 🧪 AUTOMATED DEPLOYMENT TEST COMPLETED!
```

## 🔧 **Option 2: Dry Run Mode**

### **Modify the Script for Testing:**
```bash
# Create a test version of the automated script
cp automated_deployment.sh automated_deployment_test.sh

# Edit the test version
nano automated_deployment_test.sh
```

### **Add Dry Run Mode:**
Add this at the top of the script:
```bash
# Dry run mode - comment out actual commands
DRY_RUN=true

# Modify functions to show what would happen
update_system() {
    log "DRY RUN: Would update system packages..."
    if [ "$DRY_RUN" = true ]; then
        log "DRY RUN: sudo apt update && sudo apt upgrade -y"
        return 0
    fi
    sudo apt update && sudo apt upgrade -y
    log "✅ System updated"
}
```

### **Run Dry Run Version:**
```bash
./automated_deployment_test.sh
```

## 🖥️ **Option 3: Virtual Machine Testing**

### **Set up Virtual Raspberry Pi:**
```bash
# Install QEMU for Raspberry Pi emulation
sudo apt install qemu-system-arm

# Download Raspberry Pi OS image
wget https://downloads.raspberrypi.org/raspios_lite_armhf/images/raspios_lite_armhf-2023-05-03/2023-05-03-raspios-bullseye-armhf-lite.img.xz

# Extract the image
unxz 2023-05-03-raspios-bullseye-armhf-lite.img.xz

# Run virtual Raspberry Pi
qemu-system-arm -M versatilepb -cpu arm1176 -m 256 -drive file=2023-05-03-raspios-bullseye-armhf-lite.img,format=raw -net nic -net user -nographic
```

### **Test on Virtual Pi:**
```bash
# SSH into virtual Pi
ssh pi@localhost

# Run test script
./test_automated_deployment.sh
```

## 🧪 **Testing on Your Current System**

### **Test on macOS/Linux (Development Machine):**
```bash
# The test script will work on any system
./test_automated_deployment.sh
```

**Expected Results:**
- ✅ Most tests will pass
- ⚠️ Some tests will show warnings (expected on non-Pi systems)
- ℹ️ Hardware library tests will show "would be installed"

### **Test on Raspberry Pi (Target System):**
```bash
# Copy test script to Pi
scp test_automated_deployment.sh pi@your-pi-ip-address:~/

# SSH into Pi and run test
ssh pi@your-pi-ip-address
./test_automated_deployment.sh
```

**Expected Results:**
- ✅ All system tests should pass
- ✅ Hardware library tests will show current status
- ✅ MQTT connection will be tested
- ✅ Repository access will be verified

## 📊 **What the Tests Check**

### **System Compatibility:**
- ✅ Raspberry Pi detection
- ✅ Package manager availability
- ✅ Python environment
- ✅ Network connectivity

### **Hardware Requirements:**
- ✅ I2C interface status
- ✅ Hardware library availability
- ✅ Sensor detection

### **Software Requirements:**
- ✅ Git repository access
- ✅ MQTT broker connectivity
- ✅ Service management tools

### **Resource Requirements:**
- ✅ Disk space availability
- ✅ Memory requirements
- ✅ Network bandwidth

## 🚨 **Interpreting Test Results**

### **✅ All Tests Pass:**
```
🎯 Ready for deployment:
   If all tests passed, you can run the real deployment script:
   ./automated_deployment.sh
```

### **⚠️ Some Warnings:**
```
⚠️  If any tests failed, check the warnings above before proceeding.
```

**Common Warnings:**
- Hardware libraries not installed (normal on fresh Pi)
- MQTT connection failed (check broker settings)
- Repository not accessible (check URL)

### **❌ Critical Errors:**
```
❌ TEST ERROR: [specific error message]
```

**Critical errors to fix:**
- No internet connectivity
- No disk space
- Repository completely inaccessible

## 🔧 **Fixing Test Issues**

### **MQTT Connection Failed:**
```bash
# Check MQTT broker settings
nano test_automated_deployment.sh

# Update these lines:
MQTT_BROKER="192.168.0.110"
MQTT_USERNAME="mqtt_beaches"
MQTT_PASSWORD="uQX6NiZ.7R"
```

### **Repository Not Accessible:**
```bash
# Update repository URL
nano test_automated_deployment.sh

# Change this line:
REPO_URL="https://github.com/YOUR_ACTUAL_USERNAME/sun_heat_and_ftx.git"
```

### **Hardware Libraries Missing:**
```bash
# This is normal on a fresh Pi
# The real deployment script will install them
```

## 🎯 **Next Steps After Testing**

### **If Tests Pass:**
1. ✅ Run the real deployment script
2. ✅ Connect hardware
3. ✅ Test both v1 and v3 systems

### **If Tests Show Issues:**
1. 🔧 Fix the identified problems
2. 🔄 Run the test script again
3. ✅ Proceed with deployment when all tests pass

## 📋 **Testing Checklist**

- [ ] Test script runs without errors
- [ ] System compatibility verified
- [ ] Network connectivity confirmed
- [ ] Repository access working
- [ ] MQTT connection successful
- [ ] Hardware requirements checked
- [ ] Resource availability confirmed

---

**The test script gives you confidence that the deployment will work before running the actual installation!** 🎯
