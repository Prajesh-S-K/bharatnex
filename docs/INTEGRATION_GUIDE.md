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

Replace `apps/api/decision.py` with a Python adapter that accepts one validated packet and returns
the frozen decision fields: `state`, `risk`, `confidence`, `trend`, `reason_codes`, and `actions`.
The fallback remains selectable until the Intelligence workstream passes integration tests.

## Inspection phones

The shared PWA is `/inspection`. Unit identity is device-local. Lifecycle updates use
`POST /api/v1/incidents/{id}/inspection`; WebSocket `/api/v1/live` triggers immediate refresh and
four-second polling remains the fallback.

## Safe boundaries

All thresholds, routes, timing and credentials are prototype settings. The system provides early
warning and decision support; it does not predict exact collapse time or replace certified safety
systems.
