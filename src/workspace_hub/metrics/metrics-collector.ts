/**
 * Metrics Collector - Parses test results, coverage data, and performance metrics
 */

import * as fs from 'fs-extra';
import * as path from 'path';
import { ValidationUtils } from '../utils/validation';
import { FileUtils } from '../utils/file-utils';
import {
  MetricsSnapshot,
  TestResult,
  CoverageData,
  CoverageFileData,
  PerformanceMetric,
  BaselineEngineError,
  ValidationError
} from '../types';

export interface MetricsCollectorConfig {
  parsers: {
    jest?: JestParserConfig;
    mocha?: MochaParserConfig;
    nyc?: NycParserConfig;
    istanbul?: IstanbulParserConfig;
    lcov?: LcovParserConfig;
    custom?: CustomParserConfig[];
  };
  performance: {
    enabled: boolean;
    sources: string[];
  };
}

export interface JestParserConfig {
  enabled: boolean;
  resultsPath: string;
  coveragePath?: string;
}

export interface MochaParserConfig {
  enabled: boolean;
  resultsPath: string;
  format: 'json' | 'tap' | 'xunit';
}

export interface NycParserConfig {
  enabled: boolean;
  coveragePath: string;
}

export interface IstanbulParserConfig {
  enabled: boolean;
  coveragePath: string;
}

export interface LcovParserConfig {
  enabled: boolean;
  lcovPath: string;
}

export interface CustomParserConfig {
  name: string;
  enabled: boolean;
  path: string;
  parser: string; // Path to custom parser module
}

export class MetricsCollector {
  private config: MetricsCollectorConfig;

  constructor(config: MetricsCollectorConfig) {
    this.config = config;
  }

  /**
   * Collects metrics from all configured sources
   */
  async collectMetrics(
    id: string,
    branch: string,
    commit: string,
    environment: string,
    version: string,
    metadata: Record<string, unknown> = {}
  ): Promise<MetricsSnapshot> {
    ValidationUtils.validateNonEmptyString(id, 'id');
    ValidationUtils.validateNonEmptyString(branch, 'branch');
    ValidationUtils.validateNonEmptyString(commit, 'commit');
    ValidationUtils.validateNonEmptyString(environment, 'environment');
    ValidationUtils.validateNonEmptyString(version, 'version');

    try {
      const [testResults, coverage, performance] = await Promise.all([
        this.collectTestResults(),
        this.collectCoverageData(),
        this.collectPerformanceMetrics()
      ]);

      const snapshot: MetricsSnapshot = {
        id,
        branch,
        commit,
        environment,
        version,
        previousVersion: undefined,
        tests: {
          results: testResults,
          summary: this.calculateTestSummary(testResults)
        },
        coverage,
        performance,
        metadata,
        created: new Date(),
        updated: new Date()
      };

      ValidationUtils.validateMetricsSnapshot(snapshot);
      return snapshot;
    } catch (error) {
      throw new BaselineEngineError(
        'Failed to collect metrics',
        'COLLECTION_ERROR',
        error
      );
    }
  }

  /**
   * Collects test results from configured parsers
   */
  private async collectTestResults(): Promise<TestResult[]> {
    const results: TestResult[] = [];

    // Jest parser
    if (this.config.parsers.jest?.enabled) {
      const jestResults = await this.parseJestResults(this.config.parsers.jest);
      results.push(...jestResults);
    }

    // Mocha parser
    if (this.config.parsers.mocha?.enabled) {
      const mochaResults = await this.parseMochaResults(this.config.parsers.mocha);
      results.push(...mochaResults);
    }

    // Custom parsers
    if (this.config.parsers.custom) {
      for (const customConfig of this.config.parsers.custom) {
        if (customConfig.enabled) {
          const customResults = await this.parseCustomResults(customConfig);
          results.push(...customResults);
        }
      }
    }

    return results;
  }

  /**
   * Collects coverage data from configured parsers
   */
  private async collectCoverageData(): Promise<CoverageData> {
    let coverage: CoverageData | null = null;

    // Jest coverage (if available)
    if (this.config.parsers.jest?.enabled && this.config.parsers.jest.coveragePath) {
      coverage = await this.parseJestCoverage(this.config.parsers.jest.coveragePath);
    }

    // NYC coverage
    if (!coverage && this.config.parsers.nyc?.enabled) {
      coverage = await this.parseNycCoverage(this.config.parsers.nyc);
    }

    // Istanbul coverage
    if (!coverage && this.config.parsers.istanbul?.enabled) {
      coverage = await this.parseIstanbulCoverage(this.config.parsers.istanbul);
    }

    // LCOV coverage
    if (!coverage && this.config.parsers.lcov?.enabled) {
      coverage = await this.parseLcovCoverage(this.config.parsers.lcov);
    }

    return coverage || this.createEmptyCoverage();
  }

