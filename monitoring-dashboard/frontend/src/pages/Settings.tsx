import React from 'react';

export function Settings() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gradient">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Dashboard configuration and preferences
        </p>
      </div>

      <div className="dashboard-card">
        <div className="text-center py-12">
          <h3 className="text-lg font-semibold mb-2">Settings Page Coming Soon</h3>
          <p className="text-muted-foreground">
            This page will allow configuration of dashboard settings, alert rules, and user preferences.
          </p>
        </div>
      </div>
    </div>
  );
}