# Comparison Engine Architecture

## Engine Overview

The Comparison Engine is the core analytical component that evaluates current test metrics against established baselines, detects regressions, identifies improvements, and enforces quality gates through configurable thresholds.

## Core Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Comparison Engine                         │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐│
│  │  Baseline   │  │  Threshold  │  │ Statistical │  │ Decision ││
│  │  Retrieval  │  │  Manager    │  │  Analysis   │  │  Engine  ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘│
│         │               │               │               │       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                 Comparison Processor                       ││
│  └─────────────────────────────────────────────────────────────┘│
│                            │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                   Result Generator                         ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

## 1. Baseline Retrieval System

### Smart Baseline Selection
```javascript
// baseline-retrieval.js
class BaselineRetrieval {
  constructor(storageLayer, config) {
    this.storage = storageLayer;
    this.config = config;
    this.selectionStrategies = {
      temporal: new TemporalStrategy(),
      branch: new BranchStrategy(),
      environment: new EnvironmentStrategy(),
      milestone: new MilestoneStrategy()
    };
  }

  async getApplicableBaseline(currentContext) {
    const strategy = this.determineStrategy(currentContext);
    const candidates = await this.findBaselineCandidates(currentContext);

    return await strategy.selectBaseline(candidates, currentContext);
  }

  async findBaselineCandidates(context) {
    const candidates = [];

    // Primary: Same branch, same environment
    const primary = await this.storage.findBaseline({
      branch: context.branch,
      environment: context.environment,
      project: context.project,
      limit: 5,
      orderBy: 'created_at DESC'
    });
    candidates.push(...primary.map(b => ({ ...b, priority: 'primary' })));

    // Secondary: Same branch, production environment
    if (context.environment !== 'production') {
      const secondary = await this.storage.findBaseline({
        branch: context.branch,
        environment: 'production',
        project: context.project,
        limit: 3,
        orderBy: 'created_at DESC'
      });
      candidates.push(...secondary.map(b => ({ ...b, priority: 'secondary' })));
    }

    // Tertiary: Main branch, same environment
    if (context.branch !== 'main') {
      const tertiary = await this.storage.findBaseline({
        branch: 'main',
        environment: context.environment,
        project: context.project,
        limit: 3,
        orderBy: 'created_at DESC'
      });
      candidates.push(...tertiary.map(b => ({ ...b, priority: 'tertiary' })));
    }

    // Milestone: Tagged releases
    const milestones = await this.storage.findBaseline({
      project: context.project,
      tags: ['release', 'milestone'],
      limit: 2,
      orderBy: 'created_at DESC'
    });
    candidates.push(...milestones.map(b => ({ ...b, priority: 'milestone' })));

    return candidates;
  }

  determineStrategy(context) {
    // Strategy selection logic based on context
    if (context.comparisonType === 'milestone') {
      return this.selectionStrategies.milestone;
    }

    if (context.branch !== 'main') {
      return this.selectionStrategies.branch;
    }

    if (context.environment !== 'production') {
      return this.selectionStrategies.environment;
    }

    return this.selectionStrategies.temporal;
  }
}

// Selection strategies
class TemporalStrategy {
  async selectBaseline(candidates, context) {
    // Select most recent baseline from same context
    const contextMatches = candidates.filter(c =>
      c.branch === context.branch &&
      c.environment === context.environment &&
      c.priority === 'primary'
    );

    if (contextMatches.length > 0) {
      return contextMatches[0];
    }

    // Fallback to best available
    return this.selectBestFallback(candidates);
  }

  selectBestFallback(candidates) {
    const priorityOrder = ['primary', 'secondary', 'tertiary', 'milestone'];

    for (const priority of priorityOrder) {
      const matches = candidates.filter(c => c.priority === priority);
      if (matches.length > 0) {
        return matches[0];
      }
    }

    return null;
  }
}

class BranchStrategy {
  async selectBaseline(candidates, context) {
    // For feature branches, prefer main branch baseline
    const mainBranchBaselines = candidates.filter(c =>
      c.branch === 'main' && c.environment === context.environment
    );

    if (mainBranchBaselines.length > 0) {
      return mainBranchBaselines[0];
    }

    // Fallback to branch-specific baseline
    const branchBaselines = candidates.filter(c =>
      c.branch === context.branch
    );

    return branchBaselines.length > 0 ? branchBaselines[0] : null;
  }
}
```