  /**
   * Collects performance metrics
   */
  private async collectPerformanceMetrics(): Promise<PerformanceMetric[]> {
    if (!this.config.performance.enabled) {
      return [];
    }

    const metrics: PerformanceMetric[] = [];

    for (const source of this.config.performance.sources) {
      try {
        const sourceMetrics = await this.parsePerformanceMetrics(source);
        metrics.push(...sourceMetrics);
      } catch (error) {
        console.warn(`Failed to collect performance metrics from ${source}:`, error);
      }
    }

    return metrics;
  }

  /**
   * Jest parser implementation
   */
  private async parseJestResults(config: JestParserConfig): Promise<TestResult[]> {
    if (!(await FileUtils.fileExists(config.resultsPath))) {
      throw new ValidationError(`Jest results file not found: ${config.resultsPath}`);
    }

    const jestOutput = await FileUtils.readJsonFile<any>(config.resultsPath);
    const results: TestResult[] = [];

    if (jestOutput.testResults) {
      for (const testFile of jestOutput.testResults) {
        const suiteName = this.extractSuiteName(testFile.name);

        for (const assertionResult of testFile.assertionResults) {
          results.push({
            name: assertionResult.title,
            status: this.mapJestStatus(assertionResult.status),
            duration: assertionResult.duration || 0,
            suite: suiteName,
            error: assertionResult.failureMessages?.[0] || undefined
          });
        }
      }
    }

    return results;
  }

  /**
   * Jest coverage parser implementation
   */
  private async parseJestCoverage(coveragePath: string): Promise<CoverageData> {
    const coverageFile = path.join(coveragePath, 'coverage-summary.json');

    if (!(await FileUtils.fileExists(coverageFile))) {
      throw new ValidationError(`Jest coverage file not found: ${coverageFile}`);
    }

    const coverageSummary = await FileUtils.readJsonFile<any>(coverageFile);
    const files: CoverageFileData[] = [];

    // Parse file-level coverage
    for (const [filePath, fileCoverage] of Object.entries(coverageSummary)) {
      if (filePath !== 'total' && typeof fileCoverage === 'object') {
        const coverage = fileCoverage as any;
        files.push({
          path: filePath,
          lines: coverage.lines?.total || 0,
          covered: coverage.lines?.covered || 0,
          percentage: coverage.lines?.pct || 0,
          functions: coverage.functions?.total || 0,
          functionsCovered: coverage.functions?.covered || 0,
          branches: coverage.branches?.total || 0,
          branchesCovered: coverage.branches?.covered || 0
        });
      }
    }

    const total = coverageSummary.total || {};

    return {
      lines: {
        total: total.lines?.total || 0,
        covered: total.lines?.covered || 0,
        percentage: total.lines?.pct || 0
      },
      functions: {
        total: total.functions?.total || 0,
        covered: total.functions?.covered || 0,
        percentage: total.functions?.pct || 0
      },
      branches: {
        total: total.branches?.total || 0,
        covered: total.branches?.covered || 0,
        percentage: total.branches?.pct || 0
      },
      statements: {
        total: total.statements?.total || 0,
        covered: total.statements?.covered || 0,
        percentage: total.statements?.pct || 0
      },
      files
    };
  }

  /**
   * Mocha parser implementation
   */
  private async parseMochaResults(config: MochaParserConfig): Promise<TestResult[]> {
    if (!(await FileUtils.fileExists(config.resultsPath))) {
      throw new ValidationError(`Mocha results file not found: ${config.resultsPath}`);
    }

    const results: TestResult[] = [];

    switch (config.format) {
      case 'json':
        const mochaOutput = await FileUtils.readJsonFile<any>(config.resultsPath);
        results.push(...this.parseMochaJson(mochaOutput));
        break;

      case 'tap':
        const tapContent = await fs.readFile(config.resultsPath, 'utf-8');
        results.push(...this.parseMochaTap(tapContent));
        break;

      case 'xunit':
        const xunitContent = await fs.readFile(config.resultsPath, 'utf-8');
        results.push(...this.parseMochaXunit(xunitContent));
        break;
    }

    return results;
  }

