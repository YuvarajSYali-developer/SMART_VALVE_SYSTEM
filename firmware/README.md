# 🔌 Arduino Firmware — Smart Water Valve IoT System

## 📋 Overview

This directory contains the Arduino firmware for the Smart Water Valve IoT system. The firmware runs on an **Arduino Uno R3** and handles:

- Real-time sensor monitoring (pressure and concentration)
- Valve control via relay module
- Serial communication with the backend
- Safety logic and emergency shutdown
- Telemetry broadcasting

---

## 🛠️ Hardware Requirements

### Components
- **Arduino Uno R3** (ATmega328P)
- **Relay Module** (5V, active HIGH)
- **12V Normally Closed Solenoid Valve**
- **2× Pressure Sensors** (0-10 bar, 0.5-4.5V output)
- **2× Concentration Sensors** (analog output)
- **Status LED** (built-in on Pin 13)
- **12V Power Supply** (for solenoid)
- **5V Power Supply** (for Arduino via USB or external)

### Pin Configuration

| Component | Arduino Pin |
|-----------|-------------|
| Relay Control | Digital Pin 7 |
| Status LED | Digital Pin 13 (built-in) |
| Pressure Sensor 1 | Analog Pin A0 |
| Pressure Sensor 2 | Analog Pin A1 |
| Concentration Sensor (Source) | Analog Pin A2 |
| Concentration Sensor (Destination) | Analog Pin A3 |

---

## 🔌 Wiring Diagram

```
Arduino Uno R3
┌─────────────────────┐
│                     │
│  A0 ←─ Pressure 1   │
│  A1 ←─ Pressure 2   │
│  A2 ←─ Conc. Source │
│  A3 ←─ Conc. Dest.  │
│                     │
│  D7 ──→ Relay IN    │
│  D13 ──→ Status LED │
│                     │
│  5V ──→ Sensors VCC │
│  GND ──→ Common GND │
└─────────────────────┘

Relay Module
┌──────────────┐
│ VCC ← 5V     │
│ GND ← GND    │
│ IN  ← D7     │
│              │
│ COM ←─ 12V+  │
│ NC  ─→ Valve+│
└──────────────┘

Solenoid Valve
  Valve- ← 12V GND
```

---

## 📦 Installation

### Step 1: Install Arduino IDE
Download and install from: https://www.arduino.cc/en/software

### Step 2: Open the Firmware
1. Navigate to `firmware/smart_water_valve/`
2. Open `smart_water_valve.ino` in Arduino IDE

### Step 3: Configure Board
- **Board:** Arduino Uno
- **Port:** Select the appropriate COM port (Windows) or `/dev/ttyUSB0` (Linux)
- **Baud Rate:** 115200

### Step 4: Upload
1. Connect Arduino via USB
2. Click **Upload** (→) button
3. Wait for "Done uploading" message

---

## 🚀 Usage

### Open Serial Monitor
1. In Arduino IDE, click **Tools → Serial Monitor**
2. Set baud rate to **115200**
3. Set line ending to **Newline** or **Both NL & CR**

### Available Commands

| Command | Description | Required Role |
|---------|-------------|---------------|
| `OPEN` | Open the valve (with safety checks) | Operator/Admin |
| `CLOSE` | Close the valve | Any |
| `FORCE_OPEN` | Open valve bypassing emergency mode | Admin only |
| `STATUS` | Get current system status | Any |
| `INFO` | Display system information | Any |
| `PING` | Test connection (returns PONG) | Any |
| `RESET_EMERGENCY` | Clear emergency mode | Admin |

### Command Examples

```
OPEN
> COMMAND_RECEIVED: OPEN
> VALVE_OPENED

STATUS
> === SYSTEM STATUS ===
> Valve: OPEN
> Emergency: NO
> Total runtime (s): 145
> =====================

PING
> PONG
```

---

## 📡 Telemetry Format

The firmware sends telemetry data **every 1 second** in JSON format:

```json
TELEMETRY:{"t":1234,"valve":"OPEN","p1":3.45,"p2":3.21,"c_src":140.2,"c_dst":230.1,"em":0}
```

### Telemetry Fields

| Field | Type | Description |
|-------|------|-------------|
| `t` | integer | Timestamp (seconds since boot) |
| `valve` | string | Valve state: `OPEN` or `CLOSED` |
| `p1` | float | Pressure sensor 1 (bar) |
| `p2` | float | Pressure sensor 2 (bar) |
| `c_src` | float | Source concentration (units) |
| `c_dst` | float | Destination concentration (units) |
| `em` | integer | Emergency mode: `0` (normal) or `1` (emergency) |

---

## 🛡️ Safety Features

### Emergency Triggers

The system automatically enters **emergency mode** and closes the valve when:

