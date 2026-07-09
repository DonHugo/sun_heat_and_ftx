# Solar Heating v3 — MQTT/HA Diagnostics Fix

**Date:** 2026-04-16
**Status:** ✅ Complete, deployed, verified, pushed to `origin/main`
**Project:** solar_heating_v3
**Themes:** mqtt, diagnostics, systemd, web-gui

## Problem

Web GUI "System Diagnostics" panel at `http://192.168.0.18:8080` showed
**MQTT Status: Disconnected** and **Home Assistant Status: Disconnected**
despite the backend being healthy and publishing to the broker.

## Root Cause

Two systemd services competed for port 5001:

- `solar_heating_api.service` — standalone mock `run_api_server.py` with a
  `MockSolarSystem` that had no `.mqtt` attribute. Won the port race.
- `solar_heating_v3.service` — real `main_system.py` with embedded API
  (lines 692–717) and a real `SolarHeatingSystem`. Silently failed to bind.

Frontend (`dashboard.js` 819–822) derives HA status from MQTT status, so
fixing MQTT fixed both indicators.

## Fixes (4 commits on `main`)

| SHA       | File               | Change |
|-----------|--------------------|--------|
| `99227d5` | `api_server.py`    | `_get_mqtt_status()` uses `getattr(self.solar_system, "mqtt", None)` |
| `38a1eca` | `mqtt_handler.py`  | Reconnect refactor: `_reconnecting` flag, `_reconnect_lock`, daemon thread |
| `bb8d218` | `mqtt_handler.py`  | `is_connected()` delegates to paho client |
| `5a4bbbd` | `run_api_server.py`, `docs/RUNBOOK.md` | DEPRECATED header + `__main__` guard that exits 1; RUNBOOK Section 8 troubleshooting + Section 9 Phase 5 deployment record |

## Deployment Actions

- `sudo systemctl stop solar_heating_api.service`
- `sudo systemctl disable solar_heating_api.service`
- `sudo systemctl restart solar_heating_v3.service`
- Deployed via `sudo rm` + `sudo cp` (never `cp -f` — Pi filesystem caching)

## Verification

- `curl :5001/api/mqtt` → `{"connected": true, "broker": "Connected", ...}` ✅
- `curl :5001/api/status` → healthy JSON ✅
- Zero DEBUG lines in journal ✅
- `curl :8080/` → 200 ✅
- User visually confirmed dashboard "looks good" ✅

## Rollback

```bash
sudo systemctl enable --now solar_heating_api.service
```

(Not recommended — mock service is the original bug source.)

## Runtime Environment Reference

- Host: `pi@192.168.0.18` (`rpi-solfangare-2`)
- Broker: `192.168.0.110:1883`
- `/home/pi/solar_heating/` — git checkout (runtime for web_gui service)
- `/opt/solar_heating_v3/` — runtime for `main_system.py` (owns :5001)
- `/opt/solar_heating/frontend/` — nginx static assets

## Key Files

- `python/v3/api_server.py` — `_get_mqtt_status()` ~239, `MQTTAPI` ~823
- `python/v3/mqtt_handler.py` — reconnect 188+, `is_connected()` 925–934
- `python/v3/main_system.py` — embedded API startup 692–717
- `python/v3/web_server.py` — GUI on :8080, proxies `--api-port 5001`
- `python/v3/frontend/static/js/dashboard.js` — `/api/mqtt` poll 199, `updateMQTTStatus()` 793–823
- `python/v3/run_api_server.py` — now DEPRECATED, exits 1 if invoked
- `docs/RUNBOOK.md` — authoritative deployment guide
- `docs/MQTT_HA_DIAGNOSTIC_PLAN.md` — original diagnostic plan

## Follow-ups (optional)

- Monitor journal for MQTT reconnect edge cases over next few days
- Future cleanup: consider removing `run_api_server.py` entirely
- Cleanup leftover `/tmp/api_server.py.new` staging file on Pi

## Memory MCP Note

Attempted to save this as a `memory_continuity` snapshot but the tool's
exposed schema does not allow passing the required `action` discriminator
field. Saved here as markdown instead. If the MCP tool wrapper is fixed
later, replay with:

```json
{
  "action": "save",
  "type": "snapshot",
  "title": "Solar Heating v3 MQTT/HA diagnostics fix complete",
  "project": "solar_heating_v3",
  "themes": ["mqtt", "diagnostics", "systemd"],
  "entities": ["api_server.py", "mqtt_handler.py", "run_api_server.py", "RUNBOOK.md"],
  "next_steps": ["Monitor reconnect edge cases", "Consider removing run_api_server.py"]
}
```
