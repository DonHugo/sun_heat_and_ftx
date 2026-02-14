# Local Test Deployment - MQTT Authentication

**Date**: 2026-02-14  
**Purpose**: Test Issue #44 MQTT authentication in local environment before production deployment  
**Status**: IN PROGRESS

---

## Overview

This document guides the setup of a local test environment with MQTT authentication to validate Issue #44 implementation before deploying to production.

**Environment**: macOS with Homebrew mosquitto  
**Risk Level**: ZERO (local testing only)  
**Estimated Time**: 15-20 minutes

---

## Prerequisites

✅ **Verified**:
- mosquitto 2.0.22 installed (`/opt/homebrew/sbin/mosquitto`)
- mosquitto_pub, mosquitto_sub, mosquitto_passwd available
- Python 3.9.6 environment ready
- Git repository up to date

---

## Phase 1: Local MQTT Broker Setup

### Step 1.1: Create Test Configuration Directory

```bash
# Create local test config directory
mkdir -p ~/mosquitto-test/config
mkdir -p ~/mosquitto-test/data
mkdir -p ~/mosquitto-test/log

# Set permissions
chmod 755 ~/mosquitto-test
chmod 755 ~/mosquitto-test/config
chmod 755 ~/mosquitto-test/data
chmod 755 ~/mosquitto-test/log
```

### Step 1.2: Create Test User Credentials

```bash
# Generate test password
TEST_PASSWORD=$(openssl rand -base64 20)
echo "Generated test password: $TEST_PASSWORD"
echo "SAVE THIS PASSWORD - you'll need it for .env configuration"

# Create password file with test user
mosquitto_passwd -c -b ~/mosquitto-test/config/passwd solar_test_user "$TEST_PASSWORD"

# Verify password file created
cat ~/mosquitto-test/config/passwd
# Should show: solar_test_user:$encrypted_hash

# Save credentials for reference
echo "TEST_CREDENTIALS_FILE" > ~/mosquitto-test/credentials.txt
echo "Username: solar_test_user" >> ~/mosquitto-test/credentials.txt
echo "Password: $TEST_PASSWORD" >> ~/mosquitto-test/credentials.txt
chmod 600 ~/mosquitto-test/credentials.txt

echo "✅ Test credentials saved to ~/mosquitto-test/credentials.txt"
```

### Step 1.3: Create Test Mosquitto Configuration

```bash
cat > ~/mosquitto-test/config/mosquitto.conf << 'MQTTCONF'
# Local Test MQTT Broker Configuration
# For Issue #44 authentication testing

# Listener configuration
listener 1883 127.0.0.1
protocol mqtt

# Authentication (CRITICAL)
allow_anonymous false
password_file /Users/hafs/mosquitto-test/config/passwd

# Persistence
persistence true
persistence_location /Users/hafs/mosquitto-test/data/

# Logging
log_dest file /Users/hafs/mosquitto-test/log/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information

# Connection logging
connection_messages true

# Security
max_connections 100
MQTTCONF

echo "✅ Mosquitto test configuration created"
```

### Step 1.4: Start Local Test Broker

```bash
# Start mosquitto in test mode (foreground, verbose)
echo "Starting mosquitto test broker..."
echo "Press Ctrl+C to stop when done testing"
echo ""

mosquitto -c ~/mosquitto-test/config/mosquitto.conf -v
```

**Expected Output**:
```
1708074000: mosquitto version 2.0.22 starting
1708074000: Config loaded from ~/mosquitto-test/config/mosquitto.conf
1708074000: Opening ipv4 listen socket on port 1883.
1708074000: mosquitto version 2.0.22 running
```

**Note**: Leave this running in this terminal. Open a new terminal for next steps.

---

## Phase 2: Test Authentication

### Step 2.1: Test with Valid Credentials

```bash
# Open NEW TERMINAL

# Load test credentials
TEST_USER="solar_test_user"
TEST_PASS=$(grep "Password:" ~/mosquitto-test/credentials.txt | cut -d' ' -f2)

echo "Testing with valid credentials..."

# Subscribe to test topic (runs in background)
mosquitto_sub -h 127.0.0.1 -p 1883 -t test/auth -u "$TEST_USER" -P "$TEST_PASS" &
SUB_PID=$!

sleep 2

# Publish test message
mosquitto_pub -h 127.0.0.1 -p 1883 -t test/auth -m "Authentication test message" -u "$TEST_USER" -P "$TEST_PASS"

sleep 1

# Cleanup
kill $SUB_PID 2>/dev/null

echo "✅ If you saw the test message above, authentication is working!"
```

### Step 2.2: Test with Invalid Credentials (Should Fail)

