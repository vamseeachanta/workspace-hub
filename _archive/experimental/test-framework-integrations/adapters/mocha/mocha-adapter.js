/**
 * Mocha Test Framework Adapter
 *
 * Provides Mocha-specific implementation with hooks integration,
 * custom reporters, and performance tracking.
 */

const BaseTestAdapter = require('../base-adapter');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;

class MochaAdapter extends BaseTestAdapter {
  constructor(options = {}) {
    super(options);
    this.framework = 'mocha';
    this.mochaPath = null;
    this.config = null;
    this.runnerProcess = null;
    this.hooks = {
      before: [],
      after: [],
      beforeEach: [],
      afterEach: []
    };
  }

  async _detectFramework() {
    try {
      // Check for Mocha in package.json
      const packageJson = await this._readJson(path.join(this.options.rootDir, 'package.json'));
      if (packageJson?.dependencies?.mocha || packageJson?.devDependencies?.mocha) {
        this.mochaPath = path.join(this.options.rootDir, 'node_modules/.bin/mocha');
        return await this._fileExists(this.mochaPath);
      }

      // Check for global Mocha
      try {
        require.resolve('mocha');
        this.mochaPath = 'mocha';
        return true;
      } catch {
        return false;
      }
    } catch {
      return false;
    }
  }

  async _findConfig() {
    const configFiles = [
      '.mocharc.json',
      '.mocharc.yaml',
      '.mocharc.yml',
      '.mocharc.js',
      'mocha.opts'
    ];

    for (const configFile of configFiles) {
      const configPath = path.join(this.options.rootDir, configFile);
      if (await this._fileExists(configPath)) {
        return configPath;
      }
    }

    // Check package.json for mocha config
    const packageJsonPath = path.join(this.options.rootDir, 'package.json');
    const packageJson = await this._readJson(packageJsonPath);
    if (packageJson?.mocha) {
      return packageJsonPath;
    }

    return null;
  }

  async _getVersion() {
    try {
      const packageJson = await this._readJson(
        path.join(this.options.rootDir, 'node_modules/mocha/package.json')
      );
      return packageJson?.version || 'unknown';
    } catch {
      return 'unknown';
    }
  }

  async _loadConfig() {
    if (this.configPath) {
      if (this.configPath.endsWith('package.json')) {
        const packageJson = await this._readJson(this.configPath);
        this.config = packageJson.mocha || {};
      } else if (this.configPath.endsWith('.json')) {
        this.config = await this._readJson(this.configPath) || {};
      } else {
        // For JS configs and mocha.opts, we'll handle them via command line
        this.config = {};
      }
    } else {
      this.config = {};
    }
  }

  async _setupReporters() {
    // Create custom reporter for baseline integration
    const reporterPath = path.join(__dirname, 'mocha-baseline-reporter.js');
    await this._createBaselineReporter(reporterPath);

    this.customReporter = reporterPath;
    this.reporterOptions = {
      outputFile: path.join(this.options.rootDir, '.test-baseline/mocha-results.json'),
      baseline: this.options.baseline
    };
  }

  async _setupCoverage() {
    if (this.options.coverage) {
      // Mocha typically uses nyc for coverage
      this.coverageCommand = 'nyc';
      this.coverageOptions = {
        reporter: ['json', 'text', 'html'],
        'report-dir': path.join(this.options.rootDir, '.test-baseline/coverage'),
        include: ['src/**/*.js', 'lib/**/*.js'],
        exclude: ['**/*.test.js', '**/*.spec.js', 'test/**']
      };
    }
  }

  async _setupProfiling() {
    if (this.options.profiling) {
      this.profilingOptions = {
        enableTimeouts: false,
        reporter: 'json',
        reporterOptions: {
          includePerformance: true
        }
      };
    }
  }

  _getTestPatterns() {
    return [
      'test/**/*.js',
      'test/**/*.ts',
      'spec/**/*.js',
      'spec/**/*.ts',
      '**/*.test.js',
      '**/*.test.ts',
      '**/*.spec.js',
      '**/*.spec.ts'
    ];
  }

  /**
   * Add hooks to be executed during test lifecycle
   * @param {string} type - Hook type (before, after, beforeEach, afterEach)
   * @param {function} hook - Hook function
   */
  addHook(type, hook) {
    if (this.hooks[type]) {
      this.hooks[type].push(hook);
    }
  }

