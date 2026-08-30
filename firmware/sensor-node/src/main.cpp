// SMART-MINE AI / Geo-Sentry -- sensor node firmware (ESP32 + MPU6050 + linear
// potentiometer). Emits the frozen v1 sensor-reading packet
// (contracts/sensor-reading.schema.json) directly to the FastAPI backend --
// the "direct node-to-API fallback" documented in docs/RECOVERY_BACKUP.md,
// used until the ESP32-S3 gateway (../gateway/) is deployed.
//
// STATUS: written against the frozen contract and reviewed for correctness;
// never flashed to or run on physical hardware (none exists in this
// environment). See PINOUT.md and README.md before building.
//
// This firmware does NOT compute Risk, Confidence, or state -- it only
// reports raw sensor evidence, per the same "gateway does not calculate
// Risk or Confidence" boundary documented in docs/CURRENT_HANDOFF.md.

#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <time.h>

#include "config.h"
#include "secrets.h" // untracked: WIFI_SSID, WIFI_PASSWORD, API_BASE_URL -- see README.md

// ---------------------------------------------------------------------------
// MPU6050 register map (InvenSense/TDK MPU-6050 datasheet -- standard, public
// manufacturer information; NOT sourced from the research vault, which has
// this component's page marked "status: unresearched". See PINOUT.md.)
// ---------------------------------------------------------------------------
static const uint8_t MPU6050_REG_PWR_MGMT_1 = 0x6B;
static const uint8_t MPU6050_REG_ACCEL_XOUT_H = 0x3B;

static uint32_t sequence = 0;
static bool mpu6050Ok = false;

bool mpu6050Init() {
  Wire.beginTransmission(MPU6050_I2C_ADDR);
  Wire.write(MPU6050_REG_PWR_MGMT_1);
  Wire.write(0x00); // wake the sensor out of sleep mode
  return Wire.endTransmission() == 0;
}

// Reads the three raw accelerometer axes. Returns false (and leaves outputs
// unchanged) if the I2C transaction fails, so callers can report
// mpu6050_ok=false rather than fabricating a zero reading.
bool mpu6050ReadAccel(float &ax_g, float &ay_g, float &az_g) {
  Wire.beginTransmission(MPU6050_I2C_ADDR);
  Wire.write(MPU6050_REG_ACCEL_XOUT_H);
  if (Wire.endTransmission(false) != 0) return false;

  const uint8_t bytesRequested = 6;
  if (Wire.requestFrom(MPU6050_I2C_ADDR, bytesRequested) != bytesRequested) return false;

  int16_t rawX = (Wire.read() << 8) | Wire.read();
  int16_t rawY = (Wire.read() << 8) | Wire.read();
  int16_t rawZ = (Wire.read() << 8) | Wire.read();

  // Default full-scale range +-2g -> 16384 LSB/g (MPU-6050 datasheet).
  const float lsbPerG = 16384.0f;
  ax_g = rawX / lsbPerG;
  ay_g = rawY / lsbPerG;
  az_g = rawZ / lsbPerG;
  return true;
}

// Standard accelerometer-tilt formula: angle of the gravity vector against
// each axis. Only meaningful near-static (large dynamic acceleration makes
// this unreliable) -- a documented limitation, not hidden.
void computeTiltDeg(float ax_g, float ay_g, float az_g, float &tiltXDeg, float &tiltYDeg) {
  tiltXDeg = atan2(ay_g, sqrt(ax_g * ax_g + az_g * az_g)) * 180.0f / PI;
  tiltYDeg = atan2(-ax_g, sqrt(ay_g * ay_g + az_g * az_g)) * 180.0f / PI;
}

// Simple magnitude-deviation-from-1g vibration proxy. This is a documented
// heuristic for a hackathon prototype, not a validated seismic/vibration
// signal-processing algorithm -- see
// docs/research/vault/10 VIBRATION AND SEISMIC SENSORS/Vibration Signal Processing.md
// for what real processing would require.
float computeVibrationG(float ax_g, float ay_g, float az_g) {
  float magnitude = sqrt(ax_g * ax_g + ay_g * ay_g + az_g * az_g);
  float deviation = magnitude - 1.0f; // 1g at rest
  return fabs(deviation);
}

