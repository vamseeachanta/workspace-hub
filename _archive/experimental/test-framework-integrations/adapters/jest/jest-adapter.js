/**
 * Jest Test Framework Adapter
 *
 * Provides Jest-specific implementation with custom reporter integration,
 * coverage collection, and performance profiling.
 */

const BaseTestAdapter = require('../base-adapter');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;

class JestAdapter extends BaseTestAdapter {
  constructor(options = {}) {
    super(options);
    this.framework = 'jest';
    this.jestPath = null;
    this.config = null;
    this.runnerProcess = null;
  }

  async _detectFramework() {
    try {
      // Check for Jest in package.json
      const packageJson = await this._readJson(path.join(this.options.rootDir, 'package.json'));
      if (packageJson?.dependencies?.jest || packageJson?.devDependencies?.jest) {
        this.jestPath = path.join(this.options.rootDir, 'node_modules/.bin/jest');
        return await this._fileExists(this.jestPath);
      }

      // Check for global Jest
      try {
        require.resolve('jest');
        this.jestPath = 'jest';
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
      'jest.config.js',
      'jest.config.ts',
      'jest.config.mjs',
      'jest.config.json',
      'jest.json'
    ];

    for (const configFile of configFiles) {
      const configPath = path.join(this.options.rootDir, configFile);
      if (await this._fileExists(configPath)) {
        return configPath;
      }
    }

    // Check package.json for jest config
    const packageJsonPath = path.join(this.options.rootDir, 'package.json');
    const packageJson = await this._readJson(packageJsonPath);
    if (packageJson?.jest) {
      return packageJsonPath;
    }

    return null;
  }

  async _getVersion() {
    try {
      const packageJson = await this._readJson(
        path.join(this.options.rootDir, 'node_modules/jest/package.json')
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
        this.config = packageJson.jest || {};
      } else {
        // For JS/TS configs, we'll load them dynamically
        this.config = {};
      }
    } else {
      this.config = {};
    }
  }

  async _setupReporters() {
    // Create custom reporter for baseline integration
    const reporterPath = path.join(__dirname, 'jest-baseline-reporter.js');
    await this._createBaselineReporter(reporterPath);

    this.customReporters = [
      ['default'],
      [reporterPath, {
        outputFile: path.join(this.options.rootDir, '.test-baseline/jest-results.json'),
        baseline: this.options.baseline
      }]
    ];
  }

  async _setupCoverage() {
    if (this.options.coverage) {
      this.coverageOptions = {
        collectCoverage: true,
        coverageDirectory: path.join(this.options.rootDir, '.test-baseline/coverage'),
        coverageReporters: ['json', 'text', 'html'],
        collectCoverageFrom: [
          'src/**/*.{js,jsx,ts,tsx}',
          '!src/**/*.test.{js,jsx,ts,tsx}',
          '!src/**/*.spec.{js,jsx,ts,tsx}'
        ]
      };
    }
  }

  async _setupProfiling() {
    if (this.options.profiling) {
      this.profilingOptions = {
        verbose: true,
        detectOpenHandles: true,
        detectLeaks: true,
        logHeapUsage: true
      };
    }
  }

  _getTestPatterns() {
    return [
      '**/__tests__/**/*.(js|jsx|ts|tsx)',
      '**/*.(test|spec).(js|jsx|ts|tsx)',
      '**/test/**/*.(js|jsx|ts|tsx)'
    ];
  }

  async _executeTests(options) {
    return new Promise((resolve, reject) => {
      const args = this._buildJestArgs(options);

      this.emit('testStarted', { command: `${this.jestPath} ${args.join(' ')}` });

      this.runnerProcess = spawn(this.jestPath, args, {
        cwd: this.options.rootDir,
        stdio: ['pipe', 'pipe', 'pipe']
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
    });
  }

  _buildJestArgs(options) {
    const args = [];

    // Add custom reporters
    if (this.customReporters) {
      for (const reporter of this.customReporters) {
        if (Array.isArray(reporter)) {
          args.push('--reporters', reporter[0]);
          if (reporter[1]) {
            args.push('--reporterOptions', JSON.stringify(reporter[1]));
          }
        } else {
          args.push('--reporters', reporter);
        }
      }
    }

    // Coverage options
    if (this.options.coverage && this.coverageOptions) {
      Object.entries(this.coverageOptions).forEach(([key, value]) => {
        if (typeof value === 'boolean' && value) {
          args.push(`--${key}`);
        } else if (typeof value === 'string') {
          args.push(`--${key}`, value);
        } else if (Array.isArray(value)) {
          value.forEach(item => args.push(`--${key}`, item));
        }
      });
    }

    // Profiling options
    if (this.options.profiling && this.profilingOptions) {
      Object.entries(this.profilingOptions).forEach(([key, value]) => {
        if (typeof value === 'boolean' && value) {
          args.push(`--${key}`);
        }
      });
    }

    // General options
    if (options.watch) args.push('--watch');
    if (options.watchAll) args.push('--watchAll');
    if (options.bail) args.push('--bail');
    if (options.verbose) args.push('--verbose');
    if (options.silent) args.push('--silent');
    if (options.maxWorkers) args.push('--maxWorkers', options.maxWorkers.toString());
    if (options.testTimeout) args.push('--testTimeout', options.testTimeout.toString());

    // Test pattern
    if (options.testNamePattern) {
      args.push('--testNamePattern', options.testNamePattern);
    }

    // File patterns
    if (options.testPathPattern) {
      args.push(options.testPathPattern);
    }

    // JSON output for result parsing
    args.push('--json');

    return args;
  }

  async _parseResults(exitCode, stdout, stderr) {
    try {
      // Parse JSON output from Jest
      const jsonMatch = stdout.match(/^({.*})$/m);
      let jestResults = {};

      if (jsonMatch) {
        jestResults = JSON.parse(jsonMatch[1]);
      }

      // Transform Jest results to our standard format
      const tests = this._transformTestResults(jestResults.testResults || []);
      const summary = this._calculateSummary(tests);

      // Load coverage if available
      let coverage = null;
      if (this.options.coverage) {
        coverage = await this._loadCoverageReport();
      }

      // Load profiling if available
      let profiling = null;
      if (this.options.profiling) {
        profiling = this._extractProfilingData(stdout, stderr);
      }

      return {
        tests,
        summary: {
          ...summary,
          exitCode,
          jestResults: jestResults.numTotalTestSuites ? {
            testSuites: {
              total: jestResults.numTotalTestSuites,
              passed: jestResults.numPassedTestSuites,
              failed: jestResults.numFailedTestSuites
            }
          } : {}
        },
        coverage,
        profiling,
        raw: {
          stdout,
          stderr,
          jestResults
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse Jest results: ${error.message}`);
    }
  }

  _transformTestResults(testResults) {
    const tests = [];

    for (const suite of testResults) {
      for (const test of suite.assertionResults || []) {
        tests.push({
          name: test.fullName || test.title,
          suite: suite.testFilePath,
          status: test.status,
          duration: test.duration || 0,
          error: test.failureMessages?.join('\n') || null,
          file: suite.testFilePath,
          line: test.location?.line || null
        });
      }
    }

    return tests;
  }

  async _loadCoverageReport() {
    try {
      const coveragePath = path.join(
        this.options.rootDir,
        '.test-baseline/coverage/coverage-final.json'
      );
      const coverageData = await this._readJson(coveragePath);

      if (!coverageData) return null;

      // Calculate totals
      let totalStatements = 0;
      let coveredStatements = 0;
      let totalBranches = 0;
      let coveredBranches = 0;
      let totalFunctions = 0;
      let coveredFunctions = 0;
      let totalLines = 0;
      let coveredLines = 0;

      for (const file of Object.values(coverageData)) {
        totalStatements += file.s ? Object.keys(file.s).length : 0;
        coveredStatements += file.s ? Object.values(file.s).filter(x => x > 0).length : 0;

        totalBranches += file.b ? Object.keys(file.b).length : 0;
        coveredBranches += file.b ? Object.values(file.b).filter(branches =>
          branches.some(x => x > 0)).length : 0;

        totalFunctions += file.f ? Object.keys(file.f).length : 0;
        coveredFunctions += file.f ? Object.values(file.f).filter(x => x > 0).length : 0;
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

  _extractProfilingData(stdout, stderr) {
    const profiling = {
      memoryUsage: [],
      openHandles: [],
      leaks: []
    };

    // Extract heap usage information
    const heapMatches = stdout.match(/Heap size: (\d+)/g);
    if (heapMatches) {
      profiling.memoryUsage = heapMatches.map(match => {
        const size = parseInt(match.match(/\d+/)[0]);
        return { timestamp: Date.now(), heapSize: size };
      });
    }

    // Extract open handles warnings
    const handleMatches = stderr.match(/Jest did not exit one second after.*?\n(.*?)\n/gs);
    if (handleMatches) {
      profiling.openHandles = handleMatches.map(match => match.trim());
    }

    // Extract memory leak warnings
    const leakMatches = stderr.match(/Possible memory leak detected/g);
    if (leakMatches) {
      profiling.leaks = leakMatches.map(() => ({ detected: true, timestamp: Date.now() }));
    }

    return profiling;
  }

  async _stopExecution() {
    if (this.runnerProcess) {
      this.runnerProcess.kill('SIGTERM');
      this.runnerProcess = null;
    }
  }

  async _createBaselineReporter(reporterPath) {
    const reporterCode = `
const fs = require('fs');
const path = require('path');

class BaselineReporter {
  constructor(globalConfig, options) {
    this.globalConfig = globalConfig;
    this.options = options || {};
  }

  onRunComplete(contexts, results) {
    const outputDir = path.dirname(this.options.outputFile);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const reportData = {
      timestamp: new Date().toISOString(),
      summary: results,
      tests: this._extractTestDetails(results),
      baseline: this.options.baseline
    };

    fs.writeFileSync(
      this.options.outputFile,
      JSON.stringify(reportData, null, 2)
    );
  }

  _extractTestDetails(results) {
    const tests = [];

    for (const suite of results.testResults || []) {
      for (const test of suite.assertionResults || []) {
        tests.push({
          name: test.fullName,
          suite: suite.testFilePath,
          status: test.status,
          duration: test.duration,
          error: test.failureMessages?.join('\\n') || null
        });
      }
    }

    return tests;
  }
}

module.exports = BaselineReporter;
`;

    await fs.writeFile(reporterPath, reporterCode, 'utf8');
  }
}

module.exports = JestAdapter;