  /**
   * NYC coverage parser implementation
   */
  private async parseNycCoverage(config: NycParserConfig): Promise<CoverageData> {
    const coverageFile = path.join(config.coveragePath, 'coverage-summary.json');

    if (!(await FileUtils.fileExists(coverageFile))) {
      throw new ValidationError(`NYC coverage file not found: ${coverageFile}`);
    }

    // NYC uses the same format as Jest/Istanbul
    return this.parseJestCoverage(config.coveragePath);
  }

  /**
   * Istanbul coverage parser implementation
   */
  private async parseIstanbulCoverage(config: IstanbulParserConfig): Promise<CoverageData> {
    return this.parseJestCoverage(config.coveragePath);
  }

  /**
   * LCOV coverage parser implementation
   */
  private async parseLcovCoverage(config: LcovParserConfig): Promise<CoverageData> {
    if (!(await FileUtils.fileExists(config.lcovPath))) {
      throw new ValidationError(`LCOV file not found: ${config.lcovPath}`);
    }

    const lcovContent = await fs.readFile(config.lcovPath, 'utf-8');
    return this.parseLcovContent(lcovContent);
  }

  /**
   * Custom parser implementation
   */
  private async parseCustomResults(config: CustomParserConfig): Promise<TestResult[]> {
    try {
      // Dynamic import of custom parser
      const parserModule = await import(config.parser);
      const parser = parserModule.default || parserModule;

      if (typeof parser.parse !== 'function') {
        throw new ValidationError(`Custom parser ${config.name} does not export a parse function`);
      }

      return await parser.parse(config.path);
    } catch (error) {
      throw new BaselineEngineError(
        `Failed to use custom parser ${config.name}`,
        'CUSTOM_PARSER_ERROR',
        error
      );
    }
  }

  /**
   * Performance metrics parser
   */
  private async parsePerformanceMetrics(source: string): Promise<PerformanceMetric[]> {
    if (!(await FileUtils.fileExists(source))) {
      return [];
    }

    const content = await FileUtils.readJsonFile<any>(source);
    const metrics: PerformanceMetric[] = [];

    // Handle different performance metric formats
    if (Array.isArray(content)) {
      for (const metric of content) {
        if (this.isValidPerformanceMetric(metric)) {
          metrics.push(metric);
        }
      }
    } else if (content.metrics && Array.isArray(content.metrics)) {
      for (const metric of content.metrics) {
        if (this.isValidPerformanceMetric(metric)) {
          metrics.push(metric);
        }
      }
    }

    return metrics;
  }

  /**
   * Helper methods
   */
  private calculateTestSummary(results: TestResult[]): {
    total: number;
    passed: number;
    failed: number;
    skipped: number;
    duration: number;
  } {
    return {
      total: results.length,
      passed: results.filter(r => r.status === 'pass').length,
      failed: results.filter(r => r.status === 'fail').length,
      skipped: results.filter(r => r.status === 'skip').length,
      duration: results.reduce((sum, r) => sum + r.duration, 0)
    };
  }

  private extractSuiteName(filePath: string): string {
    return path.basename(filePath, path.extname(filePath));
  }

  private mapJestStatus(status: string): 'pass' | 'fail' | 'skip' {
    switch (status) {
      case 'passed':
        return 'pass';
      case 'failed':
        return 'fail';
      case 'skipped':
      case 'pending':
        return 'skip';
      default:
        return 'fail';
    }
  }

  private parseMochaJson(mochaOutput: any): TestResult[] {
    const results: TestResult[] = [];

    if (mochaOutput.tests) {
      for (const test of mochaOutput.tests) {
        results.push({
          name: test.title,
          status: test.state === 'passed' ? 'pass' : test.state === 'failed' ? 'fail' : 'skip',
          duration: test.duration || 0,
          suite: test.parent?.title || 'unknown',
          error: test.err?.message || undefined
        });
      }
    }

    return results;
  }

  private parseMochaTap(tapContent: string): TestResult[] {
    // Basic TAP parser implementation
    const results: TestResult[] = [];
    const lines = tapContent.split('\n');

    for (const line of lines) {
      const match = line.match(/^(not )?ok (\d+) (.+)$/);
      if (match) {
        results.push({
          name: match[3] || 'Unknown test',
          status: match[1] ? 'fail' : 'pass',
          duration: 0,
          suite: 'tap'
        });
      }
    }

    return results;
  }

