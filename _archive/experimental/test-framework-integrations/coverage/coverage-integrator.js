/**
 * Coverage Integration System
 *
 * Unifies coverage collection and reporting across different test frameworks
 * and coverage providers (NYC/Istanbul, Coverage.py, V8, C8).
 */

const EventEmitter = require('events');
const path = require('path');
const fs = require('fs').promises;
const { spawn } = require('child_process');

class CoverageIntegrator extends EventEmitter {
  constructor(options = {}) {
    super();
    this.options = {
      rootDir: process.cwd(),
      outputDir: '.test-baseline/coverage',
      providers: ['auto'], // auto, nyc, istanbul, c8, v8, coverage.py
      formats: ['json', 'html', 'text'],
      include: [],
      exclude: [],
      threshold: {
        statements: 80,
        branches: 80,
        functions: 80,
        lines: 80
      },
      merge: true,
      ...options
    };

    this.detectedProviders = [];
    this.activeProvider = null;
    this.reports = new Map();
    this.mergedReport = null;
  }

  /**
   * Initialize coverage integration
   * @returns {Promise<void>}
   */
  async initialize() {
    this.emit('initialization', { status: 'started' });

    try {
      await this._detectProviders();
      await this._selectProvider();
      await this._setupOutputDirectory();

      this.emit('initialization', {
        status: 'completed',
        provider: this.activeProvider,
        detected: this.detectedProviders
      });
    } catch (error) {
      this.emit('initialization', { status: 'failed', error: error.message });
      throw error;
    }
  }

  /**
   * Collect coverage for a specific test run
   * @param {string} framework - Test framework name
   * @param {string} command - Test command to wrap with coverage
   * @param {Object} options - Coverage options
   * @returns {Promise<Object>}
   */
  async collectCoverage(framework, command, options = {}) {
    const coverageOptions = { ...this.options, ...options };

    this.emit('collectionStarted', { framework, provider: this.activeProvider });

    try {
      let coverageData;

      switch (this.activeProvider) {
        case 'nyc':
          coverageData = await this._collectNycCoverage(command, coverageOptions);
          break;
        case 'c8':
          coverageData = await this._collectC8Coverage(command, coverageOptions);
          break;
        case 'v8':
          coverageData = await this._collectV8Coverage(command, coverageOptions);
          break;
        case 'coverage.py':
          coverageData = await this._collectPythonCoverage(command, coverageOptions);
          break;
        default:
          throw new Error(`Unsupported coverage provider: ${this.activeProvider}`);
      }

      // Transform to unified format
      const unifiedCoverage = await this._transformCoverage(coverageData, framework);

      this.reports.set(framework, unifiedCoverage);

      this.emit('collectionCompleted', {
        framework,
        provider: this.activeProvider,
        coverage: unifiedCoverage
      });

      return unifiedCoverage;
    } catch (error) {
      this.emit('collectionFailed', {
        framework,
        provider: this.activeProvider,
        error: error.message
      });
      throw error;
    }
  }

  /**
   * Merge coverage reports from multiple sources
   * @param {Array<string>} frameworks - Framework names to merge
   * @returns {Promise<Object>}
   */
  async mergeCoverage(frameworks = []) {
    if (frameworks.length === 0) {
      frameworks = Array.from(this.reports.keys());
    }

    this.emit('mergeStarted', { frameworks });

    try {
      const reportsToMerge = frameworks
        .map(framework => this.reports.get(framework))
        .filter(report => report !== undefined);

      if (reportsToMerge.length === 0) {
        throw new Error('No coverage reports available to merge');
      }

      this.mergedReport = await this._mergeCoverageReports(reportsToMerge);

      // Generate merged reports
      await this._generateReports(this.mergedReport, 'merged');

      this.emit('mergeCompleted', {
        frameworks,
        coverage: this.mergedReport
      });

      return this.mergedReport;
    } catch (error) {
      this.emit('mergeFailed', { frameworks, error: error.message });
      throw error;
    }
  }