## 2. Threshold Management System

### Threshold Configuration
```javascript
// threshold-manager.js
class ThresholdManager {
  constructor(config) {
    this.config = config;
    this.thresholds = new Map();
    this.loadDefaultThresholds();
  }

  loadDefaultThresholds() {
    const defaults = {
      execution: {
        pass_rate_min_percentage: { value: 95.0, blocking: true, severity: 'critical' },
        execution_time_max_ms: { value: 60000, blocking: true, severity: 'major' },
        individual_test_max_ms: { value: 10000, blocking: false, severity: 'minor' }
      },
      coverage: {
        line_coverage_min: { value: 80.0, blocking: true, severity: 'major' },
        branch_coverage_min: { value: 75.0, blocking: true, severity: 'major' },
        function_coverage_min: { value: 90.0, blocking: false, severity: 'minor' },
        statement_coverage_min: { value: 80.0, blocking: true, severity: 'major' }
      },
      performance: {
        memory_usage_max_mb: { value: 1024, blocking: false, severity: 'minor' },
        api_response_time_p95_max_ms: { value: 300, blocking: false, severity: 'minor' },
        database_query_time_p95_max_ms: { value: 50, blocking: false, severity: 'minor' }
      },
      quality: {
        flaky_test_rate_max: { value: 0.02, blocking: false, severity: 'minor' },
        stability_score_min: { value: 0.95, blocking: false, severity: 'minor' },
        regression_tolerance_percentage: { value: 5.0, blocking: true, severity: 'major' }
      }
    };

    this.thresholds.set('default', defaults);
  }

  getThresholds(context) {
    // Context-specific threshold resolution
    const contextKey = `${context.project}:${context.branch}:${context.environment}`;

    // Try specific context first
    if (this.thresholds.has(contextKey)) {
      return this.mergeWithDefaults(this.thresholds.get(contextKey));
    }

    // Try project-level
    const projectKey = `${context.project}:*:*`;
    if (this.thresholds.has(projectKey)) {
      return this.mergeWithDefaults(this.thresholds.get(projectKey));
    }

    // Return defaults
    return this.thresholds.get('default');
  }

  async updateThresholds(context, newThresholds) {
    const contextKey = `${context.project}:${context.branch}:${context.environment}`;
    const existing = this.thresholds.get(contextKey) || {};

    const merged = this.deepMerge(existing, newThresholds);
    this.thresholds.set(contextKey, merged);

    // Persist to storage
    await this.persistThresholds(contextKey, merged);

    return merged;
  }

  validateThreshold(metricPath, currentValue, threshold, baseline) {
    const result = {
      metric: metricPath,
      current: currentValue,
      threshold: threshold.value,
      baseline: baseline,
      passed: false,
      severity: threshold.severity,
      blocking: threshold.blocking,
      message: ''
    };

    // Determine comparison type based on metric name
    if (metricPath.includes('_min')) {
      result.passed = currentValue >= threshold.value;
      result.message = result.passed
        ? `${metricPath} meets minimum threshold`
        : `${metricPath} below minimum: ${currentValue} < ${threshold.value}`;
    } else if (metricPath.includes('_max')) {
      result.passed = currentValue <= threshold.value;
      result.message = result.passed
        ? `${metricPath} within maximum threshold`
        : `${metricPath} exceeds maximum: ${currentValue} > ${threshold.value}`;
    } else {
      // For regression detection
      const regressionThreshold = threshold.value / 100; // Convert percentage
      const change = baseline ? (currentValue - baseline) / baseline : 0;

      result.passed = Math.abs(change) <= regressionThreshold;
      result.message = result.passed
        ? `${metricPath} within regression tolerance`
        : `${metricPath} regression detected: ${(change * 100).toFixed(2)}% change`;
    }

    return result;
  }
}
```

