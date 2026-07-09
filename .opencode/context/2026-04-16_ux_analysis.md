# UX Analysis — Solar Heating Web GUI

**Date:** 2026-04-16
**Scope:** `http://192.168.0.18/` (nginx :80 serving `/opt/solar_heating/frontend/`, proxy `/api/` → `127.0.0.1:5001`)
**Method:** Playwright browser at desktop (1280×720) and mobile (375×812) viewports; all 5 views inspected (Dashboard, Temperature, All Systems, System Control, Diagnostics); source review of `index.html` (659 L), `style.css` (2182 L), `dashboard.js` (1252 L).
**Status:** Advisory. No code changes made.

---

## TL;DR

The UI is functional and information-rich, but shows several rough edges that undermine trust:

1. **Stale error state** — startup race produces a "Failed to connect" toast and red footer status that never clears on recovery.
2. **Fragile mobile navigation** — hamburger is a CSS pseudo-element with hard-coded hit-box coordinates; not screen-reader accessible; programmatic clicks fail.
3. **Mobile overflow on Diagnostics** — long MQTT topic string and notification panel exceed 375 px viewport.
4. **Accessibility gaps** — raw Material Design Icons glyphs leak into the a11y tree as literal text; tab buttons lack `role="tab"` / `aria-selected`.
5. **"Never" placeholders** in System Control (last-changed timestamps) look broken rather than intentional.
6. **Significant code hygiene debt** — 50+ backup files in `frontend/` alongside active assets; risk of confusion and accidental deploys.

Prioritisation below: **P1** = trust/clarity blockers, **P2** = polish, **P3** = long-term hygiene.

---

## 1. Information Architecture & Navigation

### Observed
- 5-item sidebar: Dashboard, Temperature, All Systems, System Control, Diagnostics.
- `index.html` L20–40: `<button class="sidebar-link" data-tab="...">`; tab switching via `dashboard.js` L119–145 (`setupTabNavigation()`), toggling `.active` on `.tab-content` siblings.
- On mobile (`<= 768 px`), sidebar is off-screen (`style.css` L166 `@media`); `.sidebar.open` slides in. Tab click auto-closes sidebar (L137–142).

### Issues
- **Hamburger is a pseudo-element** (`::before`) with no `<button>` or ARIA. `setupSidebarToggle()` (dashboard.js L147–174) listens on `document.body` and checks if click coords fall within hard-coded rect `(20,20)–(70,70)`. This means:
  - Keyboard users cannot open the sidebar.
  - Screen readers see no control.
  - Automated testing (Playwright) can't reliably trigger it — click coords on the pseudo-element fall outside the literal `20–70` box.
  - Changing the header layout silently breaks the hit-box.
- Tab buttons use `data-tab` but no `role="tab"` / `aria-selected` / `aria-controls` relationships → assistive tech sees 5 unlabelled buttons.

### Recommendations
- **P1:** Replace pseudo-element hamburger with a real `<button class="sidebar-toggle" aria-label="Open navigation" aria-expanded="false">` in markup. Wire an explicit `click` handler; drop coordinate math.
- **P2:** Add `role="tablist"` on sidebar, `role="tab"` + `aria-selected` on each button, `role="tabpanel"` + `aria-labelledby` on each `.tab-content`.
- **P2:** Trap focus inside sidebar while open on mobile; close on `Escape`.

---

## 2. State Feedback & Error Handling

### Observed
- First `/api/status` after page load returns **500**; the 5-second retry returns 200. Startup race in `api_server.py`.
- `dashboard.js` L206–214 (`loadSystemData` error path):
  - Flips footer `#api-status` text to "Disconnected", adds `.error` class.
  - Fires `showNotification('Failed to connect to API server', 'error')`.
- On subsequent success there is **no symmetric clearing** — no `hideNotification()`, no reset of footer class. Result:
  - Persistent red "Failed to connect" toast while data is flowing.
  - Footer badge text "Disconnected" with green dot (CSS class desync: background indicator and text driven by different update paths).
