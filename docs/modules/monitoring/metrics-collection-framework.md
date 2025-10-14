# Metrics Collection Framework

## Framework Overview

The metrics collection framework provides a unified interface for gathering test execution data from multiple testing frameworks while maintaining framework-specific optimizations and features.

## Architecture Components

### 1. Collection Engine Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Metrics Collection Engine                   │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────┐│
│  │    Jest     │  │    Mocha    │  │   Pytest    │  │  Custom  ││
│  │   Adapter   │  │   Adapter   │  │   Adapter   │  │ Adapter  ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────┘│
│         │               │               │               │       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              Framework Detection Layer                     ││
│  └─────────────────────────────────────────────────────────────┘│
│         │               │               │               │       │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                Metric Normalization Layer                  ││
│  └─────────────────────────────────────────────────────────────┘│
│                            │                                   │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │                 Output Processing Layer                    ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
```

### 2. Framework Adapters

#### Jest Adapter
```javascript
// jest-adapter.js
class JestAdapter {
  constructor(config) {
    this.config = config;
    this.frameworkName = 'jest';
    this.version = this.detectVersion();
  }

  async collectMetrics(testResults) {
    const metrics = {
      framework: {
        name: 'jest',
        version: this.version,
        configHash: this.generateConfigHash()
      },
      execution: await this.extractExecutionMetrics(testResults),
      coverage: await this.extractCoverageMetrics(testResults),
      performance: await this.extractPerformanceMetrics(testResults),
      quality: await this.extractQualityMetrics(testResults)
    };

    return this.normalizeMetrics(metrics);
  }

  async extractExecutionMetrics(testResults) {
    return {
      totalTests: testResults.numTotalTests,
      passedTests: testResults.numPassedTests,
      failedTests: testResults.numFailedTests,
      skippedTests: testResults.numPendingTests,
      passRate: (testResults.numPassedTests / testResults.numTotalTests) * 100,
      executionTime: testResults.executionTime,
      testSuites: testResults.testResults.map(suite => ({
        name: suite.testFilePath,
        tests: suite.numTests,
        passed: suite.numPassingTests,
        failed: suite.numFailingTests,
        duration: suite.perfStats.end - suite.perfStats.start,
        assertionResults: suite.assertionResults.map(test => ({
          title: test.title,
          status: test.status,
          duration: test.duration,
          failureMessages: test.failureMessages
        }))
      }))
    };
  }

  async extractCoverageMetrics(testResults) {
    const coverage = testResults.coverageMap;
    if (!coverage) return null;

    const summary = coverage.getCoverageSummary();

    return {
      overall: {
        lineCoverage: summary.lines.pct,
        branchCoverage: summary.branches.pct,
        functionCoverage: summary.functions.pct,
        statementCoverage: summary.statements.pct
      },
      byFile: this.extractFileCoverage(coverage),
      uncoveredLines: this.extractUncoveredLines(coverage),
      thresholds: this.config.coverageThreshold || {}
    };
  }

  async extractPerformanceMetrics(testResults) {
    return {
      memoryUsage: {
        peakMemoryMB: process.memoryUsage().heapUsed / 1024 / 1024,
        averageMemoryMB: this.calculateAverageMemory(),
        memoryLeakDetected: this.detectMemoryLeaks()
      },
      timing: {
        slowestTests: this.findSlowestTests(testResults, 10),
        fastestTests: this.findFastestTests(testResults, 10),
        averageTestDuration: this.calculateAverageTestDuration(testResults)
      },
      systemMetrics: await this.collectSystemMetrics()
    };
  }

  async extractQualityMetrics(testResults) {
    const flakyTests = await this.detectFlakyTests(testResults);
    const newTests = await this.findNewTests(testResults);
    const deletedTests = await this.findDeletedTests(testResults);

    return {
      flakyTests,
      newTests,
      deletedTests,
      stabilityScore: this.calculateStabilityScore(testResults),
      complexity: await this.analyzeCodeComplexity()
    };
  }

  generateConfigHash() {
    const configStr = JSON.stringify(this.config, Object.keys(this.config).sort());
    return require('crypto').createHash('md5').update(configStr).digest('hex');
  }
}
```

#### Mocha Adapter
```javascript
// mocha-adapter.js
class MochaAdapter {
  constructor(config) {
    this.config = config;
    this.frameworkName = 'mocha';
    this.version = this.detectVersion();
    this.testResults = [];
    this.startTime = null;
  }

