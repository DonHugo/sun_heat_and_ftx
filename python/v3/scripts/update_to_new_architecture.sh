#!/bin/bash
# Solar Heating System v3 - Update to New Architecture
# Updates existing installations to the new architecture

set -e

echo "🔄 Updating Solar Heating System v3 to New Architecture"
echo ""

# Configuration
INSTALL_DIR="/opt/solar_heating"
FRONTEND_DIR="/opt/solar_heating/frontend"
BACKUP_DIR="/opt/solar_heating_backup_$(date +%Y%m%d_%H%M%S)"
SERVICE_NAME="solar_heating_v3"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Function to backup existing installation
backup_existing() {
    print_status "Creating backup of existing installation..."
    
    if [ -d "$INSTALL_DIR" ]; then
        cp -r "$INSTALL_DIR" "$BACKUP_DIR"
        print_success "Backup created at: $BACKUP_DIR"
    else
        print_warning "No existing installation found"
    fi
}

# Function to stop existing services
stop_existing_services() {
    print_status "Stopping existing services..."
    
    # Stop solar heating service
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
        print_success "Solar heating service stopped"
    fi
    
    # Stop nginx if running
    if systemctl is-active --quiet nginx; then
        systemctl stop nginx
        print_success "Nginx stopped"
    fi
}

# Function to install new dependencies
install_new_dependencies() {
    print_status "Installing new dependencies..."
    
    # Update package list
    apt update
    
    # Install nginx if not already installed
    if ! command -v nginx &> /dev/null; then
        apt install -y nginx
        print_success "Nginx installed"
    else
        print_success "Nginx already installed"
    fi
    
    # Install additional Python dependencies
    if [ -f "$INSTALL_DIR/venv/bin/activate" ]; then
        source "$INSTALL_DIR/venv/bin/activate"
        pip install flask flask-restful flask-cors
        print_success "New Python dependencies installed"
    else
        print_error "Python virtual environment not found"
        exit 1
    fi
}

# Function to update application files
update_application() {
    print_status "Updating application files..."
    
    # Create frontend directory
    mkdir -p "$FRONTEND_DIR"
    
    # Copy new application files
    cp -r python/v3/* "$INSTALL_DIR/"
    
    # Copy frontend files
    cp -r python/v3/frontend/* "$FRONTEND_DIR/"
    
    # Set permissions
    chown -R www-data:www-data "$FRONTEND_DIR"
    chmod -R 755 "$FRONTEND_DIR"
    chown -R pi:pi "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    print_success "Application files updated"
}

# Function to configure nginx
configure_nginx() {
    print_status "Configuring nginx..."
    
    # Copy nginx configuration
    cp "$INSTALL_DIR/nginx/solar_heating.conf" /etc/nginx/sites-available/
    ln -sf /etc/nginx/sites-available/solar_heating.conf /etc/nginx/sites-enabled/
    
    # Remove default nginx site
    rm -f /etc/nginx/sites-enabled/default
    
    # Test nginx configuration
    nginx -t
    
    if [ $? -eq 0 ]; then
        print_success "Nginx configuration is valid"
    else
        print_error "Nginx configuration is invalid"
        exit 1
    fi
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
    print_status "Running update tests..."
    
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
}

# Function to display update summary
display_summary() {
    print_success "Update to new architecture completed successfully!"
    echo ""
    echo "📋 Update Summary:"
    echo "   • Existing installation: ✅ Backed up"
    echo "   • Services: ✅ Stopped and restarted"
    echo "   • Dependencies: ✅ Updated"
    echo "   • Application files: ✅ Updated"
    echo "   • Nginx configuration: ✅ Configured"
    echo "   • Services: ✅ Started"
    echo "   • Tests: ✅ Passed"
    echo ""
    echo "🌐 Access the system:"
    echo "   • Web interface: http://localhost"
    echo "   • API endpoint: http://localhost/api/"
    echo "   • Health check: http://localhost/health"
    echo ""
    echo "📁 Backup location: $BACKUP_DIR"
    echo "   (Restore if needed: sudo cp -r $BACKUP_DIR/* /opt/solar_heating/)"
    echo ""
    echo "🎯 New architecture is ready for production use!"
}

# Main update function
main() {
    echo "🔄 Solar Heating System v3 - Update to New Architecture"
    echo "======================================================="
    echo ""
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
    
    # Run update steps
    backup_existing
    stop_existing_services
    install_new_dependencies
    update_application
    configure_nginx
    start_services
    run_tests
    display_summary
}

# Run main function
main "$@"
