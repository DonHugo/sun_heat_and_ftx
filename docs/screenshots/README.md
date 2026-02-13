# Dashboard Screenshots

This directory contains visual documentation of the dashboard's evolution and design states.

## Directory Structure

```
screenshots/
├── baseline-YYYY-MM-DD/    # Initial state captures
│   ├── desktop-*.png
│   ├── mobile-*.png
│   └── tablet-*.png
├── feature-NAME/           # Feature-specific screenshots
│   ├── before.png
│   └── after.png
└── issue-NNN/             # Issue-related screenshots
    ├── problem.png
    └── fixed.png
```

## Naming Convention

### Format
`{device}-{section}-{state}.png`

**Examples:**
- `mobile-dashboard-normal.png` - Dashboard tab on mobile in normal state
- `mobile-dashboard-auto-mode.png` - Dashboard in auto mode
- `desktop-temperatures-tab.png` - Temperatures tab on desktop
- `mobile-toggle-disabled.png` - Toggle in disabled state

### Devices
- `desktop` - Desktop browser (1920x1080 or similar)
- `mobile` - Mobile phone (iPhone screenshots)
- `tablet` - Tablet view (iPad or similar)

### Sections
- `dashboard` - Main dashboard view
- `temperatures` - Temperatures tab
- `status` - Status tab  
- `diagnostics` - Diagnostics tab
- `control` - Control panel/toggles

### States
- `normal` - Normal operating state
- `auto-mode` - System in auto mode
- `manual-mode` - System in manual mode
- `error` - Error state visible
- `loading` - Loading state

## How to Capture Screenshots

### On iPhone
1. Navigate to the desired screen
2. Press Side Button + Volume Up simultaneously
3. Screenshot saved to Photos
4. AirDrop or email to computer
5. Rename according to convention above
6. Place in appropriate directory

### On Desktop Browser
1. Open DevTools (F12)
2. Toggle device toolbar (Ctrl+Shift+M)
3. Select device (iPhone, iPad, etc.)
4. Right-click on page → "Capture screenshot" or use DevTools screenshot tool
5. Save and rename according to convention

### Full Page Screenshots
If you need scrolling content:
- Use browser extension (e.g., "GoFullPage")
- Or use DevTools → Command Palette (Ctrl+Shift+P) → "Capture full size screenshot"

## Current Baseline (2026-02-13)

**Version:** v9  
**Key Features:**
- Mobile API connection working
- Pump toggle shows state in auto mode (grayed out)
- Heater toggle enabled in both auto/manual modes
- Dashboard, Temperatures, Status, Diagnostics tabs

**To Add:**
- [ ] Mobile dashboard view (auto mode)
- [ ] Mobile dashboard view (manual mode)
- [ ] Desktop dashboard view
- [ ] Toggle states (enabled, disabled, pending)
- [ ] Error states
- [ ] All tabs on mobile

## Usage in Documentation

When referencing screenshots in docs:
```markdown
![Description](screenshots/baseline-2026-02-13/mobile-dashboard-auto.png)
```

Or in decisions log:
```markdown
| Date | Feature | Screenshot Reference |
|------|---------|---------------------|
| 2026-02-13 | Toggle states | See `screenshots/feature-toggles/` |
```
