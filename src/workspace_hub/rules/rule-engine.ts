/**
 * Rule Engine - Configurable threshold rules with progressive improvement targets
 */

import { ValidationUtils } from '../utils/validation';
import { FileUtils } from '../utils/file-utils';
import {
  ThresholdRule,
  ComparisonResult,
  RuleEvaluationResult,
  MetricsSnapshot,
  BaselineEngineError,
  ValidationError
} from '../types';

export interface RuleEngineConfig {
  rulesPath: string;
  autoSave: boolean;
  enableProgressive: boolean;
  progressiveSteps: number;
  defaultSeverity: 'error' | 'warning' | 'info';
}

export interface RuleTemplate {
  id: string;
  name: string;
  description: string;
  category: 'coverage' | 'tests' | 'performance' | 'quality';
  rules: Omit<ThresholdRule, 'id'>[];
}

export interface ProgressiveTarget {
  ruleId: string;
  currentValue: number;
  targetValue: number;
  steps: number;
  stepSize: number;
  nextTarget: number;
}

export class RuleEngine {
  private config: RuleEngineConfig;
  private rules: Map<string, ThresholdRule> = new Map();
  private ruleTemplates: Map<string, RuleTemplate> = new Map();

  constructor(config: RuleEngineConfig) {
    this.config = config;
    this.initializeDefaultTemplates();
  }

  /**
   * Loads rules from configuration file
   */
  async loadRules(): Promise<ThresholdRule[]> {
    try {
      if (await FileUtils.fileExists(this.config.rulesPath)) {
        const rulesData = await FileUtils.readJsonFile<ThresholdRule[]>(this.config.rulesPath);

        this.rules.clear();
        for (const rule of rulesData) {
          ValidationUtils.validateThresholdRule(rule);
          this.rules.set(rule.id, rule);
        }
      }

      return Array.from(this.rules.values());
    } catch (error) {
      throw new BaselineEngineError(
        'Failed to load rules',
        'RULES_LOAD_ERROR',
        error
      );
    }
  }

  /**
   * Saves rules to configuration file
   */
  async saveRules(rules?: ThresholdRule[]): Promise<void> {
    try {
      const rulesToSave = rules || Array.from(this.rules.values());

      // Validate all rules before saving
      for (const rule of rulesToSave) {
        ValidationUtils.validateThresholdRule(rule);
      }

      await FileUtils.writeJsonFile(this.config.rulesPath, rulesToSave);

      // Update internal cache if no specific rules provided
      if (!rules) {
        this.rules.clear();
        for (const rule of rulesToSave) {
          this.rules.set(rule.id, rule);
        }
      }
    } catch (error) {
      throw new BaselineEngineError(
        'Failed to save rules',
        'RULES_SAVE_ERROR',
        error
      );
    }
  }

  /**
   * Adds a new rule
   */
  async addRule(rule: ThresholdRule): Promise<void> {
    ValidationUtils.validateThresholdRule(rule);

    if (this.rules.has(rule.id)) {
      throw new ValidationError(`Rule with ID ${rule.id} already exists`);
    }

    this.rules.set(rule.id, rule);

    if (this.config.autoSave) {
      await this.saveRules();
    }
  }

  /**
   * Updates an existing rule
   */
  async updateRule(ruleId: string, updates: Partial<ThresholdRule>): Promise<ThresholdRule> {
    ValidationUtils.validateNonEmptyString(ruleId, 'ruleId');

    const existingRule = this.rules.get(ruleId);
    if (!existingRule) {
      throw new ValidationError(`Rule with ID ${ruleId} not found`);
    }

    const updatedRule: ThresholdRule = {
      ...existingRule,
      ...updates,
      id: existingRule.id // Ensure ID cannot be changed
    };

    ValidationUtils.validateThresholdRule(updatedRule);
    this.rules.set(ruleId, updatedRule);

    if (this.config.autoSave) {
      await this.saveRules();
    }

    return updatedRule;
  }

  /**
   * Removes a rule
   */
  async removeRule(ruleId: string): Promise<void> {
    ValidationUtils.validateNonEmptyString(ruleId, 'ruleId');

    if (!this.rules.has(ruleId)) {
      throw new ValidationError(`Rule with ID ${ruleId} not found`);
    }

    this.rules.delete(ruleId);

    if (this.config.autoSave) {
      await this.saveRules();
    }
  }

