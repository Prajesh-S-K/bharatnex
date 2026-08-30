---
title: "Geo-Sentry Environmental Build and Power Matrix"
project: Geo-Sentry
type: engineering-decision
status: partial
evidence-status: partial
created: 2026-08-30
last-reviewed: 2026-08-30
parents:
  - "17 POWER MOC"
  - "18 PHYSICAL BUILD MOC"
tags:
  - "geo-sentry"
  - "power"
  - "climate"
  - "configuration"
---

# Geo-Sentry Environmental Build and Power Matrix

> [!danger] Decision status
> This is a configuration architecture, not a released BOM. A component is acceptable only when its exact orderable part, datasheet revision, derating, certification, and test evidence satisfy the selected deployment class.

| Build class | Environment | Preferred power architecture | Battery position | Component policy | Current verdict |
|---|---|---|---|---|---|
| LAB | supervised indoor prototype | regulated wired DC/USB development supply | optional protected development pack for tests | commercial/dev-grade parts within datasheet limits | suitable for functional prototype only |
| OC-HOT | open-cast, hot, dusty, wet, solar-exposed | solar + charge controller + rechargeable battery + protected regulated rails | LFP is a candidate only inside exact cell charge/discharge limits; enclosure temperature must be measured | industrial-temperature parts, UV/corrosion/water controls, conformal-coating decision | requires thermal and energy experiments |
| OC-COLD | open-cast sub-zero charging risk | solar/wired hybrid with temperature-qualified storage | LTO is a candidate where low-temperature charging is required; Toshiba documents selected SCiB performance to −30 °C under stated conditions | industrial-temperature parts plus heater/no-charge strategy as applicable | candidate, not selected |
| UG-NONGASSY | underground location shown by competent assessment not to require explosive-atmosphere protection | wired low-voltage distribution or replaceable approved pack, decided by site study | ordinary DIY packs still require fire, maintenance and mine approval review | rugged/corrosion/dust/water design | blocked pending mine classification |
| UG-HAZ | underground explosive/hazardous atmosphere | certified intrinsically safe/approved system architecture only | no DIY battery or ordinary development-board pack | exact approved/certified equipment and controlled configuration | BLOCKED—certification path required |

## Why the variables must change

- Battery charge and discharge temperature limits vary by chemistry and exact cell.
- PV output and qualification depend on module temperature and the exact certified module; MNRE material uses 25 °C cell temperature for STC and specifies a power-temperature-coefficient limit for the cited procurement context (SRC-0011).
- MCU chip limits do not prove board, connector, sensor, battery, enclosure, or finished-system temperature suitability.
- Resistor accuracy changes with tolerance, temperature coefficient, self-heating, humidity, voltage and ageing; circuit function determines the allowable error.
- Hazardous-area compliance applies to the complete apparatus/system, not to a battery chemistry label or isolated component. IEC 60079-11 defines construction/testing for intrinsic safety, and DGMS identifies relevant approval standards for electrical items (SRC-0012, SRC-0013).

## Configuration keys

`build_class`, `ambient_min_C`, `ambient_max_C`, `enclosure_internal_max_C`, `solar_available`, `hazardous_area_classification`, `battery_model`, `charge_min_C`, `charge_max_C`, `discharge_min_C`, `discharge_max_C`, `resistor_grade`, `power_derating`, `enclosure_rating`, `approval_ids`.

## Release gate

No build proceeds from prototype to mine pilot until [[Geo-Sentry Environmental Electrical Qualification Checklist]] passes.

## Related

- [[Geo-Sentry Power Architecture]]
- [[Battery Chemistry Comparison]]
- [[Resistor Selection and Temperature Derating]]
- [[Climate Build Matrix]]
- [[Geo-Sentry Intrinsic Safety Path]]
