import React, { useEffect } from 'react';
import { useQuery } from 'react-query';
import { TestTube, Shield, Zap, AlertTriangle } from 'lucide-react';
import { LineChart } from '../components/charts/LineChart';
import { Heatmap } from '../components/charts/Heatmap';
import { MetricCard } from '../components/dashboard/MetricCard';
import { AlertsWidget } from '../components/dashboard/AlertsWidget';
import { TestExecutionMonitor } from '../components/dashboard/TestExecutionMonitor';
import { CoverageWidget } from '../components/dashboard/CoverageWidget';
import { useWebSocket } from '../hooks/useWebSocket';

interface DashboardSummary {
  tests: {
    total: number;
    passed: number;
    failed: number;
    skipped: number;
    passRate: number;
    avgDuration: number;
    trend: string;
  };
  coverage: {
    overall: number;
    lines: number;
    functions: number;
    branches: number;
    statements: number;
    trend: string;
  };
  performance: {
    avgResponseTime: number;
    p95ResponseTime: number;
    throughput: number;
    errorRate: number;
    trend: string;
  };
  alerts: {
    total: number;
    critical: number;
    high: number;
    medium: number;
    low: number;
    resolved: number;
    unresolved: number;
  };
  activity: {
    testsLast24h: number;
    deploymentsLast24h: number;
    alertsLast24h: number;
    coverageChanges: string;
  };
}

async function fetchDashboardSummary(): Promise<DashboardSummary> {
  const response = await fetch('/api/dashboard/summary');
  if (!response.ok) {
    throw new Error('Failed to fetch dashboard summary');
  }
  return response.json().then(data => data.data);
}

async function fetchTrendData(metric: string) {
  const response = await fetch(`/api/dashboard/trends?metric=${metric}&period=day&limit=7`);
  if (!response.ok) {
    throw new Error(`Failed to fetch ${metric} trend data`);
  }
  return response.json().then(data => data.data);
}

export function Dashboard() {
  const { subscribe, unsubscribe } = useWebSocket();

  // Subscribe to real-time updates
  useEffect(() => {
    subscribe(['tests', 'coverage', 'metrics', 'alerts']);
    return () => {
      unsubscribe(['tests', 'coverage', 'metrics', 'alerts']);
    };
  }, [subscribe, unsubscribe]);

  const { data: summary, isLoading: summaryLoading } = useQuery(
    'dashboard-summary',
    fetchDashboardSummary,
    {
      refetchInterval: 30000, // Refetch every 30 seconds
    }
  );

  const { data: testTrends } = useQuery(
    'test-trends',
    () => fetchTrendData('tests'),
    {
      refetchInterval: 60000, // Refetch every minute
    }
  );

  const { data: coverageTrends } = useQuery(
    'coverage-trends',
    () => fetchTrendData('coverage'),
    {
      refetchInterval: 60000,
    }
  );

  const { data: performanceTrends } = useQuery(
    'performance-trends',
    () => fetchTrendData('performance'),
    {
      refetchInterval: 60000,
    }
  );

  // Generate mock heatmap data for demonstration
  const generateHeatmapData = () => {
    const hours = Array.from({ length: 24 }, (_, i) => `${i.toString().padStart(2, '0')}:00`);
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];

    return days.flatMap(day =>
      hours.map(hour => ({
        x: hour,
        y: day,
        value: Math.random() * 100 + Math.sin((parseInt(hour) / 24) * Math.PI * 2) * 20 + 50
      }))
    );
  };

  const convertTrendsToChartData = (trends: any) => {
    if (!trends?.data) return [];
    return trends.data.map((point: any) => ({
      timestamp: new Date(point.timestamp),
      value: point.value
    }));
  };

  if (summaryLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="loading-spinner" />
        <span className="ml-2 text-muted-foreground">Loading dashboard...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gradient">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Overview of your test monitoring and performance metrics
        </p>
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <MetricCard
          title="Test Success Rate"
          value={`${summary?.tests.passRate.toFixed(1)}%`}
          change={summary?.tests.trend}
          changeValue="+2.3%"
          icon={TestTube}
          color="success"
        />
        <MetricCard
          title="Code Coverage"
          value={`${summary?.coverage.overall.toFixed(1)}%`}
          change={summary?.coverage.trend}
          changeValue="+1.5%"
          icon={Shield}
          color="info"
        />
        <MetricCard
          title="Avg Response Time"
          value={`${summary?.performance.avgResponseTime}ms`}
          change={summary?.performance.trend}
          changeValue="-12ms"
          icon={Zap}
          color="warning"
        />
        <MetricCard
          title="Active Alerts"
          value={summary?.alerts.unresolved.toString()}
          change="stable"
          changeValue="0"
          icon={AlertTriangle}
          color="error"
        />
      </div>

      {/* Main Dashboard Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Test Execution Monitor */}
        <div className="lg:col-span-2">
          <TestExecutionMonitor />
        </div>

        {/* Recent Alerts */}
        <div>
          <AlertsWidget />
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Test Trends */}
        <div className="dashboard-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Test Execution Trends</h3>
            <span className="text-sm text-muted-foreground">Last 7 days</span>
          </div>
          <LineChart
            data={convertTrendsToChartData(testTrends)}
            height={300}
            color="#10B981"
            showArea={true}
            animate={true}
          />
        </div>

        {/* Coverage Trends */}
        <div className="dashboard-card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold">Coverage Trends</h3>
            <span className="text-sm text-muted-foreground">Last 7 days</span>
          </div>
          <LineChart
            data={convertTrendsToChartData(coverageTrends)}
            height={300}
            color="#3B82F6"
            showArea={true}
            animate={true}
          />
        </div>
      </div>

      {/* Performance Heatmap */}
      <div className="dashboard-card">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold">Performance Heatmap</h3>
          <span className="text-sm text-muted-foreground">Response times by hour and day</span>
        </div>
        <Heatmap
          data={generateHeatmapData()}
          width={800}
          height={300}
          colorScheme={['#f0f9ff', '#0ea5e9', '#0369a1']}
        />
      </div>

      {/* Coverage Widget */}
      <CoverageWidget />

      {/* Recent Activity */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="metric-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Tests (24h)</p>
              <p className="text-2xl font-bold">{summary?.activity.testsLast24h}</p>
            </div>
            <TestTube className="h-8 w-8 text-success" />
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Deployments (24h)</p>
              <p className="text-2xl font-bold">{summary?.activity.deploymentsLast24h}</p>
            </div>
            <Zap className="h-8 w-8 text-info" />
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Alerts (24h)</p>
              <p className="text-2xl font-bold">{summary?.activity.alertsLast24h}</p>
            </div>
            <AlertTriangle className="h-8 w-8 text-warning" />
          </div>
        </div>

        <div className="metric-card">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-muted-foreground">Coverage Change</p>
              <p className="text-2xl font-bold text-success">{summary?.activity.coverageChanges}</p>
            </div>
            <Shield className="h-8 w-8 text-success" />
          </div>
        </div>
      </div>
    </div>
  );
}