  setupHooks() {
    // Mocha hooks for real-time metric collection
    before(() => {
      this.startTime = Date.now();
      this.initializeMetricCollection();
    });

    beforeEach((test) => {
      this.recordTestStart(test);
    });

    afterEach((test) => {
      this.recordTestEnd(test);
    });

    after(() => {
      this.finalizeMetrics();
    });
  }

  async collectMetrics(runner) {
    return new Promise((resolve) => {
      const metrics = {
        framework: {
          name: 'mocha',
          version: this.version,
          configHash: this.generateConfigHash()
        },
        execution: {},
        coverage: {},
        performance: {},
        quality: {}
      };

      runner.on('start', () => {
        this.startTime = Date.now();
      });

      runner.on('test', (test) => {
        test.startTime = Date.now();
      });

      runner.on('test end', (test) => {
        test.endTime = Date.now();
        test.duration = test.endTime - test.startTime;
        this.testResults.push(test);
      });

      runner.on('end', async () => {
        metrics.execution = this.processExecutionMetrics();
        metrics.coverage = await this.processCoverageMetrics();
        metrics.performance = await this.processPerformanceMetrics();
        metrics.quality = await this.processQualityMetrics();

        resolve(this.normalizeMetrics(metrics));
      });
    });
  }

  processExecutionMetrics() {
    const total = this.testResults.length;
    const passed = this.testResults.filter(test => test.state === 'passed').length;
    const failed = this.testResults.filter(test => test.state === 'failed').length;
    const skipped = this.testResults.filter(test => test.pending).length;

    return {
      totalTests: total,
      passedTests: passed,
      failedTests: failed,
      skippedTests: skipped,
      passRate: (passed / total) * 100,
      executionTime: Date.now() - this.startTime,
      testSuites: this.groupTestsBySuite()
    };
  }
}
```

#### Pytest Adapter
```python
# pytest_adapter.py
import pytest
import json
import time
import psutil
import hashlib
from typing import Dict, List, Any

class PytestAdapter:
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.framework_name = 'pytest'
        self.version = self.detect_version()
        self.test_results = []
        self.start_time = None
        self.coverage_data = None

    def pytest_configure(self, config):
        """Called after command line options have been parsed."""
        self.start_time = time.time()
        self.initialize_metric_collection()

    def pytest_runtest_setup(self, item):
        """Called before each test is executed."""
        item.start_time = time.time()
        item.start_memory = psutil.Process().memory_info().rss

    def pytest_runtest_teardown(self, item):
        """Called after each test is executed."""
        item.end_time = time.time()
        item.end_memory = psutil.Process().memory_info().rss
        item.duration = item.end_time - item.start_time
        item.memory_delta = item.end_memory - item.start_memory

    def pytest_runtest_logreport(self, report):
        """Called after each test phase (setup, call, teardown)."""
        if report.when == 'call':
            self.test_results.append({
                'nodeid': report.nodeid,
                'outcome': report.outcome,
                'duration': getattr(report, 'duration', 0),
                'memory_delta': getattr(report, 'memory_delta', 0),
                'longrepr': str(report.longrepr) if report.longrepr else None
            })

    def pytest_sessionfinish(self, session, exitstatus):
        """Called after whole test run finished."""
        self.finalize_metrics(session, exitstatus)

    def collect_metrics(self) -> Dict[str, Any]:
        """Main method to collect and return all metrics."""
        metrics = {
            'framework': {
                'name': 'pytest',
                'version': self.version,
                'config_hash': self.generate_config_hash()
            },
            'execution': self.extract_execution_metrics(),
            'coverage': self.extract_coverage_metrics(),
            'performance': self.extract_performance_metrics(),
            'quality': self.extract_quality_metrics()
        }

        return self.normalize_metrics(metrics)

    def extract_execution_metrics(self) -> Dict[str, Any]:
        total = len(self.test_results)
        passed = len([r for r in self.test_results if r['outcome'] == 'passed'])
        failed = len([r for r in self.test_results if r['outcome'] == 'failed'])
        skipped = len([r for r in self.test_results if r['outcome'] == 'skipped'])

        return {
            'total_tests': total,
            'passed_tests': passed,
            'failed_tests': failed,
            'skipped_tests': skipped,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'execution_time': (time.time() - self.start_time) * 1000,  # Convert to ms
            'test_details': self.test_results
        }

    def extract_coverage_metrics(self) -> Dict[str, Any]:
        """Extract coverage metrics using coverage.py integration."""
        try:
            import coverage
            cov = coverage.Coverage()
            cov.load()

            # Get coverage report
            report = cov.report(show_missing=False, skip_covered=False)

            return {
                'overall': {
                    'line_coverage': cov.get_summary()['covered_lines'] / cov.get_summary()['num_statements'] * 100,
                    'branch_coverage': self.get_branch_coverage(cov),
                    'function_coverage': self.get_function_coverage(cov),
                    'statement_coverage': cov.get_summary()['covered_lines'] / cov.get_summary()['num_statements'] * 100
                },
                'by_file': self.get_file_coverage(cov),
                'uncovered_lines': self.get_uncovered_lines(cov)
            }
        except ImportError:
            return {'error': 'Coverage.py not available'}

    def extract_performance_metrics(self) -> Dict[str, Any]:
        """Extract performance and resource usage metrics."""
        process = psutil.Process()
        memory_info = process.memory_info()

        durations = [r['duration'] for r in self.test_results if r['duration']]

        return {
            'memory_usage': {
                'peak_memory_mb': memory_info.rss / 1024 / 1024,
                'average_memory_mb': sum(r.get('memory_delta', 0) for r in self.test_results) / len(self.test_results) / 1024 / 1024,
                'memory_leak_detected': self.detect_memory_leaks()
            },
            'timing': {
                'slowest_tests': sorted(self.test_results, key=lambda x: x['duration'], reverse=True)[:10],
                'fastest_tests': sorted(self.test_results, key=lambda x: x['duration'])[:10],
                'average_test_duration': sum(durations) / len(durations) if durations else 0
            },
            'cpu_usage': {
                'peak_cpu_percentage': process.cpu_percent(),
                'average_cpu_percentage': self.calculate_average_cpu()
            }
        }
