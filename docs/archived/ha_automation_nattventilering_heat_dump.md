# Archived: HA Automation "Solvärme: Nattventilering (heat dump)"

**Removed:** 2026-07-08
**Reason:** Superseded by the built-in **night cooling** feature in Solar Heating
System v3 (entities: `switch.solar_heating_system_v3_night_cooling`,
`number.solar_heating_system_v3_night_cooling_tank_temperature`,
`binary_sensor.solar_heating_system_v3_night_cooling_active`).

The v3 feature is temperature-controlled: it runs the primary pump when the tank
is at/above the threshold (default 80°C) AND the collector is at least 5°C
colder — which naturally happens at night. Keeping this HA automation alongside
it caused both to compete for the primary pump (the automation took manual
control, which made v3 skip its own night-cooling logic via the manual-override
gate). We chose to consolidate on the v3 feature (single source of truth).

## Differences vs the v3 feature (for reference)

This automation had a few extras the v3 feature does NOT currently replicate:
- **Time window** 23:00–05:00 (v3 is purely temperature-driven, no clock)
- **Pellet-stove guard** (`binary_sensor.kamin_status` off) — don't dump heat the
  stove just made
- **Hard stop at 05:30** and a 3h safety timeout
- **Mobile notifications** on start/finish
- **70°C floor** to avoid overcooling (v3 uses a 5°C hysteresis below the
  threshold, so 80°C threshold → stops at 75°C)

If any of these behaviours are wanted later, they can be added to the v3 control
logic in `python/v3/main_system.py` (the night cooling block) rather than
re-creating a competing HA automation.

## Original configuration (as of removal)

```yaml
id: "1783495815474"
alias: "Solvärme: Nattventilering (heat dump)"
description: >-
  Dumps excess tank heat on hot summer nights by running the primary solar pump
  in reverse-cooling mode (collector radiates to the night sky). Fills the gap
  left by the built-in cooling (which protects the COLLECTORS at 90°C, not the
  tank). Starts when tank top (140cm) exceeds 80°C during the night window,
  verified that the collector outlet is meaningfully colder than the tank (so
  pumping actually removes heat). Stops at a 70°C floor so we don't overcool and
  force the pellet stove to fire next morning. Uses primary_pump_manual_control
  to take over the pump, and ALWAYS releases control (manual_control=off) at the
  end even on timeout/restart. Level re-check trigger catches an already-hot tank
  at window start.
triggers:
  - alias: "Tank top climbs above 80°C (sustained 5 min to avoid bounce)"
    trigger: numeric_state
    entity_id: sensor.solar_heating_system_v3_water_heater_140cm_temperature
    above: 80
    for:
      minutes: 5
  - alias: "Periodic re-check during night window — catches a tank that was already hot before the window opened"
    trigger: time_pattern
    minutes: "/15"
conditions:
  - alias: "Only during the night window (23:00–05:00 local)"
    condition: time
    after: "23:00:00"
    before: "05:00:00"
  - alias: "Tank top is genuinely hot (>80°C)"
    condition: numeric_state
    entity_id: sensor.solar_heating_system_v3_water_heater_140cm_temperature
    above: 80
  - alias: "Cooling is actually possible: collector outlet at least 10°C colder than tank top"
    condition: template
    value_template: "{{ (states('sensor.solar_heating_system_v3_water_heater_140cm_temperature') | float(0) - states('sensor.solar_heating_system_v3_solar_collector_outlet_temperature') | float(999)) >= 10 }}"
  - alias: "No one else is already holding manual pump control"
    condition: state
    entity_id: switch.solar_heating_system_v3_primary_pump_manual_control
    state: "off"
  - alias: "Pellet stove is not running (don't dump heat it just made)"
    condition: state
    entity_id: binary_sensor.kamin_status
    state: "off"
actions:
  - alias: "Take over the pump"
    action: switch.turn_on
    target:
      entity_id: switch.solar_heating_system_v3_primary_pump_manual_control
  - alias: "Start pump to dump heat via collector"
    action: switch.turn_on
    target:
      entity_id: switch.solar_heating_system_v3_primary_pump
  - action: notify.mobile_app_svs_iphone_hugo_mobil
    data:
      title: "🌙 Nattventilering startad"
      message: "Dumpar överskottsvärme. Tank-topp: {{ states('sensor.solar_heating_system_v3_water_heater_140cm_temperature') }}°C, kollektor ut: {{ states('sensor.solar_heating_system_v3_solar_collector_outlet_temperature') }}°C. Kör tills 70°C."
  - alias: "Wait until tank drops to 70°C floor, or 05:30 hard stop, or 3h safety timeout"
    wait_for_trigger:
      - alias: "Tank reached the 70°C floor"
        trigger: numeric_state
        entity_id: sensor.solar_heating_system_v3_water_heater_140cm_temperature
        below: 70
      - alias: "Hard stop at 05:30 regardless"
        trigger: time
        at: "05:30:00"
    timeout:
      hours: 3
    continue_on_timeout: true
  - alias: "ALWAYS stop the pump (runs on floor reached, hard stop, or timeout)"
    action: switch.turn_off
    target:
      entity_id: switch.solar_heating_system_v3_primary_pump
  - alias: "ALWAYS release control back to the system"
    action: switch.turn_off
    target:
      entity_id: switch.solar_heating_system_v3_primary_pump_manual_control
  - action: notify.mobile_app_svs_iphone_hugo_mobil
    data:
      title: "✅ Nattventilering klar"
      message: "Ventilering avslutad. Tank-topp nu: {{ states('sensor.solar_heating_system_v3_water_heater_140cm_temperature') }}°C. {% if not wait.completed %}(stoppad på timeout){% endif %}"
mode: restart
```
