# Solar Heating System v3 - Architecture Migration Guide

## Overview
This guide documents the migration from the old Flask web interface to the new REST API + Static Frontend architecture.

## Architecture Changes

### Old Architecture (Flask Web Interface)
```
┌─────────────────────────────────────────────────────────────┐
│                    Old Architecture                         │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Flask App     │    │  Main System    │    │  Home Assistant │
│   (Port 5000)   │    │  (Port 5001)    │    │  (MQTT)         │
│                 │    │                 │    │                 │
│ • Templates     │    │ • SolarHeating  │    │ • MQTT Client   │
│ • Static Files  │    │ • MQTT Client   │    │ • Discovery     │
│ • API Routes    │    │ • Hardware Ctrl │    │ • Control       │
│ • Duplicate     │    │ • Duplicate     │    │                 │
│   Components    │    │   Components    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### New Architecture (REST API + Static Frontend)
```
┌─────────────────────────────────────────────────────────────┐
│                    New Architecture                        │
└─────────────────────────────────────────────────────────────┘

┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Static Files  │    │   Nginx Proxy   │    │  Main System   │
│   (Frontend)    │◄───┤   (Port 80)     │◄───┤  (Port 5001)    │
│                 │    │                 │    │                 │
│ • HTML/CSS/JS   │    │ • Static Serve │    │ • SolarHeating  │
│ • No Python     │    │ • API Proxy     │    │ • API Server    │
│ • Mobile Ready  │    │ • CORS Headers  │    │ • MQTT Client   │
│                 │    │ • Security      │    │ • Hardware Ctrl │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Migration Steps

### 1. Backup Current System
```bash
# Create backup of current system
sudo cp -r /home/pi/solar_heating_v3 /home/pi/solar_heating_v3_backup
```

### 2. Install New Architecture
```bash
# Deploy new architecture
cd /home/pi/solar_heating_v3
git pull origin main

# Install new dependencies
pip install flask flask-restful

# Setup nginx
sudo ./scripts/setup_nginx.sh
```

### 3. Remove Old Flask Interface
```bash
# Run cleanup script
./scripts/cleanup_flask_interface.sh

# Verify cleanup
./scripts/verify_cleanup.sh
```

### 4. Test New Architecture
```bash
# Test API server
./scripts/test_api_integration.py

# Test nginx
./scripts/test_nginx.sh

# Test complete system
./scripts/test_complete_system.sh
```

## Component Mapping

### Old Components → New Components

| Old Component | New Component | Status |
|---------------|---------------|---------|
| Flask web interface | Static HTML/CSS/JS | ✅ Replaced |
| Flask templates | Static HTML | ✅ Replaced |
| Flask static files | Static CSS/JS | ✅ Replaced |
| Flask API routes | REST API server | ✅ Replaced |
| Duplicate MQTT client | Single MQTT client | ✅ Consolidated |
| Duplicate hardware interface | Single hardware interface | ✅ Consolidated |
| Flask systemd service | Nginx + API server | ✅ Replaced |

### API Endpoints Mapping

| Old Flask Route | New REST API Endpoint | Status |
|-----------------|----------------------|---------|
| `/` | `/` (static HTML) | ✅ Replaced |
| `/api/status` | `/api/status` | ✅ Replaced |
| `/api/control` | `/api/control` | ✅ Replaced |
| `/api/mode` | `/api/mode` | ✅ Replaced |
| `/api/temperatures` | `/api/temperatures` | ✅ Replaced |
| `/api/mqtt` | `/api/mqtt` | ✅ Replaced |

## Benefits of New Architecture

### 1. Performance Improvements
- **Static File Serving**: Nginx serves static files faster than Flask
- **Reduced Memory Usage**: No Python web server for static files
- **Better Caching**: Nginx provides better static file caching
- **Gzip Compression**: Automatic compression for better performance

### 2. Security Improvements
- **Security Headers**: Nginx provides comprehensive security headers
- **CORS Configuration**: Proper CORS handling for API
- **Input Validation**: REST API provides better input validation
- **Error Handling**: Improved error handling and logging

### 3. Maintainability Improvements
- **Single Source of Truth**: One system instance, no duplication
- **Clean Separation**: Static frontend + API server + main system
- **Better Testing**: Easier to test individual components
- **Documentation**: Comprehensive API documentation

### 4. Scalability Improvements
- **Load Balancing**: Nginx can handle multiple backend instances
- **Caching**: Better caching strategies for static content
- **Monitoring**: Better monitoring and logging capabilities
- **Deployment**: Easier deployment and updates

## Troubleshooting

### Common Issues

#### 1. API Server Not Starting
```bash
# Check if API server is running
curl http://localhost:5001/api/status

# Check logs
journalctl -u solar_heating_v3.service -f
```

#### 2. Nginx Not Serving Files
```bash
# Check nginx status
sudo systemctl status nginx

# Check nginx configuration
sudo nginx -t

# Check nginx logs
sudo tail -f /var/log/nginx/solar_heating_*.log
```

#### 3. Frontend Not Loading
```bash
# Check if static files exist
ls -la /opt/solar_heating/frontend/

# Check nginx configuration
sudo cat /etc/nginx/sites-available/solar_heating.conf
```

#### 4. CORS Issues
```bash
# Check CORS headers
curl -I http://localhost/api/status

# Verify nginx CORS configuration
grep -A 10 "CORS" /etc/nginx/sites-available/solar_heating.conf
```

### Recovery Procedures

#### 1. Restore from Backup
```bash
# Stop new system
sudo systemctl stop nginx
sudo systemctl stop solar_heating_v3

# Restore backup
sudo cp -r /home/pi/solar_heating_v3_backup /home/pi/solar_heating_v3

# Restart old system
sudo systemctl start solar_heating_v3
```

#### 2. Rollback to Flask Interface
```bash
# Restore Flask interface
sudo cp -r /tmp/solar_heating_backup_* /home/pi/solar_heating_v3/

# Restart Flask services
sudo systemctl start solar-heating-gui
```

## Monitoring and Maintenance

### 1. Health Checks
```bash
# Check system health
curl http://localhost/health
curl http://localhost/api/status

# Check nginx status
sudo systemctl status nginx
```

### 2. Log Monitoring
```bash
# Monitor nginx logs
sudo tail -f /var/log/nginx/solar_heating_*.log

# Monitor system logs
journalctl -u solar_heating_v3.service -f
```

### 3. Performance Monitoring
```bash
# Check nginx performance
sudo nginx -T | grep -A 5 "gzip"

# Check API response times
curl -w "@curl-format.txt" -o /dev/null -s http://localhost/api/status
```

## Conclusion

The new architecture provides significant improvements in performance, security, maintainability, and scalability. The migration process is designed to be safe with comprehensive backup and rollback procedures.

For support or questions, refer to the troubleshooting section or contact the development team.
