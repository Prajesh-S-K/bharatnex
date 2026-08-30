---
title: "Geo-Sentry Prototype Evidence and Demonstration Checklist"
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

# Geo-Sentry Prototype Evidence and Demonstration Checklist

## Evidence controls

- [ ] All claims have Claim IDs and registered sources or experiments
- [ ] Estimates, assumptions, and synthetic data are visibly labelled
- [ ] Raw measurements are preserved separately from derived results
- [ ] Configuration, firmware, algorithm, and model versions are recorded
- [ ] Limitations, uncertainty, missing data, and failures are disclosed

## End-to-end demonstration

- [ ] Physical sensor measurement
- [ ] Node validation, timestamp, sequence number, buffering
- [ ] Wireless transmission and gateway ingestion
- [ ] Backend validation and durable raw storage
- [ ] Deterministic risk, confidence, trend, state, and reason codes
- [ ] Realtime dashboard and mobile/offline behaviour
- [ ] Incident acknowledgement and inspection workflow
- [ ] Agent investigation uses read-only evidence tools and cited RAG
- [ ] Core alerting remains operational with ML, LLM, or internet unavailable
- [ ] Audit trail reconstructs data, decision, configuration, agent, and human action

## Validation gates

- [ ] Laboratory validation complete
- [ ] Network and power experiments complete
- [ ] Failure injection and recovery tests complete
- [ ] Climate/environment tests complete
- [ ] Mine pilot and professional ground-truth comparison complete
- [ ] Industrial and hazardous-area requirements reviewed by qualified parties

## Related

- [[Geo-Sentry Prototype Module Priority Plan]]
- [[Prototype vs Field Evidence]]
- [[Geo-Sentry Final Evidence Matrix]]
