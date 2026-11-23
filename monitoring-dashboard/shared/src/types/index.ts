import { z } from 'zod';

// Test Execution Types
export const TestStatusSchema = z.enum(['pending', 'running', 'passed', 'failed', 'skipped']);
export type TestStatus = z.infer<typeof TestStatusSchema>;

export const TestResultSchema = z.object({
  id: z.string(),
  name: z.string(),
  suite: z.string(),
  status: TestStatusSchema,
  duration: z.number(),
  startTime: z.string().datetime(),
  endTime: z.string().datetime().optional(),
  error: z.string().optional(),
  stackTrace: z.string().optional(),
  tags: z.array(z.string()).default([]),
  metadata: z.record(z.unknown()).default({})
});

export type TestResult = z.infer<typeof TestResultSchema>;

// Coverage Types
export const CoverageDataSchema = z.object({
  file: z.string(),
  lines: z.object({
    total: z.number(),
    covered: z.number(),
    percentage: z.number()
  }),
  functions: z.object({
    total: z.number(),
    covered: z.number(),
    percentage: z.number()
  }),
  branches: z.object({
    total: z.number(),
    covered: z.number(),
    percentage: z.number()
  }),
  statements: z.object({
    total: z.number(),
    covered: z.number(),
    percentage: z.number()
  }),
  uncoveredLines: z.array(z.number()).default([])
});

export type CoverageData = z.infer<typeof CoverageDataSchema>;

// Performance Metrics
export const PerformanceMetricSchema = z.object({
  id: z.string(),
  timestamp: z.string().datetime(),
  testSuite: z.string(),
  metric: z.enum(['duration', 'memory', 'cpu', 'throughput']),
  value: z.number(),
  unit: z.string(),
  tags: z.record(z.string()).default({})
});

export type PerformanceMetric = z.infer<typeof PerformanceMetricSchema>;

// Alert Types
export const AlertSeveritySchema = z.enum(['low', 'medium', 'high', 'critical']);
export type AlertSeverity = z.infer<typeof AlertSeveritySchema>;

export const AlertTypeSchema = z.enum(['regression', 'coverage_drop', 'performance_degradation', 'flaky_test', 'anomaly']);
export type AlertType = z.infer<typeof AlertTypeSchema>;

export const AlertSchema = z.object({
  id: z.string(),
  type: AlertTypeSchema,
  severity: AlertSeveritySchema,
  title: z.string(),
  description: z.string(),
  timestamp: z.string().datetime(),
  resolved: z.boolean().default(false),
  resolvedAt: z.string().datetime().optional(),
  metadata: z.record(z.unknown()).default({})
});

export type Alert = z.infer<typeof AlertSchema>;

// Dashboard Configuration
export const DashboardConfigSchema = z.object({
  id: z.string(),
  name: z.string(),
  layout: z.array(z.object({
    id: z.string(),
    type: z.enum(['chart', 'metric', 'table', 'heatmap', 'timeline']),
    position: z.object({
      x: z.number(),
      y: z.number(),
      width: z.number(),
      height: z.number()
    }),
    config: z.record(z.unknown()).default({})
  })),
  filters: z.record(z.unknown()).default({}),
  theme: z.enum(['light', 'dark']).default('light')
});

export type DashboardConfig = z.infer<typeof DashboardConfigSchema>;

// API Response Types
export const ApiResponseSchema = z.object({
  success: z.boolean(),
  data: z.unknown().optional(),
  error: z.string().optional(),
  timestamp: z.string().datetime()
});

export type ApiResponse<T = unknown> = {
  success: boolean;
  data?: T;
  error?: string;
  timestamp: string;
};

// Real-time Event Types
export const RealtimeEventSchema = z.object({
  type: z.enum(['test_started', 'test_completed', 'coverage_updated', 'alert_triggered', 'metric_updated']),
  payload: z.record(z.unknown()),
  timestamp: z.string().datetime()
});

export type RealtimeEvent = z.infer<typeof RealtimeEventSchema>;

// Trend Analysis Types
export const TrendDataSchema = z.object({
  period: z.enum(['hour', 'day', 'week', 'month']),
  startDate: z.string().datetime(),
  endDate: z.string().datetime(),
  data: z.array(z.object({
    timestamp: z.string().datetime(),
    value: z.number(),
    metadata: z.record(z.unknown()).default({})
  }))
});

export type TrendData = z.infer<typeof TrendDataSchema>;

// Filter Types
export const FilterSchema = z.object({
  testSuites: z.array(z.string()).optional(),
  status: z.array(TestStatusSchema).optional(),
  dateRange: z.object({
    start: z.string().datetime(),
    end: z.string().datetime()
  }).optional(),
  tags: z.array(z.string()).optional(),
  search: z.string().optional()
});

export type Filter = z.infer<typeof FilterSchema>;