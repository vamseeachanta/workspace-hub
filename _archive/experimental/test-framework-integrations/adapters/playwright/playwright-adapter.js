/**
 * Playwright Test Framework Adapter
 *
 * Provides Playwright-specific implementation for end-to-end testing
 * with browser automation, screenshot comparison, and performance monitoring.
 */

const BaseTestAdapter = require('../base-adapter');
const path = require('path');
const { spawn } = require('child_process');
const fs = require('fs').promises;

class PlaywrightAdapter extends BaseTestAdapter {
  constructor(options = {}) {
    super(options);
    this.framework = 'playwright';
    this.playwrightPath = null;
    this.config = null;
    this.runnerProcess = null;
    this.browsers = ['chromium', 'firefox', 'webkit'];
  }

  async _detectFramework() {
    try {
      // Check for Playwright in package.json
      const packageJson = await this._readJson(path.join(this.options.rootDir, 'package.json'));
      if (packageJson?.dependencies?.['@playwright/test'] ||
          packageJson?.devDependencies?.['@playwright/test']) {
        this.playwrightPath = path.join(this.options.rootDir, 'node_modules/.bin/playwright');
        return await this._fileExists(this.playwrightPath);
      }

      // Check for global Playwright
      try {
        require.resolve('@playwright/test');
        this.playwrightPath = 'playwright';
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
      'playwright.config.js',
      'playwright.config.ts',
      'playwright.config.mjs'
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
        path.join(this.options.rootDir, 'node_modules/@playwright/test/package.json')
      );
      return packageJson?.version || 'unknown';
    } catch {
      return 'unknown';
    }
  }

  async _loadConfig() {
    if (this.configPath) {
      // For JS/TS configs, we'll rely on Playwright's config loading
      this.config = { configFile: this.configPath };
    } else {
      this.config = {};
    }
  }

  async _setupReporters() {
    // Create custom reporter for baseline integration
    const reporterPath = path.join(__dirname, 'playwright-baseline-reporter.js');
    await this._createBaselineReporter(reporterPath);

    this.customReporter = reporterPath;
    this.reporterOptions = {
      outputFile: path.join(this.options.rootDir, '.test-baseline/playwright-results.json'),
      baseline: this.options.baseline
    };
  }

  async _setupCoverage() {
    if (this.options.coverage) {
      // Playwright doesn't have built-in code coverage like Jest
      // Coverage would be collected via instrumentation
      this.coverageOptions = {
        outputDir: path.join(this.options.rootDir, '.test-baseline/coverage'),
        include: ['src/**/*'],
        exclude: ['**/*.test.js', '**/*.spec.js']
      };
    }
  }

  async _setupProfiling() {
    if (this.options.profiling) {
      this.profilingOptions = {
        trace: true,
        video: 'retain-on-failure',
        screenshot: 'only-on-failure',
        outputDir: path.join(this.options.rootDir, '.test-baseline/profiling')
      };
    }
  }

  _getTestPatterns() {
    return [
      'tests/**/*.spec.{js,ts}',
      'e2e/**/*.spec.{js,ts}',
      '**/*.e2e.{js,ts}',
      '**/*.test.{js,ts}'
    ];
  }

