/**
 * Baseline Tracking Engine - Main orchestrator class
 */

import { BaselineManager } from '../baseline/baseline-manager';
import { MetricsCollector } from '../metrics/metrics-collector';
import { ComparisonEngine } from '../comparison/comparison-engine';
import { RuleEngine } from '../rules/rule-engine';
import { ReportGenerator } from '../reports/report-generator';
import { ConfigManager } from '../config/config-manager';
import { ValidationUtils } from '../utils/validation';
import {
  MetricsSnapshot,
  BaselineData,
  ComparisonReport,
  ThresholdRule,
  BaselineEngineError,
  ComparisonOptions
} from '../types';

export interface EngineOptions {
  configPath?: string;
  autoSave?: boolean;
  enableValidation?: boolean;
}

export class BaselineTrackingEngine {
  private configManager: ConfigManager;
  private baselineManager: BaselineManager | null = null;
  private metricsCollector: MetricsCollector | null = null;
  private comparisonEngine: ComparisonEngine;
  private ruleEngine: RuleEngine | null = null;
  private reportGenerator: ReportGenerator | null = null;
  private initialized: boolean = false;

  constructor(options: EngineOptions = {}) {
    this.configManager = new ConfigManager(options.configPath);
    this.comparisonEngine = new ComparisonEngine();
  }

  /**
   * Initializes the engine with configuration
   */
  async initialize(): Promise<void> {
    if (this.initialized) {
      return;
    }

    try {
      const config = await this.configManager.loadConfig();

      // Initialize components
      this.baselineManager = new BaselineManager(config.engine.baseline);
      this.metricsCollector = new MetricsCollector(config.metricsCollector);
      this.ruleEngine = new RuleEngine(config.ruleEngine);
      this.reportGenerator = new ReportGenerator(config.reportGenerator);

      // Load rules
      await this.ruleEngine.loadRules();

      this.initialized = true;
    } catch (error) {
      throw new BaselineEngineError(
        'Failed to initialize baseline tracking engine',
        'INITIALIZATION_ERROR',
        error
      );
    }
  }

  /**
   * Collects metrics and creates a snapshot
   */
  async collectMetrics(
    id: string,
    branch: string,
    commit: string,
    environment: string,
    version: string,
    metadata: Record<string, unknown> = {}
  ): Promise<MetricsSnapshot> {
    await this.ensureInitialized();

    return this.metricsCollector!.collectMetrics(
      id,
      branch,
      commit,
      environment,
      version,
      metadata
    );
  }

  /**
   * Creates a new baseline from metrics snapshot
   */
  async createBaseline(
    name: string,
    snapshot: MetricsSnapshot,
    options: {
      isDefault?: boolean;
      tags?: string[];
      metadata?: Record<string, unknown>;
    } = {}
  ): Promise<BaselineData> {
    await this.ensureInitialized();

    return this.baselineManager!.createBaseline(name, snapshot, options);
  }

  /**
   * Loads an existing baseline
   */
  async loadBaseline(id: string): Promise<BaselineData> {
    await this.ensureInitialized();

    return this.baselineManager!.loadBaseline(id);
  }

  /**
   * Gets the default baseline for a branch and environment
   */
  async getDefaultBaseline(branch: string, environment: string): Promise<BaselineData | null> {
    await this.ensureInitialized();

    return this.baselineManager!.getDefaultBaseline(branch, environment);
  }

  /**
   * Compares current metrics against a baseline
   */
  async compareAgainstBaseline(
    current: MetricsSnapshot,
    baselineId: string,
    options: ComparisonOptions = {}
  ): Promise<ComparisonReport> {
    await this.ensureInitialized();

    const baseline = await this.baselineManager!.loadBaseline(baselineId);
    const rules = this.ruleEngine!.getRules({ enabled: true });

    return this.comparisonEngine.compare(current, baseline, rules, options);
  }

