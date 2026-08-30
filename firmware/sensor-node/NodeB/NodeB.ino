#include <WiFi.h>
#include <HTTPClient.h>
#include <Wire.h>
#include <math.h>

// =====================================================
// NODE NAME
// =====================================================
#define NODE_ID "NODE_B"

// =====================================================
// ESP32-S3 GATEWAY
// =====================================================
const char* ssid = "SMART_MINE_GATEWAY";
const char* password = "mine12345";

const char* gatewayURL = "http://192.168.4.1/data";

// =====================================================
// MPU6050
// =====================================================
#define MPU_ADDR 0x68

#define SDA_PIN 21
#define SCL_PIN 22

// =====================================================
// POTENTIOMETER
// =====================================================
#define POT_PIN 34

// =====================================================
// LEDs
// =====================================================
#define BLUE_LED   25
#define YELLOW_LED 26
#define RED_LED    27

// =====================================================
// MPU VARIABLES
// =====================================================
float previousMagnitude = 1.0;

float vibration = 0.0;

float currentTilt = 0.0;
float baselineTilt = 0.0;
float tiltChange = 0.0;

bool mpuWorking = false;


// =====================================================
// WIFI
// =====================================================
void connectWiFi() {

  Serial.println();
  Serial.println("Connecting NODE B to S3 gateway...");

  WiFi.begin(ssid, password);

  int attempts = 0;

  while (WiFi.status() != WL_CONNECTED && attempts < 20) {

    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {

    Serial.println();
    Serial.println("NODE B CONNECTED TO S3");

    Serial.print("IP: ");
    Serial.println(WiFi.localIP());

  } else {

    Serial.println();
    Serial.println("NODE B WIFI CONNECTION FAILED");
  }
}


// =====================================================
// MPU START
// =====================================================
void startMPU() {

  Wire.begin(SDA_PIN, SCL_PIN);

  Wire.setClock(100000);

  delay(500);

  Wire.beginTransmission(MPU_ADDR);

  Wire.write(0x6B);
  Wire.write(0x00);

  byte error = Wire.endTransmission();

  if (error == 0) {

    Serial.println("NODE B MPU6050 CONNECTED");
    mpuWorking = true;

  } else {

    Serial.print("NODE B MPU6050 ERROR: ");
    Serial.println(error);

    mpuWorking = false;
  }
}


// =====================================================
// READ MPU
// =====================================================
bool readMPU() {

  Wire.beginTransmission(MPU_ADDR);

  Wire.write(0x3B);

  if (Wire.endTransmission(false) != 0) {

    mpuWorking = false;

    return false;
  }

  int received =
      Wire.requestFrom(
        (uint8_t)MPU_ADDR,
        (uint8_t)6,
        (uint8_t)true
      );

  if (received != 6) {

    mpuWorking = false;

    return false;
  }

  int16_t rawX =
      ((int16_t)Wire.read() << 8) | Wire.read();

  int16_t rawY =
      ((int16_t)Wire.read() << 8) | Wire.read();

  int16_t rawZ =
      ((int16_t)Wire.read() << 8) | Wire.read();

  float ax = rawX / 16384.0;

  float ay = rawY / 16384.0;

  float az = rawZ / 16384.0;


  // ===================================================
  // VIBRATION
  // ===================================================

  float magnitude =
      sqrt(
        ax * ax +
        ay * ay +
        az * az
      );

  vibration =
      abs(
        magnitude -
        previousMagnitude
      );

  previousMagnitude = magnitude;


  // ===================================================
  // TILT
  // ===================================================

  currentTilt =
      atan2(
        sqrt(ax * ax + ay * ay),
        az
      ) * 180.0 / PI;


  tiltChange =
      abs(
        currentTilt -
        baselineTilt
      );


  mpuWorking = true;

  return true;
}


// =====================================================
// CALIBRATION
// =====================================================
void calibrateMPU() {

  Serial.println();
  Serial.println("KEEP NODE B STILL!");
  Serial.println("Calibrating MPU6050...");

  float total = 0;

  int count = 0;

  for (int i = 0; i < 30; i++) {

    if (readMPU()) {

      total += currentTilt;

      count++;
    }

    delay(100);
  }

  if (count > 0) {

    baselineTilt =
        total / count;

    Serial.print("Baseline tilt: ");

    Serial.println(baselineTilt);

    Serial.println("NODE B CALIBRATION COMPLETE");

  } else {

    Serial.println("NODE B CALIBRATION FAILED");
  }
}


// =====================================================
// LED FUNCTIONS
// =====================================================
void ledsOff() {

  digitalWrite(BLUE_LED, LOW);
  digitalWrite(YELLOW_LED, LOW);
  digitalWrite(RED_LED, LOW);
}


void showNormal() {

  digitalWrite(BLUE_LED, HIGH);
  digitalWrite(YELLOW_LED, LOW);
  digitalWrite(RED_LED, LOW);
}


void blinkWarning() {

  digitalWrite(BLUE_LED, LOW);
  digitalWrite(RED_LED, LOW);

  digitalWrite(
    YELLOW_LED,
    !digitalRead(YELLOW_LED)
  );
}


void blinkCritical() {

  digitalWrite(BLUE_LED, LOW);
  digitalWrite(YELLOW_LED, LOW);

  digitalWrite(
    RED_LED,
    !digitalRead(RED_LED)
  );
}


// =====================================================
// SEND DATA TO S3
// =====================================================
void sendData(
  int potRaw,
  int displacement,
  String state
) {

  if (WiFi.status() != WL_CONNECTED) {

    connectWiFi();

    return;
  }

  String json = "{";

  json += "\"node_id\":\"";
  json += NODE_ID;
  json += "\",";

  json += "\"tilt_change\":";
  json += String(tiltChange, 2);
  json += ",";

  json += "\"vibration\":";
  json += String(vibration, 3);
  json += ",";

  json += "\"pot_raw\":";
  json += String(potRaw);
  json += ",";

  json += "\"displacement\":";
  json += String(displacement);
  json += ",";

  json += "\"state\":\"";
  json += state;
  json += "\",";

  json += "\"mpu_health\":\"";

  if (mpuWorking) {
    json += "OK";
  } else {
    json += "ERROR";
  }

  json += "\"";

  json += "}";


  HTTPClient http;

  http.begin(gatewayURL);

  http.addHeader(
    "Content-Type",
    "application/json"
  );

  int response =
      http.POST(json);


  Serial.print("S3 response: ");
  Serial.println(response);


  http.end();
}


// =====================================================
// SETUP
// =====================================================
void setup() {

  Serial.begin(115200);

  delay(1000);


  pinMode(BLUE_LED, OUTPUT);
  pinMode(YELLOW_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);

  pinMode(POT_PIN, INPUT);


  ledsOff();


  Serial.println();
  Serial.println("========================");
  Serial.println("SMART MINE NODE B");
  Serial.println("========================");


  startMPU();


  delay(500);


  calibrateMPU();


  connectWiFi();
}


// =====================================================
// LOOP
// =====================================================
void loop() {

  // ===================================================
  // READ MPU
  // ===================================================

  readMPU();


  // ===================================================
  // READ POTENTIOMETER
  // ===================================================

  int potRaw =
      analogRead(POT_PIN);


  int displacement =
      map(
        potRaw,
        0,
        4095,
        0,
        100
      );


  displacement =
      constrain(
        displacement,
        0,
        100
      );


  // ===================================================
  // SENSOR LEVELS
  // ===================================================

  int tiltLevel = 0;

  int vibrationLevel = 0;

  int displacementLevel = 0;


  // ---------------------------------------------------
  // TILT
  // ---------------------------------------------------

  if (tiltChange >= 25) {

    tiltLevel = 2;

  }

  else if (tiltChange >= 10) {

    tiltLevel = 1;
  }


  // ---------------------------------------------------
  // VIBRATION
  // ---------------------------------------------------

  if (vibration >= 0.25) {

    vibrationLevel = 2;

  }

  else if (vibration >= 0.08) {

    vibrationLevel = 1;
  }


  // ---------------------------------------------------
  // POTENTIOMETER
  // ---------------------------------------------------

  if (displacement >= 70) {

    displacementLevel = 2;

  }

  else if (displacement >= 40) {

    displacementLevel = 1;
  }


  // ===================================================
  // FIND HIGHEST LEVEL
  // ===================================================

  int level =
      max(
        tiltLevel,
        max(
          vibrationLevel,
          displacementLevel
        )
      );


  String state;


  // ===================================================
  // NORMAL
  // ===================================================

  if (level == 0) {

    state = "NORMAL";

    showNormal();
  }


  // ===================================================
  // WARNING
  // ===================================================

  else if (level == 1) {

    state = "WARNING";

    blinkWarning();
  }


  // ===================================================
  // CRITICAL
  // ===================================================

  else {

    state = "CRITICAL";

    blinkCritical();
  }


  // ===================================================
  // SERIAL MONITOR
  // ===================================================

  Serial.println();

  Serial.println("======= NODE B =======");


  Serial.print("Tilt change: ");

  Serial.print(tiltChange);

  Serial.println(" deg");


  Serial.print("Vibration: ");

  Serial.println(vibration, 3);


  Serial.print("Pot raw: ");

  Serial.println(potRaw);


  Serial.print("Displacement: ");

  Serial.print(displacement);

  Serial.println("%");


  Serial.print("STATUS: ");

  Serial.println(state);


  Serial.print("MPU: ");

  if (mpuWorking) {
    Serial.println("OK");
  } else {
    Serial.println("ERROR");
  }


  Serial.println("======================");


  // ===================================================
  // SEND TO ESP32-S3
  // ===================================================

  sendData(
    potRaw,
    displacement,
    state
  );


  delay(500);
}