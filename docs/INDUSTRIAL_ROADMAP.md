# Industrial roadmap — module status against the research vault

This is the cross-reference the research vault's own Module 0 requires: for each of
the vault's 20 prototype modules (`docs/research/vault/48 PROTOTYPE MODULES/`), what
is actually true in this codebase right now, versus what the vault's template still
lists as `UNKNOWN — REQUIRES DESIGN`. The vault's own module templates had never been
synced against real implementation progress before this document — several modules
below (5–10, 13) are substantially built despite their vault template still saying
`status: planned`.

Status labels below follow the vault's own convention
(`docs/research/vault/00 MASTER CONTROL/Geo-Sentry Prototype Evidence and Demonstration Checklist.md`,
"Prototype Status Labels" section): `IMPLEMENTED`, `IMPLEMENTED — NEEDS VALIDATION`,
`SIMULATED`, `DESIGN ONLY`, `FIELD VALIDATION REQUIRED`, `NOT IMPLEMENTED`.

| # | Module | Status | Evidence |
|---:|---|---|---|
| 0 | Research & Evidence Control | **IMPLEMENTED** | `docs/research/vault/` (this branch) |
| 1 | Physical Sensing | **IMPLEMENTED — real hardware** | Real ESP32 + MPU6050 + potentiometer nodes (`NodeA.ino`/`NodeB.ino`), team-tested and working. Only one combined tilt-from-vertical angle is measured, not independent X/Y axes — see Module 2 |
| 2 | Sensor Node & Firmware | **IMPLEMENTED — real, tested hardware** | `firmware/sensor-node/NodeA/NodeA.ino`, `firmware/sensor-node/NodeB/NodeB.ino` — the team's own tested firmware, unchanged. `firmware/sensor-node/PINOUT.md` upgraded from a design assumption to confirmed-working now that real hardware uses those exact pins |
| 3 | Wireless Communication | **IMPLEMENTED — real hardware, revised topology** | WiFi, but not the originally-assumed single-network topology: the ESP32-S3 gateway hosts its **own** AP (`SMART_MINE_GATEWAY`) for the two nodes, and separately joins the real backend network as a station (`WIFI_AP_STA`) — see Module 4. The vault's own Module 3 lists LoRa only as "research later" — not adopted |
| 4 | Gateway | **IMPLEMENTED — integration verified, hardware round-trip not yet tested** | `firmware/gateway/Gateway/Gateway.ino` — built on the team's tested AP/buzzer/webserver code, with the missing backend-forward piece added (field conversion, sequencing, NTP timestamping, real `POST /api/v1/readings`). The exact constructed packet was POSTed directly to the live backend and confirmed to return `201` with a real computed decision — the AP+STA dual WiFi mode itself has not been run on the physical board yet |
| 5 | Backend & Data Validation | **IMPLEMENTED** | `apps/api/routes.py`, `apps/api/main.py`; hardened this branch with structured logging, a real `/health` DB check, per-node rate limiting, and new `POST /api/v1/devices/{id}/health` + `GET /api/v1/devices` for device-health telemetry |
| 6 | Database & Evidence Storage | **IMPLEMENTED** | `apps/api/storage.py` — `readings`, `incidents`, `units`, `inspection_updates`, `audit_events` tables, restart-persistence tested |
| 7 | Deterministic Intelligence | **IMPLEMENTED** | `intelligence/` (I-02–I-09) wired via `apps/api/decision.py` — feature extraction, Risk, Confidence, trend, correlation, hysteresis state machine, all with `PROTOTYPE_STATUS`-labeled thresholds. Algorithm/config version now exposed via `GET /api/v1/configuration` (this branch) |
| 8 | Realtime Dashboard | **IMPLEMENTED** | `apps/dashboard/` — React/Vite/Leaflet/Recharts, WebSocket + polling fallback |
| 9 | Mobile / Field Interface | **IMPLEMENTED** | Inspection PWA (`apps/dashboard/src`, `docs/PHONE_SETUP.md`) — installable, offline shell, role-based. Now also reports BLE-anchor relative proximity (`navigator.bluetooth.requestLEScan()`, real hardware, requires the Chrome experimental-features flag and a working anchor — see below); phone-to-phone real GPS was evaluated and rejected (indoor accuracy too poor for a one-room demo) |
| 10 | ML Evidence | **IMPLEMENTED — synthetic training data** | `intelligence/anomaly.py` (I-09), Isolation Forest, held-out calibration split. Trained on a synthetic baseline, not field data — `anomaly_model_trained` now exposed via `/configuration` (this branch) |
| 11 | Agentic AI | **NOT IMPLEMENTED — explicitly deferred** | Requires a local LLM runtime decision, tool-calling infra, none of which exists here. `intelligence/explanation.py` (I-10) already satisfies the vault's core safety rule for this layer — "LLM explains, never decides," deterministic fallback on any failure — without a new agent framework |
| 12 | Local RAG & Citations | **NOT IMPLEMENTED — explicitly deferred** | No indexed document corpus or local LLM runtime available |
| 13 | Incident & Human Workflow | **IMPLEMENTED** | Full incident lifecycle (create → dispatch → acknowledge → resolve), inspection unit lifecycle, `audit_events` |
| 14 | Reliability & Failure Handling | **IMPLEMENTED — for the failure modes tested** | Malformed/duplicate/stale/out-of-order packet handling (409/422), WebSocket disconnect survival, restart/persistence, gateway-auth failure — all covered by the existing 145-test suite. Untested: physical power loss, real network hardware failure |
| 15 | Security & Audit | **IMPLEMENTED — prototype-grade** | Shared-PIN auth (`apps/api/auth.py`), `audit_events`; this branch adds session expiry + logout and structured auth logging. No per-user accounts/password hashing — see "Deferred" below |
| 16 | Environmental / Climate Support | **NOT IMPLEMENTED** | No environmental sensors, no climate testing performed |
| 17 | Experimental Validation | **NOT IMPLEMENTED** | Requires physical hardware and repeatable experiments this session cannot run |
| 18 | Comparison & Efficiency | **NOT IMPLEMENTED** | Depends on Module 17 |
| 19 | Industrialization Research | **NOT IMPLEMENTED — future/field stage** | Requires certification, real field deployment |

