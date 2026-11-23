const RuleEngine = require('../../src/rules/rule-engine');
const MockFactory = require('../fixtures/mock-factories');
const { sampleBaseline, sampleComparison } = require('../fixtures/baseline-data');

describe('RuleEngine', () => {
  let ruleEngine;
  let mockLogger;
  let mockMetrics;

  beforeEach(() => {
    mockLogger = createMockLogger();
    mockMetrics = createMockMetrics();
    
    ruleEngine = new RuleEngine({
      logger: mockLogger,
      metrics: mockMetrics
    });
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  describe('constructor', () => {
    it('should initialize with default rules', () => {
      expect(ruleEngine.rules).toBeDefined();
      expect(ruleEngine.rules.length).toBeGreaterThan(0);
    });

    it('should load custom rules', () => {
      const customRules = [
        {
          id: 'custom_rule_1',
          name: 'Custom Pass Rate Rule',
          type: 'threshold',
          condition: 'passRate < 90',
          severity: 'warning'
        }
      ];
      
      const engine = new RuleEngine({ rules: customRules });
      expect(engine.rules).toContain(customRules[0]);
    });

    it('should validate rule definitions', () => {
      const invalidRules = [
        { id: 'invalid_rule' } // Missing required fields
      ];
      
      expect(() => new RuleEngine({ rules: invalidRules }))
        .toThrow('Invalid rule definition');
    });
  });

  describe('evaluateThresholds', () => {
    it('should evaluate pass rate thresholds', async () => {
      const metrics = { passRate: 80.0 };
      const thresholds = { passRate: { min: 85.0 } };

      const violations = await ruleEngine.evaluateThresholds(metrics, thresholds);

      expect(violations).toContainEqual(expect.objectContaining({
        type: 'threshold_violation',
        metric: 'passRate',
        severity: expect.any(String),
        threshold: 85.0,
        actual: 80.0,
        message: expect.stringContaining('below minimum threshold')
      }));
    });

    it('should evaluate coverage thresholds', async () => {
      const metrics = {
        coverage: {
          lines: 75.0,
          branches: 70.0,
          functions: 85.0,
          statements: 78.0
        }
      };
      
      const thresholds = {
        coverage: {
          lines: { min: 80.0 },
          branches: { min: 75.0 },
          functions: { min: 80.0 },
          statements: { min: 80.0 }
        }
      };

      const violations = await ruleEngine.evaluateThresholds(metrics, thresholds);

      expect(violations).toHaveLength(3); // lines, branches, statements
      expect(violations[0].metric).toBe('coverage.lines');
      expect(violations[1].metric).toBe('coverage.branches');
      expect(violations[2].metric).toBe('coverage.statements');
    });

    it('should evaluate performance thresholds', async () => {
      const metrics = {
        performance: {
          averageExecutionTime: 350.0,
          memoryUsage: 250.0,
          slowestTest: 6000
        }
      };
      
      const thresholds = {
        performance: {
          averageExecutionTime: { max: 300.0 },
          memoryUsage: { max: 200.0 },
          slowestTest: { max: 5000 }
        }
      };

      const violations = await ruleEngine.evaluateThresholds(metrics, thresholds);

      expect(violations).toHaveLength(3);
      violations.forEach(violation => {
        expect(violation.type).toBe('threshold_violation');
        expect(violation.severity).toBeDefined();
      });
    });

    it('should handle nested threshold structures', async () => {
      const metrics = {
        complexity: {
          cyclomaticComplexity: 8.5,
          maintainabilityIndex: 65.0
        }
      };
      
      const thresholds = {
        complexity: {
          cyclomaticComplexity: { max: 5.0 },
          maintainabilityIndex: { min: 70.0 }
        }
      };

      const violations = await ruleEngine.evaluateThresholds(metrics, thresholds);

      expect(violations).toHaveLength(2);
      expect(violations[0].metric).toBe('complexity.cyclomaticComplexity');
      expect(violations[1].metric).toBe('complexity.maintainabilityIndex');
    });

    it('should not create violations for values within thresholds', async () => {
      const metrics = { passRate: 95.0, coverage: { lines: 90.0 } };
      const thresholds = { passRate: { min: 90.0 }, coverage: { lines: { min: 85.0 } } };

      const violations = await ruleEngine.evaluateThresholds(metrics, thresholds);

      expect(violations).toHaveLength(0);
    });

    it('should handle missing metrics gracefully', async () => {
      const metrics = { passRate: 90.0 };
      const thresholds = {
        passRate: { min: 85.0 },
        coverage: { lines: { min: 80.0 } } // Missing in metrics
      };

      const violations = await ruleEngine.evaluateThresholds(metrics, thresholds);

      expect(violations).toContainEqual(expect.objectContaining({
        type: 'missing_metric',
        metric: 'coverage.lines',
        severity: 'warning'
      }));
    });
  });

  describe('detectAnomalies', () => {
    it('should detect statistical anomalies', async () => {
      const currentMetrics = { passRate: 50.0 }; // Significant drop
      const historicalData = [
        { passRate: 95.0 },
        { passRate: 96.0 },
        { passRate: 94.0 },
        { passRate: 97.0 },
        { passRate: 95.5 }
      ];

      const anomalies = await ruleEngine.detectAnomalies(currentMetrics, historicalData);

      expect(anomalies).toContainEqual(expect.objectContaining({
        type: 'statistical_anomaly',
        metric: 'passRate',
        severity: 'critical',
        zScore: expect.any(Number),
        message: expect.stringContaining('statistical anomaly')
      }));
    });

    it('should detect performance regressions', async () => {
      const currentMetrics = {
        performance: {
          averageExecutionTime: 500.0,
          memoryUsage: 300.0
        }
      };
      
      const historicalData = [
        { performance: { averageExecutionTime: 200.0, memoryUsage: 150.0 } },
        { performance: { averageExecutionTime: 210.0, memoryUsage: 160.0 } },
        { performance: { averageExecutionTime: 195.0, memoryUsage: 155.0 } }
      ];

      const anomalies = await ruleEngine.detectAnomalies(currentMetrics, historicalData);

      expect(anomalies.length).toBeGreaterThan(0);
      expect(anomalies).toContainEqual(expect.objectContaining({
        type: 'performance_regression',
        metric: expect.stringContaining('performance'),
        severity: expect.any(String)
      }));
    });

    it('should detect coverage drops', async () => {
      const currentMetrics = {
        coverage: {
          lines: 70.0,
          branches: 65.0
        }
      };
      
      const historicalData = [
        { coverage: { lines: 90.0, branches: 85.0 } },
        { coverage: { lines: 89.0, branches: 86.0 } },
        { coverage: { lines: 91.0, branches: 84.0 } }
      ];

      const anomalies = await ruleEngine.detectAnomalies(currentMetrics, historicalData);

      expect(anomalies).toContainEqual(expect.objectContaining({
        type: 'coverage_drop',
        metric: expect.stringContaining('coverage'),
        severity: expect.any(String)
      }));
    });

    it('should calculate z-scores correctly', () => {
      const values = [10, 12, 11, 13, 9, 14, 10, 11];
      const testValue = 20; // Outlier

      const zScore = ruleEngine.calculateZScore(testValue, values);

      expect(zScore).toBeGreaterThan(2); // Should be significant
    });

    it('should handle insufficient historical data', async () => {
      const currentMetrics = { passRate: 90.0 };
      const historicalData = [{ passRate: 95.0 }]; // Only one data point

      const anomalies = await ruleEngine.detectAnomalies(currentMetrics, historicalData);

      expect(mockLogger.warn).toHaveBeenCalledWith(
        expect.stringContaining('Insufficient historical data')
      );
    });
  });

  describe('assessRisk', () => {
    it('should assess low risk for minor violations', async () => {
      const violations = [
        {
          type: 'threshold_violation',
          severity: 'warning',
          metric: 'coverage.lines',
          impact: 'minor'
        }
      ];

      const riskLevel = await ruleEngine.assessRisk(violations, {});

      expect(riskLevel).toBe('low');
    });

    it('should assess medium risk for moderate violations', async () => {
      const violations = [
        {
          type: 'performance_regression',
          severity: 'warning',
          metric: 'performance.averageExecutionTime',
          impact: 'moderate'
        },
        {
          type: 'threshold_violation',
          severity: 'warning',
          metric: 'passRate'
        }
      ];

      const riskLevel = await ruleEngine.assessRisk(violations, {});

      expect(riskLevel).toBe('medium');
    });

    it('should assess high risk for critical violations', async () => {
      const violations = [
        {
          type: 'threshold_violation',
          severity: 'critical',
          metric: 'passRate',
          impact: 'high'
        }
      ];

      const riskLevel = await ruleEngine.assessRisk(violations, {});

      expect(riskLevel).toBe('high');
    });

    it('should assess critical risk for multiple severe violations', async () => {
      const violations = [
        {
          type: 'threshold_violation',
          severity: 'critical',
          metric: 'passRate'
        },
        {
          type: 'statistical_anomaly',
          severity: 'critical',
          metric: 'coverage.lines'
        },
        {
          type: 'performance_regression',
          severity: 'critical',
          metric: 'performance.memoryUsage'
        }
      ];

      const riskLevel = await ruleEngine.assessRisk(violations, {});

      expect(riskLevel).toBe('critical');
    });

    it('should consider metric importance in risk assessment', async () => {
      const violations = [
        {
          type: 'threshold_violation',
          severity: 'warning',
          metric: 'passRate', // High importance
          impact: 'moderate'
        }
      ];
      
      const context = {
        criticalMetrics: ['passRate']
      };

      const riskLevel = await ruleEngine.assessRisk(violations, context);

      expect(riskLevel).toBe('medium'); // Elevated due to importance
    });
  });

  describe('evaluateCustomRules', () => {
    it('should evaluate JavaScript expression rules', async () => {
      const customRule = {
        id: 'pass_rate_coverage_rule',
        name: 'Pass Rate and Coverage Rule',
        type: 'expression',
        condition: 'passRate < 90 && coverage.lines < 80',
        severity: 'critical',
        message: 'Both pass rate and coverage are below acceptable levels'
      };
      
      ruleEngine.addRule(customRule);
      
      const metrics = {
        passRate: 85.0,
        coverage: { lines: 75.0 }
      };

      const violations = await ruleEngine.evaluateCustomRules(metrics);

      expect(violations).toContainEqual(expect.objectContaining({
        ruleId: 'pass_rate_coverage_rule',
        type: 'custom_rule_violation',
        severity: 'critical',
        message: 'Both pass rate and coverage are below acceptable levels'
      }));
    });

    it('should evaluate pattern-based rules', async () => {
      const patternRule = {
        id: 'flaky_test_pattern',
        name: 'Flaky Test Detection',
        type: 'pattern',
        pattern: 'test_status_changes > 3',
        severity: 'warning',
        context: 'test_results'
      };
      
      ruleEngine.addRule(patternRule);
      
      const testResults = {
        test_status_changes: 5, // Indicates flaky behavior
        failed_tests: ['test1', 'test2']
      };

      const violations = await ruleEngine.evaluateCustomRules(testResults);

      expect(violations).toContainEqual(expect.objectContaining({
        ruleId: 'flaky_test_pattern',
        type: 'pattern_violation'
      }));
    });

    it('should handle rule evaluation errors safely', async () => {
      const faultyRule = {
        id: 'faulty_rule',
        name: 'Faulty Rule',
        type: 'expression',
        condition: 'undefined.property > 5', // Will throw error
        severity: 'warning'
      };
      
      ruleEngine.addRule(faultyRule);
      
      const metrics = { passRate: 90.0 };

      const violations = await ruleEngine.evaluateCustomRules(metrics);

      expect(mockLogger.error).toHaveBeenCalledWith(
        expect.stringContaining('Error evaluating rule'),
        expect.objectContaining({ ruleId: 'faulty_rule' })
      );
      
      // Should not throw, but log error
      expect(violations).toEqual([]);
    });
  });

  describe('rule management', () => {
    it('should add new rules', () => {
      const newRule = {
        id: 'new_rule',
        name: 'New Rule',
        type: 'threshold',
        condition: 'passRate < 95',
        severity: 'warning'
      };
      
      ruleEngine.addRule(newRule);
      
      expect(ruleEngine.rules).toContain(newRule);
    });

    it('should remove rules by ID', () => {
      const ruleId = 'rule_to_remove';
      const rule = {
        id: ruleId,
        name: 'Rule to Remove',
        type: 'threshold',
        condition: 'passRate < 50',
        severity: 'critical'
      };
      
      ruleEngine.addRule(rule);
      expect(ruleEngine.rules).toContain(rule);
      
      ruleEngine.removeRule(ruleId);
      expect(ruleEngine.rules).not.toContain(rule);
    });

    it('should update existing rules', () => {
      const ruleId = 'existing_rule';
      const originalRule = {
        id: ruleId,
        name: 'Original Rule',
        type: 'threshold',
        condition: 'passRate < 80',
        severity: 'warning'
      };
      
      ruleEngine.addRule(originalRule);
      
      const updates = {
        name: 'Updated Rule',
        condition: 'passRate < 85',
        severity: 'critical'
      };
      
      ruleEngine.updateRule(ruleId, updates);
      
      const updatedRule = ruleEngine.rules.find(r => r.id === ruleId);
      expect(updatedRule.name).toBe('Updated Rule');
      expect(updatedRule.condition).toBe('passRate < 85');
      expect(updatedRule.severity).toBe('critical');
    });

    it('should validate rule structure', () => {
      const invalidRule = {
        name: 'Missing ID',
        type: 'threshold'
        // Missing id, condition, severity
      };
      
      expect(() => ruleEngine.addRule(invalidRule))
        .toThrow('Rule must have id, name, type, condition, and severity');
    });

    it('should prevent duplicate rule IDs', () => {
      const rule1 = {
        id: 'duplicate_id',
        name: 'First Rule',
        type: 'threshold',
        condition: 'passRate < 90',
        severity: 'warning'
      };
      
      const rule2 = {
        id: 'duplicate_id',
        name: 'Second Rule',
        type: 'threshold',
        condition: 'passRate < 80',
        severity: 'critical'
      };
      
      ruleEngine.addRule(rule1);
      
      expect(() => ruleEngine.addRule(rule2))
        .toThrow('Rule with ID duplicate_id already exists');
    });
  });

  describe('edge cases and performance', () => {
    it('should handle large rule sets efficiently', async () => {
      // Add many rules
      for (let i = 0; i < 1000; i++) {
        ruleEngine.addRule({
          id: `rule_${i}`,
          name: `Rule ${i}`,
          type: 'threshold',
          condition: `passRate < ${90 + (i % 10)}`,
          severity: i % 2 === 0 ? 'warning' : 'critical'
        });
      }
      
      const metrics = { passRate: 85.0 };
      
      const startTime = Date.now();
      const violations = await ruleEngine.evaluateThresholds(metrics, {});
      const endTime = Date.now();
      
      // Should complete within reasonable time
      expect(endTime - startTime).toBeLessThan(1000);
    });

    it('should handle null/undefined metrics', async () => {
      const metrics = null;
      const thresholds = { passRate: { min: 90.0 } };

      await expect(ruleEngine.evaluateThresholds(metrics, thresholds))
        .rejects.toThrow('Invalid metrics provided');
    });

    it('should handle circular references in metrics', async () => {
      const metrics = { passRate: 90.0 };
      metrics.self = metrics; // Circular reference
      
      const thresholds = { passRate: { min: 85.0 } };

      // Should not throw due to circular reference
      const violations = await ruleEngine.evaluateThresholds(metrics, thresholds);
      expect(violations).toEqual([]);
    });

    it('should handle very large numbers', async () => {
      const metrics = {
        passRate: 90.0,
        testCount: Number.MAX_SAFE_INTEGER,
        duration: Infinity
      };
      
      const thresholds = {
        testCount: { max: 1000000 },
        duration: { max: 5000 }
      };

      const violations = await ruleEngine.evaluateThresholds(metrics, thresholds);
      
      expect(violations).toHaveLength(2);
      expect(violations[0].actual).toBe(Number.MAX_SAFE_INTEGER);
      expect(violations[1].actual).toBe(Infinity);
    });
  });
});
