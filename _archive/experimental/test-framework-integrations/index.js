/**
 * Test Framework Integrations
 *
 * Main entry point for the unified test framework integration system.
 * Provides a simple API for running tests across different frameworks
 * with baseline tracking, coverage collection, and performance profiling.
 */

const UnifiedTestRunner = require('./runners/unified-test-runner');
const CoverageIntegrator = require('./coverage/coverage-integrator');
const PerformanceProfiler = require('./profilers/performance-profiler');
const BaselineReporter = require('./reporters/baseline-reporter');

// Export individual adapters
const JestAdapter = require('./adapters/jest/jest-adapter');
const MochaAdapter = require('./adapters/mocha/mocha-adapter');
const PytestAdapter = require('./adapters/pytest/pytest-adapter');
const VitestAdapter = require('./adapters/vitest/vitest-adapter');
const PlaywrightAdapter = require('./adapters/playwright/playwright-adapter');

/**
 * Main TestFrameworkIntegrations class
 * Orchestrates test execution with integrated coverage, profiling, and reporting
 */
class TestFrameworkIntegrations {
  constructor(options = {}) {
    this.options = {
      rootDir: process.cwd(),
      preferredFramework: null,
      coverage: false,
      profiling: false,
      baseline: null,
      parallel: false,
      autoDetect: true,
      reporter: 'console',
      outputDir: '.test-baseline',
      ...options
    };

    this.runner = null;
    this.coverage = null;
    this.profiler = null;
    this.reporter = null;
    this.results = null;
  }

  /**
   * Initialize the test integration system
   * @returns {Promise<void>}
   */
  async initialize() {
    // Initialize test runner
    this.runner = new UnifiedTestRunner(this.options);
    await this.runner.initialize();

    // Initialize coverage if enabled
    if (this.options.coverage) {
      this.coverage = new CoverageIntegrator(this.options);
      await this.coverage.initialize();
    }

    // Initialize profiler if enabled
    if (this.options.profiling) {
      this.profiler = new PerformanceProfiler(this.options);
      await this.profiler.initialize();
    }

    // Initialize reporter
    this.reporter = new BaselineReporter({
      ...this.options,
      format: this.options.reporter
    });
    await this.reporter.initialize();

    // Set up event forwarding
    this._setupEventForwarding();
  }

  /**
   * Discover all test files
   * @returns {Promise<string[]>}
   */
  async discoverTests() {
    if (!this.runner) {
      throw new Error('TestFrameworkIntegrations not initialized. Call initialize() first.');
    }

    return await this.runner.discoverTests();
  }

  /**
   * Run tests with integrated coverage, profiling, and reporting
   * @param {Object} options - Run options
   * @returns {Promise<Object>}
   */
  async runTests(options = {}) {
    if (!this.runner) {
      throw new Error('TestFrameworkIntegrations not initialized. Call initialize() first.');
    }

    const runOptions = { ...this.options, ...options };

    try {
      // Start profiling if enabled
      if (this.profiler) {
        await this.profiler.startProfiling();
      }

      // Notify reporter of run start
      this.reporter.onRunStart({
        framework: this.runner.activeAdapter ? {
          name: this.runner.activeAdapter.framework,
          version: this.runner.activeAdapter.version
        } : null,
        options: runOptions
      });

      // Run tests
      let results;
      if (this.coverage) {
        // Run with coverage collection
        const framework = this.runner.activeAdapter.framework;
        const command = this._buildTestCommand(runOptions);

        results = await this.runner.runTests(runOptions);

        // Collect coverage separately
        const coverageData = await this.coverage.collectCoverage(framework, command, runOptions);
        results.coverage = coverageData;
      } else {
        results = await this.runner.runTests(runOptions);
      }

      // Stop profiling and collect data
      if (this.profiler) {
        const profilingData = await this.profiler.stopProfiling();
        results.profiling = profilingData;
      }

      // Store results
      this.results = results;

      // Generate reports
      await this.reporter.onRunComplete(results);

      return results;

    } catch (error) {
      // Stop profiling on error
      if (this.profiler && this.profiler.isRunning) {
        await this.profiler.stopProfiling();
      }

      this.reporter.onRunFailed({ error: error.message });
      throw error;
    }
  }

  /**
   * Run tests across all detected frameworks
   * @param {Object} options - Run options
   * @returns {Promise<Object>}
   */
  async runAllFrameworks(options = {}) {
    if (!this.runner) {
      throw new Error('TestFrameworkIntegrations not initialized. Call initialize() first.');
    }

    return await this.runner.runAllFrameworks(options);
  }

  /**
   * Stop running tests
   * @returns {Promise<void>}
   */
  async stopTests() {
    if (this.runner) {
      await this.runner.stopTests();
    }

    if (this.profiler && this.profiler.isRunning) {
      await this.profiler.stopProfiling();
    }
  }

  /**
   * Get information about detected frameworks
   * @returns {Array}
   */
  getDetectedFrameworks() {
    if (!this.runner) {
      return [];
    }

    return this.runner.getDetectedFrameworks();
  }

  /**
   * Switch to a different framework
   * @param {string} framework - Framework name
   * @returns {Promise<void>}
   */
  async switchFramework(framework) {
    if (!this.runner) {
      throw new Error('TestFrameworkIntegrations not initialized. Call initialize() first.');
    }

    await this.runner.switchFramework(framework);
  }

