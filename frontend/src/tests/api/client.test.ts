import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { auth, valve, telemetry, alerts } from '@/api/client';

vi.mock('axios');
const mockedAxios = axios as any;

describe('API Client', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
  });

  describe('Authentication', () => {
    it('should login successfully', async () => {
      const mockResponse = {
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user: { username: 'testuser', role: 'operator' }
        }
      };
      
      mockedAxios.create.mockReturnValue({
        post: vi.fn().mockResolvedValue(mockResponse),
        interceptors: {
          request: { use: vi.fn() },
          response: { use: vi.fn() }
        }
      });

      const result = await auth.login({ username: 'testuser', password: 'pass' });
      expect(result.data.access_token).toBe('test-token');
    });
  });

  describe('Valve Control', () => {
    it('should have open valve endpoint', () => {
      expect(valve.open).toBeDefined();
      expect(typeof valve.open).toBe('function');
    });

    it('should have close valve endpoint', () => {
      expect(valve.close).toBeDefined();
      expect(typeof valve.close).toBe('function');
    });

    it('should have force open endpoint', () => {
      expect(valve.forceOpen).toBeDefined();
      expect(typeof valve.forceOpen).toBe('function');
    });

    it('should have reset emergency endpoint', () => {
      expect(valve.resetEmergency).toBeDefined();
      expect(typeof valve.resetEmergency).toBe('function');
    });
  });

  describe('Telemetry', () => {
    it('should have getStatus endpoint', () => {
      expect(telemetry.getStatus).toBeDefined();
      expect(typeof telemetry.getStatus).toBe('function');
    });

    it('should have getLatest endpoint', () => {
      expect(telemetry.getLatest).toBeDefined();
      expect(typeof telemetry.getLatest).toBe('function');
    });

    it('should have getHistory endpoint', () => {
      expect(telemetry.getHistory).toBeDefined();
      expect(typeof telemetry.getHistory).toBe('function');
    });

    it('should have getMetrics endpoint', () => {
      expect(telemetry.getMetrics).toBeDefined();
      expect(typeof telemetry.getMetrics).toBe('function');
    });
  });

  describe('Alerts', () => {
    it('should have getAll endpoint', () => {
      expect(alerts.getAll).toBeDefined();
      expect(typeof alerts.getAll).toBe('function');
    });

    it('should have acknowledge endpoint', () => {
      expect(alerts.acknowledge).toBeDefined();
      expect(typeof alerts.acknowledge).toBe('function');
    });
  });
});
