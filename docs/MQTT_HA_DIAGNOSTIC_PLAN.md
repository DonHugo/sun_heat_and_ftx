# MQTT & Home Assistant Connection Issues - Diagnostic Plan

## Issue Summary

Both MQTT and Home Assistant showing "Disconnected" status in web dashboard.

---

## Root Cause Analysis

### MQTT Configuration Requirements

From code analysis (`mqtt_handler.py`):

1. **Required Environment Variables:**
   - `MQTT_USERNAME` - MQTT broker username
   - `MQTT_PASSWORD` - MQTT broker password
   - `MQTT_BROKER` - Broker IP/hostname (default: 192.168.0.110)
   - `MQTT_PORT` - Broker port (default: 1883)

2. **Validation:**
   - System validates credentials at startup (line 47)
   - **Fails fast** if credentials missing/invalid
   - Raises ValueError if validation fails

3. **Connection Flow:**
   - Creates MQTTAuthenticator (line 44)
   - Validates credentials (line 47)
   - Connects to broker (line 95)
   - 10-second connection timeout (line 99)

### Possible Causes

#### MQTT Disconnection:

**Most Likely:**
1. ❌ MQTT broker not running
2. ❌ Missing/invalid credentials in `.env` file
3. ❌ Firewall blocking port 1883
4. ❌ Wrong broker IP address

**Less Likely:**
5. Network connectivity issues
6. Broker configuration rejecting connections
7. SSL/TLS misconfiguration

#### Home Assistant Disconnection:

**Most Likely:**
1. ✅ **Dependent on MQTT** - If MQTT down, HA will be down
2. ❌ Home Assistant server not running
3. ❌ MQTT integration not configured in HA
4. ❌ MQTT discovery not working

---

## Diagnostic Steps

### Step 1: Check if .env File Exists

```bash
# On Raspberry Pi
cd /home/pi/sun_heat_and_ftx/python/v3
ls -la .env

# If missing:
cp ../../.env.example .env
nano .env  # Edit with actual credentials
```

### Step 2: Check MQTT Broker Status

```bash
# Check if Mosquitto is running
systemctl status mosquitto

# If not running:
sudo systemctl start mosquitto
sudo systemctl enable mosquitto

# Check if listening on port 1883
sudo netstat -tulpn | grep 1883
# OR
sudo ss -tulpn | grep 1883
```

### Step 3: Test MQTT Connection Manually

```bash
# Subscribe to test topic (requires credentials if auth enabled)
mosquitto_sub -h localhost -p 1883 -t "test" -v

# With authentication:
mosquitto_sub -h localhost -p 1883 -u YOUR_USERNAME -P YOUR_PASSWORD -t "solar_heating/#" -v

# Publish test message:
mosquitto_pub -h localhost -p 1883 -u YOUR_USERNAME -P YOUR_PASSWORD -t "test" -m "hello"
```

### Step 4: Check Solar Heating Service Logs

```bash
# Check for MQTT connection errors
journalctl -u solar_heating_v3.service --since "today" | grep -i mqtt

# Look for:
# - "Invalid MQTT credentials" (line 49 in mqtt_handler.py)
# - "Connected to MQTT broker"
# - Connection timeout errors
# - Authentication failures
```

### Step 5: Check Environment Variables

```bash
# Check if env vars are loaded by service
sudo systemctl cat solar_heating_v3.service

# Check current env
cat /home/pi/sun_heat_and_ftx/python/v3/.env | grep MQTT
```

### Step 6: Verify Broker Configuration

```bash
# Check Mosquitto config
cat /etc/mosquitto/mosquitto.conf

# Check if authentication is enabled
cat /etc/mosquitto/conf.d/*.conf | grep -i "allow_anonymous\|password_file"

# If password file configured, check users
sudo cat /etc/mosquitto/passwd
```

### Step 7: Check Home Assistant (if applicable)

```bash
# Check if HA is running
systemctl status home-assistant

# Check HA logs for MQTT integration
tail -f /home/homeassistant/.homeassistant/home-assistant.log | grep -i mqtt

# In HA UI:
# Settings -> Devices & Services -> MQTT
# Check connection status
```

---

## Quick Fix Scenarios

### Scenario 1: MQTT Broker Not Running

```bash
sudo systemctl start mosquitto
sudo systemctl enable mosquitto
sudo systemctl restart solar_heating_v3.service
```

