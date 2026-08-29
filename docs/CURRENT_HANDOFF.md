# Current handoff

For full recovery, read [`RECOVERY_BACKUP.md`](RECOVERY_BACKUP.md).

## Current state

- Active branch: `fullstack/prototype-command-center`.
- `main` contains Jhasmitha's validated feature extraction from PR #1.
- Checkpoint 2 is complete: frozen packet validation → FastAPI → SQLite → readback.
- A deterministic prototype adapter provides separate Risk and Confidence, trend,
  explanations, actions and neighbour correlation until the Intelligence service replaces it.
- Normal, Warning, Critical and Sensor Failure Node A/B scenarios are available.
- Incidents and deterministic Alpha/Bravo dispatch are available.
- The React/Vite command centre renders local-XY Leaflet geometry, Recharts history,
  node sensors, explainability and dispatch.

## Verified commands

```bash
.venv/bin/ruff check .
.venv/bin/ruff format --check .
.venv/bin/python scripts/validate_contracts.py
.venv/bin/python -m pytest
cd apps/dashboard && npm run build && npm run lint
```

Browser verification confirmed live WARNING rendering and Alpha dispatch without console
errors at `http://127.0.0.1:5173` while the services run.

## Next action

1. Push this branch and open a pull request into `main`.
2. Replace `apps/api/decision.py` with Jhasmitha's contract-compatible service when ready.
3. Point the simulator or ESP32-S3 gateway at `POST /api/v1/readings`.
4. Add missing-heartbeat and controlled-recovery handling after the live demo path is stable.
