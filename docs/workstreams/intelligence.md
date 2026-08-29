# Workstream 2 — Agentic AI + ML/LLM

## Ownership

`intelligence/`: deterministic analytics, ML inference, decision pipeline, orchestration and explanation formatting.

## Deliverables

- Feature extraction and sensor-health awareness.
- Isolation Forest trained on controlled baseline/synthetic data; its output means anomaly, not collapse prediction.
- Rolling trend/progression analysis.
- Geometry proximity using local XY/GeoJSON.
- Multi-sensor confirmation and Node A/B neighbour correlation.
- Separate Risk and Confidence scores with documented inputs.
- Deterministic reason codes and human-readable explanations.
- NORMAL/WATCH/WARNING/CRITICAL transition logic.
- Adaptive logging command, incident decision and Alpha/Bravo dispatch selection.

## Safety boundary

An LLM may rewrite established reasons for presentation. It must not generate measurements, calculate Risk/Confidence, select the safety state, or issue an unverified safety action.

## First checkpoint

Given contract example packets and fixed geometry, return a deterministic decision object and unit tests for normal and warning scenarios.

