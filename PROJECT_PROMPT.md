# 💧 SMART WATER VALVE IoT SYSTEM — FULL PROJECT PROMPT KIT

**End-to-End AI Build Blueprint**

---

## 🧠 PROJECT OVERVIEW

### Goal
To build a complete IoT-based Smart Water Valve system that monitors pressure and concentration levels, ensures safety automation, and provides real-time control and analytics through a web dashboard.

### Architecture
```
Arduino (IoT) → FastAPI Backend (Serial + WebSocket) → SQLite Database → React Frontend (Dashboard)
```

### Key Features
- ✅ Real-time telemetry streaming
- 🚨 Auto emergency shutdown on critical thresholds
- 👥 Role-based control (admin/operator/viewer)
- 📊 Telemetry visualization + history logs
- 🧪 Local mock simulator for testing
- 🔒 Secure, resilient, and maintainable structure

### Safety Priorities
- **Max pressure:** 6.0 bar
- **Critical concentration:** 500 units
- **Auto close** after 30 min continuous open
- **Manual reset** required after emergency
- **Server-side validation** even if client requests are safe

---

## ⚙️ PROMPT 1 — IoT FIRMWARE (Arduino Simulation + Real Mode)

### 🎯 Objective
Generate the Arduino firmware that drives the IoT valve and sends telemetry.

### Context
You are an embedded firmware expert. Build the Arduino Uno (ATmega328P) firmware for a Smart Water Valve IoT system with the following:

### Hardware Configuration
- **Relay (Pin 7)** → Controls solenoid valve
- **LED (Pin 13)** → Valve indicator
- **Pressure sensors** → A0, A1
- **Concentration sensors** → A2, A3

### Core Requirements

#### Serial Communication (115200 baud)
**Commands:**
- `OPEN`
- `CLOSE`
- `STATUS`
- `INFO`
- `PING`
- `FORCE_OPEN`
- `RESET_EMERGENCY`

**Telemetry format (every 1s):**
```json
TELEMETRY:{"t":1690000000,"valve":"OPEN","p1":3.2,"p2":2.9,"c_src":120.3,"c_dst":110.5,"em":0}
```

#### Safety Logic
**Emergency triggers:**
- Pressure > 6.0 bar
- Concentration > 500 units
- Emergency requires manual reset
- Auto-close after 30 minutes open
- LED blinks on open, stays on if active

#### Simulation Mode
When no sensors are attached, generate random:
- **Pressure:** 0–8 bar
- **Concentration:** 0–1000 units
- Controlled via `#define SIMULATION_MODE true`

### Structure
**Functions:**
- `readSensors()`
- `checkSafety()`
- `sendTelemetry()`
- `processCommand()`

Use `snprintf()` for compact JSON telemetry.

Include full code, properly commented.

### Output
- Single `.ino` file ready for upload
- Self-contained and clean (no external libraries)
- Tested serial output with sample telemetry

### 📂 Implementation Reference
**The complete Arduino firmware is available at:**
- **File:** [`firmware/smart_water_valve/smart_water_valve.ino`](./firmware/smart_water_valve/smart_water_valve.ino)
- **Documentation:** [`firmware/README.md`](./firmware/README.md)

**Quick Start:**
1. Navigate to `firmware/smart_water_valve/`
2. Open `smart_water_valve.ino` in Arduino IDE
3. Select **Board: Arduino Uno**, **Baud: 115200**
4. Click **Upload**
5. Open **Serial Monitor** and test with commands: `PING`, `STATUS`, `INFO`

**Hardware Wiring:**
```
A0 → Pressure Sensor 1
A1 → Pressure Sensor 2
A2 → Concentration Sensor (Source)
A3 → Concentration Sensor (Destination)
D7 → Relay Module (controls solenoid)
D13 → Status LED (built-in)
```

**Example Telemetry Output:**
```
TELEMETRY:{"t":145,"valve":"CLOSED","p1":2.34,"p2":2.21,"c_src":85.4,"c_dst":112.3,"em":0}
TELEMETRY:{"t":146,"valve":"CLOSED","p1":2.35,"p2":2.22,"c_src":85.6,"c_dst":112.5,"em":0}
```

See [`firmware/README.md`](./firmware/README.md) for complete setup guide, calibration instructions, and troubleshooting.

---

## 🧩 PROMPT 2 — BACKEND (FastAPI + Serial + WebSocket)