- `showNotification()` defined at L1044; 11 call sites (L53, 211, 841, 855, 871, 875, 880, 895, 911, 939). No counterpart `clearNotifications()` / `dismissByType()`.

### Recommendations
- **P1 (immediate polish):**
  - On successful `loadSystemData`, explicitly set footer status back to connected state and call a new `clearErrorNotifications('api')` helper.
  - Or: suppress the toast during the first N seconds after page load; only fire after 2 consecutive failures.
- **P1 (root cause):** Fix the startup 500 in `api_server.py`. Likely the MQTT client/data cache isn't initialised when the first request arrives. Return 503 with a `Retry-After` header until ready, or gate the route on a `service_ready` flag.
- **P2:** Single source of truth for API connection state — one module-level variable that updates both the footer badge and any toast visibility.

---

## 3. Visual Hierarchy & Consistency

### Observed
- **Dashboard:** Clear hero metric (current temperatures) with cards for each subsystem. Works well.
- **All Systems:** Dense; each subsystem (Solar, Cartridge, Water Tank, FTX) gets equivalent visual weight even though Solar is primary.
- **System Control:** Three panels with "Last Changed: Never", "Mode Changed: Never", "Last Activated: Never". Reads as broken even when it means "no changes since boot".
- **Diagnostics:** Mixes operational status (services, MQTT) with raw technical detail (full MQTT topic strings, last message payloads). No grouping hierarchy beyond card borders.

### Recommendations
- **P2:** Replace "Never" with explicit copy: "No changes since startup at 14:32" or "—" with tooltip explaining. Distinguishes "working, nothing happened" from "tracking broken".
- **P2:** On All Systems, give Solar Heating either a larger card, a top row of its own, or a colour accent — it's the raison d'être of the system.
- **P3:** Diagnostics could split into two subsections: "Health" (green/red indicators, human-readable) and "Technical Details" (collapsed by default, contains topics, payloads, IDs).

---

## 4. Responsive / Mobile (375×812)

### Observed
- `@media (max-width: 768px)` breakpoints at L166, 812, 859, 1349, 1515, 1554, 1613, 2032 — eight blocks, suggests incremental fixes rather than a mobile-first design.
- **Diagnostics view on mobile:** Horizontal scroll appears. MQTT topic strings (long, no breaks) and the notification panel force width beyond 375 px.
- Sidebar overlay works once open (confirmed via CSS read), but the opening gesture is broken (see §1).

### Recommendations
- **P1:** Add `overflow-wrap: anywhere` (or `word-break: break-all`) to MQTT topic / payload text cells.
- **P1:** Constrain `.notification`/toast container to `max-width: calc(100vw - 2rem)` and `right: 1rem` (rather than fixed widths).
- **P2:** Consolidate the 8 mobile media-query blocks into one or two coherent sections; audit for contradicting rules.
- **P3:** Consider a mobile-first rewrite of `style.css`. 2182 lines with 8 breakpoint blocks is a maintenance hazard.

---

## 5. Accessibility

### Observed
- Material Design Icons used via icon font; glyphs like `󰔏 󰶛 󰖌` appear in the Playwright a11y snapshot as literal text — meaning screen readers will read them as unpronounceable characters.
- No visible skip-link.
- Tab buttons missing ARIA (see §1).
- Colour is the primary carrier of status (green/red dots); no text equivalent on the footer badge until you read the adjacent word.
- No confirmed keyboard focus styles (not verified exhaustively — recommend audit).

### Recommendations
- **P1:** Wrap MDI glyphs in `<span aria-hidden="true">` and add visually-hidden text labels (`<span class="sr-only">`).
- **P2:** Add `<a class="skip-link" href="#main">Skip to main content</a>` as first focusable element.
- **P2:** Audit `:focus-visible` styles across all interactive controls; ensure 3:1 contrast.
- **P2:** Pair every status colour with an icon or text (e.g., ✓ Connected / ✕ Disconnected).

---

## 6. Performance & Asset Management

