import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { AlertTriangle, Bell, CheckCircle, Clock } from 'lucide-react';
import { alerts } from '@/api/client';
import { formatTimestamp } from '@/utils/format';

export const AlertsPanel = () => {
  const queryClient = useQueryClient();

  const { data: alertsList } = useQuery({
    queryKey: ['alerts'],
    queryFn: () => alerts.getAll(false),
    refetchInterval: 5000,
  });

  const acknowledgeMutation = useMutation({
    mutationFn: (id: number) => alerts.acknowledge(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['alerts'] });
      queryClient.invalidateQueries({ queryKey: ['status'] });
    },
  });

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL': return 'bg-red-100 border-red-300 text-red-800';
      case 'HIGH': return 'bg-orange-100 border-orange-300 text-orange-800';
      case 'MEDIUM': return 'bg-yellow-100 border-yellow-300 text-yellow-800';
      default: return 'bg-blue-100 border-blue-300 text-blue-800';
    }
  };

  const getPriorityIcon = (priority: string) => {
    switch (priority) {
      case 'CRITICAL': return <AlertTriangle className="w-5 h-5" />;
      case 'HIGH': return <Bell className="w-5 h-5" />;
      default: return <Clock className="w-5 h-5" />;
    }
  };

  const activeAlerts = alertsList?.data || [];

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-bold text-gray-900">Active Alerts</h2>
        <span className="px-3 py-1 bg-red-100 text-red-800 rounded-full text-sm font-semibold">
          {activeAlerts.length}
        </span>
      </div>

      {activeAlerts.length === 0 ? (
        <div className="text-center py-8 text-gray-500">
          <CheckCircle className="w-12 h-12 mx-auto mb-3 text-green-500" />
          <p className="font-medium">All clear!</p>
          <p className="text-sm mt-1">No active alerts</p>
        </div>
      ) : (
        <div className="space-y-3 max-h-96 overflow-y-auto">
          {activeAlerts.map((alert) => (
            <div
              key={alert.id}
              className={`p-4 rounded-lg border-2 ${getPriorityColor(alert.priority)}`}
            >
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0 mt-0.5">
                  {getPriorityIcon(alert.priority)}
                </div>
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-2">
                    <div>
                      <p className="font-semibold text-sm">{alert.alert_type}</p>
                      <p className="text-xs opacity-75 mt-0.5">
                        {formatTimestamp(alert.ts_utc)}
                      </p>
                    </div>
                    <span className="text-xs font-bold px-2 py-1 bg-white bg-opacity-50 rounded">
                      {alert.priority}
                    </span>
                  </div>
                  <p className="text-sm mb-3">{alert.message}</p>
                  <button
                    onClick={() => acknowledgeMutation.mutate(alert.id)}
                    disabled={acknowledgeMutation.isPending}
                    className="text-xs px-3 py-1 bg-white hover:bg-opacity-80 bg-opacity-60 rounded font-medium transition-colors"
                  >
                    {acknowledgeMutation.isPending ? 'Acknowledging...' : 'Acknowledge'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