## 3. Statistical Analysis Engine

### Comparison Algorithms
```javascript
// statistical-analysis.js
class StatisticalAnalysis {
  constructor(config) {
    this.config = config;
    this.analysisTypes = {
      absolute: new AbsoluteComparison(),
      percentage: new PercentageComparison(),
      statistical: new StatisticalComparison(),
      trend: new TrendAnalysis()
    };
  }

  async analyzeMetrics(current, baseline, historical = []) {
    const results = {
      absolute_comparison: {},
      percentage_comparison: {},
      statistical_significance: {},
      trend_analysis: {},
      anomaly_detection: {},
      overall_assessment: {}
    };

    // Absolute comparison
    results.absolute_comparison = this.analysisTypes.absolute.compare(current, baseline);

    // Percentage comparison
    results.percentage_comparison = this.analysisTypes.percentage.compare(current, baseline);

    // Statistical significance testing
    if (historical.length >= 5) {
      results.statistical_significance = await this.analysisTypes.statistical.analyze(
        current, baseline, historical
      );
    }

    // Trend analysis
    if (historical.length >= 10) {
      results.trend_analysis = await this.analysisTypes.trend.analyze(
        current, [...historical, baseline]
      );
    }

    // Anomaly detection
    results.anomaly_detection = await this.detectAnomalies(current, historical);

    // Overall assessment
    results.overall_assessment = this.generateOverallAssessment(results);

    return results;
  }

  async detectAnomalies(current, historical) {
    if (historical.length < 10) {
      return { insufficient_data: true };
    }

    const anomalies = {};
    const metrics = this.extractMetricPaths(current);

    for (const metricPath of metrics) {
      const currentValue = this.getMetricValue(current, metricPath);
      const historicalValues = historical.map(h => this.getMetricValue(h, metricPath)).filter(v => v !== null);

      if (historicalValues.length >= 10) {
        const anomalyResult = this.detectMetricAnomaly(currentValue, historicalValues);
        if (anomalyResult.isAnomaly) {
          anomalies[metricPath] = anomalyResult;
        }
      }
    }

    return anomalies;
  }

  detectMetricAnomaly(currentValue, historicalValues) {
    // Statistical outlier detection using modified Z-score
    const median = this.calculateMedian(historicalValues);
    const mad = this.calculateMAD(historicalValues, median); // Median Absolute Deviation

    const modifiedZScore = 0.6745 * (currentValue - median) / mad;
    const threshold = 3.5; // Standard threshold for outlier detection

    const isAnomaly = Math.abs(modifiedZScore) > threshold;

    return {
      isAnomaly,
      severity: this.categorizeAnomalySeverity(Math.abs(modifiedZScore)),
      zScore: modifiedZScore,
      median,
      mad,
      percentile: this.calculatePercentile(currentValue, historicalValues)
    };
  }

  categorizeAnomalySeverity(zScore) {
    if (zScore > 5) return 'critical';
    if (zScore > 4) return 'major';
    if (zScore > 3.5) return 'minor';
    return 'normal';
  }
}

class AbsoluteComparison {
  compare(current, baseline) {
    const comparison = {};
    const metricPaths = this.extractAllMetricPaths(current, baseline);

    for (const path of metricPaths) {
      const currentVal = this.getValueByPath(current, path);
      const baselineVal = this.getValueByPath(baseline, path);

      if (currentVal !== null && baselineVal !== null) {
        comparison[path] = {
          current: currentVal,
          baseline: baselineVal,
          absolute_difference: currentVal - baselineVal,
          direction: this.determineDirection(currentVal, baselineVal, path)
        };
      }
    }

    return comparison;
  }

  determineDirection(current, baseline, metricPath) {
    const diff = current - baseline;

    // For metrics where higher is better
    if (this.isHigherBetterMetric(metricPath)) {
      if (diff > 0) return 'improvement';
      if (diff < 0) return 'regression';
      return 'unchanged';
    }

    // For metrics where lower is better
    if (diff < 0) return 'improvement';
    if (diff > 0) return 'regression';
    return 'unchanged';
  }

  isHigherBetterMetric(metricPath) {
    const higherBetterPatterns = [
      'pass_rate',
      'coverage',
      'stability_score'
    ];

    return higherBetterPatterns.some(pattern => metricPath.includes(pattern));
  }
}

class PercentageComparison {
  compare(current, baseline) {
    const comparison = {};
    const metricPaths = this.extractAllMetricPaths(current, baseline);

    for (const path of metricPaths) {
      const currentVal = this.getValueByPath(current, path);
      const baselineVal = this.getValueByPath(baseline, path);

      if (currentVal !== null && baselineVal !== null && baselineVal !== 0) {
        const percentageChange = ((currentVal - baselineVal) / baselineVal) * 100;

        comparison[path] = {
          current: currentVal,
          baseline: baselineVal,
          percentage_change: percentageChange,
          significance: this.categorizeSignificance(Math.abs(percentageChange))
        };
      }
    }

    return comparison;
  }

  categorizeSignificance(absPercentageChange) {
    if (absPercentageChange >= 20) return 'major';
    if (absPercentageChange >= 10) return 'moderate';
    if (absPercentageChange >= 5) return 'minor';
    return 'negligible';
  }
}

class StatisticalComparison {
  async analyze(current, baseline, historical) {
    const analysis = {};
    const metricPaths = this.extractAllMetricPaths(current, baseline);

    for (const path of metricPaths) {
      const currentVal = this.getValueByPath(current, path);
      const baselineVal = this.getValueByPath(baseline, path);
      const historicalVals = historical.map(h => this.getValueByPath(h, path)).filter(v => v !== null);

      if (currentVal !== null && historicalVals.length >= 5) {
        analysis[path] = await this.performStatisticalTest(currentVal, historicalVals);
      }
    }

    return analysis;
  }

  async performStatisticalTest(currentValue, historicalValues) {
    // T-test for statistical significance
    const mean = historicalValues.reduce((sum, val) => sum + val, 0) / historicalValues.length;
    const variance = historicalValues.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / (historicalValues.length - 1);
    const standardError = Math.sqrt(variance / historicalValues.length);

    const tStatistic = (currentValue - mean) / standardError;
    const degreesOfFreedom = historicalValues.length - 1;

    // Critical value for 95% confidence (two-tailed test)
    const criticalValue = this.getCriticalValue(degreesOfFreedom, 0.05);

    const isStatisticallySignificant = Math.abs(tStatistic) > criticalValue;
    const pValue = this.calculatePValue(tStatistic, degreesOfFreedom);

    return {
      current_value: currentValue,
      historical_mean: mean,
      historical_variance: variance,
      t_statistic: tStatistic,
      degrees_of_freedom: degreesOfFreedom,
      p_value: pValue,
      is_statistically_significant: isStatisticallySignificant,
      confidence_level: 0.95,
      effect_size: this.calculateEffectSize(currentValue, mean, Math.sqrt(variance))
    };
  }

  calculateEffectSize(current, mean, standardDeviation) {
    // Cohen's d
    return (current - mean) / standardDeviation;
  }

  getCriticalValue(df, alpha) {
    // Simplified critical value lookup for t-distribution
    const criticalValues = {
      5: 2.571, 10: 2.228, 15: 2.131, 20: 2.086,
      25: 2.060, 30: 2.042, 40: 2.021, 60: 2.000, 100: 1.984
    };

    for (const [threshold, value] of Object.entries(criticalValues)) {
      if (df <= parseInt(threshold)) {
        return value;
      }
    }

    return 1.96; // Normal approximation for large df
  }
}
```

