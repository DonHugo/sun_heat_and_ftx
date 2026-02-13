# Local Development Setup

This directory contains everything needed for local frontend development without deploying to the Raspberry Pi.

## Quick Start

### Option 1: Python HTTP Server (Simplest)

```bash
# From the repository root
cd python/v3/frontend

# Start local server
python3 -m http.server 8000

# Open in browser
open http://localhost:8000/index-dev.html
```

### Option 2: Node.js HTTP Server (If you have Node)

```bash
# Install http-server globally (once)
npm install -g http-server

# From frontend directory
cd python/v3/frontend
http-server -p 8000

# Open in browser
open http://localhost:8000/index-dev.html
```

## What You Get

### Mock API (`api-mock.js`)
- ✅ Simulates all Flask API endpoints
- ✅ Realistic temperature data with variations
- ✅ State management (pump, heater, mode changes persist)
- ✅ Real-time simulation (temps change over time)
- ✅ Network latency simulation (200ms delay)
- ✅ Error conditions (temp limits, mode restrictions)

### Development HTML (`index-dev.html`)
- ✅ Orange banner showing "DEV MODE"
- ✅ Loads mock API before dashboard.js
- ✅ Separate cache version (`?v=10-dev`)
- ✅ Otherwise identical to production index.html

### Smart Dashboard (`static/js/dashboard.js`)
- ✅ Auto-detects MockAPI presence
- ✅ Falls back to real API in production
- ✅ Console logging shows which mode is active
- ✅ No code changes needed for deployment

## Development Workflow

### 1. Make UI Changes
Edit files locally:
- `static/css/styles.css` - Visual styling
- `static/js/dashboard.js` - Logic and behavior  
- `index-dev.html` - HTML structure (dev version)
- `index.html` - HTML structure (production version)

### 2. Test Locally
```bash
# Start server (if not already running)
python3 -m http.server 8000

# Open in browser with dev tools
open http://localhost:8000/index-dev.html

# Check console for "[DEV MODE] Using Mock API" messages
```

### 3. Test Interactions
The mock API simulates:
- ✅ Mode changes (auto ↔ manual)
- ✅ Pump control (start/stop in manual mode)
- ✅ Heater control (works in both modes)
- ✅ Temperature changes over time
- ✅ Error conditions (pump disabled in auto mode)

### 4. Responsive Testing
Use browser DevTools:
- Press `F12` to open DevTools
- Click device toolbar icon (or `Ctrl+Shift+M`)
- Select iPhone, iPad, or custom sizes
- Test touch interactions
- Take screenshots for documentation

### 5. Deploy to Production
When changes look good:

```bash
# Update cache version in production index.html (v=9 → v=10)
sed -i '' 's/dashboard.js?v=9/dashboard.js?v=10/' index.html

# Commit changes
git add .
git commit -m "Your change description"
git push origin main

# Deploy to Pi
ssh pi@192.168.0.18 "cd /home/pi/solar_heating && git pull origin main"
ssh pi@192.168.0.18 "sudo cp /home/pi/solar_heating/python/v3/frontend/index.html /opt/solar_heating/frontend/"
ssh pi@192.168.0.18 "sudo cp /home/pi/solar_heating/python/v3/frontend/static/js/dashboard.js /opt/solar_heating/frontend/static/js/"
ssh pi@192.168.0.18 "sudo cp /home/pi/solar_heating/python/v3/frontend/static/css/styles.css /opt/solar_heating/frontend/static/css/"
ssh pi@192.168.0.18 "sudo systemctl reload nginx"
```

## Mock API Features

### State Management
The mock maintains system state across API calls:
```javascript
MockAPI.state = {
    mode: 'auto',           // System mode
    pump_running: true,     // Pump on/off
    heater_on: false,       // Heater on/off
    tank_temp: 39.1,        // Current tank temperature
    collector_temp: 44.6,   // Current collector temperature
    manual_mode: false,     // Manual control enabled
    mqtt_connected: true,   // MQTT status
    ha_connected: false,    // Home Assistant status
}
```

