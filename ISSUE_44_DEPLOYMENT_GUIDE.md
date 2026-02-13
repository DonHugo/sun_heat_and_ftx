# Issue #44 - MQTT Authentication Deployment Guide
**Target:** Production Solar Heating System  
**Status:** Code Complete, Unit Tested, Ready for Deployment  
**Date:** February 14, 2026

---

## Overview

This guide provides step-by-step instructions for deploying MQTT authentication enforcement to the production solar heating system. The deployment includes credential configuration, system validation, and security verification.

**Estimated Time:** 30-45 minutes  
**System Downtime:** 5-10 minutes (during service restart)  
**Risk Level:** MEDIUM (authentication changes could lock out system if misconfigured)

---

## Prerequisites

### Required Access
- [ ] SSH access to production server
- [ ] Sudo/root privileges for MQTT broker configuration
- [ ] Access to MQTT broker (mosquitto) configuration
- [ ] Git repository access for code deployment

### Required Knowledge
- [ ] Basic Linux command line
- [ ] MQTT broker administration (mosquitto)
- [ ] Environment variable configuration
- [ ] Python virtual environment management

### Backup Requirements
- [ ] Current system configuration backed up
- [ ] MQTT broker configuration backed up
- [ ] Rollback plan documented

---

## Pre-Deployment Checklist

### 1. Code Verification
```bash
# On development machine
cd /Users/hafs/Documents/Github/sun_heat_and_ftx
git status  # Ensure on main branch
git log --oneline -5  # Verify Issue #44 commits present

# Look for commits:
# 410bf8ac - Add MQTT authenticator (Issue #44)
# 6e4de06 - Remove hardcoded MQTT credentials (Issue #45)
```

### 2. Test Results Review
- [x] Unit tests: 21/22 passed (95% success rate)
- [x] Code reviewed and approved
- [x] Documentation complete
- [ ] Integration tests: Manual verification required post-deployment

### 3. Production Readiness
- [ ] Maintenance window scheduled
- [ ] Team notified of deployment
- [ ] Rollback plan prepared
- [ ] Monitoring systems ready

---

## Deployment Steps

### Phase 1: MQTT Broker Configuration (15 minutes)

#### Step 1.1: Backup Current Configuration
```bash
# SSH to production server
ssh user@production-server

# Backup mosquitto configuration
sudo cp /etc/mosquitto/mosquitto.conf /etc/mosquitto/mosquitto.conf.backup-$(date +%Y%m%d)
sudo cp /etc/mosquitto/passwd /etc/mosquitto/passwd.backup-$(date +%Y%m%d) 2>/dev/null || true

# Verify backups
ls -la /etc/mosquitto/*.backup-*
```

#### Step 1.2: Create MQTT User Credentials
```bash
# Generate strong password (20+ characters)
# Use password manager or command:
openssl rand -base64 24

# Example output: xK7mP9vN2wQ8zR5tL6jH4yB3

# Create MQTT user (replace <username> and enter strong password when prompted)
sudo mosquitto_passwd -c /etc/mosquitto/passwd solar_heating_user

# Verify user created
sudo cat /etc/mosquitto/passwd
# Should show: solar_heating_user:$encrypted_password_hash
```

**SECURITY NOTE:** Store the chosen username and password in your organization's secure credential management system (e.g., LastPass, 1Password, HashiCorp Vault). You'll need these for Step 2.

#### Step 1.3: Enable Authentication in Mosquitto
```bash
# Edit mosquitto configuration
sudo nano /etc/mosquitto/mosquitto.conf

# Add or modify these lines:
# --- START CONFIGURATION ---
# Disable anonymous access (CRITICAL SECURITY SETTING)
allow_anonymous false

# Specify password file location
password_file /etc/mosquitto/passwd

# Optional: Listen on specific interface
listener 1883 0.0.0.0

# Optional: Enable persistent session storage
persistence true
persistence_location /var/lib/mosquitto/

# Optional: Logging for security audit
log_dest file /var/log/mosquitto/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# Optional: Connection/subscription logging
connection_messages true
# --- END CONFIGURATION ---

# Save and exit (Ctrl+X, Y, Enter in nano)
```

#### Step 1.4: Test Mosquitto Configuration
```bash
# Check configuration syntax
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v

# Should see: "Opening ipv4 listen socket on port 1883"
# If errors, check configuration syntax

# Restart mosquitto service
sudo systemctl restart mosquitto

# Verify service running
sudo systemctl status mosquitto
# Should show: "active (running)"

# Check mosquitto logs
sudo tail -20 /var/log/mosquitto/mosquitto.log
# Look for: "Opening ipv4 listen socket on port 1883"
```

