/**
 * Pytest Test Framework Adapter
 *
 * Provides Pytest-specific implementation with plugin integration,
 * coverage collection, and performance profiling for Python projects.
 */

const BaseTestAdapter = require('../base-adapter');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;

class PytestAdapter extends BaseTestAdapter {
  constructor(options = {}) {
    super(options);
    this.framework = 'pytest';
    this.pytestPath = null;
    this.config = null;
    this.runnerProcess = null;
    this.pythonPath = 'python';
  }

  async _detectFramework() {
    try {
      // Check for pytest in requirements files
      const reqFiles = ['requirements.txt', 'requirements-dev.txt', 'pyproject.toml', 'setup.py'];

      for (const reqFile of reqFiles) {
        const reqPath = path.join(this.options.rootDir, reqFile);
        if (await this._fileExists(reqPath)) {
          const content = await fs.readFile(reqPath, 'utf8');
          if (content.includes('pytest')) {
            this.pytestPath = 'pytest';
            return true;
          }
        }
      }

      // Check if pytest is available globally
      return new Promise((resolve) => {
        const proc = spawn('pytest', ['--version'], { stdio: 'pipe' });
        proc.on('close', (code) => {
          if (code === 0) {
            this.pytestPath = 'pytest';
            resolve(true);
          } else {
            resolve(false);
          }
        });
        proc.on('error', () => resolve(false));
      });
    } catch {
      return false;
    }
  }

