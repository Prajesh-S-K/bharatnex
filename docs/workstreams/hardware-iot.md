# Workstream 3 — Hardware + IoT

## Ownership

`firmware/` and hardware-facing simulator scenarios.

## Deliverables

- Shared sensor-node firmware configured as Node A or Node B.
- MPU6050 tilt/movement and vibration-derived reading.
- Potentiometer mapped to prototype displacement.
- Green/yellow/red output commands.
- ESP32-S3 gateway forwarding, heartbeat, reconnect and buzzer command.
- Wokwi projects for both nodes and gateway before physical integration.
- Monotonic sequence numbers and the exact v1 sensor contract.
- Repeatable calibration notes and wiring/pin map.

## First checkpoint

Produce valid example packets from Node A and Node B—or Wokwi—and confirm they match `contracts/sensor-reading.schema.json`.

## Constraints

- Never commit Wi-Fi credentials.
- Do not rename fields to match convenient firmware variable names.
- Keep a direct-to-backend fallback if gateway debugging threatens the integration schedule.

