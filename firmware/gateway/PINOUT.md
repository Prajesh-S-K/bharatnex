# Gateway pinout — ESP32-S3 DevKit

> **CONFIRMED WORKING** for the buzzer pin (from the team's own tested `s3.txt`).
> The board itself and its exact silkscreen/onboard-LED pin were not independently
> re-verified here — confirm against your specific ESP32-S3 board if that varies.

## Board

ESP32-S3 development board, per `docs/RECOVERY_BACKUP.md`'s frozen physical
prototype spec ("1 × ESP32-S3 development board").

## Buzzer (CRITICAL-state demonstration)

| Signal | GPIO |
|---|---|
| Buzzer | GPIO8 |

## Network — two separate WiFi roles (AP + STA)

- **AP (unchanged, tested):** the gateway hosts its own fixed network,
  `SMART_MINE_GATEWAY` / `mine12345`, at its default AP IP `192.168.4.1`. Both
  `NodeA.ino` and `NodeB.ino` join this network and POST to
  `http://192.168.4.1/data` — this part requires no configuration and was
  already working before the backend-integration piece was added.
- **STA (new):** the gateway *also* joins the real room/lab WiFi network as a
  station, so it can reach the laptop running the FastAPI backend. This is
  configured in `Gateway/secrets.h` (copy from `secrets.h.example`) — see
  `README.md`.

This is why the gateway needs `WiFi.mode(WIFI_AP_STA)` rather than the simpler
`WIFI_AP` the original tested code used — running both roles at once is what
lets the two fixed-network nodes and the real backend network coexist through
one board.
