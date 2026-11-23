// Factory functions for creating test data

class MockFactory {
  static createBaseline(overrides = {}) {
    return {
      id: `baseline-${Date.now()}`,
      name: 'Test Baseline',
      description: 'Mock baseline for testing',
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      projectId: 'project-1',
      branch: 'main',
      commit: this.generateCommitHash(),
      status: 'active',
      metrics: this.createMetrics(),
      thresholds: this.createThresholds(),
      ...overrides
    };
  }

  static createTestRun(overrides = {}) {
    return {
      id: `test-run-${Date.now()}`,
      baselineId: 'baseline-1',
      runId: `run-${Date.now()}`,
      timestamp: new Date().toISOString(),
      branch: 'feature/test',
      commit: this.generateCommitHash(),
      status: 'completed',
      metrics: this.createMetrics(),
      tests: this.createTestResults(),
      ...overrides
    };
  }

  static createMetrics(overrides = {}) {
    return {
      testCount: this.randomInt(50, 200),
      passRate: this.randomFloat(85.0, 100.0),
      coverage: {
        lines: this.randomFloat(80.0, 95.0),
        branches: this.randomFloat(75.0, 90.0),
        functions: this.randomFloat(85.0, 98.0),
        statements: this.randomFloat(80.0, 95.0)
      },
      performance: {
        averageExecutionTime: this.randomFloat(100.0, 500.0),
        slowestTest: this.randomFloat(1000.0, 5000.0),
        fastestTest: this.randomFloat(5.0, 50.0),
        memoryUsage: this.randomFloat(100.0, 300.0)
      },
      complexity: {
        cyclomaticComplexity: this.randomFloat(2.0, 5.0),
        maintainabilityIndex: this.randomFloat(60.0, 85.0),
        technicalDebt: this.randomFloat(1.0, 4.0)
      },
      ...overrides
    };
  }

