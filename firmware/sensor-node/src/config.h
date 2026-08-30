// Per-node build configuration.
//
// Two physical boards share this codebase; each is flashed once with its own
// NODE_ID matching the frozen v1 contract's node_id enum
// (contracts/sensor-reading.schema.json: "NODE_A" | "NODE_B").
//
// Copy this file's WiFi/API values into a local, untracked
// `firmware/sensor-node/src/secrets.h` before building -- never commit real
// Wi-Fi credentials (see firmware/sensor-node/README.md).
#pragma once

#define NODE_ID "NODE_A" // or "NODE_B" for the second physical board

// I2C (MPU6050) -- see ../PINOUT.md
#define PIN_I2C_SDA 21
#define PIN_I2C_SCL 22
#define MPU6050_I2C_ADDR 0x68 // AD0 tied low -- see ../PINOUT.md

// Potentiometer (displacement proxy) -- see ../PINOUT.md
#define PIN_DISPLACEMENT_ADC 34

// Status LEDs -- see ../PINOUT.md
#define PIN_LED_GREEN 25
#define PIN_LED_YELLOW 26
#define PIN_LED_RED 27

// Reporting interval. The Full Stack prototype's demo scenarios use
// 500ms-5000ms depending on state (apps/api/routes.py SCENARIOS); this
// firmware reports on a fixed interval since it has no access to the
// server's computed state, matching the "direct node-to-API mode" fallback
// documented in docs/RECOVERY_BACKUP.md.
#define REPORT_INTERVAL_MS 2000
