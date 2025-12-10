# 💧 Smart Water Valve IoT System

An end-to-end IoT solution for intelligent water valve control with real-time monitoring, safety automation, and web-based dashboard.

![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Arduino](https://img.shields.io/badge/Arduino-Uno%20R3-00979D?logo=arduino)
![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python)
![React](https://img.shields.io/badge/React-18-61DAFB?logo=react)

---

## 🎯 Overview

This system monitors **pressure** and **concentration** levels in real-time, automatically shuts down on critical thresholds, and provides remote control through a modern web dashboard.

### Architecture
```
┌──────────────┐      Serial       ┌──────────────┐     WebSocket      ┌──────────────┐
│   Arduino    │ ←─────────────→   │   FastAPI    │ ←───────────────→  │    React     │
│   Hardware   │    115200 baud    │   Backend    │   Real-time Data   │  Dashboard   │
└──────────────┘                   └──────────────┘                     └──────────────┘
       ↓                                   ↓
  Sensors/Relay                      SQLite Database
```

---

## ✨ Key Features

- 🚨 **Safety First:** Auto-shutdown on overpressure (>6 bar) or critical concentration (>500 units)
- 📊 **Real-Time Monitoring:** Live telemetry streaming every second
- 🎛️ **Remote Control:** Web dashboard with role-based access (Admin/Operator/Viewer)
- 📈 **Analytics:** Historical data, trends, and metrics
- 🔒 **Secure:** JWT authentication and server-side validation
- 🧪 **Testing Ready:** Serial simulator for development without hardware

---

## 📦 Components

### ✅ Firmware (Complete)
- **Platform:** Arduino Uno R3
- **Language:** C++ (Arduino)
- **Location:** [`firmware/smart_water_valve/`](./firmware/smart_water_valve/)
- **Status:** ✅ Production-ready

**Features:**
- 7 serial commands (OPEN, CLOSE, STATUS, etc.)
- JSON telemetry format
- Emergency auto-shutdown
- 30-minute safety timeout

**[View Firmware Documentation →](./firmware/README.md)**

---

### ✅ Backend (Complete)
- **Framework:** FastAPI
- **Language:** Python 3.11
- **Database:** SQLite with SQLAlchemy ORM
- **Location:** [`backend/app/`](./backend/app/)
- **Status:** ✅ Production-ready

**Features:**
- Serial manager for Arduino communication
- REST API endpoints (auth, valve, telemetry)
- WebSocket telemetry broadcast
- JWT authentication with role-based access
- Safety rules engine & alert system
- Database seeding & migrations

**[View Backend Documentation →](./backend/README.md)**

---

### ✅ Frontend (Complete)
- **Framework:** React 18 + TypeScript
- **UI Library:** TailwindCSS
- **Build Tool:** Vite
- **Location:** [`frontend/src/`](./frontend/src/)
- **Status:** ✅ Production-ready

**Features:**
- Live sensor dashboard with WebSocket
- Valve control panel with role-based access
- Historical charts (Recharts)
- Alert management with acknowledgment
- System metrics and analytics
- Responsive mobile-friendly design

**[View Frontend Documentation →](./frontend/README.md)**

---

## 🚀 Quick Start

### 1. Flash Arduino Firmware

```bash
# Navigate to firmware directory
cd firmware/smart_water_valve/

# Open in Arduino IDE
# Set Board: Arduino Uno
# Set Baud Rate: 115200
# Click Upload
```

**Test via Serial Monitor:**
```
PING       → Returns PONG
STATUS     → Shows valve state
OPEN       → Opens valve (if safe)
CLOSE      → Closes valve
```

**[Complete Firmware Guide →](./firmware/README.md)**

---

### 2. Set Up Backend

```bash
cd backend/

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/seed_data.py

# Start server
uvicorn app.main:app --reload
```

**Backend available at:** http://localhost:8000  
**API docs:** http://localhost:8000/docs

**Default login:**
- Username: `admin`
- Password: `admin123`

---

### 3. Launch Frontend

```bash
cd frontend/

# Install dependencies
npm install

# Start development server
npm run dev
```

**Dashboard available at:** http://localhost:3000

**Login credentials:**
- Email: `yuvarajyali@gmail.com`
- Password: `smart_valve_system`

---

## 🛡️ Safety Features

### Emergency Triggers
The system automatically enters emergency mode and closes the valve when:

| Condition | Threshold | Action |
|-----------|-----------|--------|
| **Overpressure** | > 6.0 bar | Immediate shutdown |
| **Critical Concentration** | > 500 units | Immediate shutdown |
| **Timeout** | > 30 minutes open | Auto-close |

### Manual Reset Required
After an emergency, the valve cannot be reopened until:
1. Emergency condition is resolved
2. Admin sends `RESET_EMERGENCY` command
3. (or) Admin uses `FORCE_OPEN` command

---

## 📡 Telemetry Format

Real-time data is broadcast every second:

```json
{
  "t": 1234,           // Timestamp (seconds since boot)
  "valve": "OPEN",     // Valve state: OPEN or CLOSED
  "p1": 3.45,          // Pressure sensor 1 (bar)
  "p2": 3.21,          // Pressure sensor 2 (bar)
  "c_src": 140.2,      // Source concentration (units)
  "c_dst": 230.1,      // Destination concentration (units)
  "em": 0              // Emergency mode: 0=normal, 1=emergency
}
```

---

## 🧪 Development Without Hardware

Use the **serial simulator** to develop backend and frontend without physical Arduino:

```bash
cd backend/
python scripts/serial_simulator.py
```

The simulator:
- Emits realistic telemetry data
- Responds to all commands
- Simulates emergency conditions
- Connects via virtual serial port

---

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [PROJECT_PROMPT.md](./PROJECT_PROMPT.md) | Complete AI build blueprint with all 5 prompts |
| [firmware/README.md](./firmware/README.md) | Arduino setup, wiring, calibration, troubleshooting |
| backend/README.md | Backend API documentation (coming soon) |
| frontend/README.md | Frontend component guide (coming soon) |

---

## 🛠️ Hardware Requirements

### Core Components
- **Arduino Uno R3** (~$25)
- **5V Relay Module** (~$3)
- **12V Solenoid Valve** (Normally Closed) (~$15)
- **2× Pressure Sensors** (0-10 bar, analog output) (~$20 each)
- **2× Concentration Sensors** (analog output) (~$15 each)
- **12V Power Supply** (~$10)
- **Breadboard & Jumper Wires** (~$10)

**Total Estimated Cost:** ~$120

### Pin Connections
```
Arduino Pin    →    Component
─────────────────────────────────
A0             →    Pressure Sensor 1
A1             →    Pressure Sensor 2
A2             →    Concentration Sensor (Source)
A3             →    Concentration Sensor (Destination)
D7             →    Relay Module
D13            →    Status LED (built-in)
5V             →    Sensor Power
GND            →    Common Ground
```

---

## 🤝 Contributing

This is a personal IoT project, but suggestions and improvements are welcome!

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly (especially safety features)
5. Submit a pull request

---

## 📄 License

MIT License - Feel free to use for personal or commercial projects.

---

## 🆘 Support

- **Hardware Issues:** See [firmware/README.md](./firmware/README.md#troubleshooting)
- **Backend Issues:** Check backend logs and `/healthz` endpoint
- **Frontend Issues:** Check browser console for WebSocket errors

---

## 🎓 Learn More

This project demonstrates:
- IoT hardware integration with Arduino
- Real-time serial communication
- RESTful API design with FastAPI
- WebSocket for live data streaming
- Modern React with TypeScript
- SQLite database design
- Safety-critical system design

Perfect for learning **full-stack IoT development**!

---

**Built with 💧 for Smart Water Management**

*Last Updated: 2025-10-21*
