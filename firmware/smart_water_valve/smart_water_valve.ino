/*
  Smart Water Valve Control System (Hardware IoT Version)
  --------------------------------------------------------
  Hardware:
    - Arduino Uno R3
    - Relay module controlling 12V Normally Closed Solenoid Valve
    - 2 Pressure Sensors  -> A0, A1
    - 2 Concentration Sensors -> A2, A3
    - Status LED -> Pin 13
    - Communication -> Serial @ 115200 baud

  Safety Rules:
    - Auto emergency shutdown on overpressure (>6 bar)
    - Auto emergency shutdown on critical concentration (>500 units)
    - Auto-close after 30 minutes of continuous open state
    - Manual reset required after emergency

  Commands (Serial):
    OPEN, CLOSE, STATUS, INFO, PING, FORCE_OPEN, RESET_EMERGENCY
    Telemetry every 1s:
      TELEMETRY:{"t":1234,"valve":"OPEN","p1":3.45,"p2":3.21,"c_src":140.2,"c_dst":230.1,"em":0}
*/

#include <Arduino.h>

// --- Pin Configuration ---
#define RELAY_PIN 7
#define STATUS_LED 13
#define PRESSURE1_PIN A0
#define PRESSURE2_PIN A1
#define CONC_SRC_PIN A2
#define CONC_DST_PIN A3

// --- Timing ---
const unsigned long TELEMETRY_INTERVAL_MS = 1000UL;  // send telemetry every 1 second
const unsigned long SAFETY_TIMEOUT_MS = 1800000UL;   // 30 min (auto-close)

// --- Safety Thresholds ---
const float MAX_PRESSURE_BAR = 6.0;
const float CRITICAL_CONCENTRATION = 500.0;
const float MIN_SRC_CONCENTRATION = 10.0;
const float MAX_DST_CONCENTRATION = 400.0;

// --- Calibration (example, replace for your sensors) ---
const float PRESSURE_SENSOR_V_MIN = 0.5;     // 0 bar output voltage
const float PRESSURE_SENSOR_V_MAX = 4.5;     // full-scale voltage
const float PRESSURE_SENSOR_BAR_MAX = 10.0;  // full-scale = 10 bar

const float CONC_SENSOR_V_MIN = 0.0;         // 0 concentration voltage
const float CONC_SENSOR_V_MAX = 5.0;         // full-scale voltage
const float CONC_SENSOR_UNIT_MAX = 1000.0;   // full-scale = 1000 units

// --- Global State ---
bool valveState = false;
bool emergencyMode = false;
unsigned long lastTelemetryMs = 0;
unsigned long lastCommandTime = 0;
unsigned long valveOpenTimestamp = 0;
unsigned long totalValveRunMs = 0;

// --- Serial Buffer ---
String inputBuffer = "";
bool commandReady = false;

// --- Function Declarations ---
void processCommand(String cmd);
void sendTelemetry();
void openValve(bool forced = false);
void closeValve();
void sendStatus();
void checkSafetyConditions();
float readPressure(int pin);
float readConcentration(int pin);
float analogToVoltage(int raw);
void sendStartupInfo();

// --- Setup ---
void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(STATUS_LED, OUTPUT);

  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(STATUS_LED, LOW);

  sendStartupInfo();

  for (int i = 0; i < 3; i++) {  // startup blink
    digitalWrite(STATUS_LED, HIGH);
    delay(150);
    digitalWrite(STATUS_LED, LOW);
    delay(150);
  }
}

// --- Loop ---
void loop() {
  // Non-blocking serial read
  while (Serial.available()) {
    char c = (char)Serial.read();
    if (c == '\r') continue;
    inputBuffer += c;
    if (c == '\n') {
      commandReady = true;
      break;
    }
  }

  if (commandReady) {
    String cmd = inputBuffer;
    inputBuffer = "";
    commandReady = false;
    cmd.trim();
    cmd.toUpperCase();
    processCommand(cmd);
  }

  unsigned long now = millis();

  // Periodic telemetry
  if (now - lastTelemetryMs >= TELEMETRY_INTERVAL_MS) {
    sendTelemetry();
    lastTelemetryMs = now;
  }

  // Safety auto-close
  if (valveState && (now - lastCommandTime > SAFETY_TIMEOUT_MS)) {
    Serial.println("EVENT: SAFETY_TIMEOUT — closing valve automatically");
    closeValve();
  }

  // Continuous safety monitoring
  checkSafetyConditions();
}

// --- Sensor Reading Helpers ---
float analogToVoltage(int raw) {
  return (raw * (5.0 / 1023.0));
}

float readPressure(int pin) {
  int raw = analogRead(pin);
  float v = analogToVoltage(raw);
  float v_clamped = constrain(v, PRESSURE_SENSOR_V_MIN, PRESSURE_SENSOR_V_MAX);
  float ratio = (v_clamped - PRESSURE_SENSOR_V_MIN) / (PRESSURE_SENSOR_V_MAX - PRESSURE_SENSOR_V_MIN);
  float bar = ratio * PRESSURE_SENSOR_BAR_MAX;
  if (bar < 0) bar = 0;
  return bar;
}

