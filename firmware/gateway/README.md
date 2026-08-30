# ESP32-S3 gateway firmware

**Real, tested foundation + one new integration piece.** The AP hosting, web
server, and buzzer wiring are the team's own tested `s3.txt`, unchanged. What's
new: the gateway now also joins the real backend's WiFi network as a station
(`WIFI_AP_STA`), converts each node's raw reading into the frozen v1 contract
(`contracts/sensor-reading.schema.json`), and actually forwards it to
`POST /api/v1/readings` — the piece that was missing before, since the
original tested code only logged data and buzzed locally, never left its own
isolated network. Also reports its own chip temperature (Part A device-health
telemetry, sourced ESP32-S3 warning margin) every 10s via
`POST /api/v1/devices/ESP32-S3-GATEWAY/health` — NodeA/NodeB do not report this
themselves, since they're untouched.

> **Status:** AP hosting + node reception is tested, working hardware. The
> STA connection, field conversion, and backend forward are new and not yet
> device-tested — but the exact packet shape this firmware constructs **was**
> verified directly against the running backend (see
> `../../docs/INDUSTRIAL_ROADMAP.md`): a `POST /api/v1/readings` with these
> converted fields returns `201` and a real computed Risk/Confidence decision.

## Hardware

ESP32-S3 development board + buzzer on GPIO8 (driven through a transistor/MOSFET,
not directly off the GPIO). Wiring: see `PINOUT.md`.

## Field conversion (what changes between a node's raw POST and the backend)

| Node sends | Backend needs | How it's handled |
|---|---|---|
| `tilt_change` (one combined angle) | `tilt_x_deg` + `tilt_y_deg` | Combined value → `tilt_x_deg`; `tilt_y_deg` is `0` — this hardware doesn't measure independent axes, labeled in code, not hidden |
| `vibration` | `vibration_g` | Direct rename, same units concept |
| `pot_raw` (0–4095) | `displacement_mm` | `(pot_raw / 4095) * 50` — assumed 50mm travel, no real calibration curve yet (same open item as the original design) |
| `mpu_health` (`NodeB.ino` only) | `mpu6050_ok` | `"OK"` → `true`; absent (NodeA.ino doesn't send it) → defaults to `true` rather than guessing a failure |
| *(not sent)* | `sequence` | Gateway keeps its own per-node counter — required because the backend rejects a packet whose sequence isn't newer than the last one it stored |
| *(not sent — no internet on the AP-only network)* | `timestamp` | Gateway syncs its own clock via NTP once its STA link is up; a reading is skipped (not sent with a fake time) if the clock isn't synced yet |
| `state` (node's own local NORMAL/WARNING/CRITICAL) | *(not part of the sensor contract)* | Dropped. The node's own LEDs still use it locally; the backend's real decision comes from `intelligence/`'s Risk/Confidence/trend pipeline independently |

## Build and flash (Arduino IDE)

1. `cp Gateway/secrets.h.example Gateway/secrets.h`, fill in:
   - `STA_WIFI_SSID` / `STA_WIFI_PASSWORD` — the **real** room/lab WiFi network
     the laptop backend is also on (not the gateway's own `SMART_MINE_GATEWAY`
     AP, which stays hardcoded and unchanged).
   - `API_BASE_URL` — the laptop's LAN IP, e.g. `http://172.16.102.249:8000`.
     Find it with `ipconfig` on the laptop (IPv4 Address under the WiFi adapter
     actually on the same network); re-check it if that network changes.
2. Open `Gateway/Gateway.ino` in Arduino IDE (already a proper sketch folder,
   no renaming needed). Select "ESP32S3 Dev Module" as the board.
3. Upload, then open the Serial Monitor at 115200 baud. Expected boot sequence:
   - `Gateway AP started successfully!` and an AP IP (normally `192.168.4.1`)
   - `STA CONNECTED, gateway's own IP on that network: <ip>` — if this instead
     prints `STA WIFI CONNECTION FAILED`, double-check `secrets.h`.
4. Power on NodeA/NodeB (unchanged firmware) — they connect to the gateway's AP
   exactly as before. Each reading now also prints `NODE_A -> backend: 201` (or
   `NODE_B -> ...`) once the gateway successfully forwards it.

## Verify against the backend

Once both boot messages above are confirmed, check on the laptop:

```bash
curl http://localhost:8000/api/v1/readings?node_id=NODE_A
```

should show real readings from the physical node with increasing `sequence`
values, and the dashboard (`http://localhost:5173`) should update in real time
with the actual computed Risk/Confidence/state.

## Known limitations (documented, not hidden)

- No JSON library is used for parsing the node's incoming body or the
  backend's response (manual string search, matching the style already used in
  the original tested `s3.txt`) — deliberately minimal, not a general-purpose
  parser.
- If the STA link drops, `loop()` calls `WiFi.reconnect()` but does not retry
  buffering readings that arrive while disconnected — a node's POST during that
  window gets a `502` from the gateway's own web server (see `handleIngest()`'s
  equivalent path) and that individual reading is lost, not queued.
- `GATEWAY_DEVICE_KEY`/`SMART_MINE_GATEWAY_KEY` gateway-auth was intentionally
  left disabled for this integration (matches the current backend default) —
  see `../../docs/INDUSTRIAL_ROADMAP.md` if that's revisited later.