## The one number this roadmap deliberately did NOT change

`docs/research/vault/00 MASTER CONTROL/Geo-Sentry Sourced Parameter Register.md`
records `THR-0001 | _None approved_ | blocked` and explicitly rejects using
building-protection blast-vibration PPV limits (mm/s) as a threshold for our MEMS
accelerometer's `vibration_g` (a different physical quantity, sourced for a different
purpose). `intelligence/config.py`'s `PROTOTYPE_SENSOR_THRESHOLDS` therefore remain
exactly as they were — synthetic, demonstration-only, already labeled
`PROTOTYPE_STATUS = "PROTOTYPE / SYNTHETIC / TEST-ONLY"`. This is not an oversight;
it is the register's own conclusion.

## Deferred, not built — and why

| Item | Reason |
|---|---|
| PostgreSQL migration | SQLite is the register's own recommendation for a prototype/single-edge deployment; no benefit for a local demo |
| TLS/HTTPS | No real domain/certificate for a localhost demo |
| Real per-user accounts + password hashing + full RBAC | Current shared-PIN model is the documented, intentional closed-network hackathon design (`docs/PHONE_SETUP.md`); real accounts are a scope change, not a hardening item |
| Native mobile apps | The PWA already satisfies "installable, works on a phone"; a native wrapper adds surface area with no demonstrated need |
| Dynamic node registration | `node_id` is a frozen 2-value enum in `contracts/sensor-reading.schema.json`; changing it is a cross-workstream contract change, not a unilateral one |
| Agentic tool-calling + local LLM + RAG + agent audit trail | Modules 11–12 above — needs a local LLM runtime decision and a real, rights-cleared document corpus |
| Real hardware, field calibration, DGMS-specific thresholds | Modules 1, 17, 19 above — physically impossible without actual sensors and licensed field access |
| Redundant edge servers, load/soak testing, dependency security-scan CI | Production-operations concerns, not applicable to a laptop demo |

