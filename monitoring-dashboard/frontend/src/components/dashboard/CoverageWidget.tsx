import React from 'react';
import { useQuery } from 'react-query';
import { Shield, TrendingUp, TrendingDown } from 'lucide-react';
import { getCoverageColor, getCoverageLevel, formatPercentage } from '../../utils/formatters';

interface CoverageSummary {
  overall: number;
  lines: number;
  functions: number;
  branches: number;
  statements: number;
  totalFiles: number;
  distribution: {
    excellent: number;
    good: number;
    fair: number;
    poor: number;
  };
  trend: {
    change: number;
    direction: 'up' | 'down' | 'stable';
  };
}

async function fetchCoverageSummary(): Promise<CoverageSummary> {
  const response = await fetch('/api/coverage/summary');
  if (!response.ok) {
    throw new Error('Failed to fetch coverage summary');
  }
  return response.json().then(data => ({
    ...data.data,
    trend: {
      change: 2.1,
      direction: 'up' as const
    }
  }));
}

export function CoverageWidget() {
  const { data: coverage, isLoading } = useQuery(
    'coverage-summary',
    fetchCoverageSummary,
    {
      refetchInterval: 30000,
    }
  );

  const getDistributionColor = (level: string) => {
    switch (level) {
      case 'excellent':
        return 'bg-success text-success-foreground';
      case 'good':
        return 'bg-info text-info-foreground';
      case 'fair':
        return 'bg-warning text-warning-foreground';
      case 'poor':
        return 'bg-error text-error-foreground';
      default:
        return 'bg-muted text-muted-foreground';
    }
  };

  if (isLoading) {
    return (
      <div className="dashboard-card">
        <div className="flex items-center justify-center h-48">
          <div className="loading-spinner" />
          <span className="ml-2 text-muted-foreground">Loading coverage data...</span>
        </div>
      </div>
    );
  }

  if (!coverage) {
    return null;
  }

  return (
    <div className="dashboard-card">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold">Code Coverage Overview</h3>
        <div className="flex items-center gap-2 text-sm">
          {coverage.trend.direction === 'up' ? (
            <TrendingUp className="h-4 w-4 text-success" />
          ) : coverage.trend.direction === 'down' ? (
            <TrendingDown className="h-4 w-4 text-error" />
          ) : null}
          <span className={coverage.trend.direction === 'up' ? 'text-success' : 'text-error'}>
            {coverage.trend.change > 0 ? '+' : ''}{coverage.trend.change}%
          </span>
        </div>
      </div>

      {/* Overall Coverage */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="text-center">
          <div className={`text-3xl font-bold ${getCoverageColor(coverage.overall)}`}>
            {formatPercentage(coverage.overall)}
          </div>
          <div className="text-sm text-muted-foreground mt-1">Overall</div>
        </div>
        <div className="text-center">
          <div className={`text-3xl font-bold ${getCoverageColor(coverage.lines)}`}>
            {formatPercentage(coverage.lines)}
          </div>
          <div className="text-sm text-muted-foreground mt-1">Lines</div>
        </div>
        <div className="text-center">
          <div className={`text-3xl font-bold ${getCoverageColor(coverage.functions)}`}>
            {formatPercentage(coverage.functions)}
          </div>
          <div className="text-sm text-muted-foreground mt-1">Functions</div>
        </div>
        <div className="text-center">
          <div className={`text-3xl font-bold ${getCoverageColor(coverage.branches)}`}>
            {formatPercentage(coverage.branches)}
          </div>
          <div className="text-sm text-muted-foreground mt-1">Branches</div>
        </div>
      </div>

      {/* Coverage Distribution */}
      <div className="space-y-4">
        <h4 className="text-sm font-medium text-muted-foreground">
          File Coverage Distribution ({coverage.totalFiles} files)
        </h4>

        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {Object.entries(coverage.distribution).map(([level, count]) => (
            <div
              key={level}
              className="text-center p-3 rounded-lg border bg-card"
            >
              <div className={`inline-flex items-center justify-center w-8 h-8 rounded-full text-xs font-medium mb-2 ${getDistributionColor(level)}`}>
                {count}
              </div>
              <div className="text-sm font-medium capitalize">{level}</div>
              <div className="text-xs text-muted-foreground">
                {level === 'excellent' && '≥90%'}
                {level === 'good' && '80-89%'}
                {level === 'fair' && '70-79%'}
                {level === 'poor' && '<70%'}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Coverage Bar */}
      <div className="mt-6">
        <div className="flex items-center justify-between text-sm mb-2">
          <span className="text-muted-foreground">Coverage Progress</span>
          <span className="font-medium">{formatPercentage(coverage.overall)}</span>
        </div>
        <div className="w-full bg-muted rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-500 ${
              coverage.overall >= 90 ? 'bg-success' :
              coverage.overall >= 80 ? 'bg-info' :
              coverage.overall >= 70 ? 'bg-warning' : 'bg-error'
            }`}
            style={{ width: `${Math.min(coverage.overall, 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-xs text-muted-foreground mt-1">
          <span>0%</span>
          <span>50%</span>
          <span>100%</span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="mt-6 pt-4 border-t">
        <div className="flex flex-wrap gap-2">
          <button className="inline-flex items-center gap-1 px-3 py-1.5 text-xs bg-primary text-primary-foreground rounded-md hover:bg-primary/90 transition-colors">
            <Shield className="h-3 w-3" />
            View Details
          </button>
          <button className="inline-flex items-center gap-1 px-3 py-1.5 text-xs border rounded-md hover:bg-accent transition-colors">
            Generate Report
          </button>
          <button className="inline-flex items-center gap-1 px-3 py-1.5 text-xs border rounded-md hover:bg-accent transition-colors">
            Configure Goals
          </button>
        </div>
      </div>
    </div>
  );
}