  /**
   * Generate coverage reports in various formats
   * @param {Object} coverage - Coverage data
   * @param {string} name - Report name
   * @returns {Promise<Array<string>>}
   */
  async generateReports(coverage, name = 'coverage') {
    const outputPaths = [];

    for (const format of this.options.formats) {
      try {
        const outputPath = await this._generateReport(coverage, format, name);
        outputPaths.push(outputPath);

        this.emit('reportGenerated', {
          format,
          path: outputPath,
          name
        });
      } catch (error) {
        this.emit('reportFailed', {
          format,
          name,
          error: error.message
        });
      }
    }

    return outputPaths;
  }

  /**
   * Check coverage against thresholds
   * @param {Object} coverage - Coverage data
   * @returns {Object}
   */
  checkThresholds(coverage) {
    const results = {
      passed: true,
      failures: [],
      summary: {}
    };

    const metrics = ['statements', 'branches', 'functions', 'lines'];

    for (const metric of metrics) {
      const threshold = this.options.threshold[metric];
      const actual = coverage[metric]?.percentage || 0;

      results.summary[metric] = {
        threshold,
        actual,
        passed: actual >= threshold
      };

      if (actual < threshold) {
        results.passed = false;
        results.failures.push({
          metric,
          threshold,
          actual,
          gap: threshold - actual
        });
      }
    }

    this.emit('thresholdCheck', results);

    return results;
  }

  /**
   * Get trending coverage data
   * @param {number} days - Number of days to analyze
   * @returns {Promise<Object>}
   */
  async getCoverageTrends(days = 30) {
    try {
      const trendsDir = path.join(this.options.rootDir, this.options.outputDir, 'trends');
      const trends = {
        period: days,
        data: [],
        summary: {
          improvement: 0,
          regression: 0,
          stable: 0
        }
      };

      // Load historical coverage data
      const trendFiles = await this._loadTrendFiles(trendsDir, days);

      for (const file of trendFiles) {
        const trendData = await this._readJson(file.path);
        if (trendData) {
          trends.data.push({
            date: file.date,
            coverage: trendData.total || 0,
            details: trendData
          });
        }
      }

      // Analyze trends
      if (trends.data.length > 1) {
        trends.summary = this._analyzeTrends(trends.data);
      }

      return trends;
    } catch (error) {
      this.emit('trendsError', { error: error.message });
      return null;
    }
  }

  /**
   * Save coverage data for baseline comparison
   * @param {Object} coverage - Coverage data
   * @param {string} label - Baseline label
   * @returns {Promise<void>}
   */
  async saveBaseline(coverage, label = 'latest') {
    try {
      const baselineDir = path.join(this.options.rootDir, this.options.outputDir, 'baselines');
      await fs.mkdir(baselineDir, { recursive: true });

      const baselineFile = path.join(baselineDir, `${label}.json`);
      const baselineData = {
        timestamp: new Date().toISOString(),
        label,
        coverage,
        provider: this.activeProvider
      };

      await fs.writeFile(baselineFile, JSON.stringify(baselineData, null, 2));

      // Also save to trends
      await this._saveTrendData(coverage);

      this.emit('baselineSaved', {
        label,
        file: baselineFile,
        coverage: coverage.total
      });
    } catch (error) {
      this.emit('baselineSaveError', {
        label,
        error: error.message
      });
    }
  }

  // Private methods

  async _detectProviders() {
    const providers = [
      { name: 'nyc', command: 'nyc', packageName: 'nyc' },
      { name: 'c8', command: 'c8', packageName: 'c8' },
      { name: 'coverage.py', command: 'coverage', packageName: 'coverage' }
    ];

    for (const provider of providers) {
      try {
        // Check if package is installed
        const packageJsonPath = path.join(this.options.rootDir, 'package.json');
        const packageJson = await this._readJson(packageJsonPath);

        if (packageJson?.dependencies?.[provider.packageName] ||
            packageJson?.devDependencies?.[provider.packageName]) {
          this.detectedProviders.push(provider.name);
          continue;
        }

        // Check if command is available globally
        await this._checkCommand(provider.command);
        this.detectedProviders.push(provider.name);
      } catch {
        // Provider not available
      }
    }

    // Always include V8 as it's built into Node.js
    this.detectedProviders.push('v8');
  }

