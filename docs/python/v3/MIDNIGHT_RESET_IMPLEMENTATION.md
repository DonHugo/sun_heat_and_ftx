# Midnight Reset Implementation

## Overview

This document describes the implementation of midnight-based reset functionality for the Solar Heating System v3, which ensures that operational metrics like pump runtime and heating cycles reset at midnight (00:00:00) instead of at service restart.

## Problem Solved

**Before:** `pump_runtime_hours`, `heating_cycles_count`, and `total_heating_time` were reset to 0 every time the service restarted, losing valuable daily operational data.

**After:** These metrics persist across service restarts and only reset at midnight each day, providing accurate daily operational statistics.

## Key Features

### 1. State Persistence
- **File Storage:** Operational metrics are saved to `system_operational_state.json`
- **Automatic Loading:** Values are restored when the service starts
- **Periodic Saving:** State is saved every 5 minutes and on critical updates

### 2. Midnight Detection
- **Precise Timing:** Resets occur within 5 seconds of 00:00:00
- **Date Tracking:** Prevents multiple resets on the same day
- **Smart Logic:** Only resets when crossing midnight boundary

### 3. Comprehensive Reset
- **Energy Counters:** Daily energy collection totals
- **Operational Metrics:** Pump runtime, heating cycles, total heating time
- **Immediate Persistence:** Reset state is saved immediately

## Implementation Details

### New Methods Added

#### `_save_system_state()`
```python
def _save_system_state(self):
    """Save operational metrics to persistent storage"""
    # Saves pump_runtime_hours, heating_cycles_count, total_heating_time
    # Creates system_operational_state.json file
```

#### `_load_system_state()`
```python
def _load_system_state(self):
    """Load operational metrics from persistent storage"""
    # Restores values on service startup
    # Handles missing file gracefully
```

#### `_is_midnight_reset_needed()`
```python
def _is_midnight_reset_needed(self):
    """Check if we need to reset daily counters at midnight"""
    # Detects midnight crossing within 5-second window
    # Prevents duplicate resets on same day
```

### State File Format

The `system_operational_state.json` file contains:
```json
{
  "pump_runtime_hours": 12.5,
  "heating_cycles_count": 25,
  "total_heating_time": 15.2,
  "last_save_time": 1703123456.789,
  "last_save_date": "2023-12-21T15:30:56.789123"
}
```

### Reset Logic

1. **Detection:** System checks every 5 seconds if midnight has passed
2. **Validation:** Ensures reset hasn't already occurred today
3. **Reset:** Clears all daily counters and operational metrics
4. **Persistence:** Immediately saves the reset state
5. **Logging:** Comprehensive logging for troubleshooting

## Integration Points

### Automatic State Saving
- **On Cycle Start:** When heating cycle begins
- **On Cycle End:** When pump stops and runtime is calculated
- **Periodic:** Every 5 minutes in main loop
- **On Shutdown:** Before service stops

### State Loading
- **Service Startup:** Automatically loads previous state
- **Graceful Fallback:** Continues with defaults if file missing

## Logging and Troubleshooting

### Reset Logs
```
🕛 MIDNIGHT RESET: Daily counters and operational metrics reset
  📊 Energy: 0.00 kWh, Solar: 0.00 kWh, Cartridge: 0.00 kWh, Pellet: 0.00 kWh
  ⚙️  Pump Runtime: 0.00h, Heating Cycles: 0, Total Time: 0.00h
```

### State Persistence Logs
```
✅ Operational state saved: pump_runtime=12.50h, cycles=25, total_time=15.20h
✅ Operational state loaded: pump_runtime=12.50h, cycles=25, total_time=15.20h (last saved: 2023-12-21T15:30:56.789123)
```

### Error Handling
```
❌ Failed to save operational state: [error details]
❌ Failed to load operational state: [error details]
ℹ️  Continuing with default values
```

## Testing

Run the test script to verify functionality:
```bash
cd python/v3
python3 test_midnight_reset.py
```

## Configuration

No additional configuration required. The system automatically:
- Creates the state file in the working directory
- Uses 5-second tolerance for midnight detection
- Saves state every 5 minutes
- Handles file I/O errors gracefully

## Benefits

1. **Data Persistence:** Operational metrics survive service restarts
2. **Accurate Daily Stats:** True daily pump runtime and cycle counts
3. **Troubleshooting:** Better visibility into system performance
4. **Reliability:** Graceful handling of file system issues
5. **Performance:** Minimal overhead with efficient state management

## Future Enhancements

- **Configurable Reset Time:** Allow custom reset times (e.g., 06:00)
- **Multiple Reset Points:** Support for multiple daily resets
- **State Compression:** Compress historical state data
- **Remote Backup:** Sync state to cloud storage
- **Metrics Export:** Export daily statistics to external systems
