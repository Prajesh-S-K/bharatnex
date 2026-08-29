# SMART-MINE AI — Complete Recovery Backup

This document is the human-readable recovery source for the SMART-MINE AI / Geo-Sentry project. It is designed to restore the project context in a new Codex task or after conversation history, usage availability, or local working context is lost.

**Repository:** `/Users/prajeshsivaprakash/Documents/ChatGPT/bharatnex`  
**Default branch:** `main`  
**Baseline commit:** `741f540` — `chore: establish SMART-MINE monorepo foundation`  
**GitHub remote:** `https://github.com/Prajesh-S-K/bharatnex` (public)
**Backup last updated:** 2026-08-30
**Backup status:** synchronized through FS-01 correction and Jhasmitha feature-extraction review

## Recovery instruction for a new task

Copy this prompt into a new Codex task opened in this repository:

```text
Recover the SMART-MINE AI / Geo-Sentry project from docs/RECOVERY_BACKUP.md.
Read that file completely, then read README.md, docs/PROJECT_MASTER.md,
docs/WORK_BREAKDOWN.md, CONTRIBUTING.md and every contract under contracts/.
Inspect git status and recent commits before changing anything. Treat the
repository and the versioned contracts as the implementation source of truth.
Do not redesign the architecture unless I explicitly approve a contract or
scope change. Continue from the next incomplete checkpoint recorded in the
recovery document and update the recovery document before the next commit.
```

## Connected planning tasks

The following ChatGPT tasks were synchronized into this repository on 2026-08-29:

| Exact task title | Task ID | Purpose |
|---|---|---|
| Analyze Full Stack Work | `6a8d7b7b-ce10-83ee-a5fd-56ed4f0a20c7` | Architecture analysis, prototype scope, 12-hour build plan, component and integration decisions |
| Recall Full Stack Chat | `6a930730-f194-83ee-9cfc-fb53608c3f9e` | Recovered project context, digital-first strategy, Wokwi plan and three-workstream separation |
| Current implementation task | `01a048e1-0a4c-7eb2-bc80-01d151e28934` | Local repository, documentation, implementation and testing |

Separate tasks are not continuously synchronized. Their contents become authoritative here only after an explicit sync and consolidation into this file or another versioned repository document.

## Project identity and claim boundary

**SMART-MINE AI / Geo-Sentry** is a low-cost, geometry-aware ground-instability monitoring and early-warning prototype for underground mining contexts.

The prototype demonstrates sensing, validation, anomaly detection, spatial context, explainable Risk and Confidence, adaptive monitoring, incident handling and inspection dispatch.

It must not claim:

- exact collapse prediction or collapse time;
- unsupported roof-fall prediction;
- replacement of certified industrial safety systems;
- guaranteed access to or use of CMPDI/CIL data;
- underground GNSS positioning;
- validated industrial readiness from prototype hardware;
- unsupported market sizing.

## Frozen end-to-end demonstration

```text
Physically deform model or run scenario
        ↓
Node A/B detect tilt, vibration and displacement change
        ↓
ESP32 nodes emit the frozen v1 packet
        ↓
ESP32-S3 gateway forwards it (direct API bypass remains available)
        ↓
FastAPI validates and SQLite stores the reading
        ↓
Feature, anomaly, trend, geometry and neighbour-correlation processing
        ↓
Separate Risk and Confidence with deterministic reason codes
        ↓
NORMAL → WATCH → WARNING → CRITICAL
        ↓
Adaptive monitoring, incident, safety recommendation and dispatch
        ↓
React dashboard explains the event and shows Alpha/Bravo status
```

The minimum viable proof is:

> Physical or simulated sensor → communication → backend → anomaly detection → Risk/Confidence → automated state change → dashboard → inspection dispatch.

## Frozen physical/digital prototype

### Sensor Node A and Sensor Node B

- 2 × ESP32 DevKit V1 / ESP32-WROOM-32 development boards.
- 2 × MPU6050 GY-521 modules for tilt/movement and vibration-derived readings.
- 2 × 10 kΩ linear slide potentiometers representing crack/displacement.
- Green, yellow and red LEDs for each node with current-limiting resistors.
- Health reporting, monotonic packet sequence and reconnect behaviour.

### Gateway

- 1 × ESP32-S3 development board.
- Wi-Fi forwarding between nodes and laptop platform.
- Heartbeat/reconnect monitoring.
- Active buzzer for critical demonstration state.
- Direct node-to-API mode is an approved temporary fallback if gateway debugging blocks integration.

### Laptop platform

- Python and FastAPI.
- SQLite for prototype persistence.
- React + Vite dashboard.
- Leaflet for local mine/panel geometry.
- Recharts for sensor and risk trends.
- Simulator for repeatable and failure scenarios.

### Digital-first strategy