#### Step 1.5: Test Authentication from Broker Host
```bash
# Test with valid credentials (use username/password from Step 1.2)
mosquitto_sub -h localhost -p 1883 -t test/topic -u solar_heating_user -P "<your_password>" &
SUB_PID=$!
sleep 2
mosquitto_pub -h localhost -p 1883 -t test/topic -m "test message" -u solar_heating_user -P "<your_password>"
sleep 1
kill $SUB_PID 2>/dev/null

# Expected: You should see "test message" output
# If error "Connection Refused": Check credentials

# Test with INVALID credentials (should fail)
mosquitto_sub -h localhost -p 1883 -t test/topic -u wrong_user -P "wrong_pass"
# Expected: "Connection Refused: not authorized"

echo "✅ MQTT broker authentication working correctly"
```

---

### Phase 2: Application Deployment (10 minutes)

#### Step 2.1: Deploy Code Updates
```bash
# Navigate to application directory
cd /opt/solar_heating_system  # Adjust path as needed

# Pull latest code from repository
git fetch origin
git checkout main
git pull origin main

# Verify Issue #44 code present
git log --oneline --grep="Issue #44" --grep="Issue #45" | head -5

# Should see commits for authenticator and credential removal
```

#### Step 2.2: Configure Environment Variables
```bash
# Navigate to python v3 directory
cd python/v3

# Check if .env exists
ls -la .env

# If .env doesn't exist, create from template
if [ ! -f .env ]; then
    cp ../../.env.example .env
    echo "Created .env from template"
fi

# Edit .env file
nano .env

# Set REQUIRED values (use credentials from Phase 1, Step 1.2):
# --- REQUIRED CONFIGURATION ---
MQTT_USERNAME=solar_heating_user
MQTT_PASSWORD=<paste_strong_password_from_step_1.2>
MQTT_BROKER=192.168.0.110  # Or your broker IP
MQTT_PORT=1883

# --- OPTIONAL CONFIGURATION ---
SYSTEM_MODE=auto
LOG_LEVEL=INFO
DEBUG=false

# Save and exit (Ctrl+X, Y, Enter)

# Verify .env is not in git
git status .env
# Should show: "nothing added to commit"
# If it's tracked, add to .gitignore immediately!
```

**CRITICAL SECURITY CHECK:**
```bash
# Ensure .env is in .gitignore
grep -q "^\.env$" ../../.gitignore || echo ".env" >> ../../.gitignore

# Verify .env has correct permissions (not world-readable)
chmod 600 .env
ls -la .env
# Should show: -rw------- (only owner can read/write)
```

#### Step 2.3: Validate Python Dependencies
```bash
# Activate virtual environment (if used)
source venv/bin/activate  # Adjust path if different

# Install/update required packages
pip3 install -r requirements.txt

# Verify critical packages installed
python3 -c "import paho.mqtt.client as mqtt; import pydantic; print('✅ Dependencies OK')"
```

#### Step 2.4: Test Configuration Loading
```bash
# Test that config loads credentials correctly
python3 -c "
from config import SystemConfig
config = SystemConfig()
print(f'✅ Config loaded successfully')
print(f'MQTT Broker: {config.mqtt_broker}:{config.mqtt_port}')
print(f'MQTT Username: {config.mqtt_username}')
print('MQTT Password: [REDACTED]')
"

# Expected output:
# ✅ Config loaded successfully
# MQTT Broker: 192.168.0.110:1883
# MQTT Username: solar_heating_user
# MQTT Password: [REDACTED]

# If error "MQTT credentials required": Check .env file exists and has values
```

---

### Phase 3: System Validation (10 minutes)

#### Step 3.1: Dry Run Test
```bash
# Run system in test mode (if available) or short duration
# This tests MQTT connection without starting full system

python3 -c "
from config import SystemConfig
from mqtt_handler import MQTTHandler
import time

config = SystemConfig()
mqtt = MQTTHandler(config)
print('Attempting MQTT connection...')
if mqtt.connect():
    print('✅ MQTT connection successful with authentication')
    mqtt.disconnect()
else:
    print('❌ MQTT connection failed - check credentials')
    exit(1)
"

# Expected output:
# Attempting MQTT connection...
# ✅ MQTT connection successful with authentication
```

#### Step 3.2: Start System
```bash
# Stop existing system (if running)
sudo systemctl stop solar-heating  # Adjust service name as needed

# Or if running in screen/tmux:
# screen -r solar_heating
# Ctrl+C to stop

# Start system with logging
python3 main_system.py 2>&1 | tee system_startup.log

# Watch for authentication messages in log:
# "MQTT Connection Successful - Broker: 192.168.0.110:1883, User: solar_heating_user"
```

