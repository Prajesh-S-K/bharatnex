# Sensor node pinout — ESP32 DevKit V1 + MPU6050 (GY-521) + linear potentiometer

> **CONFIRMED WORKING on real hardware** — this is the exact pin assignment used by
> the team's own tested `NodeA.ino`/`NodeB.ino` firmware. It started as a documented
> design assumption (per the research vault's value-class taxonomy — no manufacturer
> datasheet/field source was registered for the exact GY-521 breakout or
> potentiometer part), and was never claimed as more certain than that until now.
> No specific breakout part number, tolerance, potentiometer travel-range, or
> displacement-to-voltage calibration curve is registered in the vault yet — the
> pins themselves are confirmed; the precision of what they measure is still an
> open item (see "What is NOT assumed here" below).

## Board

ESP32 DevKit V1 (ESP32-WROOM-32), per `docs/RECOVERY_BACKUP.md`'s frozen physical
prototype spec ("2 × ESP32 DevKit V1 / ESP32-WROOM-32 development boards").

## MPU6050 (GY-521) — tilt + vibration, I2C

| Signal | GPIO | Notes |
|---|---|---|
| SDA | GPIO21 | ESP32 default `Wire` library I2C data pin |
| SCL | GPIO22 | ESP32 default `Wire` library I2C clock pin |
| VCC | 3V3 | GY-521 breakout has an onboard regulator; do not feed 5V directly to the MPU6050 die pins, only to the breakout's own VCC if it accepts 5V — check the specific breakout's silkscreen before wiring |
| GND | GND | |
| AD0 | GND (or 3V3 for the second address) | I2C address `0x68` when AD0 is low, `0x69` when high — this is the MPU-6050's own documented default address selection pin, independent of this vault (the vault has no registered source for it yet; this is common, well-established manufacturer-datasheet information). Tie AD0 low unless a second I2C device on the same bus needs the alternate address |

## Linear potentiometer — displacement proxy

| Signal | GPIO | Notes |
|---|---|---|
| Wiper | GPIO34 | ADC1 channel 6 — an ADC1 (not ADC2) input-only pin, chosen because ADC2 is unusable while WiFi is active on the ESP32 |
| One end | 3V3 | |
| Other end | GND | |

## Status LEDs (green / yellow / red)

| Signal | GPIO |
|---|---|
| Green | GPIO25 |
| Yellow | GPIO26 |
| Red | GPIO27 |

Each LED needs a current-limiting resistor (330Ω–1kΩ typical for a 3.3V GPIO and a
standard 20mA LED) — exact value depends on the specific LED's forward voltage/current,
which is not registered in the vault yet either.

## Node identity

`NODE_A` vs `NODE_B` is set at compile time (`#define NODE_ID` in `NodeA.ino` /
`NodeB.ino` directly — two separate sketches, not a shared config file), not by a
GPIO strap — two physical boards, each flashed once with its own identity, matching
the frozen contract's `node_id` enum (`contracts/sensor-reading.schema.json`).

## What is NOT assumed here

- No specific GY-521 breakout part number, tolerance, or accuracy figure — that
  requires a registered `MANUFACTURER SPEC` entry per
  `docs/research/vault/00 MASTER CONTROL/Geo-Sentry Sourced Parameter Register.md`,
  which does not exist yet.
- No potentiometer travel range, linearity, or displacement-to-voltage calibration
  curve — same gap.
- Wiring this out on a breadboard/board and validating it against a physical unit is
  Module 1 (Physical Sensing) work, not something this design can self-certify.