```

#### Generic Adapter Framework
```javascript
// generic-adapter.js
class GenericAdapter {
  constructor(config) {
    this.config = config;
    this.frameworkName = config.frameworkName;
    this.version = config.version || 'unknown';
    this.customHooks = config.hooks || {};
  }

  async collectMetrics(testData) {
    const baseMetrics = {
      framework: {
        name: this.frameworkName,
        version: this.version,
        configHash: this.generateConfigHash()
      }
    };

    // Apply custom metric extraction functions
    for (const [metricType, extractor] of Object.entries(this.customHooks)) {
      if (typeof extractor === 'function') {
        try {
          baseMetrics[metricType] = await extractor(testData, this.config);
        } catch (error) {
          console.warn(`Failed to extract ${metricType} metrics:`, error);
          baseMetrics[metricType] = { error: error.message };
        }
      }
    }

    return this.normalizeMetrics(baseMetrics);
  }

  // Extensible metric extraction
  registerMetricExtractor(metricType, extractorFunction) {
    this.customHooks[metricType] = extractorFunction;
  }

  // Template for custom extractors
  static createCustomExtractor(extractorConfig) {
    return async (testData, config) => {
      // Custom extraction logic based on configuration
      const metrics = {};

      for (const [key, path] of Object.entries(extractorConfig.mappings)) {
        metrics[key] = this.extractFromPath(testData, path);
      }

      return metrics;
    };
  }
}
```

### 3. Framework Detection Layer

```javascript
// framework-detector.js
class FrameworkDetector {
  static async detectFrameworks(projectPath) {
    const detectedFrameworks = [];

    // Check package.json dependencies
    const packageJson = await this.readPackageJson(projectPath);
    if (packageJson) {
      const allDeps = {
        ...packageJson.dependencies,
        ...packageJson.devDependencies
      };

      if (allDeps.jest) {
        detectedFrameworks.push({
          name: 'jest',
          version: allDeps.jest,
          configFile: await this.findConfigFile(projectPath, ['jest.config.js', 'jest.config.json'])
        });
      }

      if (allDeps.mocha) {
        detectedFrameworks.push({
          name: 'mocha',
          version: allDeps.mocha,
          configFile: await this.findConfigFile(projectPath, ['.mocharc.json', 'mocha.opts'])
        });
      }
    }

    // Check Python requirements
    const requirements = await this.readRequirements(projectPath);
    if (requirements && requirements.includes('pytest')) {
      detectedFrameworks.push({
        name: 'pytest',
        version: this.extractVersionFromRequirements(requirements, 'pytest'),
        configFile: await this.findConfigFile(projectPath, ['pytest.ini', 'pyproject.toml'])
      });
    }

    // Check for test directories and files
    const testPatterns = await this.analyzeTestPatterns(projectPath);

    return {
      frameworks: detectedFrameworks,
      testPatterns,
      recommendedAdapter: this.recommendAdapter(detectedFrameworks)
    };
  }