  /**
   * Setup hooks file for Mocha
   */
  async _setupHooksFile() {
    const hooksPath = path.join(__dirname, 'mocha-hooks.js');
    const hooksCode = `
const { performance } = require('perf_hooks');

// Performance tracking
const testPerformance = new Map();
let suiteStartTime;

// Global hooks
exports.mochaHooks = {
  beforeAll() {
    console.log('🚀 Starting test suite with baseline tracking');
    suiteStartTime = performance.now();
  },

  beforeEach(done) {
    this.currentTest.startTime = performance.now();

    // Memory snapshot before test
    if (global.gc) {
      global.gc();
    }
    this.currentTest.memoryBefore = process.memoryUsage();

    done();
  },

  afterEach(done) {
    const endTime = performance.now();
    const duration = endTime - this.currentTest.startTime;

    // Memory snapshot after test
    const memoryAfter = process.memoryUsage();

    // Store performance data
    testPerformance.set(this.currentTest.fullTitle(), {
      duration,
      memory: {
        before: this.currentTest.memoryBefore,
        after: memoryAfter,
        delta: {
          rss: memoryAfter.rss - this.currentTest.memoryBefore.rss,
          heapUsed: memoryAfter.heapUsed - this.currentTest.memoryBefore.heapUsed,
          heapTotal: memoryAfter.heapTotal - this.currentTest.memoryBefore.heapTotal
        }
      }
    });

    done();
  },

  afterAll() {
    const totalTime = performance.now() - suiteStartTime;
    console.log(\`✅ Test suite completed in \${totalTime.toFixed(2)}ms\`);

    // Export performance data
    const performanceReport = {
      totalDuration: totalTime,
      tests: Array.from(testPerformance.entries()).map(([name, data]) => ({
        name,
        ...data
      }))
    };

    const fs = require('fs');
    const path = require('path');
    const outputDir = path.join(process.cwd(), '.test-baseline');

    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    fs.writeFileSync(
      path.join(outputDir, 'mocha-performance.json'),
      JSON.stringify(performanceReport, null, 2)
    );
  }
};

// Custom assertion extensions
const { expect } = require('chai');

// Add baseline comparison assertion
expect.extend({
  toMatchBaseline(received, baseline, tolerance = 0.1) {
    if (!baseline) {
      return {
        pass: true,
        message: () => 'No baseline provided for comparison'
      };
    }

    const diff = Math.abs(received - baseline);
    const percentDiff = (diff / baseline) * 100;
    const pass = percentDiff <= tolerance * 100;

    return {
      pass,
      message: () =>
        pass
          ? \`Expected \${received} to differ from baseline \${baseline} by more than \${tolerance * 100}%\`
          : \`Expected \${received} to be within \${tolerance * 100}% of baseline \${baseline}, but was \${percentDiff.toFixed(2)}% different\`
    };
  }
});
`;

    await fs.writeFile(hooksPath, hooksCode, 'utf8');
    return hooksPath;
  }

  async _executeTests(options) {
    return new Promise(async (resolve, reject) => {
      try {
        const args = await this._buildMochaArgs(options);

        this.emit('testStarted', { command: `${this.mochaPath} ${args.join(' ')}` });

        // Use nyc for coverage if enabled
        let command = this.mochaPath;
        let commandArgs = args;

        if (this.options.coverage && this.coverageCommand) {
          command = this.coverageCommand;
          commandArgs = this._buildCoverageArgs().concat(['--', this.mochaPath]).concat(args);
        }

        this.runnerProcess = spawn(command, commandArgs, {
          cwd: this.options.rootDir,
          stdio: ['pipe', 'pipe', 'pipe'],
          env: { ...process.env, NODE_OPTIONS: '--expose-gc' }
        });

        let stdout = '';
        let stderr = '';

        this.runnerProcess.stdout.on('data', (data) => {
          const output = data.toString();
          stdout += output;
          this.emit('testOutput', { type: 'stdout', data: output });
        });

        this.runnerProcess.stderr.on('data', (data) => {
          const output = data.toString();
          stderr += output;
          this.emit('testOutput', { type: 'stderr', data: output });
        });

        this.runnerProcess.on('close', async (code) => {
          try {
            const results = await this._parseResults(code, stdout, stderr);
            resolve(results);
          } catch (error) {
            reject(error);
          }
        });

        this.runnerProcess.on('error', (error) => {
          reject(error);
        });
      } catch (error) {
        reject(error);
      }
    });
  }

