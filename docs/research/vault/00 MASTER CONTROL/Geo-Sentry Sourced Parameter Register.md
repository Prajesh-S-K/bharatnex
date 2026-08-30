---
title: "Geo-Sentry Sourced Parameter Register"
project: Geo-Sentry
type: parameter-register
status: active
evidence-status: active
created: 2026-08-30
last-reviewed: 2026-08-30
parents:
  - "00 MASTER CONTROL MOC"
tags:
  - "geo-sentry"
  - "parameters"
  - "thresholds"
  - "evidence-control"
---

# Geo-Sentry Sourced Parameter Register

> [!danger] Use rule
> No published value becomes a Geo-Sentry alarm threshold until its purpose, units, measurement method, frequency, site conditions, protected receptor, uncertainty, and approving authority match the deployment.

## Value classes

- **Regulatory/guidance limit:** published for its stated scope
- **Source observation:** reported result, not automatically a design limit
- **Site baseline:** measured distribution at the deployment location
- **Geo-Sentry experiment:** reproducible controlled result
- **Design assumption:** temporary and visibly unvalidated
- **Derived value:** calculation retaining inputs, formula, uncertainty, and provenance

## Registered vibration values

| Value ID | PPV | Unit | Dominant frequency | Applies to | Source | Classification |
|---|---:|---|---|---|---|---|
| VAL-VIB-001 | 5 | mm/s | <8 Hz | non-owner domestic/kuchcha/brick/cement structures | SRC-0005 | regulator guidance |
| VAL-VIB-002 | 10 | mm/s | 8–25 Hz | same as VAL-VIB-001 | SRC-0005 | regulator guidance |
| VAL-VIB-003 | 15 | mm/s | >25 Hz | same as VAL-VIB-001 | SRC-0005 | regulator guidance |
| VAL-VIB-004 | 10 / 20 / 25 | mm/s | <8 / 8–25 / >25 Hz | non-owner industrial buildings | SRC-0005 | regulator guidance |
| VAL-VIB-005 | 2 / 5 / 10 | mm/s | <8 / 8–25 / >25 Hz | historical and sensitive structures | SRC-0005 | regulator guidance |
| VAL-VIB-006 | 10 / 15 / 25 | mm/s | <8 / 8–25 / >25 Hz | owner domestic structures with limited life | SRC-0005 | regulator guidance |
| VAL-VIB-007 | 15 / 25 / 50 | mm/s | <8 / 8–25 / >25 Hz | owner industrial buildings with limited life | SRC-0005 | regulator guidance |

## Values that are not credibly available yet

| Needed value | Status | Why no number is accepted | Required evidence |
|---|---|---|---|
| “Normal vibration for clay” | UNKNOWN | soil name alone does not determine dynamic site response or failure | stratigraphy, stiffness/density, shear-wave velocity, damping, saturation, baseline and geotechnical assessment |
| “Bad vibration for sand” | UNKNOWN | depends on density, confinement, saturation, waveform, duration and failure mode | site investigation and dynamic/field evidence |
| Universal mine-slope vibration alarm | REJECTED AS UNIVERSAL | building-protection PPV limits do not establish slope instability | mine-specific study, deformation/pore-pressure correlation and qualified approval |
| Geo-Sentry accelerometer alarm | UNKNOWN | raw acceleration is not automatically equivalent to PPV | calibration, waveform processing, frequency response and reference-instrument comparison |
| ESP32-S3 die temperature as an ambient-limit proxy | REJECTED AS DIRECT PROXY | die temperature runs hotter than ambient from self-heating (VAL-MCU-006 vs VAL-MCU-004); no characterized offset exists to convert one to the other | on-device thermal characterization comparing die-sensor readings to a reference ambient probe under representative load |

## Threshold approval record

| Threshold ID | Value | Purpose | Source Value IDs | Site/config | Approved by | Validation | Status |
|---|---|---|---|---|---|---|---|
| THR-0001 | _None approved_ | — | — | — | — | — | blocked |

## Environmental electrical source values

| Value ID | Parameter | Value | Unit | Applies to | Source | Use boundary |
|---|---|---:|---|---|---|---|
| VAL-BAT-001 | charge temperature | 0 to 55 | °C | EVE LF105 example cell | SRC-0008 | not selected final pack |
| VAL-BAT-002 | discharge temperature | −20 to 55 | °C | EVE LF105 example cell | SRC-0008 | not selected final pack |
| VAL-BAT-003 | documented low-temperature operation | to −30 | °C | cited Toshiba SCiB example | SRC-0009 | product/test-condition specific |
| VAL-PV-001 | STC cell temperature | 25 | °C | cited MNRE procurement context | SRC-0011 | reference test condition, not field temperature |
| VAL-PV-002 | maximum magnitude power temperature coefficient | 0.50 | %/°C | cited MNRE procurement requirement | SRC-0011 | select exact module using its certified data |
| VAL-MCU-001 | recommended ESP32 supply | 3.3 nominal; exact min/max variant-dependent | V | exact ESP32 chip | SRC-0017 | board/system may be narrower |
| VAL-MCU-002 | ESP32-S3 recommended operating voltage | 3.0 to 3.6 | V | ESP32-S3 (any variant) | SRC-0018 | manufacturer spec |
| VAL-MCU-003 | ESP32-S3 absolute max supply voltage | −0.3 to 3.6 | V | ESP32-S3 (any variant) | SRC-0018 | manufacturer spec |
| VAL-MCU-004 | ESP32-S3 recommended ambient temperature | −40 to 85 | °C | WROOM-1/standard variant (H4 variants: to 105; R8/R16V: to 65) | SRC-0018 | manufacturer spec; confirm exact module variant |
| VAL-MCU-005 | ESP32-S3 absolute max storage temperature | −40 to 105 | °C | ESP32-S3 (any variant) | SRC-0018 | manufacturer spec |
| VAL-MCU-006 | ESP32-S3 internal die-temperature sensor range | −40 to 125 | °C | ESP32-S3 (any variant), ±1–3 °C accuracy depending on sub-range | SRC-0019 | measures silicon temperature, not ambient -- see "not credibly available yet" below |

## Related

- [[Soil and Vibration Thresholds]]
- [[Blast Vibration]]
- [[Vibration Signal Processing]]
- [[Reference Instrument Validation]]
