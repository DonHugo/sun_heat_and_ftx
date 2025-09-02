#!/bin/bash
# Automated Solar Heating System Deployment Script
# For Fresh Raspberry Pi Zero 2W Setup
# This script automates the entire deployment process

set -e  # Exit on any error

# Configuration
REPO_URL="https://github.com/DonHugo/sun_heat_and_ftx.git"
PROJECT_DIR="/home/pi/solar_heating"
MQTT_BROKER="192.168.0.110"
MQTT_USERNAME="mqtt_beaches"
MQTT_PASSWORD="uQX6NiZ.7R"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging function
log() {
    if [ -n "$START_TIME" ]; then
        CURRENT_TIME=$(date +%s)
        ELAPSED=$((CURRENT_TIME - START_TIME))
        ELAPSED_MIN=$((ELAPSED / 60))
        ELAPSED_SEC=$((ELAPSED % 60))
        echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] [${ELAPSED_MIN}m${ELAPSED_SEC}s] $1${NC}"
    else
        echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
    fi
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

# Check if running on Raspberry Pi
check_raspberry_pi() {
    log "Checking if running on Raspberry Pi..."
    if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        warn "This script is designed for Raspberry Pi"
        echo "Running on: $(uname -a)"
        read -p "Continue anyway? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
    log "✅ Raspberry Pi detected"
}

# Update system packages
update_system() {
    log "Updating system packages..."
    sudo apt update && sudo DEBIAN_FRONTEND=noninteractive apt upgrade -y
    log "✅ System updated"
}

# Install essential packages
install_essentials() {
    log "Installing essential packages..."
    sudo apt install -y git curl wget htop vim build-essential python3-pip python3-dev python3-smbus mosquitto-clients
    
    # Install Python dependencies for v1 system (global environment)
    log "Installing Python dependencies for v1 system..."
    sudo apt install -y python3-paho-mqtt python3-numpy
    
    log "✅ Essential packages installed"
}

# Enable I2C interface
enable_i2c() {
    log "Enabling I2C interface..."
    
    # Check if I2C is already enabled
    if grep -q "i2c_arm=on" /boot/config.txt; then
        log "✅ I2C already enabled"
    else
        # Enable I2C
        echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
        log "✅ I2C enabled (reboot required)"
    fi
    
    # Configure I2C permissions and ensure both buses are available
    log "Configuring I2C permissions..."
    
    # Add user to i2c group if not already added
    if ! groups $USER | grep -q i2c; then
        sudo usermod -a -G i2c $USER
        log "✅ Added user to i2c group"
    fi
    
    # Ensure I2C devices exist and have correct permissions
    if [ -e /dev/i2c-1 ]; then
        sudo chmod 666 /dev/i2c-1
        sudo chown root:i2c /dev/i2c-1
        log "✅ I2C bus 1 permissions configured"
    fi
    
    if [ -e /dev/i2c-2 ]; then
        sudo chmod 666 /dev/i2c-2
        sudo chown root:i2c /dev/i2c-2
        log "✅ I2C bus 2 permissions configured"
    fi
    
    # Test I2C bus detection
    log "Testing I2C bus detection..."
    if command -v i2cdetect >/dev/null 2>&1; then
        if sudo i2cdetect -l >/dev/null 2>&1; then
            log "✅ I2C bus detection working"
        else
            warn "I2C bus detection failed - may need reboot"
        fi
    else
        warn "i2cdetect not available - installing i2c-tools"
        sudo apt install -y i2c-tools
    fi
}