  private parseMochaXunit(xunitContent: string): TestResult[] {
    // Basic XUnit XML parser implementation
    const results: TestResult[] = [];

    // Simple regex-based parsing (in production, use a proper XML parser)
    const testcaseRegex = /<testcase[^>]+name="([^"]+)"[^>]*(?:time="([^"]+)")?[^>]*(?:\/>|>.*?<\/testcase>)/g;
    let match;

    while ((match = testcaseRegex.exec(xunitContent)) !== null) {
      const name = match[1];
      const duration = parseFloat(match[2] || '0') * 1000; // Convert to ms
      const hasFailure = match[0].includes('<failure') || match[0].includes('<error');

      results.push({
        name: name || 'Unknown test',
        status: hasFailure ? 'fail' : 'pass',
        duration,
        suite: 'xunit'
      });
    }

    return results;
  }

  private parseLcovContent(content: string): CoverageData {
    const files: CoverageFileData[] = [];
    const sections = content.split('end_of_record');

    let totalLines = 0;
    let totalCovered = 0;
    let totalFunctions = 0;
    let totalFunctionsCovered = 0;
    let totalBranches = 0;
    let totalBranchesCovered = 0;

    for (const section of sections) {
      if (!section.trim()) continue;

      const lines = section.split('\n');
      let filePath = '';
      let linesFound = 0;
      let linesHit = 0;
      let functionsFound = 0;
      let functionsHit = 0;
      let branchesFound = 0;
      let branchesHit = 0;

      for (const line of lines) {
        const trimmed = line.trim();
        if (trimmed.startsWith('SF:')) {
          filePath = trimmed.substring(3);
        } else if (trimmed.startsWith('LF:')) {
          linesFound = parseInt(trimmed.substring(3), 10);
        } else if (trimmed.startsWith('LH:')) {
          linesHit = parseInt(trimmed.substring(3), 10);
        } else if (trimmed.startsWith('FNF:')) {
          functionsFound = parseInt(trimmed.substring(4), 10);
        } else if (trimmed.startsWith('FNH:')) {
          functionsHit = parseInt(trimmed.substring(4), 10);
        } else if (trimmed.startsWith('BRF:')) {
          branchesFound = parseInt(trimmed.substring(4), 10);
        } else if (trimmed.startsWith('BRH:')) {
          branchesHit = parseInt(trimmed.substring(4), 10);
        }
      }

      if (filePath) {
        files.push({
          path: filePath,
          lines: linesFound,
          covered: linesHit,
          percentage: linesFound > 0 ? (linesHit / linesFound) * 100 : 0,
          functions: functionsFound,
          functionsCovered: functionsHit,
          branches: branchesFound,
          branchesCovered: branchesHit
        });

        totalLines += linesFound;
        totalCovered += linesHit;
        totalFunctions += functionsFound;
        totalFunctionsCovered += functionsHit;
        totalBranches += branchesFound;
        totalBranchesCovered += branchesHit;
      }
    }

    return {
      lines: {
        total: totalLines,
        covered: totalCovered,
        percentage: totalLines > 0 ? (totalCovered / totalLines) * 100 : 0
      },
      functions: {
        total: totalFunctions,
        covered: totalFunctionsCovered,
        percentage: totalFunctions > 0 ? (totalFunctionsCovered / totalFunctions) * 100 : 0
      },
      branches: {
        total: totalBranches,
        covered: totalBranchesCovered,
        percentage: totalBranches > 0 ? (totalBranchesCovered / totalBranches) * 100 : 0
      },
      statements: {
        total: totalLines, // LCOV doesn't distinguish statements from lines
        covered: totalCovered,
        percentage: totalLines > 0 ? (totalCovered / totalLines) * 100 : 0
      },
      files
    };
  }

  private createEmptyCoverage(): CoverageData {
    return {
      lines: { total: 0, covered: 0, percentage: 0 },
      functions: { total: 0, covered: 0, percentage: 0 },
      branches: { total: 0, covered: 0, percentage: 0 },
      statements: { total: 0, covered: 0, percentage: 0 },
      files: []
    };
  }

  private isValidPerformanceMetric(metric: any): metric is PerformanceMetric {
    return (
      typeof metric === 'object' &&
      typeof metric.name === 'string' &&
      typeof metric.value === 'number' &&
      typeof metric.unit === 'string' &&
      ['memory', 'cpu', 'network', 'disk', 'custom'].includes(metric.category)
    );
  }
}