## 4. Decision Engine

### Gate Decision Logic
```javascript
// decision-engine.js
class DecisionEngine {
  constructor(thresholdManager, config) {
    this.thresholdManager = thresholdManager;
    this.config = config;
    this.decisionRules = new Map();
    this.loadDecisionRules();
  }

  loadDecisionRules() {
    // Rule definitions for different scenarios
    this.decisionRules.set('quality_gate', {
      blocking_failures: 'fail',
      non_blocking_failures_threshold: 3,
      regression_tolerance: 'moderate',
      improvement_bonus: true
    });

    this.decisionRules.set('release_gate', {
      blocking_failures: 'fail',
      non_blocking_failures_threshold: 0,
      regression_tolerance: 'strict',
      improvement_bonus: false
    });

    this.decisionRules.set('development', {
      blocking_failures: 'warn',
      non_blocking_failures_threshold: 5,
      regression_tolerance: 'relaxed',
      improvement_bonus: true
    });
  }

  async makeDecision(comparisonResults, context) {
    const gateType = this.determineGateType(context);
    const rules = this.decisionRules.get(gateType);

    const decision = {
      gate_type: gateType,
      overall_result: 'pending',
      blocking_issues: [],
      non_blocking_issues: [],
      improvements: [],
      warnings: [],
      recommendations: [],
      metrics_summary: this.generateMetricsSummary(comparisonResults),
      execution_timestamp: new Date().toISOString()
    };

    // Evaluate threshold violations
    await this.evaluateThresholds(decision, comparisonResults, context, rules);

    // Evaluate statistical significance
    await this.evaluateStatisticalSignificance(decision, comparisonResults);

    // Evaluate anomalies
    await this.evaluateAnomalies(decision, comparisonResults);

    // Make final decision
    decision.overall_result = this.determineOverallResult(decision, rules);

    // Generate recommendations
    decision.recommendations = this.generateRecommendations(decision, comparisonResults);

    return decision;
  }

  async evaluateThresholds(decision, comparisonResults, context, rules) {
    const thresholds = this.thresholdManager.getThresholds(context);
    const currentMetrics = comparisonResults.current_metrics;
    const baselineMetrics = comparisonResults.baseline_metrics;

    for (const [category, categoryThresholds] of Object.entries(thresholds)) {
      for (const [metricName, threshold] of Object.entries(categoryThresholds)) {
        const metricPath = `${category}.${metricName.replace('_min', '').replace('_max', '')}`;
        const currentValue = this.getMetricValue(currentMetrics, metricPath);
        const baselineValue = this.getMetricValue(baselineMetrics, metricPath);

        if (currentValue !== null) {
          const validation = this.thresholdManager.validateThreshold(
            metricPath, currentValue, threshold, baselineValue
          );

          if (!validation.passed) {
            if (validation.blocking) {
              decision.blocking_issues.push(validation);
            } else {
              decision.non_blocking_issues.push(validation);
            }
          }
        }
      }
    }
  }

  async evaluateStatisticalSignificance(decision, comparisonResults) {
    if (!comparisonResults.statistical_significance) return;

    for (const [metricPath, stats] of Object.entries(comparisonResults.statistical_significance)) {
      if (stats.is_statistically_significant) {
        const effectSize = Math.abs(stats.effect_size);

        if (effectSize >= 0.8) { // Large effect size
          if (stats.current_value > stats.historical_mean) {
            if (this.isHigherBetterMetric(metricPath)) {
              decision.improvements.push({
                metric: metricPath,
                type: 'statistical_improvement',
                effect_size: effectSize,
                confidence: 1 - stats.p_value
              });
            } else {
              decision.warnings.push({
                metric: metricPath,
                type: 'statistical_regression',
                effect_size: effectSize,
                confidence: 1 - stats.p_value
              });
            }
          }
        }
      }
    }
  }

  async evaluateAnomalies(decision, comparisonResults) {
    if (!comparisonResults.anomaly_detection) return;

    for (const [metricPath, anomaly] of Object.entries(comparisonResults.anomaly_detection)) {
      if (anomaly.isAnomaly) {
        decision.warnings.push({
          metric: metricPath,
          type: 'anomaly_detected',
          severity: anomaly.severity,
          z_score: anomaly.zScore,
          percentile: anomaly.percentile
        });
      }
    }
  }

  determineOverallResult(decision, rules) {
    // Check for blocking failures
    if (decision.blocking_issues.length > 0) {
      return rules.blocking_failures === 'fail' ? 'failed' : 'warning';
    }

    // Check non-blocking failure threshold
    if (decision.non_blocking_issues.length > rules.non_blocking_failures_threshold) {
      return 'warning';
    }

    // Check for critical anomalies
    const criticalAnomalies = decision.warnings.filter(w =>
      w.type === 'anomaly_detected' && w.severity === 'critical'
    );
    if (criticalAnomalies.length > 0) {
      return 'warning';
    }

    // Success with improvements bonus
    if (decision.improvements.length > 0 && rules.improvement_bonus) {
      return 'passed_with_improvements';
    }

    return 'passed';
  }

  generateRecommendations(decision, comparisonResults) {
    const recommendations = [];

    // Recommendations for blocking issues
    for (const issue of decision.blocking_issues) {
      recommendations.push({
        type: 'fix_required',
        priority: 'high',
        metric: issue.metric,
        suggestion: this.getFixSuggestion(issue)
      });
    }

    // Recommendations for trends
    if (comparisonResults.trend_analysis) {
      for (const [metricPath, trend] of Object.entries(comparisonResults.trend_analysis)) {
        if (trend.trend_direction === 'degrading') {
          recommendations.push({
            type: 'trend_monitoring',
            priority: 'medium',
            metric: metricPath,
            suggestion: `Monitor ${metricPath} trend - showing degradation over time`
          });
        }
      }
    }

    // Performance optimization recommendations
    if (decision.non_blocking_issues.some(issue => issue.metric.includes('performance'))) {
      recommendations.push({
        type: 'optimization',
        priority: 'low',
        suggestion: 'Consider performance optimization review'
      });
    }

    return recommendations;
  }

  determineGateType(context) {
    if (context.branch === 'main' && context.environment === 'production') {
      return 'release_gate';
    }

    if (context.tags && context.tags.includes('release')) {
      return 'release_gate';
    }

    if (context.environment === 'production') {
      return 'quality_gate';
    }

    return 'development';
  }
}
```