  async _buildMochaArgs(options) {
    const args = [];

    // Add hooks file
    const hooksFile = await this._setupHooksFile();
    args.push('--require', hooksFile);

    // Custom reporter
    if (this.customReporter) {
      args.push('--reporter', this.customReporter);
      if (this.reporterOptions) {
        args.push('--reporter-options',
          Object.entries(this.reporterOptions)
            .map(([key, value]) => `${key}=${value}`)
            .join(',')
        );
      }
    }

    // Profiling options
    if (this.options.profiling) {
      args.push('--reporter', 'json');
      args.push('--no-timeouts');
    }

    // General options
    if (options.watch) args.push('--watch');
    if (options.bail) args.push('--bail');
    if (options.grep) args.push('--grep', options.grep);
    if (options.timeout) args.push('--timeout', options.timeout.toString());
    if (options.retries) args.push('--retries', options.retries.toString());
    if (options.recursive) args.push('--recursive');

    // Test files pattern
    if (options.testPattern) {
      args.push(options.testPattern);
    } else {
      // Default test patterns
      args.push('test/**/*.js');
    }

    return args;
  }

  _buildCoverageArgs() {
    const args = [];

    if (this.coverageOptions) {
      Object.entries(this.coverageOptions).forEach(([key, value]) => {
        if (Array.isArray(value)) {
          value.forEach(item => args.push(`--${key}`, item));
        } else {
          args.push(`--${key}`, value.toString());
        }
      });
    }

    return args;
  }

