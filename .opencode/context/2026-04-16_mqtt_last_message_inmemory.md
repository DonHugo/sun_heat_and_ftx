# MQTT Last Message — In-Memory Tracking (Diagnostics Fix)

## Goal
System Diagnostics panel should show real MQTT Last Message (topic/payload/timestamp) instead of `"No messages / No data / Never"`.

## Acceptance Criteria
- [x] `/api/mqtt` returns populated `last_message` object with real topic/payload/timestamp/qos/direction.
- [x] No regression in service startup or log output.
- [x] Deployed to Pi and verified live.
- [x] Committed & pushed to `origin/main`.

## Root Cause
`APIServer._get_last_mqtt_message()` spawned `journalctl` and parsed stdout with a regex anchored to `^` expecting Python log timestamps. systemd journal lines are prefixed with syslog headers (`Apr 16 22:22:05 rpi-solfangare-2 python3[PID]: ...`), so the regex never matched. Result: panel always blank.

## Architectural Change
Replaced shell-based log scraping with in-memory attribute on `MQTTHandler`:

- `MQTTHandler.last_message: Optional[Dict[str, Any]]` populated on each publish / receive.
- `APIServer._get_mqtt_status()` reads `getattr(mqtt_handler, "last_message", None)` directly.
- `_get_last_mqtt_message()` method deleted entirely.
- `subprocess` / `re` imports in `api_server.py` kept — still used elsewhere (lines 353, 635).

## Key Files
- `python/v3/mqtt_handler.py`
  - `from datetime import datetime` import added.
  - `self.last_message` initialized in `__init__` (line 73).
  - `_record_last_message(topic, payload, direction, qos)` helper (line 369).
  - Call sites:
    - `_on_message` line 394 — direction `"in"`, qos from `msg.qos`.
    - `_handle_pellet_stove_data` line 501 — direction `"in"`.
    - `publish()` success branch line 748 — direction `"out"`, qos from arg.
- `python/v3/api_server.py`
  - `_get_mqtt_status()` simplified.
  - `_get_last_mqtt_message()` removed.

## Deployment
- Pi host: `pi@192.168.0.18`, API on port **5001**.
- Runtime path: `/opt/solar_heating_v3/`.
- Procedure (per `docs/RUNBOOK.md`): `scp` → `sudo rm` → `sudo cp` → `sudo systemctl restart solar_heating_v3.service`.

## Verification
`curl http://192.168.0.18:5001/api/mqtt` returns e.g.:
```json
{
  "mqtt_status": {
    "connected": true,
    "broker": "Connected",
    "last_message": {
      "topic": "homeassistant/sensor/udm_pro_cpu_utilization/state",
      "payload": "26.3",
      "timestamp": "2026-04-16 22:31:20",
      "qos": 0,
      "direction": "in"
    }
  }
}
```

## Commit
`d1048e3` on `main` — "fix(mqtt): track last message in-memory for diagnostics API"
(2 files changed, 28 insertions, 44 deletions). Pushed `5a4bbbd..d1048e3`.

## Notes
- Frontend consumer (`dashboard.js` `updateMQTTStatus()` ~L793–823, `index.html` `#mqtt-last-message` L394) required no changes — payload shape unchanged.
- In-memory tracking is lost on restart; acceptable since new messages arrive within seconds.
- Future: if diagnostics need history, add ring-buffer (N=10) rather than re-introducing journalctl parsing.
