# Manual Heater Control - Hardware Validation Guide

**Purpose:** Step-by-step hardware validation checklist after frontend implementation  
**Prerequisites:** Frontend code complete, backend deployed, Raspberry Pi running

---

## Pre-Validation Setup

### 1. System Preparation

```bash
# 1. Ensure system is in manual mode
curl http://localhost:5000/api/status | jq '.manual_control'
# Expected: true

# 2. Check current temperature
curl http://localhost:5000/api/status | jq '.storage_tank'
# Expected: < 80°C (safe to test)

# 3. Verify heater relay channel
cat /path/to/config.yaml | grep cartridge_heater_relay
# Expected: 2

# 4. Check current heater state
curl http://localhost:5000/api/status | jq '.cartridge_heater'
# Expected: false (OFF initially)
```

### 2. Safety Checks

⚠️ **BEFORE TESTING:**
- [ ] Verify water tank is NOT at maximum temperature (< 75°C)
- [ ] Ensure system is in manual mode
- [ ] Have emergency cutoff switch accessible
- [ ] Verify correct relay channel (default: 2)

---

## Phase 1: UI Validation (Visual Only)

### Test 1.1: Toggle Switch Appearance
1. Open browser: `http://<raspberry-pi-ip>:5000`
2. Navigate to Quick Controls card
3. **Verify:**
   - [ ] Toggle switch is visible
   - [ ] Toggle is in "OFF" position (left side)
   - [ ] Status text shows "OFF"
   - [ ] Switch styling matches pump toggles
   - [ ] Label says "Cartridge Heater"

### Test 1.2: State Synchronization (Initial Load)
1. **IF heater is already ON** (backend state = true):
   - [ ] Toggle should be in "ON" position (right side)
   - [ ] Status text should show "ON" in green
2. **IF heater is OFF** (backend state = false):
   - [ ] Toggle should be in "OFF" position
   - [ ] Status text should show "OFF"

### Test 1.3: Emergency Stop Removal
1. Scan entire page for "Emergency Stop" button
2. **Verify:**
   - [ ] Button is NOT visible anywhere
   - [ ] No "Emergency Stop" text on page
   - [ ] Console has no JavaScript errors related to emergency stop

---

## Phase 2: API Validation (Browser Dev Tools)

### Test 2.1: Toggle Sends Correct API Request
1. Open browser dev tools (F12) → Network tab
2. Click toggle to turn heater ON
3. **Verify Network Request:**
   ```
   Request URL: http://<ip>:5000/api/control
   Request Method: POST
   Request Body: {"action": "heater_start"}
   Status Code: 200 OK
   ```
4. Click toggle to turn heater OFF
5. **Verify Network Request:**
   ```
   Request URL: http://<ip>:5000/api/control
   Request Method: POST
   Request Body: {"action": "heater_stop"}
   Status Code: 200 OK
   ```

### Test 2.2: Error Handling (Not in Manual Mode)
1. **Setup:** Set system to auto mode
   ```bash
   curl -X POST http://localhost:5000/api/control \
     -H "Content-Type: application/json" \
     -d '{"action": "manual_off"}'
   ```
2. In browser, click heater toggle
3. **Verify:**
   - [ ] Toggle reverts to OFF position
   - [ ] Error message appears: "Manual control not enabled"
   - [ ] Network tab shows: Status Code: 400 Bad Request

### Test 2.3: Temperature Safety (High Temperature)
1. **Setup:** Simulate high temperature (TESTING ONLY)
   ```python
   # Temporarily modify api_server.py for testing
   # Line ~335: Set temp_limit = 40.0 (instead of reading from config)
   # This allows testing without actually heating water
   ```
2. In browser, click heater toggle to ON
3. **Verify:**
   - [ ] Toggle reverts to OFF position
   - [ ] Error message: "Temperature too high (XX°C ≥ 40°C)"
   - [ ] Network tab shows: Status Code: 400 Bad Request
4. **IMPORTANT:** Revert test modification after validation

### Test 2.4: Anti-Cycling (Rate Limiting)
1. In browser, click heater toggle ON
2. **Immediately** (within 1 second), click toggle OFF
3. **Verify:**
   - [ ] Second toggle attempt is blocked
   - [ ] Toggle shows disabled state (grayed out)
   - [ ] Error message: "Rate limit: 5 second cooldown"
   - [ ] Network tab shows: Status Code: 429 Too Many Requests
   - [ ] Countdown timer appears (5 → 4 → 3 → 2 → 1 → 0)
