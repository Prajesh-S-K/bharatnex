# SMART-MINE AI — Current Handoff

For complete recovery, read [RECOVERY_BACKUP.md](RECOVERY_BACKUP.md).

## Current state

- Integration branch: `fullstack/intelligence-integration`.
- Base: `fullstack/integrated-prototype` at `3e89032` (merge of the full I-03–I-10 Intelligence
  implementation into the finalized Full Stack prototype).
- `apps/api/decision.py` now wires the real Intelligence pipeline (Risk, Confidence, trend,
  correlation, hysteresis state machine, Isolation Forest anomaly evidence, LLM-optional
  explanation) in place of the temporary deterministic fallback. See "Intelligence adapter" in
  [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md).
- Included hardening: stale/out-of-order sequence rejection, explicit SQLite connection
  closure, dropped-WebSocket isolation, WATCH scenario, real dashboard WebSocket status and
  mobile-PWA width isolation.
- The React/FastAPI/SQLite/Leaflet/Recharts command centre and Alpha/Bravo inspection PWA are
  the runnable prototype website, now running on real Intelligence decisions end to end.
- The local n8n/Ollama Idea-to-Checkpoint system remains operational and its history is
  preserved; it was not touched by this integration.
- Combined verification passed: 145 Python tests (23 Full Stack + intelligence/tests + shared),
  Ruff lint/format, contract validation, whitespace and Git diff checks.
- Live browser verification passed on restarted API + dashboard servers: Judge Demo end to end,
  individual NORMAL/WATCH/WARNING/CRITICAL scenarios, `SENSOR_ANOMALY` reason code confirmed
  present (proving the real Isolation Forest is live, not the old fallback), incident
  acknowledge/dispatch lifecycle, and 375 px mobile layout — zero console errors on a fresh tab.

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
- `apps/api/decision.py` is the real Intelligence adapter (see "Intelligence adapter" in
  [INTEGRATION_GUIDE.md](INTEGRATION_GUIDE.md)); the temporary deterministic fallback has been
  fully replaced.
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

1. Review branch `fullstack/intelligence-integration` and its diff against
   `fullstack/integrated-prototype` (only `apps/api/decision.py`, `apps/api/routes.py` and
   `intelligence/config.py` change).
2. Merge/push the pull request — no further fixes are required before merging to `main`.
3. Connect Wokwi/ESP32 traffic using the unchanged v1 contract.
