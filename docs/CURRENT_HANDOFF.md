# SMART-MINE AI — Current Handoff

For complete recovery, read [RECOVERY_BACKUP.md](RECOVERY_BACKUP.md).

## Current state

- Integration branch: `fullstack/integrated-prototype`.
- Base: `fullstack/prototype-command-center` at `5284971`.
- Reviewed Full Stack finalization merged from `fullstack/final-software` at `ab6c010`.
- Included hardening: stale/out-of-order sequence rejection, explicit SQLite connection
  closure, dropped-WebSocket isolation, WATCH scenario, real dashboard WebSocket status and
  mobile-PWA width isolation.
- The React/FastAPI/SQLite/Leaflet/Recharts command centre and Alpha/Bravo inspection PWA are
  the runnable prototype website.
- The local n8n/Ollama Idea-to-Checkpoint system remains operational and its history is
  preserved.
- Combined verification passed: 43 Python tests, Ruff, contracts, whitespace, frontend
  lint/build, npm audit and Git diff checks.
- Live browser verification passed for WATCH, Critical dispatch, real WebSocket status and
  375/390/412 px phone layouts with no console errors.

## Runtime

- Dashboard: `http://127.0.0.1:5173/`
- Inspection PWA: `http://127.0.0.1:5173/inspection`
- API/docs: `http://127.0.0.1:8000/` and `http://127.0.0.1:8000/docs`
- n8n: `http://127.0.0.1:5678/`
- Local task form: `http://127.0.0.1:5678/form/smart-mine-idea`

## Integration boundaries

- Frozen v1 sensor and decision contracts remain authoritative and unchanged.
- Hardware/simulator/gateway must send the unchanged packet.
- Gateway does not calculate Risk or Confidence.
- `apps/api/decision.py` remains the temporary deterministic prototype adapter until the
  Intelligence implementation is separately reviewed and contract-compatible.
- n8n cannot modify contracts, automation, GitHub configuration, secrets or another
  workstream; it never pushes or merges.
- Gas remains outside frozen v1. This is a prototype, not a certified mining safety system.

## Known limitations

- The mobile offline-queue flush has a theoretical network-flap double-submit race that has
  not been reproduced.
- WebSocket failure handling is covered by automated tests, but a physical Wi-Fi interruption
  should still be included in the final cold-start rehearsal.
- Vite's bundle-size warning is non-blocking and remains deferred.

## Next action

1. Push `fullstack/integrated-prototype`.
2. Review the integration branch before merging to `main`.
3. Connect Wokwi/ESP32 traffic using the unchanged v1 contract.