  async _findConfig() {
    const configFiles = [
      'pytest.ini',
      'pyproject.toml',
      'tox.ini',
      'setup.cfg'
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
    return new Promise((resolve) => {
      const proc = spawn('pytest', ['--version'], { stdio: 'pipe' });
      let output = '';

      proc.stdout.on('data', (data) => {
        output += data.toString();
      });

      proc.on('close', () => {
        const match = output.match(/pytest (\d+\.\d+\.\d+)/);
        resolve(match ? match[1] : 'unknown');
      });

      proc.on('error', () => resolve('unknown'));
    });
  }

  async _loadConfig() {
    if (this.configPath) {
      if (this.configPath.endsWith('pyproject.toml')) {
        const content = await fs.readFile(this.configPath, 'utf8');
        // Basic TOML parsing for pytest config
        const pytest = this._parseTomlPytestConfig(content);
        this.config = pytest || {};
      } else if (this.configPath.endsWith('.ini') || this.configPath.endsWith('.cfg')) {
        const content = await fs.readFile(this.configPath, 'utf8');
        this.config = this._parseIniPytestConfig(content);
      }
    } else {
      this.config = {};
    }
  }

  async _setupReporters() {
    // Create custom pytest plugin for baseline integration
    const pluginPath = path.join(__dirname, 'pytest_baseline_plugin.py');
    await this._createBaselinePlugin(pluginPath);

    this.customPlugin = pluginPath;
    this.reporterOptions = {
      outputFile: path.join(this.options.rootDir, '.test-baseline/pytest-results.json'),
      baseline: this.options.baseline
    };
  }

  async _setupCoverage() {
    if (this.options.coverage) {
      this.coverageOptions = {
        plugin: 'pytest-cov',
        source: ['src', 'lib'],
        reportDir: path.join(this.options.rootDir, '.test-baseline/coverage'),
        formats: ['json', 'html', 'term']
      };
    }
  }

  async _setupProfiling() {
    if (this.options.profiling) {
      this.profilingOptions = {
        plugin: 'pytest-benchmark',
        outputDir: path.join(this.options.rootDir, '.test-baseline/profiling')
      };
    }
  }

  _getTestPatterns() {
    return [
      'test_*.py',
      '*_test.py',
      'tests/**/*.py',
      'test/**/*.py'
    ];
  }

  async _executeTests(options) {
    return new Promise((resolve, reject) => {
      const args = this._buildPytestArgs(options);

      this.emit('testStarted', { command: `${this.pytestPath} ${args.join(' ')}` });

      this.runnerProcess = spawn(this.pytestPath, args, {
        cwd: this.options.rootDir,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, PYTHONPATH: this.options.rootDir }
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

  _buildPytestArgs(options) {
    const args = [];

    // Add custom plugin
    if (this.customPlugin) {
      args.push('-p', `no:cacheprovider`);
      args.push('--tb=short');
      args.push('-v');
    }

    // JSON output for parsing
    args.push('--json-report');
    args.push(`--json-report-file=${path.join(this.options.rootDir, '.test-baseline/pytest-report.json')}`);

    // Coverage options
    if (this.options.coverage && this.coverageOptions) {
      args.push('--cov=' + this.coverageOptions.source.join(','));
      args.push('--cov-report=json');
      args.push(`--cov-report=html:${this.coverageOptions.reportDir}/html`);
      args.push('--cov-report=term');
    }

    // Profiling options
    if (this.options.profiling && this.profilingOptions) {
      args.push('--benchmark-json=' + path.join(this.profilingOptions.outputDir, 'benchmark.json'));
      args.push('--benchmark-only');
    }

    // General options
    if (options.verbose) args.push('-v');
    if (options.quiet) args.push('-q');
    if (options.bail) args.push('-x');
    if (options.failfast) args.push('--ff');
    if (options.maxfail) args.push('--maxfail', options.maxfail.toString());
    if (options.timeout) args.push('--timeout', options.timeout.toString());
    if (options.workers) args.push('-n', options.workers.toString());

    // Test selection
    if (options.keyword) args.push('-k', options.keyword);
    if (options.markers) args.push('-m', options.markers);
    if (options.testPathPattern) args.push(options.testPathPattern);

    // Disable warnings if not in verbose mode
    if (!options.verbose) {
      args.push('--disable-warnings');
    }

    return args;
  }

  async _parseResults(exitCode, stdout, stderr) {
    try {
      // Load JSON report
      const reportPath = path.join(this.options.rootDir, '.test-baseline/pytest-report.json');
      const jsonReport = await this._readJson(reportPath);

      let tests = [];
      if (jsonReport) {
        tests = this._transformPytestResults(jsonReport);
      } else {
        // Fallback to parsing text output
        tests = this._parseTextOutput(stdout);
      }

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
          pytest: jsonReport?.summary || {}
        },
        coverage,
        profiling,
        raw: {
          stdout,
          stderr,
          jsonReport
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse Pytest results: ${error.message}`);
    }
  }

  _transformPytestResults(jsonReport) {
    const tests = [];

    if (jsonReport.tests) {
      for (const test of jsonReport.tests) {
        tests.push({
          name: test.nodeid,
          suite: this._extractSuiteName(test.nodeid),
          status: test.outcome === 'passed' ? 'passed' :
                 test.outcome === 'failed' ? 'failed' : 'skipped',
          duration: (test.duration || 0) * 1000, // Convert to milliseconds
          error: test.call?.longrepr || test.setup?.longrepr || test.teardown?.longrepr || null,
          file: test.nodeid.split('::')[0],
          line: test.lineno || null
        });
      }
    }

    return tests;
  }

  _extractSuiteName(nodeid) {
    // Extract class/module name from pytest nodeid
    const parts = nodeid.split('::');
    if (parts.length > 2) {
      return parts.slice(0, -1).join('::');
    } else if (parts.length === 2) {
      return parts[0];
    }
    return '';
  }

  _parseTextOutput(stdout) {
    const tests = [];
    const lines = stdout.split('\n');

    for (const line of lines) {
      // Parse pytest verbose output
      const testMatch = line.match(/^(.+?::.*?)\s+(PASSED|FAILED|SKIPPED|ERROR)/);
      if (testMatch) {
        const [, name, status] = testMatch;
        tests.push({
          name: name.trim(),
          suite: this._extractSuiteName(name),
          status: status.toLowerCase() === 'passed' ? 'passed' :
                 status.toLowerCase() === 'failed' ? 'failed' : 'skipped',
          duration: 0,
          error: null,
          file: name.split('::')[0],
          line: null
        });
      }
    }

    return tests;
  }

  async _loadCoverageReport() {
    try {
      const coveragePath = path.join(this.options.rootDir, 'coverage.json');
      const coverageData = await this._readJson(coveragePath);

      if (!coverageData || !coverageData.totals) return null;

      const totals = coverageData.totals;

      return {
        statements: {
          total: totals.num_statements || 0,
          covered: totals.covered_lines || 0,
          percentage: totals.percent_covered || 0
        },
        branches: {
          total: totals.num_branches || 0,
          covered: totals.covered_branches || 0,
          percentage: totals.percent_covered_display ?
            parseFloat(totals.percent_covered_display) : 0
        },
        functions: {
          total: 0, // Pytest coverage doesn't track functions separately
          covered: 0,
          percentage: 0
        },
        lines: {
          total: totals.num_statements || 0,
          covered: totals.covered_lines || 0,
          percentage: totals.percent_covered || 0
        },
        total: totals.percent_covered || 0,
        files: coverageData.files ? Object.keys(coverageData.files).length : 0
      };
    } catch {
      return null;
    }
  }

  async _loadProfilingReport() {
    try {
      const profilingPath = path.join(
        this.profilingOptions.outputDir,
        'benchmark.json'
      );
      const profilingData = await this._readJson(profilingPath);

      if (!profilingData || !profilingData.benchmarks) return null;

      return {
        benchmarks: profilingData.benchmarks.map(benchmark => ({
          name: benchmark.name,
          group: benchmark.group,
          stats: {
            min: benchmark.stats.min,
            max: benchmark.stats.max,
            mean: benchmark.stats.mean,
            stddev: benchmark.stats.stddev,
            median: benchmark.stats.median,
            iqr: benchmark.stats.iqr,
            q1: benchmark.stats.q1,
            q3: benchmark.stats.q3
          },
          params: benchmark.params
        })),
        machine: profilingData.machine_info,
        commit: profilingData.commit_info
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

  // Helper methods for config parsing
  _parseTomlPytestConfig(content) {
    try {
      // Simple TOML parsing for pytest section
      const pytestMatch = content.match(/\[tool\.pytest\.ini_options\]([\s\S]*?)(?=\[|$)/);
      if (pytestMatch) {
        const configSection = pytestMatch[1];
        const config = {};

        const lines = configSection.split('\n');
        for (const line of lines) {
          const match = line.match(/^\s*(\w+)\s*=\s*(.+)$/);
          if (match) {
            config[match[1]] = match[2].replace(/['"]/g, '');
          }
        }

        return config;
      }
    } catch {
      // Ignore parsing errors
    }
    return {};
  }

  _parseIniPytestConfig(content) {
    try {
      const config = {};
      const lines = content.split('\n');
      let inPytestSection = false;

      for (const line of lines) {
        if (line.trim() === '[pytest]' || line.trim() === '[tool:pytest]') {
          inPytestSection = true;
          continue;
        }

        if (line.startsWith('[') && line.endsWith(']')) {
          inPytestSection = false;
          continue;
        }

        if (inPytestSection) {
          const match = line.match(/^\s*(\w+)\s*=\s*(.+)$/);
          if (match) {
            config[match[1]] = match[2].trim();
          }
        }
      }

      return config;
    } catch {
      return {};
    }
  }

  async _createBaselinePlugin(pluginPath) {
    const pluginCode = `
"""
Pytest plugin for baseline test tracking and performance monitoring.
"""
import json
import time
import os
from pathlib import Path
import pytest

class BaselineCollector:
    def __init__(self):
        self.tests = []
        self.start_time = None
        self.baseline = None

    def pytest_configure(self, config):
        self.output_file = config.getoption("--baseline-output",
                                           ".test-baseline/pytest-baseline.json")
        # Create output directory
        Path(self.output_file).parent.mkdir(parents=True, exist_ok=True)

    def pytest_runtest_setup(self, item):
        item.baseline_start_time = time.time()

    def pytest_runtest_call(self, item):
        pass

    def pytest_runtest_teardown(self, item):
        pass

    def pytest_runtest_logreport(self, report):
        if report.when == 'call':
            duration = getattr(report, 'duration', 0) * 1000  # Convert to ms

            test_data = {
                'name': report.nodeid,
                'status': 'passed' if report.passed else 'failed' if report.failed else 'skipped',
                'duration': duration,
                'suite': self._extract_suite_name(report.nodeid),
                'file': report.fspath.strpath if hasattr(report, 'fspath') else None,
                'line': report.lineno if hasattr(report, 'lineno') else None,
                'error': str(report.longrepr) if report.failed and report.longrepr else None
            }

            self.tests.append(test_data)

    def pytest_sessionfinish(self, session, exitstatus):
        """Write baseline report at the end of test session."""
        report_data = {
            'timestamp': time.time(),
            'summary': {
                'total': len(self.tests),
                'passed': len([t for t in self.tests if t['status'] == 'passed']),
                'failed': len([t for t in self.tests if t['status'] == 'failed']),
                'skipped': len([t for t in self.tests if t['status'] == 'skipped']),
                'duration': sum(t['duration'] for t in self.tests),
                'exitCode': exitstatus
            },
            'tests': self.tests,
            'baseline': self.baseline
        }

        with open(self.output_file, 'w') as f:
            json.dump(report_data, f, indent=2)

    def _extract_suite_name(self, nodeid):
        """Extract suite name from pytest nodeid."""
        parts = nodeid.split('::')
        if len(parts) > 2:
            return '::'.join(parts[:-1])
        elif len(parts) == 2:
            return parts[0]
        return ''

def pytest_addoption(parser):
    """Add command line options for baseline tracking."""
    parser.addoption(
        "--baseline-output",
        action="store",
        default=".test-baseline/pytest-baseline.json",
        help="Output file for baseline test results"
    )
    parser.addoption(
        "--baseline-compare",
        action="store",
        help="Path to baseline file for comparison"
    )

def pytest_configure(config):
    """Configure the baseline collector plugin."""
    if not hasattr(config, '_baseline_collector'):
        config._baseline_collector = BaselineCollector()
        config.pluginmanager.register(config._baseline_collector, 'baseline_collector')

@pytest.fixture
def baseline_compare():
    """Fixture to compare test results with baseline."""
    def compare_with_baseline(current_value, baseline_value, tolerance=0.1):
        if baseline_value is None:
            return True

        diff = abs(current_value - baseline_value)
        percent_diff = (diff / baseline_value) * 100 if baseline_value != 0 else 0

        return percent_diff <= tolerance * 100

    return compare_with_baseline

@pytest.fixture
def performance_monitor():
    """Fixture for monitoring test performance."""
    class PerformanceMonitor:
        def __init__(self):
            self.start_time = None
            self.memory_start = None

        def start(self):
            import psutil
            import time
            self.start_time = time.time()
            process = psutil.Process()
            self.memory_start = process.memory_info().rss

        def stop(self):
            import psutil
            import time
            end_time = time.time()
            process = psutil.Process()
            memory_end = process.memory_info().rss

            return {
                'duration': (end_time - self.start_time) * 1000,
                'memory_delta': memory_end - self.memory_start
            }

    return PerformanceMonitor()
`;

    await fs.writeFile(pluginPath, pluginCode, 'utf8');
  }
}

module.exports = PytestAdapter;