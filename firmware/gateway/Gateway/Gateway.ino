// SMART-MINE AI / Geo-Sentry -- ESP32-S3 gateway firmware.
//
// Based on the team's own tested gateway code (same AP config, buzzer pin,
// web server structure) -- this version adds the one missing piece: actually
// forwarding node readings to the real FastAPI backend, converting field
// names/units to the frozen v1 contract (contracts/sensor-reading.schema.json)
// along the way. NodeA.ino/NodeB.ino are untouched.
//
// STATUS: NodeA/NodeB are tested, working hardware. This gateway integration
// is new and NOT yet device-tested -- the constructed packet shape has been
// verified against the real backend directly (see docs/INDUSTRIAL_ROADMAP.md),
// but the actual AP+STA dual WiFi mode and real-hardware round trip have not.

#include <WiFi.h>
#include <WebServer.h>
#include <HTTPClient.h>
#include <time.h>

#include "secrets.h" // untracked: STA_WIFI_SSID, STA_WIFI_PASSWORD, API_BASE_URL

// =====================================================
// WIFI ACCESS POINT (unchanged -- NodeA/NodeB join this exact network)
// =====================================================
const char *ap_ssid = "SMART_MINE_GATEWAY";
const char *ap_password = "mine12345";

// =====================================================
// BUZZER
// =====================================================
#define BUZZER_PIN 8

// Device-health warning margin (Part A). NOT an ambient-temperature limit --
// the internal die-temperature sensor (temperatureRead()) measures silicon
// temperature, which runs hotter than ambient from self-heating with no
// characterized offset (see docs/research/vault/00 MASTER CONTROL/Geo-Sentry
// Sourced Parameter Register.md, VAL-MCU-004 vs VAL-MCU-006). This margin is
// a safety ceiling below the sourced absolute-max storage rating of 105 C
// (VAL-MCU-005), not a calibrated ambient reading.
#define CHIP_TEMP_WARNING_THRESHOLD_C 90.0f
#define DEVICE_HEALTH_REPORT_INTERVAL_MS 10000
uint32_t lastHealthReportMs = 0;

// =====================================================
// WEB SERVER
// =====================================================
WebServer server(80);

// Per-node sequence counters. Neither NodeA.ino nor NodeB.ino sends a
// sequence number, but the frozen contract requires one (integer, and the
// backend rejects a packet whose sequence isn't newer than the last one it
// stored for that node -- see tests/test_storage_sequence_ordering.py). The
// gateway is the single point every packet from a given node passes through
// on its own AP, so counting here is safe.
uint32_t sequenceA = 0;
uint32_t sequenceB = 0;

// ---------------------------------------------------------------------------
// Minimal manual JSON field extraction -- same no-library-dependency style
// already used in the team's own s3.txt (which does indexOf-based string
// matching for the "state" field). Only reads the exact fields NodeA.ino/
// NodeB.ino actually send.
// ---------------------------------------------------------------------------
String extractStringField(const String &body, const String &key) {
  String needle = "\"" + key + "\":\"";
  int start = body.indexOf(needle);
  if (start == -1) return "";
  start += needle.length();
  int end = body.indexOf('"', start);
  if (end == -1) return "";
  return body.substring(start, end);
}

float extractNumberField(const String &body, const String &key) {
  String needle = "\"" + key + "\":";
  int start = body.indexOf(needle);
  if (start == -1) return 0.0;
  start += needle.length();
  int end = start;
  while (end < (int)body.length() && (isDigit(body[end]) || body[end] == '.' || body[end] == '-')) end++;
  return body.substring(start, end).toFloat();
}

bool getIsoTimestamp(char *buffer, size_t bufferLen) {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo, 2000)) return false;
  strftime(buffer, bufferLen, "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return true;
}

