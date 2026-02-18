/**
 * Base Test Framework Adapter
 *
 * Provides the interface and common functionality for all test framework adapters.
 * Each adapter implements framework-specific methods while maintaining consistent API.
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;

/**
 * Base class for all test framework adapters
 */
class BaseTestAdapter extends EventEmitter {
  constructor(options = {}) {
    super();
    this.options = {
      rootDir: process.cwd(),
      timeout: 30000,
      retries: 0,
      bail: false,
      verbose: false,
      coverage: false,
      profiling: false,
      baseline: null,
      ...options
    };

    this.framework = null;
    this.version = null;
    this.configPath = null;
    this.testFiles = [];
    this.results = {
      tests: [],
      summary: {},
      coverage: null,
      profiling: null,
      baseline: null
    };
  }

  /**
   * Detect if this framework is available and configured
   * @returns {Promise<boolean>}
   */
  async detect() {
    try {
      const isAvailable = await this._detectFramework();
      if (isAvailable) {
        this.configPath = await this._findConfig();
        this.version = await this._getVersion();
      }
      return isAvailable;
    } catch (error) {
      this.emit('error', error);
      return false;
    }
  }

  /**
   * Initialize the adapter with framework-specific setup
   * @returns {Promise<void>}
   */
  async initialize() {
    await this._loadConfig();
    await this._setupReporters();
    await this._setupCoverage();
    await this._setupProfiling();
    this.emit('initialized', { framework: this.framework, version: this.version });
  }

  /**
   * Discover test files based on framework patterns
   * @returns {Promise<string[]>}
   */
  async discoverTests() {
    const patterns = this._getTestPatterns();
    const files = [];

    for (const pattern of patterns) {
      const matches = await this._glob(pattern);
      files.push(...matches);
    }

    this.testFiles = [...new Set(files)];
    this.emit('testsDiscovered', { count: this.testFiles.length, files: this.testFiles });
    return this.testFiles;
  }

  /**
   * Run tests with the framework
   * @param {Object} options - Run options
   * @returns {Promise<Object>}
   */
  async runTests(options = {}) {
    const runOptions = { ...this.options, ...options };

    this.emit('runStarted', { options: runOptions });

    try {
      await this._preRun(runOptions);
      const results = await this._executeTests(runOptions);
      await this._postRun(results);

      this.results = results;
      this.emit('runCompleted', results);
      return results;
    } catch (error) {
      this.emit('error', error);
      throw error;
    }
  }

  /**
   * Stop running tests
   * @returns {Promise<void>}
   */
  async stopTests() {
    await this._stopExecution();
    this.emit('runStopped');
  }

  /**
   * Get test results with optional filtering
   * @param {Object} filter - Result filter options
   * @returns {Object}
   */
  getResults(filter = {}) {
    let results = { ...this.results };

    if (filter.status) {
      results.tests = results.tests.filter(test => test.status === filter.status);
    }

    if (filter.suite) {
      results.tests = results.tests.filter(test => test.suite === filter.suite);
    }

    return results;
  }

  /**
   * Compare results with baseline
   * @param {Object} baseline - Baseline results
   * @returns {Object}
   */
  compareWithBaseline(baseline) {
    if (!baseline) return null;

    const comparison = {
      testsAdded: [],
      testsRemoved: [],
      testsChanged: [],
      performance: {
        faster: [],
        slower: [],
        avgChange: 0
      },
      coverage: {
        improved: false,
        degraded: false,
        change: 0
      }
    };

    // Compare test results
    const currentTests = new Map(this.results.tests.map(t => [t.name, t]));
    const baselineTests = new Map(baseline.tests.map(t => [t.name, t]));

    // Find added/removed tests
    for (const [name, test] of currentTests) {
      if (!baselineTests.has(name)) {
        comparison.testsAdded.push(test);
      }
    }

    for (const [name, test] of baselineTests) {
      if (!currentTests.has(name)) {
        comparison.testsRemoved.push(test);
      }
    }

    // Find changed tests
    for (const [name, currentTest] of currentTests) {
      const baselineTest = baselineTests.get(name);
      if (baselineTest) {
        if (currentTest.status !== baselineTest.status) {
          comparison.testsChanged.push({
            name,
            from: baselineTest.status,
            to: currentTest.status
          });
        }

        // Performance comparison
        if (currentTest.duration && baselineTest.duration) {
          const change = currentTest.duration - baselineTest.duration;
          if (change < 0) {
            comparison.performance.faster.push({ name, improvement: Math.abs(change) });
          } else if (change > 0) {
            comparison.performance.slower.push({ name, regression: change });
          }
        }
      }
    }

    // Coverage comparison
    if (this.results.coverage && baseline.coverage) {
      const currentCoverage = this.results.coverage.total || 0;
      const baselineCoverage = baseline.coverage.total || 0;
      comparison.coverage.change = currentCoverage - baselineCoverage;
      comparison.coverage.improved = comparison.coverage.change > 0;
      comparison.coverage.degraded = comparison.coverage.change < 0;
    }

    return comparison;
  }

  // Abstract methods to be implemented by framework adapters
  async _detectFramework() { throw new Error('_detectFramework must be implemented'); }
  async _findConfig() { throw new Error('_findConfig must be implemented'); }
  async _getVersion() { throw new Error('_getVersion must be implemented'); }
  async _loadConfig() { throw new Error('_loadConfig must be implemented'); }
  async _setupReporters() { throw new Error('_setupReporters must be implemented'); }
  async _setupCoverage() { /* Optional */ }
  async _setupProfiling() { /* Optional */ }
  _getTestPatterns() { throw new Error('_getTestPatterns must be implemented'); }
  async _executeTests(options) { throw new Error('_executeTests must be implemented'); }
  async _preRun(options) { /* Optional */ }
  async _postRun(results) { /* Optional */ }
  async _stopExecution() { /* Optional */ }

  // Helper methods
  async _glob(pattern) {
    const glob = require('glob');
    return new Promise((resolve, reject) => {
      glob(pattern, { cwd: this.options.rootDir }, (err, files) => {
        if (err) reject(err);
        else resolve(files);
      });
    });
  }

  async _fileExists(filePath) {
    try {
      await fs.access(filePath);
      return true;
    } catch {
      return false;
    }
  }

  async _readJson(filePath) {
    try {
      const content = await fs.readFile(filePath, 'utf8');
      return JSON.parse(content);
    } catch {
      return null;
    }
  }

  _formatDuration(ms) {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
    return `${Math.floor(ms / 60000)}m ${Math.floor((ms % 60000) / 1000)}s`;
  }

  _calculateSummary(tests) {
    const summary = {
      total: tests.length,
      passed: 0,
      failed: 0,
      skipped: 0,
      pending: 0,
      duration: 0,
      success: true
    };

    for (const test of tests) {
      summary[test.status]++;
      summary.duration += test.duration || 0;
    }

    summary.success = summary.failed === 0;
    return summary;
  }
}

module.exports = BaseTestAdapter;