1. **Overpressure:** Any pressure sensor reads > **6.0 bar**
2. **Critical Concentration:** Any concentration sensor reads > **500 units**
3. **Timeout:** Valve remains open for > **30 minutes**

### Emergency Mode Behavior
- Valve **immediately closes**
- `OPEN` commands are **rejected**
- LED **turns off**
- Requires **manual reset** via `RESET_EMERGENCY` command
- Only `FORCE_OPEN` (admin) can override

### Validation Checks (OPEN command)
- Pressure must be ≤ 6.0 bar
- Source concentration must be ≥ 10 units
- Destination concentration must be ≤ 400 units
- System must not be in emergency mode

---

## 🔧 Calibration

### Pressure Sensors
Edit these constants in the code to match your sensor specifications:

```cpp
const float PRESSURE_SENSOR_V_MIN = 0.5;     // Voltage at 0 bar
const float PRESSURE_SENSOR_V_MAX = 4.5;     // Voltage at full scale
const float PRESSURE_SENSOR_BAR_MAX = 10.0;  // Full scale pressure (bar)
```

### Concentration Sensors
```cpp
const float CONC_SENSOR_V_MIN = 0.0;         // Voltage at 0 concentration
const float CONC_SENSOR_V_MAX = 5.0;         // Voltage at full scale
const float CONC_SENSOR_UNIT_MAX = 1000.0;   // Full scale concentration
```

### Safety Thresholds
```cpp
const float MAX_PRESSURE_BAR = 6.0;              // Emergency pressure limit
const float CRITICAL_CONCENTRATION = 500.0;      // Emergency concentration limit
const float MIN_SRC_CONCENTRATION = 10.0;        // Minimum source concentration
const float MAX_DST_CONCENTRATION = 400.0;       // Maximum destination concentration
const unsigned long SAFETY_TIMEOUT_MS = 1800000; // 30 minutes in milliseconds
```

---

## 🧪 Testing

### Test 1: Basic Communication
```
1. Open Serial Monitor
2. Type: PING
3. Expected: PONG
```

### Test 2: Valve Control
```
1. Type: OPEN
2. Observe: Relay clicks, LED turns on
3. Type: STATUS
4. Verify: Valve: OPEN
5. Type: CLOSE
6. Observe: Relay clicks, LED turns off
```

### Test 3: Telemetry Stream
```
1. Observe automatic telemetry every second
2. Verify JSON format is correct
3. Check sensor values are reasonable
```

### Test 4: Emergency Mode (Optional)
```
⚠️ WARNING: Only for testing! May trigger false emergency.

1. Temporarily modify MAX_PRESSURE_BAR to a low value (e.g., 1.0)
2. Upload firmware
3. Type: OPEN
4. System should enter emergency mode
5. Verify OPEN is rejected
6. Type: RESET_EMERGENCY
7. Restore original MAX_PRESSURE_BAR value
```

---

## 🐛 Troubleshooting

### Issue: No telemetry output
**Solution:** Check baud rate is set to 115200

### Issue: Valve doesn't open
**Possible causes:**
- System in emergency mode → Send `RESET_EMERGENCY`
- Pressure too high → Check sensor readings with `STATUS`
- Relay wiring incorrect → Verify Pin 7 connection
- Power supply insufficient → Use external 12V for solenoid

### Issue: Relay clicks but valve doesn't move
**Solution:** Check 12V power supply to solenoid valve

### Issue: Erratic sensor readings
**Solution:**
- Add 0.1µF capacitor between sensor output and GND
- Check sensor power supply stability
- Verify sensor is within operating range

### Issue: Arduino resets randomly
**Solution:**
- Use separate power supply for Arduino (not USB)
- Add flyback diode across relay coil
- Check for ground loops

---

## 📁 File Structure

```
firmware/
├── README.md                          # This file
└── smart_water_valve/
    └── smart_water_valve.ino          # Main Arduino sketch
```

---

## 🔗 Integration with Backend

The backend (`serial_manager.py`) connects to this Arduino via serial port:

1. **Auto-detection:** Searches for Arduino by VID/PID or port name
2. **Command sending:** Backend sends commands like `OPEN\n`
3. **Telemetry parsing:** Backend reads `TELEMETRY:` lines and parses JSON
4. **WebSocket broadcast:** Telemetry is pushed to frontend clients
5. **Database storage:** All telemetry is logged to SQLite

---

## 📝 Notes

- **No external libraries required** — Uses only built-in Arduino functions
- **Non-blocking design** — Serial reading and telemetry are asynchronous
- **Memory efficient** — Uses `snprintf()` for JSON formatting
- **Production-ready** — Includes error handling and safety checks

---

## 🔄 Next Steps

1. ✅ Flash firmware to Arduino
2. ⏭️ Set up backend serial manager (see `../backend/README.md`)
3. ⏭️ Connect to web dashboard for remote control

---

**Built with 💧 for Smart Water Management**
