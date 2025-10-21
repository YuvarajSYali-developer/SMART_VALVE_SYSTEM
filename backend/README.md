# 🔌 Backend API — Smart Water Valve IoT System

FastAPI backend for Arduino serial communication, real-time telemetry streaming, and valve control.

---

## 📋 Overview

This backend provides:
- **Serial Communication:** Connects to Arduino, reads telemetry, sends commands
- **REST API:** Endpoints for authentication, valve control, and data queries
- **WebSocket:** Real-time telemetry broadcasting to frontend clients
- **Database:** SQLite storage for telemetry, alerts, and operations history
- **Safety Engine:** Validates sensor data and enforces thresholds
- **JWT Authentication:** Role-based access control (admin/operator/viewer)

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate

pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env and set:
# - JWT_SECRET (use a strong secret key)
# - ARDUINO_PORT (e.g., COM3 on Windows, /dev/ttyUSB0 on Linux)
```

### 3. Initialize Database

```bash
python scripts/seed_data.py
```

This creates:
- Database tables
- Default users (admin, operator, viewer)
- Safety rules and thresholds

### 4. Start the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

**Server will be available at:** http://localhost:8000

**API Documentation:** http://localhost:8000/docs

---

## 🧪 Testing Without Hardware

Use the serial simulator to test without physical Arduino:

```bash
python scripts/serial_simulator.py
```

The simulator:
- Emits realistic telemetry every second
- Responds to all commands (OPEN, CLOSE, etc.)
- Simulates emergency conditions randomly
- Perfect for frontend development

---

## 📡 API Endpoints

### Authentication

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/api/auth/login` | Login and get JWT token | No |

**Request Body:**
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "admin",
    "role": "admin",
    "created_at": 1697000000,
    "is_active": true
  }
}
```

---

### Valve Control

| Method | Endpoint | Description | Role Required |
|--------|----------|-------------|---------------|
| POST | `/api/valve/open` | Open valve (with safety checks) | operator, admin |
| POST | `/api/valve/close` | Close valve | any |
| POST | `/api/valve/force_open` | Force open (bypass emergency) | admin |
| POST | `/api/valve/reset_emergency` | Reset emergency mode | admin |

**Example:**
```bash
curl -X POST http://localhost:8000/api/valve/open \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "success": true,
  "message": "Valve opened successfully",
  "valve_state": "OPEN"
}
```

---

### Telemetry & Status

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/status` | Current system status | Yes |
| GET | `/api/telemetry/latest` | Latest telemetry record | Yes |
| GET | `/api/telemetry/history` | Historical telemetry | Yes |
| GET | `/api/telemetry/range` | Telemetry in time range | Yes |
| GET | `/api/metrics` | System metrics & aggregates | Yes |

**Example:**
```bash
curl http://localhost:8000/api/status \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Response:**
```json
{
  "valve_state": "CLOSED",
  "emergency_mode": false,
  "last_telemetry": {
    "id": 1234,
    "ts_utc": 1697000000,
    "valve_state": "CLOSED",
    "p1": 2.45,
    "p2": 2.38,
    "c_src": 145.2,
    "c_dst": 230.5,
    "em": 0
  },
  "active_alerts_count": 0
}
```

---

### Alerts

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/alerts` | Get all alerts | Yes |
| POST | `/api/alerts/ack` | Acknowledge alert | Yes |

---

### Operations History

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/operations/history` | Valve operations log | Yes |

---

### Health Check

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/api/healthz` | Health check | No |

---

## 🔌 WebSocket

### Connect to Real-Time Telemetry

**Endpoint:** `ws://localhost:8000/ws/telemetry`

**Authentication:**
After connecting, send JWT token:
```json
{
  "token": "YOUR_JWT_TOKEN"
}
```

**Receiving Messages:**

Telemetry updates (every 1 second):
```json
{
  "type": "telemetry",
  "data": {
    "t": 1234,
    "valve": "OPEN",
    "p1": 3.45,
    "p2": 3.21,
    "c_src": 140.2,
    "c_dst": 230.1,
    "em": 0
  }
}
```

Alert notifications:
```json
{
  "type": "alert",
  "data": {
    "type": "SAFETY_VIOLATION",
    "violations": ["Pressure sensor 1 exceeds limit: 6.5 > 6.0 bar"],
    "timestamp": 1697000000
  }
}
```

Valve events:
```json
{
  "type": "valve_event",
  "data": {
    "command": "OPEN",
    "user": "operator",
    "result": "SUCCESS",
    "timestamp": 1697000000
  }
}
```

**JavaScript Example:**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/telemetry');

ws.onopen = () => {
  // Authenticate
  ws.send(JSON.stringify({ token: 'YOUR_JWT_TOKEN' }));
};

