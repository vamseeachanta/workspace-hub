/**
 * Comparison Engine - Compares current metrics vs baseline with delta calculations
 */

import { ValidationUtils } from '../utils/validation';
import {
  MetricsSnapshot,
  BaselineData,
  ComparisonResult,
  ComparisonReport,
  ThresholdRule,
  RuleEvaluationResult,
  BaselineEngineError,
  ValidationError,
  ComparisonOptions
} from '../types';

export class ComparisonEngine {
  /**
   * Compares current metrics snapshot against baseline
   */
  async compare(
    current: MetricsSnapshot,
    baseline: BaselineData,
    rules: ThresholdRule[] = [],
    options: ComparisonOptions = {}
  ): Promise<ComparisonReport> {
    ValidationUtils.validateMetricsSnapshot(current);
    ValidationUtils.validateBaselineData(baseline);

    try {
      const comparisons = this.generateComparisons(
        current,
        baseline.metrics,
        options
      );

      const ruleEvaluations = this.evaluateRules(comparisons, rules);

      const summary = this.calculateSummary(ruleEvaluations);

      const recommendations = this.generateRecommendations(
        comparisons,
        ruleEvaluations
      );

      const overallStatus = this.determineOverallStatus(ruleEvaluations);

      const report: ComparisonReport = {
        id: `comparison-${Date.now()}`,
        baselineId: baseline.id,
        currentSnapshot: current,
        baseline,
        summary,
        comparisons,
        ruleEvaluations,
        recommendations,
        overallStatus,
        created: new Date(),
        updated: new Date()
      };

      return report;
    } catch (error) {
      throw new BaselineEngineError(
        'Failed to generate comparison report',
        'COMPARISON_ERROR',
        error
      );
    }
  }

  /**
   * Compares two individual metric values
   */
  compareMetric(
    metricName: string,
    currentValue: number,
    baselineValue: number,
    precisionDigits: number = 2
  ): ComparisonResult {
    ValidationUtils.validateNonEmptyString(metricName, 'metricName');
    ValidationUtils.validatePositiveNumber(currentValue, 'currentValue');
    ValidationUtils.validatePositiveNumber(baselineValue, 'baselineValue');

    const delta = currentValue - baselineValue;
    const deltaPercentage = baselineValue !== 0
      ? (delta / baselineValue) * 100
      : currentValue > 0 ? 100 : 0;

    let status: 'improved' | 'degraded' | 'unchanged';

    if (Math.abs(deltaPercentage) < 0.01) { // Less than 0.01% change
      status = 'unchanged';
    } else {
      // For most metrics, higher is better, but for some like error rate, lower is better
      const higherIsBetter = this.isHigherBetterMetric(metricName);
      status = (delta > 0) === higherIsBetter ? 'improved' : 'degraded';
    }

    return {
      metric: metricName,
      current: this.roundToPrecision(currentValue, precisionDigits),
      baseline: this.roundToPrecision(baselineValue, precisionDigits),
      delta: this.roundToPrecision(delta, precisionDigits),
      deltaPercentage: this.roundToPrecision(deltaPercentage, precisionDigits),
      status
    };
  }

  /**
   * Generates trend analysis for multiple snapshots
   */
  analyzeTrend(
    snapshots: MetricsSnapshot[],
    metricPath: string
  ): {
    trend: 'improving' | 'declining' | 'stable' | 'volatile';
    slope: number;
    correlation: number;
    volatility: number;
    values: { timestamp: Date; value: number }[];
  } {
    if (snapshots.length < 2) {
      throw new ValidationError('At least 2 snapshots required for trend analysis');
    }

    const values = snapshots
      .map(snapshot => ({
        timestamp: snapshot.created,
        value: this.extractMetricValue(snapshot, metricPath)
      }))
      .sort((a, b) => a.timestamp.getTime() - b.timestamp.getTime());

    const slope = this.calculateSlope(values);
    const correlation = this.calculateCorrelation(values);
    const volatility = this.calculateVolatility(values);

    let trend: 'improving' | 'declining' | 'stable' | 'volatile';

    if (volatility > 0.2) {
      trend = 'volatile';
    } else if (Math.abs(slope) < 0.001) {
      trend = 'stable';
    } else {
      const higherIsBetter = this.isHigherBetterMetric(metricPath);
      trend = (slope > 0) === higherIsBetter ? 'improving' : 'declining';
    }

    return {
      trend,
      slope,
      correlation,
      volatility,
      values
    };
  }