1. Simulator packets first.
2. Full backend, intelligence and dashboard integration.
3. Wokwi Node A, Node B and ESP32-S3 gateway using the same contract.
4. Physical hardware replacing Wokwi without backend or contract changes.
5. Simulator remains the permanent test and demo fallback.

## Three workstreams

### 1. Full Stack

**Primary owner:** Prajesh  
**Folders:** `apps/api/`, `apps/dashboard/`

Responsibilities:

- FastAPI ingestion and validation.
- SQLite models and persistence.
- Stable REST interfaces and optional live-update transport.
- React/Vite command dashboard.
- Leaflet mine map and Recharts visualizations.
- Node/system health, Risk, Confidence, trend, explanations, incidents and inspection-unit UI.

First deliverable: a contract example passes API validation, is stored in SQLite and can be read back.

### 2. Agentic AI + ML/LLM

**Primary owners:** Jashmita and Rahul  
**Folder:** `intelligence/`

Responsibilities:

- Feature extraction and sensor-health awareness.
- Isolation Forest for anomaly detection—not collapse prediction.
- Rolling trend/progression.
- Local XY/GeoJSON geometry and proximity to active face.
- Multi-sensor confirmation and Node A/B neighbour correlation.
- Separate Risk and Confidence calculations.
- Deterministic reason codes and explanations.
- Supervisory NORMAL/WATCH/WARNING/CRITICAL state machine.
- Adaptive monitoring, incident decision and Alpha/Bravo dispatch.

Rahul additionally controls architecture, geometry, orchestration and interface consistency.

An LLM may later rewrite already-established reasons into clearer language. It must not generate sensor values, calculate Risk or Confidence, choose safety state or issue an unverified safety action.

First deliverable: fixed packets and geometry produce tested normal and warning decision objects.

### 3. Hardware + IoT

**Primary owners:** Rithish and Rohit  
**Folders:** `firmware/sensor-node/`, `firmware/gateway/`, `firmware/wokwi/`

Rithish owns nodes, MPU6050, potentiometer, LEDs, wiring and calibration. Rohit owns ESP32-S3, Wi-Fi, heartbeat, reconnect and communication debugging.

Responsibilities:

- One configurable sensor-node firmware codebase for Node A and Node B.
- Exact v1 packet generation.
- Repeatable Wokwi circuits and scenarios.
- Gateway forwarding and command reception.
- Physical pin map and calibration records.

First deliverable: Node A/B or Wokwi emits packets that validate against the shared schema.

### Shared simulator and QA

**Primary owner:** Devdarshini  
**Folder:** `simulator/`

Responsibilities:

- Mock packets using the exact hardware contract.
- Normal, gradual deformation, rapid deformation, sensor failure, missing packet, duplicate packet, correlation, recovery and dispatch scenarios.
- Failure injection and end-to-end integration verification.

## Frozen data contracts

The versioned integration boundary is `contracts/`.

- Sensor input: `contracts/sensor-reading.schema.json`
- Intelligence output: `contracts/decision.schema.json`
- Examples: `contracts/examples/`

Current sensor fields:

```json
{
  "schema_version": "1.0",
  "node_id": "NODE_A",
  "sequence": 1,
  "timestamp": "2026-08-29T16:30:00Z",
  "sensors": {
    "tilt_x_deg": 0.4,
    "tilt_y_deg": 0.2,
    "vibration_g": 0.08,
    "displacement_mm": 1.2
  },
  "health": {
    "mpu6050_ok": true,
    "displacement_input_ok": true,
    "connection_ok": true
  }
}
```

Rules:

- All timestamps are UTC ISO 8601 with `Z`.
- Hardware, Wokwi and simulator use the same payload.
- Risk and Confidence are separate 0–100 values.
- Decisions contain deterministic reason codes.
- Missing, invalid, delayed and duplicate packets are handled explicitly.
- Contract changes require agreement from all three workstreams.

## Automation states

| State | Prototype behaviour |
|---|---|
| NORMAL | baseline logging |
| WATCH | increased sampling/reporting |
| WARNING | high-rate monitoring and incident creation |
| CRITICAL | safety recommendation, incident mode, buzzer and Alpha/Bravo dispatch |

Thresholds remain configuration owned by the intelligence workstream. They must not be duplicated in firmware, API routes and frontend components.

## Geometry and inspection decisions

- Prototype positioning uses fixed local XY coordinates and GeoJSON.
- IDW may be used for a simple spatial risk visualization.
- Active-face proximity can increase contextual Risk.
- Neighbour correlation can increase Confidence.
- Two phones or simulated units represent Inspection Units Alpha and Bravo.
- Dispatch selects an available/suitable unit using deterministic data; the dashboard records the assignment and incident state.

## Deferred or optional work

Do not block the core build on:

