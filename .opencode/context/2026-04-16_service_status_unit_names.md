# Service Status panel — unit name fix

Date: 2026-04-16
Commit: `27072e9` on `main`
File: `python/v3/api_server.py` (`_get_service_status`, ~L307–337)

## Problem

Web GUI "System Diagnostics → Service Status" showed MQTT and (sometimes)
Watchdog as **inactive** even when the system was healthy.

## Root causes

1. Hardcoded unit list used `"mqtt"` as a systemd unit name. No such unit
   exists on the Pi — the broker is `mosquitto.service`. `systemctl is-active mqtt`
   therefore always returned non-zero, and the code forced the status to
   `"inactive"`.
2. The code mapped any non-zero return code from `systemctl is-active` to
   `"inactive"`, hiding `activating`, `failed`, `deactivating`, etc.

## Fix

- Introduced a dict mapping **frontend key → real systemd unit**:
  - `solar_heating_v3` → `solar_heating_v3`
  - `mqtt` → `mosquitto`
  - `solar_heating_watchdog` → `solar_heating_watchdog`
- Always take the state string from `result.stdout` (regardless of return
  code) so transitional states surface in the UI.
- `"unknown"` is now reserved for subprocess errors only.

Frontend (`python/v3/frontend/static/js/dashboard.js` L307–310) already
consumes `data.service_status.{solar_heating_v3,mqtt,solar_heating_watchdog}`
— no frontend change required.

## Deploy + verification

Deployed to `/opt/solar_heating_v3/api_server.py` via `sudo rm` + `sudo cp`
per `docs/RUNBOOK.md`, restarted `solar_heating_v3.service`.

`curl http://192.168.0.18:5001/api/status` → `service_status`:

```json
{
  "solar_heating_v3": "active",
  "mqtt": "active",
  "solar_heating_watchdog": "activating"
}
```

All three keys now report the real systemd state.

## Follow-up (separate issue, NOT part of this change)

`solar_heating_watchdog.service` is crash-looping (~74016 restarts):

```
ValueError: MQTT credentials required. Set MQTT_USERNAME and MQTT_PASSWORD
environment variables.
  File "/home/pi/solar_heating/python/v3/watchdog.py", line 76, in __post_init__
```

The diagnostics panel is now correctly exposing this pre-existing problem
(previously masked as "inactive"). Likely fix: ensure the systemd unit for
the watchdog sources the same env file / `EnvironmentFile=` as
`solar_heating_v3.service`, or that `watchdog.py` loads `.env` the same
way the main service does. Needs user direction before acting.
