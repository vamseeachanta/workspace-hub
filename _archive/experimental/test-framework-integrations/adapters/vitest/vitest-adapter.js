/**
 * Vitest Test Framework Adapter
 *
 * Provides Vitest-specific implementation with modern testing features,
 * native ESM support, and built-in coverage integration.
 */

const BaseTestAdapter = require('../base-adapter');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;

class VitestAdapter extends BaseTestAdapter {
  constructor(options = {}) {
    super(options);
    this.framework = 'vitest';
    this.vitestPath = null;
    this.config = null;
    this.runnerProcess = null;
  }

  async _detectFramework() {
    try {
      // Check for Vitest in package.json
      const packageJson = await this._readJson(path.join(this.options.rootDir, 'package.json'));
      if (packageJson?.dependencies?.vitest || packageJson?.devDependencies?.vitest) {
        this.vitestPath = path.join(this.options.rootDir, 'node_modules/.bin/vitest');
        return await this._fileExists(this.vitestPath);
      }

      // Check for global Vitest
      try {
        require.resolve('vitest');
        this.vitestPath = 'vitest';
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
      'vitest.config.js',
      'vitest.config.ts',
      'vitest.config.mjs',
      'vite.config.js',
      'vite.config.ts',
      'vite.config.mjs'
    ];

    for (const configFile of configFiles) {
      const configPath = path.join(this.options.rootDir, configFile);
      if (await this._fileExists(configPath)) {
        return configPath;
      }
    }

    return null;
  }

  async _getVersion() {
    try {
      const packageJson = await this._readJson(
        path.join(this.options.rootDir, 'node_modules/vitest/package.json')
      );
      return packageJson?.version || 'unknown';
    } catch {
      return 'unknown';
    }
  }

  async _loadConfig() {
    if (this.configPath) {
      // For JS/TS configs, we'll rely on Vitest's config loading
      this.config = { configFile: this.configPath };
    } else {
      this.config = {};
    }
  }

  async _setupReporters() {
    // Create custom reporter for baseline integration
    const reporterPath = path.join(__dirname, 'vitest-baseline-reporter.js');
    await this._createBaselineReporter(reporterPath);

    this.customReporter = reporterPath;
    this.reporterOptions = {
      outputFile: path.join(this.options.rootDir, '.test-baseline/vitest-results.json'),
      baseline: this.options.baseline
    };
  }

  async _setupCoverage() {
    if (this.options.coverage) {
      // Vitest has built-in coverage via c8/v8
      this.coverageOptions = {
        provider: 'v8', // or 'c8', 'istanbul'
        reporter: ['json', 'text', 'html'],
        reportsDirectory: path.join(this.options.rootDir, '.test-baseline/coverage'),
        include: ['src/**/*'],
        exclude: [
          'src/**/*.test.{js,ts,jsx,tsx}',
          'src/**/*.spec.{js,ts,jsx,tsx}',
          'src/**/__tests__/**'
        ]
      };
    }
  }

  async _setupProfiling() {
    if (this.options.profiling) {
      this.profilingOptions = {
        benchmark: true,
        outputFile: path.join(this.options.rootDir, '.test-baseline/vitest-benchmark.json')
      };
    }
  }

  _getTestPatterns() {
    return [
      '**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}',
      '**/__tests__/**/*.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'
    ];
  }

  async _executeTests(options) {
    return new Promise((resolve, reject) => {
      const args = this._buildVitestArgs(options);

      this.emit('testStarted', { command: `${this.vitestPath} ${args.join(' ')}` });

      this.runnerProcess = spawn(this.vitestPath, args, {
        cwd: this.options.rootDir,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, NODE_ENV: 'test' }
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

  _buildVitestArgs(options) {
    const args = [];

    // Run mode (default to 'run' for CI)
    if (!options.watch) {
      args.push('run');
    }

    // Custom reporter
    if (this.customReporter) {
      args.push('--reporter', 'default');
      args.push('--reporter', this.customReporter);
    }

    // JSON output for parsing
    args.push('--reporter', 'json');
    args.push('--outputFile', path.join(this.options.rootDir, '.test-baseline/vitest-report.json'));

    // Coverage options
    if (this.options.coverage && this.coverageOptions) {
      args.push('--coverage.enabled');
      args.push('--coverage.provider', this.coverageOptions.provider);
      args.push('--coverage.reportsDirectory', this.coverageOptions.reportsDirectory);

      this.coverageOptions.reporter.forEach(reporter => {
        args.push('--coverage.reporter', reporter);
      });

      this.coverageOptions.include.forEach(pattern => {
        args.push('--coverage.include', pattern);
      });

      this.coverageOptions.exclude.forEach(pattern => {
        args.push('--coverage.exclude', pattern);
      });
    }

    // Profiling/Benchmark options
    if (this.options.profiling && this.profilingOptions) {
      args.push('--reporter', 'json');
      // Vitest benchmark mode would be handled separately
    }

    // General options
    if (options.watch) args.push('--watch');
    if (options.bail) args.push('--bail', '1');
    if (options.silent) args.push('--silent');
    if (options.verbose) args.push('--reporter', 'verbose');
    if (options.threads === false) args.push('--no-threads');
    if (options.minThreads) args.push('--minThreads', options.minThreads.toString());
    if (options.maxThreads) args.push('--maxThreads', options.maxThreads.toString());
    if (options.testTimeout) args.push('--testTimeout', options.testTimeout.toString());

    // Test filtering
    if (options.testNamePattern) args.push('--testNamePattern', options.testNamePattern);
    if (options.testPathPattern) args.push(options.testPathPattern);

    // Environment
    if (options.environment) args.push('--environment', options.environment);

    // Config file
    if (this.configPath) {
      args.push('--config', this.configPath);
    }

    return args;
  }

  async _parseResults(exitCode, stdout, stderr) {
    try {
      // Load JSON report
      const reportPath = path.join(this.options.rootDir, '.test-baseline/vitest-report.json');
      let vitestResults = {};

      try {
        vitestResults = await this._readJson(reportPath);
      } catch {
        // Fallback to parsing stdout for JSON
        const jsonMatch = stdout.match(/^(\{.*\})$/m);
        if (jsonMatch) {
          vitestResults = JSON.parse(jsonMatch[1]);
        }
      }

      const tests = this._transformVitestResults(vitestResults);
      const summary = this._calculateSummary(tests);

      // Load coverage if available
      let coverage = null;
      if (this.options.coverage) {
        coverage = await this._loadCoverageReport();
      }

      // Load profiling if available
      let profiling = null;
      if (this.options.profiling) {
        profiling = await this._loadProfilingReport();
      }

      return {
        tests,
        summary: {
          ...summary,
          exitCode,
          vitest: vitestResults.numTotalTestSuites ? {
            testSuites: {
              total: vitestResults.numTotalTestSuites,
              passed: vitestResults.numPassedTestSuites,
              failed: vitestResults.numFailedTestSuites
            },
            performance: vitestResults.testResults ? {
              avgDuration: this._calculateAverageDuration(vitestResults.testResults)
            } : null
          } : {}
        },
        coverage,
        profiling,
        raw: {
          stdout,
          stderr,
          vitestResults
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse Vitest results: ${error.message}`);
    }
  }

  _transformVitestResults(vitestResults) {
    const tests = [];

    if (vitestResults.testResults) {
      for (const suite of vitestResults.testResults) {
        if (suite.assertionResults) {
          for (const test of suite.assertionResults) {
            tests.push({
              name: test.fullName || test.title,
              suite: suite.name || path.basename(suite.testFilePath || ''),
              status: test.status,
              duration: test.duration || 0,
              error: test.failureMessages?.join('\n') || null,
              file: suite.testFilePath,
              line: test.location?.line || null
            });
          }
        }
      }
    }

    // Handle different Vitest result formats
    if (vitestResults.files) {
      for (const file of vitestResults.files) {
        if (file.tasks) {
          this._extractTestsFromTasks(file.tasks, tests, file.name);
        }
      }
    }

    return tests;
  }

  _extractTestsFromTasks(tasks, tests, suiteName, parentName = '') {
    for (const task of tasks) {
      const fullName = parentName ? `${parentName} ${task.name}` : task.name;

      if (task.type === 'test') {
        tests.push({
          name: fullName,
          suite: suiteName,
          status: task.result?.state || 'pending',
          duration: task.result?.duration || 0,
          error: task.result?.error?.message || null,
          file: suiteName,
          line: null
        });
      } else if (task.type === 'suite' && task.tasks) {
        this._extractTestsFromTasks(task.tasks, tests, suiteName, fullName);
      }
    }
  }

  _calculateAverageDuration(testResults) {
    let totalDuration = 0;
    let testCount = 0;

    for (const suite of testResults) {
      if (suite.assertionResults) {
        for (const test of suite.assertionResults) {
          totalDuration += test.duration || 0;
          testCount++;
        }
      }
    }

    return testCount > 0 ? totalDuration / testCount : 0;
  }

  async _loadCoverageReport() {
    try {
      const coveragePath = path.join(
        this.options.rootDir,
        '.test-baseline/coverage/coverage-final.json'
      );
      const coverageData = await this._readJson(coveragePath);

      if (!coverageData) return null;

      // Calculate totals from v8/c8 coverage format
      let totalStatements = 0;
      let coveredStatements = 0;
      let totalBranches = 0;
      let coveredBranches = 0;
      let totalFunctions = 0;
      let coveredFunctions = 0;
      let totalLines = 0;
      let coveredLines = 0;

      for (const [filePath, file] of Object.entries(coverageData)) {
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

        // For line coverage, use statementMap
        if (file.statementMap) {
          const lineNumbers = new Set();
          Object.values(file.statementMap).forEach(stmt => {
            if (stmt.start?.line) lineNumbers.add(stmt.start.line);
          });
          totalLines += lineNumbers.size;

          const coveredLineNumbers = new Set();
          Object.entries(file.s || {}).forEach(([stmtId, count]) => {
            if (count > 0 && file.statementMap[stmtId]?.start?.line) {
              coveredLineNumbers.add(file.statementMap[stmtId].start.line);
            }
          });
          coveredLines += coveredLineNumbers.size;
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

  async _loadProfilingReport() {
    try {
      const profilingPath = path.join(
        this.options.rootDir,
        '.test-baseline/vitest-benchmark.json'
      );
      const profilingData = await this._readJson(profilingPath);

      if (!profilingData) return null;

      return {
        benchmarks: profilingData.benchmarks || [],
        suites: profilingData.suites || [],
        totalTime: profilingData.totalTime || 0
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
const fs = require('fs');
const path = require('path');

class VitestBaselineReporter {
  onInit(ctx) {
    this.ctx = ctx;
    this.tests = [];
  }

  onTaskUpdate(packs) {
    // Extract test results from task updates
    for (const pack of packs) {
      for (const task of pack) {
        this.processTask(task);
      }
    }
  }

  onFinished(files, errors) {
    this.writeReport();
  }

  processTask(task) {
    if (task.type === 'test' && task.result) {
      this.tests.push({
        name: task.name,
        suite: task.suite?.name || task.file?.name || '',
        status: task.result.state,
        duration: task.result.duration || 0,
        error: task.result.error?.message || null,
        file: task.file?.filepath || null
      });
    } else if (task.tasks) {
      // Recursively process nested tasks
      for (const subtask of task.tasks) {
        this.processTask(subtask);
      }
    }
  }

  writeReport() {
    const outputFile = process.env.VITEST_BASELINE_OUTPUT ||
                      '.test-baseline/vitest-baseline.json';

    const outputDir = path.dirname(outputFile);
    if (!fs.existsSync(outputDir)) {
      fs.mkdirSync(outputDir, { recursive: true });
    }

    const reportData = {
      timestamp: new Date().toISOString(),
      summary: {
        total: this.tests.length,
        passed: this.tests.filter(t => t.status === 'pass').length,
        failed: this.tests.filter(t => t.status === 'fail').length,
        skipped: this.tests.filter(t => t.status === 'skip').length,
        duration: this.tests.reduce((sum, t) => sum + (t.duration || 0), 0)
      },
      tests: this.tests,
      baseline: process.env.VITEST_BASELINE_DATA ?
                JSON.parse(process.env.VITEST_BASELINE_DATA) : null
    };

    fs.writeFileSync(outputFile, JSON.stringify(reportData, null, 2));
    console.log(\`📊 Vitest baseline report written to \${outputFile}\`);
  }
}

module.exports = VitestBaselineReporter;
`;

    await fs.writeFile(reporterPath, reporterCode, 'utf8');
  }
}

module.exports = VitestAdapter;