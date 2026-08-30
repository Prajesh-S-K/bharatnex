---
title: "Blast Vibration"
project: Geo-Sentry
type: research-note
status: partial
evidence-status: partial
created: 2026-08-30
last-reviewed: 2026-08-30
parents:
  - "06 MINING ACTIVITY MOC"
  - "10 VIBRATION AND SEISMIC SENSORS MOC"
tags:
  - "geo-sentry"
  - "blast"
  - "vibration"
  - "ppv"
---

# Blast Vibration

## Verified Indian guidance values

DGMS Technical Circular 7 of 1997 uses peak particle velocity (PPV) and dominant excitation frequency for protection of specified structure categories. Values below are mm/s.

| Structure category | <8 Hz | 8–25 Hz | >25 Hz | Value IDs |
|---|---:|---:|---:|---|
| Non-owner domestic/kuchcha/brick/cement structures | 5 | 10 | 15 | VAL-VIB-001–003 |
| Non-owner industrial buildings | 10 | 20 | 25 | VAL-VIB-004 |
| Historical and sensitive structures | 2 | 5 | 10 | VAL-VIB-005 |
| Owner domestic structures with limited life | 10 | 15 | 25 | VAL-VIB-006 |
| Owner industrial buildings with limited life | 15 | 25 | 50 | VAL-VIB-007 |

## Applicability boundary

These are not “normal soil vibration” values and do not establish a mine-slope failure threshold. They concern blast-induced vibration and specified structures. Applicability must be confirmed against the official circular, later requirements, the mine plan, and competent professional advice.

## Geo-Sentry measurement requirements

- Calibrated triaxial particle velocity, or a validated derivation from calibrated waveform data
- Dominant frequency and retained waveform
- Coupling, orientation, location and synchronized blast timestamp
- Authorized charge/delay and distance metadata
- Instrument range, frequency response, sample rate and calibration record
- Structure category and ownership classification

## Verdict

**SOURCE-SUPPORTED VALUES / IMPLEMENTATION NOT VALIDATED.** Geo-Sentry cannot claim compliance monitoring until its sensing and processing chain is calibrated against an appropriate reference instrument.

## References

- SRC-0005 — https://www.dgms.gov.in/writereaddata/UploadFile/CIRCULARSNew_19092025.pdf

## Related

- [[Geo-Sentry Sourced Parameter Register]]
- [[Vibration Signal Processing]]
- [[Blast Monitor]]
- [[Reference Instrument Validation]]
- [[Soil and Vibration Thresholds]]

## Industrial jury review

> [!question] Jury position
> This page is **not jury-ready** until every applicable question below has a traceable answer. Silence, intuition, marketing language, and unlabeled assumptions count as failure.

### Problem and necessity

- What exact mine-safety or operational problem does this page address?
- Which official record, field observation, or peer-reviewed study proves the problem exists in the claimed context?
- Who is the user, decision-maker, maintainer, and accountable authority?

### Evidence and reproducibility

- Is every factual or numerical statement linked to a Source ID or Experiment ID?
- Is the source primary, official, peer-reviewed, current enough, and applicable to India and the intended mine type?
- Can an independent reviewer reproduce the measurement, calculation, comparison, or result?
- Are uncertainty, sample size, test conditions, calibration, missing data, negative results, and limitations disclosed?

### Engineering feasibility

- What are the input, output, interface, power, environmental, installation, maintenance, and failure requirements?
- What happens when the sensor, node, network, gateway, database, ML model, LLM, or operator is unavailable?
- What evidence shows the design works at the claimed accuracy, latency, range, lifetime, scale, and climate?

### Safety, regulation, and human control

- Could failure or misuse create a false sense of safety?
- Which DGMS requirement, mine procedure, standard, certification, or professional approval applies?
- Which decisions remain deterministic and which require an authorized human?
- Does the system preserve raw evidence, configuration versions, reason codes, and an audit trail?

### Hackathon evaluation

- What is genuinely novel compared with named alternatives and prior art?
- Is the prototype feasible and practical with the demonstrated resources?
- Is it sustainable, maintainable, usable, and capable of meaningful scale and impact?
- What has been physically demonstrated, and what is only proposed future work?

### Verdict

- **Current verdict:** NOT JURY-READY
- **Blocking evidence:** credible sources and/or controlled validation are incomplete
- **Promotion rule:** change this verdict only after linked entries in [[Geo-Sentry Claim Register]], [[Geo-Sentry Source Register]], and—where applicable—[[Geo-Sentry Experimental Results]] pass review.
