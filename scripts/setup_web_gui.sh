#!/bin/bash
###############################################################################
# Solar Heating System v3 - Web GUI Setup Script
# 
# This script sets up the web GUI for the solar heating system
# Run this on your Raspberry Pi to enable web-based monitoring and control
###############################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_DIR="/home/pi/sun_heat_and_ftx"
SYSTEMD_DIR="/etc/systemd/system"
WEB_PORT=8080
API_PORT=5001

echo -e "${BLUE}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║   Solar Heating System v3 - Web GUI Setup                    ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check if running on Raspberry Pi
if [ ! -f /proc/cpuinfo ] || ! grep -q "BCM" /proc/cpuinfo; then
    echo -e "${YELLOW}Warning: This doesn't appear to be a Raspberry Pi${NC}"
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if project directory exists
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}Error: Project directory not found: $PROJECT_DIR${NC}"
    echo "Please clone the repository first or update PROJECT_DIR in this script"
    exit 1
fi

echo -e "${GREEN}✓${NC} Project directory found"

# Check if frontend files exist
if [ ! -f "$PROJECT_DIR/python/v3/frontend/index.html" ]; then
    echo -e "${RED}Error: Frontend files not found${NC}"
    echo "Expected: $PROJECT_DIR/python/v3/frontend/index.html"
    exit 1
fi

echo -e "${GREEN}✓${NC} Frontend files found"

# Check if web_server.py exists
if [ ! -f "$PROJECT_DIR/python/v3/web_server.py" ]; then
    echo -e "${RED}Error: web_server.py not found${NC}"
    echo "Please ensure web_server.py is in $PROJECT_DIR/python/v3/"
    exit 1
fi

echo -e "${GREEN}✓${NC} Web server script found"

# Check Python dependencies
echo ""
echo -e "${BLUE}Checking Python dependencies...${NC}"

if ! python3 -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Flask not found. Installing...${NC}"
    sudo pip3 install flask
fi

if ! python3 -c "import flask_restful" 2>/dev/null; then
    echo -e "${YELLOW}Flask-RESTful not found. Installing...${NC}"
    sudo pip3 install flask-restful
fi

if ! python3 -c "import pydantic" 2>/dev/null; then
    echo -e "${YELLOW}Pydantic not found. Installing...${NC}"
    sudo pip3 install pydantic
fi

echo -e "${GREEN}✓${NC} Python dependencies installed"

# Copy systemd service files
echo ""
echo -e "${BLUE}Setting up systemd services...${NC}"

if [ -f "$PROJECT_DIR/systemd/solar_heating_api.service" ]; then
    sudo cp "$PROJECT_DIR/systemd/solar_heating_api.service" "$SYSTEMD_DIR/"
    echo -e "${GREEN}✓${NC} API service file installed"
else
    echo -e "${YELLOW}⚠${NC} API service file not found, skipping"
fi

if [ -f "$PROJECT_DIR/systemd/solar_heating_web_gui.service" ]; then
    sudo cp "$PROJECT_DIR/systemd/solar_heating_web_gui.service" "$SYSTEMD_DIR/"
    echo -e "${GREEN}✓${NC} Web GUI service file installed"
else
    echo -e "${YELLOW}⚠${NC} Web GUI service file not found, skipping"
fi

# Reload systemd
sudo systemctl daemon-reload
echo -e "${GREEN}✓${NC} Systemd configuration reloaded"

# Ask user what to do
echo ""
echo -e "${BLUE}What would you like to do?${NC}"
echo "1) Start services now and enable auto-start on boot"
echo "2) Only enable auto-start (don't start now)"
echo "3) Just install files (manual start)"
echo ""
read -p "Enter choice [1-3]: " choice

case $choice in
    1)
        echo -e "${BLUE}Starting and enabling services...${NC}"
        
        # Start and enable API server
        if [ -f "$SYSTEMD_DIR/solar_heating_api.service" ]; then
            sudo systemctl enable solar_heating_api.service
            sudo systemctl restart solar_heating_api.service
            echo -e "${GREEN}✓${NC} API server started and enabled"
        fi
        
        # Give API server a moment to start
        sleep 2
        
        # Start and enable web GUI
        if [ -f "$SYSTEMD_DIR/solar_heating_web_gui.service" ]; then
            sudo systemctl enable solar_heating_web_gui.service
            sudo systemctl restart solar_heating_web_gui.service
            echo -e "${GREEN}✓${NC} Web GUI started and enabled"
        fi
        ;;
    2)
        echo -e "${BLUE}Enabling services for auto-start...${NC}"
        
        if [ -f "$SYSTEMD_DIR/solar_heating_api.service" ]; then
            sudo systemctl enable solar_heating_api.service
            echo -e "${GREEN}✓${NC} API server enabled"
        fi
        
        if [ -f "$SYSTEMD_DIR/solar_heating_web_gui.service" ]; then
            sudo systemctl enable solar_heating_web_gui.service
            echo -e "${GREEN}✓${NC} Web GUI enabled"
        fi
        
        echo -e "${YELLOW}Services will start automatically on next boot${NC}"
        ;;
    3)
        echo -e "${GREEN}✓${NC} Files installed only"
        echo ""
        echo "To start services manually:"
        echo "  sudo systemctl start solar_heating_api"
        echo "  sudo systemctl start solar_heating_web_gui"
        ;;
    *)
        echo -e "${RED}Invalid choice${NC}"
        exit 1
        ;;
esac

# Check service status
echo ""
echo -e "${BLUE}Service Status:${NC}"
echo ""

if [ -f "$SYSTEMD_DIR/solar_heating_api.service" ]; then
    echo "API Server:"
    sudo systemctl status solar_heating_api.service --no-pager -l | head -n 5
    echo ""
fi

if [ -f "$SYSTEMD_DIR/solar_heating_web_gui.service" ]; then
    echo "Web GUI:"
    sudo systemctl status solar_heating_web_gui.service --no-pager -l | head -n 5
    echo ""
fi

# Get hostname
HOSTNAME=$(hostname)

# Final instructions
echo ""
echo -e "${GREEN}"
echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║                     Setup Complete!                           ║"
echo "╚═══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"
echo ""
echo -e "${BLUE}Access your Web GUI at:${NC}"
echo -e "  ${GREEN}http://${HOSTNAME}:${WEB_PORT}${NC}"
echo -e "  ${GREEN}http://$(hostname -I | awk '{print $1}'):${WEB_PORT}${NC}"
echo ""
echo -e "${BLUE}API Server running at:${NC}"
echo -e "  http://localhost:${API_PORT}"
echo ""
echo -e "${BLUE}Useful commands:${NC}"
echo "  View Web GUI logs:  journalctl -u solar_heating_web_gui -f"
echo "  View API logs:      journalctl -u solar_heating_api -f"
echo "  Restart Web GUI:    sudo systemctl restart solar_heating_web_gui"
echo "  Restart API:        sudo systemctl restart solar_heating_api"
echo "  Stop services:      sudo systemctl stop solar_heating_web_gui solar_heating_api"
echo ""
echo -e "${YELLOW}Note: Make sure your main solar heating system is running!${NC}"
echo ""