float readConcentration(int pin) {
  int raw = analogRead(pin);
  float v = analogToVoltage(raw);
  float v_clamped = constrain(v, CONC_SENSOR_V_MIN, CONC_SENSOR_V_MAX);
  float ratio = (v_clamped - CONC_SENSOR_V_MIN) / (CONC_SENSOR_V_MAX - CONC_SENSOR_V_MIN);
  float conc = ratio * CONC_SENSOR_UNIT_MAX;
  if (conc < 0) conc = 0;
  return conc;
}

// --- Command Processing ---
void processCommand(String cmd) {
  Serial.print("COMMAND_RECEIVED: ");
  Serial.println(cmd);
  lastCommandTime = millis();

  if (cmd == "OPEN") openValve();
  else if (cmd == "CLOSE") closeValve();
  else if (cmd == "STATUS") sendStatus();
  else if (cmd == "INFO") sendStartupInfo();
  else if (cmd == "PING") Serial.println("PONG");
  else if (cmd == "FORCE_OPEN") openValve(true);
  else if (cmd == "RESET_EMERGENCY") {
    emergencyMode = false;
    Serial.println("EVENT: Emergency mode reset successfully.");
  } else {
    Serial.println("ERROR: Unknown command");
  }
}

// --- Valve Control ---
void openValve(bool forced) {
  if (emergencyMode && !forced) {
    Serial.println("ERROR: Cannot OPEN — system in EMERGENCY mode.");
    return;
  }

  float p1 = readPressure(PRESSURE1_PIN);
  float p2 = readPressure(PRESSURE2_PIN);
  float c_src = readConcentration(CONC_SRC_PIN);
  float c_dst = readConcentration(CONC_DST_PIN);

  if ((p1 > MAX_PRESSURE_BAR) || (p2 > MAX_PRESSURE_BAR)) {
    Serial.println("ERROR: Overpressure — aborting OPEN.");
    emergencyMode = true;
    return;
  }

  if (c_src < MIN_SRC_CONCENTRATION) {
    Serial.println("ERROR: Source concentration too low.");
    return;
  }

  if (c_dst > MAX_DST_CONCENTRATION) {
    Serial.println("ERROR: Destination concentration too high.");
    return;
  }

  valveState = true;
  digitalWrite(RELAY_PIN, HIGH);
  digitalWrite(STATUS_LED, HIGH);
  valveOpenTimestamp = millis();
  Serial.println("VALVE_OPENED");
}

void closeValve() {
  if (!valveState) {
    Serial.println("VALVE_ALREADY_CLOSED");
    return;
  }

  valveState = false;
  digitalWrite(RELAY_PIN, LOW);
  digitalWrite(STATUS_LED, LOW);
  unsigned long runMs = millis() - valveOpenTimestamp;
  if (runMs > 0) totalValveRunMs += runMs;
  Serial.println("VALVE_CLOSED");
}

// --- Telemetry ---
void sendTelemetry() {
  float p1 = readPressure(PRESSURE1_PIN);
  float p2 = readPressure(PRESSURE2_PIN);
  float c_src = readConcentration(CONC_SRC_PIN);
  float c_dst = readConcentration(CONC_DST_PIN);
  unsigned long t = millis() / 1000;

  char buf[200];
  snprintf(buf, sizeof(buf),
           "TELEMETRY:{\"t\":%lu,\"valve\":\"%s\",\"p1\":%.2f,\"p2\":%.2f,\"c_src\":%.2f,\"c_dst\":%.2f,\"em\":%d}",
           t, valveState ? "OPEN" : "CLOSED", p1, p2, c_src, c_dst, emergencyMode ? 1 : 0);
  Serial.println(buf);
}

// --- Safety Check ---
void checkSafetyConditions() {
  float p1 = readPressure(PRESSURE1_PIN);
  float p2 = readPressure(PRESSURE2_PIN);
  float c_src = readConcentration(CONC_SRC_PIN);
  float c_dst = readConcentration(CONC_DST_PIN);

  if ((p1 > MAX_PRESSURE_BAR) || (p2 > MAX_PRESSURE_BAR)) {
    emergencyMode = true;
    if (valveState) closeValve();
    Serial.println("EVENT: OVER_PRESSURE — emergency mode triggered.");
  }

  if ((c_src > CRITICAL_CONCENTRATION) || (c_dst > CRITICAL_CONCENTRATION)) {
    emergencyMode = true;
    if (valveState) closeValve();
    Serial.println("EVENT: CRITICAL_CONCENTRATION — emergency mode triggered.");
  }
}

// --- Status & Info ---
void sendStatus() {
  Serial.println("=== SYSTEM STATUS ===");
  Serial.print("Valve: "); Serial.println(valveState ? "OPEN" : "CLOSED");
  Serial.print("Emergency: "); Serial.println(emergencyMode ? "YES" : "NO");
  Serial.print("Total runtime (s): "); Serial.println(totalValveRunMs / 1000);
  Serial.println("=====================");
}

void sendStartupInfo() {
  Serial.println("=======================================");
  Serial.println(" Smart Water Valve System — Hardware Mode");
  Serial.println(" Baud Rate: 115200");
  Serial.println(" Commands: OPEN, CLOSE, STATUS, INFO, PING, FORCE_OPEN, RESET_EMERGENCY");
  Serial.println(" Safety: Emergency triggers on overpressure or high concentration");
  Serial.println(" Telemetry format: TELEMETRY:{...}");
  Serial.println("=======================================");
}