ws.onmessage = (event) => {
  const message = JSON.parse(event.data);
  
  if (message.type === 'telemetry') {
    console.log('Telemetry:', message.data);
  }
};
```

---

## 🗄️ Database Schema

### Tables

**telemetry**
- Stores all sensor readings
- Indexed by timestamp and valve state
- Retention: configurable (default 7 days)

**valve_operations**
- Logs all valve commands
- Tracks who issued each command
- Useful for audit trail

**system_alerts**
- Stores all safety alerts
- Can be acknowledged
- Priority levels: LOW, MEDIUM, HIGH, CRITICAL

**users**
- User accounts with roles
- Password hashes (bcrypt)

**rules**
- Safety rules configuration
- JSON format for flexibility

**settings**
- Key-value configuration store

---

## 🔐 Authentication & Authorization

### Roles

| Role | Permissions |
|------|-------------|
| **admin** | Full access (OPEN, CLOSE, FORCE_OPEN, RESET_EMERGENCY) |
| **operator** | OPEN, CLOSE, view data |
| **viewer** | View data only |

### Default Users

- `yuvarajyali@gmail.com` / `smart_valve_system` (admin role) ⭐ Primary
- `admin` / `admin123` (admin role)
- `operator` / `operator123` (operator role)
- `viewer` / `viewer123` (viewer role)

**⚠️ Change these passwords in production!**

---

## 🛡️ Safety Features

### Rules Engine

The backend enforces safety rules:
- Max pressure: **6.0 bar**
- Critical concentration: **500 units**
- Minimum source concentration: **10 units**
- Maximum destination concentration: **400 units**

### Auto-Actions

When violations detected:
1. Alert created in database
2. WebSocket notification sent to clients
3. Emergency mode may be triggered
4. Valve may be auto-closed (if critical)

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./data/water_valve.db` | Database connection |
| `JWT_SECRET` | ⚠️ Change in production | Secret key for JWT |
| `JWT_ALGORITHM` | `HS256` | JWT algorithm |
| `JWT_EXPIRATION_MINUTES` | `1440` | Token expiration (24h) |
| `ARDUINO_PORT` | `COM3` | Serial port for Arduino |
| `ARDUINO_BAUD_RATE` | `115200` | Serial baud rate |
| `AUTO_DETECT_ARDUINO` | `true` | Auto-detect Arduino by VID/PID |
| `MAX_PRESSURE_BAR` | `6.0` | Maximum pressure threshold |
| `CRITICAL_CONCENTRATION` | `500.0` | Critical concentration |
| `AUTO_CLOSE_TIMEOUT_SECONDS` | `1800` | Auto-close timeout (30 min) |

---

## 📁 Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI application
│   ├── serial_manager.py          # Arduino serial communication
│   ├── ws_manager.py              # WebSocket connection manager
│   │
│   ├── api/                       # API endpoints
│   │   ├── auth.py                # Authentication
│   │   ├── valve.py               # Valve control
│   │   └── telemetry.py           # Telemetry & status
│   │
│   ├── db/                        # Database layer
│   │   ├── models.py              # SQLAlchemy models
│   │   ├── schemas.py             # Pydantic schemas
│   │   └── session.py             # DB session management
│   │
│   ├── services/                  # Business logic
│   │   ├── rules_engine.py        # Safety validation
│   │   └── alerts.py              # Alert management
│   │
│   └── utils/                     # Utilities
│       ├── logger.py              # Logging configuration
│       └── security.py            # JWT & password hashing
│
├── scripts/
│   ├── seed_data.py               # Database seeding
│   └── serial_simulator.py        # Arduino simulator
│
├── requirements.txt               # Python dependencies
├── .env.example                   # Environment template
└── README.md                      # This file
```

---

## 🐛 Troubleshooting

### Arduino Not Detected

**Issue:** `Arduino not detected on any port`

**Solutions:**
1. Check USB cable connection
2. Verify Arduino port in `.env` file
3. On Windows: Check Device Manager for COM port
4. On Linux: Check permissions (`sudo usermod -a -G dialout $USER`)
5. Try manual port: Set `AUTO_DETECT_ARDUINO=false` and `ARDUINO_PORT=COM3`

### Database Locked

**Issue:** `database is locked`

**Solution:** SQLite doesn't support many concurrent writes. For production, consider PostgreSQL.

### WebSocket Not Receiving Data

**Issue:** WebSocket connects but no telemetry

**Solutions:**
1. Check Arduino is connected: `GET /api/healthz`
2. Verify telemetry in logs: Check `logs/water_valve.log`
3. Ensure JWT token is valid
4. Check WebSocket authentication message sent correctly

### Import Errors

**Issue:** `ModuleNotFoundError`

**Solution:**
```bash
# Ensure virtual environment is activated
pip install -r requirements.txt

# Run from backend directory
cd backend
uvicorn app.main:app --reload
```

---

## 📊 Monitoring

### Logs

Logs are written to:
- **Console:** INFO level and above
- **File:** `logs/water_valve.log` (DEBUG level)

### Health Check

```bash
curl http://localhost:8000/api/healthz
```

Response:
```json
{
  "status": "healthy",
  "timestamp": 1697000000,
  "arduino_connected": true
}
```

---

## 🚢 Production Deployment

### Security Checklist

- [ ] Change `JWT_SECRET` to a strong random key
- [ ] Change all default user passwords
- [ ] Use HTTPS (TLS/SSL certificates)
- [ ] Set specific CORS origins (not `*`)
- [ ] Use PostgreSQL instead of SQLite
- [ ] Enable rate limiting
- [ ] Set up log rotation
- [ ] Configure firewall rules
- [ ] Use environment-specific `.env` files

### Docker Deployment

See main `docker-compose.yml` in project root.

---

## 🔄 Development Workflow

### Run with Auto-Reload

```bash
uvicorn app.main:app --reload
```

### Run Tests (TODO)

```bash
pytest
```

### Format Code

```bash
black app/
isort app/
```

---

## 🆘 Support

- **Backend Issues:** Check logs in `logs/water_valve.log`
- **Serial Communication:** Test with `serial_simulator.py` first
- **API Testing:** Use Swagger UI at http://localhost:8000/docs

---

**Built with 💧 for Smart Water Management**
