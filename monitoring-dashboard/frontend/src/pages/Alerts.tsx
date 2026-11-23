import React from 'react';

export function Alerts() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gradient">Alerts & Monitoring</h1>
        <p className="text-muted-foreground mt-2">
          Alert management and anomaly detection
        </p>
      </div>

      <div className="dashboard-card">
        <div className="text-center py-12">
          <h3 className="text-lg font-semibold mb-2">Alerts Page Coming Soon</h3>
          <p className="text-muted-foreground">
            This page will show alert management, rule configuration, and anomaly detection.
          </p>
        </div>
      </div>
    </div>
  );
}