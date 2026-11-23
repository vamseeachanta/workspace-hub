/**
 * Unit tests for RuleEngine
 */

import { RuleEngine, RuleEngineConfig } from '../../src/rules/rule-engine';
import { FileUtils } from '../../src/utils/file-utils';
import { ThresholdRule, MetricsSnapshot, ComparisonResult } from '../../src/types';
import * as fs from 'fs-extra';
import * as path from 'path';

// Mock FileUtils
jest.mock('../../src/utils/file-utils');
const MockedFileUtils = FileUtils as jest.Mocked<typeof FileUtils>;

describe('RuleEngine', () => {
  let ruleEngine: RuleEngine;
  let config: RuleEngineConfig;
  let tempDir: string;

  beforeEach(async () => {
    tempDir = await fs.mkdtemp(path.join(require('os').tmpdir(), 'rule-test-'));

    config = {
      rulesPath: path.join(tempDir, 'rules.json'),
      autoSave: false,
      enableProgressive: true,
      progressiveSteps: 5,
      defaultSeverity: 'warning'
    };

    ruleEngine = new RuleEngine(config);

    // Reset mocks
    jest.clearAllMocks();
  });

  afterEach(async () => {
    await fs.remove(tempDir);
  });

  describe('constructor', () => {
    it('should create instance with valid config', () => {
      expect(ruleEngine).toBeInstanceOf(RuleEngine);
    });

    it('should initialize with default templates', () => {
      const templates = ruleEngine.getRuleTemplates();
      expect(templates.length).toBeGreaterThan(0);
      expect(templates.some(t => t.category === 'coverage')).toBe(true);
      expect(templates.some(t => t.category === 'tests')).toBe(true);
    });
  });

  describe('loadRules', () => {
    const mockRules: ThresholdRule[] = [
      {
        id: 'rule-1',
        name: 'Test Rule 1',
        metric: 'coverage.lines.percentage',
        type: 'absolute',
        comparison: 'gte',
        value: 80,
        severity: 'error',
        progressive: false,
        enabled: true
      },
      {
        id: 'rule-2',
        name: 'Test Rule 2',
        metric: 'tests.failed',
        type: 'absolute',
        comparison: 'eq',
        value: 0,
        severity: 'warning',
        progressive: false,
        enabled: true
      }
    ];

    it('should load rules from file when it exists', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(true);
      MockedFileUtils.readJsonFile.mockResolvedValue(mockRules);

      const rules = await ruleEngine.loadRules();

      expect(rules).toEqual(mockRules);
      expect(MockedFileUtils.readJsonFile).toHaveBeenCalledWith(config.rulesPath);
    });

    it('should return empty array when file does not exist', async () => {
      MockedFileUtils.fileExists.mockResolvedValue(false);

      const rules = await ruleEngine.loadRules();

      expect(rules).toEqual([]);
      expect(MockedFileUtils.readJsonFile).not.toHaveBeenCalled();
    });

    it('should validate rules during loading', async () => {
      const invalidRules = [
        {
          id: 'invalid-rule',
          // Missing required fields
        }
      ];

      MockedFileUtils.fileExists.mockResolvedValue(true);
      MockedFileUtils.readJsonFile.mockResolvedValue(invalidRules);

      await expect(ruleEngine.loadRules()).rejects.toThrow();
    });
  });

  describe('saveRules', () => {
    const mockRules: ThresholdRule[] = [
      {
        id: 'rule-1',
        name: 'Test Rule',
        metric: 'coverage.lines.percentage',
        type: 'absolute',
        comparison: 'gte',
        value: 80,
        severity: 'error',
        progressive: false,
        enabled: true
      }
    ];

    it('should save rules to file', async () => {
      MockedFileUtils.writeJsonFile.mockResolvedValue();

      await ruleEngine.saveRules(mockRules);

      expect(MockedFileUtils.writeJsonFile).toHaveBeenCalledWith(
        config.rulesPath,
        mockRules
      );
    });

    it('should validate rules before saving', async () => {
      const invalidRules = [
        {
          id: 'invalid-rule',
          // Missing required fields
        }
      ] as ThresholdRule[];

      await expect(ruleEngine.saveRules(invalidRules)).rejects.toThrow();
      expect(MockedFileUtils.writeJsonFile).not.toHaveBeenCalled();
    });
  });

  describe('addRule', () => {
    const newRule: ThresholdRule = {
      id: 'new-rule',
      name: 'New Rule',
      metric: 'coverage.functions.percentage',
      type: 'absolute',
      comparison: 'gte',
      value: 75,
      severity: 'warning',
      progressive: false,
      enabled: true
    };

    it('should add new rule', async () => {
      await ruleEngine.addRule(newRule);

      const rules = ruleEngine.getRules();
      expect(rules).toContainEqual(newRule);
    });

    it('should auto-save when enabled', async () => {
      const autoSaveEngine = new RuleEngine({ ...config, autoSave: true });
      MockedFileUtils.writeJsonFile.mockResolvedValue();

      await autoSaveEngine.addRule(newRule);

      expect(MockedFileUtils.writeJsonFile).toHaveBeenCalled();
    });

    it('should reject duplicate rule IDs', async () => {
      await ruleEngine.addRule(newRule);

      await expect(ruleEngine.addRule(newRule)).rejects.toThrow('already exists');
    });

    it('should validate rule before adding', async () => {
      const invalidRule = { id: 'invalid' } as ThresholdRule;

      await expect(ruleEngine.addRule(invalidRule)).rejects.toThrow();
    });
  });

  describe('updateRule', () => {
    const existingRule: ThresholdRule = {
      id: 'existing-rule',
      name: 'Existing Rule',
      metric: 'coverage.lines.percentage',
      type: 'absolute',
      comparison: 'gte',
      value: 80,
      severity: 'error',
      progressive: false,
      enabled: true
    };

    beforeEach(async () => {
      await ruleEngine.addRule(existingRule);
    });

    it('should update existing rule', async () => {
      const updates = {
        name: 'Updated Rule',
        value: 85,
        severity: 'warning' as const
      };

      const updatedRule = await ruleEngine.updateRule('existing-rule', updates);

      expect(updatedRule.name).toBe('Updated Rule');
      expect(updatedRule.value).toBe(85);
      expect(updatedRule.severity).toBe('warning');
      expect(updatedRule.id).toBe('existing-rule'); // Should not change
    });

    it('should reject updates to non-existent rules', async () => {
      await expect(
        ruleEngine.updateRule('non-existent', { name: 'New Name' })
      ).rejects.toThrow('not found');
    });

    it('should validate updated rule', async () => {
      await expect(
        ruleEngine.updateRule('existing-rule', { comparison: 'invalid' as any })
      ).rejects.toThrow();
    });
  });

  describe('removeRule', () => {
    const ruleToRemove: ThresholdRule = {
      id: 'rule-to-remove',
      name: 'Rule to Remove',
      metric: 'coverage.lines.percentage',
      type: 'absolute',
      comparison: 'gte',
      value: 80,
      severity: 'error',
      progressive: false,
      enabled: true
    };

    beforeEach(async () => {
      await ruleEngine.addRule(ruleToRemove);
    });

    it('should remove existing rule', async () => {
      await ruleEngine.removeRule('rule-to-remove');

      const rule = ruleEngine.getRule('rule-to-remove');
      expect(rule).toBeNull();
    });

    it('should reject removal of non-existent rules', async () => {
      await expect(ruleEngine.removeRule('non-existent')).rejects.toThrow('not found');
    });
  });

  describe('getRules', () => {
    const testRules: ThresholdRule[] = [
      {
        id: 'enabled-error',
        name: 'Enabled Error',
        metric: 'coverage.lines.percentage',
        type: 'absolute',
        comparison: 'gte',
        value: 80,
        severity: 'error',
        progressive: false,
        enabled: true
      },
      {
        id: 'disabled-warning',
        name: 'Disabled Warning',
        metric: 'tests.failed',
        type: 'absolute',
        comparison: 'eq',
        value: 0,
        severity: 'warning',
        progressive: true,
        enabled: false
      },
      {
        id: 'enabled-info',
        name: 'Enabled Info',
        metric: 'performance.memory',
        type: 'percentage',
        comparison: 'lte',
        value: 10,
        severity: 'info',
        progressive: false,
        enabled: true
      }
    ];

    beforeEach(async () => {
      for (const rule of testRules) {
        await ruleEngine.addRule(rule);
      }
    });

    it('should return all rules when no filter is provided', () => {
      const rules = ruleEngine.getRules();
      expect(rules).toHaveLength(3);
    });

    it('should filter by enabled status', () => {
      const enabledRules = ruleEngine.getRules({ enabled: true });
      const disabledRules = ruleEngine.getRules({ enabled: false });

      expect(enabledRules).toHaveLength(2);
      expect(disabledRules).toHaveLength(1);
    });

    it('should filter by severity', () => {
      const errorRules = ruleEngine.getRules({ severity: 'error' });
      const warningRules = ruleEngine.getRules({ severity: 'warning' });
      const infoRules = ruleEngine.getRules({ severity: 'info' });

      expect(errorRules).toHaveLength(1);
      expect(warningRules).toHaveLength(1);
      expect(infoRules).toHaveLength(1);
    });

    it('should filter by metric pattern', () => {
      const coverageRules = ruleEngine.getRules({ metric: 'coverage' });
      expect(coverageRules).toHaveLength(1);
    });

    it('should filter by progressive flag', () => {
      const progressiveRules = ruleEngine.getRules({ progressive: true });
      const nonProgressiveRules = ruleEngine.getRules({ progressive: false });

      expect(progressiveRules).toHaveLength(1);
      expect(nonProgressiveRules).toHaveLength(2);
    });

    it('should apply multiple filters', () => {
      const filteredRules = ruleEngine.getRules({
        enabled: true,
        severity: 'error'
      });

      expect(filteredRules).toHaveLength(1);
      expect(filteredRules[0].id).toBe('enabled-error');
    });
  });

  describe('evaluateRules', () => {
    const mockComparisons: ComparisonResult[] = [
      {
        metric: 'coverage.lines.percentage',
        current: 85,
        baseline: 80,
        delta: 5,
        deltaPercentage: 6.25,
        status: 'improved'
      },
      {
        metric: 'tests.failed',
        current: 2,
        baseline: 0,
        delta: 2,
        deltaPercentage: 100,
        status: 'degraded'
      }
    ];

    const testRules: ThresholdRule[] = [
      {
        id: 'coverage-rule',
        name: 'Coverage Rule',
        metric: 'coverage.lines.percentage',
        type: 'absolute',
        comparison: 'gte',
        value: 80,
        severity: 'error',
        progressive: false,
        enabled: true
      },
      {
        id: 'test-rule',
        name: 'Test Rule',
        metric: 'tests.failed',
        type: 'absolute',
        comparison: 'eq',
        value: 0,
        severity: 'error',
        progressive: false,
        enabled: true
      }
    ];

    beforeEach(async () => {
      for (const rule of testRules) {
        await ruleEngine.addRule(rule);
      }
    });

    it('should evaluate all enabled rules', () => {
      const evaluations = ruleEngine.evaluateRules(mockComparisons);

      expect(evaluations).toHaveLength(2);
      expect(evaluations[0].rule.id).toBe('coverage-rule');
      expect(evaluations[0].passed).toBe(true); // 85 >= 80
      expect(evaluations[1].rule.id).toBe('test-rule');
      expect(evaluations[1].passed).toBe(false); // 2 != 0
    });

    it('should evaluate specific rules when IDs provided', () => {
      const evaluations = ruleEngine.evaluateRules(mockComparisons, ['coverage-rule']);

      expect(evaluations).toHaveLength(1);
      expect(evaluations[0].rule.id).toBe('coverage-rule');
    });

    it('should skip rules without matching metrics', () => {
      const limitedComparisons = [mockComparisons[0]]; // Only coverage

      const evaluations = ruleEngine.evaluateRules(limitedComparisons);

      expect(evaluations).toHaveLength(1);
      expect(evaluations[0].rule.id).toBe('coverage-rule');
    });

    it('should handle wildcard metric patterns', async () => {
      const wildcardRule: ThresholdRule = {
        id: 'wildcard-rule',
        name: 'Wildcard Rule',
        metric: 'coverage.*',
        type: 'absolute',
        comparison: 'gte',
        value: 75,
        severity: 'warning',
        progressive: false,
        enabled: true
      };

      await ruleEngine.addRule(wildcardRule);

      const evaluations = ruleEngine.evaluateRules(mockComparisons);

      expect(evaluations.some(e => e.rule.id === 'wildcard-rule')).toBe(true);
    });
  });

  describe('createProgressiveTargets', () => {
    const mockSnapshot: MetricsSnapshot = {
      id: 'snapshot-1',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      tests: {
        results: [],
        summary: { total: 100, passed: 95, failed: 5, skipped: 0, duration: 1000 }
      },
      coverage: {
        lines: { total: 1000, covered: 700, percentage: 70 },
        functions: { total: 200, covered: 140, percentage: 70 },
        branches: { total: 300, covered: 210, percentage: 70 },
        statements: { total: 1000, covered: 700, percentage: 70 },
        files: []
      },
      performance: [],
      metadata: {},
      created: new Date(),
      updated: new Date()
    };

    const progressiveRule: ThresholdRule = {
      id: 'progressive-coverage',
      name: 'Progressive Coverage',
      metric: 'coverage.lines.percentage',
      type: 'absolute',
      comparison: 'gte',
      value: 90,
      severity: 'warning',
      progressive: true,
      enabled: true
    };

    beforeEach(async () => {
      await ruleEngine.addRule(progressiveRule);
    });

    it('should create progressive targets for enabled progressive rules', () => {
      const targets = ruleEngine.createProgressiveTargets(mockSnapshot);

      expect(targets).toHaveLength(1);
      expect(targets[0].ruleId).toBe('progressive-coverage');
      expect(targets[0].currentValue).toBe(70);
      expect(targets[0].targetValue).toBe(90);
      expect(targets[0].steps).toBe(5);
      expect(targets[0].stepSize).toBe(4); // (90 - 70) / 5
      expect(targets[0].nextTarget).toBe(74); // 70 + 4
    });

    it('should filter targets by rule IDs when provided', () => {
      const targets = ruleEngine.createProgressiveTargets(mockSnapshot, ['progressive-coverage']);

      expect(targets).toHaveLength(1);
      expect(targets[0].ruleId).toBe('progressive-coverage');
    });

    it('should return empty array when progressive is disabled', () => {
      const nonProgressiveEngine = new RuleEngine({
        ...config,
        enableProgressive: false
      });

      const targets = nonProgressiveEngine.createProgressiveTargets(mockSnapshot);

      expect(targets).toHaveLength(0);
    });

    it('should skip metrics that cannot be extracted', () => {
      const ruleWithInvalidMetric: ThresholdRule = {
        id: 'invalid-metric-rule',
        name: 'Invalid Metric',
        metric: 'non.existent.metric',
        type: 'absolute',
        comparison: 'gte',
        value: 50,
        severity: 'warning',
        progressive: true,
        enabled: true
      };

      await ruleEngine.addRule(ruleWithInvalidMetric);

      const targets = ruleEngine.createProgressiveTargets(mockSnapshot);

      expect(targets).toHaveLength(1); // Only the valid one
      expect(targets[0].ruleId).toBe('progressive-coverage');
    });
  });

  describe('createRulesFromTemplate', () => {
    it('should create rules from coverage template', async () => {
      const rules = await ruleEngine.createRulesFromTemplate('coverage_basic');

      expect(rules.length).toBeGreaterThan(0);
      expect(rules.every(rule => rule.enabled)).toBe(true);
      expect(rules.some(rule => rule.metric.includes('coverage'))).toBe(true);
    });

    it('should apply overrides to template rules', async () => {
      const rules = await ruleEngine.createRulesFromTemplate('coverage_basic', {
        severity: 'info',
        enabled: false
      });

      expect(rules.every(rule => rule.severity === 'info')).toBe(true);
      expect(rules.every(rule => rule.enabled === false)).toBe(true);
    });

    it('should reject invalid template IDs', async () => {
      await expect(
        ruleEngine.createRulesFromTemplate('non-existent-template')
      ).rejects.toThrow('not found');
    });
  });

  describe('suggestRules', () => {
    const lowCoverageSnapshot: MetricsSnapshot = {
      id: 'low-coverage',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      tests: {
        results: [],
        summary: { total: 100, passed: 90, failed: 10, skipped: 0, duration: 45000 }
      },
      coverage: {
        lines: { total: 1000, covered: 600, percentage: 60 },
        functions: { total: 200, covered: 120, percentage: 60 },
        branches: { total: 300, covered: 180, percentage: 60 },
        statements: { total: 1000, covered: 600, percentage: 60 },
        files: []
      },
      performance: [],
      metadata: {},
      created: new Date(),
      updated: new Date()
    };

    it('should suggest coverage rules for low coverage', () => {
      const suggestions = ruleEngine.suggestRules(lowCoverageSnapshot);

      expect(suggestions.length).toBeGreaterThan(0);
      expect(suggestions.some(rule =>
        rule.metric.includes('coverage') && rule.progressive
      )).toBe(true);
    });

    it('should suggest test failure rules when tests are failing', () => {
      const suggestions = ruleEngine.suggestRules(lowCoverageSnapshot);

      expect(suggestions.some(rule =>
        rule.metric.includes('failed') && rule.value === 0
      )).toBe(true);
    });

    it('should suggest performance rules for slow tests', () => {
      const suggestions = ruleEngine.suggestRules(lowCoverageSnapshot);

      expect(suggestions.some(rule =>
        rule.metric.includes('duration') && rule.type === 'percentage'
      )).toBe(true);
    });
  });

  describe('validateRules', () => {
    it('should validate correct rules', () => {
      const validRules: ThresholdRule[] = [
        {
          id: 'valid-rule-1',
          name: 'Valid Rule 1',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 80,
          severity: 'error',
          progressive: false,
          enabled: true
        },
        {
          id: 'valid-rule-2',
          name: 'Valid Rule 2',
          metric: 'tests.failed',
          type: 'absolute',
          comparison: 'eq',
          value: 0,
          severity: 'warning',
          progressive: false,
          enabled: true
        }
      ];

      const result = ruleEngine.validateRules(validRules);

      expect(result.valid).toBe(true);
      expect(result.errors).toHaveLength(0);
    });

    it('should detect invalid rules', () => {
      const invalidRules = [
        {
          id: 'invalid-rule',
          name: 'Invalid Rule',
          metric: 'coverage.lines.percentage',
          type: 'invalid-type', // Invalid
          comparison: 'gte',
          value: 80,
          severity: 'error',
          progressive: false,
          enabled: true
        }
      ] as ThresholdRule[];

      const result = ruleEngine.validateRules(invalidRules);

      expect(result.valid).toBe(false);
      expect(result.errors.length).toBeGreaterThan(0);
    });

    it('should detect duplicate rule IDs', () => {
      const duplicateRules: ThresholdRule[] = [
        {
          id: 'duplicate-id',
          name: 'Rule 1',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 80,
          severity: 'error',
          progressive: false,
          enabled: true
        },
        {
          id: 'duplicate-id', // Duplicate
          name: 'Rule 2',
          metric: 'tests.failed',
          type: 'absolute',
          comparison: 'eq',
          value: 0,
          severity: 'warning',
          progressive: false,
          enabled: true
        }
      ];

      const result = ruleEngine.validateRules(duplicateRules);

      expect(result.valid).toBe(false);
      expect(result.errors.some(error => error.includes('Duplicate'))).toBe(true);
    });
  });

  describe('error handling', () => {
    it('should handle file system errors during load', async () => {
      MockedFileUtils.fileExists.mockRejectedValue(new Error('File system error'));

      await expect(ruleEngine.loadRules()).rejects.toThrow();
    });

    it('should handle file system errors during save', async () => {
      MockedFileUtils.writeJsonFile.mockRejectedValue(new Error('Write error'));

      const rule: ThresholdRule = {
        id: 'test-rule',
        name: 'Test Rule',
        metric: 'coverage.lines.percentage',
        type: 'absolute',
        comparison: 'gte',
        value: 80,
        severity: 'error',
        progressive: false,
        enabled: true
      };

      await expect(ruleEngine.saveRules([rule])).rejects.toThrow();
    });
  });
});