  async _parseResults(exitCode, stdout, stderr) {
    try {
      let mochaResults = {};
      let tests = [];

      // Try to parse JSON output if available
      try {
        const jsonMatch = stdout.match(/(\{[\s\S]*\})/);
        if (jsonMatch) {
          mochaResults = JSON.parse(jsonMatch[1]);
          tests = this._transformMochaResults(mochaResults);
        }
      } catch {
        // Fallback to parsing text output
        tests = this._parseTextOutput(stdout);
      }

      // Load performance data
      const performanceData = await this._loadPerformanceData();

      // Merge performance data with tests
      if (performanceData?.tests) {
        const perfMap = new Map(performanceData.tests.map(t => [t.name, t]));
        tests.forEach(test => {
          const perfData = perfMap.get(test.name);
          if (perfData) {
            test.duration = perfData.duration;
            test.memory = perfData.memory;
          }
        });
      }

      const summary = this._calculateSummary(tests);

      // Load coverage if available
      let coverage = null;
      if (this.options.coverage) {
        coverage = await this._loadCoverageReport();
      }

      return {
        tests,
        summary: {
          ...summary,
          exitCode,
          performance: performanceData ? {
            totalDuration: performanceData.totalDuration,
            avgTestDuration: performanceData.tests ?
              performanceData.tests.reduce((sum, t) => sum + t.duration, 0) / performanceData.tests.length : 0
          } : null
        },
        coverage,
        profiling: performanceData,
        raw: {
          stdout,
          stderr,
          mochaResults
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse Mocha results: ${error.message}`);
    }
  }

  _transformMochaResults(mochaResults) {
    const tests = [];

    function processTests(testArray, suitePath = '') {
      for (const test of testArray) {
        if (test.tests) {
          // This is a suite
          processTests(test.tests, suitePath ? `${suitePath} > ${test.title}` : test.title);
        } else {
          // This is a test
          tests.push({
            name: test.fullTitle || test.title,
            suite: suitePath,
            status: test.state === 'passed' ? 'passed' :
                   test.state === 'failed' ? 'failed' : 'skipped',
            duration: test.duration || 0,
            error: test.err?.message || null,
            file: test.file || null,
            line: null
          });
        }
      }
    }

    if (mochaResults.tests) {
      processTests(mochaResults.tests);
    }

    return tests;
  }

  _parseTextOutput(stdout) {
    const tests = [];
    const lines = stdout.split('\n');

    let currentSuite = '';
    let testPattern = /^\s*(✓|×|\d+\))\s*(.*?)(?:\s+\((\d+)ms\))?$/;

    for (const line of lines) {
      const match = line.match(testPattern);
      if (match) {
        const [, status, name, duration] = match;
        tests.push({
          name: name.trim(),
          suite: currentSuite,
          status: status === '✓' ? 'passed' : 'failed',
          duration: duration ? parseInt(duration) : 0,
          error: null,
          file: null,
          line: null
        });
      } else if (line.trim() && !line.includes('passing') && !line.includes('failing')) {
        // Might be a suite name
        const suiteMatch = line.match(/^\s*([^✓×\d].*)$/);
        if (suiteMatch) {
          currentSuite = suiteMatch[1].trim();
        }
      }
    }

    return tests;
  }

  async _loadPerformanceData() {
    try {
      const perfPath = path.join(this.options.rootDir, '.test-baseline/mocha-performance.json');
      return await this._readJson(perfPath);
    } catch {
      return null;
    }
  }

  async _loadCoverageReport() {
    try {
      const coveragePath = path.join(
        this.options.rootDir,
        '.test-baseline/coverage/coverage-final.json'
      );
      const coverageData = await this._readJson(coveragePath);

      if (!coverageData) return null;

      // Calculate totals similar to Jest adapter
      let totalStatements = 0;
      let coveredStatements = 0;
      let totalBranches = 0;
      let coveredBranches = 0;
      let totalFunctions = 0;
      let coveredFunctions = 0;
      let totalLines = 0;
      let coveredLines = 0;

      for (const [, file] of Object.entries(coverageData)) {
        if (file.s) {
          totalStatements += Object.keys(file.s).length;
          coveredStatements += Object.values(file.s).filter(x => x > 0).length;
        }

        if (file.b) {
          totalBranches += Object.keys(file.b).length;
          coveredBranches += Object.values(file.b).filter(branches =>
            branches.some(x => x > 0)).length;
        }

        if (file.f) {
          totalFunctions += Object.keys(file.f).length;
          coveredFunctions += Object.values(file.f).filter(x => x > 0).length;
        }
      }

      return {
        statements: {
          total: totalStatements,
          covered: coveredStatements,
          percentage: totalStatements > 0 ? (coveredStatements / totalStatements) * 100 : 0
        },
        branches: {
          total: totalBranches,
          covered: coveredBranches,
          percentage: totalBranches > 0 ? (coveredBranches / totalBranches) * 100 : 0
        },
        functions: {
          total: totalFunctions,
          covered: coveredFunctions,
          percentage: totalFunctions > 0 ? (coveredFunctions / totalFunctions) * 100 : 0
        },
        lines: {
          total: totalLines,
          covered: coveredLines,
          percentage: totalLines > 0 ? (coveredLines / totalLines) * 100 : 0
        },
        total: totalStatements > 0 ? (coveredStatements / totalStatements) * 100 : 0
      };
    } catch {
      return null;
    }
  }

  async _stopExecution() {
    if (this.runnerProcess) {
      this.runnerProcess.kill('SIGTERM');
      this.runnerProcess = null;
    }
  }

  async _createBaselineReporter(reporterPath) {
    const reporterCode = `
const Mocha = require('mocha');
const fs = require('fs');
const path = require('path');

const {
  EVENT_RUN_BEGIN,
  EVENT_RUN_END,
  EVENT_TEST_FAIL,
  EVENT_TEST_PASS,
  EVENT_SUITE_BEGIN,
  EVENT_SUITE_END
} = Mocha.Runner.constants;

class BaselineReporter {
  constructor(runner, options) {
    this.runner = runner;
    this.options = options.reporterOptions || {};
    this.tests = [];
    this.suites = [];

    runner
      .once(EVENT_RUN_BEGIN, () => {
        console.log('🚀 Starting Mocha test run with baseline tracking');
      })
      .on(EVENT_SUITE_BEGIN, (suite) => {
        if (suite.title) {
          this.suites.push(suite.title);
        }
      })
      .on(EVENT_SUITE_END, () => {
        this.suites.pop();
      })
      .on(EVENT_TEST_PASS, (test) => {
        this.tests.push({
          name: test.fullTitle(),
          suite: this.suites.join(' > '),
          status: 'passed',
          duration: test.duration,
          error: null
        });
      })
      .on(EVENT_TEST_FAIL, (test, err) => {
        this.tests.push({
          name: test.fullTitle(),
          suite: this.suites.join(' > '),
          status: 'failed',
          duration: test.duration,
          error: err.message
        });
      })
      .once(EVENT_RUN_END, () => {
        this.writeReport();
      });
  }

  writeReport() {
    const outputFile = this.options.outputFile;
    if (!outputFile) return;

    const outputDir = path.dirname(outputFile);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const reportData = {
      timestamp: new Date().toISOString(),
      summary: {
        total: this.tests.length,
        passed: this.tests.filter(t => t.status === 'passed').length,
        failed: this.tests.filter(t => t.status === 'failed').length,
        duration: this.tests.reduce((sum, t) => sum + (t.duration || 0), 0)
      },
      tests: this.tests,
      baseline: this.options.baseline
    };

    fs.writeFileSync(outputFile, JSON.stringify(reportData, null, 2));
    console.log(\`📊 Test report written to \${outputFile}\`);
  }
}

module.exports = BaselineReporter;
`;

    await fs.writeFile(reporterPath, reporterCode, 'utf8');
  }
}

module.exports = MochaAdapter;