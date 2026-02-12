# Web GUI Setup Guide

This guide will help you set up the web-based dashboard for your Solar Heating System v3.

## Overview

The web GUI provides:
- 📊 Real-time system status monitoring
- 🌡️ Temperature readings from all sensors
- 🎮 Direct control of pumps and system modes
- 🔧 Diagnostics for MQTT, hardware, and services
- ✅ **Works independently** of Home Assistant or MQTT issues

## Architecture

```
┌─────────────────┐
│   Web Browser   │  (Your phone/computer)
│  Port 8080      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Web GUI Server │  (Flask - serves HTML/CSS/JS)
│  Port 8080      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   API Server    │  (Flask-RESTful - provides data)
│  Port 5001      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Main System    │  (Solar heating controller)
│                 │
└─────────────────┘
```

## Quick Start

### 1. Install on Raspberry Pi

```bash
# Navigate to project directory
cd ~/sun_heat_and_ftx

# Pull latest changes
git pull

# Run setup script
./scripts/setup_web_gui.sh
```

The script will:
- ✅ Check dependencies
- ✅ Install Python packages (Flask, etc.)
- ✅ Set up systemd services
- ✅ Start the web GUI

### 2. Access the Dashboard

Open your web browser and navigate to:
```
http://raspberrypi:8080
```

Or use the IP address:
```
http://192.168.1.XXX:8080
```

## Manual Setup

If you prefer to set things up manually:

### Install Dependencies

```bash
sudo pip3 install flask flask-restful pydantic
```

### Copy Service Files

```bash
sudo cp systemd/solar_heating_api.service /etc/systemd/system/
sudo cp systemd/solar_heating_web_gui.service /etc/systemd/system/
sudo systemctl daemon-reload
```

### Start Services

```bash
# Start API server
sudo systemctl start solar_heating_api
sudo systemctl enable solar_heating_api

# Start Web GUI
sudo systemctl start solar_heating_web_gui
sudo systemctl enable solar_heating_web_gui
```

### Verify Services

```bash
# Check API server
sudo systemctl status solar_heating_api

# Check Web GUI
sudo systemctl status solar_heating_web_gui

# View logs
journalctl -u solar_heating_web_gui -f
journalctl -u solar_heating_api -f
```

## Using the Dashboard

### Main Dashboard Tab

Shows at-a-glance:
- Current system mode (Auto/Manual/Eco)
- Pump status (ON/OFF)
- Heater status (ON/OFF)
- All temperature readings
- Quick control buttons

### Temperatures Tab

Detailed temperature monitoring with status indicators:
- 🔥 Red = Hot (>80°C)
- ⚠️ Orange = Warm
- ✅ Green = Normal

### Control Tab

Direct system control:
- **Start/Stop Pump** (requires Manual mode)
- **Change System Mode** (Auto/Manual/Eco)
- **Emergency Stop** (always works)

### Diagnostics Tab

System health information:
- MQTT connection status and last message
- Hardware status (RTD boards, relays, sensors)
- Service status (main system, MQTT, watchdog)

## Troubleshooting

### Web GUI Not Loading

1. **Check if services are running:**
   ```bash
   sudo systemctl status solar_heating_web_gui
   sudo systemctl status solar_heating_api
   ```

2. **Check logs:**
   ```bash
   journalctl -u solar_heating_web_gui -n 50
   journalctl -u solar_heating_api -n 50
   ```

3. **Restart services:**
   ```bash
   sudo systemctl restart solar_heating_api
   sudo systemctl restart solar_heating_web_gui
   ```

### "API Server Not Connected"

This means the web GUI can't reach the API server:

1. **Check if API server is running:**
   ```bash
   curl http://localhost:5001/api/status
   ```

2. **If not responding, check the main system:**
   ```bash
   sudo systemctl status solar_heating_v3
   ```

3. **Check firewall (if enabled):**
   ```bash
   sudo ufw status
   sudo ufw allow 8080
   sudo ufw allow 5001
   ```

### Buttons Not Working

1. **For pump control**, make sure system is in **Manual mode**
2. **Check the error message** in the notification toast
3. **View browser console** (F12 in most browsers) for errors
4. **Check API logs** for validation errors

### Data Not Updating

1. **Check auto-refresh** is working (last update time in footer)
2. **Verify main system is running:**
   ```bash
   sudo systemctl status solar_heating_v3
   ```
3. **Check network connectivity** between browser and Raspberry Pi

## Advanced Configuration

### Change Ports

Edit the systemd service files:

```bash
sudo nano /etc/systemd/system/solar_heating_web_gui.service
```

Change the `--port` argument, then:

```bash
sudo systemctl daemon-reload
sudo systemctl restart solar_heating_web_gui
```

### Run Manually (Testing)

```bash
# Start API server
cd ~/sun_heat_and_ftx/python/v3
python3 run_api_server.py

# In another terminal, start web GUI
python3 web_server.py --port 8080 --api-port 5001
```

### Enable HTTPS (with nginx)

See `NGINX_SETUP.md` for instructions on adding HTTPS support.

## Security Notes

⚠️ **Important Security Considerations:**

1. **No Authentication**: The current setup has no password protection
2. **Local Network Only**: Don't expose to the internet without adding authentication
3. **Firewall**: Consider restricting access to local network only

### Add Basic Authentication (Optional)

If you want to add password protection, see `docs/AUTHENTICATION.md`.

## Maintenance

### View Logs

```bash
# Real-time logs
journalctl -u solar_heating_web_gui -f

# Last 100 lines
journalctl -u solar_heating_web_gui -n 100

# Logs from today
journalctl -u solar_heating_web_gui --since today
```

### Update the GUI

```bash
cd ~/sun_heat_and_ftx
git pull
sudo systemctl restart solar_heating_web_gui
```

### Disable Auto-Start

```bash
sudo systemctl disable solar_heating_web_gui
sudo systemctl disable solar_heating_api
```

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. View the logs: `journalctl -u solar_heating_web_gui -n 100`
3. Create an issue on GitHub with the log output

## What's Next?

- [ ] Add authentication/password protection
- [ ] Add HTTPS support with nginx
- [ ] Add temperature graphs/history
- [ ] Add email/push notifications
- [ ] Add mobile app wrapper

