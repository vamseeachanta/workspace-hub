import React from 'react';
import { useQuery } from 'react-query';
import { AlertTriangle, Clock, CheckCircle } from 'lucide-react';
import { formatRelativeTime } from '../../utils/formatters';

interface Alert {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  title: string;
  description: string;
  timestamp: string;
  resolved: boolean;
  resolvedAt?: string;
}

async function fetchRecentAlerts(): Promise<Alert[]> {
  const response = await fetch('/api/alerts?limit=5&resolved=false');
  if (!response.ok) {
    throw new Error('Failed to fetch recent alerts');
  }
  return response.json().then(data => data.data.alerts);
}

export function AlertsWidget() {
  const { data: alerts, isLoading } = useQuery(
    'recent-alerts',
    fetchRecentAlerts,
    {
      refetchInterval: 10000,
    }
  );

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
      case 'high':
        return <AlertTriangle className="h-4 w-4" />;
      case 'medium':
        return <Clock className="h-4 w-4" />;
      case 'low':
      default:
        return <CheckCircle className="h-4 w-4" />;
    }
  };

  const getSeverityStyle = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'alert-critical';
      case 'high':
        return 'alert-high';
      case 'medium':
        return 'alert-medium';
      case 'low':
      default:
        return 'alert-low';
    }
  };

  if (isLoading) {
    return (
      <div className="dashboard-card">
        <div className="flex items-center justify-center h-48">
          <div className="loading-spinner" />
          <span className="ml-2 text-muted-foreground">Loading alerts...</span>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-card">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold">Recent Alerts</h3>
        <span className="text-sm text-muted-foreground">
          {alerts?.length || 0} active
        </span>
      </div>

      <div className="space-y-3">
        {alerts?.map((alert) => (
          <div
            key={alert.id}
            className="p-3 rounded-lg border transition-all duration-200 hover:shadow-sm"
          >
            <div className="flex items-start gap-3">
              <div className={`p-1 rounded ${getSeverityStyle(alert.severity)}`}>
                {getSeverityIcon(alert.severity)}
              </div>

              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <p className="font-medium text-sm truncate">{alert.title}</p>
                  <span className={`status-badge alert-${alert.severity}`}>
                    {alert.severity}
                  </span>
                </div>
                <p className="text-xs text-muted-foreground mb-2 line-clamp-2">
                  {alert.description}
                </p>
                <div className="flex items-center justify-between text-xs text-muted-foreground">
                  <span>{alert.type.replace(/_/g, ' ')}</span>
                  <span>{formatRelativeTime(alert.timestamp)}</span>
                </div>
              </div>
            </div>
          </div>
        ))}

        {(!alerts || alerts.length === 0) && (
          <div className="text-center py-8 text-muted-foreground">
            <CheckCircle className="h-8 w-8 mx-auto mb-2 opacity-50" />
            <p>No active alerts</p>
            <p className="text-xs">All systems are running normally</p>
          </div>
        )}
      </div>

      {alerts && alerts.length > 0 && (
        <div className="mt-4 pt-4 border-t">
          <button className="w-full text-sm text-primary hover:text-primary/80 transition-colors">
            View all alerts →
          </button>
        </div>
      )}
    </div>
  );
}