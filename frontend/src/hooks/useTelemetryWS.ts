import { useEffect, useRef, useState, useCallback } from 'react';
import type { Telemetry } from '@/api/client';

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws/telemetry';

interface TelemetryMessage {
  type: 'telemetry' | 'alert' | 'valve_event' | 'auth_success' | 'auth_error' | 'heartbeat' | 'pong';
  data?: any;
  message?: string;
}

export const useTelemetryWS = (token: string | null) => {
  const [telemetry, setTelemetry] = useState<Telemetry | null>(null);
  const [isConnected, setIsConnected] = useState(false);
  const [alerts, setAlerts] = useState<any[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout>();
  const reconnectAttempts = useRef(0);

  const connect = useCallback(() => {
    if (!token) return;

    try {
      const ws = new WebSocket(WS_URL);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        reconnectAttempts.current = 0;
        
        // Send authentication
        ws.send(JSON.stringify({ token }));
        
        // Start heartbeat
        const heartbeatInterval = setInterval(() => {
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000); // Every 30 seconds

        ws.addEventListener('close', () => {
          clearInterval(heartbeatInterval);
        });
      };

      ws.onmessage = (event) => {
        try {
          const message: TelemetryMessage = JSON.parse(event.data);

          switch (message.type) {
            case 'auth_success':
              console.log('WebSocket authenticated');
              break;
            
            case 'auth_error':
              console.error('WebSocket auth error:', message.message);
              ws.close();
              break;
            
            case 'telemetry':
              setTelemetry(message.data);
              break;
            
            case 'alert':
              setAlerts(prev => [message.data, ...prev].slice(0, 10));
              break;
            
            case 'valve_event':
              console.log('Valve event:', message.data);
              break;
            
            case 'heartbeat':
            case 'pong':
              // Keep-alive messages
              break;
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      ws.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        
        // Exponential backoff reconnection
        if (reconnectAttempts.current < 10) {
          const delay = Math.min(1000 * Math.pow(2, reconnectAttempts.current), 30000);
          reconnectAttempts.current++;
          
          console.log(`Reconnecting in ${delay}ms (attempt ${reconnectAttempts.current})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            connect();
          }, delay);
        }
      };
    } catch (error) {
      console.error('Failed to create WebSocket:', error);
    }
  }, [token]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    
    setIsConnected(false);
  }, []);

  useEffect(() => {
    if (token) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [token, connect, disconnect]);

  return {
    telemetry,
    isConnected,
    alerts,
    reconnect: connect,
  };
};
