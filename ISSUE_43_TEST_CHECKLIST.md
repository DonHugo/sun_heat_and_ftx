# Issue #43 - Quick Test Checklist

**Test on Raspberry Pi:** `ssh pi@192.168.0.18`

---

## 🚀 Quick Deployment (5 minutes)

```bash
# SSH to Pi
ssh pi@192.168.0.18

# Pull code
cd /home/pi/sun_heat_and_ftx && git pull

# Install dependencies
cd python/v3
pip3 install --upgrade pydantic flask flask-restful

# Test models work
python3 << 'EOF'
from api_models import ControlRequest
req = ControlRequest(action='pump_start')
print(f"✅ Models work! Action: {req.action.value}")
EOF

# Restart service
sudo systemctl restart solar_heating_v3.service
sleep 5
sudo systemctl status solar_heating_v3.service
```

---

## ✅ Quick Functional Tests (5 minutes)

```bash
# Test 1: Valid action (should work)
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start"}' | python3 -m json.tool
# Expected: 200 OK, success: true

# Test 2: Invalid action (should fail)
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "hack_the_system"}' | python3 -m json.tool
# Expected: 400 Bad Request, VALIDATION_ERROR
```

---

## 🔒 Quick Security Tests (5 minutes)

```bash
# Test 3: SQL injection (should fail)
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start; DROP TABLE sensors;"}' | python3 -m json.tool
# Expected: 400 Bad Request

# Test 4: XSS attack (should fail)
curl -X POST http://localhost:5001/api/mode \
  -H "Content-Type: application/json" \
  -d '{"mode": "<script>alert(1)</script>"}' | python3 -m json.tool
# Expected: 400 Bad Request

# Test 5: Extra fields (should fail)
curl -X POST http://localhost:5001/api/control \
  -H "Content-Type: application/json" \
  -d '{"action": "pump_start", "admin": true}' | python3 -m json.tool
# Expected: 400 Bad Request
```

---

## 🌐 Quick Dashboard Test (2 minutes)

Open in browser: `http://192.168.0.18/`
- [ ] Dashboard loads
- [ ] Try to start/stop pump
- [ ] Try to change mode
- [ ] No errors

---

## 📊 Results

**Total Time:** ~15 minutes

### Checklist
- [ ] Code deployed
- [ ] Dependencies installed
- [ ] Service restarted
- [ ] Valid inputs work (200 OK)
- [ ] Invalid inputs rejected (400)
- [ ] SQL injection blocked
- [ ] XSS blocked
- [ ] Dashboard works
- [ ] System stable

### Decision
- [ ] ✅ All tests passed - **CLOSE ISSUE**
- [ ] ⚠️ Some issues - **REPORT BACK**

---

**Full Testing Guide:** `python/v3/docs/validation/ISSUE_43_HARDWARE_VALIDATION_GUIDE.md`

