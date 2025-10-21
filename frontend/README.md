# 🖥️ Frontend Dashboard — Smart Water Valve IoT System

React + TypeScript dashboard for real-time valve monitoring and control.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Configure Environment

```bash
# Copy example env file
copy .env.example .env

# Edit .env if needed (default settings work with local backend)
```

### 3. Start Development Server

```bash
npm run dev
```

Dashboard will be available at: http://localhost:3000

---

## 🎯 Features

### ✅ Authentication
- Login with email/username and password
- JWT token management
- Automatic session persistence
- Role-based UI elements

### ✅ Real-Time Monitoring
- Live telemetry via WebSocket
- Automatic reconnection with exponential backoff
- Sensor readings update every second
- Connection status indicator

### ✅ Valve Control
- Open/Close buttons
- Safety confirmations
- Admin-only force open
- Emergency reset (admin only)
- Role-based button visibility

### ✅ Data Visualization
- Live sensor panels (pressure & concentration)
- Historical charts (last hour)
- System metrics (24h averages)
- Color-coded status indicators

### ✅ Alert Management
- Active alerts panel
- Priority-based coloring
- Acknowledgment functionality
- Real-time alert notifications

### ✅ Responsive Design
- Mobile-friendly layout
- TailwindCSS styling
- Clean and modern UI
- Accessible components

---

## 🔑 Default Login

```
Email: yuvarajyali@gmail.com
Password: smart_valve_system
```

**User Roles:**
- **Admin:** Full access (open, close, force_open, reset_emergency)
- **Operator:** Can open and close valve
- **Viewer:** Read-only access

---

## 📁 Project Structure

```
frontend/
├── src/
│   ├── pages/
│   │   ├── Login.tsx              # Login page
│   │   └── Dashboard.tsx          # Main dashboard
│   │
│   ├── components/
│   │   ├── StatusCard.tsx         # System status overview
│   │   ├── SensorPanel.tsx        # Live sensor readings
│   │   ├── ControlPanel.tsx       # Valve control buttons
│   │   ├── HistoryChart.tsx       # Telemetry history chart
│   │   ├── AlertsPanel.tsx        # Active alerts
│   │   └── MetricsCard.tsx        # System metrics
│   │
│   ├── hooks/
│   │   ├── useAuth.ts             # Authentication state
│   │   └── useTelemetryWS.ts      # WebSocket connection
│   │
│   ├── api/
│   │   └── client.ts              # API client & types
│   │
│   ├── utils/
│   │   └── format.ts              # Formatting utilities
│   │
│   ├── App.tsx                    # Root component
│   ├── main.tsx                   # Entry point
│   └── index.css                  # Global styles
│
├── package.json
├── vite.config.ts
├── tsconfig.json
└── tailwind.config.js
```

---

## 🛠️ Tech Stack

- **Framework:** React 18
- **Language:** TypeScript
- **Build Tool:** Vite
- **Styling:** TailwindCSS
- **State Management:** Zustand + React Query
- **Charts:** Recharts
- **Icons:** Lucide React
- **HTTP Client:** Axios
- **Routing:** React Router

---

## 🔌 API Integration

### REST Endpoints

All API calls go through `/api` proxy to backend:
- `POST /api/auth/login` - Authentication
- `GET /api/status` - Current system status
- `POST /api/valve/open` - Open valve
- `POST /api/valve/close` - Close valve
- `GET /api/telemetry/history` - Historical data
- `GET /api/metrics` - System metrics
- `GET /api/alerts` - Active alerts

### WebSocket

Real-time telemetry via WebSocket at `/ws/telemetry`:
- Automatic authentication with JWT
- Reconnection with exponential backoff
- Heartbeat/ping-pong for keepalive
- Message types: telemetry, alert, valve_event

---

## 🎨 UI Components

### Status Card
- Valve state (OPEN/CLOSED)
- Emergency mode indicator
- Active alerts count
- Last update timestamp
- WebSocket connection status

### Sensor Panel
- Pressure readings (2 sensors)
- Concentration readings (source/destination)
- Color-coded status (normal/warning/critical)
- Threshold indicators

### Control Panel
- Open/Close buttons
- Role-based access control
- Admin controls (force open, reset emergency)
- Safety confirmations
- Real-time feedback

### History Chart
- Line chart with 4 metrics
- Last 60 data points
- Auto-refresh every 10 seconds
- Responsive design

### Alerts Panel
- Priority-based sorting
- Color-coded by severity
- Acknowledge button
- Scrollable list
- Empty state

### Metrics Card
- 24-hour averages
- Operation count
- Total runtime
- System uptime

---

## 🧪 Development

### Run Development Server
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

### Lint Code
```bash
npm run lint
```

---

## 🐛 Troubleshooting

### WebSocket Connection Issues

**Issue:** WebSocket not connecting

**Solutions:**
1. Ensure backend is running on port 8000
2. Check backend logs for WebSocket errors
3. Verify JWT token is valid
4. Check browser console for errors

### API Errors

**Issue:** API calls failing with 401

**Solution:** Token expired, logout and login again

**Issue:** CORS errors

**Solution:** Backend CORS middleware should allow `http://localhost:3000`

### Chart Not Displaying

**Issue:** History chart is empty

**Solution:** Backend needs to have telemetry data. Run for a few minutes or use simulator.

---

## 🔒 Security

- JWT tokens stored in localStorage
- Automatic token refresh on page load
- Tokens expire after 24 hours
- Password input masked
- HTTPS recommended for production

---

## 📱 Responsive Design

The dashboard is fully responsive:
- **Desktop:** Full 3-column layout
- **Tablet:** 2-column adaptive layout
- **Mobile:** Single column stacked layout

---

## 🎯 User Roles & Permissions

| Feature | Viewer | Operator | Admin |
|---------|--------|----------|-------|
| View telemetry | ✅ | ✅ | ✅ |
| View alerts | ✅ | ✅ | ✅ |
| Close valve | ✅ | ✅ | ✅ |
| Open valve | ❌ | ✅ | ✅ |
| Force open | ❌ | ❌ | ✅ |
| Reset emergency | ❌ | ❌ | ✅ |

---

## 🔄 Real-Time Updates

- **Telemetry:** Updates every second via WebSocket
- **Status:** Polls every 5 seconds
- **History Chart:** Refreshes every 10 seconds
- **Metrics:** Refreshes every 30 seconds
- **Alerts:** Polls every 5 seconds

---

## 🚀 Deployment

### Build for Production
```bash
npm run build
```

Output will be in `dist/` folder.

### Deploy to Netlify/Vercel
```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
netlify deploy --prod --dir=dist
```

### Environment Variables
Set in production:
- `VITE_API_URL` - Backend API URL
- `VITE_WS_URL` - WebSocket URL

---

**Built with 💧 for Smart Water Management**