  /**
   * Gets a rule by ID
   */
  getRule(ruleId: string): ThresholdRule | null {
    return this.rules.get(ruleId) || null;
  }

  /**
   * Gets all rules, optionally filtered
   */
  getRules(filter?: {
    enabled?: boolean;
    severity?: 'error' | 'warning' | 'info';
    metric?: string;
    progressive?: boolean;
  }): ThresholdRule[] {
    let rules = Array.from(this.rules.values());

    if (filter) {
      if (filter.enabled !== undefined) {
        rules = rules.filter(rule => rule.enabled === filter.enabled);
      }
      if (filter.severity) {
        rules = rules.filter(rule => rule.severity === filter.severity);
      }
      if (filter.metric) {
        rules = rules.filter(rule => rule.metric.includes(filter.metric!));
      }
      if (filter.progressive !== undefined) {
        rules = rules.filter(rule => (rule.progressive || false) === filter.progressive);
      }
    }

    return rules;
  }

  /**
   * Evaluates rules against comparison results
   */
  evaluateRules(
    comparisons: ComparisonResult[],
    ruleIds?: string[]
  ): RuleEvaluationResult[] {
    const rulesToEvaluate = ruleIds
      ? ruleIds.map(id => this.rules.get(id)).filter(Boolean) as ThresholdRule[]
      : this.getRules({ enabled: true });

    const evaluations: RuleEvaluationResult[] = [];

    for (const rule of rulesToEvaluate) {
      const matchingComparisons = comparisons.filter(comp =>
        this.doesMetricMatchRule(comp.metric, rule.metric)
      );

      for (const comparison of matchingComparisons) {
        const evaluation = this.evaluateRule(rule, comparison);
        evaluations.push(evaluation);
      }
    }

    return evaluations;
  }

  /**
   * Creates progressive improvement targets
   */
  createProgressiveTargets(
    currentSnapshot: MetricsSnapshot,
    targetRules: string[] = []
  ): ProgressiveTarget[] {
    if (!this.config.enableProgressive) {
      return [];
    }

    const progressiveRules = this.getRules({
      progressive: true,
      enabled: true
    }).filter(rule => targetRules.length === 0 || targetRules.includes(rule.id));

    const targets: ProgressiveTarget[] = [];

    for (const rule of progressiveRules) {
      const currentValue = this.extractMetricValue(currentSnapshot, rule.metric);

      if (currentValue === null) continue;

      const target = this.calculateProgressiveTarget(rule, currentValue);
      if (target) {
        targets.push(target);
      }
    }

    return targets;
  }

  /**
   * Updates progressive rules based on current performance
   */
  async updateProgressiveRules(targets: ProgressiveTarget[]): Promise<void> {
    for (const target of targets) {
      const rule = this.rules.get(target.ruleId);
      if (!rule || !rule.progressive) continue;

      // Update rule value to next progressive target
      if (rule) {
        await this.updateRule(target.ruleId, {
          value: target.nextTarget,
          metadata: {
            ...rule.metadata,
            progressiveStep: (rule.metadata?.progressiveStep as number || 0) + 1,
            lastUpdated: new Date().toISOString()
          }
        });
      }
    }
  }

  /**
   * Creates rules from predefined templates
   */
  async createRulesFromTemplate(templateId: string, overrides?: Partial<ThresholdRule>): Promise<ThresholdRule[]> {
    const template = this.ruleTemplates.get(templateId);
    if (!template) {
      throw new ValidationError(`Template with ID ${templateId} not found`);
    }

    const createdRules: ThresholdRule[] = [];

    for (const ruleTemplate of template.rules) {
      const rule: ThresholdRule = {
        id: `${template.id}_${ruleTemplate.name.toLowerCase().replace(/\s+/g, '_')}_${Date.now()}`,
        ...ruleTemplate,
        ...overrides,
        enabled: overrides?.enabled ?? true
      };

      await this.addRule(rule);
      createdRules.push(rule);
    }

    return createdRules;
  }

