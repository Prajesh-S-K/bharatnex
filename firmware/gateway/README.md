# ESP32-S3 gateway firmware

Receives sensor-node packets over the local network at `POST /ingest`,
forwards them unmodified to the FastAPI backend
(`POST /api/v1/readings`), applies the backend's returned `gateway_command`
(drives the buzzer on `CRITICAL`), and acknowledges it
(`POST /api/v1/gateway/ack`). Performs **no** Risk/Confidence/ML calculation
itself — see `apps/api/routes.py`'s `ingest_reading()` for the exact
`gateway_command` shape this firmware parses.

> **Status: written, not run.** Reviewed against the backend's actual
> response shape; never flashed to or tested on physical hardware — none
> exists in this environment. See `PINOUT.md` and
> `../../docs/INDUSTRIAL_ROADMAP.md`.

This is **optional**: `../sensor-node/` already posts directly to the backend
(the documented "direct node-to-API fallback"). Deploy this gateway once
nodes are out of the laptop's own WiFi range but still in range of a closer
relay point, or to centralize the physical buzzer at one location.

## Hardware

ESP32-S3 development board + buzzer (driven through a transistor/MOSFET, not
directly off the GPIO) + status LED. Wiring: see `PINOUT.md`.

## Build and flash (PlatformIO)

1. `cp src/secrets.h.example src/secrets.h`, fill in WiFi credentials, the
   laptop's `API_BASE_URL`, and `GATEWAY_DEVICE_KEY` if the backend has
   `SMART_MINE_GATEWAY_KEY` set (leave empty otherwise — the prototype
   default).
2. `pio run --target upload`, then `pio device monitor` — the serial output
   prints the gateway's local IP once WiFi connects.
3. Point sensor nodes at the gateway instead of the backend directly by
   changing their `API_BASE_URL` (`../sensor-node/src/secrets.h`) to
   `http://<gateway-ip>` and posting to `/ingest` instead of
   `/api/v1/readings` — this requires a small firmware change to
   `../sensor-node/src/main.cpp`'s POST path, not implemented here since no
   deployment has decided it needs the gateway yet (direct-to-API works today).

## Verify against the backend

```bash
curl -X POST http://<gateway-ip>/ingest \
  -H "Content-Type: application/json" \
  -d '{"schema_version":"1.0","node_id":"NODE_A","sequence":1,"timestamp":"2026-08-30T00:00:00Z","sensors":{"tilt_x_deg":0.4,"tilt_y_deg":0.2,"vibration_g":0.06,"displacement_mm":1.0},"health":{"mpu6050_ok":true,"displacement_input_ok":true,"connection_ok":true}}'
```

should forward through to the FastAPI backend and appear in
`GET /api/v1/readings`, same as a direct POST.
