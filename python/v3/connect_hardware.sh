#!/bin/bash

# Solar Heating System v3 - Hardware Connection Script
# This script automates the process of connecting real hardware to the v3 system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if user is root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        error "This script should not be run as root"
        exit 1
    fi
}

# Function to check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if we're in the right directory
    if [[ ! -f "main_system.py" ]]; then
        error "Please run this script from the v3 directory (/home/pi/solar_heating/python/v3)"
        exit 1
    fi
    
    # Check if virtual environment exists
    if [[ ! -d "/opt/solar_heating_v3" ]]; then
        error "Virtual environment not found at /opt/solar_heating_v3"
        exit 1
    fi
    
    # Check if git is available
    if ! command_exists git; then
        error "Git is not installed. Please install git first."
        exit 1
    fi
    
    log "✅ Prerequisites check passed"
}

# Function to stop the service
stop_service() {
    log "Stopping solar_heating_v3 service..."
    if systemctl is-active --quiet solar_heating_v3.service; then
        sudo systemctl stop solar_heating_v3.service
        log "✅ Service stopped"
    else
        warn "Service was not running"
    fi
}

# Function to install hardware libraries
install_hardware_libraries() {
    log "Installing hardware libraries..."
    
    # Create temporary directory
    TEMP_DIR="/tmp/hardware_libs_$$"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Install megabas
    log "Installing megabas library..."
    if git clone https://github.com/SequentMicrosystems/megabas-rpi.git 2>/dev/null; then
        cd megabas-rpi
        if /opt/solar_heating_v3/bin/pip install -e . >/dev/null 2>&1; then
            log "✅ megabas installed successfully"
        else
            error "Failed to install megabas"
            return 1
        fi
        cd ..
    else
        error "Failed to clone megabas repository"
        return 1
    fi
    
    # Install librtd
    log "Installing librtd library..."
    if git clone https://github.com/SequentMicrosystems/rtd-rpi.git 2>/dev/null; then
        cd rtd-rpi
        if /opt/solar_heating_v3/bin/pip install -e . >/dev/null 2>&1; then
            log "✅ librtd installed successfully"
        else
            error "Failed to install librtd"
            return 1
        fi
        cd ..
    else
        error "Failed to clone librtd repository"
        return 1
    fi
    
    # Install lib4relind
    log "Installing lib4relind library..."
    if git clone https://github.com/SequentMicrosystems/4relind-rpi.git 2>/dev/null; then
        cd 4relind-rpi
        if /opt/solar_heating_v3/bin/pip install -e . >/dev/null 2>&1; then
            log "✅ lib4relind installed successfully"
        else
            error "Failed to install lib4relind"
            return 1
        fi
        cd ..
    else
        error "Failed to clone lib4relind repository"
        return 1
    fi
    
    # Clean up
    cd /home/pi/solar_heating/python/v3
    rm -rf "$TEMP_DIR"
    
    log "✅ All hardware libraries installed successfully"
}

# Function to configure I2C
configure_i2c() {
    log "Configuring I2C buses..."
    
    # Check I2C bus availability
    if [[ ! -e /dev/i2c-1 ]]; then
        warn "I2C bus 1 not found. Enabling I2C..."
        sudo raspi-config nonint do_i2c 0
        log "✅ I2C enabled"
    fi
    
    if [[ ! -e /dev/i2c-2 ]]; then
        warn "I2C bus 2 not found. This might be normal for some Pi models."
    fi
    
    # Set permissions
    if [[ -e /dev/i2c-1 ]]; then
        sudo chmod 666 /dev/i2c-1
        sudo chown root:i2c /dev/i2c-1
        log "✅ I2C bus 1 permissions configured"
    fi
    
    if [[ -e /dev/i2c-2 ]]; then
        sudo chmod 666 /dev/i2c-2
        sudo chown root:i2c /dev/i2c-2
        log "✅ I2C bus 2 permissions configured"
    fi
    
    # Add user to i2c group
    if ! groups $USER | grep -q i2c; then
        sudo usermod -a -G i2c $USER
        log "✅ Added user to i2c group"
    fi
    
    # Install i2c-tools if not available
    if ! command_exists i2cdetect; then
        log "Installing i2c-tools..."
        sudo apt update
        sudo apt install -y i2c-tools
    fi
}

# Function to test hardware detection
test_hardware_detection() {
    log "Testing hardware detection..."
    
    # Activate virtual environment
    source /opt/solar_heating_v3/bin/activate
    
    # Test MegaBAS on stack 3
    log "Testing MegaBAS on stack 3..."
    if python3 -c "import megabas; result = megabas.getRIn1K(3, 1); print(f'MegaBAS stack 3, input 1: {result}')" 2>/dev/null; then
        log "✅ MegaBAS detected on stack 3"
    else
        warn "MegaBAS not detected on stack 3"
    fi
    
    # Test RTD on stack 0
    log "Testing RTD on stack 0..."
    if python3 -c "import librtd; result = librtd.get(0, 1); print(f'RTD stack 0, sensor 1: {result}°C')" 2>/dev/null; then
        log "✅ RTD detected on stack 0"
    else
        warn "RTD not detected on stack 0"
    fi
    
    # Test 4RELIND on stack 2
    log "Testing 4RELIND on stack 2..."
    if python3 -c "import lib4relind; result = lib4relind.get_relay(2, 1); print(f'4RELIND stack 2, relay 1: {result}')" 2>/dev/null; then
        log "✅ 4RELIND detected on stack 2"
    else
        warn "4RELIND not detected on stack 2"
    fi
}

