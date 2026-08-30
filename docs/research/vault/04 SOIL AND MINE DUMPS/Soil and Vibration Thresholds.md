---
title: "Soil and Vibration Thresholds"
project: Geo-Sentry
type: research-note
status: partial
evidence-status: partial
created: 2026-08-30
last-reviewed: 2026-08-30
parents:
  - "04 SOIL AND MINE DUMPS MOC"
  - "10 VIBRATION AND SEISMIC SENSORS MOC"
tags:
  - "geo-sentry"
  - "soil"
  - "vibration"
  - "thresholds"
---

# Soil and Vibration Thresholds

## Jury answer

There is no credible universal number that Geo-Sentry can label “normal” or “bad” from the words clay, silt, sand, mine spoil, or rock alone.

## Source-supported findings

- USGS reports that seismic-wave amplitudes can increase through soft near-surface soil layers and that site-response models require layer geometry plus dynamic properties such as density, wave velocity, and damping (CLM-0007; SRC-0006).
- USGS identifies surface-material softness and sediment thickness as important local influences on shaking (SRC-0007).
- DGMS blast guidance evaluates potential structural damage using PPV and dominant frequency. Its values apply to named structure categories, not soil-failure classification (CLM-0006; SRC-0005).

## Variables required before a site threshold

- Stratigraphy and layer thickness
- Density, stiffness/shear modulus and shear-wave velocity
- Damping, moisture, saturation, groundwater and pore pressure
- Confining stress, compaction and disturbance
- Vibration source, duration, frequency, repetition and direction
- Distance, propagation path and protected receptor/failure mechanism
- Correlated displacement, tilt, cracking, pore pressure and operational events

## Defensible Geo-Sentry method

1. Record calibrated three-axis waveform data and operational context.
2. Establish baselines by geotechnical zone and operating state; baseline does not mean safe.
3. Separate blast, machinery, handling, electrical and sensor-fault signatures.
4. Apply external compliance limits only to their stated receptor and measurement method.
5. Treat deviation from baseline as evidence requiring correlation, not proof of instability.
6. Approve thresholds only through a mine-specific geotechnical process.

## Verdict

**PARTIAL / NOT THRESHOLD-READY.** The dependency on site properties is supported. Soil-specific normal/danger values remain unknown without site evidence.

## References

- SRC-0005 — DGMS circular compilation containing Technical Circular 7 of 1997
- SRC-0006 — USGS record for *Local site effects and dynamic soil behavior*
- SRC-0007 — USGS *Earthquake Processes and Effects: Ground Shaking*

## Related

- [[Geo-Sentry Sourced Parameter Register]]
- [[Soil Type and Slope Behaviour]]
- [[Vibration as Supplementary Evidence]]
- [[Blast Vibration]]
- [[Pore Water Pressure]]

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
