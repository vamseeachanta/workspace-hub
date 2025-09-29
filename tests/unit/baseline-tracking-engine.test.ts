/**
 * Unit tests for BaselineTrackingEngine
 */

import { BaselineTrackingEngine } from '../../src/engine/baseline-tracking-engine';
import { BaselineManager } from '../../src/baseline/baseline-manager';
import { MetricsCollector } from '../../src/metrics/metrics-collector';
import { RuleEngine } from '../../src/rules/rule-engine';
import { ReportGenerator } from '../../src/reports/report-generator';
import { ConfigManager } from '../../src/config/config-manager';
import { MetricsSnapshot, BaselineData, ThresholdRule } from '../../src/types';

// Mock all dependencies
jest.mock('../../src/baseline/baseline-manager');
jest.mock('../../src/metrics/metrics-collector');
jest.mock('../../src/rules/rule-engine');
jest.mock('../../src/reports/report-generator');
jest.mock('../../src/config/config-manager');

const MockedBaselineManager = BaselineManager as jest.MockedClass<typeof BaselineManager>;
const MockedMetricsCollector = MetricsCollector as jest.MockedClass<typeof MetricsCollector>;
const MockedRuleEngine = RuleEngine as jest.MockedClass<typeof RuleEngine>;
const MockedReportGenerator = ReportGenerator as jest.MockedClass<typeof ReportGenerator>;
const MockedConfigManager = ConfigManager as jest.MockedClass<typeof ConfigManager>;

