---
title: "Geo-Sentry Claim Register"
project: Geo-Sentry
type: control-note
status: active
evidence-status: active
created: 2026-08-30
last-reviewed: 2026-08-30
parents:
  - "00 MASTER CONTROL MOC"
tags:
  - "geo-sentry"
  - "evidence-control"
---

# Geo-Sentry Claim Register

> [!danger] Rule
> Every factual or quantitative claim needs a real registered source or an appropriately designed Geo-Sentry experiment. Synthetic data cannot validate mine-safety performance.

| Claim ID | Claim | Classification | Status | Source IDs | Scope/limitation | Used in |
|---|---|---|---|---|---|---|
| CLM-0001 | SIH 2024 official evaluation criteria included novelty, complexity, clarity/detail, feasibility, practicability, sustainability, scale of impact, user experience, and future-work progression. | fact | source-supported | SRC-0001 | 2024 guidance; current event rules must be rechecked | [[Geo-Sentry Industrial Jury Review Framework]] |
| CLM-0002 | DGMS Circular 02 of 2020 calls for a suitable slope-monitoring system customized to local needs for timely withdrawal from areas likely to be affected by impending slope failure. | fact | source-supported | SRC-0002 | opencast coal and metalliferous mines; quote context must be preserved | [[Indian Mine Ground-Control Context]] |
| CLM-0003 | DGMS Circular 02 of 2020 ties mechanized opencast planning, ultimate pit slope, dump slope, and slope monitoring to a scientific study under the cited Coal Mines Regulations provision. | fact | source-supported | SRC-0002 | legal applicability and later amendments require current professional review | [[Indian Mine Ground-Control Context]] |
| CLM-0004 | NIOSH states that monitoring effectiveness hinges on mine-specific alarm thresholds selected by mine personnel. | fact | source-supported | SRC-0003 | research guidance, not a universal numeric threshold or Indian legal rule | [[Risk Scoring]] |
| CLM-0005 | NIOSH published a 2024 guide covering ground-control instrumentation and data acquisition used by its researchers. | fact | source-supported | SRC-0004 | does not validate Geo-Sentry hardware | [[Mine Monitoring Technology Comparison]] |

| CLM-0006 | DGMS Technical Circular 7 of 1997 specifies permissible blast-induced PPV by structure category and dominant frequency; it does not establish a universal soil-instability threshold. | fact plus bounded interpretation | source-supported | SRC-0005 | blast/structure-protection context | [[Blast Vibration]] |
| CLM-0007 | Dynamic site response depends on subsurface layering and properties; soil name alone cannot establish a universal safe/danger vibration threshold. | fact plus engineering conclusion | source-supported | SRC-0006, SRC-0007 | supports dependency, not a Geo-Sentry alarm number | [[Soil and Vibration Thresholds]] |

| CLM-0008 | The cited EVE LF105 sheet lists charge temperature 0–55 °C and discharge temperature −20–55 °C for that exact cell/revision. | manufacturer specification | source-supported | SRC-0008 | not transferable to all LFP cells or finished packs | [[Battery Chemistry Comparison]] |
| CLM-0009 | Toshiba documents selected SCiB low-temperature use to −30 °C and ≥20,000 cycles under stated test conditions. | manufacturer specification | source-supported | SRC-0009 | exact product/test conditions; not a universal LTO guarantee | [[Battery Chemistry Comparison]] |
| CLM-0010 | The cited MNRE project specification defines PV STC at 25 °C cell temperature and specifies a power temperature coefficient no worse than 0.50%/°C for its procurement. | official procurement fact | source-supported | SRC-0011 | not a universal design value for every module | [[Solar Power]] |
| CLM-0011 | Intrinsic safety is a complete-apparatus/system construction and testing matter; DGMS identifies IS/IEC/EN 60079 family standards in its approval guidance. | standards/regulator fact | source-supported | SRC-0012, SRC-0013 | exact current edition and approval route require confirmation | [[Geo-Sentry Intrinsic Safety Path]] |
| CLM-0012 | Resistor accuracy across temperature depends on TCR and technology; matched networks can improve ratiometric stability. | manufacturer technical fact | source-supported | SRC-0014, SRC-0015, SRC-0016 | exact part/circuit still requires error analysis | [[Resistor Selection and Temperature Derating]] |
| CLM-0013 | ESP32 temperature and supply limits vary by exact chip/module; chip ratings do not qualify the complete Geo-Sentry node. | datasheet fact plus boundary | source-supported | SRC-0017 | exact orderable module and board must be checked | [[Geo-Sentry Environmental Build and Power Matrix]] |
| CLM-0014 | The ESP32-S3 datasheet specifies recommended operating voltage 3.0–3.6 V (absolute max −0.3 to 3.6 V) and recommended ambient temperature −40 to 85 °C for the WROOM-1/standard variant (H4 variants to 105 °C, R8/R16V to 65 °C); absolute max storage temperature is −40 to 105 °C. | manufacturer specification | source-supported | SRC-0018 | exact module variant must be confirmed; these are chip/module limits, not a finished-board or enclosure rating | [[Geo-Sentry Environmental Build and Power Matrix]] |
| CLM-0015 | The ESP32-S3's internal die-temperature sensor measures silicon temperature (not ambient) over −40 to 125 °C with accuracy ±1–3 °C depending on the selected sub-range; Espressif's own docs state it cannot give a precise measurement value. | official technical documentation | source-supported | SRC-0019 | die temperature runs hotter than ambient from self-heating with no characterized offset available; must not be used as an ambient-limit proxy | [[Geo-Sentry Environmental Build and Power Matrix]] |

## Status meanings

- `unverified`: adequate evidence not attached
- `source-supported`: registered source checked for the stated scope
- `experiment-supported`: reproducible controlled result registered
- `field-validated`: genuine field data plus defensible ground truth
- `rejected`: evidence fails to support the claim

## Related

- [[Geo-Sentry Source Register]]
- [[Geo-Sentry Data, Value and Citation Register]]
- [[Prototype vs Field Evidence]]
