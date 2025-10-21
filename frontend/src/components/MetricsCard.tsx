import { useQuery } from '@tanstack/react-query';
import { TrendingUp, Activity, Clock, Zap } from 'lucide-react';
import { telemetry } from '@/api/client';
import { formatDuration, formatNumber } from '@/utils/format';

export const MetricsCard = () => {
  const { data: metrics } = useQuery({
    queryKey: ['metrics'],
    queryFn: () => telemetry.getMetrics(24),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const stats = metrics?.data;

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-900 mb-6">System Metrics (24h)</h2>

      <div className="grid grid-cols-2 gap-4">
        {/* Average Pressure */}
        <div className="p-4 bg-blue-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <TrendingUp className="w-5 h-5 text-blue-600" />
            <p className="text-sm font-medium text-blue-900">Avg. Pressure</p>
          </div>
          <p className="text-2xl font-bold text-blue-700">
            {stats ? formatNumber((stats.avg_pressure_p1 + stats.avg_pressure_p2) / 2) : '--'}
            <span className="text-sm ml-1">bar</span>
          </p>
        </div>

        {/* Average Concentration */}
        <div className="p-4 bg-green-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Activity className="w-5 h-5 text-green-600" />
            <p className="text-sm font-medium text-green-900">Avg. Concentration</p>
          </div>
          <p className="text-2xl font-bold text-green-700">
            {stats ? formatNumber((stats.avg_concentration_src + stats.avg_concentration_dst) / 2, 1) : '--'}
            <span className="text-sm ml-1">units</span>
          </p>
        </div>

        {/* Total Operations */}
        <div className="p-4 bg-purple-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Zap className="w-5 h-5 text-purple-600" />
            <p className="text-sm font-medium text-purple-900">Operations</p>
          </div>
          <p className="text-2xl font-bold text-purple-700">
            {stats?.total_operations || 0}
          </p>
        </div>

        {/* Total Runtime */}
        <div className="p-4 bg-orange-50 rounded-lg">
          <div className="flex items-center gap-2 mb-2">
            <Clock className="w-5 h-5 text-orange-600" />
            <p className="text-sm font-medium text-orange-900">Runtime</p>
          </div>
          <p className="text-lg font-bold text-orange-700">
            {stats ? formatDuration(stats.total_runtime_seconds) : '--'}
          </p>
        </div>
      </div>

      {/* System Uptime */}
      {stats && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-sm text-gray-600">
            <span className="font-medium">System Uptime:</span> {formatDuration(stats.uptime_seconds)}
          </p>
        </div>
      )}
    </div>
  );
};