  /**
   * Private helper methods
   */
  private generateComparisons(
    current: MetricsSnapshot,
    baseline: MetricsSnapshot,
    options: ComparisonOptions
  ): ComparisonResult[] {
    const comparisons: ComparisonResult[] = [];

    // Test metrics comparisons
    comparisons.push(
      this.compareMetric(
        'tests.total',
        current.tests.summary.total,
        baseline.tests.summary.total,
        options.precisionDigits
      ),
      this.compareMetric(
        'tests.passed',
        current.tests.summary.passed,
        baseline.tests.summary.passed,
        options.precisionDigits
      ),
      this.compareMetric(
        'tests.failed',
        current.tests.summary.failed,
        baseline.tests.summary.failed,
        options.precisionDigits
      ),
      this.compareMetric(
        'tests.passRate',
        current.tests.summary.total > 0
          ? (current.tests.summary.passed / current.tests.summary.total) * 100
          : 0,
        baseline.tests.summary.total > 0
          ? (baseline.tests.summary.passed / baseline.tests.summary.total) * 100
          : 0,
        options.precisionDigits
      ),
      this.compareMetric(
        'tests.duration',
        current.tests.summary.duration,
        baseline.tests.summary.duration,
        options.precisionDigits
      )
    );

    // Coverage metrics comparisons
    comparisons.push(
      this.compareMetric(
        'coverage.lines.percentage',
        current.coverage.lines.percentage,
        baseline.coverage.lines.percentage,
        options.precisionDigits
      ),
      this.compareMetric(
        'coverage.functions.percentage',
        current.coverage.functions.percentage,
        baseline.coverage.functions.percentage,
        options.precisionDigits
      ),
      this.compareMetric(
        'coverage.branches.percentage',
        current.coverage.branches.percentage,
        baseline.coverage.branches.percentage,
        options.precisionDigits
      ),
      this.compareMetric(
        'coverage.statements.percentage',
        current.coverage.statements.percentage,
        baseline.coverage.statements.percentage,
        options.precisionDigits
      )
    );

    // Performance metrics comparisons
    const performanceMetrics = new Map<string, { current: number; baseline: number }>();

    // Group performance metrics by name
    for (const metric of current.performance) {
      const key = `${metric.name}.${metric.unit}`;
      if (!performanceMetrics.has(key)) {
        performanceMetrics.set(key, { current: 0, baseline: 0 });
      }
      performanceMetrics.get(key)!.current = metric.value;
    }

    for (const metric of baseline.performance) {
      const key = `${metric.name}.${metric.unit}`;
      if (!performanceMetrics.has(key)) {
        performanceMetrics.set(key, { current: 0, baseline: 0 });
      }
      performanceMetrics.get(key)!.baseline = metric.value;
    }

    // Generate comparisons for performance metrics
    for (const [metricName, values] of performanceMetrics) {
      if (values.current > 0 || values.baseline > 0) {
        comparisons.push(
          this.compareMetric(
            `performance.${metricName}`,
            values.current,
            values.baseline,
            options.precisionDigits
          )
        );
      }
    }

    // Filter comparisons based on options
    let filteredComparisons = comparisons;

    if (options.excludeMetrics && options.excludeMetrics.length > 0) {
      filteredComparisons = filteredComparisons.filter(
        comp => !options.excludeMetrics!.some(excluded => comp.metric.includes(excluded))
      );
    }

    if (options.customMetrics && options.customMetrics.length > 0) {
      const customComps = filteredComparisons.filter(
        comp => options.customMetrics!.some(custom => comp.metric.includes(custom))
      );
      filteredComparisons = [...filteredComparisons, ...customComps];
    }

    if (!options.includeUnchanged) {
      filteredComparisons = filteredComparisons.filter(
        comp => comp.status !== 'unchanged'
      );
    }

    return filteredComparisons;
  }

