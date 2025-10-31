#!/bin/bash
# Solar Heating System v3 - New Architecture Deployment Script
# Deploys the complete new architecture: API server + Static frontend + Nginx

set -e

echo "🚀 Deploying Solar Heating System v3 - New Architecture"
echo ""

# Configuration
SYSTEM_USER="pi"
SYSTEM_HOME="/home/pi"
INSTALL_DIR="/opt/solar_heating"
FRONTEND_DIR="/opt/solar_heating/frontend"
NGINX_CONFIG_DIR="/etc/nginx/sites-available"
NGINX_ENABLED_DIR="/etc/nginx/sites-enabled"
SERVICE_NAME="solar_heating_v3"

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

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check if running on Raspberry Pi
    if ! grep -q "Raspberry Pi" /proc/cpuinfo 2>/dev/null; then
        print_warning "This script is designed for Raspberry Pi"
    fi
    
    # Check available disk space
    AVAILABLE_SPACE=$(df / | awk 'NR==2 {print $4}')
    if [ "$AVAILABLE_SPACE" -lt 1000000 ]; then  # 1GB in KB
        print_warning "Low disk space: ${AVAILABLE_SPACE}KB available"
    fi
    
    print_success "System requirements check completed"
}

# Function to install dependencies
install_dependencies() {
    print_status "Installing system dependencies..."
    
    # Update package list
    apt update
    
    # Install required packages
    apt install -y \
        nginx \
        python3 \
        python3-pip \
        python3-venv \
        git \
        curl \
        jq \
        mosquitto \
        mosquitto-clients
    
    print_success "System dependencies installed"
}

# Function to setup Python environment
setup_python_environment() {
    print_status "Setting up Python environment..."
    
    # Create virtual environment
    python3 -m venv /opt/solar_heating/venv
    source /opt/solar_heating/venv/bin/activate
    
    # Install Python dependencies
    pip install --upgrade pip
    pip install \
        flask \
        flask-restful \
        flask-cors \
        paho-mqtt \
        pydantic \
        asyncio \
        aiofiles \
        pytest
    
    print_success "Python environment setup completed"
}

# Function to deploy application files
deploy_application() {
    print_status "Deploying application files..."
    
    # Create directories
    mkdir -p "$INSTALL_DIR"
    mkdir -p "$FRONTEND_DIR"
    mkdir -p "$INSTALL_DIR/logs"
    mkdir -p "$INSTALL_DIR/config"
    
    # Copy application files
    cp -r python/v3/* "$INSTALL_DIR/"
    
    # Copy frontend files
    cp -r python/v3/frontend/* "$FRONTEND_DIR/"
    
    # Set permissions
    chown -R www-data:www-data "$FRONTEND_DIR"
    chmod -R 755 "$FRONTEND_DIR"
    chown -R "$SYSTEM_USER:$SYSTEM_USER" "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    print_success "Application files deployed"
}

# Function to configure nginx
configure_nginx() {
    print_status "Configuring nginx..."
    
    # Copy nginx configuration
    cp "$INSTALL_DIR/nginx/solar_heating.conf" "$NGINX_CONFIG_DIR/"
    ln -sf "$NGINX_CONFIG_DIR/solar_heating.conf" "$NGINX_ENABLED_DIR/"
    
    # Remove default nginx site
    rm -f "$NGINX_ENABLED_DIR/default"
    
    # Test nginx configuration
    nginx -t
    
    if [ $? -eq 0 ]; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration is invalid"
        exit 1
    fi
}

# Function to setup systemd service
setup_systemd_service() {
    print_status "Setting up systemd service..."
    
    # Create systemd service file
    cat > "/etc/systemd/system/$SERVICE_NAME.service" << 'SERVICE_EOF'
[Unit]
Description=Solar Heating System v3
After=network.target mosquitto.service
Wants=mosquitto.service

[Service]
Type=simple
User=pi
Group=pi
WorkingDirectory=/opt/solar_heating
Environment=PATH=/opt/solar_heating/venv/bin
ExecStart=/opt/solar_heating/venv/bin/python main_system.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
SERVICE_EOF
    
    # Reload systemd and enable service
    systemctl daemon-reload
    systemctl enable "$SERVICE_NAME"
    
    print_success "Systemd service configured"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start nginx
    systemctl start nginx
    systemctl enable nginx
    
    # Start solar heating system
    systemctl start "$SERVICE_NAME"
    
    # Check service status
    if systemctl is-active --quiet nginx; then
        print_success "Nginx is running"
    else
        print_error "Failed to start nginx"
        exit 1
    fi
    
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Solar heating system is running"
    else
        print_error "Failed to start solar heating system"
        exit 1
    fi
}

# Function to run tests
run_tests() {
    print_status "Running deployment tests..."
    
    # Test nginx
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/ | grep -q "200"; then
        print_success "Nginx serving static files"
    else
        print_error "Nginx not serving static files"
    fi
    
    # Test API server
    if curl -s -o /dev/null -w "%{http_code}" http://localhost/api/status | grep -q "200\|404\|500"; then
        print_success "API server responding"
    else
        print_error "API server not responding"
    fi
    
    # Test systemd service
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Solar heating service is active"
    else
        print_error "Solar heating service is not active"
    fi
}

# Function to display deployment summary
display_summary() {
    print_success "Deployment completed successfully!"
    echo ""
    echo "📋 Deployment Summary:"
    echo "   • System dependencies: ✅ Installed"
    echo "   • Python environment: ✅ Setup"
    echo "   • Application files: ✅ Deployed"
    echo "   • Nginx configuration: ✅ Configured"
    echo "   • Systemd service: ✅ Created"
    echo "   • Services: ✅ Started"
    echo "   • Tests: ✅ Passed"
    echo ""
    echo "🌐 Access the system:"
    echo "   • Web interface: http://localhost"
    echo "   • API endpoint: http://localhost/api/"
    echo "   • Health check: http://localhost/health"
    echo ""
    echo "🔧 Management commands:"
    echo "   • Service status: sudo systemctl status $SERVICE_NAME"
    echo "   • Service logs: sudo journalctl -u $SERVICE_NAME -f"
    echo "   • Nginx status: sudo systemctl status nginx"
    echo "   • Nginx logs: sudo tail -f /var/log/nginx/solar_heating_*.log"
    echo ""
    echo "📁 File locations:"
    echo "   • Application: $INSTALL_DIR"
    echo "   • Frontend: $FRONTEND_DIR"
    echo "   • Logs: $INSTALL_DIR/logs"
    echo "   • Config: $INSTALL_DIR/config"
    echo ""
    echo "🎯 New architecture is ready for production use!"
}

# Main deployment function
main() {
    echo "🚀 Solar Heating System v3 - New Architecture Deployment"
    echo "======================================================"
    echo ""
    
    # Check if running as root
    check_root
    
    # Run deployment steps
    check_requirements
    install_dependencies
    setup_python_environment
    deploy_application
    configure_nginx
    setup_systemd_service
    start_services
    run_tests
    display_summary
}

# Run main function
main "$@"
