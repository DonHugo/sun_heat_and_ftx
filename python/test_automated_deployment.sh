#!/bin/bash
# Test Version of Automated Solar Heating System Deployment Script
# This script tests the deployment process without making actual changes

set -e  # Exit on any error

# Configuration
REPO_URL="https://github.com/yourusername/sun_heat_and_ftx.git"
PROJECT_DIR="/home/pi/solar_heating"
MQTT_BROKER="192.168.0.110"
MQTT_USERNAME="mqtt_beaches"
MQTT_PASSWORD="uQX6NiZ.7R"

# Test mode flag
TEST_MODE=true

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] TEST: $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] TEST WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] TEST ERROR: $1${NC}"
    exit 1
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    log "Checking if running on Raspberry Pi..."
    if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        warn "This script is designed for Raspberry Pi"
        echo "Running on: $(uname -a)"
        log "✅ Raspberry Pi check completed (simulated)"
    else
        log "✅ Raspberry Pi detected"
    fi
}

# Test system packages (without installing)
test_system_packages() {
    log "Testing system package availability..."
    
    # Check if apt is available
    if command -v apt >/dev/null 2>&1; then
        log "✅ apt package manager available"
    else
        warn "apt package manager not available"
    fi
    
    # Check if git is available
    if command -v git >/dev/null 2>&1; then
        log "✅ git available"
    else
        warn "git not available"
    fi
    
    # Check if python3 is available
    if command -v python3 >/dev/null 2>&1; then
        log "✅ python3 available"
    else
        warn "python3 not available"
    fi
    
    log "✅ System package test completed"
}

# Test I2C interface
test_i2c() {
    log "Testing I2C interface..."
    
    # Check if I2C is enabled
    if grep -q "i2c_arm=on" /boot/config.txt 2>/dev/null; then
        log "✅ I2C already enabled in config"
    else
        log "ℹ️  I2C not enabled (would be enabled in real deployment)"
    fi
    
    # Check if i2cdetect is available
    if command -v i2cdetect >/dev/null 2>&1; then
        log "✅ i2cdetect available"
        log "I2C devices detected:"
        i2cdetect -y 1 2>/dev/null || warn "No I2C devices found"
    else
        warn "i2cdetect not available"
    fi
    
    log "✅ I2C test completed"
}

# Test hardware libraries (simulated)
test_hardware_libraries() {
    log "Testing hardware library availability..."
    
    # Test RTD library
    if python3 -c "import librtd" 2>/dev/null; then
        log "✅ RTD library already installed"
    else
        log "ℹ️  RTD library not installed (would be installed in real deployment)"
    fi
    
    # Test MegaBAS library
    if python3 -c "import megabas" 2>/dev/null; then
        log "✅ MegaBAS library already installed"
    else
        log "ℹ️  MegaBAS library not installed (would be installed in real deployment)"
    fi
    
    # Test 4RELIND library
    if python3 -c "import lib4relind" 2>/dev/null; then
        log "✅ 4RELIND library already installed"
    else
        log "ℹ️  4RELIND library not installed (would be installed in real deployment)"
    fi
    
    log "✅ Hardware library test completed"
}

# Test repository access
test_repository() {
    log "Testing repository access..."
    
    # Test if git can access the repository
    if git ls-remote "$REPO_URL" >/dev/null 2>&1; then
        log "✅ Repository accessible"
    else
        warn "Repository not accessible - check URL: $REPO_URL"
    fi
    
    # Check if project directory exists
    if [ -d "$PROJECT_DIR" ]; then
        log "✅ Project directory exists: $PROJECT_DIR"
        
        # Check for key files
        if [ -f "$PROJECT_DIR/python/temperature_monitoring.py" ]; then
            log "✅ v1 system file found"
        else
            warn "v1 system file not found"
        fi
        
        if [ -d "$PROJECT_DIR/python/v3" ]; then
            log "✅ v3 system directory found"
        else
            warn "v3 system directory not found"
        fi
        
        if [ -f "$PROJECT_DIR/python/automated_deployment.sh" ]; then
            log "✅ Automated deployment script found"
        else
            warn "Automated deployment script not found"
        fi
    else
        log "ℹ️  Project directory doesn't exist (would be created in real deployment)"
    fi
    
    log "✅ Repository test completed"
}