### 🎯 Objective
Generate the backend that connects to Arduino, stores telemetry, and manages control APIs.

### Context
You are a senior backend engineer. Create a complete FastAPI backend for the Smart Water Valve IoT System.

### Tech Stack
- Python 3.11
- FastAPI + Uvicorn
- SQLite (SQLAlchemy ORM)
- WebSocket for telemetry push
- PySerial for Arduino communication
- JWT authentication (admin/operator/viewer roles)

### Core Functions

#### Serial Manager
- Detect Arduino by VID/PID or port name
- Read telemetry lines (`TELEMETRY:` prefix)
- Parse JSON → store in database → broadcast via WebSocket
- Commands (`OPEN`, `CLOSE`, etc.) sent via serial with 3s timeout
- Auto reconnect on disconnect

#### REST Endpoints
- `POST /api/auth/login` → returns JWT
- `GET /api/status` → last telemetry snapshot
- `POST /api/valve/open` → operator/admin only
- `POST /api/valve/close`
- `POST /api/valve/force_open` → admin only
- `GET /api/history` → telemetry history
- `GET /api/metrics` → aggregates (avg pressure, open time)
- `POST /api/alerts/ack` → acknowledge alert

#### WebSocket
- `/ws/telemetry` endpoint
- Push telemetry JSON in real-time to clients with valid JWT
- Handles disconnects and heartbeats

#### Safety Logic
- Backend enforces thresholds before opening valve
- If unsafe telemetry received, auto CLOSE and log emergency alert

### Deliverables

#### Folder Structure
```
backend/
  ├── app/
  │   ├── main.py
  │   ├── serial_manager.py
  │   ├── ws_manager.py
  │   ├── db/
  │   │   ├── models.py
  │   │   └── session.py
  │   ├── api/
  │   │   ├── valve.py
  │   │   ├── telemetry.py
  │   │   └── auth.py
  │   ├── services/
  │   │   ├── rules_engine.py
  │   │   └── alerts.py
  │   └── utils/
  │       ├── logger.py
  │       └── security.py
  └── requirements.txt
```

#### README
- Include command: `uvicorn app.main:app --reload`

---

## 🧱 PROMPT 3 — DATABASE (Schema + ORM + Queries)

### 🎯 Objective
Generate all tables, models, and seed data for the IoT system.

### Context
You are a database architect. Design and generate a SQLite database schema with ORM models.

### Tables

#### `telemetry`
- `id` (PK)
- `ts_utc` (INTEGER)
- `valve_state` (TEXT)
- `p1`, `p2`, `c_src`, `c_dst` (REAL)
- `em` (INTEGER)
- `raw_line` (TEXT)

#### `valve_operations`
- `id`, `ts_utc`, `command`, `issuer_user`, `result`, `message`

#### `system_alerts`
- `id`, `ts_utc`, `alert_type`, `message`, `priority`, `acknowledged` (0/1), `metadata` (JSON)

#### `users`
- `id`, `username`, `password_hash`, `role`, `created_at`

#### `rules`
- `id`, `name`, `json_config`, `last_updated`

#### `settings`
- `key` (PK), `value` (TEXT)

### ORM and Migrations
- SQLAlchemy ORM + Alembic migrations
- **Indexes:** `telemetry(ts_utc)`, `telemetry(valve_state)`
- Pydantic schemas for API responses

### Seed Data

#### Default admin user:
```json
{ "username": "admin", "password": "admin123", "role": "admin" }
```

#### Default thresholds in rules:
- Max pressure: 6 bar
- Critical concentration: 500 units
- Daily ops limit: 20

### Deliverables
- SQL schema (`CREATE TABLE`s)
- ORM models in `models.py`
- Migration files (`/migrations/initial.py`)
- Seed script (`seed_data.py`)

#### Example queries:
- Avg. pressure last 24h
- All unacknowledged alerts
- Operation count by user/day

---

## 🖥️ PROMPT 4 — FRONTEND (React + TypeScript + Tailwind + WS)

### 🎯 Objective
Generate the interactive dashboard UI.

### Context
You are a frontend architect. Build a complete React + TypeScript (Vite) dashboard app.

### Stack
- React 18 + TypeScript
- TailwindCSS + shadcn/ui
- React Query for API
- WebSocket hook for live telemetry
- Recharts for graphs

### Pages

#### Login
- Username/password
- Auth via `/api/auth/login`
- JWT stored in memory

