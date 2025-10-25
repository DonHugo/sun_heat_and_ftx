#!/bin/bash

# Deploy Local GUI to Raspberry Pi
echo "🌐 Deploying Local GUI to Raspberry Pi"
echo "======================================"
echo ""

# Configuration
PI_HOST="192.168.0.18"
PI_USER="pi"
PI_PATH="/home/pi/solar_heating/python/v3"
LOCAL_WEB_DIR="python/v3/web_interface"

echo "📋 Deployment Configuration:"
echo "  • Raspberry Pi: $PI_USER@$PI_HOST"
echo "  • Target Path: $PI_PATH/web_interface"
echo "  • Local Source: $LOCAL_WEB_DIR"
echo ""

# Check if local web interface exists
if [ ! -d "$LOCAL_WEB_DIR" ]; then
    echo "❌ Error: Local web interface directory not found: $LOCAL_WEB_DIR"
    echo "Please run the feature implementation first."
    exit 1
fi

echo "✅ Local web interface found"
echo ""

# Test SSH connection
echo "🔌 Testing SSH connection to Raspberry Pi..."
if ! ssh -o ConnectTimeout=10 -o BatchMode=yes $PI_USER@$PI_HOST "echo 'SSH connection successful'" 2>/dev/null; then
    echo "❌ Error: Cannot connect to Raspberry Pi via SSH"
    echo "Please ensure:"
    echo "  • Raspberry Pi is powered on and connected to network"
    echo "  • SSH is enabled on the Pi"
    echo "  • SSH key authentication is set up (or use password authentication)"
    echo "  • IP address is correct: $PI_HOST"
    exit 1
fi

echo "✅ SSH connection successful"
echo ""

# Create target directory on Pi
echo "📁 Creating target directory on Raspberry Pi..."
ssh $PI_USER@$PI_HOST "mkdir -p $PI_PATH/web_interface"
echo "✅ Target directory created"
echo ""

# Copy web interface files
echo "📤 Copying web interface files to Raspberry Pi..."
echo ""

# Copy all files from web_interface directory
rsync -avz --progress \
    --exclude="__pycache__" \
    --exclude="*.pyc" \
    --exclude=".DS_Store" \
    "$LOCAL_WEB_DIR/" \
    "$PI_USER@$PI_HOST:$PI_PATH/web_interface/"

if [ $? -eq 0 ]; then
    echo "✅ Files copied successfully"
else
    echo "❌ Error: Failed to copy files"
    exit 1
fi

echo ""

# Set permissions on Pi
echo "🔧 Setting permissions on Raspberry Pi..."
ssh $PI_USER@$PI_HOST "chmod +x $PI_PATH/web_interface/app.py"
ssh $PI_USER@$PI_HOST "chmod +x $PI_PATH/web_interface/start_gui.sh"
echo "✅ Permissions set"
echo ""

# Install Python dependencies
echo "📦 Installing Python dependencies on Raspberry Pi..."
ssh $PI_USER@$PI_HOST "cd $PI_PATH/web_interface && pip3 install -r requirements.txt"

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "⚠️  Warning: Some dependencies may have failed to install"
    echo "You may need to install them manually on the Pi"
fi

echo ""

# Create systemd service for auto-start
echo "🔧 Creating systemd service for auto-start..."
ssh $PI_USER@$PI_HOST "sudo tee /etc/systemd/system/solar-heating-gui.service > /dev/null" << 'EOF'
[Unit]
Description=Solar Heating System Local GUI
After=network.target
Wants=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/solar_heating/python/v3/web_interface
ExecStart=/usr/bin/python3 /home/pi/solar_heating/python/v3/web_interface/app.py
Restart=always
RestartSec=10
Environment=PYTHONPATH=/home/pi/solar_heating/python/v3

[Install]
WantedBy=multi-user.target
EOF

echo "✅ Systemd service created"
echo ""

# Enable and start the service
echo "🚀 Enabling and starting the GUI service..."
ssh $PI_USER@$PI_HOST "sudo systemctl daemon-reload"
ssh $PI_USER@$PI_HOST "sudo systemctl enable solar-heating-gui.service"
ssh $PI_USER@$PI_HOST "sudo systemctl start solar-heating-gui.service"

if [ $? -eq 0 ]; then
    echo "✅ GUI service started successfully"
else
    echo "⚠️  Warning: Service may not have started properly"
    echo "You can start it manually with: sudo systemctl start solar-heating-gui.service"
fi

echo ""

# Check service status
echo "📊 Checking service status..."
ssh $PI_USER@$PI_HOST "sudo systemctl status solar-heating-gui.service --no-pager -l"

echo ""

# Test web interface
echo "🌐 Testing web interface..."
echo "Waiting 5 seconds for service to start..."
sleep 5

if curl -s --connect-timeout 10 "http://$PI_HOST:5000" > /dev/null; then
    echo "✅ Web interface is accessible!"
    echo ""
    echo "🎉 DEPLOYMENT SUCCESSFUL!"
    echo "========================"
    echo ""
    echo "🌐 Access your Local GUI:"
    echo "  • URL: http://$PI_HOST:5000"
    echo "  • Mobile: Works on phones and tablets"
    echo "  • Features: Real-time monitoring, manual control, diagnostics"
    echo ""
    echo "🔧 Service Management:"
    echo "  • Status: sudo systemctl status solar-heating-gui.service"
    echo "  • Start:  sudo systemctl start solar-heating-gui.service"
    echo "  • Stop:   sudo systemctl stop solar-heating-gui.service"
    echo "  • Logs:   sudo journalctl -u solar-heating-gui.service -f"
    echo ""
    echo "📱 Mobile Access:"
    echo "  • Open browser on your phone"
    echo "  • Go to: http://$PI_HOST:5000"
    echo "  • Bookmark for easy access"
    echo ""
else
    echo "⚠️  Warning: Web interface may not be accessible yet"
    echo "The service might still be starting up."
    echo ""
    echo "🔍 Troubleshooting:"
    echo "  • Check service status: sudo systemctl status solar-heating-gui.service"
    echo "  • Check logs: sudo journalctl -u solar-heating-gui.service -f"
    echo "  • Manual start: cd $PI_PATH/web_interface && python3 app.py"
    echo ""
fi

echo "🎯 Next Steps:"
echo "============="
echo "1. Open browser and go to: http://$PI_HOST:5000"
echo "2. Test the interface and controls"
echo "3. Bookmark the URL for easy access"
echo "4. Test on mobile device"
echo "5. Report any issues for troubleshooting"
echo ""
echo "✅ Deployment completed!"
