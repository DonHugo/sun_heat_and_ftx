#!/bin/bash
# Solar Heating System v3 Deployment Script for Raspberry Pi
# This script sets up the v3 system on the Raspberry Pi

set -e  # Exit on any error

echo "🚀 Solar Heating System Deployment Script"
echo "=========================================="

# Check if running on Raspberry Pi
if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi"
    echo "   Running on: $(uname -a)"
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "📦 Installing required packages..."
sudo apt install -y python3 python3-pip python3-venv git libi2c-dev i2c-tools mosquitto-clients

# Create project directory
PROJECT_DIR="/home/pi/solar_heating"
echo "📁 Setting up project directory: $PROJECT_DIR"

if [ -d "$PROJECT_DIR" ]; then
    echo "⚠️  Project directory already exists. Backing up..."
    sudo mv "$PROJECT_DIR" "${PROJECT_DIR}_backup_$(date +%Y%m%d_%H%M%S)"
fi

# Clone repository (you'll need to update this URL)
echo "📥 Cloning repository..."
echo "⚠️  Please update the repository URL below and uncomment the git clone command"
# git clone https://github.com/yourusername/sun_heat_and_ftx.git "$PROJECT_DIR"
echo "   Or if repository already exists, pull latest changes:"
echo "   cd $PROJECT_DIR && git pull origin main"

# Note: v1 system has been removed - only v3 is supported
echo "ℹ️  v1 system has been removed from this repository"
echo "   Only v3 system is supported and will be configured"

# Set up v3 system
echo "🔧 Setting up v3 system..."
if [ -d "$PROJECT_DIR/python/v3" ]; then
    cd "$PROJECT_DIR/python/v3"
    
    # Create virtual environment
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    
    # Install dependencies
    echo "📦 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r requirements.txt
    
    # Install TaskMaster AI dependencies
    echo "🧠 Installing TaskMaster AI dependencies..."
    pip install httpx python-dotenv pydantic
    
    # Test TaskMaster AI integration
    echo "🧪 Testing TaskMaster AI integration..."
    if python3 test_taskmaster.py; then
        echo "✅ TaskMaster AI integration test passed"
    else
        echo "⚠️  TaskMaster AI integration test failed - continuing anyway"
    fi
    
    # Create TaskMaster AI configuration
    echo "⚙️  Creating TaskMaster AI configuration..."
    if [ ! -f ".env" ]; then
        cat > .env << 'EOF'
# TaskMaster AI Configuration
SOLAR_TASKMASTER_ENABLED=true
SOLAR_TASKMASTER_API_KEY=your_api_key_here
SOLAR_TASKMASTER_BASE_URL=https://api.taskmaster.ai

# System Configuration
SOLAR_TEST_MODE=false
SOLAR_DEBUG_MODE=false
SOLAR_LOG_LEVEL=info

# MQTT Configuration
SOLAR_MQTT_BROKER=192.168.0.110
SOLAR_MQTT_PORT=1883
SOLAR_MQTT_USERNAME=mqtt_beaches
SOLAR_MQTT_PASSWORD=uQX6NiZ.7R

# Hardware Configuration
SOLAR_HARDWARE_PLATFORM=raspberry_pi_zero_2_w
SOLAR_RTD_BOARD_ADDRESS=0
SOLAR_MEGABAS_BOARD_ADDRESS=3
SOLAR_RELAY_BOARD_ADDRESS=2

# Temperature Thresholds
SOLAR_TEMPERATURE_THRESHOLD_HIGH=80.0
SOLAR_TEMPERATURE_THRESHOLD_LOW=20.0
SOLAR_TEMPERATURE_UPDATE_INTERVAL=30

# Solar Collector Configuration
SOLAR_SET_TEMP_TANK_1=70.0
SOLAR_DTSTART_TANK_1=8.0
SOLAR_DTSTOP_TANK_1=4.0
SOLAR_KYLNING_KOLLEKTOR=90.0
SOLAR_TEMP_KOK=150.0

# Performance Configuration
SOLAR_MAX_CONCURRENT_TASKS=5
SOLAR_AI_ANALYSIS_INTERVAL=3600
EOF
        echo "✅ TaskMaster AI configuration created"
    else
        echo "ℹ️  .env file already exists - TaskMaster AI will use existing configuration"
    fi
    
    # Create service file with TaskMaster AI support
    echo "🔧 Creating v3 service file with TaskMaster AI support..."
    sudo tee /etc/systemd/system/solar_heating_v3.service > /dev/null <<EOF