# Install Sequent Microsystems libraries
install_hardware_libraries() {
    log "Installing Sequent Microsystems libraries..."
    
    # Create temporary directory
    TEMP_DIR="/tmp/solar_heating_install"
    rm -rf "$TEMP_DIR"  # Clean up any existing directory
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Install RTD Data Acquisition
    log "Installing RTD Data Acquisition..."
    if git clone https://github.com/SequentMicrosystems/rtd-rpi.git; then
        cd rtd-rpi/python/
        sudo python3 setup.py install
        cd "$TEMP_DIR"
        log "✅ RTD Data Acquisition installed"
    else
        warn "Failed to clone RTD repository"
    fi
    
    # Install Building Automation V4 (MegaBAS)
    log "Installing Building Automation V4 (MegaBAS)..."
    if git clone https://github.com/SequentMicrosystems/megabas-rpi.git; then
        cd megabas-rpi/python/
        sudo python3 setup.py install
        cd "$TEMP_DIR"
        log "✅ MegaBAS installed"
    else
        warn "Failed to clone MegaBAS repository"
    fi
    
    # Install Four Relays four HV Inputs
    log "Installing Four Relays four HV Inputs..."
    if git clone https://github.com/SequentMicrosystems/4relind-rpi.git; then
        cd 4relind-rpi/python/
        sudo python3 setup.py install
        cd "$TEMP_DIR"
        log "✅ 4RELIND installed"
    else
        warn "Failed to clone 4RELIND repository"
    fi
    
    # Clean up
    cd ~
    sudo rm -rf "$TEMP_DIR"
    
    log "✅ Hardware libraries installed"
}

# Verify hardware libraries
verify_hardware_libraries() {
    log "Verifying hardware libraries..."
    
    # Test RTD library
    if python3 -c "import librtd; print('RTD library OK')" 2>/dev/null; then
        log "✅ RTD library verified"
    else
        error "RTD library verification failed"
    fi
    
    # Test MegaBAS library
    if python3 -c "import megabas; print('MegaBAS library OK')" 2>/dev/null; then
        log "✅ MegaBAS library verified"
    else
        error "MegaBAS library verification failed"
    fi
    
    # Test 4RELIND library
    if python3 -c "import lib4relind; print('4RELIND library OK')" 2>/dev/null; then
        log "✅ 4RELIND library verified"
    else
        error "4RELIND library verification failed"
    fi
}

# Verify v1 system dependencies
verify_v1_dependencies() {
    log "Verifying v1 system dependencies..."
    
    # Test MQTT library
    if python3 -c "from paho.mqtt import client as mqtt_client; print('MQTT library OK')" 2>/dev/null; then
        log "✅ MQTT library verified"
    else
        error "MQTT library verification failed"
    fi
    
    # Test NumPy library
    if python3 -c "import numpy; print('NumPy library OK')" 2>/dev/null; then
        log "✅ NumPy library verified"
    else
        error "NumPy library verification failed"
    fi
}

# Test hardware detection on correct stacks
test_hardware_detection() {
    log "Testing hardware detection on correct stacks..."
    
    # Test MegaBAS on stack 3
    if python3 -c "
import megabas
try:
    result = megabas.getRIn1K(3, 1)
    print(f'MegaBAS stack 3, input 1: {result}')
except Exception as e:
    print(f'MegaBAS error: {e}')
" 2>/dev/null | grep -q "MegaBAS stack 3"; then
        log "✅ MegaBAS detected on stack 3"
    else
        warn "MegaBAS not detected on stack 3"
    fi
    
    # Test RTD on stack 0
    if python3 -c "
import librtd
try:
    result = librtd.get(0, 1)
    print(f'RTD stack 0, sensor 1: {result}')
except Exception as e:
    print(f'RTD error: {e}')
" 2>/dev/null | grep -q "RTD stack 0"; then
        log "✅ RTD detected on stack 0"
    else
        warn "RTD not detected on stack 0"
    fi
    
    # Test 4RELIND on stack 2
    if python3 -c "
import lib4relind
try:
    result = lib4relind.get_relay(2, 1)
    print(f'4RELIND stack 2, relay 1: {result}')
except Exception as e:
    print(f'4RELIND error: {e}')
" 2>/dev/null | grep -q "4RELIND stack 2"; then
        log "✅ 4RELIND detected on stack 2"
    else
        warn "4RELIND not detected on stack 2"
    fi
}

# Clone repository
clone_repository() {
    log "Cloning solar heating repository..."
    
    if [ -d "$PROJECT_DIR" ]; then
        warn "Project directory already exists. Backing up..."
        sudo mv "$PROJECT_DIR" "${PROJECT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
    fi
    
    git clone "$REPO_URL" "$PROJECT_DIR"
    cd "$PROJECT_DIR"
    
    log "✅ Repository cloned"
}