  static recommendAdapter(frameworks) {
    if (frameworks.length === 1) {
      return frameworks[0].name;
    }

    // Multi-framework projects
    if (frameworks.length > 1) {
      return 'multi-framework';
    }

    return 'generic';
  }
}
```

### 4. Metric Normalization Layer

```javascript
// metric-normalizer.js
class MetricNormalizer {
  static normalizeMetrics(rawMetrics, frameworkName) {
    const normalized = {
      metadata: {
        framework: frameworkName,
        version: rawMetrics.framework.version,
        timestamp: new Date().toISOString(),
        normalizer_version: '1.0.0'
      },
      execution: this.normalizeExecution(rawMetrics.execution),
      coverage: this.normalizeCoverage(rawMetrics.coverage),
      performance: this.normalizePerformance(rawMetrics.performance),
      quality: this.normalizeQuality(rawMetrics.quality)
    };

    return this.validateNormalizedMetrics(normalized);
  }

  static normalizeExecution(executionData) {
    return {
      total_tests: this.safeInteger(executionData.totalTests || executionData.total_tests),
      passed_tests: this.safeInteger(executionData.passedTests || executionData.passed_tests),
      failed_tests: this.safeInteger(executionData.failedTests || executionData.failed_tests),
      skipped_tests: this.safeInteger(executionData.skippedTests || executionData.skipped_tests || 0),
      pass_rate_percentage: this.safeFloat(executionData.passRate || executionData.pass_rate || 0),
      total_execution_time_ms: this.safeInteger(executionData.executionTime || executionData.execution_time || 0),
      average_test_duration_ms: this.calculateAverageTestDuration(executionData)
    };
  }

  static normalizeCoverage(coverageData) {
    if (!coverageData || coverageData.error) {
      return {
        overall: {
          line_coverage: 0,
          branch_coverage: 0,
          function_coverage: 0,
          statement_coverage: 0
        },
        available: false,
        error: coverageData?.error || 'Coverage data not available'
      };
    }

    const overall = coverageData.overall || {};
    return {
      overall: {
        line_coverage: this.safeFloat(overall.lineCoverage || overall.line_coverage || 0),
        branch_coverage: this.safeFloat(overall.branchCoverage || overall.branch_coverage || 0),
        function_coverage: this.safeFloat(overall.functionCoverage || overall.function_coverage || 0),
        statement_coverage: this.safeFloat(overall.statementCoverage || overall.statement_coverage || 0)
      },
      by_file: this.normalizeByCoverage(coverageData.byFile || coverageData.by_file),
      uncovered_lines: coverageData.uncoveredLines || coverageData.uncovered_lines || [],
      available: true
    };
  }

  static normalizePerformance(performanceData) {
    if (!performanceData) {
      return {
        memory_usage: { peak_memory_mb: 0, average_memory_mb: 0 },
        timing: { average_test_duration_ms: 0 },
        available: false
      };
    }

    const memory = performanceData.memoryUsage || performanceData.memory_usage || {};
    const timing = performanceData.timing || {};

    return {
      memory_usage: {
        peak_memory_mb: this.safeFloat(memory.peakMemoryMB || memory.peak_memory_mb || 0),
        average_memory_mb: this.safeFloat(memory.averageMemoryMB || memory.average_memory_mb || 0),
        memory_leak_detected: Boolean(memory.memoryLeakDetected || memory.memory_leak_detected)
      },
      timing: {
        average_test_duration_ms: this.safeFloat(timing.averageTestDuration || timing.average_test_duration || 0),
        slowest_test_ms: this.extractSlowestTest(timing),
        fastest_test_ms: this.extractFastestTest(timing)
      },
      cpu_usage: this.normalizeCpuUsage(performanceData.cpuUsage || performanceData.cpu_usage),
      available: true
    };
  }

