#!/bin/bash
# Solar Heating System v3 - Nginx Management Script

NGINX_CONFIG="/etc/nginx/sites-available/solar_heating.conf"
NGINX_ENABLED="/etc/nginx/sites-enabled/solar_heating.conf"
FRONTEND_DIR="/opt/solar_heating/frontend"

case "$1" in
    start)
        echo "🚀 Starting nginx..."
        systemctl start nginx
        ;;
    stop)
        echo "🛑 Stopping nginx..."
        systemctl stop nginx
        ;;
    restart)
        echo "🔄 Restarting nginx..."
        systemctl restart nginx
        ;;
    reload)
        echo "🔄 Reloading nginx configuration..."
        nginx -t && systemctl reload nginx
        ;;
    status)
        echo "📊 Nginx status:"
        systemctl status nginx
        ;;
    test)
        echo "🧪 Testing nginx configuration..."
        nginx -t
        ;;
    logs)
        echo "📋 Nginx logs:"
        tail -f /var/log/nginx/solar_heating_*.log
        ;;
    update-frontend)
        echo "📁 Updating frontend files..."
        if [ -d "$FRONTEND_DIR" ]; then
            cp -r /home/pi/solar_heating_v3/frontend/* "$FRONTEND_DIR/"
            chown -R www-data:www-data "$FRONTEND_DIR"
            chmod -R 755 "$FRONTEND_DIR"
            echo "✅ Frontend files updated"
        else
            echo "❌ Frontend directory not found: $FRONTEND_DIR"
        fi
        ;;
    enable)
        echo "✅ Enabling nginx site..."
        ln -sf "$NGINX_CONFIG" "$NGINX_ENABLED"
        systemctl reload nginx
        ;;
    disable)
        echo "❌ Disabling nginx site..."
        rm -f "$NGINX_ENABLED"
        systemctl reload nginx
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|reload|status|test|logs|update-frontend|enable|disable}"
        echo ""
        echo "Commands:"
        echo "  start           - Start nginx service"
        echo "  stop            - Stop nginx service"
        echo "  restart         - Restart nginx service"
        echo "  reload          - Reload nginx configuration"
        echo "  status          - Show nginx status"
        echo "  test            - Test nginx configuration"
        echo "  logs            - Show nginx logs"
        echo "  update-frontend - Update frontend files"
        echo "  enable          - Enable nginx site"
        echo "  disable         - Disable nginx site"
        exit 1
        ;;
esac
