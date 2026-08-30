# Prototype integration guide

The live API documentation is available at `http://<laptop-ip>:8000/docs`.

## Hardware gateway

Send the unchanged frozen sensor packet to `POST /api/v1/readings`. Optional prototype gateway
authentication uses `X-Device-Id` and `X-Device-Key` headers. The response includes the frozen
decision plus a separate `gateway_command` containing reporting interval, LED state and buzzer
state. Acknowledge it with `POST /api/v1/gateway/ack`:

```json
{"command_id":"NODE_A-42","status":"APPLIED"}
```

The command is separate from the sensor and decision contracts. NORMAL/WATCH/WARNING/CRITICAL
reporting intervals are 5000/2000/1000/500 ms for demonstration only.

## Intelligence adapter

`apps/api/decision.py` wires the Full Stack prototype to the real Intelligence pipeline
(`intelligence/` — I-02 through I-09: feature extraction, Risk, Confidence, trend/correlation,
the hysteresis state machine, Isolation Forest anomaly evidence and the deterministic
orchestrator). It is the only file that imports `intelligence/`; `apps/api/routes.py` calls its
`evaluate(packet, history, neighbour)` function and gets back the frozen decision fields —
`state`, `risk`, `confidence`, `trend`, `reason_codes`, and `actions` — without knowing
Intelligence exists.

`evaluate()` replays `intelligence.state_machine.evaluate_state()` over the node's prior readings
to reconstruct `(previous_state, streak)` on every call. This is deliberate: it keeps the
hysteresis state machine a pure function with zero persisted state and required no schema or
storage changes. Isolation Forest evidence is trained once from a synthetic baseline on first use
and cached in-process; if that training ever fails, `evaluate()` continues with
`anomaly_evidence=None` — the deterministic pipeline never depends on ML succeeding.

The former deterministic fallback formula has been fully replaced. Any future adapter change must
preserve this same call boundary and the frozen decision shape.

## Inspection phones

The shared PWA is `/inspection`. Unit identity is device-local. Lifecycle updates use
`POST /api/v1/incidents/{id}/inspection`; WebSocket `/api/v1/live` triggers immediate refresh and
four-second polling remains the fallback.

## Safe boundaries

All thresholds, routes, timing and credentials are prototype settings. The system provides early
warning and decision support; it does not predict exact collapse time or replace certified safety
systems.
