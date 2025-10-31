# Production Environment Documentation

**Last Updated:** October 31, 2025  
**Owner:** @coach  
**Status:** Active Production Environment

---

## 📍 Environment Overview

### Server Details
- **Device:** Raspberry Pi 4
- **Hostname:** `rpi-solfangare-2`
- **IP Address:** `192.168.0.18`
- **OS:** Raspberry Pi OS (Debian-based)
- **Architecture:** ARM64 (aarch64)

### Access
```bash
# SSH Access
ssh pi@192.168.0.18

# User:** pi
# Authentication: SSH key
```

---

## 🐍 Python Environment

### System Python
- **Location:** `/usr/bin/python3`
- **Version:** 3.11.x (system default)
- **Usage:** NOT used for production service

### Production Virtual Environment ⭐
- **Location:** `/opt/solar_heating_v3`
- **Python:** `/opt/solar_heating_v3/bin/python3`
- **Pip:** `/opt/solar_heating_v3/bin/pip3`
- **Version:** Python 3.11.x
- **Purpose:** Isolated environment for solar heating service

**Why Separate Venv?**
- Isolation from system Python
- Prevents dependency conflicts
- Easier dependency management
- System updates don't break service

---

## 📦 Package Management

### Installing Packages in Production

**❌ WRONG (System Python):**
```bash
pip3 install package_name
python3 -m pip install package_name
```

**✅ RIGHT (Production Venv):**
```bash
/opt/solar_heating_v3/bin/pip3 install package_name --break-system-packages
```

### Why `--break-system-packages`?
Modern Debian/Raspberry Pi OS requires this flag for system-wide pip installs in venvs to prevent accidental system modifications.

### Installing from requirements.txt
```bash
# On Raspberry Pi
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 install -r ~/solar_heating/python/v3/requirements.txt --break-system-packages"
```

### Verifying Installed Packages
```bash
# List all packages in production venv
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 list"

# Check specific package
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 show flask"

# Use verification script
./scripts/verify_deps.sh
```

---

## 📁 Directory Structure

### Code Location
```
/home/pi/solar_heating/
├── python/
│   └── v3/
│       ├── main_system.py       # Main service entry point
│       ├── api_server.py         # Flask API server
│       ├── api_models.py         # Pydantic validation models
│       ├── config.py             # Configuration
│       ├── hardware_interface.py # Hardware abstraction
│       ├── mqtt_handler.py       # MQTT client
│       ├── requirements.txt      # Python dependencies
│       ├── tests/                # Test suite
│       └── docs/                 # Documentation
├── scripts/                      # Utility scripts
└── docs/                         # Project documentation
```

### Important Paths
- **Code:** `~/solar_heating/python/v3`
- **Logs:** `/tmp/solar_heating/logs/`
- **Config:** `~/solar_heating/python/v3/config.py`
- **Venv:** `/opt/solar_heating_v3`

---

## ⚙️ Systemd Service

### Service Configuration
- **Service Name:** `solar_heating_v3.service`
- **Unit File:** `/etc/systemd/system/solar_heating_v3.service`
- **Type:** Simple (long-running process)
- **User:** pi
- **Working Directory:** `/home/pi/solar_heating/python/v3`
- **Python:** `/opt/solar_heating_v3/bin/python3`

### Service Commands
```bash
# Check status
sudo systemctl status solar_heating_v3.service

# Start service
sudo systemctl start solar_heating_v3.service

# Stop service
sudo systemctl stop solar_heating_v3.service

# Restart service
sudo systemctl restart solar_heating_v3.service

# View logs (live)
sudo journalctl -u solar_heating_v3.service -f

# View logs (last 50 lines)
sudo journalctl -u solar_heating_v3.service -n 50 --no-pager

# View logs since time
sudo journalctl -u solar_heating_v3.service --since "10 minutes ago"
```

### Service Auto-Start
- **Enabled:** Yes
- **Starts on boot:** Yes
- **Restart on failure:** Yes (configured in unit file)

---

## 🔧 Key Dependencies

### Production Packages (in venv)