## Firmware run instructions (Modules 2 and 4) — updated, real hardware now exists

`NodeA.ino`/`NodeB.ino` are real, team-tested firmware running on physical ESP32 +
MPU6050 + potentiometer nodes — see `firmware/sensor-node/README.md`. The gateway
(`firmware/gateway/README.md`) builds on the team's own tested AP/buzzer code, adding
the backend-forward integration. None of this was flashed from *this* session (no
Bluetooth/USB/board access here, same constraint as the BLE anchor) — the constructed
packet shape was verified directly against the live backend instead (see below), and
the actual AP+STA dual WiFi mode + hardware round-trip is the next thing to confirm on
the real boards. The simulator (`apps/api/routes.py`'s `SCENARIOS`) remains available
as a fallback demo/test path regardless — the project's documented "digital-first
strategy" (`docs/RECOVERY_BACKUP.md`).

**Verified without hardware, directly against the running backend:** POSTed the exact
JSON the new gateway firmware constructs (converted `tilt_x_deg`/`tilt_y_deg`/
`vibration_g`/`displacement_mm`/`health` fields, per-node `sequence`) to
`POST /api/v1/readings` and confirmed `201` with a real computed decision (Risk,
Confidence, state, `gateway_command.buzzer`) both for a high-tilt case (→ `CRITICAL`)
and a low-reading case. This proves the field-conversion logic is correct
independent of whether the physical AP+STA WiFi handshake succeeds on the real board.

## ESP32-S3 device-health warnings (Part A) — status

**Fully implemented and live-verified** (posted synthetic values directly to
`POST /api/v1/devices/{id}/health` and confirmed the dashboard's Device Health tile
renders correctly, including the warning badge). The firmware side
(`temperatureRead()` calling the real internal die-temperature sensor) is written and
reviewed but, like the rest of Modules 2/4, cannot be flash-tested without physical
hardware. Warning threshold is a safety margin against the sourced absolute-max
rating (VAL-MCU-005), never framed as an ambient-temperature measurement — see
`docs/research/vault/00 MASTER CONTROL/Geo-Sentry Sourced Parameter Register.md`.

## BLE-anchor phone proximity (Part B) — status

Backend and dashboard: **fully implemented and live-verified** (posted synthetic RSSI
for both units directly and confirmed the Field Proximity panel's closer-to-anchor
comparison, including its correct expiry after the 35-second freshness window).

What this session verified with real hardware, not just code:

- This dev machine's own Bluetooth adapter **cannot** advertise as a BLE peripheral
  (`BluetoothLEAdvertisementPublisher` test → `ABORTED`, `RADIO_NOT_AVAILABLE`).
- A second, separate Windows laptop **can** — same test script, real result:
  `SUCCESS`.
- `navigator.bluetooth.requestLEScan()` requires manually enabling
  `chrome://flags/#enable-experimental-web-platform-features` in Chrome on each phone.

What still needs checking on the real hardware before a demo (this session cannot do
this itself — no Bluetooth or second-laptop access here):

1. Run `tools/ble_anchor.py` on the second (verified-working) laptop, confirm it
   prints `STARTED`, not `ABORTED`.
2. On both phones, confirm the Chrome flag above is still enabled (it can reset on a
   Chrome update).
3. Open the Inspection PWA as ALPHA and BRAVO, tap "Start proximity scan" on each,
   confirm real RSSI values start appearing in the Field Proximity panel within 30s.