#### Step 3.3: Verify Logs for Successful Authentication
```bash
# Check system logs for successful MQTT connection
grep -i "mqtt" system_startup.log | head -20

# Look for success indicators:
# ✅ "MQTT Connection Successful"
# ✅ "Broker: 192.168.0.110:1883"
# ✅ "User: solar_heating_user"

# Check for authentication failures (should be none):
grep -i "auth" system_startup.log | grep -i "fail\|error"
# Expected: No output (no auth failures)
```

---

### Phase 4: Security Verification (10 minutes)

#### Step 4.1: Test Unauthorized Access Prevention
```bash
# From a different terminal/machine, attempt connection without credentials
mosquitto_sub -h 192.168.0.110 -p 1883 -t solar/# 

# Expected result: Connection refused / not authorized
# ✅ This confirms anonymous access is blocked

# Test with wrong credentials
mosquitto_sub -h 192.168.0.110 -p 1883 -t solar/# -u wrong_user -P wrong_pass

# Expected result: Connection refused / not authorized
# ✅ This confirms invalid credentials are rejected
```

#### Step 4.2: Verify System Logs Show Auth Enforcement
```bash
# Check mosquitto logs for rejected connections
sudo tail -50 /var/log/mosquitto/mosquitto.log | grep -i "denied\|refused\|not authorized"

# Should see entries like:
# "New connection from X.X.X.X:XXXXX"
# "Client ID not provided, disconnecting"
# Or: "Bad username or password"

# This confirms broker is rejecting unauthorized connections
```

#### Step 4.3: Monitor System Operation
```bash
# Let system run for 5-10 minutes
# Monitor for:
# 1. Successful MQTT publishes (sensor data, status updates)
# 2. No authentication errors
# 3. Normal system operation

# Check system status
tail -f system_startup.log

# Look for normal operation indicators:
# - Temperature readings published
# - Heater control messages sent
# - No MQTT disconnections

# After 10 minutes, if no errors:
echo "✅ System operating normally with authentication"
```

---

## Post-Deployment Verification

### Checklist
- [ ] MQTT broker enforcing authentication
- [ ] Anonymous connections rejected
- [ ] Invalid credentials rejected  
- [ ] Valid credentials accepted
- [ ] System connecting successfully
- [ ] No authentication errors in logs
- [ ] Normal system operations confirmed
- [ ] Sensor data being published
- [ ] Heater control working

### Success Criteria
✅ All checklist items marked complete  
✅ No authentication-related errors in logs  
✅ System operating for 10+ minutes without issues  
✅ Manual security test shows unauthorized access blocked  

---

## Monitoring and Maintenance

### Daily Monitoring
```bash
# Check for authentication failures (possible attacks)
sudo grep -i "not authorized\|bad username\|auth.*fail" /var/log/mosquitto/mosquitto.log | tail -20

# If seeing many failures from same IP, consider firewall rules
```

### Weekly Maintenance
- Review MQTT logs for unusual patterns
- Verify system uptime and stability
- Check for software updates

### Monthly Security Review
- Rotate MQTT credentials (recommended every 90 days)
- Review access logs for security incidents
- Update to latest software versions
- Verify backup and recovery procedures

---

## Rollback Procedure

If deployment causes issues, follow this rollback:

### Quick Rollback (5 minutes)
```bash
# 1. Restore mosquitto configuration
sudo cp /etc/mosquitto/mosquitto.conf.backup-YYYYMMDD /etc/mosquitto/mosquitto.conf
sudo systemctl restart mosquitto

# 2. Revert code changes
cd /opt/solar_heating_system
git checkout <previous_commit_hash>

# 3. Restart system
sudo systemctl restart solar-heating
```

### Full Rollback (15 minutes)
```bash
# 1. Stop system
sudo systemctl stop solar-heating

# 2. Restore ALL backups
sudo cp /etc/mosquitto/mosquitto.conf.backup-YYYYMMDD /etc/mosquitto/mosquitto.conf
sudo cp /etc/mosquitto/passwd.backup-YYYYMMDD /etc/mosquitto/passwd 2>/dev/null || true
sudo systemctl restart mosquitto

# 3. Revert code to pre-Issue-44 state
cd /opt/solar_heating_system
git checkout <commit_before_issue_44>

# 4. Restore previous .env (if exists)
cp .env.backup .env 2>/dev/null || true

# 5. Restart system
sudo systemctl restart solar-heating

# 6. Verify system operational
sudo systemctl status solar-heating
tail -f /var/log/solar_heating/system.log  # Adjust path as needed
```

