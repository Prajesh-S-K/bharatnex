# Workstream 1 — Full Stack

## Ownership

`apps/api/`, `apps/dashboard/`, database migrations, REST/WebSocket interfaces and frontend integration.

## Deliverables

- FastAPI health endpoint and `POST /api/v1/readings`.
- JSON Schema/Pydantic validation, duplicate-sequence handling and UTC timestamps.
- SQLite tables for readings, decisions, incidents, inspection units and system events.
- API adapters that call the intelligence package without embedding ML logic in routes.
- One command dashboard with mine map, Node A/B status, sensor trends, Risk, Confidence, reasons, incident state and Alpha/Bravo status.
- Clear offline/error/loading states.

## First checkpoint

Run a contract example through API validation, store it, and return it from a read endpoint. Do not wait for firmware or ML.

## Do not own

Sensor firmware, anomaly algorithms, risk thresholds or LLM prompts.

