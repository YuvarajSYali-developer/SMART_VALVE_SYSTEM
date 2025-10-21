import { useState } from 'react';
import { Power, PowerOff, AlertTriangle, RotateCcw } from 'lucide-react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { valve } from '@/api/client';
import { useAuth } from '@/hooks/useAuth';

interface ControlPanelProps {
  valveState: 'OPEN' | 'CLOSED' | undefined;
  emergencyMode: boolean;
}

export const ControlPanel = ({ valveState, emergencyMode }: ControlPanelProps) => {
  const [showForceConfirm, setShowForceConfirm] = useState(false);
  const queryClient = useQueryClient();
  const user = useAuth((state) => state.user);

  const isAdmin = user?.role === 'admin';
  const canOperate = isAdmin || user?.role === 'operator';

  const openMutation = useMutation({
    mutationFn: valve.open,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['status'] });
    },
  });

  const closeMutation = useMutation({
    mutationFn: valve.close,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['status'] });
    },
  });

  const forceOpenMutation = useMutation({
    mutationFn: valve.forceOpen,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['status'] });
      setShowForceConfirm(false);
    },
  });

  const resetEmergencyMutation = useMutation({
    mutationFn: valve.resetEmergency,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['status'] });
    },
  });

  const handleOpen = () => {
    if (window.confirm('Are you sure you want to OPEN the valve?')) {
      openMutation.mutate();
    }
  };

  const handleForceOpen = () => {
    if (showForceConfirm) {
      forceOpenMutation.mutate();
    } else {
      setShowForceConfirm(true);
    }
  };

  return (
    <div className="card">
      <h2 className="text-xl font-bold text-gray-900 mb-6">Valve Control</h2>

      {/* Role Info */}
      <div className="mb-4 p-3 bg-blue-50 border border-blue-200 rounded-lg">
        <p className="text-sm text-blue-800">
          <span className="font-semibold">Access Level:</span> {user?.role || 'Unknown'}
        </p>
      </div>

      {/* Emergency Warning */}
      {emergencyMode && (
        <div className="mb-4 p-4 bg-red-50 border-2 border-red-300 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-6 h-6 text-red-600 flex-shrink-0" />
            <div>
              <p className="font-bold text-red-800">EMERGENCY MODE ACTIVE</p>
              <p className="text-sm text-red-700 mt-1">
                Valve control is restricted. Admin must reset emergency mode.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Control Buttons */}
      <div className="space-y-3">
        {/* Open Button */}
        <button
          onClick={handleOpen}
          disabled={!canOperate || emergencyMode || valveState === 'OPEN' || openMutation.isPending}
          className="btn-primary w-full flex items-center justify-center gap-3 py-4 text-lg"
        >
          <Power className="w-6 h-6" />
          {openMutation.isPending ? 'Opening...' : 'Open Valve'}
        </button>

        {/* Close Button */}
        <button
          onClick={() => closeMutation.mutate()}
          disabled={valveState === 'CLOSED' || closeMutation.isPending}
          className="btn-secondary w-full flex items-center justify-center gap-3 py-4 text-lg"
        >
          <PowerOff className="w-6 h-6" />
          {closeMutation.isPending ? 'Closing...' : 'Close Valve'}
        </button>

        {/* Admin Controls */}
        {isAdmin && (
          <>
            <div className="border-t border-gray-300 my-4 pt-4">
              <p className="text-sm font-semibold text-gray-700 mb-3">Admin Controls</p>

              {/* Force Open */}
              {showForceConfirm ? (
                <div className="p-4 bg-yellow-50 border-2 border-yellow-400 rounded-lg mb-3">
                  <p className="text-sm font-bold text-yellow-900 mb-3">
                    ⚠️ Confirm Force Open
                  </p>
                  <p className="text-xs text-yellow-800 mb-3">
                    This will bypass all safety checks. Use only in controlled conditions.
                  </p>
                  <div className="flex gap-2">
                    <button
                      onClick={handleForceOpen}
                      disabled={forceOpenMutation.isPending}
                      className="btn-danger flex-1"
                    >
                      {forceOpenMutation.isPending ? 'Opening...' : 'Confirm'}
                    </button>
                    <button
                      onClick={() => setShowForceConfirm(false)}
                      className="btn-secondary flex-1"
                    >
                      Cancel
                    </button>
                  </div>
                </div>
              ) : (
                <button
                  onClick={handleForceOpen}
                  disabled={!emergencyMode}
                  className="btn-danger w-full flex items-center justify-center gap-2 mb-3"
                >
                  <AlertTriangle className="w-5 h-5" />
                  Force Open (Bypass Safety)
                </button>
              )}

              {/* Reset Emergency */}
              <button
                onClick={() => resetEmergencyMutation.mutate()}
                disabled={!emergencyMode || resetEmergencyMutation.isPending}
                className="btn-secondary w-full flex items-center justify-center gap-2"
              >
                <RotateCcw className="w-5 h-5" />
                {resetEmergencyMutation.isPending ? 'Resetting...' : 'Reset Emergency Mode'}
              </button>
            </div>
          </>
        )}
      </div>

      {/* Messages */}
      {openMutation.isError && (
        <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-sm text-red-800">
            {(openMutation.error as any)?.response?.data?.detail || 'Failed to open valve'}
          </p>
        </div>
      )}

      {openMutation.isSuccess && (
        <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
          <p className="text-sm text-green-800">
            {openMutation.data?.data.message || 'Valve opened successfully'}
          </p>
        </div>
      )}
    </div>
  );
};
