/**
 * Baseline-Aware Reporter
 *
 * Custom reporter that provides baseline comparison, trend analysis,
 * and intelligent failure reporting across all test frameworks.
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;
const chalk = require('chalk');

class BaselineReporter extends EventEmitter {
  constructor(options = {}) {
    super();
    this.options = {
      rootDir: process.cwd(),
      outputDir: '.test-baseline',
      outputFile: null,
      baseline: null,
      showDiff: true,
      showTrends: true,
      showRecommendations: true,
      colorOutput: true,
      verbose: false,
      format: 'console', // console, json, html, markdown
      thresholds: {
        performance: {
          warning: 1.5, // 50% slower than baseline
          error: 2.0    // 100% slower than baseline
        },
        coverage: {
          warning: -5,  // 5% coverage drop
          error: -10    // 10% coverage drop
        }
      },
      ...options
    };

    this.results = null;
    this.baseline = null;
    this.comparison = null;
    this.trends = null;
    this.startTime = null;
    this.endTime = null;
  }

  /**
   * Initialize the reporter
   * @returns {Promise<void>}
   */
  async initialize() {
    this.emit('initialization', { status: 'started' });

    try {
      await this._setupOutputDirectory();
      await this._loadBaseline();
      await this._loadTrends();

      this.emit('initialization', { status: 'completed' });
    } catch (error) {
      this.emit('initialization', { status: 'failed', error: error.message });
      throw error;
    }
  }

  /**
   * Handle test run start
   * @param {Object} data - Test run start data
   */
  onRunStart(data) {
    this.startTime = Date.now();
    this.emit('runStarted', data);

    if (this.options.format === 'console') {
      console.log(chalk.blue('🚀 Starting test run with baseline tracking\n'));

      if (data.framework) {
        console.log(chalk.gray(`Framework: ${data.framework.name} v${data.framework.version}`));
      }

      if (this.baseline) {
        console.log(chalk.gray(`Baseline: ${this.baseline.timestamp} (${this.baseline.framework?.name || 'unknown'})`));
      }

      console.log('');
    }
  }

  /**
   * Handle test output
   * @param {Object} data - Test output data
   */
  onTestOutput(data) {
    if (this.options.verbose && this.options.format === 'console') {
      const prefix = data.type === 'stderr' ? chalk.red('[stderr]') : chalk.gray('[stdout]');
      console.log(`${prefix} ${data.data}`);
    }
  }

  /**
   * Handle individual test completion
   * @param {Object} test - Test result
   */
  onTestComplete(test) {
    this.emit('testCompleted', test);

    if (this.options.format === 'console' && this.options.verbose) {
      const status = this._getTestStatusIcon(test.status);
      const duration = test.duration ? ` (${test.duration}ms)` : '';
      console.log(`  ${status} ${test.name}${duration}`);
    }
  }

  /**
   * Handle test run completion
   * @param {Object} results - Complete test results
   */
  async onRunComplete(results) {
    this.endTime = Date.now();
    this.results = results;

    try {
      // Perform baseline comparison
      if (this.baseline) {
        this.comparison = await this._compareWithBaseline(results);
      }

      // Generate reports
      await this._generateReports();

      this.emit('runCompleted', {
        results: this.results,
        comparison: this.comparison,
        trends: this.trends
      });
    } catch (error) {
      this.emit('reportError', { error: error.message });
    }
  }

  /**
   * Handle run failure
   * @param {Object} error - Error information
   */
  onRunFailed(error) {
    this.endTime = Date.now();
    this.emit('runFailed', error);

    if (this.options.format === 'console') {
      console.log(chalk.red(`\n❌ Test run failed: ${error.error}\n`));
    }
  }

  /**
   * Generate all configured report formats
   * @returns {Promise<Array<string>>}
   */
  async _generateReports() {
    const formats = Array.isArray(this.options.format) ? this.options.format : [this.options.format];
    const generatedReports = [];

    for (const format of formats) {
      try {
        let reportPath;

        switch (format) {
          case 'console':
            await this._generateConsoleReport();
            reportPath = 'console';
            break;
          case 'json':
            reportPath = await this._generateJsonReport();
            break;
          case 'html':
            reportPath = await this._generateHtmlReport();
            break;
          case 'markdown':
            reportPath = await this._generateMarkdownReport();
            break;
          default:
            throw new Error(`Unsupported format: ${format}`);
        }

        generatedReports.push(reportPath);
      } catch (error) {
        this.emit('reportError', { format, error: error.message });
      }
    }

    return generatedReports;
  }

  async _generateConsoleReport() {
    const summary = this.results.summary;
    const duration = this.endTime - this.startTime;

    console.log(chalk.bold('\n📊 Test Results Summary\n'));

    // Overall status
    const overallStatus = summary.success ? '✅ PASSED' : '❌ FAILED';
    const statusColor = summary.success ? chalk.green : chalk.red;
    console.log(statusColor(overallStatus));

    // Test counts
    console.log(chalk.white(`Tests:       ${summary.total}`));
    console.log(chalk.green(`  Passed:    ${summary.passed}`));
    if (summary.failed > 0) {
      console.log(chalk.red(`  Failed:    ${summary.failed}`));
    }
    if (summary.skipped > 0) {
      console.log(chalk.yellow(`  Skipped:   ${summary.skipped}`));
    }

    // Duration
    console.log(chalk.white(`Duration:    ${this._formatDuration(duration)}`));

    // Coverage
    if (this.results.coverage) {
      console.log(chalk.white(`Coverage:    ${this.results.coverage.total.toFixed(2)}%`));
    }

    // Baseline comparison
    if (this.comparison) {
      console.log(chalk.bold('\n🔍 Baseline Comparison\n'));
      this._displayBaselineComparison();
    }

    // Performance analysis
    if (this.results.profiling) {
      console.log(chalk.bold('\n⚡ Performance Analysis\n'));
      this._displayPerformanceAnalysis();
    }

    // Recommendations
    if (this.options.showRecommendations) {
      const recommendations = this._generateRecommendations();
      if (recommendations.length > 0) {
        console.log(chalk.bold('\n💡 Recommendations\n'));
        this._displayRecommendations(recommendations);
      }
    }

    // Failed tests detail
    if (summary.failed > 0) {
      console.log(chalk.bold('\n🔴 Failed Tests\n'));
      this._displayFailedTests();
    }

    console.log('');
  }

  async _generateJsonReport() {
    const reportData = {
      timestamp: new Date().toISOString(),
      duration: this.endTime - this.startTime,
      results: this.results,
      baseline: this.baseline,
      comparison: this.comparison,
      trends: this.trends,
      recommendations: this._generateRecommendations()
    };

    const outputFile = this.options.outputFile ||
      path.join(this.options.rootDir, this.options.outputDir, 'baseline-report.json');

    await fs.writeFile(outputFile, JSON.stringify(reportData, null, 2));
    return outputFile;
  }

  async _generateHtmlReport() {
    const html = this._generateHtmlContent();
    const outputFile = path.join(this.options.rootDir, this.options.outputDir, 'baseline-report.html');

    await fs.writeFile(outputFile, html);
    return outputFile;
  }

  async _generateMarkdownReport() {
    const markdown = this._generateMarkdownContent();
    const outputFile = path.join(this.options.rootDir, this.options.outputDir, 'baseline-report.md');

    await fs.writeFile(outputFile, markdown);
    return outputFile;
  }

  _displayBaselineComparison() {
    const comp = this.comparison;

    // Test changes
    if (comp.testsAdded.length > 0) {
      console.log(chalk.green(`✨ Tests Added: ${comp.testsAdded.length}`));
      comp.testsAdded.slice(0, 3).forEach(test => {
        console.log(chalk.green(`  + ${test.name}`));
      });
      if (comp.testsAdded.length > 3) {
        console.log(chalk.gray(`    ... and ${comp.testsAdded.length - 3} more`));
      }
    }

    if (comp.testsRemoved.length > 0) {
      console.log(chalk.red(`🗑️  Tests Removed: ${comp.testsRemoved.length}`));
      comp.testsRemoved.slice(0, 3).forEach(test => {
        console.log(chalk.red(`  - ${test.name}`));
      });
      if (comp.testsRemoved.length > 3) {
        console.log(chalk.gray(`    ... and ${comp.testsRemoved.length - 3} more`));
      }
    }

    if (comp.testsChanged.length > 0) {
      console.log(chalk.yellow(`🔄 Tests Changed: ${comp.testsChanged.length}`));
      comp.testsChanged.slice(0, 3).forEach(test => {
        console.log(chalk.yellow(`  ~ ${test.name}: ${test.from} → ${test.to}`));
      });
      if (comp.testsChanged.length > 3) {
        console.log(chalk.gray(`    ... and ${comp.testsChanged.length - 3} more`));
      }
    }

    // Performance changes
    if (comp.performance.faster.length > 0) {
      console.log(chalk.green(`🚀 Faster Tests: ${comp.performance.faster.length}`));
      comp.performance.faster.slice(0, 3).forEach(test => {
        console.log(chalk.green(`  ⚡ ${test.name}: ${test.improvement.toFixed(0)}ms faster`));
      });
    }

    if (comp.performance.slower.length > 0) {
      console.log(chalk.red(`🐌 Slower Tests: ${comp.performance.slower.length}`));
      comp.performance.slower.slice(0, 3).forEach(test => {
        console.log(chalk.red(`  🕐 ${test.name}: ${test.regression.toFixed(0)}ms slower`));
      });
    }

    // Coverage changes
    if (comp.coverage.change !== 0) {
      const changeColor = comp.coverage.improved ? chalk.green : chalk.red;
      const changeIcon = comp.coverage.improved ? '📈' : '📉';
      const changeSign = comp.coverage.change > 0 ? '+' : '';
      console.log(changeColor(`${changeIcon} Coverage: ${changeSign}${comp.coverage.change.toFixed(2)}%`));
    }
  }

  _displayPerformanceAnalysis() {
    const profiling = this.results.profiling;

    if (profiling.bottlenecks) {
      const bottlenecks = profiling.bottlenecks;

      if (bottlenecks.slowTests.length > 0) {
        console.log(chalk.yellow('🐌 Slowest Tests:'));
        bottlenecks.slowTests.slice(0, 5).forEach((test, index) => {
          console.log(chalk.yellow(`  ${index + 1}. ${test.name}: ${this._formatDuration(test.duration)}`));
        });
      }

      if (bottlenecks.memoryIntensive.length > 0) {
        console.log(chalk.yellow('\n🧠 Memory-Intensive Tests:'));
        bottlenecks.memoryIntensive.slice(0, 3).forEach((test, index) => {
          const memoryDelta = test.memoryDelta.heapUsed / 1024 / 1024; // MB
          console.log(chalk.yellow(`  ${index + 1}. ${test.name}: +${memoryDelta.toFixed(2)}MB`));
        });
      }

      if (bottlenecks.gcPressure.length > 0) {
        console.log(chalk.red('\n♻️  High GC Pressure Detected'));
        bottlenecks.gcPressure.forEach(gc => {
          console.log(chalk.red(`  Average GC time: ${gc.averageGcTime.toFixed(2)}ms`));
        });
      }
    }
  }

  _displayRecommendations(recommendations) {
    recommendations.forEach((rec, index) => {
      const severityColor = {
        low: chalk.gray,
        medium: chalk.yellow,
        high: chalk.red
      }[rec.severity] || chalk.white;

      const severityIcon = {
        low: 'ℹ️',
        medium: '⚠️',
        high: '🚨'
      }[rec.severity] || 'ℹ️';

      console.log(severityColor(`${severityIcon} ${rec.message}`));

      if (rec.tests && rec.tests.length > 0) {
        console.log(severityColor(`   Affected tests: ${rec.tests.slice(0, 3).join(', ')}`));
        if (rec.tests.length > 3) {
          console.log(severityColor(`   ... and ${rec.tests.length - 3} more`));
        }
      }
      console.log('');
    });
  }

  _displayFailedTests() {
    const failedTests = this.results.tests.filter(test => test.status === 'failed');

    failedTests.forEach((test, index) => {
      console.log(chalk.red(`${index + 1}. ${test.name}`));
      if (test.error) {
        const errorLines = test.error.split('\n');
        console.log(chalk.red(`   ${errorLines[0]}`));
        if (errorLines.length > 1) {
          console.log(chalk.gray(`   ... (${errorLines.length - 1} more lines)`));
        }
      }
      console.log('');
    });
  }

  _generateRecommendations() {
    const recommendations = [];

    // Performance recommendations
    if (this.comparison?.performance?.slower?.length > 0) {
      const slowTests = this.comparison.performance.slower;
      const significantSlowdown = slowTests.filter(test =>
        test.regression > 1000 // More than 1 second slower
      );

      if (significantSlowdown.length > 0) {
        recommendations.push({
          type: 'performance',
          severity: 'high',
          message: `${significantSlowdown.length} tests are significantly slower than baseline. Consider profiling and optimizing these tests.`,
          tests: significantSlowdown.map(t => t.name)
        });
      }
    }

    // Coverage recommendations
    if (this.comparison?.coverage?.degraded) {
      const change = this.comparison.coverage.change;
      if (change <= this.options.thresholds.coverage.error) {
        recommendations.push({
          type: 'coverage',
          severity: 'high',
          message: `Coverage dropped by ${Math.abs(change).toFixed(2)}%. Add tests to restore coverage levels.`
        });
      } else if (change <= this.options.thresholds.coverage.warning) {
        recommendations.push({
          type: 'coverage',
          severity: 'medium',
          message: `Coverage dropped by ${Math.abs(change).toFixed(2)}%. Consider adding more tests.`
        });
      }
    }

    // Memory recommendations
    if (this.results.profiling?.bottlenecks?.memoryIntensive?.length > 0) {
      recommendations.push({
        type: 'memory',
        severity: 'medium',
        message: 'Some tests are using significant memory. Consider optimizing data usage or using mocks.',
        tests: this.results.profiling.bottlenecks.memoryIntensive.map(t => t.name)
      });
    }

    // Test maintenance recommendations
    if (this.comparison?.testsChanged?.length > 0) {
      const failingTests = this.comparison.testsChanged.filter(t => t.to === 'failed');
      if (failingTests.length > 0) {
        recommendations.push({
          type: 'maintenance',
          severity: 'high',
          message: `${failingTests.length} previously passing tests are now failing. Review recent changes.`,
          tests: failingTests.map(t => t.name)
        });
      }
    }

    return recommendations;
  }

  _generateHtmlContent() {
    const summary = this.results.summary;
    const duration = this.endTime - this.startTime;

    return `
<!DOCTYPE html>
<html>
<head>
    <title>Test Baseline Report</title>
    <meta charset="utf-8">
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; margin: 40px; }
        .header { border-bottom: 2px solid #e1e4e8; padding-bottom: 20px; margin-bottom: 30px; }
        .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .card { background: #f6f8fa; padding: 20px; border-radius: 8px; border-left: 4px solid #0366d6; }
        .card.success { border-left-color: #28a745; }
        .card.failure { border-left-color: #d73a49; }
        .card.warning { border-left-color: #ffc107; }
        .metric { font-size: 2em; font-weight: bold; margin-bottom: 5px; }
        .label { color: #586069; font-size: 0.9em; }
        .comparison { background: #f1f8ff; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .test-list { list-style: none; padding: 0; }
        .test-item { padding: 10px; border-bottom: 1px solid #e1e4e8; display: flex; justify-content: space-between; }
        .test-item:last-child { border-bottom: none; }
        .status { padding: 4px 8px; border-radius: 4px; font-size: 0.85em; font-weight: bold; }
        .status.passed { background: #dcffe4; color: #0e5020; }
        .status.failed { background: #ffeef0; color: #86181d; }
        .status.skipped { background: #fff8c5; color: #735c0f; }
        .recommendations { background: #fffbf0; border: 1px solid #f9c74f; padding: 20px; border-radius: 8px; margin: 20px 0; }
        .recommendation { margin-bottom: 15px; padding: 10px; background: white; border-radius: 4px; }
        .recommendation.high { border-left: 4px solid #d73a49; }
        .recommendation.medium { border-left: 4px solid #ffc107; }
        .recommendation.low { border-left: 4px solid #28a745; }
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 Test Baseline Report</h1>
        <p>Generated on ${new Date().toISOString()}</p>
        ${this.results.framework ? `<p>Framework: ${this.results.framework.name} v${this.results.framework.version}</p>` : ''}
    </div>

    <div class="summary">
        <div class="card ${summary.success ? 'success' : 'failure'}">
            <div class="metric">${summary.total}</div>
            <div class="label">Total Tests</div>
        </div>
        <div class="card success">
            <div class="metric">${summary.passed}</div>
            <div class="label">Passed</div>
        </div>
        ${summary.failed > 0 ? `
        <div class="card failure">
            <div class="metric">${summary.failed}</div>
            <div class="label">Failed</div>
        </div>` : ''}
        <div class="card">
            <div class="metric">${this._formatDuration(duration)}</div>
            <div class="label">Duration</div>
        </div>
        ${this.results.coverage ? `
        <div class="card">
            <div class="metric">${this.results.coverage.total.toFixed(1)}%</div>
            <div class="label">Coverage</div>
        </div>` : ''}
    </div>

    ${this.comparison ? this._generateHtmlComparison() : ''}

    ${this._generateHtmlRecommendations()}

    ${summary.failed > 0 ? this._generateHtmlFailedTests() : ''}

    <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e1e4e8; color: #586069; font-size: 0.9em;">
        Report generated by Baseline Reporter
    </div>
</body>
</html>`;
  }

  _generateHtmlComparison() {
    if (!this.comparison) return '';

    const comp = this.comparison;
    let html = '<div class="comparison"><h2>📊 Baseline Comparison</h2>';

    if (comp.testsAdded.length > 0) {
      html += `<h3>✨ Tests Added (${comp.testsAdded.length})</h3>`;
      html += '<ul class="test-list">';
      comp.testsAdded.slice(0, 10).forEach(test => {
        html += `<li class="test-item">${test.name}</li>`;
      });
      if (comp.testsAdded.length > 10) {
        html += `<li class="test-item"><em>... and ${comp.testsAdded.length - 10} more</em></li>`;
      }
      html += '</ul>';
    }

    if (comp.performance.slower.length > 0) {
      html += `<h3>🐌 Slower Tests (${comp.performance.slower.length})</h3>`;
      html += '<ul class="test-list">';
      comp.performance.slower.slice(0, 10).forEach(test => {
        html += `<li class="test-item">
          <span>${test.name}</span>
          <span>+${test.regression.toFixed(0)}ms</span>
        </li>`;
      });
      html += '</ul>';
    }

    html += '</div>';
    return html;
  }

  _generateHtmlRecommendations() {
    const recommendations = this._generateRecommendations();
    if (recommendations.length === 0) return '';

    let html = '<div class="recommendations"><h2>💡 Recommendations</h2>';

    recommendations.forEach(rec => {
      html += `<div class="recommendation ${rec.severity}">
        <strong>${this._getSeverityIcon(rec.severity)} ${rec.message}</strong>
        ${rec.tests ? `<br><small>Affected tests: ${rec.tests.slice(0, 5).join(', ')}${rec.tests.length > 5 ? ` and ${rec.tests.length - 5} more` : ''}</small>` : ''}
      </div>`;
    });

    html += '</div>';
    return html;
  }

  _generateHtmlFailedTests() {
    const failedTests = this.results.tests.filter(test => test.status === 'failed');

    let html = '<div><h2>🔴 Failed Tests</h2><ul class="test-list">';

    failedTests.forEach(test => {
      html += `<li class="test-item">
        <div>
          <strong>${test.name}</strong>
          ${test.error ? `<br><small style="color: #d73a49;">${test.error.split('\n')[0]}</small>` : ''}
        </div>
        <span class="status failed">FAILED</span>
      </li>`;
    });

    html += '</ul></div>';
    return html;
  }

  _generateMarkdownContent() {
    const summary = this.results.summary;
    const duration = this.endTime - this.startTime;

    let markdown = `# 🧪 Test Baseline Report

Generated on ${new Date().toISOString()}

`;

    if (this.results.framework) {
      markdown += `**Framework:** ${this.results.framework.name} v${this.results.framework.version}\n\n`;
    }

    // Summary
    markdown += `## 📊 Summary

| Metric | Value |
|--------|-------|
| Total Tests | ${summary.total} |
| Passed | ${summary.passed} |
| Failed | ${summary.failed} |
| Skipped | ${summary.skipped} |
| Duration | ${this._formatDuration(duration)} |
`;

    if (this.results.coverage) {
      markdown += `| Coverage | ${this.results.coverage.total.toFixed(2)}% |\n`;
    }

    // Baseline comparison
    if (this.comparison) {
      markdown += '\n## 🔍 Baseline Comparison\n\n';

      if (this.comparison.testsAdded.length > 0) {
        markdown += `### ✨ Tests Added (${this.comparison.testsAdded.length})\n\n`;
        this.comparison.testsAdded.slice(0, 10).forEach(test => {
          markdown += `- ${test.name}\n`;
        });
        if (this.comparison.testsAdded.length > 10) {
          markdown += `- ... and ${this.comparison.testsAdded.length - 10} more\n`;
        }
        markdown += '\n';
      }

      if (this.comparison.performance.slower.length > 0) {
        markdown += `### 🐌 Slower Tests (${this.comparison.performance.slower.length})\n\n`;
        this.comparison.performance.slower.slice(0, 10).forEach(test => {
          markdown += `- **${test.name}**: +${test.regression.toFixed(0)}ms\n`;
        });
        markdown += '\n';
      }
    }

    // Recommendations
    const recommendations = this._generateRecommendations();
    if (recommendations.length > 0) {
      markdown += '## 💡 Recommendations\n\n';
      recommendations.forEach(rec => {
        const icon = this._getSeverityIcon(rec.severity);
        markdown += `### ${icon} ${rec.message}\n\n`;
        if (rec.tests && rec.tests.length > 0) {
          markdown += `**Affected tests:**\n`;
          rec.tests.slice(0, 5).forEach(test => {
            markdown += `- ${test}\n`;
          });
          if (rec.tests.length > 5) {
            markdown += `- ... and ${rec.tests.length - 5} more\n`;
          }
        }
        markdown += '\n';
      });
    }

    return markdown;
  }

  async _setupOutputDirectory() {
    const outputDir = path.join(this.options.rootDir, this.options.outputDir);
    await fs.mkdir(outputDir, { recursive: true });
  }

  async _loadBaseline() {
    if (this.options.baseline) {
      if (typeof this.options.baseline === 'string') {
        try {
          const baselineContent = await fs.readFile(this.options.baseline, 'utf8');
          this.baseline = JSON.parse(baselineContent);
        } catch (error) {
          this.emit('baselineLoadError', { file: this.options.baseline, error: error.message });
        }
      } else {
        this.baseline = this.options.baseline;
      }
    }
  }

  async _loadTrends() {
    // Load trending data if available
    try {
      const trendsDir = path.join(this.options.rootDir, this.options.outputDir, 'trends');
      const trendFiles = await fs.readdir(trendsDir);

      // Load recent trend data (last 30 days)
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - 30);

      this.trends = [];
      for (const file of trendFiles.filter(f => f.endsWith('.json'))) {
        const dateStr = file.replace('.json', '');
        if (new Date(dateStr) >= cutoffDate) {
          const trendData = JSON.parse(await fs.readFile(path.join(trendsDir, file), 'utf8'));
          this.trends.push({ date: dateStr, ...trendData });
        }
      }

      this.trends.sort((a, b) => a.date.localeCompare(b.date));
    } catch {
      // Trends not available
      this.trends = null;
    }
  }

  async _compareWithBaseline(results) {
    if (!this.baseline) return null;

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

    // Compare tests
    const currentTests = new Map(results.tests.map(t => [t.name, t]));
    const baselineTests = new Map(this.baseline.results?.tests?.map(t => [t.name, t]) || []);

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
          if (change < -10) { // More than 10ms faster
            comparison.performance.faster.push({
              name,
              improvement: Math.abs(change)
            });
          } else if (change > 10) { // More than 10ms slower
            comparison.performance.slower.push({
              name,
              regression: change
            });
          }
        }
      }
    }

    // Coverage comparison
    if (results.coverage && this.baseline.results?.coverage) {
      const currentCoverage = results.coverage.total || 0;
      const baselineCoverage = this.baseline.results.coverage.total || 0;
      comparison.coverage.change = currentCoverage - baselineCoverage;
      comparison.coverage.improved = comparison.coverage.change > 0;
      comparison.coverage.degraded = comparison.coverage.change < 0;
    }

    return comparison;
  }

  _getTestStatusIcon(status) {
    switch (status) {
      case 'passed': return '✅';
      case 'failed': return '❌';
      case 'skipped': return '⏭️';
      default: return '❓';
    }
  }

  _getSeverityIcon(severity) {
    switch (severity) {
      case 'high': return '🚨';
      case 'medium': return '⚠️';
      case 'low': return 'ℹ️';
      default: return 'ℹ️';
    }
  }

  _formatDuration(ms) {
    if (ms < 1000) return `${ms}ms`;
    if (ms < 60000) return `${(ms / 1000).toFixed(2)}s`;
    const minutes = Math.floor(ms / 60000);
    const seconds = Math.floor((ms % 60000) / 1000);
    return `${minutes}m ${seconds}s`;
  }
}

module.exports = BaselineReporter;