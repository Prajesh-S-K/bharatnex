---
title: "Battery Chemistry Comparison"
project: Geo-Sentry
type: research-note
status: partial
evidence-status: partial
created: 2026-08-30
last-reviewed: 2026-08-30
parents:
  - "17 POWER MOC"
tags:
  - "geo-sentry"
  - "battery"
  - "temperature"
  - "selection"
---

# Battery Chemistry Comparison

## Decision: no universal winner

| Candidate | Evidence-supported advantage | Critical limitation | Suitable Geo-Sentry role | Status |
|---|---|---|---|---|
| LFP rechargeable | Example EVE LF105 documentation lists 0–55 °C charge and −20–55 °C discharge for that datasheet revision (SRC-0008) | must not generalize to every LFP cell; hot enclosure and sub-zero charging need control | open-cast solar prototype when exact smaller cell/pack and BMS pass review | candidate |
| LTO rechargeable | Toshiba SCiB documents selected-cell low-temperature operation to −30 °C and ≥20,000 cycles under stated test conditions (SRC-0009) | manufacturer-specific, cost/size/voltage and availability need study | cold/high-cycle build candidate | candidate |
| Li-SOCl₂ primary | Tadiran publishes industrial documentation for long-term harsh-environment primary batteries (SRC-0010) | not rechargeable; pulse capability and passivation require exact-cell/pulse design; replacement waste | ultra-low-duty remote node candidate | research required |
| Ordinary consumer Li-ion pack | high availability | exact pack temperature/safety/quality vary; no mine approval implied | laboratory only unless fully qualified | rejected for industrial claim |
| Lead-acid/VRLA | established technology | mass, temperature, cycle and maintenance must be evaluated for exact use | gateway/backup candidate, not small node default | research required |

## Non-negotiable protections

- Exact cell/pack datasheet and traceable supplier
- BMS/protection against overcharge, over-discharge, overcurrent, short circuit and unsafe temperature where applicable
- Cell and enclosure temperature sensing
- Charge inhibit outside documented limits
- Fuse/current limiting and fault-energy analysis
- Capacity derating from measured load and temperature—not nominal Ah alone
- Transport, fire, disposal, mechanical restraint and service procedure
- Hazardous-area approval for the complete power system where applicable

## Unresolved selection inputs

Actual node energy per measurement/transmission cycle, reporting interval, radio retries, solar resource/shading, autonomy target, internal enclosure temperature, maintenance interval, size, mass, cost and approval route. Until measured, battery capacity is `UNKNOWN`.

## Sources

- SRC-0008 — EVE LF105 product sheet: https://www.adafruit.evebatteryusa.com/linked/lfp105.pdf
- SRC-0009 — Toshiba SCiB official brochure: https://www.toshiba.com/tic/datafiles/brochures/SciB_Brochure.pdf
- SRC-0010 — Tadiran repository: https://tadiranbatteries.de/download-repository/

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