# Function to test hardware interface
test_hardware_interface() {
    log "Testing hardware interface..."
    
    # Activate virtual environment
    source /opt/solar_heating_v3/bin/activate
    
    # Test the hardware interface
    if python3 -c "
from hardware_interface import HardwareInterface
hw = HardwareInterface(simulation_mode=False)
print('Hardware interface initialized')
test_results = hw.test_hardware_connection()
print(f'Hardware test results: {test_results}')
" 2>/dev/null; then
        log "✅ Hardware interface test completed"
    else
        error "Hardware interface test failed"
        return 1
    fi
}

# Function to restart service
restart_service() {
    log "Restarting solar_heating_v3 service..."
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Start the service
    sudo systemctl start solar_heating_v3.service
    
    # Wait a moment for service to start
    sleep 3
    
    # Check service status
    if systemctl is-active --quiet solar_heating_v3.service; then
        log "✅ Service started successfully"
    else
        error "Service failed to start"
        sudo systemctl status solar_heating_v3.service
        return 1
    fi
}

# Function to verify hardware mode
verify_hardware_mode() {
    log "Verifying hardware mode..."
    
    # Wait a moment for logs to be written
    sleep 5
    
    # Check if system is running in hardware mode
    if grep -q "Hardware interface initialized in hardware mode" solar_heating_v3.log 2>/dev/null; then
        log "✅ System is running in hardware mode"
    else
        warn "System might still be in simulation mode"
        log "Recent log entries:"
        tail -10 solar_heating_v3.log 2>/dev/null || echo "No log file found"
    fi
    
    # Check for hardware test results
    if grep -q "Hardware test results" solar_heating_v3.log 2>/dev/null; then
        log "Hardware test results found in logs"
        grep "Hardware test results" solar_heating_v3.log | tail -1
    fi
}

# Function to display I2C bus information
display_i2c_info() {
    log "Displaying I2C bus information..."
    
    echo
    echo "=== I2C Bus Information ==="
    
    # List I2C buses
    echo "Available I2C buses:"
    ls -la /dev/i2c* 2>/dev/null || echo "No I2C buses found"
    
    echo
    echo "I2C bus detection:"
    if command_exists i2cdetect; then
        sudo i2cdetect -l 2>/dev/null || echo "i2cdetect failed"
    else
        echo "i2cdetect not available"
    fi
    
    echo
    echo "I2C bus 1 devices:"
    if [[ -e /dev/i2c-1 ]]; then
        sudo i2cdetect -y 1 2>/dev/null || echo "Failed to scan I2C bus 1"
    else
        echo "I2C bus 1 not available"
    fi
    
    echo
    echo "I2C bus 2 devices:"
    if [[ -e /dev/i2c-2 ]]; then
        sudo i2cdetect -y 2 2>/dev/null || echo "Failed to scan I2C bus 2"
    else
        echo "I2C bus 2 not available"
    fi
}

# Main execution
main() {
    echo "=== Solar Heating System v3 - Hardware Connection Script ==="
    echo "This script will connect real hardware to your v3 system"
    echo
    
    # Check if not running as root
    check_root
    
    # Check prerequisites
    check_prerequisites
    
    # Display I2C information before starting
    display_i2c_info
    
    echo
    echo "Press Enter to continue with hardware installation, or Ctrl+C to cancel..."
    read -r
    
    # Stop the service
    stop_service
    
    # Install hardware libraries
    if ! install_hardware_libraries; then
        error "Hardware library installation failed"
        exit 1
    fi
    
    # Configure I2C
    configure_i2c
    
    # Test hardware detection
    test_hardware_detection
    
    # Test hardware interface
    if ! test_hardware_interface; then
        error "Hardware interface test failed"
        exit 1
    fi
    
    # Restart service
    if ! restart_service; then
        error "Service restart failed"
        exit 1
    fi
    
    # Verify hardware mode
    verify_hardware_mode
    
    echo
    log "=== Hardware Connection Complete ==="
    log "Your v3 system should now be running with real hardware!"
    log "Use './monitor_v3.sh' to check system status"
    log "Use 'sudo journalctl -u solar_heating_v3.service -f' to watch logs"
    echo
    
    # Final status check
    echo "=== Final Status Check ==="
    sudo systemctl status solar_heating_v3.service --no-pager -l
}

# Run main function
main "$@"
