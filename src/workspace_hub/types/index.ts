/**
 * Core type definitions for the baseline tracking and comparison engine
 */

// Base interfaces
export interface Timestamp {
  created: Date;
  updated: Date;
}

export interface Versioned {
  version: string;
  previousVersion?: string;
}

export interface Metadata {
  [key: string]: unknown;
}

// Metric types
export interface TestResult {
  name: string;
  status: 'pass' | 'fail' | 'skip';
  duration: number;
  error?: string;
  suite?: string;
}

export interface CoverageData {
  lines: {
    total: number;
    covered: number;
    percentage: number;
  };
  functions: {
    total: number;
    covered: number;
    percentage: number;
  };
  branches: {
    total: number;
    covered: number;
    percentage: number;
  };
  statements: {
    total: number;
    covered: number;
    percentage: number;
  };
  files: CoverageFileData[];
}

export interface CoverageFileData {
  path: string;
  lines: number;
  covered: number;
  percentage: number;
  functions: number;
  functionsCovered: number;
  branches: number;
  branchesCovered: number;
}

export interface PerformanceMetric {
  name: string;
  value: number;
  unit: string;
  category: 'memory' | 'cpu' | 'network' | 'disk' | 'custom';
  metadata?: Metadata;
}

export interface MetricsSnapshot extends Timestamp, Versioned {
  id: string;
  branch: string;
  commit: string;
  environment: string;
  tests: {
    results: TestResult[];
    summary: {
      total: number;
      passed: number;
      failed: number;
      skipped: number;
      duration: number;
    };
  };
  coverage: CoverageData;
  performance: PerformanceMetric[];
  metadata: Metadata;
}

// Baseline management
export interface BaselineData extends Timestamp, Versioned {
  id: string;
  name: string;
  branch: string;
  commit: string;
  environment: string;
  metrics: MetricsSnapshot;
  isDefault: boolean;
  tags: string[];
  metadata: Metadata;
}

export interface BaselineConfig {
  storagePath: string;
  retentionPolicy: {
    maxVersions: number;
    maxAge: number; // days
  };
  mergeStrategy: 'latest' | 'best' | 'manual';
  backupEnabled: boolean;
  backupPath?: string;
}

// Comparison and rules
export interface ComparisonResult {
  metric: string;
  current: number;
  baseline: number;
  delta: number;
  deltaPercentage: number;
  status: 'improved' | 'degraded' | 'unchanged';
  threshold?: ThresholdRule;
}

export interface ThresholdRule {
  id: string;
  name: string;
  metric: string;
  type: 'absolute' | 'percentage';
  comparison: 'gte' | 'lte' | 'eq' | 'ne' | 'gt' | 'lt';
  value: number;
  severity: 'error' | 'warning' | 'info';
  progressive?: boolean;
  enabled: boolean;
  metadata?: Metadata;
}

export interface RuleEvaluationResult {
  rule: ThresholdRule;
  comparison: ComparisonResult;
  passed: boolean;
  message: string;
}

export interface ComparisonReport extends Timestamp {
  id: string;
  baselineId: string;
  currentSnapshot: MetricsSnapshot;
  baseline: BaselineData;
  summary: {
    total: number;
    passed: number;
    failed: number;
    warnings: number;
  };
  comparisons: ComparisonResult[];
  ruleEvaluations: RuleEvaluationResult[];
  recommendations: string[];
  overallStatus: 'pass' | 'fail' | 'warning';
}

// Configuration
export interface EngineConfig {
  baseline: BaselineConfig;
  rules: ThresholdRule[];
  reporting: {
    formats: ('json' | 'html' | 'markdown')[];
    outputPath: string;
    includeDetails: boolean;
    includeTrends: boolean;
  };
  metrics: {
    parseFormats: string[];
    customParsers: string[];
  };
}

// Comparison options
export interface ComparisonOptions {
  includeUnchanged?: boolean;
  precisionDigits?: number;
  customMetrics?: string[];
  excludeMetrics?: string[];
}

// Error types
export class BaselineEngineError extends Error {
  constructor(message: string, public code: string, public details?: unknown) {
    super(message);
    this.name = 'BaselineEngineError';
  }
}

export class ValidationError extends BaselineEngineError {
  constructor(message: string, details?: unknown) {
    super(message, 'VALIDATION_ERROR', details);
  }
}

export class FileSystemError extends BaselineEngineError {
  constructor(message: string, details?: unknown) {
    super(message, 'FILESYSTEM_ERROR', details);
  }
}

export class ComparisonError extends BaselineEngineError {
  constructor(message: string, details?: unknown) {
    super(message, 'COMPARISON_ERROR', details);
  }
}

// Utility types
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

export type MetricType = 'test' | 'coverage' | 'performance';

export type SortOrder = 'asc' | 'desc';

export interface FilterOptions {
  branch?: string;
  environment?: string;
  dateFrom?: Date;
  dateTo?: Date;
  tags?: string[];
  version?: string;
}

export interface SortOptions {
  field: string;
  order: SortOrder;
}