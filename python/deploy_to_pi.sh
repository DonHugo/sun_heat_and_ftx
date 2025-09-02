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
    
    # Create service file
    echo "🔧 Creating v3 service file..."
    sudo tee /etc/systemd/system/solar_heating_v3.service > /dev/null <<EOF
[Unit]
Description=Solar Heating System v3
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=$PROJECT_DIR/python/v3
Environment=PATH=$PROJECT_DIR/python/v3/venv/bin
ExecStart=$PROJECT_DIR/python/v3/venv/bin/python3 main_system.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
    
    sudo systemctl daemon-reload
    sudo systemctl enable solar_heating_v3.service
    echo "✅ v3 system configured"
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
echo "3. Test v3 system:"
echo "   cd $PROJECT_DIR/python/v3"
echo "   source venv/bin/activate"
echo "   SOLAR_TEST_MODE=true python3 main.py"
echo ""
echo "4. Switch between systems:"
echo "   system_switch.py v1    # Switch to v1"
echo "   system_switch.py v3    # Switch to v3"
echo "   system_switch.py status # Check status"
echo ""
echo "📚 For detailed instructions, see: $PROJECT_DIR/python/deployment_guide.md"
echo ""
echo "✅ Deployment script completed successfully!"