  static normalizeQuality(qualityData) {
    if (!qualityData) {
      return {
        flaky_tests: [],
        stability_score: 1.0,
        available: false
      };
    }

    return {
      flaky_tests: this.normalizeFlakyTests(qualityData.flakyTests || qualityData.flaky_tests || []),
      new_tests: qualityData.newTests || qualityData.new_tests || [],
      deleted_tests: qualityData.deletedTests || qualityData.deleted_tests || [],
      stability_score: this.safeFloat(qualityData.stabilityScore || qualityData.stability_score || 1.0),
      complexity: qualityData.complexity || {},
      available: true
    };
  }

  static safeInteger(value) {
    const parsed = parseInt(value);
    return isNaN(parsed) ? 0 : parsed;
  }

  static safeFloat(value) {
    const parsed = parseFloat(value);
    return isNaN(parsed) ? 0.0 : parsed;
  }

  static validateNormalizedMetrics(metrics) {
    const errors = [];

    // Validate execution metrics
    if (metrics.execution.total_tests < 0) {
      errors.push('Total tests cannot be negative');
    }

    if (metrics.execution.passed_tests + metrics.execution.failed_tests + metrics.execution.skipped_tests > metrics.execution.total_tests) {
      errors.push('Sum of test results exceeds total tests');
    }

    // Validate coverage percentages
    const coverageMetrics = ['line_coverage', 'branch_coverage', 'function_coverage', 'statement_coverage'];
    for (const metric of coverageMetrics) {
      const value = metrics.coverage.overall[metric];
      if (value < 0 || value > 100) {
        errors.push(`${metric} must be between 0 and 100`);
      }
    }

    if (errors.length > 0) {
      metrics.validation_errors = errors;
    }

    return metrics;
  }
}
```

### 5. Collection Orchestrator

```javascript
// collection-orchestrator.js
class CollectionOrchestrator {
  constructor(config) {
    this.config = config;
    this.adapters = new Map();
    this.detector = new FrameworkDetector();
    this.normalizer = new MetricNormalizer();
  }

  async initialize() {
    // Detect available frameworks
    const detection = await this.detector.detectFrameworks(this.config.projectPath);

    // Initialize appropriate adapters
    for (const framework of detection.frameworks) {
      const adapter = this.createAdapter(framework);
      this.adapters.set(framework.name, adapter);
    }

    return detection;
  }

  async collectAllMetrics() {
    const results = new Map();

    // Collect metrics from each framework
    for (const [frameworkName, adapter] of this.adapters) {
      try {
        const rawMetrics = await adapter.collectMetrics();
        const normalizedMetrics = this.normalizer.normalizeMetrics(rawMetrics, frameworkName);
        results.set(frameworkName, normalizedMetrics);
      } catch (error) {
        console.error(`Failed to collect metrics from ${frameworkName}:`, error);
        results.set(frameworkName, { error: error.message });
      }
    }

    // Merge metrics if multiple frameworks
    if (results.size > 1) {
      return this.mergeMultiFrameworkMetrics(results);
    }

    return results.values().next().value;
  }

  createAdapter(frameworkConfig) {
    switch (frameworkConfig.name) {
      case 'jest':
        return new JestAdapter(frameworkConfig);
      case 'mocha':
        return new MochaAdapter(frameworkConfig);
      case 'pytest':
        return new PytestAdapter(frameworkConfig);
      default:
        return new GenericAdapter(frameworkConfig);
    }
  }

  mergeMultiFrameworkMetrics(frameworkResults) {
    const merged = {
      metadata: {
        frameworks: Array.from(frameworkResults.keys()),
        timestamp: new Date().toISOString(),
        merge_strategy: 'aggregate'
      },
      execution: this.mergeExecutionMetrics(frameworkResults),
      coverage: this.mergeCoverageMetrics(frameworkResults),
      performance: this.mergePerformanceMetrics(frameworkResults),
      quality: this.mergeQualityMetrics(frameworkResults)
    };

    return merged;
  }
}
```

This metrics collection framework provides comprehensive, extensible support for multiple testing frameworks while maintaining data consistency and enabling deep insights into test execution patterns and quality metrics.