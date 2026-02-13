#!/bin/bash
# Quick energy number verification tool
# Usage: ./verify_energy_numbers.sh

echo "================================================"
echo "Energy Number Verification Tool"
echo "================================================"
echo ""

# Fetch current status from API
echo "Fetching current system status..."
STATUS=$(curl -s http://192.168.0.18/api/status)

if [ -z "$STATUS" ]; then
    echo "❌ ERROR: Could not fetch API data"
    echo "   Check that the API is running on http://192.168.0.18/api/status"
    exit 1
fi

echo "✅ API data retrieved"
echo ""

# Extract energy values using jq
SOLAR_TODAY=$(echo "$STATUS" | jq -r '.system_state.solar_energy_today // 0')
CARTRIDGE_TODAY=$(echo "$STATUS" | jq -r '.system_state.cartridge_energy_today // 0')
PELLET_TODAY=$(echo "$STATUS" | jq -r '.system_state.pellet_energy_today // 0')

SOLAR_HOUR=$(echo "$STATUS" | jq -r '.system_state.solar_energy_hour // 0')
CARTRIDGE_HOUR=$(echo "$STATUS" | jq -r '.system_state.cartridge_energy_hour // 0')
PELLET_HOUR=$(echo "$STATUS" | jq -r '.system_state.pellet_energy_hour // 0')

# Calculate total
TOTAL_TODAY=$(echo "$SOLAR_TODAY + $CARTRIDGE_TODAY + $PELLET_TODAY" | bc)

# Check pump and heater status
PUMP_ON=$(echo "$STATUS" | jq -r '.system_state.primary_pump')
HEATER_ON=$(echo "$STATUS" | jq -r '.system_state.cartridge_heater')

# Get temperatures
SOLAR_TEMP=$(echo "$STATUS" | jq -r '.temperatures.solar_collector // 0')
TANK_TEMP=$(echo "$STATUS" | jq -r '.temperatures.storage_tank // 0')
DT=$(echo "$SOLAR_TEMP - $TANK_TEMP" | bc)

echo "================================================"
echo "DAILY ENERGY TOTALS (kWh)"
echo "================================================"
printf "☀️  Solar:           %6.2f kWh\n" "$SOLAR_TODAY"
printf "🔥 Cartridge Heater: %6.2f kWh\n" "$CARTRIDGE_TODAY"
printf "🪵 Pellet Furnace:   %6.2f kWh\n" "$PELLET_TODAY"
echo "------------------------------------------------"
printf "📊 TOTAL:            %6.2f kWh\n" "$TOTAL_TODAY"
echo ""

echo "================================================"
echo "CURRENT HOURLY RATES (kWh in last hour)"
echo "================================================"
printf "☀️  Solar:           %6.2f kWh/h\n" "$SOLAR_HOUR"
printf "🔥 Cartridge Heater: %6.2f kWh/h\n" "$CARTRIDGE_HOUR"
printf "🪵 Pellet Furnace:   %6.2f kWh/h\n" "$PELLET_HOUR"
echo ""

echo "================================================"
echo "CURRENT SYSTEM STATE"
echo "================================================"
echo "Primary Pump:     $PUMP_ON"
echo "Cartridge Heater: $HEATER_ON"
printf "Solar Collector:  %.1f°C\n" "$SOLAR_TEMP"
printf "Tank Temperature: %.1f°C\n" "$TANK_TEMP"
printf "Temperature Diff: %.1f°C\n" "$DT"
echo ""

echo "================================================"
echo "SANITY CHECKS"
echo "================================================"

# Check if total is within reasonable range
if (( $(echo "$TOTAL_TODAY > 36" | bc -l) )); then
    echo "⚠️  WARNING: Total energy ($TOTAL_TODAY kWh) exceeds tank capacity (36 kWh)"
    echo "    This suggests a sensor or calculation issue."
else
    echo "✅ Total energy within expected range (<36 kWh)"
fi

# Check cartridge heater rate
if [ "$HEATER_ON" = "true" ]; then
    if (( $(echo "$CARTRIDGE_HOUR < 2" | bc -l) )); then
        echo "⚠️  WARNING: Cartridge heater ON but hourly rate is low ($CARTRIDGE_HOUR kWh/h)"
        echo "    Expected ~3 kWh/h for a 3kW heater"
    elif (( $(echo "$CARTRIDGE_HOUR > 4" | bc -l) )); then
        echo "⚠️  WARNING: Cartridge heater rate too high ($CARTRIDGE_HOUR kWh/h)"
        echo "    Expected ~3 kWh/h for a 3kW heater"
    else
        echo "✅ Cartridge heater rate looks reasonable (~3 kWh/h expected)"
    fi
else
    if (( $(echo "$CARTRIDGE_HOUR > 0.1" | bc -l) )); then
        echo "⚠️  WARNING: Cartridge heater OFF but showing energy ($CARTRIDGE_HOUR kWh/h)"
        echo "    May be residual from recent shutdown"
    else
        echo "✅ Cartridge heater OFF and no energy being added"
    fi
fi

# Check solar
if [ "$PUMP_ON" = "true" ] && (( $(echo "$DT > 5" | bc -l) )); then
    if (( $(echo "$SOLAR_HOUR < 0.5" | bc -l) )); then
        echo "⚠️  WARNING: Solar should be heating (pump ON, dT=$DT°C) but low energy"
    else
        echo "✅ Solar actively heating (pump ON, dT=$DT°C)"
    fi
elif [ "$PUMP_ON" = "false" ]; then
    if (( $(echo "$SOLAR_HOUR > 0.1" | bc -l) )); then
        echo "⚠️  WARNING: Solar pump OFF but showing energy ($SOLAR_HOUR kWh/h)"
        echo "    May be residual from recent shutdown"
    else
        echo "✅ Solar pump OFF and no energy being added"
    fi
fi

echo ""
echo "================================================"
echo "RECOMMENDATIONS"
echo "================================================"

# Time-based recommendations
HOUR=$(date +%H)
if [ "$HOUR" -ge 6 ] && [ "$HOUR" -le 18 ]; then
    echo "🌞 It's daytime ($HOUR:00) - solar energy should be accumulating if sunny"
    if (( $(echo "$SOLAR_TODAY < 1" | bc -l) )); then
        echo "   Note: Solar total is low ($SOLAR_TODAY kWh) - cloudy day or issue?"
    fi
else
    echo "🌙 It's nighttime ($HOUR:00) - solar energy should be zero"
fi

# Expected ranges
echo ""
echo "Expected Ranges (for reference):"
echo "  Solar daily:     0-30 kWh (depends on weather)"
echo "  Cartridge daily: 3 kWh per hour of operation"
echo "  Pellet daily:    5-15 kWh per hour of operation"
echo ""
echo "See ENERGY_CALCULATION_EXPLAINED.md for detailed info"
echo "================================================"