// Device-health telemetry (Part A) -- reports the GATEWAY's own chip
// temperature only (NodeA.ino/NodeB.ino are untouched and do not report
// this). Kept entirely separate from the frozen sensor packet.
void reportDeviceHealth() {
  float chipTempC = temperatureRead();
  bool warning = chipTempC >= CHIP_TEMP_WARNING_THRESHOLD_C;

  String payload = "{\"chip_temp_c\":" + String(chipTempC, 1) +
                    ",\"chip_temp_warning\":" + String(warning ? "true" : "false") + "}";

  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/api/v1/devices/ESP32-S3-GATEWAY/health");
  http.addHeader("Content-Type", "application/json");
  int status = http.POST(payload);
  Serial.printf("Device health -> backend: %d (chip_temp_c=%.1f)\n", status, chipTempC);
  http.end();
}

// Converts one node's raw JSON (NodeA.ino/NodeB.ino's sendData() body) into
// the frozen v1 packet and forwards it to the real backend. Drives the
// buzzer from the backend's own gateway_command response, not the node's own
// naive local threshold -- the backend's Risk/Confidence/trend pipeline is
// the actual decision authority; the node's local LEDs are a separate,
// immediate visual aid and are unaffected by this.
void forwardToBackend(const String &nodeBody) {
  String nodeId = extractStringField(nodeBody, "node_id");
  if (nodeId != "NODE_A" && nodeId != "NODE_B") {
    Serial.println("Unknown node_id, dropping packet");
    return;
  }

  float tiltChange = extractNumberField(nodeBody, "tilt_change");
  float vibration = extractNumberField(nodeBody, "vibration");
  float potRaw = extractNumberField(nodeBody, "pot_raw");
  // Only NodeB.ino sends mpu_health; NodeA.ino does not -- default to healthy
  // when the field is absent rather than guessing a failure.
  String mpuHealth = extractStringField(nodeBody, "mpu_health");
  bool mpuOk = mpuHealth.length() == 0 ? true : (mpuHealth == "OK");

  // DESIGN NOTE: NodeA.ino/NodeB.ino compute one combined tilt-from-vertical
  // angle (atan2(sqrt(ax^2+ay^2), az)), not independent X/Y axis tilts. The
  // frozen contract requires both tilt_x_deg and tilt_y_deg -- the combined
  // value is reported as tilt_x_deg; tilt_y_deg is 0 because this hardware
  // does not measure it independently. Labelled here, not hidden.
  float tiltXDeg = tiltChange;
  float tiltYDeg = 0.0;

  // DESIGN ASSUMPTION: same as noted in firmware/sensor-node/PINOUT.md for the
  // originally-drafted firmware -- 0-4095 ADC mapped to an assumed 0-50mm
  // potentiometer travel, no real calibration curve exists yet.
  float displacementMm = (potRaw / 4095.0) * 50.0;
  bool displacementOk = potRaw > 5 && potRaw < 4090;

  uint32_t &sequence = (nodeId == "NODE_A") ? sequenceA : sequenceB;
  sequence++;

  char timestamp[32];
  bool haveTime = getIsoTimestamp(timestamp, sizeof(timestamp));
  if (!haveTime) {
    Serial.println("Clock not synced yet -- skipping this reading (no internet on the STA link?)");
    return;
  }

  String packet = "{";
  packet += "\"schema_version\":\"1.0\",";
  packet += "\"node_id\":\"" + nodeId + "\",";
  packet += "\"sequence\":" + String(sequence) + ",";
  packet += "\"timestamp\":\"" + String(timestamp) + "\",";
  packet += "\"sensors\":{";
  packet += "\"tilt_x_deg\":" + String(tiltXDeg, 3) + ",";
  packet += "\"tilt_y_deg\":" + String(tiltYDeg, 3) + ",";
  packet += "\"vibration_g\":" + String(vibration, 3) + ",";
  packet += "\"displacement_mm\":" + String(displacementMm, 3);
  packet += "},";
  packet += "\"health\":{";
  packet += "\"mpu6050_ok\":" + String(mpuOk ? "true" : "false") + ",";
  packet += "\"displacement_input_ok\":" + String(displacementOk ? "true" : "false") + ",";
  packet += "\"connection_ok\":true";
  packet += "}}";

  HTTPClient http;
  http.begin(String(API_BASE_URL) + "/api/v1/readings");
  http.addHeader("Content-Type", "application/json");
  http.addHeader("X-Device-Id", "ESP32-S3-GATEWAY");
  int status = http.POST(packet);
  Serial.print(nodeId);
  Serial.print(" -> backend: ");
  Serial.println(status);

  if (status == 201) {
    String responseBody = http.getString();
    bool buzzerOn = responseBody.indexOf("\"buzzer\":true") >= 0;
    digitalWrite(BUZZER_PIN, buzzerOn ? HIGH : LOW);
  }
  http.end();
}