#### Dashboard
- **Status Card** → valve state, emergency
- **Live Sensor Panel** → p1, p2, c_src, c_dst (auto-updating)
- **Control Panel** → OPEN, CLOSE, FORCE_OPEN (role-based)
- **Alerts Panel** → active alerts + acknowledge
- **History Chart** → last 10 mins trends
- **Metrics Panel** → uptime, avg. runtime, op count
- **Theme toggle** (dark/light)

### Logic
- WebSocket reconnect with exponential backoff
- Disable controls on emergency
- Confirm modal before OPEN/FORCE_OPEN
- Accessible and mobile-friendly

### Deliverables

#### Directory Structure
```
frontend/
  ├── src/
  │   ├── pages/
  │   │   ├── Login.tsx
  │   │   └── Dashboard.tsx
  │   ├── components/
  │   │   ├── StatusCard.tsx
  │   │   ├── ControlPanel.tsx
  │   │   ├── AlertsPanel.tsx
  │   │   ├── HistoryChart.tsx
  │   │   └── MetricsCard.tsx
  │   ├── hooks/
  │   │   ├── useAuth.ts
  │   │   ├── useTelemetryWS.ts
  │   │   └── useApi.ts
  │   └── api/client.ts
  └── vite.config.ts
```

#### README
- Build/run steps: `npm install && npm run dev`

---

## 🔗 PROMPT 5 — INTEGRATION & DEPLOYMENT (Full Stack)

### 🎯 Objective
Connect everything, provide simulator, and enable easy testing + deployment.

### Context
You are an IoT integration engineer. Produce a full end-to-end connection and deployment setup for the Smart Water Valve system.

### Components

#### Serial Manager
- Runs continuously, connects to Arduino or simulator
- Parses telemetry lines → pushes to WebSocket clients and DB
- Sends commands with lock to avoid overlap
- Heartbeat every 10s

#### Serial Simulator
- Python script that emits random telemetry every second
- Responds to commands (OPEN, CLOSE, etc.)
- Used for backend/frontend development when hardware is absent

#### Docker Compose Setup
```yaml
version: "3.8"
services:
  backend:
    build: ./backend
    ports: ["8000:8000"]
    volumes: ["./db/sqlite:/app/data"]
  frontend:
    build: ./frontend
    ports: ["3000:3000"]
  serial-sim:
    build: ./backend
    command: ["python", "scripts/serial_simulator.py"]
```

`.env.dev` with `JWT_SECRET`, `DB_PATH`, `ARDUINO_PORT`.

### Security & Monitoring
- TLS-ready (nginx reverse proxy optional)
- `/healthz` endpoint for backend
- Logs in JSON format
- Alerts persisted and optionally emailed

### Deliverables
- `serial_manager.py`
- `serial_simulator.py`
- `docker-compose.yml`
- `.env.example`

#### README explaining:
- How to flash Arduino firmware
- How to start full stack locally
- How to test safety flow
- How to recover from emergency mode

---

## ✅ USAGE INSTRUCTIONS

You can now paste this entire Prompt Kit into your AI IDE (or each section individually) — it will generate a complete production-grade Smart Water Valve IoT system, from firmware to full-stack dashboard.

### Development Workflow

1. **Start with Prompt 1** → Generate Arduino firmware
2. **Move to Prompt 3** → Set up database schema
3. **Continue with Prompt 2** → Build backend API
4. **Implement Prompt 4** → Create frontend dashboard
5. **Finalize with Prompt 5** → Integration & deployment

### Testing Strategy

- Use serial simulator for development without hardware
- Test safety flows with mock data
- Verify role-based access control
- Validate WebSocket reconnection logic
- Stress test emergency shutdown mechanisms

---

## 📋 PROJECT CHECKLIST

- [x] Arduino firmware flashed and tested ✅
- [x] Backend API endpoints working ✅
- [x] Database schema created and seeded ✅
- [x] WebSocket telemetry streaming ✅
- [x] Authentication and authorization ✅
- [x] Safety thresholds enforced ✅
- [x] Serial simulator functional ✅
- [ ] Frontend dashboard responsive
- [ ] Emergency mode tested end-to-end
- [ ] Docker compose configuration
- [ ] Production deployment ready

---

## 📁 PROJECT STRUCTURE

