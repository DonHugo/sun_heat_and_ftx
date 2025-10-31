#!/bin/bash
# Solar Heating System v3 - Rollback Script
# Rolls back to previous architecture if needed

set -e

echo "🔄 Rolling back Solar Heating System v3 Architecture"
echo ""

# Configuration
INSTALL_DIR="/opt/solar_heating"
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

# Function to find latest backup
find_latest_backup() {
    print_status "Finding latest backup..."
    
    # Look for backup directories
    BACKUP_PATTERN="/opt/solar_heating_backup_*"
    LATEST_BACKUP=$(ls -td $BACKUP_PATTERN 2>/dev/null | head -1)
    
    if [ -z "$LATEST_BACKUP" ]; then
        print_error "No backup found. Cannot rollback."
        exit 1
    fi
    
    print_success "Latest backup found: $LATEST_BACKUP"
    echo "$LATEST_BACKUP"
}

# Function to stop services
stop_services() {
    print_status "Stopping services..."
    
    # Stop solar heating service
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        systemctl stop "$SERVICE_NAME"
        print_success "Solar heating service stopped"
    fi
    
    # Stop nginx
    if systemctl is-active --quiet nginx; then
        systemctl stop nginx
        print_success "Nginx stopped"
    fi
}

# Function to restore from backup
restore_backup() {
    local backup_dir="$1"
    
    print_status "Restoring from backup: $backup_dir"
    
    if [ ! -d "$backup_dir" ]; then
        print_error "Backup directory not found: $backup_dir"
        exit 1
    fi
    
    # Create current backup before restoring
    if [ -d "$INSTALL_DIR" ]; then
        cp -r "$INSTALL_DIR" "/opt/solar_heating_current_backup_$(date +%Y%m%d_%H%M%S)"
    fi
    
    # Restore from backup
    rm -rf "$INSTALL_DIR"
    cp -r "$backup_dir" "$INSTALL_DIR"
    
    # Set permissions
    chown -R pi:pi "$INSTALL_DIR"
    chmod -R 755 "$INSTALL_DIR"
    
    print_success "Backup restored"
}

# Function to start services
start_services() {
    print_status "Starting services..."
    
    # Start solar heating system
    systemctl start "$SERVICE_NAME"
    
    # Check service status
    if systemctl is-active --quiet "$SERVICE_NAME"; then
        print_success "Solar heating system is running"
    else
        print_error "Failed to start solar heating system"
        exit 1
    fi
}

# Function to display rollback summary
display_summary() {
    print_success "Rollback completed successfully!"
    echo ""
    echo "📋 Rollback Summary:"
    echo "   • Services: ✅ Stopped and restarted"
    echo "   • Application: ✅ Restored from backup"
    echo "   • Permissions: ✅ Set correctly"
    echo "   • Services: ✅ Started"
    echo ""
    echo "🌐 Access the system:"
    echo "   • Web interface: http://localhost:5000 (if Flask interface)"
    echo "   • API endpoint: http://localhost:5001/api/"
    echo ""
    echo "📁 Current backup: /opt/solar_heating_current_backup_*"
    echo "   (Restore if needed: sudo cp -r /opt/solar_heating_current_backup_* /opt/solar_heating/)"
    echo ""
    echo "🎯 Previous architecture is restored!"
}

# Main rollback function
main() {
    echo "🔄 Solar Heating System v3 - Architecture Rollback"
    echo "=================================================="
    echo ""
    
    # Check if running as root
    if [ "$EUID" -ne 0 ]; then
        print_error "This script must be run as root (use sudo)"
        exit 1
    fi
    
    # Find latest backup
    LATEST_BACKUP=$(find_latest_backup)
    
    # Run rollback steps
    stop_services
    restore_backup "$LATEST_BACKUP"
    start_services
    display_summary
}

# Run main function
main "$@"