### Observed
- `dashboard.js` loaded with `?v=24` cache-bust query — manual versioning.
- `style.css` is 2182 lines, unminified.
- No evidence of HTTP compression check (recommend verifying nginx `gzip on` for text/css, application/javascript).

### Recommendations
- **P3:** Move to content-hash cache busting (`dashboard.[hash].js`) or rely on nginx `ETag`/`Cache-Control: no-cache` + conditional requests.
- **P3:** Consider minifying CSS/JS on deploy. At current file sizes, gains are modest but startup cost on the Pi's local network is still real.

---

## 7. Code Hygiene / Deploy Safety (high priority for maintainer)

### Observed — `python/v3/frontend/`
- **16×** `index.html.*` backups (`.bak`, `.before-*`, versioned)
- **14×** `style.css.*` backups
- **20×** `dashboard.js.*` backups
- Additional dev artefacts: `api-mock.js`, `index-dev.html`, `README-DEV.md`
- `web_server.py.bak` alongside `web_server.py` (legacy :8080 Flask server, likely unused now nginx serves statics).

### Risks
- Easy to `cp` a stale `.bak` over live asset during troubleshooting.
- `rsync` / deploy scripts may pick up unwanted files depending on include/exclude rules.
- Git history is the proper place for "before" snapshots; these files duplicate that role unreliably.

### Recommendations
- **P2:** Move all `*.bak*`, `*.before-*`, `*.v[0-9]*`, `index-dev.html`, `api-mock.js`, `README-DEV.md` into `python/v3/frontend/_archive/` (or delete after confirming git has them). Leave a `_archive/README.md` explaining.
- **P2:** Delete `web_server.py` + `.bak` if the :8080 server is truly dead. Verify no systemd unit references it first.
- **P3:** Add `.gitignore` / deploy-script excludes for `*.bak*`, `*.before-*` under `frontend/`.

---

## 8. Diagnostics View — Specific Observations

After sub-tasks 1 & 2 (deployed earlier today), Diagnostics now shows real data. Observations:

- **MQTT Last Message** card renders correctly with topic + payload + timestamp.
- **Service Status** card lists units with accurate active/inactive states.
- **Layout:** Works on desktop; overflows on mobile (see §4).
- **Watchdog:** Card shows service as running but the underlying MQTT auth is broken (known; awaiting Option A/B/C decision). The UI has no way to surface this — the service appears healthy even though its MQTT subscriber loop is failing.

### Recommendation
- **P2:** Each monitored service card should report *functional* health, not just `systemctl is-active`. Expose a `/health` endpoint per service (or have the service publish a heartbeat to MQTT) and display last-heartbeat age.

---

## Prioritised Backlog

### P1 (trust/correctness, do first)
1. Clear "Failed to connect" toast + reset footer badge when API recovers (`dashboard.js` L206–214).
2. Fix startup 500 in `api_server.py` (initialise before accepting requests; or return 503 with backoff).
3. Replace pseudo-element hamburger with real `<button>` + ARIA.
4. Mobile overflow fixes on Diagnostics (word-break for long topics; constrain toast width).
5. `aria-hidden` on MDI glyphs + screen-reader labels.

### P2 (polish / a11y)
6. ARIA tablist/tab/tabpanel on sidebar + panels.
7. Replace "Never" placeholders with meaningful copy.
8. Pair colour status with icon/text.
9. Archive backup files out of `frontend/`.
10. Remove legacy `web_server.py` if confirmed unused.

### P3 (long-term)
11. Mobile-first CSS rewrite / media-query consolidation.
12. Content-hash cache busting + minification.
13. Per-service functional health endpoints surfaced in Diagnostics.

---

## Not Changed

No code was modified during this analysis. All findings above are observations + recommendations for a future implementation pass. Watchdog MQTT auth fix (Option A/B/C) is still paused awaiting user decision — see `.opencode/context/` prior notes.

---

## Implementation Pass — 2026-04-16 (evening)