```
WATER VALVE/
├── PROJECT_PROMPT.md              # This file - Complete project blueprint
│
├── firmware/                      # ✅ IMPLEMENTED
│   ├── README.md                  # Arduino setup guide & troubleshooting
│   └── smart_water_valve/
│       └── smart_water_valve.ino  # Production-ready Arduino code
│
├── backend/                       # ✅ IMPLEMENTED
│   ├── app/
│   │   ├── main.py                # FastAPI application
│   │   ├── serial_manager.py      # Arduino communication
│   │   ├── ws_manager.py          # WebSocket manager
│   │   ├── db/                    # Database models & schemas
│   │   ├── api/                   # REST endpoints
│   │   ├── services/              # Rules engine & alerts
│   │   └── utils/                 # Logger & security
│   ├── scripts/
│   │   ├── seed_data.py           # Database seeding
│   │   └── serial_simulator.py    # Arduino simulator
│   ├── requirements.txt
│   ├── .env.example
│   └── README.md
│
├── frontend/                      # 🔜 TO BE IMPLEMENTED (PROMPT 4)
│   ├── src/
│   │   ├── pages/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── api/
│   └── package.json
│
└── docker-compose.yml             # 🔜 TO BE IMPLEMENTED (PROMPT 5)
```

---

## 🚀 IMPLEMENTED COMPONENTS

### ✅ Firmware (PROMPT 1) — Complete

**Location:** `firmware/smart_water_valve/smart_water_valve.ino`

**Features:**
- ✅ Serial communication at 115200 baud
- ✅ 7 commands: OPEN, CLOSE, STATUS, INFO, PING, FORCE_OPEN, RESET_EMERGENCY
- ✅ JSON telemetry every 1 second
- ✅ Safety logic with emergency shutdown
- ✅ Pressure monitoring (2 sensors on A0, A1)
- ✅ Concentration monitoring (2 sensors on A2, A3)
- ✅ Auto-close after 30 minutes
- ✅ Relay control on Pin 7
- ✅ Status LED on Pin 13

**Documentation:** [`firmware/README.md`](./firmware/README.md)

**Test Command:**
```bash
# Upload to Arduino and test
PING → should return PONG
STATUS → shows valve state and emergency mode
```

---

### ✅ Backend (PROMPT 2 & 3) — Complete

**Location:** `backend/app/`

**Features:**
- ✅ FastAPI application with async support
- ✅ Serial manager with auto-detect & reconnection
- ✅ WebSocket real-time telemetry broadcasting
- ✅ REST API endpoints:
  - Authentication (`/api/auth/login`)
  - Valve control (`/api/valve/open`, `/api/valve/close`, `/api/valve/force_open`)
  - Telemetry & status (`/api/status`, `/api/telemetry/*`)
  - Alerts (`/api/alerts`, `/api/alerts/ack`)
  - Operations history (`/api/operations/history`)
  - Health check (`/api/healthz`)
- ✅ SQLite database with SQLAlchemy ORM
- ✅ 6 database tables (telemetry, valve_operations, system_alerts, users, rules, settings)
- ✅ JWT authentication with role-based access (admin/operator/viewer)
- ✅ Safety rules engine with configurable thresholds
- ✅ Alert service with priority levels
- ✅ Database seeding script with default users
- ✅ Arduino serial simulator for testing
- ✅ Logging to console and file
- ✅ Password hashing (bcrypt)
- ✅ CORS middleware

**Documentation:** [`backend/README.md`](./backend/README.md)

**Quick Start:**
```bash
cd backend
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
python scripts/seed_data.py
uvicorn app.main:app --reload
```

**Default Users:**
- admin / admin123 (admin)
- operator / operator123 (operator)
- viewer / viewer123 (viewer)

**API Docs:** http://localhost:8000/docs

---

## 🔜 NEXT STEPS

1. **Implement Backend (PROMPT 2):**
   - Serial manager to connect to Arduino
   - FastAPI REST endpoints
   - WebSocket for live telemetry
   - SQLite database integration

2. **Create Database Schema (PROMPT 3):**
   - Define tables and ORM models
   - Seed default users and thresholds

3. **Build Frontend (PROMPT 4):**
   - React + TypeScript dashboard
   - Live sensor visualization
   - Role-based valve control

4. **Deploy Full Stack (PROMPT 5):**
   - Docker compose configuration
   - Serial simulator for testing
   - Production deployment guide

---

**Built with 💧 for Smart Water Management**