---

## Troubleshooting

### Issue: "MQTT credentials required" error

**Symptoms:**
```
pydantic_core._pydantic_core.ValidationError: MQTT credentials required
```

**Solution:**
```bash
# Check .env file exists and has values
cat .env | grep MQTT

# Verify environment variables loaded
python3 -c "import os; print(os.getenv('MQTT_USERNAME'), os.getenv('MQTT_PASSWORD'))"

# If None/None, create/edit .env file
nano .env
```

### Issue: "Connection refused" or "not authorized"

**Symptoms:**
- System logs show MQTT connection failures
- Return code 4 or 5 in logs

**Solution:**
```bash
# 1. Verify credentials match between .env and mosquitto
cat .env | grep MQTT_USERNAME
sudo cat /etc/mosquitto/passwd

# 2. Test credentials manually
mosquitto_sub -h 192.168.0.110 -p 1883 -t test -u <username_from_env> -P <password_from_env>

# 3. If manual test fails, recreate MQTT user
sudo mosquitto_passwd -b /etc/mosquitto/passwd <username> <password>
sudo systemctl restart mosquitto
```

### Issue: System connects but publishes fail

**Symptoms:**
- Initial connection successful
- Publishes fail with auth errors

**Solution:**
```bash
# Check mosquitto ACL configuration (if enabled)
sudo cat /etc/mosquitto/acl

# Ensure user has publish permissions:
# user solar_heating_user
# topic write solar/#

# Restart mosquitto after ACL changes
sudo systemctl restart mosquitto
```

### Issue: Mosquitto won't start after configuration change

**Symptoms:**
```
sudo systemctl status mosquitto
Active: failed
```

**Solution:**
```bash
# Check configuration syntax
sudo mosquitto -c /etc/mosquitto/mosquitto.conf -v

# Common issues:
# 1. Typo in configuration file
# 2. Password file path incorrect
# 3. Permissions on password file

# Check password file permissions
sudo ls -la /etc/mosquitto/passwd
# Should be: -rw-r----- root mosquitto

# Fix permissions if needed
sudo chown mosquitto:mosquitto /etc/mosquitto/passwd
sudo chmod 640 /etc/mosquitto/passwd

# Restart service
sudo systemctl restart mosquitto
```

---

## Security Best Practices

### Credential Management
1. ✅ Use strong passwords (20+ characters, random)
2. ✅ Store in secure credential manager
3. ✅ Never commit .env to git
4. ✅ Set .env permissions to 600
5. ✅ Rotate credentials every 90 days

### MQTT Broker Security
1. ✅ Disable anonymous access
2. ✅ Use password authentication
3. ⚠️ Consider TLS/SSL encryption (port 8883)
4. ⚠️ Implement ACL for topic-level permissions
5. ⚠️ Rate limit connections (future enhancement)

### Monitoring
1. ✅ Log all authentication attempts
2. ✅ Monitor for repeated failures
3. ✅ Alert on suspicious patterns
4. ⚠️ Integrate with SIEM (future enhancement)

---

## Next Steps After Deployment

### Immediate (Within 24 hours)
- [ ] Document actual production credentials (in secure vault)
- [ ] Update system documentation with new auth requirements
- [ ] Notify team of successful deployment
- [ ] Schedule follow-up review in 1 week

### Short-term (Within 1 month)
- [ ] Implement TLS/SSL encryption (Issue: create new)
- [ ] Add rate limiting for failed auth attempts (Issue #47 related)
- [ ] Set up automated security alerts
- [ ] Create credential rotation procedure

### Long-term (Within 3 months)
- [ ] Consider certificate-based authentication
- [ ] Implement automated credential rotation
- [ ] Add multi-factor authentication (if applicable)
- [ ] Security audit and penetration testing

---

## Related Documentation

- `ISSUE_44_TEST_RESULTS.md` - Test execution results
- `ISSUE_44_STATUS_ANALYSIS.md` - Implementation analysis
- `python/v3/docs/requirements/ISSUE_44_MQTT_AUTH_REQUIREMENTS.md` - Requirements
- `python/v3/docs/architecture/ISSUE_44_MQTT_AUTH_ARCHITECTURE.md` - Architecture
- `.env.example` - Environment variable template

---

## Support and Contact

**Issue Tracking:** GitHub Issue #44  
**Documentation:** `/python/v3/docs/` directory  
**Emergency Rollback:** See "Rollback Procedure" section above  

---

**Deployment Guide Version:** 1.0  
**Last Updated:** February 14, 2026  
**Author:** AI Development Team  
**Status:** Ready for Production Deployment