#### Core Functionality
- `paho-mqtt` - MQTT client for communication
- `w1thermsensor` - 1-Wire temperature sensor interface
- `RPi.GPIO` - GPIO control (or compatible library)

#### API Server (Issue #43)
- `flask==3.1.2` - Web framework
- `flask-restful==0.3.10` - REST API framework
- `pydantic==2.11.7` - Data validation

#### TaskMaster AI
- `aiohttp` - Async HTTP client
- Other AI-related packages

#### Utilities
- `python-dotenv` - Environment variable management
- Various logging and monitoring tools

### System Dependencies
- Temperature sensor drivers (1-Wire)
- MQTT broker access (external)
- GPIO hardware access

---

## 🌐 Network Configuration

### API Server
- **Port:** 5001
- **Host:** 0.0.0.0 (all interfaces)
- **Protocol:** HTTP
- **Access:** Local network only (not exposed to internet)

### MQTT Broker
- **External Service:** (configuration in config.py)
- **Port:** Typically 1883 (MQTT) or 8883 (MQTT over TLS)
- **Topics:** Various (solar heating telemetry)

### Home Assistant Integration
- **Protocol:** MQTT
- **Discovery:** Automatic via MQTT discovery protocol

---

## 🔍 Testing & Validation

### Test Scripts
```bash
# Test production environment
./scripts/test_production_env.sh

# Verify dependencies
./scripts/verify_deps.sh
```

### Manual Testing
```bash
# Test imports with production Python
ssh pi@192.168.0.18 "cd ~/solar_heating/python/v3 && /opt/solar_heating_v3/bin/python3 -c 'import api_server; print(\"✅ OK\")'"

# Test API server (if running)
ssh pi@192.168.0.18 "curl -s http://localhost:5001/api/status | head -20"

# Check service logs for errors
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service --since '5 minutes ago' | grep -i error"
```

---

## 📊 Monitoring

### Service Health
```bash
# Quick health check
ssh pi@192.168.0.18 "systemctl is-active solar_heating_v3.service && echo '✅ Service Running' || echo '❌ Service Down'"
```

### Resource Usage
```bash
# CPU and memory usage
ssh pi@192.168.0.18 "top -b -n 1 | head -20"

# Disk space
ssh pi@192.168.0.18 "df -h /"
```

### Log Monitoring
```bash
# Watch logs in real-time
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service -f"

# Check for errors
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service --since '1 hour ago' | grep -i 'error\|failed\|exception'"
```

---

## 🚀 Deployment Process

### Standard Deployment Steps

1. **Backup Current State**
   ```bash
   ssh pi@192.168.0.18 "cd ~/solar_heating && git log --oneline -1"
   ```

2. **Pull Latest Code**
   ```bash
   ssh pi@192.168.0.18 "cd ~/solar_heating && git pull"
   ```

3. **Install New Dependencies (if any)**
   ```bash
   ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 install -r ~/solar_heating/python/v3/requirements.txt --break-system-packages"
   ```

4. **Restart Service**
   ```bash
   ssh pi@192.168.0.18 "sudo systemctl restart solar_heating_v3.service"
   ```

5. **Verify Service Started**
   ```bash
   ssh pi@192.168.0.18 "sleep 5 && sudo systemctl status solar_heating_v3.service --no-pager | head -20"
   ```

6. **Check for Errors**
   ```bash
   ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service --since '2 minutes ago' | grep -i error"
   ```

### See Also
- [Deployment Runbook](DEPLOYMENT_RUNBOOK.md) - Detailed step-by-step guide
- [Pre-Deployment Checklist](PRE_DEPLOYMENT_CHECKLIST.md) - Pre-deployment verification

---

## 🔙 Rollback Procedure

### Quick Rollback
```bash
# 1. SSH to Pi
ssh pi@192.168.0.18

# 2. Go to code directory
cd ~/solar_heating

# 3. Rollback to previous commit
git log --oneline -5  # Find commit to rollback to
git checkout <commit-hash> python/v3/

# 4. Restart service
sudo systemctl restart solar_heating_v3.service

# 5. Verify
sudo systemctl status solar_heating_v3.service
```

