# Project master specification

Status: **Prototype architecture frozen for v1 integration**  
Last synchronized: **2026-08-29**

## Goal

Demonstrate one complete Smart Automation loop:

> Deform the model → sensors report change → platform detects abnormal behaviour → separate Risk and Confidence change → monitoring escalates → incident is created → dashboard explains why → Alpha or Bravo is assigned.

## Frozen prototype scope

- Two ESP32 DevKit/WROOM-32 sensor nodes: `NODE_A` and `NODE_B`.
- Each node: MPU6050 plus a 10 kΩ potentiometer representing crack/displacement, and green/yellow/red status LEDs.
- One ESP32-S3 Wi-Fi gateway with active buzzer; the API may be reached directly if the gateway blocks early integration.
- Laptop: FastAPI, SQLite, validation, health monitoring, Isolation Forest and decision pipeline.
- Geometry: fixed local XY coordinates and simple GeoJSON. No underground GNSS claim.
- Intelligence: feature extraction, anomaly, trend, geometry, multi-sensor confirmation, neighbour correlation, separate Risk and Confidence, explainability.
- Automation: adaptive logging, supervisory state machine, safety-response recommendation, incident handling, Alpha/Bravo dispatch.
- Dashboard: React + Vite, Leaflet and Recharts.
- Simulator: normal, gradual deformation, rapid deformation, sensor fault, missing packets, neighbour correlation, recovery and dispatch scenarios.

## Explicitly deferred

- LLM involvement in safety-critical scoring or state decisions.
- Exact collapse-time or roof-fall prediction.
- Rover, CNN, mesh networking, industrial sensors and certified deployment hardware.
- Advanced cybersecurity beyond prototype authentication/replay protection basics.
- Gas sensing unless the core end-to-end loop is already stable.

An LLM may later convert deterministic reasons into clearer prose, but it must not calculate Risk, Confidence, or safety state.

## State behaviour

| State | Intended prototype action |
|---|---|
| NORMAL | baseline logging |
| WATCH | increased sampling/reporting |
| WARNING | high-rate monitoring and incident creation |
| CRITICAL | safety recommendation, incident mode, buzzer and inspection dispatch |

Threshold values are provisional and must be recorded in the intelligence configuration, not scattered across services.

## Shared rules

1. `contracts/` is the integration source of truth.
2. All timestamps use UTC ISO 8601 with `Z`.
3. Risk and Confidence are distinct values from 0 to 100.
4. Every decision supplies deterministic reason codes.
5. Missing, duplicate, delayed or invalid packets must not silently become normal readings.
6. Digital simulation comes first; Wokwi and physical devices must use the same payload.

