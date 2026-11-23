const ComparisonEngine = require('../../src/comparison/comparison-engine');
const MockFactory = require('../fixtures/mock-factories');
const { sampleBaseline, sampleTestResults, sampleComparison } = require('../fixtures/baseline-data');

describe('ComparisonEngine', () => {
  let comparisonEngine;
  let mockLogger;
  let mockMetrics;
  let mockRuleEngine;

  beforeEach(() => {
    mockLogger = createMockLogger();
    mockMetrics = createMockMetrics();
    mockRuleEngine = {
      evaluateThresholds: jest.fn(),
      detectAnomalies: jest.fn(),
      assessRisk: jest.fn()
    };
    
    comparisonEngine = new ComparisonEngine({
      logger: mockLogger,
      metrics: mockMetrics,
      ruleEngine: mockRuleEngine
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('should initialize with required dependencies', () => {
      expect(comparisonEngine).toBeInstanceOf(ComparisonEngine);
      expect(comparisonEngine.logger).toBe(mockLogger);
      expect(comparisonEngine.ruleEngine).toBe(mockRuleEngine);
    });

    it('should use default configuration when not provided', () => {
      const engine = new ComparisonEngine({});
      expect(engine.config).toBeDefined();
      expect(engine.config.significanceThreshold).toBeDefined();
    });

    it('should merge custom configuration', () => {
      const customConfig = {
        significanceThreshold: 0.05,
        minSampleSize: 10
      };
      
      const engine = new ComparisonEngine({ config: customConfig });
      expect(engine.config.significanceThreshold).toBe(0.05);
      expect(engine.config.minSampleSize).toBe(10);
    });
  });

  describe('compareMetrics', () => {
    it('should compare baseline and current metrics', async () => {
      const baseline = sampleBaseline.metrics;
      const current = sampleTestResults.metrics;
      
      mockRuleEngine.evaluateThresholds.mockResolvedValueOnce([
        {
          type: 'threshold_violation',
          metric: 'passRate',
          severity: 'warning',
          threshold: 95.0,
          actual: current.passRate
        }
      ]);
      
      mockRuleEngine.detectAnomalies.mockResolvedValueOnce([]);
      mockRuleEngine.assessRisk.mockResolvedValueOnce('medium');

      const result = await comparisonEngine.compareMetrics(baseline, current);

      expect(result).toEqual({
        summary: {
          overallStatus: expect.any(String),
          riskLevel: 'medium',
          changesDetected: expect.any(Number),
          significantChanges: expect.any(Number)
        },
        metrics: expect.objectContaining({
          passRate: expect.objectContaining({
            baseline: baseline.passRate,
            current: current.passRate,
            change: expect.any(Number),
            changePercent: expect.any(Number),
            status: expect.stringMatching(/improvement|stable|degradation/)
          })
        }),
        violations: expect.any(Array),
        timestamp: expect.any(String)
      });
    });

    it('should detect improvements correctly', async () => {
      const baseline = { passRate: 85.0, coverage: { lines: 80.0 } };
      const current = { passRate: 95.0, coverage: { lines: 90.0 } };
      
      mockRuleEngine.evaluateThresholds.mockResolvedValueOnce([]);
      mockRuleEngine.detectAnomalies.mockResolvedValueOnce([]);
      mockRuleEngine.assessRisk.mockResolvedValueOnce('low');

      const result = await comparisonEngine.compareMetrics(baseline, current);

      expect(result.metrics.passRate.status).toBe('improvement');
      expect(result.metrics.coverage.lines.status).toBe('improvement');
      expect(result.summary.overallStatus).toBe('improvement');
    });

    it('should detect degradations correctly', async () => {
      const baseline = { passRate: 95.0, coverage: { lines: 90.0 } };
      const current = { passRate: 85.0, coverage: { lines: 80.0 } };
      
      mockRuleEngine.evaluateThresholds.mockResolvedValueOnce([
        {
          type: 'threshold_violation',
          metric: 'passRate',
          severity: 'critical'
        }
      ]);
      mockRuleEngine.detectAnomalies.mockResolvedValueOnce([]);
      mockRuleEngine.assessRisk.mockResolvedValueOnce('high');

      const result = await comparisonEngine.compareMetrics(baseline, current);

      expect(result.metrics.passRate.status).toBe('degradation');
      expect(result.metrics.coverage.lines.status).toBe('degradation');
      expect(result.summary.overallStatus).toBe('degradation');
    });

    it('should identify stable metrics', async () => {
      const baseline = { passRate: 90.0, coverage: { lines: 85.0 } };
      const current = { passRate: 90.5, coverage: { lines: 85.2 } }; // <1% change
      
      mockRuleEngine.evaluateThresholds.mockResolvedValueOnce([]);
      mockRuleEngine.detectAnomalies.mockResolvedValueOnce([]);
      mockRuleEngine.assessRisk.mockResolvedValueOnce('low');

      const result = await comparisonEngine.compareMetrics(baseline, current);

      expect(result.metrics.passRate.status).toBe('stable');
      expect(result.metrics.coverage.lines.status).toBe('stable');
    });

    it('should handle missing metrics gracefully', async () => {
      const baseline = { passRate: 90.0 };
      const current = { passRate: 85.0, newMetric: 75.0 };
      
      mockRuleEngine.evaluateThresholds.mockResolvedValueOnce([]);
      mockRuleEngine.detectAnomalies.mockResolvedValueOnce([]);
      mockRuleEngine.assessRisk.mockResolvedValueOnce('medium');

      const result = await comparisonEngine.compareMetrics(baseline, current);

      expect(result.metrics.passRate).toBeDefined();
      expect(result.metrics.newMetric).toEqual({
        baseline: null,
        current: 75.0,
        change: null,
        changePercent: null,
        status: 'new_metric'
      });
    });
  });

  describe('calculateChange', () => {
    it('should calculate absolute and percentage change', () => {
      const result = comparisonEngine.calculateChange(80.0, 90.0);
      
      expect(result).toEqual({
        absolute: 10.0,
        percentage: 12.5,
        direction: 'increase'
      });
    });

    it('should handle negative changes', () => {
      const result = comparisonEngine.calculateChange(90.0, 80.0);
      
      expect(result).toEqual({
        absolute: -10.0,
        percentage: -11.11,
        direction: 'decrease'
      });
    });

    it('should handle zero baseline', () => {
      const result = comparisonEngine.calculateChange(0, 50.0);
      
      expect(result).toEqual({
        absolute: 50.0,
        percentage: Infinity,
        direction: 'increase'
      });
    });

    it('should handle identical values', () => {
      const result = comparisonEngine.calculateChange(75.0, 75.0);
      
      expect(result).toEqual({
        absolute: 0,
        percentage: 0,
        direction: 'stable'
      });
    });

    it('should round to specified decimal places', () => {
      const result = comparisonEngine.calculateChange(33.333, 66.666, 2);
      
      expect(result.absolute).toBe(33.33);
      expect(result.percentage).toBe(100.0);
    });
  });

  describe('determineStatus', () => {
    it('should determine improvement status', () => {
      const testCases = [
        { metric: 'passRate', change: 5.0, expected: 'improvement' },
        { metric: 'coverage.lines', change: 3.0, expected: 'improvement' },
        { metric: 'performance.averageExecutionTime', change: -10.0, expected: 'improvement' },
        { metric: 'performance.memoryUsage', change: -5.0, expected: 'improvement' }
      ];

      testCases.forEach(({ metric, change, expected }) => {
        const status = comparisonEngine.determineStatus(metric, change);
        expect(status).toBe(expected);
      });
    });

    it('should determine degradation status', () => {
      const testCases = [
        { metric: 'passRate', change: -5.0, expected: 'degradation' },
        { metric: 'coverage.lines', change: -3.0, expected: 'degradation' },
        { metric: 'performance.averageExecutionTime', change: 10.0, expected: 'degradation' },
        { metric: 'performance.memoryUsage', change: 15.0, expected: 'degradation' }
      ];

      testCases.forEach(({ metric, change, expected }) => {
        const status = comparisonEngine.determineStatus(metric, change);
        expect(status).toBe(expected);
      });
    });

    it('should determine stable status for small changes', () => {
      const testCases = [
        { metric: 'passRate', change: 0.5, expected: 'stable' },
        { metric: 'coverage.lines', change: -0.8, expected: 'stable' },
        { metric: 'performance.averageExecutionTime', change: 1.0, expected: 'stable' }
      ];

      testCases.forEach(({ metric, change, expected }) => {
        const status = comparisonEngine.determineStatus(metric, change);
        expect(status).toBe(expected);
      });
    });

    it('should handle custom significance thresholds', () => {
      const customEngine = new ComparisonEngine({
        config: { significanceThreshold: 0.1 } // 10% threshold
      });

      expect(customEngine.determineStatus('passRate', 5.0)).toBe('stable'); // Below 10%
      expect(customEngine.determineStatus('passRate', 15.0)).toBe('improvement'); // Above 10%
    });
  });

  describe('compareTestResults', () => {
    it('should compare individual test results', async () => {
      const baselineTests = [
        { name: 'test1', status: 'passed', duration: 100 },
        { name: 'test2', status: 'passed', duration: 200 },
        { name: 'test3', status: 'failed', duration: 150 }
      ];
      
      const currentTests = [
        { name: 'test1', status: 'passed', duration: 120 },
        { name: 'test2', status: 'failed', duration: 250 },
        { name: 'test3', status: 'passed', duration: 130 },
        { name: 'test4', status: 'passed', duration: 80 } // New test
      ];

      const result = await comparisonEngine.compareTestResults(baselineTests, currentTests);

      expect(result).toEqual({
        summary: {
          totalTests: {
            baseline: 3,
            current: 4,
            added: 1,
            removed: 0
          },
          statusChanges: {
            improved: 1, // test3: failed -> passed
            degraded: 1, // test2: passed -> failed
            stable: 1    // test1: passed -> passed
          }
        },
        changes: expect.arrayContaining([
          expect.objectContaining({
            testName: 'test2',
            changeType: 'status_change',
            baseline: { status: 'passed' },
            current: { status: 'failed' },
            impact: 'degradation'
          }),
          expect.objectContaining({
            testName: 'test4',
            changeType: 'new_test',
            baseline: null,
            current: { status: 'passed' }
          })
        ])
      });
    });

    it('should detect performance regressions in tests', async () => {
      const baselineTests = [
        { name: 'slow_test', status: 'passed', duration: 1000 }
      ];
      
      const currentTests = [
        { name: 'slow_test', status: 'passed', duration: 5000 } // 5x slower
      ];

      const result = await comparisonEngine.compareTestResults(baselineTests, currentTests);

      const performanceChange = result.changes.find(c => 
        c.testName === 'slow_test' && c.changeType === 'performance_change'
      );
      
      expect(performanceChange).toBeDefined();
      expect(performanceChange.impact).toBe('degradation');
      expect(performanceChange.details.durationChange).toBe(4000);
    });

    it('should identify flaky tests', async () => {
      const baselineTests = [
        { name: 'flaky_test', status: 'passed', duration: 100 }
      ];
      
      const currentTests = [
        { name: 'flaky_test', status: 'failed', duration: 100 }
      ];
      
      // Mock historical data showing this test has been flaky
      comparisonEngine.getTestHistory = jest.fn().mockResolvedValueOnce([
        { status: 'passed' },
        { status: 'failed' },
        { status: 'passed' },
        { status: 'failed' },
        { status: 'passed' }
      ]);

      const result = await comparisonEngine.compareTestResults(baselineTests, currentTests);

      const flakyTest = result.changes.find(c => 
        c.testName === 'flaky_test' && c.changeType === 'flaky_behavior'
      );
      
      expect(flakyTest).toBeDefined();
      expect(flakyTest.details.flakinessScore).toBeGreaterThan(0.5);
    });
  });

  describe('calculateOverallStatus', () => {
    it('should determine overall improvement', () => {
      const metrics = {
        passRate: { status: 'improvement' },
        coverage: { lines: { status: 'improvement' } },
        performance: { averageExecutionTime: { status: 'stable' } }
      };
      
      const violations = [];

      const status = comparisonEngine.calculateOverallStatus(metrics, violations);
      expect(status).toBe('improvement');
    });

    it('should determine overall degradation', () => {
      const metrics = {
        passRate: { status: 'degradation' },
        coverage: { lines: { status: 'stable' } }
      };
      
      const violations = [
        { severity: 'critical', type: 'threshold_violation' }
      ];

      const status = comparisonEngine.calculateOverallStatus(metrics, violations);
      expect(status).toBe('degradation');
    });

    it('should determine stable status', () => {
      const metrics = {
        passRate: { status: 'stable' },
        coverage: { lines: { status: 'stable' } },
        performance: { averageExecutionTime: { status: 'stable' } }
      };
      
      const violations = [];

      const status = comparisonEngine.calculateOverallStatus(metrics, violations);
      expect(status).toBe('stable');
    });

    it('should prioritize critical violations', () => {
      const metrics = {
        passRate: { status: 'improvement' },
        coverage: { lines: { status: 'improvement' } }
      };
      
      const violations = [
        { severity: 'critical', type: 'threshold_violation' },
        { severity: 'warning', type: 'performance_degradation' }
      ];

      const status = comparisonEngine.calculateOverallStatus(metrics, violations);
      expect(status).toBe('degradation');
    });
  });

  describe('statistical analysis', () => {
    it('should perform statistical significance testing', async () => {
      const baseline = {
        passRate: 90.0,
        sampleSize: 1000,
        variance: 2.5
      };
      
      const current = {
        passRate: 85.0,
        sampleSize: 1000,
        variance: 3.0
      };

      const result = await comparisonEngine.performStatisticalTest(baseline, current);

      expect(result).toEqual({
        isSignificant: expect.any(Boolean),
        pValue: expect.any(Number),
        confidenceInterval: expect.objectContaining({
          lower: expect.any(Number),
          upper: expect.any(Number)
        }),
        testType: 'two_sample_t_test'
      });
    });

    it('should detect outliers in metrics', async () => {
      const metrics = {
        testDurations: [100, 105, 98, 102, 5000, 99, 103] // 5000 is outlier
      };

      const outliers = await comparisonEngine.detectOutliers(metrics.testDurations);

      expect(outliers).toContain(5000);
    });

    it('should calculate confidence intervals', () => {
      const data = [85, 87, 89, 91, 93, 95, 97];
      const confidence = 0.95;

      const interval = comparisonEngine.calculateConfidenceInterval(data, confidence);

      expect(interval).toEqual({
        lower: expect.any(Number),
        upper: expect.any(Number),
        mean: expect.any(Number),
        margin: expect.any(Number)
      });
      
      expect(interval.lower).toBeLessThan(interval.upper);
    });
  });

  describe('edge cases and error handling', () => {
    it('should handle empty metrics gracefully', async () => {
      const result = await comparisonEngine.compareMetrics({}, {});

      expect(result.summary.overallStatus).toBe('stable');
      expect(result.metrics).toEqual({});
    });

    it('should handle null/undefined values', async () => {
      const baseline = { passRate: null, coverage: undefined };
      const current = { passRate: 90.0, coverage: { lines: 85.0 } };

      const result = await comparisonEngine.compareMetrics(baseline, current);

      expect(result.metrics.passRate.baseline).toBeNull();
      expect(result.metrics.coverage.baseline).toBeNull();
    });

    it('should handle extreme values', async () => {
      const baseline = { passRate: 0.001 };
      const current = { passRate: 99.999 };

      const result = await comparisonEngine.compareMetrics(baseline, current);

      expect(result.metrics.passRate.changePercent).toBeGreaterThan(1000000);
      expect(result.metrics.passRate.status).toBe('improvement');
    });

    it('should handle invalid metric types', async () => {
      const baseline = { passRate: 'invalid' };
      const current = { passRate: 90.0 };

      await expect(comparisonEngine.compareMetrics(baseline, current))
        .rejects.toThrow('Invalid metric values');
    });

    it('should handle concurrent comparisons', async () => {
      const baseline = MockFactory.createMetrics();
      const current = MockFactory.createMetrics();
      
      mockRuleEngine.evaluateThresholds.mockResolvedValue([]);
      mockRuleEngine.detectAnomalies.mockResolvedValue([]);
      mockRuleEngine.assessRisk.mockResolvedValue('low');

      const promises = Array(10).fill(null).map(() => 
        comparisonEngine.compareMetrics(baseline, current)
      );

      const results = await Promise.all(promises);
      
      expect(results).toHaveLength(10);
      results.forEach(result => {
        expect(result.summary).toBeDefined();
        expect(result.metrics).toBeDefined();
      });
    });

    it('should handle memory pressure during large comparisons', async () => {
      const largeBaseline = {
        tests: Array(10000).fill(null).map((_, i) => MockFactory.createTestResults(1)[0])
      };
      
      const largeCurrent = {
        tests: Array(10000).fill(null).map((_, i) => MockFactory.createTestResults(1)[0])
      };

      const startMemory = process.memoryUsage().heapUsed;
      
      await comparisonEngine.compareTestResults(largeBaseline.tests, largeCurrent.tests);
      
      const endMemory = process.memoryUsage().heapUsed;
      const memoryIncrease = endMemory - startMemory;
      
      // Should not use excessive memory (less than 100MB)
      expect(memoryIncrease).toBeLessThan(100 * 1024 * 1024);
    });
  });
});
