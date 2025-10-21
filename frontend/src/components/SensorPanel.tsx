import { Gauge, Beaker } from 'lucide-react';
import type { Telemetry } from '@/api/client';
import { formatNumber } from '@/utils/format';

interface SensorPanelProps {
  telemetry: Telemetry | null;
}

export const SensorPanel = ({ telemetry }: SensorPanelProps) => {
  const getSensorStatus = (value: number, max: number, critical: number) => {
    if (value >= critical) return 'critical';
    if (value >= max * 0.8) return 'warning';
    return 'normal';
  };

  const pressureStatus = telemetry
    ? getSensorStatus(Math.max(telemetry.p1, telemetry.p2), 6.0, 6.0)
    : 'normal';
  
  const concentrationStatus = telemetry
    ? getSensorStatus(Math.max(telemetry.c_src, telemetry.c_dst), 400, 500)
    : 'normal';

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return 'text-red-600 bg-red-50 border-red-200';
      case 'warning': return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      default: return 'text-green-600 bg-green-50 border-green-200';
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Live Sensors</h2>

      <div className="space-y-6">
        {/* Pressure Sensors */}
        <div className={`p-4 rounded-lg border-2 ${getStatusColor(pressureStatus)}`}>
          <div className="flex items-center gap-3 mb-4">
            <Gauge className="w-6 h-6" />
            <h3 className="font-semibold text-lg">Pressure Sensors</h3>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm opacity-75 mb-1">Sensor 1</p>
              <p className="text-3xl font-bold">
                {telemetry ? formatNumber(telemetry.p1) : '--'} <span className="text-lg">bar</span>
              </p>
            </div>
            <div>
              <p className="text-sm opacity-75 mb-1">Sensor 2</p>
              <p className="text-3xl font-bold">
                {telemetry ? formatNumber(telemetry.p2) : '--'} <span className="text-lg">bar</span>
              </p>
            </div>
          </div>
          
          <div className="mt-3 pt-3 border-t border-current opacity-50">
            <p className="text-xs">Maximum: 6.0 bar</p>
          </div>
        </div>

        {/* Concentration Sensors */}
        <div className={`p-4 rounded-lg border-2 ${getStatusColor(concentrationStatus)}`}>
          <div className="flex items-center gap-3 mb-4">
            <Beaker className="w-6 h-6" />
            <h3 className="font-semibold text-lg">Concentration Sensors</h3>
          </div>
          
          <div className="grid grid-cols-2 gap-4">
            <div>
              <p className="text-sm opacity-75 mb-1">Source</p>
              <p className="text-3xl font-bold">
                {telemetry ? formatNumber(telemetry.c_src, 1) : '--'} <span className="text-lg">units</span>
              </p>
            </div>
            <div>
              <p className="text-sm opacity-75 mb-1">Destination</p>
              <p className="text-3xl font-bold">
                {telemetry ? formatNumber(telemetry.c_dst, 1) : '--'} <span className="text-lg">units</span>
              </p>
            </div>
          </div>
          
          <div className="mt-3 pt-3 border-t border-current opacity-50">
            <p className="text-xs">Critical: 500 units</p>
          </div>
        </div>
      </div>
    </div>
  );
};
