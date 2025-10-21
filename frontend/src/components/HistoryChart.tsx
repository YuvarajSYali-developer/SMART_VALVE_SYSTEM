import { useQuery } from '@tanstack/react-query';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { telemetry } from '@/api/client';

export const HistoryChart = () => {
  const { data: history } = useQuery({
    queryKey: ['telemetry-history'],
    queryFn: () => telemetry.getHistory(60),
    refetchInterval: 10000, // Refresh every 10 seconds
  });

  const chartData = history?.data.slice().reverse().map((t) => ({
    time: new Date(t.ts_utc * 1000).toLocaleTimeString(),
    timestamp: t.ts_utc,
    p1: t.p1,
    p2: t.p2,
    c_src: t.c_src / 10, // Scale down for better visualization
    c_dst: t.c_dst / 10,
  })) || [];

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Sensor History (Last Hour)</h2>

      {chartData.length > 0 ? (
        <div className="h-80">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis 
                dataKey="time" 
                tick={{ fontSize: 12 }}
                interval="preserveStartEnd"
              />
              <YAxis tick={{ fontSize: 12 }} />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: 'rgba(255, 255, 255, 0.95)',
                  border: '1px solid #ccc',
                  borderRadius: '8px'
                }}
                formatter={(value: number, name: string) => {
                  if (name.startsWith('c_')) {
                    return [(value * 10).toFixed(1), name === 'c_src' ? 'Source Conc.' : 'Dest. Conc.'];
                  }
                  return [value.toFixed(2), name === 'p1' ? 'Pressure 1' : 'Pressure 2'];
                }}
              />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="p1" 
                stroke="#3b82f6" 
                name="Pressure 1 (bar)"
                dot={false}
                strokeWidth={2}
              />
              <Line 
                type="monotone" 
                dataKey="p2" 
                stroke="#8b5cf6" 
                name="Pressure 2 (bar)"
                dot={false}
                strokeWidth={2}
              />
              <Line 
                type="monotone" 
                dataKey="c_src" 
                stroke="#10b981" 
                name="Source Conc. (÷10)"
                dot={false}
                strokeWidth={2}
              />
              <Line 
                type="monotone" 
                dataKey="c_dst" 
                stroke="#f59e0b" 
                name="Dest. Conc. (÷10)"
                dot={false}
                strokeWidth={2}
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      ) : (
        <div className="h-80 flex items-center justify-center text-gray-500">
          No historical data available
        </div>
      )}
    </div>
  );
};