  async _selectProvider() {
    if (this.options.providers.includes('auto')) {
      // Auto-select based on detected providers and project type
      if (this.detectedProviders.includes('nyc')) {
        this.activeProvider = 'nyc';
      } else if (this.detectedProviders.includes('c8')) {
        this.activeProvider = 'c8';
      } else if (this.detectedProviders.includes('coverage.py')) {
        this.activeProvider = 'coverage.py';
      } else {
        this.activeProvider = 'v8';
      }
    } else {
      // Use specified provider
      const specifiedProvider = this.options.providers.find(p =>
        this.detectedProviders.includes(p)
      );

      if (!specifiedProvider) {
        throw new Error(`None of the specified providers are available: ${this.options.providers.join(', ')}`);
      }

      this.activeProvider = specifiedProvider;
    }
  }

  async _setupOutputDirectory() {
    const outputDir = path.join(this.options.rootDir, this.options.outputDir);
    await fs.mkdir(outputDir, { recursive: true });

    // Create subdirectories
    const subdirs = ['raw', 'html', 'trends', 'baselines'];
    for (const subdir of subdirs) {
      await fs.mkdir(path.join(outputDir, subdir), { recursive: true });
    }
  }

  async _collectNycCoverage(command, options) {
    const args = [
      '--reporter', 'json',
      '--report-dir', path.join(this.options.rootDir, this.options.outputDir, 'raw'),
      '--temp-dir', path.join(this.options.rootDir, '.nyc_output')
    ];

    // Add include/exclude patterns
    options.include.forEach(pattern => args.push('--include', pattern));
    options.exclude.forEach(pattern => args.push('--exclude', pattern));

    // Add the command to run
    args.push('--', ...command.split(' '));

    return this._runCommand('nyc', args);
  }

  async _collectC8Coverage(command, options) {
    const args = [
      '--reporter', 'json',
      '--reports-dir', path.join(this.options.rootDir, this.options.outputDir, 'raw')
    ];

    // Add include/exclude patterns
    options.include.forEach(pattern => args.push('--include', pattern));
    options.exclude.forEach(pattern => args.push('--exclude', pattern));

    // Add the command to run
    args.push('--', ...command.split(' '));

    return this._runCommand('c8', args);
  }

  async _collectV8Coverage(command, options) {
    // V8 coverage requires Node.js flags
    const env = {
      ...process.env,
      NODE_V8_COVERAGE: path.join(this.options.rootDir, this.options.outputDir, 'raw')
    };

    return this._runCommand('node', command.split(' '), { env });
  }

  async _collectPythonCoverage(command, options) {
    const args = ['run'];

    // Add source patterns
    if (options.include.length > 0) {
      args.push('--source', options.include.join(','));
    }

    // Add the command to run
    args.push(...command.split(' '));

    await this._runCommand('coverage', args);

    // Generate JSON report
    await this._runCommand('coverage', [
      'json',
      '-o',
      path.join(this.options.rootDir, this.options.outputDir, 'raw', 'coverage.json')
    ]);

    return 'coverage.json';
  }

  async _runCommand(command, args, options = {}) {
    return new Promise((resolve, reject) => {
      const proc = spawn(command, args, {
        cwd: this.options.rootDir,
        stdio: 'pipe',
        ...options
      });

      let stdout = '';
      let stderr = '';

      proc.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      proc.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      proc.on('close', (code) => {
        if (code === 0) {
          resolve({ stdout, stderr });
        } else {
          reject(new Error(`Command failed with code ${code}: ${stderr}`));
        }
      });

      proc.on('error', reject);
    });
  }

  async _transformCoverage(rawData, framework) {
    // Load raw coverage data and transform to unified format
    const rawDir = path.join(this.options.rootDir, this.options.outputDir, 'raw');

    let coverageData;
    if (this.activeProvider === 'coverage.py') {
      coverageData = await this._readJson(path.join(rawDir, 'coverage.json'));
    } else {
      // Look for JSON coverage files
      const jsonFiles = await this._findJsonFiles(rawDir);
      if (jsonFiles.length > 0) {
        coverageData = await this._readJson(jsonFiles[0]);
      }
    }

    if (!coverageData) {
      throw new Error('No coverage data found');
    }

    return this._normalizeCoverage(coverageData, framework);
  }

