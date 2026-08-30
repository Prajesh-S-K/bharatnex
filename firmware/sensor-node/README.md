# ESP32 sensor-node firmware

**Status: real, tested, working hardware.** `NodeA.ino` and `NodeB.ino` are the
team's own firmware, confirmed running on physical boards. They do **not** talk to
the FastAPI backend directly — each connects to the ESP32-S3 gateway's own WiFi
network (`SMART_MINE_GATEWAY`) and POSTs its readings to `http://192.168.4.1/data`.
The gateway (`../gateway/`) is what actually reaches the backend — see its README
for the integration piece that was added on top of this tested node code.

## Hardware

- ESP32 DevKit V1 (per-node board)
- MPU6050 (GY-521 breakout), I2C on GPIO21 (SDA) / GPIO22 (SCL), address `0x68`
- One linear potentiometer on GPIO34 (ADC)
- 3 status LEDs: blue/yellow/red on GPIO25/26/27

Wiring: see `PINOUT.md` — confirmed working, not a design assumption anymore.

## What each node actually does

- Reads tilt (one combined tilt-from-vertical angle, not separate X/Y axes) and
  vibration (magnitude deviation from the previous reading) from the MPU6050.
- Reads displacement from the potentiometer, mapped to 0–100.
- Runs its own simple local NORMAL/WARNING/CRITICAL threshold check purely to
  drive its own LEDs — this is a local visual aid only. **It is not the system's
  safety decision** — the backend's real Risk/Confidence/trend pipeline
  (`intelligence/`) makes that determination independently once the gateway
  forwards the reading; the two can legitimately disagree in the short term
  (e.g. hysteresis keeping the backend at a prior CRITICAL state a moment
  longer than a node's own instantaneous local read).
- POSTs its own field names/shape (`node_id`, `tilt_change`, `vibration`,
  `pot_raw`, `displacement`, `state`, and — `NodeB.ino` only — `mpu_health`) to
  the gateway. These are **not** the frozen `contracts/sensor-reading.schema.json`
  shape; the gateway converts them (see `../gateway/README.md`).

## Build and flash (Arduino IDE)

1. Install the `esp32` board package (Espressif) via Boards Manager, if not
   already installed.
2. Open `NodeA/NodeA.ino` (or `NodeB/NodeB.ino`) directly — each is already a
   proper Arduino sketch folder (folder name matches the `.ino` file name), no
   renaming needed.
3. WiFi credentials (`SMART_MINE_GATEWAY` / `mine12345`) are hardcoded in the
   file already — this is the gateway's own fixed AP, unrelated to whatever
   real network the gateway also joins to reach the backend. Nothing to
   configure here unless you change the gateway's AP credentials too.
4. Select "ESP32 Dev Module" as the board, select the correct COM port, upload.
5. Open the Serial Monitor at 115200 baud. On boot it calibrates (keep the node
   still for ~3 seconds), then prints `NODE A CONNECTED TO S3` /
   `NODE A WIFI CONNECTION FAILED` — confirm this before expecting any data to
   reach the backend.

## Verifying data reaches the backend

This node firmware only talks to the gateway, not the backend directly — verify
at the gateway level (its Serial Monitor prints `NODE_A -> backend: 201` per
reading) and then on the laptop:

```bash
curl http://localhost:8000/api/v1/readings?node_id=NODE_A
```

The exact packet shape the gateway constructs from this node's readings was
verified directly against the running backend (see
`../../docs/INDUSTRIAL_ROADMAP.md`) — a real `POST /api/v1/readings` with the
converted fields returns `201` and a real computed decision, before any hardware
round-trip was attempted.

## Known limitations (documented, not hidden)

- Only one combined tilt-from-vertical angle is measured, not independent X/Y
  axis tilts — see `../gateway/README.md`'s field-mapping table for how this is
  handled at conversion time.
- `displacement` is a raw 0–100 mapping of the potentiometer's ADC range, with
  no real calibration curve — same open item as before, now converted to mm at
  the gateway using the same assumed 50mm travel.
- `NodeA.ino` does not send `mpu_health` (only `NodeB.ino` does) — the gateway
  defaults `mpu6050_ok=true` for NODE_A when the field is absent, rather than
  guessing a failure. Adding the same field to `NodeA.ino` would close this gap
  if wanted later.
- Each node's own NORMAL/WARNING/CRITICAL/LED logic uses its own fixed
  thresholds, independent of `intelligence/config.py`'s centrally documented
  (and equally synthetic/unvalidated) thresholds — the two are not the same
  numbers and were never meant to be reconciled; only the backend's decision is
  the system's official one.