  private evaluateRules(
    comparisons: ComparisonResult[],
    rules: ThresholdRule[]
  ): RuleEvaluationResult[] {
    const evaluations: RuleEvaluationResult[] = [];

    for (const rule of rules) {
      if (!rule.enabled) continue;

      const matchingComparison = comparisons.find(comp =>
        this.doesMetricMatchRule(comp.metric, rule.metric)
      );

      if (!matchingComparison) {
        continue; // Skip rule if no matching metric found
      }

      const evaluation = this.evaluateRule(rule, matchingComparison);
      evaluations.push(evaluation);
    }

    return evaluations;
  }

  private evaluateRule(
    rule: ThresholdRule,
    comparison: ComparisonResult
  ): RuleEvaluationResult {
    let passed: boolean;
    let message: string;

    const valueToCompare = rule.type === 'percentage'
      ? comparison.deltaPercentage
      : comparison.delta;

    const threshold = rule.value;

    switch (rule.comparison) {
      case 'gte':
        passed = valueToCompare >= threshold;
        message = `${comparison.metric} ${rule.type === 'percentage' ? 'change' : 'delta'} (${valueToCompare}) should be >= ${threshold}`;
        break;
      case 'lte':
        passed = valueToCompare <= threshold;
        message = `${comparison.metric} ${rule.type === 'percentage' ? 'change' : 'delta'} (${valueToCompare}) should be <= ${threshold}`;
        break;
      case 'gt':
        passed = valueToCompare > threshold;
        message = `${comparison.metric} ${rule.type === 'percentage' ? 'change' : 'delta'} (${valueToCompare}) should be > ${threshold}`;
        break;
      case 'lt':
        passed = valueToCompare < threshold;
        message = `${comparison.metric} ${rule.type === 'percentage' ? 'change' : 'delta'} (${valueToCompare}) should be < ${threshold}`;
        break;
      case 'eq':
        passed = Math.abs(valueToCompare - threshold) < 0.001;
        message = `${comparison.metric} ${rule.type === 'percentage' ? 'change' : 'delta'} (${valueToCompare}) should equal ${threshold}`;
        break;
      case 'ne':
        passed = Math.abs(valueToCompare - threshold) >= 0.001;
        message = `${comparison.metric} ${rule.type === 'percentage' ? 'change' : 'delta'} (${valueToCompare}) should not equal ${threshold}`;
        break;
      default:
        passed = false;
        message = `Unknown comparison operator: ${rule.comparison}`;
    }

    return {
      rule,
      comparison,
      passed,
      message: passed ? `✓ ${message}` : `✗ ${message}`
    };
  }

  private calculateSummary(evaluations: RuleEvaluationResult[]): {
    total: number;
    passed: number;
    failed: number;
    warnings: number;
  } {
    return {
      total: evaluations.length,
      passed: evaluations.filter(e => e.passed).length,
      failed: evaluations.filter(e => !e.passed && e.rule.severity === 'error').length,
      warnings: evaluations.filter(e => !e.passed && e.rule.severity === 'warning').length
    };
  }

  private generateRecommendations(
    comparisons: ComparisonResult[],
    evaluations: RuleEvaluationResult[]
  ): string[] {
    const recommendations: string[] = [];

    // Analyze failing evaluations
    const failedEvaluations = evaluations.filter(e => !e.passed);
    for (const evaluation of failedEvaluations) {
      if (evaluation.rule.severity === 'error') {
        recommendations.push(
          `Critical: ${evaluation.comparison.metric} has degraded significantly. ` +
          `Consider investigating the root cause.`
        );
      }
    }

    // Analyze significant degradations
    const significantDegradations = comparisons.filter(
      comp => comp.status === 'degraded' && Math.abs(comp.deltaPercentage) > 10
    );

    for (const degradation of significantDegradations) {
      recommendations.push(
        `${degradation.metric} has degraded by ${degradation.deltaPercentage.toFixed(2)}%. ` +
        `Review recent changes that might have impacted this metric.`
      );
    }

    // Suggest improvements
    const coverageComparison = comparisons.find(c => c.metric === 'coverage.lines.percentage');
    if (coverageComparison && coverageComparison.current < 80) {
      recommendations.push(
        `Line coverage is ${coverageComparison.current.toFixed(2)}%. ` +
        `Consider adding more tests to reach the 80% threshold.`
      );
    }

    const testFailures = comparisons.find(c => c.metric === 'tests.failed');
    if (testFailures && testFailures.current > 0) {
      recommendations.push(
        `${testFailures.current} tests are failing. ` +
        `Fix failing tests before deploying to maintain quality.`
      );
    }

    return recommendations.length > 0 ? recommendations : ['All metrics are within acceptable ranges.'];
  }