4. Wait 5 seconds
5. **Verify:**
   - [ ] Toggle becomes enabled again
   - [ ] Countdown timer disappears
   - [ ] Can now toggle heater

---

## Phase 3: Hardware Validation (Physical Relay)

⚠️ **SAFETY:** Have emergency cutoff accessible during these tests.

### Test 3.1: Heater ON Command (Relay Activation)

**Safety Check Before Test:**
```bash
# Verify temperature is safe
curl http://localhost:5000/api/status | jq '.storage_tank'
# Must be < 70°C
```

**Test Procedure:**
1. Open browser to dashboard
2. Click toggle to turn heater ON
3. **Immediately verify:**
   - [ ] Audible "click" from relay board (relay energizing)
   - [ ] Relay LED indicator lights up (if board has LEDs)
   - [ ] Toggle shows "ON" in green
   - [ ] Status text shows "ON"

4. **Verify via MQTT (Home Assistant):**
   ```bash
   mosquitto_sub -h 192.168.0.110 -u <user> -P <pass> \
     -t "homeassistant/switch/solar_heating_cartridge_heater/state"
   # Expected: "ON"
   ```

5. **Verify via system logs:**
   ```bash
   journalctl -u solar_heating_api -n 20 | grep heater
   # Expected: "Cartridge heater relay 2 set to ON"
   ```

6. **Physical verification (OPTIONAL - ONLY IF SAFE):**
   - [ ] Measure current draw on heater circuit (should be > 0A)
   - [ ] Temperature should start rising slowly (over 10+ minutes)

### Test 3.2: Heater OFF Command (Relay Deactivation)

**Test Procedure:**
1. With heater currently ON, click toggle to turn OFF
2. **Immediately verify:**
   - [ ] Audible "click" from relay board (relay de-energizing)
   - [ ] Relay LED indicator turns off
   - [ ] Toggle shows "OFF"
   - [ ] Status text shows "OFF" (gray color)

3. **Verify via MQTT:**
   ```bash
   mosquitto_sub -h 192.168.0.110 -u <user> -P <pass> \
     -t "homeassistant/switch/solar_heating_cartridge_heater/state"
   # Expected: "OFF"
   ```

4. **Verify via system logs:**
   ```bash
   journalctl -u solar_heating_api -n 20 | grep heater
   # Expected: "Cartridge heater relay 2 set to OFF"
   ```

5. **Physical verification (OPTIONAL):**
   - [ ] Current draw on heater circuit = 0A
   - [ ] Temperature rise stops

### Test 3.3: NC Relay Logic Verification

**Critical Test:** Ensure Normally Closed relay logic is correct.

**Background:**
- NC relay: Contact is CLOSED when relay is DE-ENERGIZED
- To turn heater ON: Relay must be ENERGIZED (contact closed = heater gets power)
- Hardware expects: `False` = energize relay = heater ON

**Test:**
1. **With heater OFF** (toggle in OFF position):
   ```bash
   # Check GPIO state (relay should be de-energized)
   # This is hardware-dependent, example for MegaBAS:
   i2cget -y 1 0x02 0x<relay_channel>
   # Expected: 0x01 (True = relay OFF)
   ```

2. **Turn heater ON** (click toggle):
   ```bash
   # Check GPIO state (relay should be energized)
   i2cget -y 1 0x02 0x<relay_channel>
   # Expected: 0x00 (False = relay ON)
   ```

3. **Verify:**
   - [ ] OFF state → GPIO = 1 (True) → Relay de-energized → Heater OFF ✅
   - [ ] ON state → GPIO = 0 (False) → Relay energized → Heater ON ✅

**If logic is reversed:**
- ❌ Heater turns OFF when toggle is ON
- ❌ Heater turns ON when toggle is OFF
- **FIX:** Invert logic in `api_server.py` line 410

---

## Phase 4: Integration Validation (Automation Safety)

### Test 4.1: Cannot Control Heater in Auto Mode
1. **Setup:** Set system to auto mode
   ```bash
   curl -X POST http://localhost:5000/api/control \
     -H "Content-Type: application/json" \
     -d '{"action": "manual_off"}'
   ```
