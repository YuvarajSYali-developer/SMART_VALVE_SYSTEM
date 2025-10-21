import { useQuery } from '@tanstack/react-query';
import { LogOut, User } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useTelemetryWS } from '@/hooks/useTelemetryWS';
import { telemetry } from '@/api/client';
import { StatusCard } from '@/components/StatusCard';
import { SensorPanel } from '@/components/SensorPanel';
import { ControlPanel } from '@/components/ControlPanel';
import { HistoryChart } from '@/components/HistoryChart';
import { AlertsPanel } from '@/components/AlertsPanel';
import { MetricsCard } from '@/components/MetricsCard';

export const Dashboard = () => {
  const { user, token, logout } = useAuth();
  const { telemetry: liveTelemetry, isConnected } = useTelemetryWS(token);

  // Fetch initial status
  const { data: status } = useQuery({
    queryKey: ['status'],
    queryFn: () => telemetry.getStatus(),
    refetchInterval: 5000,
  });

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
      window.location.href = '/';
    }
  };

  // Use live telemetry if available, otherwise use status
  const currentTelemetry = liveTelemetry || status?.data.last_telemetry || null;

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">Smart Water Valve Dashboard</h1>
              <p className="text-sm text-gray-600 mt-1">Real-time IoT Monitoring & Control</p>
            </div>
            
            <div className="flex items-center gap-4">
              {/* User Info */}
              <div className="flex items-center gap-2 px-4 py-2 bg-gray-100 rounded-lg">
                <User className="w-5 h-5 text-gray-600" />
                <div className="text-sm">
                  <p className="font-medium text-gray-900">{user?.username}</p>
                  <p className="text-xs text-gray-600 capitalize">{user?.role}</p>
                </div>
              </div>

              {/* Logout Button */}
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 text-red-600 hover:bg-red-50 rounded-lg transition-colors"
              >
                <LogOut className="w-5 h-5" />
                <span className="font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Status Overview */}
        <div className="mb-8">
          <StatusCard status={status?.data} isConnected={isConnected} />
        </div>

        {/* Main Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-8">
          {/* Left Column - Sensors & Control */}
          <div className="lg:col-span-1 space-y-8">
            <SensorPanel telemetry={currentTelemetry} />
            <ControlPanel 
              valveState={status?.data.valve_state} 
              emergencyMode={status?.data.emergency_mode || false}
            />
          </div>

          {/* Right Column - Charts & Alerts */}
          <div className="lg:col-span-2 space-y-8">
            <HistoryChart />
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <AlertsPanel />
              <MetricsCard />
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center text-sm text-gray-500 mt-12 pt-8 border-t border-gray-200">
          <p>Smart Water Valve IoT System v1.0 • Built with 💧 for Water Management</p>
        </div>
      </main>
    </div>
  );
};
