# 🚀 Deploy Web GUI to Raspberry Pi - Step by Step

## Step 1: Connect to Your Raspberry Pi

Open a terminal and SSH to your Raspberry Pi:

```bash
ssh pi@raspberrypi.local
# OR use IP address:
# ssh pi@192.168.1.XXX
```

## Step 2: Pull Latest Changes

```bash
cd ~/sun_heat_and_ftx
git pull
```

You should see:
```
remote: Enumerating objects: XX, done.
Updating 410bf8a..1551b37
Fast-forward
 8 files changed, 1216 insertions(+), 24 deletions(-)
 create mode 100644 WEB_GUI_SUMMARY.md
 create mode 100644 docs/WEB_GUI_QUICK_START.md
 create mode 100644 docs/WEB_GUI_SETUP.md
 create mode 100755 python/v3/web_server.py
 create mode 100755 scripts/setup_web_gui.sh
 create mode 100644 systemd/solar_heating_api.service
 create mode 100644 systemd/solar_heating_web_gui.service
```

## Step 3: Run the Setup Script

```bash
./scripts/setup_web_gui.sh
```

The script will:
1. ✅ Check if you're on Raspberry Pi
2. ✅ Verify all files are present
3. ✅ Install Python dependencies (Flask, pydantic)
4. ✅ Copy systemd service files
5. ✅ Ask you what to do (choose option 1 to start now)

**When prompted, select option 1** to start services now and enable auto-start.

## Step 4: Verify Services Are Running

```bash
# Check web GUI status
sudo systemctl status solar_heating_web_gui

# Check API status
sudo systemctl status solar_heating_api
```

You should see **"active (running)"** in green.

## Step 5: Access the Web GUI

Open your web browser and go to:

```
http://raspberrypi.local:8080
```

Or use the IP address:
```
http://192.168.1.XXX:8080
```

Replace `XXX` with your Raspberry Pi's IP address.

## 🎉 Success!

You should now see the Solar Heating System dashboard with:
- ✅ Real-time temperature readings
- ✅ System status (mode, pump, heater)
- ✅ Control buttons
- ✅ Diagnostics information

## 🔍 Troubleshooting

### If setup script fails:

**Check the error message** and follow the suggestions.

**Manual installation:**
```bash
# Install dependencies
sudo pip3 install flask flask-restful pydantic

# Copy service files
sudo cp ~/sun_heat_and_ftx/systemd/*.service /etc/systemd/system/
sudo systemctl daemon-reload

# Start services
sudo systemctl enable --now solar_heating_api
sudo systemctl enable --now solar_heating_web_gui
```

### If web GUI doesn't load:

**1. Check if services are running:**
```bash
sudo systemctl status solar_heating_web_gui
sudo systemctl status solar_heating_api
```

**2. Check logs:**
```bash
journalctl -u solar_heating_web_gui -n 50
journalctl -u solar_heating_api -n 50
```

**3. Check what's listening on port 8080:**
```bash
sudo netstat -tlnp | grep 8080
```

**4. Test API directly:**
```bash
curl http://localhost:5001/api/status
```

### If you get "Connection Refused":

**Check firewall:**
```bash
sudo ufw status
# If firewall is active, allow the ports:
sudo ufw allow 8080
sudo ufw allow 5001
```

**Restart services:**
```bash
sudo systemctl restart solar_heating_api
sudo systemctl restart solar_heating_web_gui
```

### If buttons don't work:

1. **Switch to Manual mode** first (buttons require manual mode for safety)
2. **Check browser console** (press F12) for error messages
3. **View API logs:** `journalctl -u solar_heating_api -n 50`

## 📊 View Logs in Real-Time

```bash
# Watch web GUI logs
journalctl -u solar_heating_web_gui -f

# Watch API logs
journalctl -u solar_heating_api -f

# Watch all solar heating services
journalctl -u solar_heating* -f
```

Press `Ctrl+C` to stop viewing logs.

## 🔄 Restart Services

If you need to restart:

```bash
# Restart both
sudo systemctl restart solar_heating_web_gui solar_heating_api

# Or individually
sudo systemctl restart solar_heating_web_gui
sudo systemctl restart solar_heating_api
```

## ✅ What to Test

Once the GUI loads:

1. **Dashboard Tab:**
   - [ ] Temperature readings showing correct values
   - [ ] Pump status shows ON/OFF correctly
   - [ ] System mode displays current mode

2. **Temperatures Tab:**
   - [ ] All four temperature sensors show values
   - [ ] Status indicators show (Normal/Hot/Cold)

3. **Control Tab:**
   - [ ] Switch to Manual mode
   - [ ] Try starting pump (should work in manual mode)
   - [ ] Try stopping pump
   - [ ] Test Emergency Stop button

4. **Diagnostics Tab:**
   - [ ] MQTT status shows connected/disconnected
   - [ ] Hardware status displays
   - [ ] Service status shows running/inactive

## 📱 Access from Your Phone

Once working on your computer, you can also access from your phone on the same WiFi network:

```
http://raspberrypi.local:8080
```

Or:
```
http://192.168.1.XXX:8080
```

The dashboard is mobile-responsive and works great on phones!

## 🆘 Need Help?

If you encounter any issues:

1. **Check the logs** (commands above)
2. **Look at the error message** - it usually tells you what's wrong
3. **Verify main solar heating system is running:**
   ```bash
   sudo systemctl status solar_heating_v3
   ```

## 📚 More Information

- **Full documentation:** `docs/WEB_GUI_SETUP.md`
- **Quick reference:** `docs/WEB_GUI_QUICK_START.md`
- **Technical details:** `WEB_GUI_SUMMARY.md`

---

**Ready? Let's deploy!** 🚀

Start at Step 1 above and work through each step.