2. Try to turn heater ON via UI
3. **Verify:**
   - [ ] Toggle is blocked
   - [ ] Error message: "Manual control not enabled"
4. **Restore manual mode:**
   ```bash
   curl -X POST http://localhost:5000/api/control \
     -H "Content-Type: application/json" \
     -d '{"action": "manual_on"}'
   ```

### Test 4.2: State Persists Across Browser Refresh
1. Turn heater ON via UI
2. Wait 3 seconds (ensure state is saved)
3. Hard refresh browser (Ctrl+Shift+R)
4. **Verify:**
   - [ ] Toggle is still in ON position
   - [ ] Status still shows "ON"
   - [ ] Relay is still energized (audible, LED on)

### Test 4.3: State Syncs Across Multiple Clients
1. Open dashboard in two browser tabs/devices
2. In **Tab 1**, turn heater ON
3. Wait 2 seconds
4. Check **Tab 2**
5. **Verify:**
   - [ ] Tab 2 toggle automatically updates to ON
   - [ ] Status text shows "ON" in both tabs

### Test 4.4: State Persists Across API Restart
1. Turn heater ON via UI
2. Restart API service:
   ```bash
   sudo systemctl restart solar_heating_api
   ```
3. Wait 10 seconds (service startup)
4. Check heater state:
   ```bash
   curl http://localhost:5000/api/status | jq '.cartridge_heater'
   # Expected: true (state restored)
   ```
5. Refresh browser
6. **Verify:**
   - [ ] Toggle is in ON position
   - [ ] Relay is still energized

---

## Phase 5: Safety Validation (Critical)

### Test 5.1: Temperature Safety Prevents Overheating

**Setup (SIMULATION ONLY - DO NOT OVERHEAT WATER):**
```python
# Temporarily modify api_server.py for testing
# Line ~347: Mock current_temp = 85.0 (above 80°C limit)
```

**Test:**
1. Try to turn heater ON via UI
2. **Verify:**
   - [ ] Toggle is blocked
   - [ ] Error: "Temperature too high (85.0°C ≥ 80.0°C)"
   - [ ] Relay remains OFF
   - [ ] No state change in system

**Cleanup:** Revert test modification

### Test 5.2: Anti-Cycling Prevents Rapid Switching

**Test:**
1. Turn heater ON
2. Immediately try to turn OFF (within 1 second)
3. **Verify:**
   - [ ] Second command blocked
   - [ ] Error: "Rate limit: 5 second cooldown"
   - [ ] Relay state doesn't change
4. Wait 5 seconds
5. Try to turn OFF again
6. **Verify:**
   - [ ] Command succeeds
   - [ ] Relay turns OFF

### Test 5.3: Hardware Failure Handling

**Test:**
1. **Simulate hardware failure** (TESTING ONLY):
   ```python
   # Temporarily modify hardware.py
   # Make set_relay_state() return False
   ```
2. Try to turn heater ON
3. **Verify:**
   - [ ] Toggle reverts to OFF
   - [ ] Error: "Hardware control failed"
   - [ ] System logs error
   - [ ] No state change

**Cleanup:** Revert test modification

---

## Phase 6: User Experience Validation

### Test 6.1: Mobile Responsive Design
1. Open dashboard on mobile device (phone/tablet)
2. **Verify:**
   - [ ] Toggle switch is visible and appropriately sized
   - [ ] Toggle is easily clickable (large touch target)
   - [ ] Status text is readable
   - [ ] Error messages display properly
   - [ ] Works in portrait and landscape orientations

### Test 6.2: Browser Compatibility
Test in multiple browsers:
- [ ] Chrome/Chromium (Linux/Windows/Mac)
- [ ] Firefox
- [ ] Safari (Mac/iOS)
- [ ] Edge

**For each browser, verify:**
- [ ] Toggle switch appears correctly
- [ ] Toggle animations work smoothly
- [ ] No JavaScript console errors
- [ ] State updates work
- [ ] Error messages display

### Test 6.3: Accessibility
1. Navigate using keyboard only (Tab key)
2. **Verify:**
   - [ ] Toggle can be focused with Tab
   - [ ] Space/Enter toggles the switch
   - [ ] Visual focus indicator is visible

---

## Validation Checklist Summary

