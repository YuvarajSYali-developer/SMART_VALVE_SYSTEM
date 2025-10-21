import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add auth token to requests
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle auth errors
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/';
    }
    return Promise.reject(error);
  }
);

// Types
export interface LoginRequest {
  username: string;
  password: string;
}

export interface User {
  id: number;
  username: string;
  role: 'admin' | 'operator' | 'viewer';
  created_at: number;
  is_active: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface Telemetry {
  id: number;
  ts_utc: number;
  valve_state: 'OPEN' | 'CLOSED';
  p1: number;
  p2: number;
  c_src: number;
  c_dst: number;
  em: number;
}

export interface SystemStatus {
  valve_state: 'OPEN' | 'CLOSED';
  emergency_mode: boolean;
  last_telemetry: Telemetry | null;
  active_alerts_count: number;
}

export interface SystemMetrics {
  avg_pressure_p1: number;
  avg_pressure_p2: number;
  avg_concentration_src: number;
  avg_concentration_dst: number;
  total_operations: number;
  total_runtime_seconds: number;
  uptime_seconds: number;
}

export interface Alert {
  id: number;
  ts_utc: number;
  alert_type: string;
  message: string;
  priority: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  acknowledged: boolean;
  metadata: any;
}

export interface ValveOperation {
  id: number;
  ts_utc: number;
  command: string;
  issuer_user: string | null;
  result: string;
  message: string | null;
}

export interface ValveCommandResponse {
  success: boolean;
  message: string;
  valve_state?: 'OPEN' | 'CLOSED';
}

// API functions
export const auth = {
  login: (data: LoginRequest) => 
    apiClient.post<LoginResponse>('/api/auth/login', data),
};

export const valve = {
  open: () => 
    apiClient.post<ValveCommandResponse>('/api/valve/open'),
  close: () => 
    apiClient.post<ValveCommandResponse>('/api/valve/close'),
  forceOpen: () => 
    apiClient.post<ValveCommandResponse>('/api/valve/force_open'),
  resetEmergency: () => 
    apiClient.post<ValveCommandResponse>('/api/valve/reset_emergency'),
};

export const telemetry = {
  getStatus: () => 
    apiClient.get<SystemStatus>('/api/status'),
  getLatest: () => 
    apiClient.get<Telemetry>('/api/telemetry/latest'),
  getHistory: (limit = 100) => 
    apiClient.get<Telemetry[]>('/api/telemetry/history', { params: { limit } }),
  getMetrics: (hours = 24) => 
    apiClient.get<SystemMetrics>('/api/metrics', { params: { hours } }),
};

export const alerts = {
  getAll: (acknowledged?: boolean) => 
    apiClient.get<Alert[]>('/api/alerts', { params: { acknowledged } }),
  acknowledge: (alertId: number) => 
    apiClient.post('/api/alerts/ack', null, { params: { alert_id: alertId } }),
};

export const operations = {
  getHistory: (limit = 100) => 
    apiClient.get<ValveOperation[]>('/api/operations/history', { params: { limit } }),
};