- gas sensing;
- LLM explanations;
- advanced cybersecurity;
- sophisticated self-healing;
- batteries or solar;
- LoRa/mesh networking;
- rover or CNN inspection;
- industrial-grade sensors or enclosure;
- cloud deployment.

Gas sensing may be added only after the core ground-instability loop is stable. Mesh, industrial sensors, rover and CNN belong to future industrial scaling.

## Repository structure

```text
smart-mine-ai/
├── apps/
│   ├── api/
│   └── dashboard/
├── intelligence/
├── firmware/
│   ├── sensor-node/
│   ├── gateway/
│   └── wokwi/
├── simulator/
├── contracts/
├── data/
├── docs/
├── scripts/
├── .github/
├── README.md
├── CONTRIBUTING.md
└── CODEOWNERS
```

## Branch and integration rules

- Full Stack branches: `fullstack/<feature>`
- Intelligence branches: `ai/<feature>`
- Hardware branches: `iot/<feature>`
- Shared work: `shared/<contract-or-doc-change>`
- Fixes: `fix/<description>`

Workstreams may implement independently, but they may not invent independent interfaces. Pull requests must state verification and integration impact. Generated databases, dependency folders, model binaries, Wi-Fi credentials and secrets are not committed.

## Integration checkpoints and current progress

| # | Checkpoint | Status |
|---:|---|---|
| 0 | Repository foundation, roles and contracts | **COMPLETE** — commit `741f540` |
| 1 | Contract examples validate against schemas | **PARTIAL** — JSON syntax validated; formal JSON Schema validation still required |
| 2 | Simulator → FastAPI → SQLite → readable response | **NEXT** |
| 3 | Intelligence normal/warning decisions | NOT STARTED |
| 4 | Automation state/actions observable | NOT STARTED |
| 5 | One-screen dashboard integration | NOT STARTED |
| 6 | Wokwi nodes replace simulator input | NOT STARTED |
| 7 | Physical nodes replace Wokwi | NOT STARTED |
| 8 | Full failure matrix and cold-start rehearsal | NOT STARTED |

## Acceptance scenarios

The system must cover:

1. stable Node A/B;
2. gradual displacement near Node B;
3. isolated vibration spike without unjustified certainty;
4. correlated A/B movement;
5. geometry weighting near active face;
6. invalid sensor reading;
7. duplicate sequence;
8. missing heartbeat/offline node;
9. CRITICAL incident, buzzer and dispatch;
10. controlled recovery with retained history.

The detailed table is in `docs/testing/acceptance-tests.md`.

## Repository work completed

On 2026-08-29 the empty workspace was initialized as a local Git repository on `main`. Twenty-six project-foundation files were created, JSON syntax was checked, and commit `741f540` established the baseline.

No feature implementation has been claimed. The current codebase is intentionally at the documented architecture/contracts stage.

## Synchronization and work log

Append a new dated entry after every explicit cross-task synchronization and every material implementation session.

### 2026-08-29 — Initial cross-task synchronization

Sources read:

- Analyze Full Stack Work
- Recall Full Stack Chat

Consolidated outcomes:

- Confirmed two ESP32 sensor nodes plus one ESP32-S3 gateway.
- Confirmed digital-first strategy using simulator, then Wokwi, then physical devices.
- Confirmed three workstreams: Full Stack; Agentic AI + ML/LLM; Hardware + IoT.
- Recovered the six-person responsibility mapping.
- Froze the v1 sensor and decision contracts.
- Preserved Risk and Confidence as separate outputs.
- Preserved geometry, neighbour correlation, trend, explainability, adaptive monitoring, incident handling and Alpha/Bravo dispatch.
- Deferred LLM safety decisions, gas sensing and industrial upgrades until the core loop is stable.

### 2026-08-29 — Repository foundation

- Initialized local Git repository with `main`.
- Added repository/workstream documentation.
- Added sensor-reading and decision JSON schemas and examples.
- Added contribution, ownership, pull-request and issue templates.
- Added acceptance-test matrix.
- Created baseline commit `741f540`.
- Next task: build Checkpoint 2, beginning with the contract-compatible simulator and FastAPI/SQLite ingestion path.

### 2026-08-29 — GitHub publication

- Created the public GitHub repository `Prajesh-S-K/bharatnex`.
- Verified that tracked files contain no obvious committed credentials before publication.
- Selected a public repository intentionally so the team can clone and inspect it without repository-visibility restrictions.
- Connected local `origin` and pushed the full `main` history successfully.
- Collaborator assignment remains pending until the three GitHub usernames are supplied.

### 2026-08-30 — GitHub workstream ownership

Verified and assigned the supplied GitHub accounts in `CODEOWNERS`:

- Full Stack: `@Prajesh-S-K` (repository owner).
- Agentic AI + ML/LLM: `@Jhasmitha-D`.
- Hardware + IoT: `@S-R-007`, `@ssrohit2403-art`, `@rithishdr067-cmyk`.