  /**
   * Compares current metrics against the default baseline
   */
  async compareAgainstDefault(
    current: MetricsSnapshot,
    options: ComparisonOptions = {}
  ): Promise<ComparisonReport> {
    await this.ensureInitialized();

    const baseline = await this.baselineManager!.getDefaultBaseline(
      current.branch,
      current.environment
    );

    if (!baseline) {
      throw new BaselineEngineError(
        `No default baseline found for branch ${current.branch} and environment ${current.environment}`,
        'NO_DEFAULT_BASELINE'
      );
    }

    const rules = this.ruleEngine!.getRules({ enabled: true });

    return this.comparisonEngine.compare(current, baseline, rules, options);
  }

  /**
   * Generates a comparison report in multiple formats
   */
  async generateReport(report: ComparisonReport): Promise<{ [format: string]: string }> {
    await this.ensureInitialized();

    return this.reportGenerator!.generateReport(report);
  }

  /**
   * Complete workflow: collect metrics, compare, and generate report
   */
  async runComparison(
    id: string,
    branch: string,
    commit: string,
    environment: string,
    version: string,
    baselineId?: string,
    metadata: Record<string, unknown> = {}
  ): Promise<{
    snapshot: MetricsSnapshot;
    report: ComparisonReport;
    generatedFiles: { [format: string]: string };
  }> {
    await this.ensureInitialized();

    try {
      // Step 1: Collect current metrics
      const snapshot = await this.collectMetrics(
        id,
        branch,
        commit,
        environment,
        version,
        metadata
      );

      // Step 2: Compare against baseline
      const report = baselineId
        ? await this.compareAgainstBaseline(snapshot, baselineId)
        : await this.compareAgainstDefault(snapshot);

      // Step 3: Generate reports
      const generatedFiles = await this.generateReport(report);

      return {
        snapshot,
        report,
        generatedFiles
      };
    } catch (error) {
      throw new BaselineEngineError(
        'Failed to run comparison workflow',
        'WORKFLOW_ERROR',
        error
      );
    }
  }

  /**
   * Rule management methods
   */
  async addRule(rule: ThresholdRule): Promise<void> {
    await this.ensureInitialized();
    await this.ruleEngine!.addRule(rule);
  }

  async updateRule(ruleId: string, updates: Partial<ThresholdRule>): Promise<ThresholdRule> {
    await this.ensureInitialized();
    return this.ruleEngine!.updateRule(ruleId, updates);
  }

  async removeRule(ruleId: string): Promise<void> {
    await this.ensureInitialized();
    await this.ruleEngine!.removeRule(ruleId);
  }

  async getRules(filter?: {
    enabled?: boolean;
    severity?: 'error' | 'warning' | 'info';
    metric?: string;
  }): Promise<ThresholdRule[]> {
    await this.ensureInitialized();
    return this.ruleEngine!.getRules(filter);
  }

  /**
   * Creates rules from templates
   */
  async createRulesFromTemplate(
    templateId: string,
    overrides?: Partial<ThresholdRule>
  ): Promise<ThresholdRule[]> {
    await this.ensureInitialized();
    return this.ruleEngine!.createRulesFromTemplate(templateId, overrides);
  }

  /**
   * Suggests rules based on metrics data
   */
  async suggestRules(snapshot: MetricsSnapshot): Promise<ThresholdRule[]> {
    await this.ensureInitialized();
    return this.ruleEngine!.suggestRules(snapshot);
  }

  /**
   * Baseline management methods
   */
  async listBaselines(filter?: {
    branch?: string;
    environment?: string;
    dateFrom?: Date;
    dateTo?: Date;
    tags?: string[];
  }): Promise<BaselineData[]> {
    await this.ensureInitialized();
    return this.baselineManager!.listBaselines(filter);
  }

  async setDefaultBaseline(id: string): Promise<void> {
    await this.ensureInitialized();
    await this.baselineManager!.setAsDefault(id);
  }

