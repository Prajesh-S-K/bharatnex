# SMART-MINE AI / Geo-Sentry

SMART-MINE AI is a digital-first prototype for geometry-aware ground-instability monitoring and early warning. Two ESP32 sensor nodes send tilt, vibration, and simulated displacement readings through an ESP32-S3 gateway. A laptop platform validates and stores the data, evaluates anomaly, trend, spatial context, neighbour correlation, Risk and Confidence, and presents explainable alerts, incidents, and inspection dispatch on a GIS dashboard.

> Prototype scope: early warning and decision support. It does not claim exact collapse prediction, roof-fall prediction, or replacement of certified industrial safety systems.

## Three parallel workstreams

| Workstream | Owns | Start here |
|---|---|---|
| Full Stack | FastAPI, SQLite, REST API, React, Leaflet, Recharts | [Full Stack guide](docs/workstreams/full-stack.md) |
| Agentic AI + ML/LLM | features, Isolation Forest, trend, geometry, correlation, Risk/Confidence, orchestration, explanations | [Intelligence guide](docs/workstreams/intelligence.md) |
| Hardware + IoT | ESP32 nodes, MPU6050, potentiometers, LEDs, ESP32-S3 gateway, Wokwi, communication | [Hardware guide](docs/workstreams/hardware-iot.md) |

All workstreams must follow the versioned files in [`contracts/`](contracts/). Contract changes require review from all three workstreams.

## Prototype flow

```text
ESP32 Node A/B or Simulator
        ↓
ESP32-S3 Gateway (optional bypass during integration)
        ↓
FastAPI validation → SQLite
        ↓
Feature + anomaly + trend + geometry + correlation
        ↓
Risk + Confidence + deterministic explanation
        ↓
NORMAL → WATCH → WARNING → CRITICAL
        ↓
Adaptive monitoring + incident + Alpha/Bravo dispatch
        ↓
React dashboard: Leaflet map + Recharts
```

## Repository map

```text
apps/api/                 Full Stack: backend and database
apps/dashboard/           Full Stack: command dashboard
intelligence/             Agentic AI + ML/LLM modules
firmware/sensor-node/     Hardware: shared Node A/B firmware
firmware/gateway/         Hardware: ESP32-S3 gateway firmware
firmware/wokwi/           Hardware: digital circuit projects
simulator/                Contract-compatible scenarios and fallback
contracts/                Shared schemas and examples (integration boundary)
data/                     GeoJSON and safe sample data
docs/                     Architecture, roles, workflow, testing
scripts/                  Cross-project helper scripts
```

## Start working

1. For complete restoration or handoff, read [`docs/RECOVERY_BACKUP.md`](docs/RECOVERY_BACKUP.md).
2. Read [`docs/PROJECT_MASTER.md`](docs/PROJECT_MASTER.md).
3. Read your workstream guide and [`CONTRIBUTING.md`](CONTRIBUTING.md).
4. Build against `contracts/sensor-reading.schema.json`—never invent different field names.
5. Use a feature branch such as `fullstack/ingestion`, `ai/risk-engine`, or `iot/node-a`.
6. Integrate through examples and tests before connecting physical hardware.

The concise current continuation point is maintained in [`docs/CURRENT_HANDOFF.md`](docs/CURRENT_HANDOFF.md). Update both recovery files before every material commit or handoff.

All contributors must follow [`docs/CODING_STANDARDS.md`](docs/CODING_STANDARDS.md). GitHub automatically checks Python style/formatting, shared contracts, tests, whitespace and common credential assignments.

For the team's lightweight, chat-guided operating process, use [`docs/MANUAL_CHAT_WORKFLOW.md`](docs/MANUAL_CHAT_WORKFLOW.md). It keeps Git and review simple while preserving contracts, tests and recovery backups.

The first shared milestone is: **simulator → API → SQLite → reading visible**.