## 5. Result Formatting and Output

### Structured Result Format
```javascript
// result-formatter.js
class ResultFormatter {
  static formatComparisonResult(decisionResult, comparisonData) {
    return {
      summary: {
        overall_result: decisionResult.overall_result,
        gate_type: decisionResult.gate_type,
        execution_time: decisionResult.execution_timestamp,
        baseline_used: comparisonData.baseline_metadata,
        issues_count: {
          blocking: decisionResult.blocking_issues.length,
          non_blocking: decisionResult.non_blocking_issues.length,
          warnings: decisionResult.warnings.length
        }
      },
      detailed_analysis: {
        threshold_violations: {
          blocking: decisionResult.blocking_issues,
          non_blocking: decisionResult.non_blocking_issues
        },
        statistical_analysis: comparisonData.statistical_significance,
        anomaly_detection: comparisonData.anomaly_detection,
        trend_analysis: comparisonData.trend_analysis
      },
      metrics_comparison: {
        absolute: comparisonData.absolute_comparison,
        percentage: comparisonData.percentage_comparison
      },
      recommendations: decisionResult.recommendations,
      improvements: decisionResult.improvements,
      raw_data: {
        current_metrics: comparisonData.current_metrics,
        baseline_metrics: comparisonData.baseline_metrics
      }
    };
  }
}
```

This comparison engine provides comprehensive analysis capabilities with configurable thresholds, statistical validation, anomaly detection, and intelligent decision-making to ensure robust quality gates across different development contexts.