  async deleteBaseline(id: string): Promise<void> {
    await this.ensureInitialized();
    await this.baselineManager!.deleteBaseline(id);
  }

  /**
   * Configuration management
   */
  async getConfig(): Promise<any> {
    return this.configManager.getConfig();
  }

  async updateConfig(updates: any): Promise<any> {
    const updatedConfig = await this.configManager.updateConfig(updates);

    // Reinitialize components with new config if already initialized
    if (this.initialized) {
      this.initialized = false;
      await this.initialize();
    }

    return updatedConfig;
  }

  async createConfigBackup(): Promise<string> {
    return this.configManager.createBackup();
  }

  async restoreConfigFromBackup(backupPath: string): Promise<void> {
    await this.configManager.restoreFromBackup(backupPath);

    // Reinitialize with restored config
    if (this.initialized) {
      this.initialized = false;
      await this.initialize();
    }
  }

  /**
   * Trend analysis
   */
  async analyzeTrend(
    snapshots: MetricsSnapshot[],
    metricPath: string
  ): Promise<{
    trend: 'improving' | 'declining' | 'stable' | 'volatile';
    slope: number;
    correlation: number;
    volatility: number;
    values: { timestamp: Date; value: number }[];
  }> {
    return this.comparisonEngine.analyzeTrend(snapshots, metricPath);
  }

  /**
   * Validation utilities
   */
  async validateSnapshot(snapshot: unknown): Promise<boolean> {
    try {
      ValidationUtils.validateMetricsSnapshot(snapshot);
      return true;
    } catch {
      return false;
    }
  }

  async validateBaseline(baseline: unknown): Promise<boolean> {
    try {
      ValidationUtils.validateBaselineData(baseline);
      return true;
    } catch {
      return false;
    }
  }

  async validateRule(rule: unknown): Promise<boolean> {
    try {
      ValidationUtils.validateThresholdRule(rule);
      return true;
    } catch {
      return false;
    }
  }

  /**
   * Health check
   */
  async healthCheck(): Promise<{
    status: 'healthy' | 'unhealthy';
    components: {
      [component: string]: {
        status: 'healthy' | 'unhealthy';
        message?: string;
      };
    };
  }> {
    const components: any = {};

    try {
      // Check configuration
      await this.configManager.getConfig();
      components.config = { status: 'healthy' };
    } catch (error) {
      components.config = {
        status: 'unhealthy',
        message: `Configuration error: ${error instanceof Error ? error.message : String(error)}`
      };
    }

    if (this.initialized) {
      try {
        // Check baseline storage
        await this.baselineManager!.listBaselines();
        components.baseline = { status: 'healthy' };
      } catch (error) {
        components.baseline = {
          status: 'unhealthy',
          message: `Baseline storage error: ${error instanceof Error ? error.message : String(error)}`
        };
      }

      try {
        // Check rules
        await this.ruleEngine!.getRules();
        components.rules = { status: 'healthy' };
      } catch (error) {
        components.rules = {
          status: 'unhealthy',
          message: `Rule engine error: ${error instanceof Error ? error.message : String(error)}`
        };
      }
    } else {
      components.baseline = { status: 'unhealthy', message: 'Not initialized' };
      components.rules = { status: 'unhealthy', message: 'Not initialized' };
    }

    const unhealthyComponents = Object.values(components).filter(
      (comp: any) => comp.status === 'unhealthy'
    );

    return {
      status: unhealthyComponents.length === 0 ? 'healthy' : 'unhealthy',
      components
    };
  }

  /**
   * Cleanup and shutdown
   */
  async shutdown(): Promise<void> {
    // Perform any necessary cleanup
    this.initialized = false;
    this.baselineManager = null;
    this.metricsCollector = null;
    this.ruleEngine = null;
    this.reportGenerator = null;
  }

  /**
   * Private helper methods
   */
  private async ensureInitialized(): Promise<void> {
    if (!this.initialized) {
      await this.initialize();
    }
  }
}