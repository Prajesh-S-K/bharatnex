---
title: "Resistor Selection and Temperature Derating"
project: Geo-Sentry
type: research-note
status: partial
evidence-status: partial
created: 2026-08-30
last-reviewed: 2026-08-30
parents:
  - "17 POWER MOC"
  - "21 CALIBRATION AND SENSOR QUALITY MOC"
tags:
  - "geo-sentry"
  - "resistors"
  - "derating"
  - "temperature"
---

# Resistor Selection and Temperature Derating

## Professional selection rule

There is no single “best resistor” or climate-based resistance value. First determine circuit function and error budget; then select resistance, tolerance, temperature coefficient (TCR), power, voltage, pulse, noise, humidity and stability ratings.

## Provisional component policy

| Function | Preferred technology | Provisional target—not yet a released specification | Verification required |
|---|---|---|---|
| precision sensor/ADC divider | matched thin-film network or precision thin film | ratio tolerance ≤0.1%; low matched TCR suitable for error budget | worst-case ratio error across board temperature and self-heating |
| gain/reference network | matched precision network | select by ratio drift, not only absolute tolerance | amplifier/ADC full error budget |
| pull-up, logic bias | industrial-rated thick/metal film as appropriate | value from interface timing/current; temperature range covers internal enclosure | logic margins and leakage across temperature |
| current limiting/LED | pulse- and power-rated resistor | calculate worst-case current and dissipation | voltage, surge, ambient and enclosure derating |
| shunt/current measurement | dedicated low-TCR current-sense resistor | Kelvin connection where required | power, pulse, TCR and calibration |
| surge/energy limiting for hazardous design | only within certified intrinsic-safety design | no provisional hobby value accepted | fault analysis and certification |

Vishay explains TCR as resistance change relative to the +25 °C value, and its fixed-film guidance distinguishes temperature behaviour by film technology (SRC-0014, SRC-0015). TI notes that matched resistor networks improve ratiometric matching and stability across temperature (SRC-0016). These sources support selection principles, not the provisional numeric design target above.

## Required calculation per resistor

- nominal and worst-case voltage/current
- steady and pulse power
- ambient plus self-heating temperature
- tolerance and TCR contribution across full internal temperature range
- voltage coefficient, long-term drift and humidity where material
- package working voltage, creepage/clearance and contamination
- failure mode and consequence
- calibration contribution and replacement control

## Verdict

**POLICY PARTIAL; VALUES UNSELECTED.** Final resistor values require the actual schematic and sensor-interface requirements.

## Sources

- SRC-0014 — Vishay PSF information: https://www.vishay.com/doc/?30162=
- SRC-0015 — Vishay fixed-film guidance: https://www.vishay.com/docs/20103/geninfo.pdf
- SRC-0016 — TI matched thin-film overview: https://www.ti.com/product-category/passive-discrete/matched-thin-film-resistors/overview.html

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
