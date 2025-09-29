/**
 * Unit tests for ComparisonEngine
 */

import { ComparisonEngine } from '../../src/comparison/comparison-engine';
import { MetricsSnapshot, BaselineData, ThresholdRule } from '../../src/types';

describe('ComparisonEngine', () => {
  let comparisonEngine: ComparisonEngine;
  let currentSnapshot: MetricsSnapshot;
  let baselineSnapshot: MetricsSnapshot;
  let baseline: BaselineData;

  beforeEach(() => {
    comparisonEngine = new ComparisonEngine();

    baselineSnapshot = {
      id: 'baseline-snapshot',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      tests: {
        results: [],
        summary: {
          total: 100,
          passed: 95,
          failed: 5,
          skipped: 0,
          duration: 10000
        }
      },
      coverage: {
        lines: { total: 1000, covered: 800, percentage: 80 },
        functions: { total: 200, covered: 160, percentage: 80 },
        branches: { total: 300, covered: 240, percentage: 80 },
        statements: { total: 1000, covered: 800, percentage: 80 },
        files: []
      },
      performance: [
        { name: 'memory', value: 100, unit: 'MB', category: 'memory' },
        { name: 'cpu', value: 50, unit: '%', category: 'cpu' }
      ],
      metadata: {},
      created: new Date('2023-01-01'),
      updated: new Date('2023-01-01')
    };

    currentSnapshot = {
      id: 'current-snapshot',
      branch: 'main',
      commit: 'def456',
      environment: 'production',
      version: '1.1.0',
      tests: {
        results: [],
        summary: {
          total: 110,
          passed: 105,
          failed: 5,
          skipped: 0,
          duration: 9000
        }
      },
      coverage: {
        lines: { total: 1100, covered: 880, percentage: 80 },
        functions: { total: 220, covered: 176, percentage: 80 },
        branches: { total: 330, covered: 264, percentage: 80 },
        statements: { total: 1100, covered: 880, percentage: 80 },
        files: []
      },
      performance: [
        { name: 'memory', value: 105, unit: 'MB', category: 'memory' },
        { name: 'cpu', value: 45, unit: '%', category: 'cpu' }
      ],
      metadata: {},
      created: new Date('2023-01-02'),
      updated: new Date('2023-01-02')
    };

    baseline = {
      id: 'baseline-1',
      name: 'test-baseline',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      metrics: baselineSnapshot,
      isDefault: true,
      tags: [],
      metadata: {},
      created: new Date('2023-01-01'),
      updated: new Date('2023-01-01')
    };
  });

  describe('compareMetric', () => {
    it('should compare two metric values correctly', () => {
      const result = comparisonEngine.compareMetric('test.metric', 100, 80);

      expect(result.metric).toBe('test.metric');
      expect(result.current).toBe(100);
      expect(result.baseline).toBe(80);
      expect(result.delta).toBe(20);
      expect(result.deltaPercentage).toBe(25);
      expect(result.status).toBe('improved');
    });

    it('should detect degradation', () => {
      const result = comparisonEngine.compareMetric('test.metric', 70, 80);

      expect(result.delta).toBe(-10);
      expect(result.deltaPercentage).toBe(-12.5);
      expect(result.status).toBe('degraded');
    });

    it('should detect unchanged values', () => {
      const result = comparisonEngine.compareMetric('test.metric', 80, 80);

      expect(result.delta).toBe(0);
      expect(result.deltaPercentage).toBe(0);
      expect(result.status).toBe('unchanged');
    });

    it('should handle zero baseline values', () => {
      const result = comparisonEngine.compareMetric('test.metric', 50, 0);

      expect(result.deltaPercentage).toBe(100);
      expect(result.status).toBe('improved');
    });

    it('should handle lower-is-better metrics', () => {
      const result = comparisonEngine.compareMetric('test.failed', 5, 10);

      expect(result.status).toBe('improved'); // Lower failures is better
    });

    it('should round values to specified precision', () => {
      const result = comparisonEngine.compareMetric('test.metric', 100.12345, 80.98765, 2);

      expect(result.current).toBe(100.12);
      expect(result.baseline).toBe(80.99);
    });
  });

  describe('compare', () => {
    it('should generate comprehensive comparison report', async () => {
      const rules: ThresholdRule[] = [
        {
          id: 'coverage-rule',
          name: 'Minimum Coverage',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 75,
          severity: 'error',
          progressive: false,
          enabled: true
        }
      ];

      const report = await comparisonEngine.compare(currentSnapshot, baseline, rules);

      expect(report).toBeDefined();
      expect(report.baselineId).toBe(baseline.id);
      expect(report.currentSnapshot).toBe(currentSnapshot);
      expect(report.baseline).toBe(baseline);
      expect(report.comparisons.length).toBeGreaterThan(0);
      expect(report.ruleEvaluations.length).toBe(1);
      expect(report.summary.total).toBe(1);
      expect(report.overallStatus).toMatch(/pass|fail|warning/);
      expect(report.recommendations.length).toBeGreaterThan(0);
    });

    it('should include test metrics in comparisons', async () => {
      const report = await comparisonEngine.compare(currentSnapshot, baseline);

      const testComparisons = report.comparisons.filter(c => c.metric.startsWith('tests.'));

      expect(testComparisons.length).toBeGreaterThan(0);
      expect(testComparisons.some(c => c.metric === 'tests.total')).toBe(true);
      expect(testComparisons.some(c => c.metric === 'tests.passed')).toBe(true);
      expect(testComparisons.some(c => c.metric === 'tests.failed')).toBe(true);
    });

    it('should include coverage metrics in comparisons', async () => {
      const report = await comparisonEngine.compare(currentSnapshot, baseline);

      const coverageComparisons = report.comparisons.filter(c => c.metric.startsWith('coverage.'));

      expect(coverageComparisons.length).toBeGreaterThan(0);
      expect(coverageComparisons.some(c => c.metric === 'coverage.lines.percentage')).toBe(true);
      expect(coverageComparisons.some(c => c.metric === 'coverage.functions.percentage')).toBe(true);
    });

    it('should include performance metrics in comparisons', async () => {
      const report = await comparisonEngine.compare(currentSnapshot, baseline);

      const performanceComparisons = report.comparisons.filter(c => c.metric.startsWith('performance.'));

      expect(performanceComparisons.length).toBeGreaterThan(0);
    });

    it('should exclude unchanged metrics when option is set', async () => {
      // Make all metrics identical
      const identicalSnapshot = { ...currentSnapshot };
      identicalSnapshot.tests = { ...baselineSnapshot.tests };
      identicalSnapshot.coverage = { ...baselineSnapshot.coverage };
      identicalSnapshot.performance = [...baselineSnapshot.performance];

      const report = await comparisonEngine.compare(
        identicalSnapshot,
        baseline,
        [],
        { includeUnchanged: false }
      );

      expect(report.comparisons.length).toBe(0);
    });

    it('should apply precision to all comparisons', async () => {
      const report = await comparisonEngine.compare(
        currentSnapshot,
        baseline,
        [],
        { precisionDigits: 1 }
      );

      for (const comparison of report.comparisons) {
        expect(comparison.current.toString().split('.')[1]?.length || 0).toBeLessThanOrEqual(1);
        expect(comparison.baseline.toString().split('.')[1]?.length || 0).toBeLessThanOrEqual(1);
      }
    });
  });

  describe('rule evaluation', () => {
    it('should evaluate threshold rules correctly', async () => {
      const rules: ThresholdRule[] = [
        {
          id: 'pass-rule',
          name: 'Passing Rule',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 75,
          severity: 'error',
          progressive: false,
          enabled: true
        },
        {
          id: 'fail-rule',
          name: 'Failing Rule',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 90,
          severity: 'error',
          progressive: false,
          enabled: true
        }
      ];

      const report = await comparisonEngine.compare(currentSnapshot, baseline, rules);

      expect(report.ruleEvaluations).toHaveLength(2);

      const passedEvaluations = report.ruleEvaluations.filter(e => e.passed);
      const failedEvaluations = report.ruleEvaluations.filter(e => !e.passed);

      expect(passedEvaluations).toHaveLength(1);
      expect(failedEvaluations).toHaveLength(1);
    });

    it('should handle percentage-based rules', async () => {
      const rules: ThresholdRule[] = [
        {
          id: 'percentage-rule',
          name: 'Max Coverage Decrease',
          metric: 'coverage.lines.percentage',
          type: 'percentage',
          comparison: 'gte',
          value: -5, // Max 5% decrease allowed
          severity: 'warning',
          progressive: false,
          enabled: true
        }
      ];

      const report = await comparisonEngine.compare(currentSnapshot, baseline, rules);

      expect(report.ruleEvaluations).toHaveLength(1);
      expect(report.ruleEvaluations[0].passed).toBe(true); // 0% change >= -5%
    });

    it('should skip disabled rules', async () => {
      const rules: ThresholdRule[] = [
        {
          id: 'disabled-rule',
          name: 'Disabled Rule',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 90,
          severity: 'error',
          progressive: false,
          enabled: false
        }
      ];

      const report = await comparisonEngine.compare(currentSnapshot, baseline, rules);

      expect(report.ruleEvaluations).toHaveLength(0);
    });

    it('should handle wildcard metric patterns', async () => {
      const rules: ThresholdRule[] = [
        {
          id: 'wildcard-rule',
          name: 'Coverage Wildcard',
          metric: 'coverage.*.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 75,
          severity: 'warning',
          progressive: false,
          enabled: true
        }
      ];

      const report = await comparisonEngine.compare(currentSnapshot, baseline, rules);

      expect(report.ruleEvaluations.length).toBeGreaterThan(1); // Should match multiple coverage metrics
    });
  });

  describe('summary calculation', () => {
    it('should calculate summary statistics correctly', async () => {
      const rules: ThresholdRule[] = [
        {
          id: 'error-rule',
          name: 'Error Rule',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 95,
          severity: 'error',
          progressive: false,
          enabled: true
        },
        {
          id: 'warning-rule',
          name: 'Warning Rule',
          metric: 'coverage.functions.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 95,
          severity: 'warning',
          progressive: false,
          enabled: true
        }
      ];

      const report = await comparisonEngine.compare(currentSnapshot, baseline, rules);

      expect(report.summary.total).toBe(2);
      expect(report.summary.passed).toBe(0);
      expect(report.summary.failed).toBe(1); // Error rule failed
      expect(report.summary.warnings).toBe(1); // Warning rule failed
    });
  });

  describe('recommendations', () => {
    it('should generate relevant recommendations', async () => {
      // Set up a scenario with failing tests
      const snapshotWithFailures = {
        ...currentSnapshot,
        tests: {
          ...currentSnapshot.tests,
          summary: {
            ...currentSnapshot.tests.summary,
            failed: 10,
            passed: 95
          }
        }
      };

      const report = await comparisonEngine.compare(snapshotWithFailures, baseline);

      expect(report.recommendations.length).toBeGreaterThan(0);
      expect(report.recommendations.some(r => r.includes('failing'))).toBe(true);
    });

    it('should recommend coverage improvements', async () => {
      // Set up low coverage scenario
      const lowCoverageSnapshot = {
        ...currentSnapshot,
        coverage: {
          ...currentSnapshot.coverage,
          lines: { total: 1000, covered: 600, percentage: 60 }
        }
      };

      const report = await comparisonEngine.compare(lowCoverageSnapshot, baseline);

      expect(report.recommendations.some(r => r.includes('coverage'))).toBe(true);
    });

    it('should provide positive feedback when all metrics are good', async () => {
      const report = await comparisonEngine.compare(currentSnapshot, baseline);

      expect(report.recommendations.some(r =>
        r.includes('acceptable') || r.includes('good')
      )).toBe(true);
    });
  });

  describe('overall status determination', () => {
    it('should return fail when error rules fail', async () => {
      const rules: ThresholdRule[] = [
        {
          id: 'error-rule',
          name: 'Critical Rule',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 95,
          severity: 'error',
          progressive: false,
          enabled: true
        }
      ];

      const report = await comparisonEngine.compare(currentSnapshot, baseline, rules);

      expect(report.overallStatus).toBe('fail');
    });

    it('should return warning when only warning rules fail', async () => {
      const rules: ThresholdRule[] = [
        {
          id: 'warning-rule',
          name: 'Warning Rule',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 95,
          severity: 'warning',
          progressive: false,
          enabled: true
        }
      ];

      const report = await comparisonEngine.compare(currentSnapshot, baseline, rules);

      expect(report.overallStatus).toBe('warning');
    });

    it('should return pass when all rules pass', async () => {
      const rules: ThresholdRule[] = [
        {
          id: 'pass-rule',
          name: 'Passing Rule',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 70,
          severity: 'error',
          progressive: false,
          enabled: true
        }
      ];

      const report = await comparisonEngine.compare(currentSnapshot, baseline, rules);

      expect(report.overallStatus).toBe('pass');
    });
  });

  describe('analyzeTrend', () => {
    it('should analyze metric trends across snapshots', async () => {
      const snapshots = [
        { ...baselineSnapshot, created: new Date('2023-01-01') },
        { ...currentSnapshot, created: new Date('2023-01-02') },
        {
          ...currentSnapshot,
          id: 'snapshot-3',
          created: new Date('2023-01-03'),
          coverage: {
            ...currentSnapshot.coverage,
            lines: { total: 1200, covered: 960, percentage: 80 }
          }
        }
      ];

      const trend = await comparisonEngine.analyzeTrend(snapshots, 'coverage.lines.percentage');

      expect(trend).toBeDefined();
      expect(trend.trend).toMatch(/improving|declining|stable|volatile/);
      expect(typeof trend.slope).toBe('number');
      expect(typeof trend.correlation).toBe('number');
      expect(typeof trend.volatility).toBe('number');
      expect(trend.values).toHaveLength(3);
    });

    it('should handle insufficient data for trend analysis', async () => {
      const snapshots = [baselineSnapshot];

      await expect(
        comparisonEngine.analyzeTrend(snapshots, 'coverage.lines.percentage')
      ).rejects.toThrow('At least 2 snapshots required');
    });

    it('should handle missing metric paths', async () => {
      const snapshots = [baselineSnapshot, currentSnapshot];

      const trend = await comparisonEngine.analyzeTrend(snapshots, 'non.existent.metric');

      expect(trend.values.every(v => v.value === 0)).toBe(true);
    });
  });

  describe('error handling', () => {
    it('should handle invalid snapshot data', async () => {
      const invalidSnapshot = {} as MetricsSnapshot;

      await expect(
        comparisonEngine.compare(invalidSnapshot, baseline)
      ).rejects.toThrow();
    });

    it('should handle invalid baseline data', async () => {
      const invalidBaseline = {} as BaselineData;

      await expect(
        comparisonEngine.compare(currentSnapshot, invalidBaseline)
      ).rejects.toThrow();
    });

    it('should handle missing metric data gracefully', async () => {
      const incompleteSnapshot = {
        ...currentSnapshot,
        coverage: undefined as any
      };

      // Should not throw but handle gracefully
      const report = await comparisonEngine.compare(incompleteSnapshot, baseline);
      expect(report).toBeDefined();
    });
  });
});