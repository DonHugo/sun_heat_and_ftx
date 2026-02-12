# Web GUI - Quick Start 🚀

## One-Command Setup

```bash
cd ~/sun_heat_and_ftx && ./scripts/setup_web_gui.sh
```

## Access Dashboard

```
http://raspberrypi:8080
```

## Useful Commands

```bash
# View logs
journalctl -u solar_heating_web_gui -f

# Restart services
sudo systemctl restart solar_heating_web_gui solar_heating_api

# Check status
sudo systemctl status solar_heating_web_gui
```

## Troubleshooting

**Can't access GUI?**
```bash
# Check if running
sudo systemctl status solar_heating_web_gui

# Check what ports are listening
sudo netstat -tlnp | grep :8080
```

**API not responding?**
```bash
# Test API directly
curl http://localhost:5001/api/status

# Check API service
sudo systemctl status solar_heating_api
```

**Buttons don't work?**
- Switch to "Manual" mode to control pump
- Check browser console (F12) for errors
- View API logs: `journalctl -u solar_heating_api -n 50`

## Features

✅ Real-time temperature monitoring  
✅ Pump control (Manual mode)  
✅ System mode switching  
✅ MQTT status diagnostics  
✅ Hardware health checks  
✅ Works even if Home Assistant is down  

## Architecture

```
Browser (Port 8080) 
    ↓
Web GUI Server
    ↓
API Server (Port 5001)
    ↓
Main Solar System
```

For full documentation, see: `docs/WEB_GUI_SETUP.md`

