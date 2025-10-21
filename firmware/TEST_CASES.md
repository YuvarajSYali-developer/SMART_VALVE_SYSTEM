# Arduino Firmware Test Cases

## Hardware Requirements
- Arduino Uno R3
- USB cable for serial communication
- Arduino IDE or Serial Monitor
- Optional: Actual sensors for hardware integration testing

## Test Environment Setup
1. Upload `smart_water_valve.ino` to Arduino Uno
2. Open Serial Monitor at 115200 baud
3. Ensure "Both NL & CR" line ending is selected

---

## Test Suite

### Test 1: System Initialization
**Objective:** Verify Arduino starts correctly and sends startup info

**Steps:**
1. Upload sketch and open Serial Monitor
2. Press reset button on Arduino

**Expected Output:**
```
EVENT: Smart Water Valve System Started
INFO: Valve=CLOSED, Emergency=NO
```

**Status:** [ ] Pass [ ] Fail

---

### Test 2: PING Command
**Objective:** Verify basic communication

**Steps:**
1. Send command: `PING`

**Expected Output:**
```
PONG
```

**Status:** [ ] Pass [ ] Fail

---

### Test 3: STATUS Command
**Objective:** Verify status reporting

**Steps:**
1. Send command: `STATUS`

**Expected Output:**
```
STATUS: Valve=CLOSED, Emergency=NO, Uptime=XXXXs
```

**Status:** [ ] Pass [ ] Fail

---

### Test 4: INFO Command
**Objective:** Verify system information reporting

**Steps:**
1. Send command: `INFO`

**Expected Output:**
```
SYSTEM_INFO:{"version":"1.0","uptime":XXXX,"valve":"CLOSED","em":0,"runtime_ms":0}
```

**Status:** [ ] Pass [ ] Fail

---

### Test 5: Telemetry Stream
**Objective:** Verify continuous telemetry transmission

**Steps:**
1. Wait and observe Serial Monitor for 5 seconds

**Expected Output:** Telemetry messages every 1 second:
```
TELEMETRY:{"t":XXXXXXX,"valve":"CLOSED","p1":X.XX,"p2":X.XX,"c_src":XXX.X,"c_dst":XXX.X,"em":0}
```

**Validation:**
- Messages arrive every ~1 second
- JSON format is valid
- All fields present: t, valve, p1, p2, c_src, c_dst, em

**Status:** [ ] Pass [ ] Fail

---

### Test 6: OPEN Command (Normal Conditions)
**Objective:** Verify valve opens under safe conditions

**Steps:**
1. Send command: `OPEN`
2. Observe LED on pin 13 (should turn ON)
3. Observe relay state

**Expected Output:**
```
VALVE_OPENED
```

**Validation:**
- Status LED turns ON
- Telemetry shows valve="OPEN"
- Relay activates (if connected)

**Status:** [ ] Pass [ ] Fail

---

### Test 7: CLOSE Command
**Objective:** Verify valve closes

**Steps:**
1. Ensure valve is OPEN (from Test 6)
2. Send command: `CLOSE`
3. Observe LED on pin 13 (should turn OFF)

**Expected Output:**
```
VALVE_CLOSED
```

**Validation:**
- Status LED turns OFF
- Telemetry shows valve="CLOSED"
- Relay deactivates (if connected)

**Status:** [ ] Pass [ ] Fail

---

### Test 8: Double CLOSE Command
**Objective:** Verify idempotent CLOSE behavior

**Steps:**
1. Ensure valve is CLOSED
2. Send command: `CLOSE`

**Expected Output:**
```
ALREADY_CLOSED
```

**Status:** [ ] Pass [ ] Fail

---

### Test 9: Emergency Mode - High Pressure
**Objective:** Verify emergency shutdown on overpressure

**Steps:**
1. Open valve with `OPEN`
2. Simulate high pressure by temporarily modifying code or using voltage source
3. Set A0 or A1 to voltage equivalent to >6 bar

**Expected Output:**
```
EVENT: EMERGENCY - Overpressure detected
VALVE_CLOSED
```

**Validation:**
- Valve automatically closes
- Emergency mode activated (em=1 in telemetry)
- Cannot reopen with normal OPEN command