### Real-Time Simulation
Temperatures change every 2 seconds:
- **Pump running**: Tank temp rises, collector cools (heat transfer)
- **Heater on**: Tank temp rises faster (+0.2°C per update)
- **Idle**: Natural cooling (-0.05°C per update)
- **Collector**: Random variations simulating sunlight

### Error Handling
Mock API enforces same rules as production:
- ❌ Pump control blocked in auto mode
- ❌ Heater blocked if tank temp ≥ 80°C
- ✅ Heater works in both auto and manual modes
- ✅ Mode changes allowed anytime

### Console Logging
Watch the browser console for:
```
🔧 Mock API loaded - Local development mode active
📊 Initial state: {mode: 'auto', pump_running: true, ...}
[DEV MODE] Using Mock API for: GET /status
[MOCK API] GET /status
[MOCK] Mode changed to: manual
[MOCK] Pump started
```

## File Structure

```
python/v3/frontend/
├── index.html              # Production version
├── index-dev.html          # Development version (loads mock)
├── api-mock.js             # Mock API implementation
├── README-DEV.md           # This file
├── static/
│   ├── css/
│   │   └── styles.css      # Visual styling
│   └── js/
│       └── dashboard.js    # Dashboard logic (works with both real and mock APIs)
```

## Tips & Tricks

### Faster Iteration
- Keep browser DevTools open (F12)
- Enable "Disable cache" in Network tab
- Use LiveReload extension for auto-refresh
- Console shows which API mode is active

### Testing Different States
Open browser console and manually change state:
```javascript
// Change system mode
MockAPI.state.mode = 'manual';
MockAPI.state.manual_mode = true;

// Simulate hot tank
MockAPI.state.tank_temp = 78;

// Trigger error condition
MockAPI.state.tank_temp = 85; // Heater will be blocked

// Disconnect MQTT
MockAPI.state.mqtt_connected = false;
```

### Comparing with Production
Keep two tabs open:
- **Tab 1**: `http://localhost:8000/index-dev.html` (mock)
- **Tab 2**: `http://192.168.0.18` (real system)

Compare behavior side-by-side!

### Mobile Testing
Use browser DevTools responsive mode:
1. Open DevTools (F12)
2. Click device toolbar (Ctrl+Shift+M)
3. Select "iPhone 12 Pro" or similar
4. Test touch interactions
5. Take screenshots (right-click → Capture screenshot)

### Performance Testing
Check console timing:
```
[MOCK API] GET /status (200ms delay)
```
Mock adds 200ms latency to simulate real network conditions.

## Common Issues

### "MockAPI is not defined"
- Make sure `api-mock.js` loads BEFORE `dashboard.js`
- Check `index-dev.html` has `<script src="api-mock.js"></script>` first

### Changes Not Visible
- Hard refresh: `Ctrl+Shift+R` (or `Cmd+Shift+R` on Mac)
- Clear cache in DevTools settings
- Check cache version in `index-dev.html`

### CORS Errors
- Use a local server, don't open `file://` directly
- Python's `http.server` handles CORS correctly
- Use `python3 -m http.server 8000` from frontend directory

### CSS Not Loading
- Check path in `<link>` tag: `href="static/css/styles.css"`
- Paths are relative to `index-dev.html` location
- Restart server after moving files

## Next Steps

### Phase 3: Structured UX Review
After comfortable with local development:
1. Document current user experience
2. Identify friction points
3. Prioritize improvements
4. Iterate quickly with mock API

### Future Enhancements
- [ ] Add mock for historical data graphs
- [ ] Simulate error conditions (API timeout, etc.)
- [ ] Add mock for schedule programming
- [ ] Visual regression testing setup
- [ ] Automated screenshot comparison

## Questions?

Check the main UX guidelines: `docs/UX_GUIDELINES.md`
