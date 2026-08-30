# Sensor node pinout — ESP32 DevKit V1 + MPU6050 (GY-521) + linear potentiometer

> **DESIGN ASSUMPTION — not yet physically validated.** Per the research vault's own
> value-class taxonomy (`docs/research/vault/00 MASTER CONTROL/Geo-Sentry Sourced
> Parameter Register.md`), this is a design assumption, not a sourced fact: the vault's
> own `09 TILT SENSOR RESEARCH/MEMS Accelerometer for Tilt.md` and `08 DISPLACEMENT
> SENSOR RESEARCH/Linear Potentiometer.md` pages are both `status: unresearched` —
> no manufacturer datasheet or field source has been registered for either component
> yet. The GPIO assignment below has never been built or tested on physical hardware.

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

`NODE_A` vs `NODE_B` is set at compile time (`NODE_ID` in `src/config.h`), not by a
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