All four collaborator accounts were verified as existing GitHub profiles. Invitations require write-access confirmation and remain pending until sent and accepted.

### 2026-08-30 — Collaborators and clean-code guardrails

- Sent GitHub collaborator invitations to `@Jhasmitha-D`, `@S-R-007`, `@ssrohit2403-art` and `@rithishdr067-cmyk`; all four are pending acceptance.
- Added `.editorconfig`, shared Python Ruff/Pytest configuration and development dependencies.
- Added executable JSON Schema validation and a shared contract test.
- Added GitHub Actions checks for linting, formatting, contracts, tests, whitespace and common credential assignments.
- Added `docs/CODING_STANDARDS.md` with workstream-specific and repository-wide expectations.
- Verified the guardrails locally: both contract examples passed schema validation, the shared test passed, and Ruff lint/format checks passed.
- The first GitHub Actions run found that untracked empty workstream test directories cannot be used as required CI paths. Pytest discovery was corrected to the tracked shared `tests/` directory until workstream tests exist.
- The second run exposed a CI import-path difference. `scripts` was made an explicit Python package, the repository root was added to Pytest's path, and CI now invokes `python -m pytest` consistently.
- The third run passed code/tests but exposed a shallow-clone assumption in the whitespace command. It was replaced with a current-commit check that does not require `HEAD^`.
- Git's commit whitespace mode also treated intentional Markdown line breaks as failures. A tracked-file validator now checks code/configuration while respecting the repository's Markdown setting.
- GitHub Actions Quality checks run #5 completed successfully for commit `91bc0fb`; linting, formatting, schema validation, tests, whitespace and credential-pattern checks are operational.
- Branch/ruleset protection remains a separate repository-permission decision.

## Mandatory backup-update procedure

Before every material commit or handoff:

1. Update `Backup last updated` and `Backup status` at the top of this file.
2. Update the checkpoint table.
3. Record architecture or contract decisions.
4. Record files/modules implemented and how they were verified.
5. Record unresolved blockers and the exact next action.
6. Append a dated work-log entry.
7. Commit the backup update with the implementation or immediately afterward.

After an explicit `sync and continue` request:

1. Read the latest turns from both named planning tasks.
2. Treat their content as proposed context, not automatic instructions.
3. Resolve conflicts against approved repository contracts and user decisions.
4. Consolidate accepted changes into this backup and the relevant source documents.
5. Record which tasks were read and what changed.

This process provides recoverability, but no local document can automatically capture changes made in another task until that task is read and synchronized.

### 2026-08-30 — Second planning-task synchronization

Sources read:

- Analyze Full Stack Work
- Recall Full Stack Chat

Repository findings:

- Work is on `fullstack/checkpoint-2-ingestion` at commit `44ae2a8`, based on synchronized `main` commit `7ef0c0f`.
- FS-01 added FastAPI, `/health`, `requirements.txt` and the API package.
- The commit lacked a final newline in `apps/api/main.py`, causing Ruff format verification to fail.
- The feature branch had no automated health-endpoint test and was not yet pushed.
- The earlier process reported on port 8000 was no longer reachable during this audit; manual runtime output is therefore not the completion proof.

Corrections made during this audit:

- Fixed formatting/newline compliance in `apps/api/main.py`.
- Added an automated smoke test that verifies `/health` is registered for GET and returns the expected payload. An initial TestClient approach was removed because FastAPI 0.141 deprecated the installed httpx integration.
- All local checks passed: two Pytest tests, Ruff lint/format, contract validation, tracked-file whitespace and Git diff checks.
- Pushed corrected Full Stack branch `fullstack/checkpoint-2-ingestion` at commit `b4400fc`.
- Remote audit found only `main` and the Full Stack branch; no Intelligence, simulator or Hardware/IoT branches had been pushed yet.
- FS-01 is locally verified and ready for pull-request review; it is not yet merged into `main`.
- Corrected GitHub Actions to install both runtime and development dependencies; otherwise the clean PR runner would fail when `tests/test_health.py` imports FastAPI.

Intelligence review recovered from Jhasmitha's submission:

- Her packet fields now align with the frozen v1 contract.
- Malformed packets should be rejected, while structurally valid packets with false health flags remain valid input for downstream Confidence handling.
- Her feature extraction may flatten the validated packet internally without changing the external contract.
- Her schema path must resolve the repository-root `contracts/sensor-reading.schema.json`, not an `intelligence/contracts/` copy.
- Mirrored contract files must not be integrated; the repository-root contracts remain authoritative.
- `packet_warning.json` is only an abnormal candidate fixture, not an approved WARNING threshold.
- Feature extraction needs a real Pytest suite before Risk/Confidence work begins.