### Full Repository Rollback
```bash
ssh pi@192.168.0.18 "cd ~/solar_heating && git reset --hard <commit-hash> && sudo systemctl restart solar_heating_v3.service"
```

---

## ⚠️ Common Issues & Solutions

### Issue 1: ModuleNotFoundError

**Symptom:**
```
ModuleNotFoundError: No module named 'flask'
```

**Cause:** Package not installed in production venv

**Solution:**
```bash
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 install flask --break-system-packages"
```

### Issue 2: Service Won't Start

**Symptom:** Service status shows "failed"

**Diagnosis:**
```bash
# Check logs for error
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service -n 50 --no-pager"
```

**Common Causes:**
- Syntax errors in Python code
- Missing dependencies
- Configuration errors
- Hardware access issues

**Solution:** Fix the underlying issue, then restart

### Issue 3: Import Works Locally But Not in Production

**Cause:** Testing with system Python instead of production venv

**Solution:** Always test with production Python:
```bash
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/python3 -c 'import module'"
```

### Issue 4: Git Pull Conflicts

**Symptom:** `git pull` reports conflicts

**Solution:**
```bash
ssh pi@192.168.0.18 "cd ~/solar_heating && git stash && git pull && git stash pop"
```

Or for uncommitted local changes you want to discard:
```bash
ssh pi@192.168.0.18 "cd ~/solar_heating && git reset --hard HEAD && git pull"
```

---

## 📝 Configuration Management

### Configuration Files
- **Main Config:** `python/v3/config.py`
- **Environment Variables:** `.env` (if used)
- **Service Config:** `/etc/systemd/system/solar_heating_v3.service`

### Changing Configuration
1. Edit configuration file
2. Commit and push changes (if tracking in git)
3. Pull on Raspberry Pi
4. Restart service

### Secrets Management
- **DO NOT** commit secrets to git
- Use environment variables
- Store in `.env` file (excluded from git)
- Or use external secrets management

---

## 🔐 Security Considerations

### Access Control
- SSH key authentication only
- No password authentication
- Limited to local network

### Service Permissions
- Runs as `pi` user (not root)
- Requires sudo for hardware access (GPIO, sensors)
- Service configured with appropriate permissions

### API Security
- API runs on local network only
- Input validation via Pydantic (Issue #43)
- Rate limiting recommended (future enhancement)

---

## 📞 Quick Reference

### Most Common Commands
```bash
# Deploy new code
ssh pi@192.168.0.18 "cd ~/solar_heating && git pull && sudo systemctl restart solar_heating_v3.service"

# Check service status
ssh pi@192.168.0.18 "sudo systemctl status solar_heating_v3.service"

# View logs
ssh pi@192.168.0.18 "sudo journalctl -u solar_heating_v3.service -f"

# Test API
ssh pi@192.168.0.18 "curl -s http://localhost:5001/api/status"

# Install package
ssh pi@192.168.0.18 "/opt/solar_heating_v3/bin/pip3 install <package> --break-system-packages"

# Verify environment
./scripts/test_production_env.sh
```

---

## 🎯 Best Practices

1. **Always use production Python environment** - `/opt/solar_heating_v3/bin/python3`
2. **Test locally before deploying** - Use pre-deployment checklist
3. **Verify after deployment** - Check service status and logs
4. **Keep rollback plan ready** - Know the last good commit
5. **Monitor after deployment** - Watch logs for 5-10 minutes
6. **Document changes** - Update this doc when environment changes

---

## 📚 Related Documentation

- [Pre-Deployment Checklist](PRE_DEPLOYMENT_CHECKLIST.md)
- [Deployment Runbook](DEPLOYMENT_RUNBOOK.md)
- [Multi-Agent Guide](../../MULTI_AGENT_GUIDE.md)
- [Test Scripts](../../scripts/)

---

**Questions or Issues?**
- Check the troubleshooting section above
- Review service logs
- Ask @manager or @coach for help

*Last Updated: October 31, 2025 by @coach*

