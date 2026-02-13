#!/bin/bash
# Deployment script for Watchdog MQTT Connection Prevention System
# This script will deploy all necessary files and configure the system

set -e

echo "🚀 Deploying Watchdog MQTT Connection Prevention System..."
echo "=================================================="

# Configuration
RPI_USER="pi"
RPI_HOST="rpi-solfangare-2"  # Update this to your Pi's hostname or IP
LOCAL_DIR="/Users/hafs/Documents/Github/sun_heat_and_ftx/python/v3"
REMOTE_DIR="/home/pi/solar_heating/python/v3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if we're running from the correct directory
if [ ! -f "watchdog_enhanced.py" ]; then
    print_error "watchdog_enhanced.py not found. Please run this script from the python/v3 directory."
    exit 1
fi

print_status "Starting deployment to Raspberry Pi..."

# Step 1: Copy files to Raspberry Pi
print_status "Step 1: Copying files to Raspberry Pi..."

# List of files to copy
FILES=(
    "watchdog_enhanced.py"
    "watchdog_health_monitor.sh"
    "solar_heating_watchdog_health.service"
    "solar_heating_watchdog_health.timer"
    "setup_watchdog_prevention.sh"
)

# Copy each file
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        print_status "Copying $file..."
        scp "$file" "$RPI_USER@$RPI_HOST:$REMOTE_DIR/"
        if [ $? -eq 0 ]; then
            print_success "Copied $file successfully"
        else
            print_error "Failed to copy $file"
            exit 1
        fi
    else
        print_warning "File $file not found, skipping..."
    fi
done

# Step 2: Copy documentation
print_status "Step 2: Copying documentation..."
if [ -f "../docs/WATCHDOG_MQTT_PREVENTION.md" ]; then
    scp "../docs/WATCHDOG_MQTT_PREVENTION.md" "$RPI_USER@$RPI_HOST:/home/pi/solar_heating/docs/"
    print_success "Copied documentation"
else
    print_warning "Documentation file not found, skipping..."
fi

# Step 3: Execute setup on Raspberry Pi
print_status "Step 3: Setting up the prevention system on Raspberry Pi..."

ssh "$RPI_USER@$RPI_HOST" << 'EOF'
    set -e
    
    echo "🔧 Setting up Watchdog MQTT Connection Prevention System on Raspberry Pi..."
    
    # Make scripts executable
    chmod +x /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh
    chmod +x /home/pi/solar_heating/python/v3/setup_watchdog_prevention.sh
    
    # Copy service files to systemd directory
    sudo cp /home/pi/solar_heating/python/v3/solar_heating_watchdog_health.service /etc/systemd/system/
    sudo cp /home/pi/solar_heating/python/v3/solar_heating_watchdog_health.timer /etc/systemd/system/
    
    # Reload systemd
    sudo systemctl daemon-reload
    
    # Enable and start the timer
    sudo systemctl enable solar_heating_watchdog_health.timer
    sudo systemctl start solar_heating_watchdog_health.timer
    
    echo "✅ Setup completed successfully!"
    
    # Show status
    echo ""
    echo "📊 System Status:"
    echo "=================="
    sudo systemctl status solar_heating_watchdog_health.timer --no-pager -l
    echo ""
    echo "📋 Timer Status:"
    sudo systemctl list-timers solar_heating_watchdog_health.timer --no-pager
    echo ""
    echo "🔍 Recent Health Checks:"
    sudo journalctl -u solar_heating_watchdog_health.service --since "5 minutes ago" --no-pager || echo "No recent health checks yet"
    
    echo ""
    echo "🎯 The prevention system is now active!"
    echo "   • Health checks run every 5 minutes"
    echo "   • Watchdog will restart if MQTT connection is stale"
    echo "   • Daily restart prevents long-running stale connections"
    echo "   • Logs are available in /var/log/solar_heating_watchdog_health.log"
EOF

if [ $? -eq 0 ]; then
    print_success "Deployment completed successfully!"
else
    print_error "Deployment failed during setup phase"
    exit 1
fi

# Step 4: Verify deployment
print_status "Step 4: Verifying deployment..."

ssh "$RPI_USER@$RPI_HOST" << 'EOF'
    echo "🔍 Verifying deployment..."
    
    # Check if files exist
    echo "📁 Checking files:"
    ls -la /home/pi/solar_heating/python/v3/watchdog_*
    ls -la /home/pi/solar_heating/python/v3/solar_heating_watchdog_health.*
    
    # Check if services are installed
    echo ""
    echo "🔧 Checking systemd services:"
    sudo systemctl list-unit-files | grep solar_heating_watchdog_health
    
    # Check if timer is active
    echo ""
    echo "⏰ Checking timer status:"
    sudo systemctl is-active solar_heating_watchdog_health.timer
    sudo systemctl is-enabled solar_heating_watchdog_health.timer
    
    # Run a test health check
    echo ""
    echo "🧪 Running test health check..."
    sudo /home/pi/solar_heating/python/v3/watchdog_health_monitor.sh
    
    echo ""
    echo "✅ Verification completed!"
EOF

print_success "🎉 Deployment and verification completed successfully!"
echo ""
echo "📋 Next Steps:"
echo "=============="
echo "1. Monitor the system: ssh $RPI_USER@$RPI_HOST 'sudo journalctl -u solar_heating_watchdog_health.service -f'"
echo "2. Check health logs: ssh $RPI_USER@$RPI_HOST 'tail -f /var/log/solar_heating_watchdog_health.log'"
echo "3. Verify timer: ssh $RPI_USER@$RPI_HOST 'sudo systemctl status solar_heating_watchdog_health.timer'"
echo ""
echo "🛡️ Your watchdog is now protected against stale MQTT connections!"
echo "   The system will automatically monitor and recover from connection issues."