### Scenario 2: Missing .env File

```bash
cd /home/pi/sun_heat_and_ftx/python/v3
cp ../../.env.example .env

# Edit .env file with actual values:
nano .env
# Set: MQTT_USERNAME, MQTT_PASSWORD, MQTT_BROKER, MQTT_PORT

# Restart service
sudo systemctl restart solar_heating_v3.service
```

### Scenario 3: Wrong Credentials

```bash
# Test credentials manually first:
mosquitto_sub -h localhost -p 1883 -u YOUR_USERNAME -P YOUR_PASSWORD -t "test" -v

# If successful, update .env:
nano /home/pi/sun_heat_and_ftx/python/v3/.env

# Restart service
sudo systemctl restart solar_heating_v3.service
```

### Scenario 4: Broker Requires Authentication

```bash
# Create MQTT user
sudo mosquitto_passwd -c /etc/mosquitto/passwd solar_user
# Enter password when prompted

# Update Mosquitto config
sudo nano /etc/mosquitto/conf.d/auth.conf
# Add:
#   allow_anonymous false
#   password_file /etc/mosquitto/passwd

# Restart Mosquitto
sudo systemctl restart mosquitto

# Update .env with credentials
nano /home/pi/sun_heat_and_ftx/python/v3/.env

# Restart service
sudo systemctl restart solar_heating_v3.service
```

---

## Expected Outcomes

### ✅ When Working:

1. **MQTT Status:**
   - Dashboard shows: "MQTT: Connected" (green badge)
   - Service logs: "Connected to MQTT broker at <IP>:<PORT>"

2. **Home Assistant Status:**
   - Dashboard shows: "HA: Connected" (green badge)
   - HA shows solar heating entities
   - Can control system from HA

3. **System Behavior:**
   - Temperature data published to MQTT
   - System state updates visible in MQTT
   - HA receives updates via MQTT discovery

### ❌ When Broken:

1. **MQTT Status:**
   - Dashboard shows: "MQTT: Disconnected" (red badge)
   - Service logs: Connection timeout, auth failure, or ValueError

2. **Home Assistant Status:**
   - Dashboard shows: "HA: Disconnected" (red badge)
   - HA shows "unavailable" for solar heating entities

---

## Configuration Files Reference

### Required Files:

1. **`/home/pi/sun_heat_and_ftx/python/v3/.env`**
   ```bash
   MQTT_USERNAME=your_username
   MQTT_PASSWORD=your_password
   MQTT_BROKER=192.168.0.110
   MQTT_PORT=1883
   ```

2. **`/etc/mosquitto/mosquitto.conf`** (if using auth)
   ```
   listener 1883
   allow_anonymous false
   password_file /etc/mosquitto/passwd
   ```

3. **`/etc/systemd/system/solar_heating_v3.service`**
   - Should have EnvironmentFile pointing to .env
   - OR environment variables defined inline

---

## Verification Checklist

After fixes, verify:

- [ ] MQTT broker running (`systemctl status mosquitto`)
- [ ] Port 1883 open (`netstat -tulpn | grep 1883`)
- [ ] Credentials work (`mosquitto_sub -h localhost -u USER -P PASS -t test`)
- [ ] `.env` file exists and has correct values
- [ ] Service logs show "Connected to MQTT broker"
- [ ] Dashboard shows "MQTT: Connected"
- [ ] Dashboard shows "HA: Connected" (if HA configured)
- [ ] Can subscribe to `solar_heating/#` topics
- [ ] Temperature data being published

---

## Issue #44 Context

The system now **requires** MQTT authentication:
- Issue #44 removed hardcoded credentials
- System validates credentials at startup
- **Fails fast** if missing/invalid
- This is a **security improvement** but requires configuration

**Migration Path:**
1. Copy `.env.example` to `.env`
2. Set MQTT credentials in `.env`
3. Restart service
4. Verify connection in dashboard

---

## Next Actions

**For User:**
1. Run diagnostic steps on Raspberry Pi
2. Share results (especially service logs)
3. Confirm MQTT broker status
4. Provide current `.env` configuration (redact passwords)

**Expected Time:**
- Diagnosis: 5-10 minutes
- Fix: 2-5 minutes (depending on cause)
- Verification: 2 minutes

**Following "Option C - Balanced" approach:**
- This is a **quick fix** (<15 min total)
- Fix immediately once cause identified
- Document solution for future reference