// =====================================================
// HANDLE DATA FROM NODE A / NODE B
// =====================================================
void handleData() {

  if (!server.hasArg("plain")) {

    server.send(
      400,
      "text/plain",
      "NO DATA RECEIVED"
    );

    return;
  }

  String data = server.arg("plain");

  Serial.println();
  Serial.println("==================================");
  Serial.println("      SENSOR DATA RECEIVED");
  Serial.println("==================================");

  Serial.println(data);

  forwardToBackend(data);

  Serial.println("==================================");

  // Tell ESP32 node that data arrived
  server.send(
    200,
    "text/plain",
    "DATA RECEIVED BY S3"
  );
}

// =====================================================
// SETUP
// =====================================================
void setup() {

  Serial.begin(115200);

  delay(1000);


  // -----------------------------------
  // BUZZER
  // -----------------------------------
  pinMode(BUZZER_PIN, OUTPUT);

  digitalWrite(BUZZER_PIN, LOW);


  Serial.println();
  Serial.println("==================================");
  Serial.println("    SMART-MINE ESP32-S3 GATEWAY");
  Serial.println("==================================");


  // -----------------------------------
  // AP + STA DUAL MODE
  // -----------------------------------
  // AP: the fixed network NodeA/NodeB already join (unchanged).
  // STA: joins the real room/lab Wi-Fi so this gateway can reach the laptop
  // running the FastAPI backend -- this is the piece that was missing.
  WiFi.mode(WIFI_AP_STA);

  bool result =
    WiFi.softAP(
      ap_ssid,
      ap_password
    );


  if (result) {

    Serial.println("Gateway AP started successfully!");

  }

  else {

    Serial.println("WiFi AP FAILED!");
  }


  Serial.println();

  Serial.print("AP SSID: ");
  Serial.println(ap_ssid);

  Serial.print("AP Gateway IP: ");
  Serial.println(WiFi.softAPIP());

  Serial.println();
  Serial.print("Connecting to real network \"");
  Serial.print(STA_WIFI_SSID);
  Serial.println("\" to reach the backend...");

  WiFi.begin(STA_WIFI_SSID, STA_WIFI_PASSWORD);
  uint32_t staStart = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - staStart < 15000) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    Serial.print("STA CONNECTED, gateway's own IP on that network: ");
    Serial.println(WiFi.localIP());
    // Needs internet access on the STA network for NTP; if there is none,
    // getIsoTimestamp() will keep failing and forwardToBackend() will keep
    // skipping readings rather than sending a fabricated timestamp.
    configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  } else {
    Serial.println("STA WIFI CONNECTION FAILED -- readings cannot reach the backend.");
    Serial.println("Check STA_WIFI_SSID/STA_WIFI_PASSWORD in secrets.h.");
  }


  // -----------------------------------
  // START HTTP SERVER
  // -----------------------------------
  server.on(
    "/data",
    HTTP_POST,
    handleData
  );


  server.begin();


  Serial.println();
  Serial.println("HTTP server started");

  Serial.println(
    "Waiting for NODE A and NODE B..."
  );

  Serial.println("==================================");
}

// =====================================================
// LOOP
// =====================================================
void loop() {

  server.handleClient();

  // Reconnect the STA link if it drops -- the AP side (NodeA/NodeB-facing)
  // is unaffected by this, since softAP() runs independently.
  if (WiFi.status() != WL_CONNECTED) {
    WiFi.reconnect();
    return;
  }

  if (millis() - lastHealthReportMs >= DEVICE_HEALTH_REPORT_INTERVAL_MS) {
    reportDeviceHealth();
    lastHealthReportMs = millis();
  }
}
