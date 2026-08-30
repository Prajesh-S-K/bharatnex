# Current handoff

For full recovery, read [RECOVERY_BACKUP.md](RECOVERY_BACKUP.md).

## Current state

- Active branch: `fullstack/prototype-command-center`.
- Backend inspection workflow committed at `aa779b5`.
- Mobile inspection PWA committed at `9a60a54`.
- Operator/demo/integration checkpoint is implemented and browser-verified, but not yet committed.
- Judge Demo passed end-to-end:
  BASELINE → RISING RISK → CRITICAL + DISPATCH → INSPECTION DEMO → COMPLETE.
- Mine Panel Overview is rendering correctly with Leaflet local-XY geometry.
- Python tests: 13 passed.
- Ruff lint/format: passed.
- Contract validation: passed.
- Frontend ESLint/build: passed.
- npm audit: 0 vulnerabilities.
- `git diff --check`: passed.
- `scripts/prototype_tools.py check`: passed.
- Vite bundle-size warning is non-blocking.

## Integration boundaries

- Frozen v1 sensor contract remains authoritative.
- Hardware/simulator/gateway must send the unchanged packet.
- Gateway does not calculate Risk or Confidence.
- `apps/api/decision.py` remains the temporary deterministic prototype adapter.
- Replace it only after the Intelligence implementation is reviewed and contract-compatible.
- Gas remains outside frozen v1.
- This is a prototype, not a certified mining safety system.

## Next action

1. Run final repository verification.
2. Stage all Checkpoint 3 files, including untracked files.
3. Commit Checkpoint 3.
4. Push `fullstack/prototype-command-center`.
5. Review the pull request before merging into `main`.
