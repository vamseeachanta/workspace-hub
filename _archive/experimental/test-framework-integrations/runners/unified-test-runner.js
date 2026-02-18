/**
 * Unified Test Runner
 *
 * Auto-detects available test frameworks and provides a unified interface
 * for running tests with baseline tracking, coverage collection, and performance profiling.
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;

// Import all adapters
const JestAdapter = require('../adapters/jest/jest-adapter');
const MochaAdapter = require('../adapters/mocha/mocha-adapter');
const PytestAdapter = require('../adapters/pytest/pytest-adapter');
const VitestAdapter = require('../adapters/vitest/vitest-adapter');
const PlaywrightAdapter = require('../adapters/playwright/playwright-adapter');

class UnifiedTestRunner extends EventEmitter {
  constructor(options = {}) {
    super();
    this.options = {
      rootDir: process.cwd(),
      preferredFramework: null,
      parallel: false,
      coverage: false,
      profiling: false,
      baseline: null,
      autoDetect: true,
      fallbackOrder: ['jest', 'vitest', 'mocha', 'pytest', 'playwright'],
      ...options
    };

    this.adapters = new Map();
    this.detectedFrameworks = [];
    this.activeAdapter = null;
    this.results = null;
  }

  /**
   * Initialize the runner by detecting available frameworks
   * @returns {Promise<void>}
   */
  async initialize() {
    this.emit('initialization', { status: 'started' });

    try {
      await this._detectFrameworks();
      await this._selectAdapter();

      if (this.activeAdapter) {
        await this.activeAdapter.initialize();
        this.emit('initialization', {
          status: 'completed',
          framework: this.activeAdapter.framework,
          version: this.activeAdapter.version
        });
      } else {
        throw new Error('No compatible test frameworks detected');
      }
    } catch (error) {
      this.emit('initialization', { status: 'failed', error: error.message });
      throw error;
    }
  }

  /**
   * Discover test files using the active adapter
   * @returns {Promise<string[]>}
   */
  async discoverTests() {
    if (!this.activeAdapter) {
      throw new Error('Runner not initialized. Call initialize() first.');
    }

    const files = await this.activeAdapter.discoverTests();
    this.emit('testsDiscovered', {
      framework: this.activeAdapter.framework,
      count: files.length,
      files
    });

    return files;
  }

  /**
   * Run tests with the active adapter
   * @param {Object} options - Run options
   * @returns {Promise<Object>}
   */
  async runTests(options = {}) {
    if (!this.activeAdapter) {
      throw new Error('Runner not initialized. Call initialize() first.');
    }

    const runOptions = { ...this.options, ...options };

    // Set up event forwarding
    this._forwardEvents(this.activeAdapter);

    try {
      this.results = await this.activeAdapter.runTests(runOptions);

      // Enhance results with framework information
      this.results.framework = {
        name: this.activeAdapter.framework,
        version: this.activeAdapter.version,
        adapter: this.activeAdapter.constructor.name
      };

      // Save results for baseline comparison
      if (runOptions.saveBaseline) {
        await this._saveBaseline(this.results);
      }

      this.emit('runCompleted', {
        framework: this.activeAdapter.framework,
        results: this.results
      });

      return this.results;
    } catch (error) {
      this.emit('runFailed', {
        framework: this.activeAdapter.framework,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Run tests across multiple detected frameworks
   * @param {Object} options - Run options
   * @returns {Promise<Object>}
   */
  async runAllFrameworks(options = {}) {
    const results = {};
    const errors = {};

    for (const framework of this.detectedFrameworks) {
      this.emit('frameworkRunStarted', { framework });

      try {
        const adapter = this.adapters.get(framework);
        await adapter.initialize();

        this._forwardEvents(adapter, framework);

        const frameworkResults = await adapter.runTests({ ...this.options, ...options });
        results[framework] = {
          ...frameworkResults,
          framework: {
            name: adapter.framework,
            version: adapter.version,
            adapter: adapter.constructor.name
          }
        };

        this.emit('frameworkRunCompleted', { framework, results: frameworkResults });
      } catch (error) {
        errors[framework] = error.message;
        this.emit('frameworkRunFailed', { framework, error: error.message });
      }
    }

    const summary = this._createMultiFrameworkSummary(results, errors);

    this.emit('allFrameworksCompleted', { results, errors, summary });

    return { results, errors, summary };
  }

  /**
   * Stop running tests
   * @returns {Promise<void>}
   */
  async stopTests() {
    if (this.activeAdapter) {
      await this.activeAdapter.stopTests();
    }

    // Stop all adapters if running multiple
    for (const adapter of this.adapters.values()) {
      try {
        await adapter.stopTests();
      } catch {
        // Ignore errors when stopping
      }
    }

    this.emit('testsStopped');
  }

  /**
   * Get results from the last test run
   * @param {Object} filter - Result filter options
   * @returns {Object}
   */
  getResults(filter = {}) {
    if (!this.results) {
      return null;
    }

    if (this.activeAdapter) {
      return this.activeAdapter.getResults(filter);
    }

    return this.results;
  }

  /**
   * Compare current results with baseline
   * @param {Object} baseline - Baseline results
   * @returns {Object}
   */
  compareWithBaseline(baseline) {
    if (!this.results || !this.activeAdapter) {
      return null;
    }

    return this.activeAdapter.compareWithBaseline(baseline);
  }

  /**
   * Get information about detected frameworks
   * @returns {Array}
   */
  getDetectedFrameworks() {
    return this.detectedFrameworks.map(framework => {
      const adapter = this.adapters.get(framework);
      return {
        name: framework,
        version: adapter.version,
        configPath: adapter.configPath,
        testPatterns: adapter._getTestPatterns ? adapter._getTestPatterns() : [],
        isActive: this.activeAdapter === adapter
      };
    });
  }

  /**
   * Switch to a different framework adapter
   * @param {string} framework - Framework name
   * @returns {Promise<void>}
   */
  async switchFramework(framework) {
    if (!this.adapters.has(framework)) {
      throw new Error(`Framework '${framework}' not detected or not supported`);
    }

    const adapter = this.adapters.get(framework);
    await adapter.initialize();

    this.activeAdapter = adapter;
    this.emit('frameworkSwitched', {
      framework,
      version: adapter.version
    });
  }

  // Private methods

  async _detectFrameworks() {
    const adapters = [
      { name: 'jest', class: JestAdapter },
      { name: 'vitest', class: VitestAdapter },
      { name: 'mocha', class: MochaAdapter },
      { name: 'pytest', class: PytestAdapter },
      { name: 'playwright', class: PlaywrightAdapter }
    ];

    this.emit('detection', { status: 'started', frameworks: adapters.map(a => a.name) });

    for (const { name, class: AdapterClass } of adapters) {
      try {
        const adapter = new AdapterClass(this.options);
        const isDetected = await adapter.detect();

        this.adapters.set(name, adapter);

        if (isDetected) {
          this.detectedFrameworks.push(name);
          this.emit('frameworkDetected', {
            framework: name,
            version: adapter.version,
            configPath: adapter.configPath
          });
        }
      } catch (error) {
        this.emit('detectionError', {
          framework: name,
          error: error.message
        });
      }
    }

    this.emit('detection', {
      status: 'completed',
      detected: this.detectedFrameworks
    });

    if (this.detectedFrameworks.length === 0) {
      throw new Error('No compatible test frameworks detected');
    }
  }

  async _selectAdapter() {
    let selectedFramework = null;

    // Use preferred framework if specified and detected
    if (this.options.preferredFramework &&
        this.detectedFrameworks.includes(this.options.preferredFramework)) {
      selectedFramework = this.options.preferredFramework;
    } else {
      // Use fallback order to select framework
      for (const framework of this.options.fallbackOrder) {
        if (this.detectedFrameworks.includes(framework)) {
          selectedFramework = framework;
          break;
        }
      }
    }

    if (!selectedFramework) {
      // Default to first detected framework
      selectedFramework = this.detectedFrameworks[0];
    }

    this.activeAdapter = this.adapters.get(selectedFramework);

    this.emit('adapterSelected', {
      framework: selectedFramework,
      version: this.activeAdapter.version,
      reason: this.options.preferredFramework === selectedFramework ? 'preferred' :
             this.options.fallbackOrder.includes(selectedFramework) ? 'fallback' : 'default'
    });
  }

  _forwardEvents(adapter, prefix = '') {
    const eventPrefix = prefix ? `${prefix}:` : '';

    adapter.on('testStarted', (data) => this.emit(`${eventPrefix}testStarted`, data));
    adapter.on('testOutput', (data) => this.emit(`${eventPrefix}testOutput`, data));
    adapter.on('runCompleted', (data) => this.emit(`${eventPrefix}runCompleted`, data));
    adapter.on('error', (error) => this.emit(`${eventPrefix}error`, error));
  }

  _createMultiFrameworkSummary(results, errors) {
    const summary = {
      frameworks: {
        total: Object.keys(results).length + Object.keys(errors).length,
        successful: Object.keys(results).length,
        failed: Object.keys(errors).length
      },
      tests: {
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0
      },
      coverage: null,
      duration: 0
    };

    // Aggregate test results
    for (const [framework, result] of Object.entries(results)) {
      summary.tests.total += result.summary.total;
      summary.tests.passed += result.summary.passed;
      summary.tests.failed += result.summary.failed;
      summary.tests.skipped += result.summary.skipped;
      summary.duration += result.summary.duration;
    }

    // Find best coverage if available
    let bestCoverage = null;
    let bestCoverageFramework = null;

    for (const [framework, result] of Object.entries(results)) {
      if (result.coverage && result.coverage.total > (bestCoverage?.total || 0)) {
        bestCoverage = result.coverage;
        bestCoverageFramework = framework;
      }
    }

    if (bestCoverage) {
      summary.coverage = {
        ...bestCoverage,
        source: bestCoverageFramework
      };
    }

    return summary;
  }

  async _saveBaseline(results) {
    try {
      const baselineDir = path.join(this.options.rootDir, '.test-baseline');
      await fs.mkdir(baselineDir, { recursive: true });

      const baselineFile = path.join(baselineDir, 'baseline.json');
      const baselineData = {
        timestamp: new Date().toISOString(),
        framework: results.framework,
        results: {
          tests: results.tests,
          summary: results.summary,
          coverage: results.coverage
        }
      };

      await fs.writeFile(baselineFile, JSON.stringify(baselineData, null, 2));

      this.emit('baselineSaved', {
        file: baselineFile,
        framework: results.framework.name
      });
    } catch (error) {
      this.emit('baselineSaveError', { error: error.message });
    }
  }
}

module.exports = UnifiedTestRunner;