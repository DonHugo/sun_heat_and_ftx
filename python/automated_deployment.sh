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
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
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
    sudo apt update && sudo apt upgrade -y
    log "✅ System updated"
}

# Install essential packages
install_essentials() {
    log "Installing essential packages..."
    sudo apt install -y git curl wget htop vim build-essential python3-pip python3-dev python3-smbus mosquitto-clients
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
}

# Install Sequent Microsystems libraries
install_hardware_libraries() {
    log "Installing Sequent Microsystems libraries..."
    
    # Create temporary directory
    TEMP_DIR="/tmp/solar_heating_install"
    mkdir -p "$TEMP_DIR"
    cd "$TEMP_DIR"
    
    # Install RTD Data Acquisition
    log "Installing RTD Data Acquisition..."
    git clone https://github.com/SequentMicrosystems/rtd-rpi.git
    cd rtd-rpi/python/rtd/
    sudo python3 setup.py install
    cd "$TEMP_DIR"
    
    # Install Building Automation V4 (MegaBAS)
    log "Installing Building Automation V4 (MegaBAS)..."
    git clone https://github.com/SequentMicrosystems/megabas-rpi.git
    cd megabas-rpi/python/
    sudo python3 setup.py install
    cd "$TEMP_DIR"
    
    # Install Four Relays four HV Inputs
    log "Installing Four Relays four HV Inputs..."
    git clone https://github.com/SequentMicrosystems/4relind-rpi.git
    cd 4relind-rpi/python/4relind/
    sudo python3 setup.py install
    cd "$TEMP_DIR"
    
    # Clean up
    cd ~
    rm -rf "$TEMP_DIR"
    
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
        
        # Create virtual environment
        log "Creating Python virtual environment..."
        python3 -m venv venv
        source venv/bin/activate
        
        # Install dependencies
        log "Installing Python dependencies..."
        pip install --upgrade pip
        pip install -r requirements.txt
        
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
    echo "1. Connect your hardware boards"
    echo "2. Reboot the system: sudo reboot"
    echo "3. Test v1 system: sudo systemctl start temperature_monitoring.service"
    echo "4. Test v3 system: cd $PROJECT_DIR/python/v3 && source venv/bin/activate && python3 main.py"
    echo "5. Use system switching: system_switch.py status"
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
    echo "🚀 Automated Solar Heating System Deployment"
    echo "============================================"
    echo "This script will deploy both v1 and v3 systems"
    echo "on your Raspberry Pi Zero 2W"
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
    
    # Run deployment steps
    check_raspberry_pi
    update_system
    install_essentials
    enable_i2c
    install_hardware_libraries
    verify_hardware_libraries
    clone_repository
    setup_v1_system
    setup_v3_system
    setup_system_switch
    setup_update_script
    create_health_check
    create_sensor_test
    setup_backup
    setup_log_rotation
    set_permissions
    test_mqtt
    test_hardware
    final_check
    completion_message
}

# Run main function
main "$@"
