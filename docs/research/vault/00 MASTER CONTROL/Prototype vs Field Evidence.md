---
title: "Prototype vs Field Evidence"
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

# Prototype vs Field Evidence

| Evidence class | Can demonstrate | Cannot demonstrate by itself |
|---|---|---|
| Synthetic data | Parsing, UI, workflows, algorithm execution, failure handling | Mine-failure prediction accuracy or field reliability |
| Laboratory prototype | Functional behaviour under controlled conditions | Ruggedness, hazardous-area suitability, mine-wide performance |
| Controlled experiment | Performance for the tested setup and conditions | Untested climates, geology, scale, or deployment conditions |
| Mine pilot | Site-specific operational evidence | Broad generalization without replication |
| Field validation with ground truth | Capability within documented scope | Universal safety assurance |

> [!danger] Boundary
> Never promote synthetic, simulated, or estimated values to field evidence. Record limitations and provenance with every result.

## Related

- [[Geo-Sentry Prototype Evidence and Demonstration Checklist]]
- [[Geo-Sentry Experimental Results]]
- [[Geo-Sentry Final Evidence Matrix]]