### ✅ Must Pass (Production Blockers)
- [ ] **Test 1.1:** Toggle switch visible and styled correctly
- [ ] **Test 1.3:** Emergency stop button removed
- [ ] **Test 2.1:** API requests formatted correctly
- [ ] **Test 2.4:** Anti-cycling enforced (5-second cooldown)
- [ ] **Test 3.1:** Heater turns ON (relay energizes)
- [ ] **Test 3.2:** Heater turns OFF (relay de-energizes)
- [ ] **Test 3.3:** NC relay logic correct (False=ON, True=OFF)
- [ ] **Test 5.1:** Temperature safety prevents operation > 80°C
- [ ] **Test 5.2:** Anti-cycling prevents rapid switching

### ⚠️ Should Pass (Important but not blocking)
- [ ] **Test 2.2:** Error handling for manual mode
- [ ] **Test 4.1:** Cannot control in auto mode
- [ ] **Test 4.2:** State persists across refresh
- [ ] **Test 4.3:** State syncs across clients
- [ ] **Test 6.1:** Mobile responsive
- [ ] **Test 6.2:** Browser compatibility

### 🟢 Nice to Have (Can be improved later)
- [ ] **Test 5.3:** Hardware failure handling
- [ ] **Test 6.3:** Accessibility features

---

## Post-Validation Actions

### If All Critical Tests Pass: ✅
1. **Document test results:**
   ```bash
   cp ISSUE_44_HARDWARE_VALIDATION_GUIDE.md ISSUE_44_HARDWARE_VALIDATION_RESULTS.md
   # Add test results, timestamps, who performed tests
   ```

2. **Create production deployment ticket:**
   - Attach validation results
   - Include rollback plan
   - Define monitoring metrics

3. **Deploy to production:**
   ```bash
   git add python/v3/frontend/
   git commit -m "feat: Add manual heater control UI (#44)

   - Add toggle switch to Quick Controls card
   - Implement heater control JavaScript handlers
   - Add toggle switch CSS styling
   - Remove emergency stop button
   - Add anti-cycling countdown timer
   - Update cache version to v=5

   Safety features:
   - Temperature safety (80°C limit)
   - Anti-cycling (5-second cooldown)
   - Manual mode enforcement
   - NC relay logic (False=ON)"
   
   git push origin main
   ```

4. **Monitor for 24 hours** (see ISSUE_44_VALIDATION_REPORT.md → Monitoring section)

### If Any Critical Test Fails: ❌
1. **Stop deployment immediately**
2. **Document failure:**
   - Which test failed
   - Expected vs. actual behavior
   - Error messages/logs
3. **Fix issue:**
   - Review code
   - Make corrections
   - Test locally
4. **Re-run validation from beginning**

---

## Emergency Procedures

### Emergency Stop (If Heater Malfunctions)
1. **Immediate action:**
   - Physical emergency cutoff switch
   - OR: Power off Raspberry Pi
   - OR: Unplug heater

2. **Disable in software:**
   ```bash
   # Force heater OFF via API
   curl -X POST http://localhost:5000/api/control \
     -H "Content-Type: application/json" \
     -d '{"action": "heater_stop"}'
   
   # Verify state
   curl http://localhost:5000/api/status | jq '.cartridge_heater'
   # Expected: false
   ```

3. **Rollback deployment:**
   ```bash
   cd /Users/hafs/Documents/Github/sun_heat_and_ftx
   git checkout HEAD~1 python/v3/frontend/
   sudo systemctl restart solar_heating_api
   ```

### Relay Failure (Relay Won't Turn OFF)
1. **Immediate:** Physical cutoff
2. **Investigate:**
   ```bash
   journalctl -u solar_heating_api -n 50 | grep heater
   # Check for hardware errors
   ```
3. **Verify GPIO state:**
   ```bash
   i2cget -y 1 0x02 0x02  # Check relay channel 2
   ```
4. **Manual relay control (TESTING ONLY):**
   ```bash
   i2cset -y 1 0x02 0x02 0x01  # Force relay OFF
   ```

---

## Validation Sign-Off

**Validation Performed By:** _________________  
**Date:** _________________  
**System:** Raspberry Pi Zero 2 W / Solar Heating System v3

**Results:**
- [ ] All critical tests passed
- [ ] All important tests passed
- [ ] Ready for production deployment

**Signatures:**
- Hardware Engineer: _________________
- Safety Officer: _________________
- System Administrator: _________________

---

**END OF HARDWARE VALIDATION GUIDE**
