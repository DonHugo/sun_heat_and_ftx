# Solar Heating Dashboard - UX Guidelines

## Overview

This document captures the design principles, component patterns, and decision rationale for the Solar Heating System v3 dashboard. The goal is to maintain consistency and provide context for future design decisions.

## Design Principles

### 1. Safety First
**Controls should be obvious and hard to accidentally trigger**
- Critical actions require explicit interaction (toggle switches, not auto-actions)
- System state is always clearly visible
- Error states are prominent and actionable
- Temperature limits are enforced by backend (80°C heater limit)

### 2. Status at a Glance
**Key metrics visible without scrolling**
- Most important info in the top section:
  - Tank temperature (primary metric)
  - Collector temperature (energy source status)
  - Pump state (system operation indicator)
  - Current mode (auto/manual/heating)
- Color coding for quick comprehension (green = OK, red = error)

### 3. Mobile-First
**Primary access is via smartphone while near the system**
- Designed for portrait orientation on phones
- Touch-friendly controls (large tap targets)
- Works on small screens (iPhone SE and up)
- Readable in various lighting conditions (good contrast)

### 4. Network Resilience
**Works reliably across different network conditions**
- Relative URLs work from any device on local network
- Clear error messages when API is unreachable
- 5-second polling interval balances freshness vs. load
- No external dependencies (works offline on LAN)

## Component Patterns

### Toggle Controls

#### Behavior
- **Visual State = Actual State**: Toggle position always reflects real hardware state
- **Auto Mode Handling**:
  - Pump toggle: Grayed out (50% opacity), shows actual state, NOT clickable
  - Heater toggle: Full color, shows actual state, IS clickable (emergency heat)
- **Manual Mode**: Both toggles fully enabled and clickable
- **Feedback**: Toggle updates within 5 seconds via polling (not instant)

#### Implementation Details
```javascript
// Pump toggle: Disabled in auto mode, syncs with actual state
updatePumpToggle() {
    if (!this.pumpToggle) return;
    this.pumpToggle.checked = this.pumpState;
    this.pumpToggle.disabled = !this.manualControlEnabled;
}

// Heater toggle: Always enabled (emergency heat), syncs with actual state
updateHeaterToggle() {
    if (!this.heaterToggle) return;
    this.heaterToggle.checked = this.heaterState;
    // No manual mode check - heater works in both modes
    this.heaterToggle.disabled = this.heaterPending || 
                                  this.heaterLockoutUntil > Date.now();
}
```

#### Rationale
- Users need to see pump status even when they can't control it (situational awareness)
- Heater serves as emergency/supplemental heat in any mode (safety feature)
- Graying out clearly communicates "I can see it but can't change it"

### Status Display

#### Color Coding
| Status | Color | Use Case |
|--------|-------|----------|
| **Green** | `#4ade80` | Operating normally, collecting energy, system healthy |
| **Yellow/Orange** | `#fbbf24` | Warning states, attention needed |
| **Red** | `#ef4444` | Errors, disconnected, critical issues |
| **Gray** | `#9ca3af` | Disabled, unavailable, not applicable |

#### Temperature Display
- **Format**: `XX.X°C` (one decimal place)
- **Context**: Always include description (e.g., "Cold - needs heating")
- **Icons**: Emoji for quick recognition (🌡️ tank, ☀️ collector, 💧 pump, ⚡ heater)

#### Connection Status
- **MQTT**: Shows connection to message broker
- **Home Assistant**: Shows integration status
- **Format**: `Connected` (green) or `Disconnected` (red badge)

### Tab Navigation

#### Structure
1. **Dashboard** (default): Overview + quick controls
2. **Temperatures**: Detailed temperature readings
3. **Status**: System health and diagnostics
4. **Diagnostics**: Advanced info and logs