**Status:** [ ] Pass [ ] Fail [ ] N/A (Hardware not available)

---

### Test 10: Emergency Mode - Critical Concentration
**Objective:** Verify emergency shutdown on critical concentration

**Steps:**
1. Open valve with `OPEN`
2. Simulate critical concentration >500 units on A2 or A3

**Expected Output:**
```
EVENT: EMERGENCY - Critical concentration detected
VALVE_CLOSED
```

**Validation:**
- Valve automatically closes
- Emergency mode activated (em=1 in telemetry)

**Status:** [ ] Pass [ ] Fail [ ] N/A (Hardware not available)

---

### Test 11: FORCE_OPEN Command
**Objective:** Verify force open bypasses safety checks

**Steps:**
1. Trigger emergency mode (Test 9 or 10)
2. Send command: `FORCE_OPEN`

**Expected Output:**
```
VALVE_OPENED (forced)
```

**Validation:**
- Valve opens despite emergency mode
- Emergency flag remains set (em=1)

**Status:** [ ] Pass [ ] Fail [ ] N/A (Hardware not available)

---

### Test 12: RESET_EMERGENCY Command
**Objective:** Verify emergency mode can be reset

**Steps:**
1. Trigger emergency mode
2. Ensure safe conditions restored
3. Send command: `RESET_EMERGENCY`

**Expected Output:**
```
EVENT: Emergency mode reset
```

**Validation:**
- Emergency flag clears (em=0 in telemetry)
- Normal OPEN command works again

**Status:** [ ] Pass [ ] Fail [ ] N/A (Hardware not available)

---

### Test 13: Auto-Close Timer
**Objective:** Verify valve auto-closes after 30 minutes

**Steps:**
1. Open valve with `OPEN`
2. Wait 30 minutes (or modify SAFETY_TIMEOUT_MS to shorter duration for testing)

**Expected Output:**
```
EVENT: Auto-close safety timeout (30 min)
VALVE_CLOSED
```

**Validation:**
- Valve automatically closes after timeout
- Emergency mode NOT activated
- Can reopen immediately

**Status:** [ ] Pass [ ] Fail [ ] N/A (Too time-consuming)

---

### Test 14: Invalid Command
**Objective:** Verify handling of unknown commands

**Steps:**
1. Send command: `INVALID_COMMAND`

**Expected Output:**
```
ERROR: Unknown command
```

**Status:** [ ] Pass [ ] Fail

---

### Test 15: Sensor Reading Consistency
**Objective:** Verify sensor readings are within expected ranges

**Steps:**
1. Observe telemetry for 10 seconds
2. Record values for p1, p2, c_src, c_dst

**Validation:**
- No negative values
- Values within reasonable ranges (0-10 bar, 0-1000 units)
- No sudden impossible jumps
- Pressure readings show some variation (not stuck at 0)

**Status:** [ ] Pass [ ] Fail [ ] N/A (Sensors not connected)

---

### Test 16: Serial Communication Stability
**Objective:** Verify stable long-term operation

**Steps:**
1. Let system run for 5 minutes
2. Send various commands intermittently

**Validation:**
- No communication errors
- Telemetry continues regularly
- Commands processed correctly
- No buffer overflows or crashes

**Status:** [ ] Pass [ ] Fail

---

### Test 17: LED Status Indicator
**Objective:** Verify LED correctly indicates valve state

**Steps:**
1. Send `OPEN` - LED should be ON
2. Send `CLOSE` - LED should be OFF
3. Repeat 3 times

**Validation:**
- LED state always matches valve state
- LED blinks on startup (3 times)

**Status:** [ ] Pass [ ] Fail

---

## Test Summary

**Total Tests:** 17  
**Passed:** ___  
**Failed:** ___  
**N/A (Hardware):** ___  

**Date Tested:** ___________  
**Tester:** ___________  
**Arduino Board:** ___________  
**Sketch Version:** 1.0  

---

## Notes

Add any observations, issues, or additional comments:

```
[Your notes here]
```

---

## Known Issues / Limitations

1. Auto-close timer test requires 30 minutes (modify SAFETY_TIMEOUT_MS for faster testing)
2. Emergency tests require actual sensors or voltage simulation
3. Sensor calibration values are examples and need adjustment for specific hardware