  /**
   * Gets available rule templates
   */
  getRuleTemplates(category?: string): RuleTemplate[] {
    const templates = Array.from(this.ruleTemplates.values());

    if (category) {
      return templates.filter(template => template.category === category);
    }

    return templates;
  }

  /**
   * Validates rule configuration
   */
  validateRules(rules: ThresholdRule[]): { valid: boolean; errors: string[] } {
    const errors: string[] = [];

    for (const rule of rules) {
      try {
        ValidationUtils.validateThresholdRule(rule);
      } catch (error) {
        errors.push(`Rule ${rule.id}: ${error instanceof Error ? error.message : String(error)}`);
      }
    }

    // Check for duplicate IDs
    const ids = new Set<string>();
    for (const rule of rules) {
      if (ids.has(rule.id)) {
        errors.push(`Duplicate rule ID: ${rule.id}`);
      }
      ids.add(rule.id);
    }

    return {
      valid: errors.length === 0,
      errors
    };
  }

  /**
   * Suggests rules based on metrics data
   */
  suggestRules(snapshot: MetricsSnapshot): ThresholdRule[] {
    const suggestions: ThresholdRule[] = [];

    // Suggest coverage rules if coverage is low
    if (snapshot.coverage.lines.percentage < 80) {
      suggestions.push({
        id: `coverage_lines_${Date.now()}`,
        name: 'Minimum Line Coverage',
        metric: 'coverage.lines.percentage',
        type: 'absolute',
        comparison: 'gte',
        value: Math.max(snapshot.coverage.lines.percentage + 5, 70),
        severity: 'warning',
        progressive: true,
        enabled: true
      });
    }

    // Suggest test failure rules
    if (snapshot.tests.summary.failed > 0) {
      suggestions.push({
        id: `test_failures_${Date.now()}`,
        name: 'No Test Failures',
        metric: 'tests.failed',
        type: 'absolute',
        comparison: 'eq',
        value: 0,
        severity: 'error',
        progressive: false,
        enabled: true
      });
    }

    // Suggest performance rules for slow tests
    if (snapshot.tests.summary.duration > 30000) { // 30 seconds
      suggestions.push({
        id: `test_duration_${Date.now()}`,
        name: 'Test Suite Performance',
        metric: 'tests.duration',
        type: 'percentage',
        comparison: 'lte',
        value: 10, // Max 10% increase
        severity: 'warning',
        progressive: true,
        enabled: true
      });
    }

    return suggestions;
  }

  /**
   * Private helper methods
   */
  private evaluateRule(rule: ThresholdRule, comparison: ComparisonResult): RuleEvaluationResult {
    const valueToCompare = rule.type === 'percentage'
      ? comparison.deltaPercentage
      : rule.type === 'absolute' && rule.metric.includes('percentage')
        ? comparison.current
        : comparison.delta;

    let passed: boolean;
    let message: string;

    const threshold = rule.value;
    const metricDisplay = rule.type === 'percentage' ? 'change' : 'value';

    switch (rule.comparison) {
      case 'gte':
        passed = valueToCompare >= threshold;
        message = `${comparison.metric} ${metricDisplay} (${valueToCompare.toFixed(2)}) should be >= ${threshold}`;
        break;
      case 'lte':
        passed = valueToCompare <= threshold;
        message = `${comparison.metric} ${metricDisplay} (${valueToCompare.toFixed(2)}) should be <= ${threshold}`;
        break;
      case 'gt':
        passed = valueToCompare > threshold;
        message = `${comparison.metric} ${metricDisplay} (${valueToCompare.toFixed(2)}) should be > ${threshold}`;
        break;
      case 'lt':
        passed = valueToCompare < threshold;
        message = `${comparison.metric} ${metricDisplay} (${valueToCompare.toFixed(2)}) should be < ${threshold}`;
        break;
      case 'eq':
        passed = Math.abs(valueToCompare - threshold) < 0.001;
        message = `${comparison.metric} ${metricDisplay} (${valueToCompare.toFixed(2)}) should equal ${threshold}`;
        break;
      case 'ne':
        passed = Math.abs(valueToCompare - threshold) >= 0.001;
        message = `${comparison.metric} ${metricDisplay} (${valueToCompare.toFixed(2)}) should not equal ${threshold}`;
        break;
      default:
        passed = false;
        message = `Unknown comparison operator: ${rule.comparison}`;
    }

    return {
      rule,
      comparison,
      passed,
      message: `${passed ? '✓' : '✗'} ${message} [${rule.severity.toUpperCase()}]`
    };
  }

