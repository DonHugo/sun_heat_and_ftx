#!/bin/bash
# Continue Solar Heating System Deployment
# This script continues the deployment from where it left off

set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

PROJECT_DIR="/home/pi/solar_heating"

log "Continuing deployment from where it left off..."

# Check if we're in the right directory
if [ ! -d "$PROJECT_DIR/python/v3" ]; then
    error "v3 directory not found. Please run the full deployment script first."
    exit 1
fi

cd "$PROJECT_DIR/python/v3"

# Remove existing virtual environment if it exists
if [ -d "venv" ]; then
    log "Removing existing virtual environment..."
    rm -rf venv
fi

# Create virtual environment with system packages access
log "Creating Python virtual environment with system packages access..."
python3 -m venv venv --system-site-packages
source venv/bin/activate

# Install PyPI dependencies
log "Installing PyPI dependencies..."
pip install --upgrade pip

if [ -f "requirements_virtual.txt" ]; then
    pip install -r requirements_virtual.txt
else
    # Fallback to individual package installation
    pip install paho-mqtt asyncio-mqtt numpy pandas fastapi uvicorn pydantic influxdb-client httpx python-dotenv pydantic-settings structlog pytest pytest-asyncio black flake8 mypy
fi

log "Hardware libraries (megabas, librtd, lib4relind) are already installed system-wide"

# Test hardware libraries
log "Testing hardware libraries in virtual environment..."
python3 -c "
import sys
print('Python path:', sys.path)

try:
    import megabas
    print('✅ megabas imported successfully')
except ImportError as e:
    print(f'❌ megabas import failed: {e}')

try:
    import librtd
    print('✅ librtd imported successfully')
except ImportError as e:
    print(f'❌ librtd import failed: {e}')

try:
    import lib4relind
    print('✅ lib4relind imported successfully')
except ImportError as e:
    print(f'❌ lib4relind import failed: {e}')
"

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

log "✅ v3 system setup completed successfully!"
log "You can now start the v3 service with: sudo systemctl start solar_heating_v3.service"
log "Check status with: sudo systemctl status solar_heating_v3.service"