// Potentiometer wiper -> displacement_mm. DESIGN ASSUMPTION: maps the full
// 12-bit ADC range (ESP32 default) to an assumed 0-50mm travel, because no
// specific potentiometer part or calibration is registered yet (PINOUT.md).
// A real deployment must replace this with an actual calibration curve.
float readDisplacementMm(bool &ok) {
  int raw = analogRead(PIN_DISPLACEMENT_ADC);
  const int adcMax = 4095;
  const float assumedTravelMm = 50.0f;
  // A reading pinned at either rail for a full sample usually means the
  // wiper (or its wiring) is disconnected, not a real 0mm/max reading.
  ok = raw > 5 && raw < (adcMax - 5);
  float mm = (raw / (float)adcMax) * assumedTravelMm;
  return mm < 0.0f ? 0.0f : mm;
}

bool getIsoTimestamp(char *buffer, size_t bufferLen) {
  struct tm timeinfo;
  if (!getLocalTime(&timeinfo, 2000)) return false;
  strftime(buffer, bufferLen, "%Y-%m-%dT%H:%M:%SZ", &timeinfo);
  return true;
}

void setLeds(bool healthy, bool connected) {
  digitalWrite(PIN_LED_GREEN, healthy && connected ? HIGH : LOW);
  digitalWrite(PIN_LED_YELLOW, healthy && !connected ? HIGH : LOW);
  digitalWrite(PIN_LED_RED, !healthy ? HIGH : LOW);
}

// Builds the frozen v1 packet as a JSON string by hand (no JSON library
// dependency) -- field names and shape must exactly match
// contracts/sensor-reading.schema.json; additionalProperties is false there,
// so nothing extra may be added here either.
String buildPacketJson(const char *timestamp, float tiltX, float tiltY, float vibration,
                        float displacement, bool mpuOk, bool dispOk, bool connOk) {
  String json = "{";
  json += "\"schema_version\":\"1.0\",";
  json += "\"node_id\":\"" + String(NODE_ID) + "\",";
  json += "\"sequence\":" + String(sequence) + ",";
  json += "\"timestamp\":\"" + String(timestamp) + "\",";
  json += "\"sensors\":{";
  json += "\"tilt_x_deg\":" + String(tiltX, 3) + ",";
  json += "\"tilt_y_deg\":" + String(tiltY, 3) + ",";
  json += "\"vibration_g\":" + String(vibration, 3) + ",";
  json += "\"displacement_mm\":" + String(displacement, 3);
  json += "},";
  json += "\"health\":{";
  json += "\"mpu6050_ok\":" + String(mpuOk ? "true" : "false") + ",";
  json += "\"displacement_input_ok\":" + String(dispOk ? "true" : "false") + ",";
  json += "\"connection_ok\":" + String(connOk ? "true" : "false");
  json += "}}";
  return json;
}

void setup() {
  Serial.begin(115200);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_YELLOW, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);
  setLeds(false, false);

  Wire.begin(PIN_I2C_SDA, PIN_I2C_SCL);
  mpu6050Ok = mpu6050Init();
  if (!mpu6050Ok) Serial.println("MPU6050 init failed -- check wiring (see PINOUT.md)");

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  Serial.print("Connecting to WiFi");
  uint32_t start = millis();
  while (WiFi.status() != WL_CONNECTED && millis() - start < 15000) {
    delay(250);
    Serial.print(".");
  }
  Serial.println();

  if (WiFi.status() == WL_CONNECTED) {
    // Uses the network's DHCP-provided time servers via SNTP; falls back to
    // pool.ntp.org. Requires the local network to have internet access for
    // an accurate wall-clock timestamp.
    configTime(0, 0, "pool.ntp.org", "time.nist.gov");
  }
}

void loop() {
  float ax, ay, az, tiltX = 0, tiltY = 0, vibration = 0;
  bool mpuReadOk = mpu6050Ok && mpu6050ReadAccel(ax, ay, az);
  if (mpuReadOk) {
    computeTiltDeg(ax, ay, az, tiltX, tiltY);
    vibration = computeVibrationG(ax, ay, az);
  }

  bool dispOk;
  float displacement = readDisplacementMm(dispOk);

  bool connOk = WiFi.status() == WL_CONNECTED;
  setLeds(mpuReadOk && dispOk, connOk);

  char timestamp[32];
  if (connOk && getIsoTimestamp(timestamp, sizeof(timestamp))) {
    String payload = buildPacketJson(timestamp, tiltX, tiltY, vibration, displacement,
                                      mpuReadOk, dispOk, connOk);

    HTTPClient http;
    http.begin(String(API_BASE_URL) + "/api/v1/readings");
    http.addHeader("Content-Type", "application/json");
    int status = http.POST(payload);
    Serial.printf("POST /api/v1/readings -> %d\n", status);
    http.end();

    sequence++;
  } else {
    Serial.println("Skipped this cycle: no WiFi connection or clock not yet synced");
  }

  delay(REPORT_INTERVAL_MS);
}