  static createThresholds(overrides = {}) {
    return {
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
      },
      ...overrides
    };
  }

  static createTestResults(count = 10) {
    const results = [];
    const suites = ['Authentication', 'Authorization', 'API', 'Database', 'UI'];
    const statuses = ['passed', 'failed', 'skipped'];
    
    for (let i = 0; i < count; i++) {
      results.push({
        name: `should ${this.generateTestName()}`,
        status: statuses[Math.floor(Math.random() * statuses.length)],
        duration: this.randomInt(10, 1000),
        file: `tests/${this.randomChoice(suites).toLowerCase()}/test-${i + 1}.test.js`,
        suite: this.randomChoice(suites),
        ...(Math.random() < 0.1 && {
          error: {
            message: this.generateErrorMessage(),
            stack: `Error: ${this.generateErrorMessage()}\n    at test-${i + 1}.test.js:${this.randomInt(10, 100)}:${this.randomInt(1, 50)}`
          }
        })
      });
    }
    
    return results;
  }

  static createComparison(baselineId, testRunId, overrides = {}) {
    const degradationTypes = ['improvement', 'stable', 'degradation'];
    const severities = ['low', 'medium', 'high', 'critical'];
    
    return {
      id: `comparison-${Date.now()}`,
      baselineId,
      testRunId,
      timestamp: new Date().toISOString(),
      status: 'completed',
      summary: {
        overallStatus: this.randomChoice(degradationTypes),
        riskLevel: this.randomChoice(severities),
        changesDetected: this.randomInt(0, 15),
        criticalIssues: this.randomInt(0, 3),
        warnings: this.randomInt(0, 8)
      },
      metrics: this.createComparisonMetrics(),
      violations: this.createViolations(),
      ...overrides
    };
  }

  static createComparisonMetrics() {
    return {
      passRate: this.createMetricComparison(95.0, 98.0),
      coverage: {
        lines: this.createMetricComparison(85.0, 92.0),
        branches: this.createMetricComparison(80.0, 88.0),
        functions: this.createMetricComparison(90.0, 95.0),
        statements: this.createMetricComparison(85.0, 91.0)
      },
      performance: {
        averageExecutionTime: this.createMetricComparison(200.0, 300.0, true),
        memoryUsage: this.createMetricComparison(150.0, 200.0, true)
      }
    };
  }

  static createMetricComparison(min, max, lowerIsBetter = false) {
    const baseline = this.randomFloat(min, max);
    const current = baseline + this.randomFloat(-max * 0.1, max * 0.1);
    const change = current - baseline;
    const changePercent = (change / baseline) * 100;
    
    let status;
    if (Math.abs(changePercent) < 2) {
      status = 'stable';
    } else if ((lowerIsBetter && change < 0) || (!lowerIsBetter && change > 0)) {
      status = 'improvement';
    } else {
      status = 'degradation';
    }
    
    return {
      baseline: Number(baseline.toFixed(2)),
      current: Number(current.toFixed(2)),
      change: Number(change.toFixed(2)),
      changePercent: Number(changePercent.toFixed(2)),
      status
    };
  }

  static createViolations(count = null) {
    const violationTypes = ['threshold_violation', 'performance_degradation', 'coverage_drop', 'test_failure'];
    const severities = ['warning', 'critical'];
    const metrics = ['passRate', 'coverage.lines', 'performance.averageExecutionTime', 'testCount'];
    
    const violations = [];
    const violationCount = count || this.randomInt(0, 5);
    
    for (let i = 0; i < violationCount; i++) {
      violations.push({
        type: this.randomChoice(violationTypes),
        severity: this.randomChoice(severities),
        metric: this.randomChoice(metrics),
        message: this.generateViolationMessage(),
        threshold: this.randomFloat(80.0, 95.0),
        actual: this.randomFloat(70.0, 100.0),
        baseline: this.randomFloat(85.0, 100.0)
      });
    }
    
    return violations;
  }

  static createAlert(comparisonId, overrides = {}) {
    const alertTypes = ['threshold_violation', 'performance_degradation', 'coverage_drop', 'test_failure'];
    const severities = ['info', 'warning', 'critical'];
    
    return {
      id: `alert-${Date.now()}`,
      comparisonId,
      type: this.randomChoice(alertTypes),
      severity: this.randomChoice(severities),
      title: this.generateAlertTitle(),
      message: this.generateAlertMessage(),
      timestamp: new Date().toISOString(),
      acknowledged: Math.random() < 0.3,
      assignee: Math.random() < 0.5 ? 'developer@example.com' : null,
      metadata: {
        metric: 'passRate',
        threshold: this.randomFloat(85.0, 95.0),
        actual: this.randomFloat(80.0, 100.0),
        baseline: this.randomFloat(90.0, 100.0)
      },
      ...overrides
    };
  }

  // Utility methods
  static randomInt(min, max) {
    return Math.floor(Math.random() * (max - min + 1)) + min;
  }

  static randomFloat(min, max, decimals = 2) {
    const value = Math.random() * (max - min) + min;
    return Number(value.toFixed(decimals));
  }

  static randomChoice(array) {
    return array[Math.floor(Math.random() * array.length)];
  }

  static generateCommitHash() {
    return Math.random().toString(36).substr(2, 12);
  }

  static generateTestName() {
    const actions = ['validate', 'handle', 'process', 'verify', 'authenticate', 'authorize', 'create', 'update', 'delete'];
    const objects = ['user input', 'database connection', 'API response', 'file upload', 'payment', 'session', 'request'];
    return `${this.randomChoice(actions)} ${this.randomChoice(objects)} correctly`;
  }

  static generateErrorMessage() {
    const errors = [
      'Timeout waiting for response',
      'Connection refused',
      'Invalid credentials',
      'Permission denied',
      'Resource not found',
      'Validation error',
      'Network error',
      'Database constraint violation'
    ];
    return this.randomChoice(errors);
  }

  static generateViolationMessage() {
    const messages = [
      'Metric value exceeded configured threshold',
      'Performance degradation detected',
      'Coverage dropped below minimum requirement',
      'Test failure rate increased significantly',
      'Memory usage exceeded limits'
    ];
    return this.randomChoice(messages);
  }

  static generateAlertTitle() {
    const titles = [
      'Test Pass Rate Below Threshold',
      'Performance Degradation Detected',
      'Coverage Drop Alert',
      'Memory Usage Warning',
      'Critical Test Failures'
    ];
    return this.randomChoice(titles);
  }

  static generateAlertMessage() {
    const messages = [
      'The test pass rate has dropped below the configured threshold',
      'Average test execution time has increased significantly',
      'Code coverage has decreased below minimum requirements',
      'Memory usage has exceeded the configured limits',
      'Multiple critical tests have failed in the latest run'
    ];
    return this.randomChoice(messages);
  }

  // Property-based testing helpers
  static generateProperty(type, constraints = {}) {
    switch (type) {
      case 'percentage':
        return this.randomFloat(constraints.min || 0, constraints.max || 100);
      case 'duration':
        return this.randomFloat(constraints.min || 1, constraints.max || 5000);
      case 'count':
        return this.randomInt(constraints.min || 0, constraints.max || 1000);
      case 'string':
        return this.generateRandomString(constraints.length || 10);
      case 'email':
        return `user${this.randomInt(1, 1000)}@example.com`;
      default:
        return null;
    }
  }

  static generateRandomString(length) {
    const chars = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
      result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
  }
}

module.exports = MockFactory;