  async _executeTests(options) {
    return new Promise((resolve, reject) => {
      const args = this._buildPlaywrightArgs(options);

      this.emit('testStarted', { command: `${this.playwrightPath} test ${args.join(' ')}` });

      this.runnerProcess = spawn(this.playwrightPath, ['test', ...args], {
        cwd: this.options.rootDir,
        stdio: ['pipe', 'pipe', 'pipe'],
        env: { ...process.env, CI: options.ci ? 'true' : 'false' }
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

  _buildPlaywrightArgs(options) {
    const args = [];

    // Custom reporter
    if (this.customReporter) {
      args.push('--reporter', `json,${this.customReporter}`);
    } else {
      args.push('--reporter', 'json');
    }

    // Output file for JSON results
    args.push('--output', path.join(this.options.rootDir, '.test-baseline'));

    // Browser selection
    if (options.browser) {
      args.push('--browser', options.browser);
    } else if (options.browsers) {
      options.browsers.forEach(browser => {
        args.push('--browser', browser);
      });
    }

    // Profiling options
    if (this.options.profiling && this.profilingOptions) {
      if (this.profilingOptions.trace) {
        args.push('--trace', 'on');
      }
      if (this.profilingOptions.video) {
        args.push('--video', this.profilingOptions.video);
      }
      if (this.profilingOptions.screenshot) {
        args.push('--screenshot', this.profilingOptions.screenshot);
      }
      args.push('--output-dir', this.profilingOptions.outputDir);
    }

    // General options
    if (options.headed) args.push('--headed');
    if (options.debug) args.push('--debug');
    if (options.ui) args.push('--ui');
    if (options.workers) args.push('--workers', options.workers.toString());
    if (options.maxFailures) args.push('--max-failures', options.maxFailures.toString());
    if (options.timeout) args.push('--timeout', options.timeout.toString());
    if (options.retries) args.push('--retries', options.retries.toString());

    // Test filtering
    if (options.grep) args.push('--grep', options.grep);
    if (options.grepInvert) args.push('--grep-invert', options.grepInvert);
    if (options.project) args.push('--project', options.project);

    // Config file
    if (this.configPath) {
      args.push('--config', this.configPath);
    }

    // Test files pattern
    if (options.testPathPattern) {
      args.push(options.testPathPattern);
    }

    return args;
  }

  async _parseResults(exitCode, stdout, stderr) {
    try {
      // Try to load JSON report
      let playwrightResults = {};
      const reportFiles = [
        path.join(this.options.rootDir, '.test-baseline/results.json'),
        path.join(this.options.rootDir, 'test-results/results.json'),
        path.join(this.options.rootDir, 'playwright-report/results.json')
      ];

      for (const reportFile of reportFiles) {
        try {
          playwrightResults = await this._readJson(reportFile);
          if (playwrightResults) break;
        } catch {
          continue;
        }
      }

      const tests = this._transformPlaywrightResults(playwrightResults);
      const summary = this._calculateSummary(tests);

      // Load trace and performance data
      let profiling = null;
      if (this.options.profiling) {
        profiling = await this._loadProfilingData();
      }

      // Load visual comparison data
      let visualData = null;
      if (this.options.visual) {
        visualData = await this._loadVisualData();
      }

      return {
        tests,
        summary: {
          ...summary,
          exitCode,
          playwright: {
            suites: playwrightResults.suites?.length || 0,
            projects: playwrightResults.config?.projects?.length || 0,
            browsers: this._extractBrowsers(tests)
          }
        },
        coverage: null, // Playwright doesn't provide built-in coverage
        profiling,
        visual: visualData,
        raw: {
          stdout,
          stderr,
          playwrightResults
        }
      };
    } catch (error) {
      throw new Error(`Failed to parse Playwright results: ${error.message}`);
    }
  }

  _transformPlaywrightResults(playwrightResults) {
    const tests = [];

    if (playwrightResults.suites) {
      for (const suite of playwrightResults.suites) {
        this._extractTestsFromSuite(suite, tests);
      }
    }

    return tests;
  }

  _extractTestsFromSuite(suite, tests, parentTitle = '') {
    const suiteTitle = parentTitle ? `${parentTitle} > ${suite.title}` : suite.title;

    if (suite.tests) {
      for (const test of suite.tests) {
        // Playwright can run the same test across multiple projects/browsers
        for (const result of test.results || []) {
          const projectName = result.projectName || 'default';
          const browser = this._extractBrowser(projectName);

          tests.push({
            name: `${test.title} [${projectName}]`,
            suite: suiteTitle,
            status: result.status === 'passed' ? 'passed' :
                   result.status === 'failed' ? 'failed' : 'skipped',
            duration: result.duration || 0,
            error: result.error?.message || result.errors?.[0]?.message || null,
            file: suite.file || test.location?.file,
            line: test.location?.line || null,
            browser: browser,
            project: projectName,
            retry: result.retry || 0,
            attachments: result.attachments || []
          });
        }
      }
    }

    if (suite.suites) {
      for (const nestedSuite of suite.suites) {
        this._extractTestsFromSuite(nestedSuite, tests, suiteTitle);
      }
    }
  }

  _extractBrowser(projectName) {
    const browserNames = ['chromium', 'firefox', 'webkit', 'chrome', 'safari', 'edge'];
    for (const browser of browserNames) {
      if (projectName.toLowerCase().includes(browser)) {
        return browser;
      }
    }
    return 'unknown';
  }

  _extractBrowsers(tests) {
    const browsers = new Set();
    for (const test of tests) {
      if (test.browser) {
        browsers.add(test.browser);
      }
    }
    return Array.from(browsers);
  }

  async _loadProfilingData() {
    try {
      const profilingDir = this.profilingOptions?.outputDir ||
                          path.join(this.options.rootDir, 'test-results');

      const profiling = {
        traces: [],
        videos: [],
        screenshots: [],
        performance: []
      };

      // Scan for trace files
      const traceFiles = await this._findFiles(profilingDir, '.zip');
      profiling.traces = traceFiles.map(file => ({
        path: file,
        test: this._extractTestNameFromPath(file),
        size: 0 // Could add file size here
      }));

      // Scan for video files
      const videoFiles = await this._findFiles(profilingDir, '.webm');
      profiling.videos = videoFiles.map(file => ({
        path: file,
        test: this._extractTestNameFromPath(file),
        size: 0
      }));

      // Scan for screenshot files
      const screenshotFiles = await this._findFiles(profilingDir, '.png');
      profiling.screenshots = screenshotFiles.map(file => ({
        path: file,
        test: this._extractTestNameFromPath(file),
        type: file.includes('diff') ? 'diff' :
              file.includes('expected') ? 'expected' :
              file.includes('actual') ? 'actual' : 'screenshot'
      }));

      return profiling;
    } catch {
      return null;
    }
  }

  async _loadVisualData() {
    try {
      const visualDir = path.join(this.options.rootDir, 'test-results');
      const visualData = {
        comparisons: [],
        failures: []
      };

      // Look for visual comparison files
      const diffFiles = await this._findFiles(visualDir, '-diff.png');
      for (const diffFile of diffFiles) {
        const testName = this._extractTestNameFromPath(diffFile);
        const expectedFile = diffFile.replace('-diff.png', '-expected.png');
        const actualFile = diffFile.replace('-diff.png', '-actual.png');

        visualData.comparisons.push({
          test: testName,
          diff: diffFile,
          expected: await this._fileExists(expectedFile) ? expectedFile : null,
          actual: await this._fileExists(actualFile) ? actualFile : null,
          passed: false
        });
      }

      return visualData;
    } catch {
      return null;
    }
  }

  async _findFiles(dir, extension) {
    try {
      const files = await fs.readdir(dir, { recursive: true });
      return files
        .filter(file => file.endsWith(extension))
        .map(file => path.join(dir, file));
    } catch {
      return [];
    }
  }

  _extractTestNameFromPath(filePath) {
    const basename = path.basename(filePath);
    // Remove file extension and browser/project suffixes
    return basename
      .replace(/\.(zip|webm|png)$/, '')
      .replace(/-chromium.*$/, '')
      .replace(/-firefox.*$/, '')
      .replace(/-webkit.*$/, '')
      .replace(/-\d+$/, ''); // Remove retry numbers
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

class PlaywrightBaselineReporter {
  constructor(options = {}) {
    this.options = options;
    this.tests = [];
    this.suites = [];
  }

  onBegin(config, suite) {
    console.log('🚀 Starting Playwright tests with baseline tracking');
    this.rootSuite = suite;
  }

  onTestBegin(test, result) {
    // Test started
  }

  onTestEnd(test, result) {
    const projectName = result.projectName || test.projectName || 'default';

    this.tests.push({
      name: \`\${test.title} [\${projectName}]\`,
      suite: this.getSuitePath(test.parent),
      status: result.status === 'passed' ? 'passed' :
             result.status === 'failed' ? 'failed' : 'skipped',
      duration: result.duration || 0,
      error: result.error?.message || result.errors?.[0]?.message || null,
      file: test.location?.file,
      line: test.location?.line,
      browser: this.extractBrowser(projectName),
      project: projectName,
      retry: result.retry || 0,
      attachments: (result.attachments || []).map(att => ({
        name: att.name,
        path: att.path,
        contentType: att.contentType
      }))
    });
  }

  onEnd(result) {
    this.writeReport();
  }

  getSuitePath(suite) {
    const path = [];
    let current = suite;

    while (current && current.title) {
      path.unshift(current.title);
      current = current.parent;
    }

    return path.join(' > ');
  }

  extractBrowser(projectName) {
    const browserNames = ['chromium', 'firefox', 'webkit', 'chrome', 'safari', 'edge'];
    for (const browser of browserNames) {
      if (projectName.toLowerCase().includes(browser)) {
        return browser;
      }
    }
    return 'unknown';
  }

  writeReport() {
    const outputFile = this.options.outputFile || '.test-baseline/playwright-baseline.json';
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
        skipped: this.tests.filter(t => t.status === 'skipped').length,
        duration: this.tests.reduce((sum, t) => sum + (t.duration || 0), 0),
        browsers: [...new Set(this.tests.map(t => t.browser))]
      },
      tests: this.tests,
      baseline: this.options.baseline
    };

    fs.writeFileSync(outputFile, JSON.stringify(reportData, null, 2));
    console.log(\`📊 Playwright baseline report written to \${outputFile}\`);
  }
}

module.exports = PlaywrightBaselineReporter;
`;

    await fs.writeFile(reporterPath, reporterCode, 'utf8');
  }
}

module.exports = PlaywrightAdapter;