### Watchdog MQTT Auth Fix — COMPLETE
Option A applied: commented `MQTT_USERNAME` / `MQTT_PASSWORD` lines (L40–41) in `/home/pi/solar_heating/python/v3/.env` on Pi. Watchdog now connects to Mosquitto anonymously. Pi-only edit, not mirrored to repo.

### P1 Items — ALL COMPLETE (deployed, verified)
1. **Toast clearing + 503 silent-retry** (`dashboard.js`): 503 responses during API startup now log and defer to next poll instead of surfacing error toasts.
2. **503 startup race** (`api_server.py`): 5 Resource classes now return 503 + Retry-After when system not yet initialized (prevents misleading 500s during boot).
3. **Hamburger menu button** (HTML+CSS+JS): 50×50 touch target, click/Escape/outside-click close, hidden on desktop (`≥768px`).
4. **Mobile overflow fix** (`style.css`): resolved horizontal scroll on 375px viewports.
5. **MDI icon a11y**: `aria-hidden="true"` on 32 decorative glyphs, screen-reader labels where needed.

Cache bust: CSS `v=36`, JS `v=25`. Frontend deployed to `/opt/solar_heating/frontend/`.

### Sidequest: `/api/status` 500 Regression — FIXED
**Symptom**: All `/api/status` calls returned 500 with `AttributeError: RATE_LIMIT_EXCEEDED` in `rate_limiter.py:206`.
**Root causes**:
1. `APIErrorCode` enum (in `api_errors.py`) missing `RATE_LIMIT_EXCEEDED` member. **Fix**: added `RATE_LIMIT_EXCEEDED = "E400"` + ERROR_MESSAGES entry `"Rate limit exceeded, please retry"`.
2. `rate_limiter.py` called `create_error_response()` with wrong signature and treated return value as a Flask Response. **Fix**: corrected kwargs to `(error_code, details: str, exception, http_status)`, wrapped dict return with `make_response(jsonify(...), status)`, added `make_response` to flask import (L12).

**Files deployed** to `/opt/solar_heating_v3/` with `.bak-20260416-234641`:
- `api_errors.py` (126 lines)
- `rate_limiter.py` (231 lines, L12 import + L203–221 block edited)

Service restarted 23:46 CEST. **Verification**: 30× curl `/api/status` → 30× 200, zero 500s, no rate_limiter tracebacks in journal.

### Observations (not in scope, logged for follow-up)
- `/api/system` returns **404** — endpoint referenced by frontend but never registered in `api_server.py`. Pre-existing defect unrelated to this pass.
- MegaBAS sensor 5 WARN in journal — pre-existing hardware issue.
- HA discovery `KeyError: 'device_class'` — pre-existing bug, separate from UX work.

### Deployed File Inventory (all live on Pi)
| Local path | Pi path | Backup |
|---|---|---|
| `python/v3/api_server.py` | `/opt/solar_heating_v3/api_server.py` | `.bak-20260416-232512` |
| `python/v3/api_errors.py` | `/opt/solar_heating_v3/api_errors.py` | `.bak-20260416-234641` |
| `python/v3/rate_limiter.py` | `/opt/solar_heating_v3/rate_limiter.py` | `.bak-20260416-234641` |
| `python/v3/frontend/index.html` | `/opt/solar_heating/frontend/index.html` | — |
| `python/v3/frontend/static/js/dashboard.js` | `/opt/solar_heating/frontend/static/js/dashboard.js` | — |
| `python/v3/frontend/static/css/style.css` | `/opt/solar_heating/frontend/static/css/style.css` | — |


## References
- Sources reviewed: `python/v3/frontend/index.html`, `python/v3/frontend/static/css/style.css`, `python/v3/frontend/static/js/dashboard.js`
- Snapshots captured: `.playwright-mcp/page-2026-04-16T20-*.yml` (11 snapshots across 5 views + mobile variants)
- Prior context: `2026-04-16_mqtt_ha_diagnostics_fix.md`, `2026-04-16_mqtt_last_message_inmemory.md`, `2026-04-16_service_status_unit_names.md`