#### Navigation Pattern
- Tabs persist state (don't reset on navigation)
- Active tab highlighted with blue background
- Tab content loads without page refresh

### Mode Switching

#### Available Modes
- **Auto**: System manages pump based on temperature differential
- **Manual**: User has full control of pump
- **Heating**: Active solar collection mode

#### Mode Indicator
- Prominent badge showing current mode
- Green color for active modes
- Located in "System Overview" section

## Accessibility Considerations

### Color Contrast
- Background: `#8b5cf6` (purple gradient)
- Text: White or very light gray
- Contrast ratio: Meets WCAG AA standards for large text

### Touch Targets
- Minimum size: 44x44px (iOS guidelines)
- Toggle switches: Large enough for easy tapping
- Buttons: Full-width on mobile for easy access

### Error Messages
- Clear, human-readable error text
- Red color for visibility
- Actionable when possible (e.g., "Retry" option)

## Design Decisions Log

| Date | Issue | Decision | Rationale |
|------|-------|----------|-----------|
| 2026-02-13 | Pump toggle in auto mode | Gray out but show actual state | Users need situational awareness of pump status even when they can't control it manually |
| 2026-02-13 | Heater toggle in auto mode | Keep enabled and clickable | Heater serves as emergency/supplemental heat and should be accessible anytime |
| 2026-02-13 | iPhone API connection | Use relative URLs (`/api`) instead of `localhost:5001` | Allows dashboard to work from any device on the network via nginx proxy |
| 2026-02-13 | Toggle state synchronization | Update toggle position to match actual hardware state every 5 seconds | Prevents confusion when auto mode changes pump state - toggle reflects reality not just user commands |
| 2026-02-12 | API polling interval | 5 seconds | Balance between freshness (responsive UI) and load (Raspberry Pi resource constraints) |

## Technical Constraints

### Hardware
- **Server**: Raspberry Pi Zero 2 W (limited CPU/memory)
- **Network**: Local LAN only (192.168.0.x)
- **Deployment**: Static files + Flask API (no build process)

### Browser Support
- **Primary**: Mobile Safari (iOS)
- **Secondary**: Desktop Chrome/Firefox
- **Not supported**: IE11 (uses modern JavaScript)

### Performance
- **Target load time**: < 2 seconds on local network
- **Polling frequency**: 5 seconds
- **Cache strategy**: Version-based cache busting (`?v=9`)

## Future Considerations

### Potential Improvements
- [ ] Dark mode support (easier on eyes at night)
- [ ] Historical temperature graphs (trend visualization)
- [ ] Push notifications for alerts (if critical)
- [ ] Offline mode indicator (show when API is unreachable)
- [ ] Schedule programming (heat at specific times)
- [ ] Energy usage statistics (kWh tracking)

### Known Limitations
- No authentication (assumes trusted local network)
- No multi-user support (single system state)
- Limited error recovery (requires page refresh in some cases)
- No undo for control actions (could add confirmation dialogs)

## Testing Checklist

### Before Deploying UI Changes
- [ ] Test on iPhone (primary device)
- [ ] Test on desktop browser
- [ ] Verify responsive design (resize browser)
- [ ] Test in auto mode (pump toggle behavior)
- [ ] Test in manual mode (both toggles active)
- [ ] Check error states (disconnect API, check messages)
- [ ] Hard refresh after deployment (cache busting)
- [ ] Verify all tabs load correctly
- [ ] Check console for JavaScript errors

### Accessibility Check
- [ ] Text is readable at arm's length on phone
- [ ] Color contrast sufficient in bright/dim lighting
- [ ] Touch targets are large enough
- [ ] Error messages are clear and helpful

## Resources

### Key Files
- **Frontend**: `/opt/solar_heating/frontend/`
  - `index.html` - Main page structure
  - `static/js/dashboard.js` - Dashboard logic
  - `static/css/styles.css` - Visual styling
- **API**: `/opt/solar_heating_v3/api_server.py`
- **Nginx Config**: `/etc/nginx/sites-enabled/solar_heating.conf`

### Deployment Process
```bash
# 1. Make changes locally
# 2. Update cache version in index.html (v=X → v=X+1)
# 3. Commit and push
git add .
git commit -m "Description of UX change"
git push origin main

# 4. Deploy to Pi
ssh pi@192.168.0.18 "cd /home/pi/solar_heating && git pull origin main"
ssh pi@192.168.0.18 "sudo cp /home/pi/solar_heating/python/v3/frontend/index.html /opt/solar_heating/frontend/"
ssh pi@192.168.0.18 "sudo cp /home/pi/solar_heating/python/v3/frontend/static/js/dashboard.js /opt/solar_heating/frontend/static/js/"
ssh pi@192.168.0.18 "sudo systemctl reload nginx"
```

### External References
- [iOS Human Interface Guidelines](https://developer.apple.com/design/human-interface-guidelines/)
- [WCAG 2.1 Accessibility Standards](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design Icons](https://materialdesignicons.com/)

---

**Last Updated**: 2026-02-13  
**Document Version**: 1.0  
**Dashboard Version**: v9 (cache version in index.html)
