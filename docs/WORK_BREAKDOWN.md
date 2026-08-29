# Work breakdown and handoffs

## Team mapping from the synchronized plan

| Person | Primary responsibility | Workstream |
|---|---|---|
| Prajesh | FastAPI, SQLite, React and GIS dashboard | Full Stack |
| Jashmita | Isolation Forest, fusion, Risk/Confidence, trend and decision logic | Agentic AI + ML/LLM |
| Rahul | Architecture, geometry, supervisory orchestrator and interface control | Agentic AI + ML/LLM / integration |
| Devdarshini | Simulator, scenarios, failure injection and integration QA | Shared testing support |
| Rithish | ESP32 nodes, MPU6050, potentiometer, wiring and calibration | Hardware + IoT |
| Rohit | ESP32-S3, Wi-Fi, heartbeat, reconnect and communication debugging | Hardware + IoT |

Adjust names only through an agreed documentation update; folder ownership remains the stable three-workstream model.

## Integration checkpoints

1. **Contract:** examples validate against schemas.
2. **Data path:** simulator → FastAPI → SQLite → readable response.
3. **Intelligence:** normal and deformation packets produce tested decisions.
4. **Automation:** WATCH/WARNING/CRITICAL actions are observable.
5. **Dashboard:** full decision and system health are visible on one screen.
6. **Wokwi:** virtual nodes replace simulator input.
7. **Physical:** real nodes replace Wokwi; simulator remains fallback.

