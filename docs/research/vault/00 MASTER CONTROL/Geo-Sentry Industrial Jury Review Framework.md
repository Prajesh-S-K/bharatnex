---
title: "Geo-Sentry Industrial Jury Review Framework"
project: Geo-Sentry
type: jury-control
status: active
evidence-status: active
created: 2026-08-30
last-reviewed: 2026-08-30
parents:
  - "Geo-Sentry Home"
tags:
  - "geo-sentry"
  - "jury"
  - "hackathon"
  - "evidence-control"
---

# Geo-Sentry Industrial Jury Review Framework

> [!danger] Jury rule
> A compelling demonstration is not proof of safety or field performance. Unsupported claims, hidden assumptions, synthetic-data accuracy, and untraceable numbers are automatic blockers.

## Evidence hierarchy

1. Applicable law, regulator material, and current official guidance
2. Current standards and certification evidence (within access and licensing limits)
3. Peer-reviewed primary research and authoritative government research
4. Manufacturer documentation for component-specific characteristics
5. Reproducible Geo-Sentry controlled experiments with raw data
6. Mine field validation with professional ground truth
7. Estimates and assumptions—allowed only as visibly labelled design inputs
8. Synthetic data—allowed only to test software and workflows

## National-hackathon gate

The official Smart India Hackathon 2024 guidance lists novelty, complexity, clarity/detail, feasibility, practicability, sustainability, scale of impact, user experience, and future-work progression among evaluation criteria (SRC-0001). Geo-Sentry must therefore show evidence under each heading instead of relying on presentation quality.

| Gate | Jury question | Passing evidence | Current status |
|---|---|---|---|
| Problem | Is the need regulator/field supported? | DGMS or equivalent official evidence and scoped user problem | partial |
| Novelty | What is new over named alternatives? | prior-art matrix and bounded differentiator | open |
| Feasibility | Does the end-to-end prototype work? | physical demonstration plus reproducible artifacts | open |
| Practicability | Can mines install, operate, maintain, and trust it? | workflow, site constraints, maintenance and failure tests | open |
| Sustainability | Can it operate economically and environmentally? | measured power, lifecycle, maintenance and cost evidence | open |
| Impact | Who benefits and how much? | defensible baseline and measured outcome | open |
| UX | Can operators act correctly under pressure? | task testing, alarm and offline workflow evidence | open |
| Progression | Is the route from prototype to field legal and credible? | validation, certification, pilot and governance plan | open |

## Automatic rejection conditions

- Claiming prediction accuracy from synthetic data
- Treating a general-purpose sensor as certified or suitable for a hazardous mine without evidence
- Presenting estimated battery life, radio range, accuracy, latency, cost, or scale as measured
- Allowing ML or an LLM to be the sole critical-alert path
- Missing raw-data provenance, calibration, versioning, uncertainty, or failure handling
- Claiming replacement of professional geotechnical judgement or existing mine controls without comparative field evidence

## Review sequence

[[00 MASTER CONTROL MOC]] → physical problem and regulatory need → measurement validity → full-stack evidence integrity → deterministic safety logic → AI permission boundaries → experiments → field comparison → economics and readiness.

## Sources

- SRC-0001 — Smart India Hackathon 2024 official guidance
- SRC-0002 — DGMS Technical Circular 02 of 2020
- SRC-0003 — NIOSH Mine Slope and Subsidence Monitoring Partnership
- SRC-0004 — NIOSH Ground Control Monitoring guide