  /**
   * Compare current results with baseline
   * @param {Object} baseline - Baseline results
   * @returns {Object}
   */
  compareWithBaseline(baseline) {
    if (!this.results) {
      return null;
    }

    return this.runner.compareWithBaseline(baseline);
  }

  /**
   * Generate coverage reports
   * @param {string} name - Report name
   * @returns {Promise<Array<string>>}
   */
  async generateCoverageReports(name = 'coverage') {
    if (!this.coverage) {
      throw new Error('Coverage not enabled. Set coverage: true in options.');
    }

    const frameworks = Array.from(this.coverage.reports.keys());
    if (frameworks.length > 1) {
      await this.coverage.mergeCoverage(frameworks);
      return await this.coverage.generateReports(this.coverage.mergedReport, 'merged');
    } else if (frameworks.length === 1) {
      const report = this.coverage.reports.get(frameworks[0]);
      return await this.coverage.generateReports(report, name);
    }

    return [];
  }

  /**
   * Analyze performance bottlenecks
   * @returns {Object}
   */
  analyzeBottlenecks() {
    if (!this.profiler) {
      throw new Error('Profiling not enabled. Set profiling: true in options.');
    }

    return this.profiler.analyzeBottlenecks();
  }

  /**
   * Save current results as baseline
   * @param {string} label - Baseline label
   * @returns {Promise<void>}
   */
  async saveBaseline(label = 'latest') {
    if (!this.results) {
      throw new Error('No test results available. Run tests first.');
    }

    // Save baseline for coverage
    if (this.coverage && this.results.coverage) {
      await this.coverage.saveBaseline(this.results.coverage, label);
    }

    // Save baseline for runner
    const baselineData = {
      timestamp: new Date().toISOString(),
      label,
      framework: this.results.framework,
      results: {
        tests: this.results.tests,
        summary: this.results.summary,
        coverage: this.results.coverage
      }
    };

    const fs = require('fs').promises;
    const path = require('path');

    const baselineDir = path.join(this.options.rootDir, this.options.outputDir, 'baselines');
    await fs.mkdir(baselineDir, { recursive: true });

    const baselineFile = path.join(baselineDir, `${label}.json`);
    await fs.writeFile(baselineFile, JSON.stringify(baselineData, null, 2));
  }

  /**
   * Get current performance metrics (while tests are running)
   * @returns {Object}
   */
  getCurrentMetrics() {
    if (!this.profiler) {
      return null;
    }

    return this.profiler.getCurrentMetrics();
  }

  // Private methods

  _setupEventForwarding() {
    // Forward runner events to reporter
    this.runner.on('testStarted', (data) => {
      if (this.profiler) {
        this.profiler.markTestStart(data.testName || 'unknown', data);
      }
    });

    this.runner.on('testOutput', (data) => {
      this.reporter.onTestOutput(data);
    });

    this.runner.on('testCompleted', (data) => {
      if (this.profiler) {
        this.profiler.markTestEnd(data.testName || 'unknown', data);
      }
      this.reporter.onTestComplete(data);
    });

    this.runner.on('error', (error) => {
      this.reporter.onRunFailed({ error: error.message || error });
    });

    // Forward coverage events
    if (this.coverage) {
      this.coverage.on('collectionCompleted', (data) => {
        console.log(`✅ Coverage collected for ${data.framework}: ${data.coverage.total.toFixed(2)}%`);
      });

      this.coverage.on('thresholdCheck', (results) => {
        if (!results.passed) {
          console.log(`⚠️  Coverage thresholds not met: ${results.failures.map(f => f.metric).join(', ')}`);
        }
      });
    }

    // Forward profiler events
    if (this.profiler) {
      this.profiler.on('profilingStarted', () => {
        console.log('🔍 Performance profiling started');
      });

      this.profiler.on('reportGenerated', (data) => {
        console.log('📊 Performance report generated');
      });
    }
  }

  _buildTestCommand(options) {
    // Build appropriate test command based on active framework
    const framework = this.runner.activeAdapter.framework;

    switch (framework) {
      case 'jest':
        return 'jest --json';
      case 'mocha':
        return 'mocha --reporter json';
      case 'vitest':
        return 'vitest run --reporter json';
      case 'pytest':
        return 'pytest --json-report';
      case 'playwright':
        return 'playwright test --reporter json';
      default:
        return 'npm test';
    }
  }
}

// Static factory methods
TestFrameworkIntegrations.createRunner = (options) => {
  return new UnifiedTestRunner(options);
};

TestFrameworkIntegrations.createCoverageIntegrator = (options) => {
  return new CoverageIntegrator(options);
};

TestFrameworkIntegrations.createPerformanceProfiler = (options) => {
  return new PerformanceProfiler(options);
};

TestFrameworkIntegrations.createBaselineReporter = (options) => {
  return new BaselineReporter(options);
};

// Export adapters
TestFrameworkIntegrations.adapters = {
  JestAdapter,
  MochaAdapter,
  PytestAdapter,
  VitestAdapter,
  PlaywrightAdapter
};

// Export main class and components
module.exports = TestFrameworkIntegrations;
module.exports.UnifiedTestRunner = UnifiedTestRunner;
module.exports.CoverageIntegrator = CoverageIntegrator;
module.exports.PerformanceProfiler = PerformanceProfiler;
module.exports.BaselineReporter = BaselineReporter;