  _normalizecoverage(coverageData, framework) {
    // Normalize different coverage formats to unified structure
    const normalized = {
      framework,
      provider: this.activeProvider,
      timestamp: new Date().toISOString(),
      statements: { total: 0, covered: 0, percentage: 0 },
      branches: { total: 0, covered: 0, percentage: 0 },
      functions: { total: 0, covered: 0, percentage: 0 },
      lines: { total: 0, covered: 0, percentage: 0 },
      files: {},
      total: 0
    };

    if (this.activeProvider === 'coverage.py') {
      // Python coverage format
      const totals = coverageData.totals || {};
      normalized.statements.total = totals.num_statements || 0;
      normalized.statements.covered = totals.covered_lines || 0;
      normalized.statements.percentage = totals.percent_covered || 0;
      normalized.total = normalized.statements.percentage;
    } else {
      // JavaScript coverage formats (NYC, C8, V8)
      let totalStatements = 0;
      let coveredStatements = 0;
      let totalBranches = 0;
      let coveredBranches = 0;
      let totalFunctions = 0;
      let coveredFunctions = 0;

      for (const [filePath, fileData] of Object.entries(coverageData)) {
        if (fileData.s) {
          totalStatements += Object.keys(fileData.s).length;
          coveredStatements += Object.values(fileData.s).filter(x => x > 0).length;
        }

        if (fileData.b) {
          totalBranches += Object.keys(fileData.b).length;
          coveredBranches += Object.values(fileData.b).filter(branches =>
            branches.some(x => x > 0)).length;
        }

        if (fileData.f) {
          totalFunctions += Object.keys(fileData.f).length;
          coveredFunctions += Object.values(fileData.f).filter(x => x > 0).length;
        }

        normalized.files[filePath] = {
          statements: fileData.s ? {
            total: Object.keys(fileData.s).length,
            covered: Object.values(fileData.s).filter(x => x > 0).length
          } : { total: 0, covered: 0 },
          branches: fileData.b ? {
            total: Object.keys(fileData.b).length,
            covered: Object.values(fileData.b).filter(branches =>
              branches.some(x => x > 0)).length
          } : { total: 0, covered: 0 },
          functions: fileData.f ? {
            total: Object.keys(fileData.f).length,
            covered: Object.values(fileData.f).filter(x => x > 0).length
          } : { total: 0, covered: 0 }
        };
      }

      normalized.statements = {
        total: totalStatements,
        covered: coveredStatements,
        percentage: totalStatements > 0 ? (coveredStatements / totalStatements) * 100 : 0
      };

      normalized.branches = {
        total: totalBranches,
        covered: coveredBranches,
        percentage: totalBranches > 0 ? (coveredBranches / totalBranches) * 100 : 0
      };

      normalized.functions = {
        total: totalFunctions,
        covered: coveredFunctions,
        percentage: totalFunctions > 0 ? (coveredFunctions / totalFunctions) * 100 : 0
      };

      normalized.total = normalized.statements.percentage;
    }

    return normalized;
  }

  async _mergeCoverageReports(reports) {
    const merged = {
      frameworks: reports.map(r => r.framework),
      providers: [...new Set(reports.map(r => r.provider))],
      timestamp: new Date().toISOString(),
      statements: { total: 0, covered: 0, percentage: 0 },
      branches: { total: 0, covered: 0, percentage: 0 },
      functions: { total: 0, covered: 0, percentage: 0 },
      lines: { total: 0, covered: 0, percentage: 0 },
      files: {},
      total: 0
    };

    // Merge file-level coverage
    const allFiles = new Set();
    for (const report of reports) {
      Object.keys(report.files || {}).forEach(file => allFiles.add(file));
    }

    for (const filePath of allFiles) {
      const fileStats = {
        statements: { total: 0, covered: 0 },
        branches: { total: 0, covered: 0 },
        functions: { total: 0, covered: 0 }
      };

      for (const report of reports) {
        const fileData = report.files[filePath];
        if (fileData) {
          fileStats.statements.total = Math.max(fileStats.statements.total, fileData.statements.total);
          fileStats.statements.covered = Math.max(fileStats.statements.covered, fileData.statements.covered);
          fileStats.branches.total = Math.max(fileStats.branches.total, fileData.branches.total);
          fileStats.branches.covered = Math.max(fileStats.branches.covered, fileData.branches.covered);
          fileStats.functions.total = Math.max(fileStats.functions.total, fileData.functions.total);
          fileStats.functions.covered = Math.max(fileStats.functions.covered, fileData.functions.covered);
        }
      }

      merged.files[filePath] = fileStats;
    }

    // Calculate merged totals
    for (const fileStats of Object.values(merged.files)) {
      merged.statements.total += fileStats.statements.total;
      merged.statements.covered += fileStats.statements.covered;
      merged.branches.total += fileStats.branches.total;
      merged.branches.covered += fileStats.branches.covered;
      merged.functions.total += fileStats.functions.total;
      merged.functions.covered += fileStats.functions.covered;
    }

    // Calculate percentages
    merged.statements.percentage = merged.statements.total > 0 ?
      (merged.statements.covered / merged.statements.total) * 100 : 0;
    merged.branches.percentage = merged.branches.total > 0 ?
      (merged.branches.covered / merged.branches.total) * 100 : 0;
    merged.functions.percentage = merged.functions.total > 0 ?
      (merged.functions.covered / merged.functions.total) * 100 : 0;

    merged.total = merged.statements.percentage;

    return merged;
  }