```bash
# This should fail with "Connection Refused: not authorized"
echo "Testing with INVALID credentials (should fail)..."

mosquitto_sub -h 127.0.0.1 -p 1883 -t test/auth -u "wrong_user" -P "wrong_pass" 2>&1 | head -5

echo "✅ If you saw 'Connection Refused' or 'not authorized', security is working!"
```

### Step 2.3: Test Anonymous Access (Should Fail)

```bash
# This should fail because allow_anonymous is false
echo "Testing anonymous access (should fail)..."

mosquitto_sub -h 127.0.0.1 -p 1883 -t test/auth 2>&1 | head -5

echo "✅ If connection was refused, anonymous blocking is working!"
```

---

## Phase 3: Configure Application

### Step 3.1: Create Local Test .env File

```bash
cd /Users/hafs/Documents/Github/sun_heat_and_ftx/python/v3

# Load test credentials
TEST_USER="solar_test_user"
TEST_PASS=$(grep "Password:" ~/mosquitto-test/credentials.txt | cut -d' ' -f2)

# Create .env file with test credentials
cat > .env << ENVEOF
# Local Test Environment - MQTT Authentication
# Generated: $(date)
# DO NOT COMMIT THIS FILE

# MQTT Broker Configuration (Local Test)
MQTT_USERNAME=${TEST_USER}
MQTT_PASSWORD=${TEST_PASS}
MQTT_BROKER=127.0.0.1
MQTT_PORT=1883

# System Configuration
SYSTEM_MODE=auto
LOG_LEVEL=DEBUG
DEBUG=true

# Note: This is for LOCAL TESTING ONLY
# Production will use different credentials
ENVEOF

# Secure the file
chmod 600 .env

# Verify .env is gitignored
if ! git check-ignore .env > /dev/null 2>&1; then
    echo "⚠️  WARNING: .env is not in .gitignore!"
    echo "Adding .env to .gitignore..."
    echo ".env" >> ../../.gitignore
fi

echo "✅ Local test .env created with secure permissions"
cat .env
```

### Step 3.2: Verify Python Can Load Configuration

```bash
cd /Users/hafs/Documents/Github/sun_heat_and_ftx/python/v3

# Test loading configuration
python3 << 'PYEOF'
import os
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Verify variables loaded
username = os.getenv('MQTT_USERNAME')
password = os.getenv('MQTT_PASSWORD')
broker = os.getenv('MQTT_BROKER')
port = os.getenv('MQTT_PORT')

print("✅ Environment variables loaded:")
print(f"   Username: {username}")
print(f"   Password: {'*' * len(password) if password else 'NOT SET'}")
print(f"   Broker: {broker}")
print(f"   Port: {port}")

if not all([username, password, broker, port]):
    print("❌ ERROR: Missing required environment variables")
    exit(1)

print("\n✅ All required credentials present")
PYEOF

echo ""
echo "✅ Configuration loading successful"
```

---

## Phase 4: Test MQTT Authenticator

### Step 4.1: Test MQTTAuthenticator Class

```bash
cd /Users/hafs/Documents/Github/sun_heat_and_ftx/python/v3

# Test the authenticator directly
python3 << 'PYEOF'
import os
from dotenv import load_dotenv
from mqtt_authenticator import MQTTAuthenticator

# Load environment
load_dotenv()

# Create authenticator
print("Creating MQTTAuthenticator...")
auth = MQTTAuthenticator()

print(f"✅ Authenticator created")
print(f"   Username: {auth.username}")
print(f"   Password: {'*' * 10}")
print(f"   Broker: {auth.broker}:{auth.port}")

# Test credential validation
print("\nValidating credentials...")
is_valid = auth.validate_credentials()
print(f"✅ Credentials valid: {is_valid}")

# Test connection
print("\nTesting MQTT connection...")
client = auth.create_authenticated_client(client_id="test_client")
print(f"✅ Authenticated client created")

try:
    client.connect(auth.broker, auth.port, 60)
    print("✅ Connection successful!")
    client.disconnect()
    print("✅ Disconnection successful!")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    exit(1)

print("\n✅ All authenticator tests passed!")
PYEOF
```

### Step 4.2: Test MQTT Handler Integration

```bash
cd /Users/hafs/Documents/Github/sun_heat_and_ftx/python/v3

# Test MQTT handler with authentication
python3 << 'PYEOF'
import os
import time
from dotenv import load_dotenv
from mqtt_handler import MQTTHandler

# Load environment
load_dotenv()

print("Creating MQTTHandler with authentication...")
try:
    handler = MQTTHandler()
    print("✅ MQTTHandler created")
    
    print("\nConnecting to broker...")
    handler.connect()
    print("✅ Connected successfully")
    
    # Wait a moment for connection to stabilize
    time.sleep(2)
    
    print("\nPublishing test message...")
    success = handler.publish("test/integration", {"test": "authenticated_message"})
    print(f"✅ Publish successful: {success}")
    
    time.sleep(1)
    
    print("\nDisconnecting...")
    handler.disconnect()
    print("✅ Disconnected successfully")
    
    print("\n✅ All MQTT handler tests passed!")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
    exit(1)
PYEOF
```

