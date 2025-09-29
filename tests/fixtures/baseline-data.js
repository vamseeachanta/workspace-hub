// Sample baseline data for testing

const sampleBaseline = {
  id: 'baseline-1',
  name: 'User Authentication Tests',
  description: 'Baseline for user authentication functionality',
  createdAt: '2024-01-15T10:00:00Z',
  updatedAt: '2024-01-15T10:00:00Z',
  projectId: 'project-1',
  branch: 'main',
  commit: 'abc123def456',
  status: 'active',
  metrics: {
    testCount: 125,
    passRate: 98.4,
    coverage: {
      lines: 92.5,
      branches: 88.7,
      functions: 95.2,
      statements: 91.8
    },
    performance: {
      averageExecutionTime: 245.6,
      slowestTest: 2340,
      fastestTest: 12,
      memoryUsage: 156.7
    },
    complexity: {
      cyclomaticComplexity: 3.2,
      maintainabilityIndex: 78.5,
      technicalDebt: 2.1
    }
  },
  thresholds: {
    passRate: { min: 95.0, max: 100.0 },
    coverage: {
      lines: { min: 85.0 },
      branches: { min: 80.0 },
      functions: { min: 90.0 },
      statements: { min: 85.0 }
    },
    performance: {
      averageExecutionTime: { max: 300.0 },
      memoryUsage: { max: 200.0 }
    }
  }
};

const sampleTestResults = {
  id: 'test-run-1',
  baselineId: 'baseline-1',
  runId: 'run-2024-01-16-001',
  timestamp: '2024-01-16T14:30:00Z',
  branch: 'feature/login-improvements',
  commit: 'def456ghi789',
  status: 'completed',
  metrics: {
    testCount: 127,
    passRate: 96.8,
    coverage: {
      lines: 90.2,
      branches: 85.4,
      functions: 93.7,
      statements: 89.5
    },
    performance: {
      averageExecutionTime: 267.3,
      slowestTest: 2890,
      fastestTest: 15,
      memoryUsage: 178.2
    },
    complexity: {
      cyclomaticComplexity: 3.4,
      maintainabilityIndex: 76.8,
      technicalDebt: 2.3
    }
  },
  tests: [
    {
      name: 'should authenticate valid user',
      status: 'passed',
      duration: 156,
      file: 'tests/auth/login.test.js',
      suite: 'Authentication'
    },
    {
      name: 'should reject invalid credentials',
      status: 'passed',
      duration: 89,
      file: 'tests/auth/login.test.js',
      suite: 'Authentication'
    },
    {
      name: 'should handle password reset flow',
      status: 'failed',
      duration: 2890,
      file: 'tests/auth/password-reset.test.js',
      suite: 'Password Management',
      error: {
        message: 'Timeout waiting for email confirmation',
        stack: 'Error: Timeout\n    at /tests/auth/password-reset.test.js:45:12'
      }
    }
  ]
};

const sampleComparison = {
  id: 'comparison-1',
  baselineId: 'baseline-1',
  testRunId: 'test-run-1',
  timestamp: '2024-01-16T14:35:00Z',
  status: 'completed',
  summary: {
    overallStatus: 'degradation',
    riskLevel: 'medium',
    changesDetected: 7,
    criticalIssues: 2,
    warnings: 3
  },
  metrics: {
    passRate: {
      baseline: 98.4,
      current: 96.8,
      change: -1.6,
      status: 'degradation'
    },
    coverage: {
      lines: {
        baseline: 92.5,
        current: 90.2,
        change: -2.3,
        status: 'degradation'
      },
      branches: {
        baseline: 88.7,
        current: 85.4,
        change: -3.3,
        status: 'degradation'
      }
    },
    performance: {
      averageExecutionTime: {
        baseline: 245.6,
        current: 267.3,
        change: 21.7,
        status: 'degradation'
      },
      memoryUsage: {
        baseline: 156.7,
        current: 178.2,
        change: 21.5,
        status: 'warning'
      }
    }
  },
  violations: [
    {
      type: 'threshold_violation',
      severity: 'critical',
      metric: 'passRate',
      message: 'Pass rate fell below minimum threshold',
      threshold: 95.0,
      actual: 96.8,
      baseline: 98.4
    },
    {
      type: 'performance_degradation',
      severity: 'warning',
      metric: 'averageExecutionTime',
      message: 'Average execution time increased significantly',
      threshold: 300.0,
      actual: 267.3,
      baseline: 245.6,
      change: '+8.8%'
    }
  ]
};

const sampleAlerts = [
  {
    id: 'alert-1',
    comparisonId: 'comparison-1',
    type: 'threshold_violation',
    severity: 'critical',
    title: 'Test Pass Rate Below Threshold',
    message: 'The test pass rate has dropped below the configured threshold of 95%',
    timestamp: '2024-01-16T14:35:00Z',
    acknowledged: false,
    assignee: null,
    metadata: {
      metric: 'passRate',
      threshold: 95.0,
      actual: 96.8,
      baseline: 98.4
    }
  },
  {
    id: 'alert-2',
    comparisonId: 'comparison-1',
    type: 'performance_degradation',
    severity: 'warning',
    title: 'Performance Degradation Detected',
    message: 'Average test execution time has increased by 8.8%',
    timestamp: '2024-01-16T14:35:00Z',
    acknowledged: true,
    assignee: 'developer@example.com',
    metadata: {
      metric: 'averageExecutionTime',
      change: '+8.8%',
      baseline: 245.6,
      current: 267.3
    }
  }
];

const edgeCases = {
  emptyBaseline: {
    id: 'baseline-empty',
    name: 'Empty Baseline',
    metrics: {
      testCount: 0,
      passRate: 0,
      coverage: { lines: 0, branches: 0, functions: 0, statements: 0 },
      performance: { averageExecutionTime: 0, memoryUsage: 0 }
    }
  },
  
  extremeValues: {
    id: 'baseline-extreme',
    name: 'Extreme Values Baseline',
    metrics: {
      testCount: 999999,
      passRate: 100.0,
      coverage: { lines: 100.0, branches: 100.0, functions: 100.0, statements: 100.0 },
      performance: { averageExecutionTime: 0.001, memoryUsage: 999999.9 }
    }
  },
  
  invalidData: {
    id: 'baseline-invalid',
    name: 'Invalid Data Baseline',
    metrics: {
      testCount: -1,
      passRate: 150.0,
      coverage: { lines: -5.0, branches: 'invalid', functions: null, statements: undefined },
      performance: { averageExecutionTime: 'fast', memoryUsage: NaN }
    }
  }
};

module.exports = {
  sampleBaseline,
  sampleTestResults,
  sampleComparison,
  sampleAlerts,
  edgeCases
};
