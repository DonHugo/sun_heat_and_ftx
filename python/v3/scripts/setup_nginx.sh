#!/bin/bash
# Solar Heating System v3 - Nginx Setup Script
# Installs and configures nginx for static file serving and API proxy

set -e

echo "🔧 Setting up nginx for Solar Heating System v3..."

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "❌ This script must be run as root (use sudo)"
    exit 1
fi

# Update package list
echo "📦 Updating package list..."
apt update

# Install nginx
echo "📦 Installing nginx..."
apt install -y nginx

# Create directories
echo "📁 Creating directories..."
mkdir -p /opt/solar_heating/frontend
mkdir -p /var/log/nginx
mkdir -p /etc/nginx/sites-available
mkdir -p /etc/nginx/sites-enabled

# Copy frontend files
echo "📁 Copying frontend files..."
cp -r /home/pi/solar_heating_v3/frontend/* /opt/solar_heating/frontend/

# Set permissions
echo "🔐 Setting permissions..."
chown -R www-data:www-data /opt/solar_heating/frontend
chmod -R 755 /opt/solar_heating/frontend

# Copy nginx configuration
echo "⚙️  Configuring nginx..."
cp /home/pi/solar_heating_v3/nginx/solar_heating.conf /etc/nginx/sites-available/
ln -sf /etc/nginx/sites-available/solar_heating.conf /etc/nginx/sites-enabled/

# Remove default nginx site
echo "🗑️  Removing default nginx site..."
rm -f /etc/nginx/sites-enabled/default

# Test nginx configuration
echo "🧪 Testing nginx configuration..."
nginx -t

if [ $? -eq 0 ]; then
    echo "✅ Nginx configuration is valid"
    
    # Start and enable nginx
    echo "🚀 Starting nginx..."
    systemctl start nginx
    systemctl enable nginx
    
    # Check nginx status
    if systemctl is-active --quiet nginx; then
        echo "✅ Nginx is running successfully"
        echo ""
        echo "📋 Nginx Setup Summary:"
        echo "   • Nginx installed and configured"
        echo "   • Static files served from /opt/solar_heating/frontend"
        echo "   • API requests proxied to localhost:5001"
        echo "   • CORS headers configured for API"
        echo "   • Gzip compression enabled"
        echo "   • Security headers added"
        echo ""
        echo "🌐 Access the system at: http://localhost"
        echo "🔧 API available at: http://localhost/api/"
    else
        echo "❌ Failed to start nginx"
        exit 1
    fi
else
    echo "❌ Nginx configuration is invalid"
    exit 1
fi

echo ""
echo "✅ Nginx setup completed successfully!"
