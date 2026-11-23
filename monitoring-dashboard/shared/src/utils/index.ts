import { TestResult, CoverageData, PerformanceMetric } from '../types';

// Date utilities
export const formatDate = (date: string | Date): string => {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  });
};

export const formatDuration = (milliseconds: number): string => {
  if (milliseconds < 1000) {
    return `${milliseconds}ms`;
  }

  const seconds = milliseconds / 1000;
  if (seconds < 60) {
    return `${seconds.toFixed(1)}s`;
  }

  const minutes = seconds / 60;
  if (minutes < 60) {
    return `${minutes.toFixed(1)}m`;
  }

  const hours = minutes / 60;
  return `${hours.toFixed(1)}h`;
};

// Test result utilities
export const calculateTestSummary = (tests: TestResult[]) => {
  const total = tests.length;
  const passed = tests.filter(t => t.status === 'passed').length;
  const failed = tests.filter(t => t.status === 'failed').length;
  const skipped = tests.filter(t => t.status === 'skipped').length;
  const running = tests.filter(t => t.status === 'running').length;
  const pending = tests.filter(t => t.status === 'pending').length;

  return {
    total,
    passed,
    failed,
    skipped,
    running,
    pending,
    passRate: total > 0 ? (passed / total) * 100 : 0
  };
};

export const calculateTotalDuration = (tests: TestResult[]): number => {
  return tests.reduce((total, test) => total + test.duration, 0);
};

export const groupTestsByStatus = (tests: TestResult[]) => {
  return tests.reduce((groups, test) => {
    const status = test.status;
    if (!groups[status]) {
      groups[status] = [];
    }
    groups[status].push(test);
    return groups;
  }, {} as Record<string, TestResult[]>);
};

// Coverage utilities
export const calculateOverallCoverage = (coverageData: CoverageData[]): CoverageData => {
  if (coverageData.length === 0) {
    return {
      file: 'overall',
      lines: { total: 0, covered: 0, percentage: 0 },
      functions: { total: 0, covered: 0, percentage: 0 },
      branches: { total: 0, covered: 0, percentage: 0 },
      statements: { total: 0, covered: 0, percentage: 0 },
      uncoveredLines: []
    };
  }

  const totals = coverageData.reduce(
    (acc, coverage) => ({
      lines: {
        total: acc.lines.total + coverage.lines.total,
        covered: acc.lines.covered + coverage.lines.covered
      },
      functions: {
        total: acc.functions.total + coverage.functions.total,
        covered: acc.functions.covered + coverage.functions.covered
      },
      branches: {
        total: acc.branches.total + coverage.branches.total,
        covered: acc.branches.covered + coverage.branches.covered
      },
      statements: {
        total: acc.statements.total + coverage.statements.total,
        covered: acc.statements.covered + coverage.statements.covered
      }
    }),
    {
      lines: { total: 0, covered: 0 },
      functions: { total: 0, covered: 0 },
      branches: { total: 0, covered: 0 },
      statements: { total: 0, covered: 0 }
    }
  );

  return {
    file: 'overall',
    lines: {
      ...totals.lines,
      percentage: totals.lines.total > 0 ? (totals.lines.covered / totals.lines.total) * 100 : 0
    },
    functions: {
      ...totals.functions,
      percentage: totals.functions.total > 0 ? (totals.functions.covered / totals.functions.total) * 100 : 0
    },
    branches: {
      ...totals.branches,
      percentage: totals.branches.total > 0 ? (totals.branches.covered / totals.branches.total) * 100 : 0
    },
    statements: {
      ...totals.statements,
      percentage: totals.statements.total > 0 ? (totals.statements.covered / totals.statements.total) * 100 : 0
    },
    uncoveredLines: []
  };
};

// Performance utilities
export const calculatePerformanceTrend = (metrics: PerformanceMetric[], periods: number = 7) => {
  const sortedMetrics = metrics.sort((a, b) =>
    new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
  );

  if (sortedMetrics.length < 2) {
    return { trend: 'stable', change: 0 };
  }

  const recent = sortedMetrics.slice(-periods);
  const previous = sortedMetrics.slice(-periods * 2, -periods);

  if (previous.length === 0) {
    return { trend: 'stable', change: 0 };
  }

  const recentAvg = recent.reduce((sum, m) => sum + m.value, 0) / recent.length;
  const previousAvg = previous.reduce((sum, m) => sum + m.value, 0) / previous.length;

  const change = ((recentAvg - previousAvg) / previousAvg) * 100;

  let trend: 'improving' | 'degrading' | 'stable';
  if (Math.abs(change) < 5) {
    trend = 'stable';
  } else if (change > 0) {
    trend = 'degrading';
  } else {
    trend = 'improving';
  }

  return { trend, change: Math.abs(change) };
};

// Color utilities for visualization
export const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    passed: '#10B981',
    failed: '#EF4444',
    skipped: '#F59E0B',
    running: '#3B82F6',
    pending: '#6B7280'
  };
  return colors[status] || '#6B7280';
};

export const getCoverageColor = (percentage: number): string => {
  if (percentage >= 90) return '#10B981';
  if (percentage >= 80) return '#F59E0B';
  if (percentage >= 70) return '#EF4444';
  return '#DC2626';
};

// Data aggregation utilities
export const aggregateDataByTimeRange = <T extends { timestamp: string }>(
  data: T[],
  range: 'hour' | 'day' | 'week' | 'month'
): Record<string, T[]> => {
  const formatMap = {
    hour: (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')} ${String(date.getHours()).padStart(2, '0')}:00`,
    day: (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(date.getDate()).padStart(2, '0')}`,
    week: (date: Date) => {
      const week = Math.ceil(date.getDate() / 7);
      return `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-W${week}`;
    },
    month: (date: Date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`
  };

  const formatter = formatMap[range];

  return data.reduce((groups, item) => {
    const key = formatter(new Date(item.timestamp));
    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);
    return groups;
  }, {} as Record<string, T[]>);
};

// Validation utilities
export const isValidTimeRange = (start: string, end: string): boolean => {
  const startDate = new Date(start);
  const endDate = new Date(end);
  return startDate <= endDate && startDate <= new Date();
};

export const sanitizeSearchQuery = (query: string): string => {
  return query.replace(/[^\w\s-]/g, '').trim();
};