# Energy Calculation Explanation

## Overview
The energy numbers displayed in the dashboard are calculated based on **actual stored energy changes** in your 360L water heater tank, measured by 9 temperature sensors distributed throughout the tank.

## How It Works

### 1. **Stored Energy Calculation (Base Measurement)**

The system calculates the total thermal energy stored in the tank using:

```
Energy (kWh) = (mass × specific_heat × temperature_change) / 3600
```

**Parameters:**
- **Tank Volume**: 360 liters (360 kg of water)
- **Specific Heat Capacity**: 4.186 kJ/(kg·°C) for water
- **Reference Temperature**: 4°C (zero energy baseline)
- **Sensors**: 8 RTD sensors + 1 MegaBAS sensor measuring different tank levels

**Tank Divisions:**
- Bottom half: RTD sensors 0-4 (5 sensors × 45L each)
- Top half: RTD sensors 5-7 + MegaBAS sensor 5 (4 sensors × 45L each)

**Example:**
If average tank temperature is 60°C:
```
Energy = 360 kg × 4.186 kJ/(kg·°C) × (60°C - 4°C) / 3600
Energy ≈ 23.4 kWh
```

Maximum expected energy for your tank: **~36 kWh** (at 90°C)

---

### 2. **Daily Energy Totals (What Heated the Water)**

The system tracks which heat source added energy to the tank by monitoring:

#### **Solar Energy** (`solar_energy_today`)
- **Detection**: Primary pump is ON **AND** solar collector is hotter than tank by >5°C
- **Calculation**: Energy increase weighted by temperature difference (dT)
  - Higher dT = more solar contribution (max weight: 1.0)
  - Formula: `weight = min(1.0, max(0.1, dT / 20.0))`

#### **Cartridge Heater Energy** (`cartridge_energy_today`)
- **Detection**: Cartridge heater relay is ON
- **Calculation**: Energy increase weighted at 80% when active
  - Assumes consistent heating rate from 3kW cartridge heater

#### **Pellet Furnace Energy** (`pellet_energy_today`)
- **Detection**: Energy increasing but no other heat source is active
- **Calculation**: Assumes 100% contribution when other sources are off

**Energy Accumulation:**
Every 30 seconds (or each measurement cycle), the system:
1. Calculates current stored energy from tank temperatures
2. Compares to previous stored energy
3. If energy increased (`energy_diff > 0`):
   - Identifies active heat sources
   - Allocates the energy gain proportionally to active sources
   - Adds to daily totals

**Example Scenario:**
```
Time 10:00: Tank = 25 kWh
Time 10:30: Tank = 26 kWh (gained 1 kWh)
Active sources: Solar (dT=15°C) + Cartridge heater (ON)

Contribution weights:
- Solar: 0.75 (based on dT=15°C)
- Cartridge: 0.80 (fixed rate when ON)
Total weight: 1.55

Allocation:
- Solar gets: 1 kWh × (0.75/1.55) = 0.48 kWh
- Cartridge gets: 1 kWh × (0.80/1.55) = 0.52 kWh

Daily totals updated:
- solar_energy_today += 0.48 kWh
- cartridge_energy_today += 0.52 kWh
```

---

### 3. **Hourly Rates (Current Power Output)**

The `_hour` values show the **current heating rate** in the past hour:

- `solar_energy_hour`: kWh collected from solar in the last hour
- `cartridge_energy_hour`: kWh from cartridge heater in the last hour
- `pellet_energy_hour`: kWh from pellet furnace in the last hour

**Reset Logic:**
- Hourly counters reset every 3600 seconds (1 hour)
- Daily counters reset at midnight

---

## What Numbers Are "Reasonable"?

### **Daily Totals (Typical Values)**

**Solar Energy:**
- **Sunny day**: 5-15 kWh (winter) to 20-30 kWh (summer)
- **Cloudy day**: 0-3 kWh
- **Night**: 0 kWh

**Cartridge Heater:**
- **3kW heater running 1 hour**: 3 kWh
- **Running 4 hours**: 12 kWh
- **All day (8h)**: 24 kWh

**Pellet Furnace:**
- Depends on your furnace power output
- Typical pellet stove: 5-15 kW output
- If running 2 hours: 10-30 kWh

### **Hourly Rates (Current Power)**

These should match the **nominal power** of your heat sources:

- **Solar**: 0-6 kW (depends on sun intensity and collector efficiency)
- **Cartridge Heater**: ~3 kW when ON (should match your heater spec)
- **Pellet Furnace**: 5-15 kW when burning (depends on your model)

**⚠️ Warning Signs:**
- Total energy > 36 kWh (tank can't store more than this)
- Cartridge heater showing >4 kW (it's rated at 3kW)
- Energy increasing with no heat source active (indicates calibration issue)

---

## Checking Your Current Values

**Look at your dashboard numbers and compare:**

1. **Total stored energy** (not shown on dashboard yet):
   - Should be 5-35 kWh depending on tank temperature
   - Calculate expected: `(avg_temp - 4°C) × 0.418 kWh/°C`
   - Example: 50°C avg = (50-4) × 0.418 = **19.2 kWh**

2. **Daily totals** should add up to energy gained today:
   - If tank went from 20 kWh (morning) to 30 kWh (evening) = 10 kWh gained
   - Solar + Cartridge + Pellet should ≈ 10 kWh total

3. **Hourly rates** should match equipment power:
   - Cartridge heater ON → should show ~3 kW
   - Solar heating with good sun → 2-6 kW
   - No heating active → all rates should be near 0 kW

---

## Troubleshooting

**If numbers look wrong:**

1. **Check tank temperature sensors**:
   - Are RTD sensors 0-7 working? (Dashboard → Systems tab, when built)
   - Is MegaBAS sensor 5 reading correctly?

2. **Verify heat source detection**:
   - Check logs: `/tmp/solar_heating/logs/solar_heating_v3.log`
   - Look for: "Active heat sources: [solar, cartridge]"

3. **Inspect energy calculation logs**:
   - Search for: "Energy collected: X.XXX kWh"
   - Should show which sources contributed

4. **Common issues**:
   - **All zeros**: Sensors not reading or tank temperature below 4°C baseline
   - **Huge numbers**: Sensor calibration issue or temperature spike
   - **Wrong attribution**: Heat source detection logic needs tuning

---

## Code References

**Energy Storage Calculation:**
- File: `python/v3/main_system.py`
- Lines: 1520-1560 (stored energy from temperature sensors)

**Energy Source Attribution:**
- File: `python/v3/main_system.py`
- Lines: 1600-1700 (heat source detection and accumulation)

**Dashboard Display:**
- File: `python/v3/frontend/static/js/dashboard.js`
- Lines: 380-416 (updateEnergyCard method)
- Data source: `data.system_state.solar_energy_today`, etc.

---

## Summary

Your energy numbers are **real measurements** based on:
- ✅ Physical tank temperature changes
- ✅ Known water properties (mass, specific heat)
- ✅ Active heat source detection (pump state, relay state)
- ✅ Weighted allocation when multiple sources are active

**The numbers should match reality:**
- Solar energy on sunny days
- Cartridge heater matching its power rating
- Total energy matching tank capacity

**Next step**: Check your current dashboard values and compare to these expected ranges!