describe('BaselineTrackingEngine', () => {
  let engine: BaselineTrackingEngine;
  let mockConfigManager: jest.Mocked<ConfigManager>;
  let mockBaselineManager: jest.Mocked<BaselineManager>;
  let mockMetricsCollector: jest.Mocked<MetricsCollector>;
  let mockRuleEngine: jest.Mocked<RuleEngine>;
  let mockReportGenerator: jest.Mocked<ReportGenerator>;

  const mockConfig = {
    version: '1.0.0',
    engine: {
      baseline: {
        storagePath: './baselines',
        retentionPolicy: { maxVersions: 10, maxAge: 30 },
        mergeStrategy: 'latest',
        backupEnabled: true
      },
      rules: [],
      reporting: {
        formats: ['json', 'html'],
        outputPath: './reports',
        includeDetails: true,
        includeTrends: false
      },
      metrics: {
        parseFormats: ['jest'],
        customParsers: []
      }
    },
    metricsCollector: {
      parsers: {
        jest: { enabled: true, resultsPath: './test-results.json' }
      },
      performance: { enabled: false, sources: [] }
    },
    reportGenerator: {
      outputPath: './reports',
      formats: ['json', 'html'],
      includeDetails: true,
      includeTrends: false,
      includeCharts: false
    },
    ruleEngine: {
      rulesPath: './rules.json',
      autoSave: true,
      enableProgressive: false,
      progressiveSteps: 5,
      defaultSeverity: 'warning'
    }
  };

  beforeEach(() => {
    // Reset all mocks
    jest.clearAllMocks();

    // Setup mock instances
    mockConfigManager = new MockedConfigManager() as jest.Mocked<ConfigManager>;
    mockBaselineManager = new MockedBaselineManager({} as any) as jest.Mocked<BaselineManager>;
    mockMetricsCollector = new MockedMetricsCollector({} as any) as jest.Mocked<MetricsCollector>;
    mockRuleEngine = new MockedRuleEngine({} as any) as jest.Mocked<RuleEngine>;
    mockReportGenerator = new MockedReportGenerator({} as any) as jest.Mocked<ReportGenerator>;

    // Setup ConfigManager mock
    MockedConfigManager.mockImplementation(() => mockConfigManager);
    mockConfigManager.loadConfig.mockResolvedValue(mockConfig as any);

    // Setup other mocks
    MockedBaselineManager.mockImplementation(() => mockBaselineManager);
    MockedMetricsCollector.mockImplementation(() => mockMetricsCollector);
    MockedRuleEngine.mockImplementation(() => mockRuleEngine);
    MockedReportGenerator.mockImplementation(() => mockReportGenerator);

    mockRuleEngine.loadRules.mockResolvedValue([]);

    engine = new BaselineTrackingEngine();
  });

  describe('constructor', () => {
    it('should create instance with default options', () => {
      expect(engine).toBeInstanceOf(BaselineTrackingEngine);
      expect(MockedConfigManager).toHaveBeenCalledWith(undefined);
    });

    it('should create instance with custom config path', () => {
      const customEngine = new BaselineTrackingEngine({ configPath: './custom-config.yml' });
      expect(customEngine).toBeInstanceOf(BaselineTrackingEngine);
      expect(MockedConfigManager).toHaveBeenCalledWith('./custom-config.yml');
    });
  });

  describe('initialize', () => {
    it('should initialize all components', async () => {
      await engine.initialize();

      expect(mockConfigManager.loadConfig).toHaveBeenCalled();
      expect(MockedBaselineManager).toHaveBeenCalledWith(mockConfig.engine.baseline);
      expect(MockedMetricsCollector).toHaveBeenCalledWith(mockConfig.metricsCollector);
      expect(MockedRuleEngine).toHaveBeenCalledWith(mockConfig.ruleEngine);
      expect(MockedReportGenerator).toHaveBeenCalledWith(mockConfig.reportGenerator);
      expect(mockRuleEngine.loadRules).toHaveBeenCalled();
    });

    it('should not reinitialize if already initialized', async () => {
      await engine.initialize();
      await engine.initialize(); // Second call

      expect(mockConfigManager.loadConfig).toHaveBeenCalledTimes(1);
    });

    it('should handle initialization errors', async () => {
      mockConfigManager.loadConfig.mockRejectedValue(new Error('Config error'));

      await expect(engine.initialize()).rejects.toThrow('Failed to initialize');
    });
  });

  describe('collectMetrics', () => {
    const mockSnapshot: MetricsSnapshot = {
      id: 'test-snapshot',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      tests: {
        results: [],
        summary: { total: 100, passed: 95, failed: 5, skipped: 0, duration: 1000 }
      },
      coverage: {
        lines: { total: 1000, covered: 800, percentage: 80 },
        functions: { total: 200, covered: 160, percentage: 80 },
        branches: { total: 300, covered: 240, percentage: 80 },
        statements: { total: 1000, covered: 800, percentage: 80 },
        files: []
      },
      performance: [],
      metadata: {},
      created: new Date(),
      updated: new Date()
    };

    beforeEach(async () => {
      await engine.initialize();
      mockMetricsCollector.collectMetrics.mockResolvedValue(mockSnapshot);
    });

    it('should collect metrics using collector', async () => {
      const result = await engine.collectMetrics(
        'test-id',
        'main',
        'abc123',
        'production',
        '1.0.0',
        { custom: 'metadata' }
      );

      expect(mockMetricsCollector.collectMetrics).toHaveBeenCalledWith(
        'test-id',
        'main',
        'abc123',
        'production',
        '1.0.0',
        { custom: 'metadata' }
      );
      expect(result).toBe(mockSnapshot);
    });

    it('should auto-initialize if not initialized', async () => {
      const uninitializedEngine = new BaselineTrackingEngine();
      mockMetricsCollector.collectMetrics.mockResolvedValue(mockSnapshot);

      await uninitializedEngine.collectMetrics('test-id', 'main', 'abc123', 'production', '1.0.0');

      expect(mockConfigManager.loadConfig).toHaveBeenCalled();
    });
  });

  describe('createBaseline', () => {
    const mockSnapshot: MetricsSnapshot = {} as MetricsSnapshot;
    const mockBaseline: BaselineData = {
      id: 'baseline-1',
      name: 'test-baseline',
      branch: 'main',
      commit: 'abc123',
      environment: 'production',
      version: '1.0.0',
      metrics: mockSnapshot,
      isDefault: false,
      tags: [],
      metadata: {},
      created: new Date(),
      updated: new Date()
    };

    beforeEach(async () => {
      await engine.initialize();
      mockBaselineManager.createBaseline.mockResolvedValue(mockBaseline);
    });

    it('should create baseline using manager', async () => {
      const result = await engine.createBaseline('test-baseline', mockSnapshot);

      expect(mockBaselineManager.createBaseline).toHaveBeenCalledWith(
        'test-baseline',
        mockSnapshot,
        {}
      );
      expect(result).toBe(mockBaseline);
    });

    it('should create baseline with options', async () => {
      const options = {
        isDefault: true,
        tags: ['stable'],
        metadata: { version: '1.0.0' }
      };

      await engine.createBaseline('test-baseline', mockSnapshot, options);

      expect(mockBaselineManager.createBaseline).toHaveBeenCalledWith(
        'test-baseline',
        mockSnapshot,
        options
      );
    });
  });

  describe('compareAgainstBaseline', () => {
    const mockSnapshot: MetricsSnapshot = {} as MetricsSnapshot;
    const mockBaseline: BaselineData = {
      id: 'baseline-1',
      name: 'test-baseline',
      metrics: {} as MetricsSnapshot
    } as BaselineData;
    const mockReport = {
      id: 'report-1',
      baselineId: 'baseline-1',
      currentSnapshot: mockSnapshot,
      baseline: mockBaseline,
      summary: { total: 0, passed: 0, failed: 0, warnings: 0 },
      comparisons: [],
      ruleEvaluations: [],
      recommendations: [],
      overallStatus: 'pass' as const,
      created: new Date(),
      updated: new Date()
    };

    beforeEach(async () => {
      await engine.initialize();
      mockBaselineManager.loadBaseline.mockResolvedValue(mockBaseline);
      mockRuleEngine.getRules.mockReturnValue([]);

      // Mock the comparison engine
      const mockComparisonEngine = {
        compare: jest.fn().mockResolvedValue(mockReport)
      };
      (engine as any).comparisonEngine = mockComparisonEngine;
    });

    it('should compare against specified baseline', async () => {
      const result = await engine.compareAgainstBaseline(mockSnapshot, 'baseline-1');

      expect(mockBaselineManager.loadBaseline).toHaveBeenCalledWith('baseline-1');
      expect(mockRuleEngine.getRules).toHaveBeenCalledWith({ enabled: true });
      expect(result).toBe(mockReport);
    });

    it('should pass comparison options', async () => {
      const options = { includeUnchanged: false, precisionDigits: 3 };

      await engine.compareAgainstBaseline(mockSnapshot, 'baseline-1', options);

      const mockCompare = (engine as any).comparisonEngine.compare;
      expect(mockCompare).toHaveBeenCalledWith(
        mockSnapshot,
        mockBaseline,
        [],
        options
      );
    });
  });

  describe('compareAgainstDefault', () => {
    const mockSnapshot: MetricsSnapshot = {
      branch: 'main',
      environment: 'production'
    } as MetricsSnapshot;
    const mockBaseline: BaselineData = {
      id: 'default-baseline',
      name: 'default',
      metrics: {} as MetricsSnapshot
    } as BaselineData;

    beforeEach(async () => {
      await engine.initialize();
      mockRuleEngine.getRules.mockReturnValue([]);

      const mockReport = {
        id: 'report-1',
        baselineId: 'default-baseline',
        currentSnapshot: mockSnapshot,
        baseline: mockBaseline,
        summary: { total: 0, passed: 0, failed: 0, warnings: 0 },
        comparisons: [],
        ruleEvaluations: [],
        recommendations: [],
        overallStatus: 'pass' as const,
        created: new Date(),
        updated: new Date()
      };

      const mockComparisonEngine = {
        compare: jest.fn().mockResolvedValue(mockReport)
      };
      (engine as any).comparisonEngine = mockComparisonEngine;
    });

    it('should compare against default baseline', async () => {
      mockBaselineManager.getDefaultBaseline.mockResolvedValue(mockBaseline);

      await engine.compareAgainstDefault(mockSnapshot);

      expect(mockBaselineManager.getDefaultBaseline).toHaveBeenCalledWith('main', 'production');
    });

    it('should throw error when no default baseline exists', async () => {
      mockBaselineManager.getDefaultBaseline.mockResolvedValue(null);

      await expect(engine.compareAgainstDefault(mockSnapshot)).rejects.toThrow(
        'No default baseline found'
      );
    });
  });

  describe('runComparison', () => {
    const mockSnapshot: MetricsSnapshot = {
      id: 'snapshot-1',
      branch: 'main',
      environment: 'production'
    } as MetricsSnapshot;
    const mockReport = {
      id: 'report-1',
      summary: { total: 0, passed: 0, failed: 0, warnings: 0 },
      comparisons: [],
      ruleEvaluations: [],
      recommendations: [],
      overallStatus: 'pass' as const
    } as any;
    const mockGeneratedFiles = {
      json: './reports/report.json',
      html: './reports/report.html'
    };

    beforeEach(async () => {
      await engine.initialize();
      mockMetricsCollector.collectMetrics.mockResolvedValue(mockSnapshot);
      mockReportGenerator.generateReport.mockResolvedValue(mockGeneratedFiles);

      // Mock comparison method
      (engine as any).compareAgainstDefault = jest.fn().mockResolvedValue(mockReport);
    });

    it('should run complete comparison workflow', async () => {
      const result = await engine.runComparison(
        'test-id',
        'main',
        'abc123',
        'production',
        '1.0.0'
      );

      expect(mockMetricsCollector.collectMetrics).toHaveBeenCalledWith(
        'test-id',
        'main',
        'abc123',
        'production',
        '1.0.0',
        {}
      );
      expect((engine as any).compareAgainstDefault).toHaveBeenCalledWith(mockSnapshot);
      expect(mockReportGenerator.generateReport).toHaveBeenCalledWith(mockReport);

      expect(result.snapshot).toBe(mockSnapshot);
      expect(result.report).toBe(mockReport);
      expect(result.generatedFiles).toBe(mockGeneratedFiles);
    });

    it('should use specific baseline when provided', async () => {
      (engine as any).compareAgainstBaseline = jest.fn().mockResolvedValue(mockReport);

      await engine.runComparison(
        'test-id',
        'main',
        'abc123',
        'production',
        '1.0.0',
        'baseline-1'
      );

      expect((engine as any).compareAgainstBaseline).toHaveBeenCalledWith(
        mockSnapshot,
        'baseline-1'
      );
    });

    it('should handle workflow errors', async () => {
      mockMetricsCollector.collectMetrics.mockRejectedValue(new Error('Collection failed'));

      await expect(
        engine.runComparison('test-id', 'main', 'abc123', 'production', '1.0.0')
      ).rejects.toThrow('Failed to run comparison workflow');
    });
  });

  describe('rule management', () => {
    const mockRule: ThresholdRule = {
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

    beforeEach(async () => {
      await engine.initialize();
    });

    it('should add rules', async () => {
      await engine.addRule(mockRule);

      expect(mockRuleEngine.addRule).toHaveBeenCalledWith(mockRule);
    });

    it('should update rules', async () => {
      const updates = { value: 85 };
      mockRuleEngine.updateRule.mockResolvedValue({ ...mockRule, ...updates });

      const result = await engine.updateRule('test-rule', updates);

      expect(mockRuleEngine.updateRule).toHaveBeenCalledWith('test-rule', updates);
      expect(result.value).toBe(85);
    });

    it('should remove rules', async () => {
      await engine.removeRule('test-rule');

      expect(mockRuleEngine.removeRule).toHaveBeenCalledWith('test-rule');
    });

    it('should get rules with filters', async () => {
      const filter = { enabled: true, severity: 'error' as const };
      mockRuleEngine.getRules.mockReturnValue([mockRule]);

      const result = await engine.getRules(filter);

      expect(mockRuleEngine.getRules).toHaveBeenCalledWith(filter);
      expect(result).toEqual([mockRule]);
    });
  });

  describe('validation utilities', () => {
    beforeEach(async () => {
      await engine.initialize();
    });

    it('should validate snapshots', async () => {
      const validSnapshot = {
        id: 'test',
        branch: 'main',
        commit: 'abc123',
        environment: 'production',
        version: '1.0.0',
        tests: { results: [], summary: { total: 0, passed: 0, failed: 0, skipped: 0, duration: 0 } },
        coverage: {
          lines: { total: 0, covered: 0, percentage: 0 },
          functions: { total: 0, covered: 0, percentage: 0 },
          branches: { total: 0, covered: 0, percentage: 0 },
          statements: { total: 0, covered: 0, percentage: 0 },
          files: []
        },
        performance: [],
        metadata: {},
        created: new Date(),
        updated: new Date()
      };

      const isValid = await engine.validateSnapshot(validSnapshot);
      expect(isValid).toBe(true);

      const isInvalid = await engine.validateSnapshot({ invalid: true });
      expect(isInvalid).toBe(false);
    });

    it('should validate baselines', async () => {
      const validBaseline = {
        id: 'test',
        name: 'test',
        branch: 'main',
        commit: 'abc123',
        environment: 'production',
        version: '1.0.0',
        metrics: {} as MetricsSnapshot,
        isDefault: false,
        tags: [],
        metadata: {},
        created: new Date(),
        updated: new Date()
      };

      const isValid = await engine.validateBaseline(validBaseline);
      expect(isValid).toBe(true);

      const isInvalid = await engine.validateBaseline({ invalid: true });
      expect(isInvalid).toBe(false);
    });

    it('should validate rules', async () => {
      const validRule = {
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

      const isValid = await engine.validateRule(validRule);
      expect(isValid).toBe(true);

      const isInvalid = await engine.validateRule({ invalid: true });
      expect(isInvalid).toBe(false);
    });
  });

  describe('healthCheck', () => {
    it('should report healthy status when all components are working', async () => {
      await engine.initialize();
      mockConfigManager.getConfig.mockResolvedValue(mockConfig as any);
      mockBaselineManager.listBaselines.mockResolvedValue([]);
      mockRuleEngine.getRules.mockReturnValue([]);

      const health = await engine.healthCheck();

      expect(health.status).toBe('healthy');
      expect(health.components.config.status).toBe('healthy');
      expect(health.components.baseline.status).toBe('healthy');
      expect(health.components.rules.status).toBe('healthy');
    });

    it('should report unhealthy status when configuration fails', async () => {
      mockConfigManager.getConfig.mockRejectedValue(new Error('Config error'));

      const health = await engine.healthCheck();

      expect(health.status).toBe('unhealthy');
      expect(health.components.config.status).toBe('unhealthy');
      expect(health.components.config.message).toContain('Configuration error');
    });

    it('should report unhealthy status when not initialized', async () => {
      const health = await engine.healthCheck();

      expect(health.status).toBe('unhealthy');
      expect(health.components.baseline.status).toBe('unhealthy');
      expect(health.components.baseline.message).toBe('Not initialized');
    });
  });

  describe('shutdown', () => {
    it('should cleanup resources', async () => {
      await engine.initialize();
      await engine.shutdown();

      // Verify internal state is reset
      expect((engine as any).initialized).toBe(false);
      expect((engine as any).baselineManager).toBeNull();
      expect((engine as any).metricsCollector).toBeNull();
      expect((engine as any).ruleEngine).toBeNull();
      expect((engine as any).reportGenerator).toBeNull();
    });
  });
});