# Set up v1 system
setup_v1_system() {
    log "Setting up v1 system..."
    
    if [ -f "$PROJECT_DIR/python/temperature_monitoring.py" ]; then
        sudo cp "$PROJECT_DIR/python/temperature_monitoring.py" /usr/local/bin/
        sudo chmod +x /usr/local/bin/temperature_monitoring.py
        
        if [ -f "$PROJECT_DIR/python/temperature_monitoring.service" ]; then
            sudo cp "$PROJECT_DIR/python/temperature_monitoring.service" /etc/systemd/system/
            sudo systemctl daemon-reload
            sudo systemctl enable temperature_monitoring.service
            log "✅ v1 system configured"
        else
            warn "v1 service file not found"
        fi
    else
        error "v1 system file not found"
    fi
}

# Set up v3 system
setup_v3_system() {
    log "Setting up v3 system..."
    
    if [ -d "$PROJECT_DIR/python/v3" ]; then
        cd "$PROJECT_DIR/python/v3"
        
        # Create virtual environment with system packages access
        log "Creating Python virtual environment..."
        python3 -m venv venv --system-site-packages
        source venv/bin/activate
        
        # Install dependencies
        log "Installing Python dependencies..."
        pip install --upgrade pip
        
        # Install PyPI dependencies (excluding hardware libraries)
        log "Installing PyPI dependencies..."
        if [ -f "requirements_virtual.txt" ]; then
            pip install -r requirements_virtual.txt
        else
            # Fallback to individual package installation
            pip install paho-mqtt asyncio-mqtt numpy pandas fastapi uvicorn pydantic influxdb-client httpx python-dotenv pydantic-settings structlog pytest pytest-asyncio black flake8 mypy
        fi
        
        # Note: taskmaster-ai package may not be available on PyPI - will be handled separately if needed
        
        # Note: Hardware libraries (megabas, librtd, lib4relind) are already installed system-wide
        log "Hardware libraries already installed system-wide"
        
        # Create service file
        log "Creating v3 service file..."
        sudo tee /etc/systemd/system/solar_heating_v3.service > /dev/null <<EOF
[Unit]
Description=Solar Heating System v3
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR/python/v3
Environment=PATH=$PROJECT_DIR/python/v3/venv/bin
ExecStart=$PROJECT_DIR/python/v3/venv/bin/python3 main.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
        
        sudo systemctl daemon-reload
        sudo systemctl enable solar_heating_v3.service
        log "✅ v3 system configured"
    else
        error "v3 system directory not found"
    fi
}

# Set up system switch script
setup_system_switch() {
    log "Setting up system switch script..."
    
    if [ -f "$PROJECT_DIR/python/system_switch.py" ]; then
        sudo cp "$PROJECT_DIR/python/system_switch.py" /usr/local/bin/
        sudo chmod +x /usr/local/bin/system_switch.py
        log "✅ System switch script installed"
    else
        warn "System switch script not found"
    fi
}

# Set up update script
setup_update_script() {
    log "Setting up update script..."
    
    if [ -f "$PROJECT_DIR/python/update_solar_heating.sh" ]; then
        cp "$PROJECT_DIR/python/update_solar_heating.sh" /home/pi/
        chmod +x /home/pi/update_solar_heating.sh
        log "✅ Update script installed"
    else
        warn "Update script not found"
    fi
}

# Create health check script
create_health_check() {
    log "Creating health check script..."
    
    cat > /home/pi/health_check.sh <<'EOF'
#!/bin/bash
# Health check for solar heating system

echo "🏥 Solar Heating System Health Check"
echo "===================================="

# Check v1 service
if systemctl is-active --quiet temperature_monitoring.service; then
    echo "✅ v1 service: RUNNING"
else
    echo "❌ v1 service: STOPPED"
fi

# Check v3 service
if systemctl is-active --quiet solar_heating_v3.service; then
    echo "✅ v3 service: RUNNING"
else
    echo "❌ v3 service: STOPPED"
fi

# Check MQTT connection
if mosquitto_pub -h 192.168.0.110 -u mqtt_beaches -P uQX6NiZ.7R -t "health_check" -m "test" 2>/dev/null; then
    echo "✅ MQTT: CONNECTED"
else
    echo "❌ MQTT: DISCONNECTED"
fi

# Check disk space
DISK_USAGE=$(df /home/pi | tail -1 | awk '{print $5}' | sed 's/%//')
if [ $DISK_USAGE -lt 90 ]; then
    echo "✅ Disk space: OK ($DISK_USAGE%)"
else
    echo "⚠️  Disk space: LOW ($DISK_USAGE%)"
fi

echo "===================================="
EOF
    
    chmod +x /home/pi/health_check.sh
    log "✅ Health check script created"
}