[Unit]
Description=Solar Heating System v3 with TaskMaster AI Integration
After=network.target mqtt.service
Wants=mqtt.service

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR/python/v3
Environment=PATH=$PROJECT_DIR/python/v3/venv/bin
ExecStart=$PROJECT_DIR/python/v3/venv/bin/python3 main_system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

# TaskMaster AI specific environment variables
Environment=SOLAR_TASKMASTER_ENABLED=true
Environment=SOLAR_TASKMASTER_API_KEY=your_api_key_here

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable solar_heating_v3.service
    echo "✅ v3 system with TaskMaster AI configured"
    
    # Verify TaskMaster AI integration
    echo "🔍 Verifying TaskMaster AI integration..."
    if python3 -c "
from taskmaster_integration import taskmaster
from taskmaster_service import taskmaster_service
print('✓ TaskMaster AI modules imported successfully')
"; then
        echo "✅ TaskMaster AI integration verified"
    else
        echo "❌ TaskMaster AI integration verification failed"
        echo "   This may indicate missing dependencies or configuration issues"
    fi
else
    echo "❌ v3 system directory not found"
fi

# Set up system switch script
echo "🔧 Setting up system switch script..."
if [ -f "$PROJECT_DIR/python/system_switch.py" ]; then
    sudo cp "$PROJECT_DIR/python/system_switch.py" /usr/local/bin/
    sudo chmod +x /usr/local/bin/system_switch.py
    echo "✅ System switch script installed"
else
    echo "⚠️  System switch script not found"
fi

# Create backup directory
echo "💾 Setting up backup directory..."
mkdir -p /home/pi/backup
echo "✅ Backup directory created"

# Set up log rotation
echo "📋 Setting up log rotation..."
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

# Create logs directory
mkdir -p /home/pi/solar_heating/logs

# Set permissions
echo "🔐 Setting permissions..."
sudo chown -R pi:pi "$PROJECT_DIR"
sudo chmod -R 755 "$PROJECT_DIR"

# Display summary
echo ""
echo "🎉 Deployment completed!"
echo "========================"
echo ""
echo "📋 Next steps:"
echo "1. Install Sequent Microsystems libraries:"
echo "   # Install RTD Data Acquisition"
echo "   git clone https://github.com/SequentMicrosystems/rtd-rpi.git"
echo "   cd rtd-rpi/python/rtd/ && sudo python3 setup.py install"
echo "   # Install Building Automation V4 (MegaBAS)"
echo "   git clone https://github.com/SequentMicrosystems/megabas-rpi.git"
echo "   cd megabas-rpi/python/ && sudo python3 setup.py install"
echo "   # Install Four Relays four HV Inputs"
echo "   git clone https://github.com/SequentMicrosystems/4relind-rpi.git"
echo "   cd 4relind-rpi/python/4relind/ && sudo python3 setup.py install"
echo ""
echo "2. Test v1 system:"
echo "   sudo systemctl start temperature_monitoring.service"
echo "   sudo systemctl status temperature_monitoring.service"
echo ""
echo "3. Test v3 system with TaskMaster AI:"
echo "   cd $PROJECT_DIR/python/v3"
echo "   source venv/bin/activate"
echo "   SOLAR_TEST_MODE=true python3 main_system.py"
echo ""
echo "4. Test TaskMaster AI integration:"
echo "   python3 test_taskmaster.py"
echo "   python3 demo_insights.py"
echo ""
echo "4. Switch between systems:"
echo "   system_switch.py v1    # Switch to v1"
echo "   system_switch.py v3    # Switch to v3"
echo "   system_switch.py status # Check status"
echo ""
echo "📚 For detailed instructions, see: $PROJECT_DIR/python/deployment_guide.md"
echo ""
echo "🧠 TaskMaster AI Integration Notes:"
echo "   • TaskMaster AI is enabled by default"
echo "   • Edit .env file to set your API key: SOLAR_TASKMASTER_API_KEY=your_key"
echo "   • System will automatically create AI tasks for optimization"
echo "   • Check logs for TaskMaster AI activity: sudo journalctl -u solar_heating_v3.service -f"
echo ""
echo "✅ Deployment script completed successfully!"
