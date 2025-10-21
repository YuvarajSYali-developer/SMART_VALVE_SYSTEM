# Quick Start Guide
## Smart Water Valve IoT System

## 🚀 Start the System

### Step 1: Start Backend Server

```bash
cd backend
uvicorn app.main:app --reload
```

**Backend will run on**: `http://localhost:8000`

**API Documentation**: `http://localhost:8000/docs`

---

### Step 2: Start Frontend (Separate Terminal)

```bash
cd frontend
npm install    # First time only
npm run dev
```

**Frontend will run on**: `http://localhost:5173`

---

### Step 3: Login

Open `http://localhost:5173` in your browser

**Your Credentials:**
- **Username**: `yuvarajyali@gmail`
- **Password**: `SMART_VALVE_SYSTEM`

**Alternative Admin:**
- Username: `admin`
- Password: `admin123`

---

## 🔧 Optional: Arduino Setup

If you have Arduino hardware:

1. Open Arduino IDE
2. Open: `firmware/smart_water_valve/smart_water_valve.ino`
3. Select Board: Arduino Uno
4. Upload to Arduino
5. The backend will auto-detect and connect

**Without Arduino:**
Use the serial simulator:
```bash
cd backend
python scripts/serial_simulator.py
```

---

## ✅ Verify System is Working

### Test Backend API
```bash
# Health check
curl http://localhost:8000/api/healthz

# Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"yuvarajyali@gmail","password":"SMART_VALVE_SYSTEM"}'
```

### Test Frontend
1. Open `http://localhost:5173`
2. Login with your credentials
3. You should see the dashboard

---

## 📱 Dashboard Features

After logging in, you'll have access to:

- ✅ **Live Telemetry** - Real-time sensor readings
- ✅ **Valve Control** - Open/Close buttons
- ✅ **Historical Charts** - Pressure & concentration graphs
- ✅ **Active Alerts** - Safety notifications
- ✅ **System Metrics** - Uptime, operations, averages
- ✅ **WebSocket Status** - Live connection indicator

---

## 🛠️ Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is available
netstat -an | findstr :8000

# Reinstall dependencies
pip install -r requirements.txt
```

### Frontend won't start
```bash
# Clean install
rm -rf node_modules package-lock.json
npm install
```

### Can't login
- Verify credentials in `CREDENTIALS.md`
- Check backend is running on port 8000
- Check browser console for errors

### Arduino not connecting
- Verify correct COM port in `.env` file
- Check USB cable connection
- Try the serial simulator instead

---

## 📚 Additional Documentation

- `README.md` - Project overview
- `CREDENTIALS.md` - All user accounts
- `TEST_SUMMARY.md` - Test results
- `BUILD_STATUS.md` - System status
- `backend/README.md` - API documentation
- `frontend/README.md` - Frontend guide
- `firmware/README.md` - Arduino setup
- `firmware/TEST_CASES.md` - Hardware testing

---

## 🎯 Quick Commands

```bash
# Backend
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend  
cd frontend
npm run dev

# Arduino Simulator (no hardware needed)
cd backend
python scripts/serial_simulator.py

# Run Tests
cd backend && python -m pytest tests/ -v
cd frontend && npm test
```

---

**Default Ports:**
- Backend API: `8000`
- Frontend: `5173` (Vite dev server)
- WebSocket: `ws://localhost:8000/ws/telemetry`

**Happy Monitoring! 💧**