---

## Phase 5: Run Validation Tests

### Step 5.1: Run Unit Tests

```bash
cd /Users/hafs/Documents/Github/sun_heat_and_ftx/python/v3

# Run MQTT authenticator tests
echo "Running MQTT authenticator unit tests..."
python3 -m pytest tests/mqtt/test_mqtt_authenticator.py -v

# Expected: 21/22 tests pass (1 timeout expected)
```

### Step 5.2: Run Security Tests

```bash
cd /Users/hafs/Documents/Github/sun_heat_and_ftx/python/v3

# Run security validation tests
echo "Running MQTT security tests..."
python3 -m pytest tests/mqtt/test_mqtt_security.py -v -k "not timeout"

# Tests should validate:
# - Credential loading
# - Authentication enforcement
# - Connection security
```

---

## Phase 6: Clean Up

### Stop Test Broker

```bash
# In the terminal running mosquitto, press Ctrl+C

# Verify stopped
ps aux | grep mosquitto | grep -v grep
# Should show no results
```

### Archive Test Data (Optional)

```bash
# Archive test data for reference
tar -czf ~/mosquitto-test-$(date +%Y%m%d).tar.gz ~/mosquitto-test/

# Remove test data
rm -rf ~/mosquitto-test/

echo "✅ Test environment cleaned up"
```

### Remove Test .env (Optional)

```bash
# If you want to remove test credentials
cd /Users/hafs/Documents/Github/sun_heat_and_ftx/python/v3
rm .env

echo "✅ Test .env removed"
```

---

## Validation Checklist

After completing all phases, verify:

- [ ] Local mosquitto broker started successfully
- [ ] Test credentials created and secured
- [ ] Valid credentials: Connection successful ✅
- [ ] Invalid credentials: Connection refused ✅
- [ ] Anonymous access: Connection refused ✅
- [ ] .env file created with correct credentials
- [ ] Python can load environment variables
- [ ] MQTTAuthenticator creates successfully
- [ ] MQTTAuthenticator validates credentials
- [ ] MQTTAuthenticator connects successfully
- [ ] MQTTHandler integrates with authenticator
- [ ] MQTTHandler publishes messages successfully
- [ ] Unit tests pass (21/22 expected)
- [ ] Security tests pass

---

## Success Criteria

✅ **Test deployment successful if**:
1. Broker enforces authentication (rejects anonymous/invalid credentials)
2. Application connects with valid credentials
3. Messages publish/subscribe successfully
4. All integration tests pass
5. No credential leaks (git status clean)

---

## Troubleshooting

### Issue: "Connection Refused"
**Cause**: Credentials incorrect or broker not running  
**Fix**: Check ~/mosquitto-test/credentials.txt, verify broker running

### Issue: "Address already in use"
**Cause**: Another process using port 1883  
**Fix**: `lsof -i :1883` to find process, stop it, or use different port

### Issue: "Permission denied" on password file
**Cause**: Incorrect file permissions  
**Fix**: `chmod 644 ~/mosquitto-test/config/passwd`

### Issue: ".env not loaded"
**Cause**: Wrong directory or file doesn't exist  
**Fix**: Verify .env in python/v3/ directory, check file contents

### Issue: "Module not found"
**Cause**: Not in python/v3 directory or missing dependencies  
**Fix**: `cd python/v3 && pip install -r ../../requirements.txt`

---

## Next Steps After Successful Test

1. ✅ **Document test results** - Note any issues encountered
2. ✅ **Review production deployment guide** - `ISSUE_44_DEPLOYMENT_GUIDE.md`
3. ✅ **Prepare production credentials** - Generate strong passwords
4. ✅ **Schedule production deployment** - Coordinate maintenance window
5. ✅ **Execute production deployment** - Follow deployment guide
6. ✅ **Verify production** - Run validation tests on production
7. ✅ **Close Issue #44** - Update GitHub with deployment results

---

## Reference Files

- **Deployment Guide**: `ISSUE_44_DEPLOYMENT_GUIDE.md`
- **Validation Report**: `ISSUE_44_VALIDATION_COMPLETE.md`
- **Test Results**: `ISSUE_44_TEST_RESULTS.md`
- **Environment Template**: `.env.example`

---

**Status**: Ready to begin  
**Confidence**: HIGH (comprehensive test plan)  
**Risk**: ZERO (local testing only)
