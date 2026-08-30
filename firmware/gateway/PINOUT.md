# Gateway pinout — ESP32-S3 DevKit

> **DESIGN ASSUMPTION — not yet physically validated.** Same status as
> `../sensor-node/PINOUT.md`: no gateway hardware exists, nothing here has been
> built or tested.

## Board

ESP32-S3 development board, per `docs/RECOVERY_BACKUP.md`'s frozen physical
prototype spec ("1 × ESP32-S3 development board").

## Buzzer (CRITICAL-state demonstration)

| Signal | GPIO |
|---|---|
| Buzzer (active, via NPN transistor or MOSFET driver — do not drive a buzzer directly off a GPIO beyond its rated current) | GPIO4 |

## Status LED (gateway health)

| Signal | GPIO |
|---|---|
| Heartbeat LED | GPIO2 (the ESP32-S3 DevKit's onboard LED on most common boards — confirm against your specific board's silkscreen, this varies by vendor) |

## Network

Gateway and both sensor nodes join the same local WiFi network (laptop hotspot
or a router on the demo network) — no dedicated point-to-point radio link
(LoRa, ESP-NOW, etc.) is used; see `../../docs/INDUSTRIAL_ROADMAP.md`'s Module 3
entry for why WiFi was kept instead of switching to a different wireless
technology.
