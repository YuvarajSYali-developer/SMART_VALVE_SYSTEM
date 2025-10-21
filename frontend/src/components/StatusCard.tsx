import { Activity, Droplet, AlertTriangle } from 'lucide-react';
import type { SystemStatus } from '@/api/client';
import { formatTimestamp } from '@/utils/format';

interface StatusCardProps {
  status: SystemStatus | undefined;
  isConnected: boolean;
}

export const StatusCard = ({ status, isConnected }: StatusCardProps) => {
  const valveOpen = status?.valve_state === 'OPEN';
  const emergency = status?.emergency_mode || false;

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">System Status</h2>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
          <span className="text-sm text-gray-600">
            {isConnected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Valve State */}
        <div className={`p-4 rounded-lg ${valveOpen ? 'bg-green-50 border border-green-200' : 'bg-gray-50 border border-gray-200'}`}>
          <div className="flex items-center gap-3">
            <Droplet className={`w-8 h-8 ${valveOpen ? 'text-green-600' : 'text-gray-400'}`} />
            <div>
              <p className="text-sm text-gray-600">Valve State</p>
              <p className={`text-lg font-bold ${valveOpen ? 'text-green-700' : 'text-gray-700'}`}>
                {status?.valve_state || 'UNKNOWN'}
              </p>
            </div>
          </div>
        </div>

        {/* Emergency Mode */}
        <div className={`p-4 rounded-lg ${emergency ? 'bg-red-50 border border-red-200' : 'bg-gray-50 border border-gray-200'}`}>
          <div className="flex items-center gap-3">
            <AlertTriangle className={`w-8 h-8 ${emergency ? 'text-red-600' : 'text-gray-400'}`} />
            <div>
              <p className="text-sm text-gray-600">Emergency</p>
              <p className={`text-lg font-bold ${emergency ? 'text-red-700' : 'text-gray-700'}`}>
                {emergency ? 'ACTIVE' : 'Normal'}
              </p>
            </div>
          </div>
        </div>

        {/* Active Alerts */}
        <div className={`p-4 rounded-lg ${(status?.active_alerts_count || 0) > 0 ? 'bg-yellow-50 border border-yellow-200' : 'bg-gray-50 border border-gray-200'}`}>
          <div className="flex items-center gap-3">
            <Activity className={`w-8 h-8 ${(status?.active_alerts_count || 0) > 0 ? 'text-yellow-600' : 'text-gray-400'}`} />
            <div>
              <p className="text-sm text-gray-600">Active Alerts</p>
              <p className={`text-lg font-bold ${(status?.active_alerts_count || 0) > 0 ? 'text-yellow-700' : 'text-gray-700'}`}>
                {status?.active_alerts_count || 0}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Last Update */}
      {status?.last_telemetry && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500">
            Last update: {formatTimestamp(status.last_telemetry.ts_utc)}
          </p>
        </div>
      )}
    </div>
  );
};
