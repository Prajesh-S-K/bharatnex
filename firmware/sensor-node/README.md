# ESP32 sensor-node firmware

One codebase supports Node A and Node B through a compile-time `NODE_ID`
(`src/config.h`). Reads the MPU6050 (tilt + vibration) and a linear
potentiometer (displacement proxy), reports health, and emits the frozen v1
sensor-reading contract (`contracts/sensor-reading.schema.json`) directly to
the FastAPI backend over WiFi.

> **Status: written, not run.** This firmware has been reviewed against the
> frozen contract but never flashed to or tested on physical hardware --
> none exists in this environment. See `PINOUT.md` for exactly which parts
> of the wiring are a sourced fact versus a labeled design assumption, and
> `../../docs/INDUSTRIAL_ROADMAP.md` for this module's tracked status.

## Hardware

- ESP32 DevKit V1 (ESP32-WROOM-32)
- MPU6050 (GY-521 breakout)
- One linear potentiometer (10kΩ, per `docs/RECOVERY_BACKUP.md`'s frozen prototype spec)
- 3 status LEDs (green/yellow/red) + current-limiting resistors

Wiring: see `PINOUT.md`.

## Build and flash (PlatformIO)

1. Install [PlatformIO](https://platformio.org/) (VS Code extension or CLI).
2. `cp src/secrets.h.example src/secrets.h` and fill in your WiFi SSID/password
   and the laptop's `API_BASE_URL` (e.g. `http://192.168.1.50:8000`) — this
   file is gitignored, never commit it.
3. Set `NODE_ID` in `src/config.h` to `"NODE_A"` or `"NODE_B"` for this
   specific board.
4. Connect the board over USB, then:
   ```bash
   pio run --target upload
   pio device monitor
   ```
5. The serial monitor prints `POST /api/v1/readings -> <status>` each
   reporting cycle (`REPORT_INTERVAL_MS` in `config.h`, default 2000ms) once
   WiFi connects and the clock syncs via NTP.

## Build and flash (Arduino IDE, alternative)

1. Install the `esp32` board package (Espressif) via Boards Manager.
2. Open `src/main.cpp` in a sketch folder named `main` (Arduino IDE expects
   the `.ino`/main file to match its containing folder name — rename the
   folder or copy the files accordingly).
3. Same `secrets.h` and `config.h` setup as above.
4. Select "ESP32 Dev Module" as the board, select the correct COM port, upload.

## Verify against the backend

Once flashed and reporting, confirm on the laptop:

```bash
curl http://<laptop-ip>:8000/api/v1/readings
```

should show this node's readings appearing with increasing `sequence` values.
The dashboard (`http://<laptop-ip>:5173`) should show the node's Risk/Confidence
update in real time — this is the same ingestion path the software simulator
already exercises (`apps/api/routes.py`'s `SCENARIOS`), so no backend changes
are needed for a real node to work once physically wired.

## Known limitations (documented, not hidden)

- `displacement_mm` uses an assumed 0–50mm potentiometer travel range with no
  real calibration curve (see `PINOUT.md`) — Module 1 (Physical Sensing) work.
- `vibration_g` is a simple magnitude-deviation-from-1g heuristic, not
  validated signal processing (`docs/research/vault/10 VIBRATION AND SEISMIC
  SENSORS/Vibration Signal Processing.md` describes what real processing
  would need).
- `sequence` resets to 0 on every reboot (in-memory only) — the backend
  already handles this correctly (a lower sequence than previously seen is
  rejected as stale, not silently accepted; see
  `tests/test_storage_sequence_ordering.py`), but a reboot means a gap in
  this node's accepted sequence range, not data loss.
- Timestamp requires NTP (internet access on the local network at boot). An
  offline deployment needs a different clock source — not implemented here.
