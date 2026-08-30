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
