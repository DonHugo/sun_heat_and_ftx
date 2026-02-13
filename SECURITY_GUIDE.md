# Security Guide - Solar Heating System v3

**Issue #45 Remediation**: This guide documents the security improvements made to remove hardcoded credentials.

## 🔐 Overview

All MQTT credentials and sensitive information have been removed from the codebase and must now be provided via environment variables. This prevents credential exposure in version control and allows for proper secrets management.

## 🚨 Critical Security Changes (Issue #45)

### What Was Fixed

**Before (INSECURE):**
- MQTT credentials hardcoded in 16 files
- Username: `mqtt_beaches` 
- Password: `uQX6NiZ.7R`
- Exposed in git history

**After (SECURE):**
- All credentials loaded from environment variables
- No default credentials in code
- System fails fast if credentials missing
- `.env` files properly excluded from git

### Files Modified

**Python v3 (Production):**
1. `python/v3/watchdog_enhanced.py` - Enhanced watchdog system
2. `python/v3/watchdog.py` - Standard watchdog system
3. `python/v3/get_mode_status.py` - Mode status utility
4. `python/v3/monitor_mode_changes.py` - Mode change monitor
5. `python/v3/test_mode_changes.py` - Mode change tests
6. `python/v3/test_heartbeat_simple.py` - Heartbeat tests

**Python v2 & v1 (Legacy):**
7. `python/v2/config.py` - v2 configuration
8. `python/v1/temperature_monitoring.py` - v1 temperature monitor

**Configuration:**
9. `python/v3/docker-compose.yml` - Docker configuration
10. `config/mcp.json` - MCP server configuration

**Security Files:**
11. `.gitignore` - Enhanced secret exclusion patterns
12. `.env.example` - Template for environment variables (NEW)

---

## 📋 Setup Instructions

### 1. Create Environment File

Copy the example template:
```bash
cp .env.example .env
```

### 2. Configure Credentials

Edit `.env` and set your actual credentials:
```bash
# Required credentials
MQTT_USERNAME=your_actual_username
MQTT_PASSWORD=your_actual_password
MQTT_BROKER=192.168.0.110
MQTT_PORT=1883

# Optional configuration
INFLUXDB_TOKEN=your_influxdb_token
TASKMASTER_API_KEY=your_taskmaster_key
```

### 3. Verify Security

**CRITICAL**: Ensure `.env` is never committed:
```bash
# Check .env is in .gitignore
grep -q "^\.env$" .gitignore && echo "✅ .env protected" || echo "❌ WARNING: .env not in .gitignore!"

# Verify .env not tracked by git
git check-ignore .env && echo "✅ .env ignored by git" || echo "❌ WARNING: .env may be tracked!"
```

### 4. Load Environment Variables

**For direct Python execution:**
```bash
# Load from .env file (requires python-dotenv)
python3 -c "from dotenv import load_dotenv; load_dotenv()"
python3 your_script.py

# Or export manually
export $(cat .env | grep -v '^#' | xargs)
```

**For Docker:**
```bash
# Docker Compose automatically loads .env
docker-compose up -d
```

**For systemd services:**
```bash
# Add to service file
[Service]
EnvironmentFile=/path/to/.env
```

---

## 🔄 Credential Rotation

### When to Rotate

- **Immediately**: If credentials were exposed or compromised
- **Regularly**: Every 90 days (recommended)
- **After**: Team member departure
- **Before**: Production deployment

### Rotation Procedure

1. **Generate New Credentials**
```bash
# Generate strong password
openssl rand -base64 32
```

2. **Update MQTT Broker**
   - Add new user credentials to MQTT broker
   - OR update existing user's password

3. **Update .env File**
```bash
# Backup old credentials (temporarily)
cp .env .env.backup

# Update .env with new credentials
nano .env
```

4. **Test Connectivity**
```bash
# Test MQTT connection
python3 python/v3/test_heartbeat_simple.py
```

5. **Deploy Changes**
```bash
# Restart services
docker-compose restart
# OR for systemd
sudo systemctl restart solar_heating_v3
```

6. **Verify Operation**
```bash
# Check logs
tail -f /var/log/solar_heating_watchdog.log

# Check MQTT connection status
docker-compose logs -f solar-heating-v3 | grep "MQTT"
```

7. **Revoke Old Credentials**
   - Remove old user from MQTT broker
   - OR disable old password

8. **Cleanup**
```bash
# Securely delete backup
shred -u .env.backup
```

---

## 🔍 Security Audit Checklist

### Pre-Deployment

- [ ] `.env` file exists and contains all required credentials
- [ ] `.env` is listed in `.gitignore`
- [ ] `.env` is NOT tracked by git (`git status` shows nothing)
- [ ] No hardcoded credentials in source code
- [ ] All Python files pass syntax check
- [ ] Docker containers start successfully
- [ ] MQTT authentication works

### Regular Audits

```bash
# Check for exposed secrets in code
grep -r "password\|secret\|api.key" --include="*.py" . | grep -v "\.env"

# Check git history for leaked secrets (use git-secrets tool)
git secrets --scan

# Verify environment variables are loaded
docker-compose config | grep MQTT_
```

---

## 🚫 Common Mistakes to Avoid

1. **❌ DON'T** commit `.env` files
   ```bash
   git add .env  # NEVER DO THIS!
   ```

2. **❌ DON'T** use default/example credentials in production
   ```bash
   MQTT_PASSWORD=change_me_in_production  # Bad!
   ```

3. **❌ DON'T** log credentials
   ```python
   logger.info(f"Password: {password}")  # Never log secrets!
   ```

4. **❌ DON'T** share credentials via email/slack
   - Use secure password manager
   - Use encrypted channels

5. **❌ DON'T** reuse credentials across environments
   - Production ≠ Development ≠ Testing

---

## 🛡️ Defense in Depth

### Layer 1: Environment Variables
- Credentials in `.env` file (not in code)
- `.env` excluded from version control

### Layer 2: Validation
- System validates credentials at startup
- Fails fast if credentials missing
- Clear error messages

### Layer 3: Access Control
- MQTT broker authentication enabled
- User-level permissions configured
- Network segmentation (firewall rules)

### Layer 4: Monitoring
- Log authentication failures
- Alert on repeated auth failures
- Audit credential usage

### Layer 5: Secrets Management (Production)
Consider using:
- **HashiCorp Vault** - Enterprise secrets management
- **AWS Secrets Manager** - Cloud-native secrets
- **Azure Key Vault** - Azure secrets management
- **Kubernetes Secrets** - Container orchestration secrets

---

## 📚 Additional Resources

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [NIST Password Guidelines](https://pages.nist.gov/800-63-3/)
- [Mozilla Security Guidelines](https://infosec.mozilla.org/guidelines/)

---

## 📝 Version History

- **v1.0.0** (2026-02-14): Initial security guide (Issue #45 remediation)
  - Removed all hardcoded credentials
  - Implemented environment variable loading
  - Enhanced .gitignore patterns
  - Created .env.example template

---

## 🆘 Emergency Response

### If Credentials Are Compromised

1. **Immediate Actions** (within 1 hour):
   - Rotate compromised credentials immediately
   - Check access logs for unauthorized access
   - Disable compromised accounts

2. **Short-term Actions** (within 24 hours):
   - Audit all systems for breach indicators
   - Review git history for credential exposure
   - Notify affected parties if required

3. **Long-term Actions** (within 1 week):
   - Implement additional security measures
   - Conduct security training
   - Update incident response procedures

### Contact

For security issues:
- **DO NOT** open public GitHub issues
- Contact: [Your security contact email]
- PGP Key: [Your PGP key fingerprint]