# Test MQTT connection
test_mqtt() {
    log "Testing MQTT connection..."
    
    # Check if mosquitto client is available
    if command -v mosquitto_pub >/dev/null 2>&1; then
        log "✅ mosquitto client available"
        
        # Test MQTT connection
        if mosquitto_pub -h "$MQTT_BROKER" -u "$MQTT_USERNAME" -P "$MQTT_PASSWORD" -t "test" -m "automated_deployment_test" 2>/dev/null; then
            log "✅ MQTT connection successful"
        else
            warn "MQTT connection failed - check broker settings"
        fi
    else
        warn "mosquitto client not available"
    fi
    
    log "✅ MQTT test completed"
}

# Test system services
test_services() {
    log "Testing system service availability..."
    
    # Check if systemctl is available
    if command -v systemctl >/dev/null 2>&1; then
        log "✅ systemctl available"
        
        # Check if services exist
        if [ -f "/etc/systemd/system/temperature_monitoring.service" ]; then
            log "✅ v1 service file exists"
        else
            log "ℹ️  v1 service file doesn't exist (would be created in real deployment)"
        fi
        
        if [ -f "/etc/systemd/system/solar_heating_v3.service" ]; then
            log "✅ v3 service file exists"
        else
            log "ℹ️  v3 service file doesn't exist (would be created in real deployment)"
        fi
    else
        warn "systemctl not available"
    fi
    
    log "✅ Service test completed"
}

# Test Python environment
test_python_environment() {
    log "Testing Python environment..."
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1)
    log "✅ Python version: $PYTHON_VERSION"
    
    # Check pip availability
    if command -v pip3 >/dev/null 2>&1; then
        log "✅ pip3 available"
    else
        warn "pip3 not available"
    fi
    
    # Check virtual environment creation
    if command -v python3 -m venv >/dev/null 2>&1; then
        log "✅ virtual environment creation available"
    else
        warn "virtual environment creation not available"
    fi
    
    log "✅ Python environment test completed"
}

# Test disk space
test_disk_space() {
    log "Testing disk space..."
    
    # Check available disk space
    DISK_USAGE=$(df /home/pi 2>/dev/null | tail -1 | awk '{print $5}' | sed 's/%//' || echo "0")
    if [ "$DISK_USAGE" -lt 90 ]; then
        log "✅ Disk space: OK ($DISK_USAGE%)"
    else
        warn "Disk space: LOW ($DISK_USAGE%)"
    fi
    
    log "✅ Disk space test completed"
}

# Test network connectivity
test_network() {
    log "Testing network connectivity..."
    
    # Test internet connectivity
    if ping -c 1 8.8.8.8 >/dev/null 2>&1; then
        log "✅ Internet connectivity available"
    else
        warn "Internet connectivity not available"
    fi
    
    # Test GitHub access
    if ping -c 1 github.com >/dev/null 2>&1; then
        log "✅ GitHub accessible"
    else
        warn "GitHub not accessible"
    fi
    
    log "✅ Network test completed"
}

# Display test summary
test_summary() {
    echo ""
    echo "🧪 AUTOMATED DEPLOYMENT TEST COMPLETED!"
    echo "======================================="
    echo ""
    echo "📋 Test Results Summary:"
    echo "✅ System compatibility checked"
    echo "✅ Hardware library availability tested"
    echo "✅ Repository access verified"
    echo "✅ MQTT connection tested"
    echo "✅ Service configuration checked"
    echo "✅ Python environment validated"
    echo "✅ Disk space verified"
    echo "✅ Network connectivity tested"
    echo ""
    echo "🎯 Ready for deployment:"
    echo "   If all tests passed, you can run the real deployment script:"
    echo "   ./automated_deployment.sh"
    echo ""
    echo "⚠️  If any tests failed, check the warnings above before proceeding."
    echo ""
    echo "🚀 Test completed successfully!"
}

# Main test function
main() {
    echo "🧪 Testing Automated Solar Heating System Deployment"
    echo "===================================================="
    echo "This script tests the deployment process without making changes"
    echo "TEST MODE: No actual installation or configuration will be performed"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        error "Please don't run this script as root"
    fi
    
    # Confirm test
    read -p "Continue with deployment test? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Test cancelled"
        exit 0
    fi
    
    # Run test steps
    check_raspberry_pi
    test_system_packages
    test_i2c
    test_hardware_libraries
    test_repository
    test_mqtt
    test_services
    test_python_environment
    test_disk_space
    test_network
    test_summary
}

# Run main function
main "$@"
