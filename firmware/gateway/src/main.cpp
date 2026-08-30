// SMART-MINE AI / Geo-Sentry -- ESP32-S3 gateway firmware.
//
// Receives sensor-node packets over the local network, forwards them
// unmodified to the FastAPI backend, and applies the backend's returned
// gateway_command (buzzer/LED) -- it performs NO Risk/Confidence/ML
// calculation itself, per docs/CURRENT_HANDOFF.md's "gateway does not
// calculate Risk or Confidence" boundary.
//
// STATUS: written and reviewed against apps/api/routes.py's actual
// gateway_command response shape; never flashed to or run on physical
// hardware (none exists in this environment). See PINOUT.md and README.md.
//
// This is optional -- ../sensor-node/ already posts directly to the backend
// (the "direct node-to-API fallback" in docs/RECOVERY_BACKUP.md). This
// gateway is useful once nodes are out of the backend's own WiFi range but
// still in range of a closer gateway, or to centralize the buzzer.

#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>

#include "config.h"
#include "secrets.h"

WebServer server(80);
uint32_t lastForwardSuccessMs = 0;
uint32_t lastHealthReportMs = 0;

// Device-health telemetry (Part A) -- see the identical note in
// ../../sensor-node/src/main.cpp: temperatureRead() is the real internal
// die-temperature sensor, chip_temp_warning is a safety margin against the
// sourced absolute-max rating, NOT an ambient-temperature claim.
void reportDeviceHealth() {
  float chipTempC = temperatureRead();
  bool warning = chipTempC >= CHIP_TEMP_WARNING_THRESHOLD_C;

  String payload = "{\"chip_temp_c\":" + String(chipTempC, 1) +
                    ",\"chip_temp_warning\":" + String(warning ? "true" : "false") + "}";

  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/api/v1/devices/" + GATEWAY_DEVICE_ID + "/health");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Id", GATEWAY_DEVICE_ID);
  if (strlen(GATEWAY_DEVICE_KEY) > 0) http.addHeader("X-Device-Key", GATEWAY_DEVICE_KEY);
  int status = http.POST(payload);
  Serial.printf("POST /api/v1/devices/%s/health -> %d (chip_temp_c=%.1f)\n", GATEWAY_DEVICE_ID, status,
                chipTempC);
  http.end();
}

// Minimal, deliberately fragile extraction of two fields from the backend's
// JSON response -- no JSON library dependency (see ../../sensor-node/README.md
// for the same design choice). Only ever reads apps/api/routes.py's actual
// gateway_command shape: {"command_id": "...", ..., "buzzer": true|false}.
bool extractGatewayCommand(const String &responseBody, String &commandId, bool &buzzerOn) {
  int commandIdKey = responseBody.indexOf("\"command_id\":\"");
  if (commandIdKey == -1) return false;
  int idStart = commandIdKey + strlen("\"command_id\":\"");
  int idEnd = responseBody.indexOf('"', idStart);
  if (idEnd == -1) return false;
  commandId = responseBody.substring(idStart, idEnd);

  int buzzerKey = responseBody.indexOf("\"buzzer\":");
  if (buzzerKey == -1) return false;
  int valueStart = buzzerKey + strlen("\"buzzer\":");
  buzzerOn = responseBody.startsWith("true", valueStart);
  return true;
}

void applyGatewayCommand(const String &commandId, bool buzzerOn) {
  digitalWrite(PIN_BUZZER, buzzerOn ? HIGH : LOW);

  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/api/v1/gateway/ack");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Id", GATEWAY_DEVICE_ID);
  if (strlen(GATEWAY_DEVICE_KEY) > 0) http.addHeader("X-Device-Key", GATEWAY_DEVICE_KEY);
  String ackBody = "{\"command_id\":\"" + commandId + "\",\"status\":\"APPLIED\"}";
  http.POST(ackBody);
  http.end();
}

// Forwards one node's raw packet body to the backend unmodified, then
// applies whatever gateway_command comes back.
int forwardToBackend(const String &packetJson) {
  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/api/v1/readings");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Id", GATEWAY_DEVICE_ID);
  if (strlen(GATEWAY_DEVICE_KEY) > 0) http.addHeader("X-Device-Key", GATEWAY_DEVICE_KEY);

  int status = http.POST(packetJson);
  if (status == 201) {
    String body = http.getString();
    String commandId;
    bool buzzerOn;
    if (extractGatewayCommand(body, commandId, buzzerOn)) {
      applyGatewayCommand(commandId, buzzerOn);
    }
    lastForwardSuccessMs = millis();
  }
  http.end();
  return status;
}

void handleIngest() {
  if (!server.hasArg("plain")) {
    server.send(400, "application/json", "{\"detail\":\"missing body\"}");
    return;
  }
  int status = forwardToBackend(server.arg("plain"));
  server.send(status > 0 ? status : 502, "application/json",
              status > 0 ? "{}" : "{\"detail\":\"backend unreachable\"}");
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_STATUS_LED, OUTPUT);
  digitalWrite(PIN_BUZZER, LOW);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();
  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("Gateway IP: ");
    Serial.println(WiFi.localIP());
  }

  server.on("/ingest", HTTP_POST, handleIngest);
  server.begin();
}

void loop() {
  server.handleClient();

  // Reconnect if WiFi drops -- matches the heartbeat/reconnect requirement
  // in docs/RECOVERY_BACKUP.md's gateway spec.
  if (WiFi.status() != WL_CONNECTED) {
    digitalWrite(PIN_STATUS_LED, LOW);
    WiFi.reconnect();
    delay(1000);
    return;
  }

  bool uplinkHealthy = (millis() - lastForwardSuccessMs) < UPLINK_STALE_MS || lastForwardSuccessMs == 0;
  digitalWrite(PIN_STATUS_LED, uplinkHealthy ? HIGH : LOW);

  if (millis() - lastHealthReportMs >= DEVICE_HEALTH_REPORT_INTERVAL_MS) {
    reportDeviceHealth();
    lastHealthReportMs = millis();
  }
}