# Create sensor test script
create_sensor_test() {
    log "Creating sensor test script..."
    
    cat > /home/pi/test_sensors.py <<'EOF'
#!/usr/bin/env python3
import librtd
import megabas
import lib4relind
import time

print("Testing temperature sensors...")

# Test RTD sensors
try:
    rtd = librtd.RTD()
    for i in range(8):
        temp = rtd.readTemp(0, i)
        print(f"RTD {i}: {temp:.1f}°C")
except Exception as e:
    print(f"RTD error: {e}")

# Test MegaBAS sensors
try:
    mb = megabas.MegaBAS()
    for i in range(8):
        temp = mb.readTemp(3, i)
        print(f"MegaBAS {i}: {temp:.1f}°C")
except Exception as e:
    print(f"MegaBAS error: {e}")

print("Sensor test completed")
EOF
    
    chmod +x /home/pi/test_sensors.py
    log "✅ Sensor test script created"
}

# Set up backup directory
setup_backup() {
    log "Setting up backup directory..."
    mkdir -p /home/pi/backup
    log "✅ Backup directory created"
}

# Set up log rotation
setup_log_rotation() {
    log "Setting up log rotation..."
    
    sudo tee /etc/logrotate.d/solar_heating > /dev/null <<EOF
/home/pi/solar_heating/logs/*.log {
    daily
    missingok
    rotate 7
    compress
    delaycompress
    notifempty
    create 644 pi pi
}
EOF
    
    mkdir -p /home/pi/solar_heating/logs
    log "✅ Log rotation configured"
}

# Set permissions
set_permissions() {
    log "Setting permissions..."
    sudo chown -R pi:pi "$PROJECT_DIR"
    sudo chmod -R 755 "$PROJECT_DIR"
    log "✅ Permissions set"
}

# Test MQTT connection
test_mqtt() {
    log "Testing MQTT connection..."
    
    if mosquitto_pub -h "$MQTT_BROKER" -u "$MQTT_USERNAME" -P "$MQTT_PASSWORD" -t "test" -m "automated_deployment_test" 2>/dev/null; then
        log "✅ MQTT connection successful"
    else
        warn "MQTT connection failed - check your MQTT broker"
    fi
}

# Test hardware connections
test_hardware() {
    log "Testing hardware connections..."
    
    # Check I2C devices
    if command -v i2cdetect >/dev/null 2>&1; then
        log "I2C devices detected:"
        i2cdetect -y 1 | grep -v "^$" | tail -n +2
    else
        warn "i2cdetect not available"
    fi
    
    # Test hardware detection on correct stacks
    test_hardware_detection
}

# Final system check
final_check() {
    log "Performing final system check..."
    
    # Check services
    if systemctl is-enabled temperature_monitoring.service >/dev/null 2>&1; then
        log "✅ v1 service enabled"
    else
        warn "v1 service not enabled"
    fi
    
    if systemctl is-enabled solar_heating_v3.service >/dev/null 2>&1; then
        log "✅ v3 service enabled"
    else
        warn "v3 service not enabled"
    fi
    
    # Check disk space
    DISK_USAGE=$(df /home/pi | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ $DISK_USAGE -lt 90 ]; then
        log "✅ Disk space: OK ($DISK_USAGE%)"
    else
        warn "Disk space: LOW ($DISK_USAGE%)"
    fi
    
    # Check Python environment
    if [ -f "$PROJECT_DIR/python/v3/venv/bin/activate" ]; then
        log "✅ v3 Python environment created"
    else
        warn "v3 Python environment not found"
    fi
}

# Display completion message
completion_message() {
    echo ""
    echo "🎉 AUTOMATED DEPLOYMENT COMPLETED!"
    echo "=================================="
    echo ""
    echo "✅ Your solar heating system is now deployed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Connect your hardware boards (if not already connected)"
    echo "2. Reboot the system: sudo reboot"
    echo "3. Test v1 system: sudo systemctl start temperature_monitoring.service"
    echo "4. Test v3 system: cd $PROJECT_DIR/python/v3 && source venv/bin/activate && python3 main.py"
    echo "5. Use system switching: system_switch.py status"
    echo ""
    echo "🔍 Hardware Configuration:"
    echo "  MegaBAS: Stack 3 (temperature sensors)"
    echo "  RTD: Stack 0 (high-precision temperature sensors)"
    echo "  4RELIND: Stack 2 (relay control)"
    echo ""
    echo "🔧 Useful commands:"
    echo "  system_switch.py status    # Check system status"
    echo "  system_switch.py v1        # Switch to v1"
    echo "  system_switch.py v3        # Switch to v3"
    echo "  /home/pi/health_check.sh   # Health check"
    echo "  /home/pi/test_sensors.py   # Test sensors"
    echo "  /home/pi/update_solar_heating.sh  # Update system"
    echo ""
    echo "📚 Documentation:"
    echo "  $PROJECT_DIR/python/FRESH_PI_DEPLOYMENT_STEPS.md"
    echo "  $PROJECT_DIR/python/git_deployment_guide.md"
    echo ""
    echo "🚀 System is ready for production!"
}

# Main deployment function
main() {
    # Start timer
    START_TIME=$(date +%s)
    
    echo "🚀 Automated Solar Heating System Deployment"
    echo "============================================"
    echo "This script will deploy both v1 and v3 systems"
    echo "on your Raspberry Pi Zero 2W"
    echo ""
    echo "⏱️  Deployment started at: $(date)"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then
        error "Please don't run this script as root"
    fi
    
    # Confirm deployment
    read -p "Continue with deployment? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Deployment cancelled"
        exit 0
    fi
    
    # Run deployment steps with timing
    log "🚀 Starting deployment process..."
    
    log "Step 1/20: Checking Raspberry Pi..."
    check_raspberry_pi
    
    log "Step 2/20: Updating system packages..."
    update_system
    
    log "Step 3/20: Installing essential packages..."
    install_essentials
    
    log "Step 4/20: Enabling I2C interface..."
    enable_i2c
    
    log "Step 5/20: Installing hardware libraries..."
    install_hardware_libraries
    
    log "Step 6/20: Verifying hardware libraries..."
    verify_hardware_libraries
    
    log "Step 7/20: Verifying v1 dependencies..."
    verify_v1_dependencies
    
    log "Step 8/20: Cloning repository..."
    clone_repository
    
    log "Step 9/20: Setting up v1 system..."
    setup_v1_system
    
    log "Step 10/20: Setting up v3 system..."
    setup_v3_system
    
    log "Step 11/20: Setting up system switch..."
    setup_system_switch
    
    log "Step 12/20: Setting up update script..."
    setup_update_script
    
    log "Step 13/20: Creating health check..."
    create_health_check
    
    log "Step 14/20: Creating sensor test..."
    create_sensor_test
    
    log "Step 15/20: Setting up backup..."
    setup_backup
    
    log "Step 16/20: Configuring log rotation..."
    setup_log_rotation
    
    log "Step 17/20: Setting permissions..."
    set_permissions
    
    log "Step 18/20: Testing MQTT..."
    test_mqtt
    
    log "Step 19/20: Testing hardware..."
    test_hardware
    
    log "Step 20/20: Final system check..."
    final_check
    
    completion_message
    
    # Calculate and display execution time
    END_TIME=$(date +%s)
    EXECUTION_TIME=$((END_TIME - START_TIME))
    MINUTES=$((EXECUTION_TIME / 60))
    SECONDS=$((EXECUTION_TIME % 60))
    
    echo ""
    echo "⏱️  DEPLOYMENT TIMING"
    echo "===================="
    echo "Started at:  $(date -d "@$START_TIME")"
    echo "Completed at: $(date -d "@$END_TIME")"
    echo "Total time:   ${MINUTES}m ${SECONDS}s"
    echo ""
}

# Run main function
main "$@"
