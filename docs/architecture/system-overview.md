# System architecture

## Component boundaries

```text
[Sensor Node A] ─┐
                 ├─ Wi-Fi ─> [ESP32-S3 Gateway] ─ HTTP ─> [FastAPI]
[Sensor Node B] ─┘                                      │
[Simulator] ────────────────────────────────────────────┘
                                                        ↓
                                                 [Validation/SQLite]
                                                        ↓
 [Geometry] → [Features] → [Isolation Forest] → [Trend/Correlation]
                                                        ↓
                                       [Risk + Confidence + Reasons]
                                                        ↓
                                   [Orchestrator/Incident/Dispatch]
                                                        ↓
                                         [REST API / React Dashboard]
```

## Dependency rule

- Firmware and simulator produce the sensor-reading contract.
- Full Stack validates/persists it and exposes stable service interfaces.
- Intelligence accepts validated domain objects and returns decision objects.
- The dashboard consumes API responses; it does not reproduce decision logic.
- Hardware indicators consume commands/state; they do not independently override the supervisory decision.