  private determineOverallStatus(evaluations: RuleEvaluationResult[]): 'pass' | 'fail' | 'warning' {
    const hasErrors = evaluations.some(e => !e.passed && e.rule.severity === 'error');
    const hasWarnings = evaluations.some(e => !e.passed && e.rule.severity === 'warning');

    if (hasErrors) return 'fail';
    if (hasWarnings) return 'warning';
    return 'pass';
  }

  private doesMetricMatchRule(metricName: string, rulePattern: string): boolean {
    // Support wildcards in rule patterns
    const pattern = rulePattern
      .replace(/\./g, '\\.')
      .replace(/\*/g, '.*')
      .replace(/\?/g, '.');

    const regex = new RegExp(`^${pattern}$`);
    return regex.test(metricName);
  }

  private isHigherBetterMetric(metricName: string): boolean {
    const lowerIsBetterPatterns = [
      'failed',
      'error',
      'duration',
      'time',
      'latency',
      'memory',
      'cpu'
    ];

    return !lowerIsBetterPatterns.some(pattern =>
      metricName.toLowerCase().includes(pattern)
    );
  }

  private extractMetricValue(snapshot: MetricsSnapshot, metricPath: string): number {
    const pathParts = metricPath.split('.');
    let current: any = snapshot;

    for (const part of pathParts) {
      if (current === null || current === undefined) {
        return 0;
      }
      current = current[part];
    }

    return typeof current === 'number' ? current : 0;
  }

  private roundToPrecision(value: number, digits: number = 2): number {
    const factor = Math.pow(10, digits);
    return Math.round(value * factor) / factor;
  }

  private calculateSlope(values: { timestamp: Date; value: number }[]): number {
    if (values.length < 2) return 0;

    const n = values.length;
    const xValues = values.map((v, i) => i);
    const yValues = values.map(v => v.value);

    const sumX = xValues.reduce((a, b) => a + b, 0);
    const sumY = yValues.reduce((a, b) => a + b, 0);
    const sumXY = xValues.reduce((sum, x, i) => sum + x * (yValues[i] || 0), 0);
    const sumX2 = xValues.reduce((sum, x) => sum + x * x, 0);

    const slope = (n * sumXY - sumX * sumY) / (n * sumX2 - sumX * sumX);
    return isFinite(slope) ? slope : 0;
  }

  private calculateCorrelation(values: { timestamp: Date; value: number }[]): number {
    if (values.length < 2) return 0;

    const n = values.length;
    const xValues = values.map((v, i) => i);
    const yValues = values.map(v => v.value);

    const meanX = xValues.reduce((a, b) => a + b, 0) / n;
    const meanY = yValues.reduce((a, b) => a + b, 0) / n;

    const numerator = xValues.reduce((sum, x, i) =>
      sum + (x - meanX) * ((yValues[i] || 0) - meanY), 0
    );

    const denomX = Math.sqrt(xValues.reduce((sum, x) =>
      sum + Math.pow(x - meanX, 2), 0
    ));

    const denomY = Math.sqrt(yValues.reduce((sum, y) =>
      sum + Math.pow(y - meanY, 2), 0
    ));

    const correlation = numerator / (denomX * denomY);
    return isFinite(correlation) ? correlation : 0;
  }

  private calculateVolatility(values: { timestamp: Date; value: number }[]): number {
    if (values.length < 2) return 0;

    const mean = values.reduce((sum, v) => sum + v.value, 0) / values.length;
    const variance = values.reduce((sum, v) =>
      sum + Math.pow(v.value - mean, 2), 0
    ) / values.length;

    const standardDeviation = Math.sqrt(variance);
    const volatility = mean !== 0 ? standardDeviation / Math.abs(mean) : 0;

    return isFinite(volatility) ? volatility : 0;
  }
}