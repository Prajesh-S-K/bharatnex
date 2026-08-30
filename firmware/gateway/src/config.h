// Gateway build configuration. Copy secrets.h.example to secrets.h (untracked)
// before building -- see README.md.
#pragma once

#define GATEWAY_DEVICE_ID "GATEWAY_01"

// Buzzer / status LED -- see ../PINOUT.md
#define PIN_BUZZER 4
#define PIN_STATUS_LED 2

// How long without a successful forward-to-backend before the gateway
// considers its own uplink unhealthy (distinct from any single node being
// offline, which the backend already tracks per-node).
#define UPLINK_STALE_MS 10000

// Device-health warning margin. NOT an ambient-temperature limit -- see the
// identical note in ../../sensor-node/src/config.h. Safety ceiling below the
// sourced absolute-max storage rating of 105 C (VAL-MCU-005 in the research
// vault's Sourced Parameter Register), not a calibrated ambient reading.
#define CHIP_TEMP_WARNING_THRESHOLD_C 90.0f

// How often to report device health to the backend (separate from the
// sensor-reading cadence).
#define DEVICE_HEALTH_REPORT_INTERVAL_MS 10000