  async _generateReport(coverage, format, name) {
    const outputDir = path.join(this.options.rootDir, this.options.outputDir);
    let outputPath;

    switch (format) {
      case 'json':
        outputPath = path.join(outputDir, `${name}.json`);
        await fs.writeFile(outputPath, JSON.stringify(coverage, null, 2));
        break;

      case 'html':
        outputPath = path.join(outputDir, 'html', name);
        await this._generateHtmlReport(coverage, outputPath);
        break;

      case 'text':
        outputPath = path.join(outputDir, `${name}.txt`);
        await this._generateTextReport(coverage, outputPath);
        break;

      default:
        throw new Error(`Unsupported report format: ${format}`);
    }

    return outputPath;
  }

  async _generateHtmlReport(coverage, outputPath) {
    await fs.mkdir(outputPath, { recursive: true });

    const html = `
<!DOCTYPE html>
<html>
<head>
    <title>Coverage Report</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .summary { background: #f5f5f5; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
        .metric { display: inline-block; margin: 10px; padding: 10px; background: white; border-radius: 3px; }
        .percentage { font-weight: bold; font-size: 1.2em; }
        .good { color: green; }
        .medium { color: orange; }
        .poor { color: red; }
        table { width: 100%; border-collapse: collapse; }
        th, td { padding: 8px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #f2f2f2; }
    </style>
</head>
<body>
    <h1>Coverage Report</h1>

    <div class="summary">
        <h2>Summary</h2>
        <div class="metric">
            <div>Statements</div>
            <div class="percentage ${this._getCoverageClass(coverage.statements.percentage)}">
                ${coverage.statements.percentage.toFixed(2)}%
            </div>
            <div>${coverage.statements.covered}/${coverage.statements.total}</div>
        </div>
        <div class="metric">
            <div>Branches</div>
            <div class="percentage ${this._getCoverageClass(coverage.branches.percentage)}">
                ${coverage.branches.percentage.toFixed(2)}%
            </div>
            <div>${coverage.branches.covered}/${coverage.branches.total}</div>
        </div>
        <div class="metric">
            <div>Functions</div>
            <div class="percentage ${this._getCoverageClass(coverage.functions.percentage)}">
                ${coverage.functions.percentage.toFixed(2)}%
            </div>
            <div>${coverage.functions.covered}/${coverage.functions.total}</div>
        </div>
    </div>

    <h2>Files</h2>
    <table>
        <thead>
            <tr>
                <th>File</th>
                <th>Statements</th>
                <th>Branches</th>
                <th>Functions</th>
            </tr>
        </thead>
        <tbody>
            ${Object.entries(coverage.files || {}).map(([file, stats]) => `
                <tr>
                    <td>${file}</td>
                    <td class="${this._getCoverageClass(this._calculatePercentage(stats.statements))}">
                        ${this._calculatePercentage(stats.statements).toFixed(2)}%
                    </td>
                    <td class="${this._getCoverageClass(this._calculatePercentage(stats.branches))}">
                        ${this._calculatePercentage(stats.branches).toFixed(2)}%
                    </td>
                    <td class="${this._getCoverageClass(this._calculatePercentage(stats.functions))}">
                        ${this._calculatePercentage(stats.functions).toFixed(2)}%
                    </td>
                </tr>
            `).join('')}
        </tbody>
    </table>

    <footer>
        <p>Generated on ${new Date().toISOString()}</p>
        <p>Framework: ${coverage.framework || 'Multiple'} | Provider: ${coverage.provider || coverage.providers?.join(', ')}</p>
    </footer>
</body>
</html>`;

    await fs.writeFile(path.join(outputPath, 'index.html'), html);
  }

