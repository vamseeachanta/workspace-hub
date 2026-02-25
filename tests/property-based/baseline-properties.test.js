const fc = require('fast-check');
const BaselineManager = require('../../src/baseline/baseline-manager');
const ComparisonEngine = require('../../src/comparison/comparison-engine');
const RuleEngine = require('../../src/rules/rule-engine');
const MockFactory = require('../fixtures/mock-factories');

describe('Property-Based Testing', () => {
  let baselineManager;
  let comparisonEngine;
  let ruleEngine;
  let mockDatabase;
  let mockLogger;

  beforeEach(() => {
    mockDatabase = createMockDatabase();
    mockLogger = createMockLogger();
    
    baselineManager = new BaselineManager({
      database: mockDatabase,
      logger: mockLogger
    });
    
    comparisonEngine = new ComparisonEngine({
      logger: mockLogger
    });
    
    ruleEngine = new RuleEngine({
      logger: mockLogger
    });
  });

  describe('Baseline Properties', () => {
    // Property: Creating a baseline with valid data should always succeed
    it('should always create baselines with valid data', () => {
      const validBaselineArb = fc.record({
        name: fc.string({ minLength: 1, maxLength: 100 }),
        description: fc.string({ maxLength: 500 }),
        projectId: fc.string({ minLength: 1, maxLength: 50 }),
        branch: fc.string({ minLength: 1, maxLength: 50 }),
        commit: fc.hexaString({ minLength: 7, maxLength: 40 })
      });

      return fc.assert(
        fc.asyncProperty(validBaselineArb, async (baselineData) => {
          mockDatabase.query.mockResolvedValueOnce({ insertId: 'baseline-123' });
          mockDatabase.query.mockResolvedValueOnce([{ ...baselineData, id: 'baseline-123' }]);

          const result = await baselineManager.createBaseline(baselineData);
          
          expect(result.id).toBeDefined();
          expect(result.name).toBe(baselineData.name);
          expect(result.projectId).toBe(baselineData.projectId);
        }),
        { numRuns: 50 }
      );
    });

    // Property: Baseline validation should be consistent
    it('should consistently validate baseline data', () => {
      const invalidBaselineArb = fc.oneof(
        // Missing required fields
        fc.record({
          description: fc.string(),
          projectId: fc.string()
          // Missing name
        }),
        // Invalid field types
        fc.record({
          name: fc.integer(), // Should be string
          projectId: fc.string(),
          branch: fc.string()
        }),
        // Empty required fields
        fc.record({
          name: fc.constant(''),
          projectId: fc.string(),
          branch: fc.string()
        })
      );

      return fc.assert(
        fc.property(invalidBaselineArb, (invalidData) => {
          expect(() => baselineManager.validateBaseline(invalidData))
            .toThrow();
        }),
        { numRuns: 30 }
      );
    });

    // Property: Baseline metrics should maintain mathematical relationships
    it('should maintain mathematical relationships in metrics', () => {
      const metricsArb = fc.record({
        testCount: fc.nat({ max: 10000 }),
        passCount: fc.nat({ max: 10000 }),
        failCount: fc.nat({ max: 10000 }),
        skipCount: fc.nat({ max: 1000 })
      }).filter(m => m.passCount + m.failCount + m.skipCount <= m.testCount);

      return fc.assert(
        fc.property(metricsArb, (metrics) => {
          const calculatedPassRate = metrics.testCount > 0 
            ? (metrics.passCount / metrics.testCount) * 100 
            : 0;
          
          expect(calculatedPassRate).toBeGreaterThanOrEqual(0);
          expect(calculatedPassRate).toBeLessThanOrEqual(100);
          expect(metrics.passCount + metrics.failCount + metrics.skipCount)
            .toBeLessThanOrEqual(metrics.testCount);
        }),
        { numRuns: 100 }
      );
    });
  });

  describe('Comparison Properties', () => {
    // Property: Comparing identical metrics should always result in 'stable' status
    it('should always return stable status for identical metrics', () => {
      const metricsArb = fc.record({
        passRate: fc.float({ min: 0, max: 100 }),
        coverage: fc.record({
          lines: fc.float({ min: 0, max: 100 }),
          branches: fc.float({ min: 0, max: 100 }),
          functions: fc.float({ min: 0, max: 100 }),
          statements: fc.float({ min: 0, max: 100 })
        }),
        performance: fc.record({
          averageExecutionTime: fc.float({ min: 0, max: 10000 }),
          memoryUsage: fc.float({ min: 0, max: 1000 })
        })
      });

      return fc.assert(
        fc.asyncProperty(metricsArb, async (metrics) => {
          const comparison = await comparisonEngine.compareMetrics(metrics, metrics);
          
          expect(comparison.summary.overallStatus).toBe('stable');
          expect(comparison.metrics.passRate.status).toBe('stable');
          expect(comparison.metrics.passRate.change).toBe(0);
        }),
        { numRuns: 50 }
      );
    });

    // Property: Change calculations should be symmetric
    it('should calculate symmetric changes', () => {
      const valueArb = fc.float({ min: 1, max: 1000 });

      return fc.assert(
        fc.property(valueArb, valueArb, (value1, value2) => {
          const change1to2 = comparisonEngine.calculateChange(value1, value2);
          const change2to1 = comparisonEngine.calculateChange(value2, value1);
          
          expect(Math.abs(change1to2.absolute)).toBeCloseTo(Math.abs(change2to1.absolute), 5);
          expect(change1to2.direction === 'increase' ? change2to1.direction : change1to2.direction)
            .toBe(change2to1.direction === 'increase' ? 'decrease' : change2to1.direction);
        }),
        { numRuns: 100 }
      );
    });

    // Property: Percentage changes should be bounded
    it('should calculate bounded percentage changes', () => {
      const changeArb = fc.tuple(
        fc.float({ min: 0.1, max: 100 }),
        fc.float({ min: 0.1, max: 100 })
      );

      return fc.assert(
        fc.property(changeArb, ([baseline, current]) => {
          const change = comparisonEngine.calculateChange(baseline, current);
          
          // Percentage change should be finite (not Infinity or NaN)
          expect(Number.isFinite(change.percentage)).toBe(true);
          
          // For values greater than 0, percentage should be calculable
          if (baseline > 0) {
            const expectedPercentage = ((current - baseline) / baseline) * 100;
            expect(change.percentage).toBeCloseTo(expectedPercentage, 2);
          }
        }),
        { numRuns: 100 }
      );
    });

    // Property: Status determination should be consistent with change direction
    it('should consistently determine status from changes', () => {
      const metricChangeArb = fc.tuple(
        fc.constantFrom('passRate', 'coverage.lines', 'performance.averageExecutionTime'),
        fc.float({ min: -50, max: 50 })
      );

      return fc.assert(
        fc.property(metricChangeArb, ([metric, change]) => {
          const status = comparisonEngine.determineStatus(metric, change);
          
          if (Math.abs(change) < 2) {
            expect(status).toBe('stable');
          } else if (metric.includes('performance') && change > 0) {
            expect(status).toBe('degradation'); // Higher execution time is worse
          } else if (!metric.includes('performance') && change > 0) {
            expect(status).toBe('improvement'); // Higher pass rate/coverage is better
          } else if (metric.includes('performance') && change < 0) {
            expect(status).toBe('improvement'); // Lower execution time is better
          } else {
            expect(status).toBe('degradation'); // Lower pass rate/coverage is worse
          }
        }),
        { numRuns: 100 }
      );
    });
  });

  describe('Rule Engine Properties', () => {
    // Property: Threshold evaluation should be monotonic
    it('should evaluate thresholds monotonically', () => {
      const thresholdTestArb = fc.record({
        metric: fc.constantFrom('passRate', 'coverage.lines', 'coverage.branches'),
        threshold: fc.float({ min: 0, max: 100 }),
        actualValue: fc.float({ min: 0, max: 100 })
      });

      return fc.assert(
        fc.asyncProperty(thresholdTestArb, async ({ metric, threshold, actualValue }) => {
          const metrics = { [metric.split('.')[0]]: metric.includes('.') 
            ? { [metric.split('.')[1]]: actualValue }
            : actualValue
          };
          
          const thresholds = { [metric.split('.')[0]]: metric.includes('.')
            ? { [metric.split('.')[1]]: { min: threshold } }
            : { min: threshold }
          };

          const violations = await ruleEngine.evaluateThresholds(metrics, thresholds);
          
          if (actualValue >= threshold) {
            expect(violations.filter(v => v.metric === metric)).toHaveLength(0);
          } else {
            expect(violations.filter(v => v.metric === metric)).toHaveLength(1);
          }
        }),
        { numRuns: 50 }
      );
    });

    // Property: Risk assessment should increase with violation severity
    it('should assess higher risk for more severe violations', () => {
      const violationsArb = fc.array(
        fc.record({
          type: fc.constantFrom('threshold_violation', 'performance_regression', 'coverage_drop'),
          severity: fc.constantFrom('warning', 'critical'),
          metric: fc.constantFrom('passRate', 'coverage.lines', 'performance.averageExecutionTime')
        }),
        { minLength: 1, maxLength: 10 }
      );

      return fc.assert(
        fc.asyncProperty(violationsArb, async (violations) => {
          const riskLevel = await ruleEngine.assessRisk(violations, {});
          
          const criticalViolations = violations.filter(v => v.severity === 'critical');
          const warningViolations = violations.filter(v => v.severity === 'warning');
          
          if (criticalViolations.length >= 3) {
            expect(riskLevel).toBe('critical');
          } else if (criticalViolations.length > 0) {
            expect(['medium', 'high', 'critical']).toContain(riskLevel);
          } else if (warningViolations.length > 0) {
            expect(['low', 'medium']).toContain(riskLevel);
          }
        }),
        { numRuns: 50 }
      );
    });

    // Property: Z-score calculations should be mathematically correct
    it('should calculate correct z-scores', () => {
      const dataArb = fc.array(
        fc.float({ min: 0, max: 1000 }),
        { minLength: 3, maxLength: 20 }
      );
      
      const testValueArb = fc.float({ min: 0, max: 1000 });

      return fc.assert(
        fc.property(dataArb, testValueArb, (data, testValue) => {
          const zScore = ruleEngine.calculateZScore(testValue, data);
          
          // Calculate expected z-score
          const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
          const variance = data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length;
          const stdDev = Math.sqrt(variance);
          
          const expectedZScore = stdDev > 0 ? (testValue - mean) / stdDev : 0;
          
          expect(zScore).toBeCloseTo(expectedZScore, 5);
          
          // Z-score should be finite
          expect(Number.isFinite(zScore)).toBe(true);
        }),
        { numRuns: 100 }
      );
    });
  });

  describe('Data Integrity Properties', () => {
    // Property: Serialization should be reversible
    it('should maintain data integrity through serialization', () => {
      const baselineArb = fc.record({
        id: fc.string(),
        name: fc.string(),
        metrics: fc.record({
          testCount: fc.nat(),
          passRate: fc.float({ min: 0, max: 100 }),
          coverage: fc.record({
            lines: fc.float({ min: 0, max: 100 }),
            branches: fc.float({ min: 0, max: 100 })
          })
        }),
        timestamp: fc.date().map(d => d.toISOString())
      });

      return fc.assert(
        fc.property(baselineArb, (baseline) => {
          const serialized = JSON.stringify(baseline);
          const deserialized = JSON.parse(serialized);
          
          expect(deserialized).toEqual(baseline);
          expect(deserialized.metrics.passRate).toBe(baseline.metrics.passRate);
          expect(deserialized.timestamp).toBe(baseline.timestamp);
        }),
        { numRuns: 100 }
      );
    });

    // Property: Validation should reject boundary violations
    it('should reject values outside valid boundaries', () => {
      const invalidMetricsArb = fc.oneof(
        // Negative values where they shouldn't be
        fc.record({
          testCount: fc.integer({ max: -1 }),
          passRate: fc.float({ min: 0, max: 100 })
        }),
        // Percentages over 100
        fc.record({
          testCount: fc.nat(),
          passRate: fc.float({ min: 100.1, max: 200 })
        }),
        // Coverage over 100%
        fc.record({
          testCount: fc.nat(),
          passRate: fc.float({ min: 0, max: 100 }),
          coverage: fc.record({
            lines: fc.float({ min: 100.1, max: 200 })
          })
        })
      );

      return fc.assert(
        fc.property(invalidMetricsArb, (invalidMetrics) => {
          expect(() => baselineManager.validateMetrics(invalidMetrics))
            .toThrow();
        }),
        { numRuns: 50 }
      );
    });
  });

  describe('Edge Case Properties', () => {
    // Property: Division by zero should be handled gracefully
    it('should handle division by zero gracefully', () => {
      const divisionTestArb = fc.tuple(
        fc.constantFrom(0, 0.0),
        fc.float({ min: 0, max: 100 })
      );

      return fc.assert(
        fc.property(divisionTestArb, ([baseline, current]) => {
          const change = comparisonEngine.calculateChange(baseline, current);
          
          expect(Number.isFinite(change.absolute)).toBe(true);
          
          if (baseline === 0 && current > 0) {
            expect(change.percentage).toBe(Infinity);
          } else if (baseline === 0 && current === 0) {
            expect(change.percentage).toBe(0);
          }
        }),
        { numRuns: 50 }
      );
    });

    // Property: Extreme values should not break the system
    it('should handle extreme values without breaking', () => {
      const extremeValuesArb = fc.oneof(
        fc.constant(Number.MAX_SAFE_INTEGER),
        fc.constant(Number.MIN_SAFE_INTEGER),
        fc.constant(Number.POSITIVE_INFINITY),
        fc.constant(Number.NEGATIVE_INFINITY),
        fc.constant(NaN),
        fc.float({ min: 1e10, max: 1e15 }),
        fc.float({ min: 1e-10, max: 1e-5 })
      );

      return fc.assert(
        fc.property(extremeValuesArb, (extremeValue) => {
          // Should not throw errors, but may return special values
          expect(() => {
            const change = comparisonEngine.calculateChange(100, extremeValue);
            // Result should be defined, even if infinite or NaN
            expect(change).toBeDefined();
            expect(change.absolute).toBeDefined();
            expect(change.percentage).toBeDefined();
          }).not.toThrow();
        }),
        { numRuns: 30 }
      );
    });
  });
});