  private doesMetricMatchRule(metricName: string, rulePattern: string): boolean {
    // Support wildcards and regex patterns
    if (rulePattern.includes('*') || rulePattern.includes('?')) {
      const pattern = rulePattern
        .replace(/\./g, '\\.')
        .replace(/\*/g, '.*')
        .replace(/\?/g, '.');

      const regex = new RegExp(`^${pattern}$`, 'i');
      return regex.test(metricName);
    }

    // Exact match or contains
    return metricName === rulePattern || metricName.includes(rulePattern);
  }

  private extractMetricValue(snapshot: MetricsSnapshot, metricPath: string): number | null {
    const pathParts = metricPath.split('.');
    let current: any = snapshot;

    for (const part of pathParts) {
      if (current === null || current === undefined) {
        return null;
      }
      current = current[part];
    }

    return typeof current === 'number' ? current : null;
  }

  private calculateProgressiveTarget(rule: ThresholdRule, currentValue: number): ProgressiveTarget | null {
    const targetValue = rule.value;
    const steps = this.config.progressiveSteps;

    if (steps <= 1) return null;

    const difference = targetValue - currentValue;
    const stepSize = difference / steps;

    // Only create progressive target if there's meaningful improvement needed
    if (Math.abs(stepSize) < 0.01) return null;

    const nextTarget = currentValue + stepSize;

    return {
      ruleId: rule.id,
      currentValue,
      targetValue,
      steps,
      stepSize,
      nextTarget
    };
  }

  private initializeDefaultTemplates(): void {
    // Coverage templates
    this.ruleTemplates.set('coverage_basic', {
      id: 'coverage_basic',
      name: 'Basic Coverage Rules',
      description: 'Essential code coverage thresholds',
      category: 'coverage',
      rules: [
        {
          name: 'Minimum Line Coverage',
          metric: 'coverage.lines.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 80,
          severity: 'warning',
          progressive: true,
          enabled: true
        },
        {
          name: 'Minimum Function Coverage',
          metric: 'coverage.functions.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 80,
          severity: 'warning',
          progressive: true,
          enabled: true
        },
        {
          name: 'Minimum Branch Coverage',
          metric: 'coverage.branches.percentage',
          type: 'absolute',
          comparison: 'gte',
          value: 70,
          severity: 'info',
          progressive: true,
          enabled: true
        }
      ]
    });

    // Test quality templates
    this.ruleTemplates.set('test_quality', {
      id: 'test_quality',
      name: 'Test Quality Rules',
      description: 'Rules for maintaining test quality and reliability',
      category: 'tests',
      rules: [
        {
          name: 'No Test Failures',
          metric: 'tests.failed',
          type: 'absolute',
          comparison: 'eq',
          value: 0,
          severity: 'error',
          progressive: false,
          enabled: true
        },
        {
          name: 'Test Pass Rate',
          metric: 'tests.passRate',
          type: 'absolute',
          comparison: 'gte',
          value: 100,
          severity: 'error',
          progressive: false,
          enabled: true
        },
        {
          name: 'Coverage Regression Prevention',
          metric: 'coverage.lines.percentage',
          type: 'percentage',
          comparison: 'gte',
          value: -2, // Max 2% decrease
          severity: 'warning',
          progressive: false,
          enabled: true
        }
      ]
    });

    // Performance templates
    this.ruleTemplates.set('performance_basic', {
      id: 'performance_basic',
      name: 'Basic Performance Rules',
      description: 'Essential performance monitoring rules',
      category: 'performance',
      rules: [
        {
          name: 'Test Suite Duration',
          metric: 'tests.duration',
          type: 'percentage',
          comparison: 'lte',
          value: 20, // Max 20% increase
          severity: 'warning',
          progressive: true,
          enabled: true
        },
        {
          name: 'Memory Usage',
          metric: 'performance.memory*',
          type: 'percentage',
          comparison: 'lte',
          value: 15, // Max 15% increase
          severity: 'warning',
          progressive: true,
          enabled: false
        }
      ]
    });
  }
}