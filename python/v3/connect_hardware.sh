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

# Function to check if hardware libraries are already available
check_hardware_libraries() {
    log "Checking for existing hardware libraries..."
    
    # Activate virtual environment
    source /opt/solar_heating_v3/bin/activate
    
    local all_available=true
    
    # Check megabas
    if python3 -c "import megabas" 2>/dev/null; then
        log "✅ megabas library already available"
    else
        log "❌ megabas library not found"
        all_available=false
    fi
    
    # Check librtd
    if python3 -c "import librtd" 2>/dev/null; then
        log "✅ librtd library already available"
    else
        log "❌ librtd library not found"
        all_available=false
    fi
    
    # Check lib4relind
    if python3 -c "import lib4relind" 2>/dev/null; then
        log "✅ lib4relind library already available"
    else
        log "❌ lib4relind library not found"
        all_available=false
    fi
    
    if $all_available; then
        log "✅ All hardware libraries are already available!"
        return 0
    else
        log "⚠️ Some hardware libraries are missing"
        return 1
    fi
}

# Function to install hardware libraries with better error handling
install_hardware_libraries() {
    log "Installing hardware libraries..."
    
    # First check if libraries are already available
    if check_hardware_libraries; then
        log "✅ Hardware libraries already installed - skipping installation"
        return 0
    fi
    
    # Check if egg files exist in system packages
    log "Checking for system-installed egg files..."
    if [[ -f "/usr/local/lib/python3.11/dist-packages/smmegabas-1.0.3-py3.11.egg" ]] && \
       [[ -f "/usr/local/lib/python3.11/dist-packages/smrtd-1.0.3-py3.11.egg" ]] && \
       [[ -f "/usr/local/lib/python3.11/dist-packages/sm4relind-1.0.5-py3.11.egg" ]]; then
        
        log "Found system egg files - installing in virtual environment..."
        
        # Create temporary directory
        TEMP_DIR="/tmp/hardware_libs_$$"
        mkdir -p "$TEMP_DIR"
        cd "$TEMP_DIR"
        
        # Extract and install egg files
        log "Extracting and installing egg files..."
        
        # Extract megabas
        if unzip -q "/usr/local/lib/python3.11/dist-packages/smmegabas-1.0.3-py3.11.egg"; then
            if [[ -d "megabas" ]]; then
                cp -r megabas /opt/solar_heating_v3/lib/python3.11/site-packages/
                log "✅ megabas installed from egg file"
            else
                error "Failed to extract megabas from egg file"
                return 1
            fi
        else
            error "Failed to extract megabas egg file"
            return 1
        fi
        
        # Extract librtd
        if unzip -q "/usr/local/lib/python3.11/dist-packages/smrtd-1.0.3-py3.11.egg"; then
            if [[ -d "librtd" ]]; then
                cp -r librtd /opt/solar_heating_v3/lib/python3.11/site-packages/
                log "✅ librtd installed from egg file"
            else
                error "Failed to extract librtd from egg file"
                return 1
            fi
        else
            error "Failed to extract librtd egg file"
            return 1
        fi
        
        # Extract lib4relind
        if unzip -q "/usr/local/lib/python3.11/dist-packages/sm4relind-1.0.5-py3.11.egg"; then
            if [[ -d "lib4relind" ]]; then
                cp -r lib4relind /opt/solar_heating_v3/lib/python3.11/site-packages/
                log "✅ lib4relind installed from egg file"
            else
                error "Failed to extract lib4relind from egg file"
                return 1
            fi
        else
            error "Failed to extract lib4relind egg file"
            return 1
        fi
        
        # Clean up
        cd /home/pi/solar_heating/python/v3
        rm -rf "$TEMP_DIR"
        
        # Verify installation
        if check_hardware_libraries; then
            log "✅ All hardware libraries installed successfully from egg files"
            return 0
        else
            error "Failed to install libraries from egg files"
            return 1
        fi
    fi
    
    # Fallback to GitHub installation (original method)
    log "No system egg files found - trying GitHub installation..."
    
    # Create temporary directory
    TEMP_DIR="/tmp/hardware_libs_$$"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Try different repository URLs and installation methods
    install_megabas() {
        log "Installing megabas library..."
        
        # Try multiple repository URLs
        local repos=(
            "https://github.com/SequentMicrosystems/megabas-rpi.git"
            "https://github.com/SequentMicrosystems/megabas.git"
            "https://github.com/SequentMicrosystems/megabas-rpi"
        )
        
        for repo in "${repos[@]}"; do
            log "Trying repository: $repo"
            if git clone "$repo" megabas-temp 2>/dev/null; then
                cd megabas-temp
                
                # Try different installation methods
                if /opt/solar_heating_v3/bin/pip install -e . >/dev/null 2>&1; then
                    log "✅ megabas installed successfully"
                    cd ..
                    rm -rf megabas-temp
                    return 0
                elif /opt/solar_heating_v3/bin/pip install . >/dev/null 2>&1; then
                    log "✅ megabas installed successfully"
                    cd ..
                    rm -rf megabas-temp
                    return 0
                elif /opt/solar_heating_v3/bin/python3 setup.py install >/dev/null 2>&1; then
                    log "✅ megabas installed successfully"
                    cd ..
                    rm -rf megabas-temp
                    return 0
                else
                    cd ..
                    rm -rf megabas-temp
                    warn "Failed to install from $repo"
                fi
            else
                warn "Failed to clone $repo"
            fi
        done
        
        # If all methods fail, try manual installation
        log "Trying manual megabas installation..."
        if /opt/solar_heating_v3/bin/pip install megabas >/dev/null 2>&1; then
            log "✅ megabas installed via pip"
            return 0
        fi
        
        error "All megabas installation methods failed"
        return 1
    }
    
    install_librtd() {
        log "Installing librtd library..."
        
        # Try multiple repository URLs
        local repos=(
            "https://github.com/SequentMicrosystems/rtd-rpi.git"
            "https://github.com/SequentMicrosystems/rtd.git"
            "https://github.com/SequentMicrosystems/rtd-rpi"
        )
        
        for repo in "${repos[@]}"; do
            log "Trying repository: $repo"
            if git clone "$repo" rtd-temp 2>/dev/null; then
                cd rtd-temp
                
                # Try different installation methods
                if /opt/solar_heating_v3/bin/pip install -e . >/dev/null 2>&1; then
                    log "✅ librtd installed successfully"
                    cd ..
                    rm -rf rtd-temp
                    return 0
                elif /opt/solar_heating_v3/bin/pip install . >/dev/null 2>&1; then
                    log "✅ librtd installed successfully"
                    cd ..
                    rm -rf rtd-temp
                    return 0
                elif /opt/solar_heating_v3/bin/python3 setup.py install >/dev/null 2>&1; then
                    log "✅ librtd installed successfully"
                    cd ..
                    rm -rf rtd-temp
                    return 0
                else
                    cd ..
                    rm -rf rtd-temp
                    warn "Failed to install from $repo"
                fi
            else
                warn "Failed to clone $repo"
            fi
        done
        
        # If all methods fail, try manual installation
        log "Trying manual librtd installation..."
        if /opt/solar_heating_v3/bin/pip install librtd >/dev/null 2>&1; then
            log "✅ librtd installed via pip"
            return 0
        fi
        
        error "All librtd installation methods failed"
        return 1
    }
    
    install_lib4relind() {
        log "Installing lib4relind library..."
        
        # Try multiple repository URLs
        local repos=(
            "https://github.com/SequentMicrosystems/4relind-rpi.git"
            "https://github.com/SequentMicrosystems/4relind.git"
            "https://github.com/SequentMicrosystems/4relind-rpi"
        )
        
        for repo in "${repos[@]}"; do
            log "Trying repository: $repo"
            if git clone "$repo" 4relind-temp 2>/dev/null; then
                cd 4relind-temp
                
                # Try different installation methods
                if /opt/solar_heating_v3/bin/pip install -e . >/dev/null 2>&1; then
                    log "✅ lib4relind installed successfully"
                    cd ..
                    rm -rf 4relind-temp
                    return 0
                elif /opt/solar_heating_v3/bin/pip install . >/dev/null 2>&1; then
                    log "✅ lib4relind installed successfully"
                    cd ..
                    rm -rf 4relind-temp
                    return 0
                elif /opt/solar_heating_v3/bin/python3 setup.py install >/dev/null 2>&1; then
                    log "✅ lib4relind installed successfully"
                    cd ..
                    rm -rf 4relind-temp
                    return 0
                else
                    cd ..
                    rm -rf 4relind-temp
                    warn "Failed to install from $repo"
                fi
            else
                warn "Failed to clone $repo"
            fi
        done
        
        # If all methods fail, try manual installation
        log "Trying manual lib4relind installation..."
        if /opt/solar_heating_v3/bin/pip install lib4relind >/dev/null 2>&1; then
            log "✅ lib4relind installed via pip"
            return 0
        fi
        
        error "All lib4relind installation methods failed"
        return 1
    }
    
    # Install each library
    if ! install_megabas; then
        return 1
    fi
    
    if ! install_librtd; then
        return 1
    fi
    
    if ! install_lib4relind; then
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
        echo
        echo "Troubleshooting tips:"
        echo "1. Check internet connection"
        echo "2. Try manual installation:"
        echo "   source /opt/solar_heating_v3/bin/activate"
        echo "   pip install megabas librtd lib4relind"
        echo "3. Check if hardware libraries are available from Sequent Microsystems"
        echo "4. Try installing from source:"
        echo "   git clone https://github.com/SequentMicrosystems/[library-name].git"
        echo "   cd [library-name] && python3 setup.py install"
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