  async _generateTextReport(coverage, outputPath) {
    const lines = [
      'Coverage Report',
      '===============',
      '',
      'Summary:',
      `  Statements: ${coverage.statements.percentage.toFixed(2)}% (${coverage.statements.covered}/${coverage.statements.total})`,
      `  Branches:   ${coverage.branches.percentage.toFixed(2)}% (${coverage.branches.covered}/${coverage.branches.total})`,
      `  Functions:  ${coverage.functions.percentage.toFixed(2)}% (${coverage.functions.covered}/${coverage.functions.total})`,
      `  Total:      ${coverage.total.toFixed(2)}%`,
      '',
      'Files:',
      '------'
    ];

    for (const [file, stats] of Object.entries(coverage.files || {})) {
      const stmtPct = this._calculatePercentage(stats.statements);
      const branchPct = this._calculatePercentage(stats.branches);
      const funcPct = this._calculatePercentage(stats.functions);

      lines.push(`${file}: ${stmtPct.toFixed(2)}% | ${branchPct.toFixed(2)}% | ${funcPct.toFixed(2)}%`);
    }

    lines.push('');
    lines.push(`Generated: ${new Date().toISOString()}`);
    lines.push(`Framework: ${coverage.framework || 'Multiple'}`);
    lines.push(`Provider: ${coverage.provider || coverage.providers?.join(', ')}`);

    await fs.writeFile(outputPath, lines.join('\n'));
  }

  _getCoverageClass(percentage) {
    if (percentage >= 80) return 'good';
    if (percentage >= 60) return 'medium';
    return 'poor';
  }

  _calculatePercentage(stats) {
    return stats.total > 0 ? (stats.covered / stats.total) * 100 : 0;
  }

  async _saveTrendData(coverage) {
    const trendsDir = path.join(this.options.rootDir, this.options.outputDir, 'trends');
    const date = new Date().toISOString().split('T')[0]; // YYYY-MM-DD
    const trendFile = path.join(trendsDir, `${date}.json`);

    await fs.writeFile(trendFile, JSON.stringify(coverage, null, 2));
  }

  async _loadTrendFiles(trendsDir, days) {
    try {
      const files = await fs.readdir(trendsDir);
      const cutoffDate = new Date();
      cutoffDate.setDate(cutoffDate.getDate() - days);

      return files
        .filter(file => file.endsWith('.json'))
        .map(file => ({
          path: path.join(trendsDir, file),
          date: file.replace('.json', '')
        }))
        .filter(item => new Date(item.date) >= cutoffDate)
        .sort((a, b) => a.date.localeCompare(b.date));
    } catch {
      return [];
    }
  }

  _analyzeTrends(data) {
    const summary = {
      improvement: 0,
      regression: 0,
      stable: 0,
      trend: 'stable'
    };

    for (let i = 1; i < data.length; i++) {
      const current = data[i].coverage;
      const previous = data[i - 1].coverage;
      const diff = current - previous;

      if (Math.abs(diff) < 0.1) {
        summary.stable++;
      } else if (diff > 0) {
        summary.improvement++;
      } else {
        summary.regression++;
      }
    }

    if (summary.improvement > summary.regression) {
      summary.trend = 'improving';
    } else if (summary.regression > summary.improvement) {
      summary.trend = 'declining';
    }

    return summary;
  }

  async _checkCommand(command) {
    return new Promise((resolve, reject) => {
      const proc = spawn(command, ['--version'], { stdio: 'pipe' });
      proc.on('close', (code) => {
        if (code === 0) resolve();
        else reject(new Error(`Command not found: ${command}`));
      });
      proc.on('error', reject);
    });
  }

  async _findJsonFiles(dir) {
    try {
      const files = await fs.readdir(dir);
      return files
        .filter(file => file.endsWith('.json'))
        .map(file => path.join(dir, file));
    } catch {
      return [];
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
}

module.exports = CoverageIntegrator;