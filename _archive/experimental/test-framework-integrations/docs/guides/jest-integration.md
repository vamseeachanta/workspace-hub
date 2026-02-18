# Jest Integration Guide

Complete guide for integrating Test Framework Integrations with Jest, the popular JavaScript testing framework.

## 📚 Overview

Jest is a delightful JavaScript testing framework with a focus on simplicity. This guide covers:
- **Installation and Setup**: Getting Jest working with Test Framework Integrations
- **Configuration**: Optimizing Jest for baseline tracking and coverage
- **Advanced Features**: Custom reporters, parallel execution, and performance monitoring
- **Best Practices**: Tips for optimal Jest integration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Jest and Test Framework Integrations
npm install --save-dev jest test-framework-integrations

# Optional: TypeScript support
npm install --save-dev @types/jest ts-jest

# Optional: Additional Jest utilities
npm install --save-dev jest-environment-jsdom @jest/globals
```

### 2. Basic Configuration

Create or update your `jest.config.js`:

```javascript
// jest.config.js
module.exports = {
  // Test environment
  testEnvironment: 'node', // or 'jsdom' for browser-like environment

  // Test file patterns
  testMatch: [
    '**/__tests__/**/*.(js|jsx|ts|tsx)',
    '**/*.(test|spec).(js|jsx|ts|tsx)'
  ],

  // Coverage configuration
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.js'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html', 'json'],

  // Test Framework Integrations setup
  setupFilesAfterEnv: ['<rootDir>/test-framework-integration.setup.js'],

  // Performance optimization
  maxWorkers: '50%',
  cache: true,
  clearMocks: true,
  restoreMocks: true
};
```

### 3. Setup Integration

Create `test-framework-integration.setup.js`:

```javascript
// test-framework-integration.setup.js
const TestFrameworkIntegrations = require('test-framework-integrations');

// Global test integration instance
global.testIntegration = new TestFrameworkIntegrations({
  framework: 'jest',
  coverage: true,
  profiling: true,
  baseline: process.env.BASELINE_FILE || './baseline.json',
  reporter: 'console'
});

// Initialize before all tests
beforeAll(async () => {
  await global.testIntegration.initialize();
});

// Cleanup after all tests
afterAll(async () => {
  if (global.testIntegration) {
    await global.testIntegration.stopTests();
  }
});
```

### 4. Update Package.json Scripts

```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:integration": "node -e \"require('./run-integration-tests.js')()\"",
    "test:baseline": "BASELINE_FILE=./baseline.json jest",
    "test:performance": "jest --detectOpenHandles --forceExit"
  }
}
```

## 🔧 Advanced Configuration

### Custom Jest Configuration with Integration

```javascript
// jest.config.js
const TestFrameworkIntegrations = require('test-framework-integrations');

module.exports = async () => {
  // Initialize integration system
  const integration = new TestFrameworkIntegrations({
    framework: 'jest',
    autoDetect: false,
    coverage: {
      enabled: true,
      threshold: {
        statements: 90,
        branches: 85,
        functions: 90,
        lines: 90
      }
    },
    profiling: {
      enabled: true,
      memoryInterval: 100,
      detectLeaks: true
    }
  });

  await integration.initialize();

  return {
    // Basic Jest configuration
    testEnvironment: 'node',
    setupFilesAfterEnv: ['<rootDir>/jest.setup.js'],

    // Test patterns
    testMatch: [
      '**/__tests__/**/*.test.{js,jsx,ts,tsx}',
      '**/*.{test,spec}.{js,jsx,ts,tsx}'
    ],
    testPathIgnorePatterns: [
      '/node_modules/',
      '/build/',
      '/coverage/'
    ],

    // Module resolution
    moduleNameMapping: {
      '^@/(.*)$': '<rootDir>/src/$1',
      '\\.(css|less|scss|sass)$': 'identity-obj-proxy'
    },

    // Transform configuration
    transform: {
      '^.+\\.(js|jsx|ts|tsx)$': 'babel-jest',
      '^.+\\.css$': 'jest-css-modules-transform'
    },

    // Coverage configuration
    collectCoverage: process.env.CI === 'true',
    collectCoverageFrom: [
      'src/**/*.{js,jsx,ts,tsx}',
      '!src/**/*.d.ts',
      '!src/**/*.stories.{js,jsx,ts,tsx}',
      '!src/index.{js,jsx,ts,tsx}'
    ],
    coverageDirectory: 'coverage',
    coverageReporters: process.env.CI === 'true'
      ? ['json', 'lcov', 'text-summary']
      : ['text', 'html'],
    coverageThreshold: {
      global: {
        statements: 90,
        branches: 85,
        functions: 90,
        lines: 90
      }
    },

    // Performance and debugging
    maxWorkers: process.env.CI === 'true' ? 2 : '50%',
    cache: true,
    cacheDirectory: '<rootDir>/.jest-cache',
    clearMocks: true,
    restoreMocks: true,
    resetMocks: false,

    // Timeouts
    testTimeout: 30000,

    // Reporters
    reporters: [
      'default',
      ['jest-junit', {
        outputDirectory: 'test-results',
        outputName: 'jest-results.xml'
      }],
      // Custom integration reporter
      '<rootDir>/jest-integration-reporter.js'
    ],

    // Global variables
    globals: {
      TEST_INTEGRATION_ENABLED: true,
      BASELINE_TRACKING: process.env.BASELINE_TRACKING || 'true'
    }
  };
};
```

### Custom Jest Reporter

Create `jest-integration-reporter.js`:

```javascript
// jest-integration-reporter.js
const TestFrameworkIntegrations = require('test-framework-integrations');

class JestIntegrationReporter {
  constructor(globalConfig, options) {
    this.globalConfig = globalConfig;
    this.options = options;
    this.integration = null;
  }

  async onRunStart(results, options) {
    // Initialize integration if not already done
    if (!this.integration) {
      this.integration = new TestFrameworkIntegrations({
        framework: 'jest',
        coverage: true,
        profiling: true,
        baseline: process.env.BASELINE_FILE,
        reporter: 'console'
      });
      await this.integration.initialize();
    }

    console.log('🧪 Jest Integration Reporter - Test Run Started');
    console.log(`📁 Running ${results.numTotalTestSuites} test suites`);
  }

  onTestStart(test) {
    // Mark test start for profiling
    if (this.integration) {
      this.integration.emit('testStarted', {
        testName: test.path,
        suite: test.context.config.displayName || 'default'
      });
    }
  }

  onTestResult(test, testResult) {
    // Process individual test results
    testResult.testResults.forEach(result => {
      if (this.integration) {
        this.integration.emit('testCompleted', {
          testName: result.fullName,
          status: this._mapJestStatus(result.status),
          duration: result.duration,
          file: test.path,
          error: result.failureDetails?.[0]?.message
        });
      }
    });
  }

  async onRunComplete(contexts, results) {
    console.log('\n📊 Jest Integration Results:');
    console.log(`✅ Passed: ${results.numPassedTests}`);
    console.log(`❌ Failed: ${results.numFailedTests}`);
    console.log(`⏸️  Skipped: ${results.numPendingTests}`);
    console.log(`⏱️  Duration: ${results.runtime}ms`);

    if (this.integration) {
      // Convert Jest results to integration format
      const integrationResults = this._convertJestResults(results);

      // Save baseline if requested
      if (process.env.SAVE_BASELINE === 'true') {
        await this.integration.saveBaseline(integrationResults, 'latest');
        console.log('💾 Baseline saved');
      }

      // Compare with baseline if available
      if (process.env.BASELINE_FILE) {
        try {
          const fs = require('fs');
          const baseline = JSON.parse(fs.readFileSync(process.env.BASELINE_FILE, 'utf8'));
          const comparison = this.integration.compareWithBaseline(baseline);

          if (comparison) {
            this._reportBaselineComparison(comparison);
          }
        } catch (error) {
          console.log('⚠️  Could not load baseline for comparison');
        }
      }
    }
  }

  _mapJestStatus(jestStatus) {
    const statusMap = {
      'passed': 'passed',
      'failed': 'failed',
      'skipped': 'skipped',
      'pending': 'pending',
      'disabled': 'skipped'
    };
    return statusMap[jestStatus] || 'unknown';
  }

  _convertJestResults(jestResults) {
    const tests = [];

    jestResults.testResults.forEach(suiteResult => {
      suiteResult.testResults.forEach(testResult => {
        tests.push({
          name: testResult.fullName,
          suite: suiteResult.testFilePath,
          status: this._mapJestStatus(testResult.status),
          duration: testResult.duration,
          file: suiteResult.testFilePath,
          error: testResult.failureDetails?.[0]?.message
        });
      });
    });

    return {
      framework: {
        name: 'jest',
        version: require('jest/package.json').version,
        adapter: 'JestAdapter'
      },
      tests,
      summary: {
        total: jestResults.numTotalTests,
        passed: jestResults.numPassedTests,
        failed: jestResults.numFailedTests,
        skipped: jestResults.numPendingTests,
        pending: 0,
        duration: jestResults.runtime,
        success: jestResults.numFailedTests === 0
      },
      timestamp: new Date().toISOString()
    };
  }

  _reportBaselineComparison(comparison) {
    console.log('\n📈 Baseline Comparison:');

    if (comparison.testsAdded.length > 0) {
      console.log(`➕ Added tests: ${comparison.testsAdded.length}`);
    }

    if (comparison.testsRemoved.length > 0) {
      console.log(`➖ Removed tests: ${comparison.testsRemoved.length}`);
    }

    if (comparison.testsChanged.length > 0) {
      console.log(`🔄 Changed tests: ${comparison.testsChanged.length}`);
    }

    if (comparison.performance.slower.length > 0) {
      console.log('🐌 Performance regressions:');
      comparison.performance.slower.slice(0, 3).forEach(test => {
        console.log(`  ${test.name}: +${test.regression}ms`);
      });
    }

    if (comparison.performance.faster.length > 0) {
      console.log('🚀 Performance improvements:');
      comparison.performance.faster.slice(0, 3).forEach(test => {
        console.log(`  ${test.name}: -${test.improvement}ms`);
      });
    }
  }
}

module.exports = JestIntegrationReporter;
```

## 🧪 Test Examples

### Basic Test with Integration

```javascript
// src/utils.test.js
describe('Utils', () => {
  test('should calculate sum correctly', () => {
    const result = add(2, 3);
    expect(result).toBe(5);
  });

  test('should handle edge cases', async () => {
    // This test will be tracked by the integration system
    const result = await processLargeDataset();
    expect(result).toBeDefined();
  });
});
```

### Integration-Aware Test Suite

```javascript
// src/components/Button.test.js
import { render, fireEvent, screen } from '@testing-library/react';
import { Button } from './Button';

describe('Button Component', () => {
  beforeEach(() => {
    // Mark test suite start for profiling
    if (global.testIntegration) {
      global.testIntegration.emit('testStarted', {
        testName: 'Button Component',
        suite: 'components'
      });
    }
  });

  test('renders button with text', () => {
    render(<Button>Click me</Button>);
    expect(screen.getByText('Click me')).toBeInTheDocument();
  });

  test('handles click events', () => {
    const handleClick = jest.fn();
    render(<Button onClick={handleClick}>Click me</Button>);

    fireEvent.click(screen.getByText('Click me'));
    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  test('applies custom className', () => {
    render(<Button className="custom-button">Test</Button>);
    expect(screen.getByText('Test')).toHaveClass('custom-button');
  });
});
```

### Performance-Aware Test

```javascript
// src/api/users.test.js
import { fetchUsers, processUsers } from './users';

describe('User API', () => {
  test('should fetch users efficiently', async () => {
    const startTime = performance.now();

    const users = await fetchUsers();

    const endTime = performance.now();
    const duration = endTime - startTime;

    // Performance assertion
    expect(duration).toBeLessThan(1000); // Should complete within 1 second
    expect(users).toHaveLength(10);
  });

  test('should process large user datasets', async () => {
    // Generate large dataset for performance testing
    const largeUserSet = Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      name: `User ${i}`,
      email: `user${i}@example.com`
    }));

    const startMemory = process.memoryUsage();

    const result = await processUsers(largeUserSet);

    const endMemory = process.memoryUsage();
    const memoryDelta = endMemory.heapUsed - startMemory.heapUsed;

    // Memory usage assertion
    expect(memoryDelta).toBeLessThan(50 * 1024 * 1024); // Less than 50MB
    expect(result).toBeDefined();
  });
});
```

## 🔍 Coverage Integration

### Advanced Coverage Configuration

```javascript
// jest.config.js - Coverage focused configuration
module.exports = {
  // Coverage collection
  collectCoverage: true,
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/**/*.stories.{js,jsx,ts,tsx}',
    '!src/**/__tests__/**',
    '!src/index.{js,jsx,ts,tsx}'
  ],

  // Coverage directory and reporters
  coverageDirectory: 'coverage',
  coverageReporters: [
    'text',           // Console output
    'html',           // HTML reports
    'lcov',           // LCOV format for CI
    'json',           // JSON format for integration
    'json-summary',   // Summary JSON
    'cobertura'       // Cobertura XML for some CI systems
  ],

  // Coverage thresholds
  coverageThreshold: {
    global: {
      statements: 90,
      branches: 85,
      functions: 90,
      lines: 90
    },
    './src/components/': {
      statements: 95,
      branches: 90,
      functions: 95,
      lines: 95
    },
    './src/utils/': {
      statements: 100,
      branches: 95,
      functions: 100,
      lines: 100
    }
  },

  // Coverage providers
  coverageProvider: 'v8', // or 'babel' for older Node versions

  // Skip coverage for test files
  testPathIgnorePatterns: [
    '/node_modules/',
    '/coverage/'
  ]
};
```

### Custom Coverage Integration

```javascript
// coverage-integration.js
const TestFrameworkIntegrations = require('test-framework-integrations');
const fs = require('fs').promises;
const path = require('path');

class CoverageIntegration {
  constructor() {
    this.integration = new TestFrameworkIntegrations({
      framework: 'jest',
      coverage: true
    });
  }

  async processCoverageReport() {
    try {
      // Read Jest coverage report
      const coveragePath = path.join(process.cwd(), 'coverage/coverage-final.json');
      const coverageData = JSON.parse(await fs.readFile(coveragePath, 'utf8'));

      // Convert to integration format
      const integrationCoverage = this.convertJestCoverage(coverageData);

      // Save coverage baseline
      await this.integration.coverage.saveBaseline(integrationCoverage, 'latest');

      // Check coverage thresholds
      const thresholdCheck = this.integration.coverage.checkThresholds(integrationCoverage);

      if (!thresholdCheck.passed) {
        console.error('Coverage thresholds not met:');
        thresholdCheck.failures.forEach(failure => {
          console.error(`  ${failure.metric}: ${failure.actual}% (required: ${failure.threshold}%)`);
        });
        process.exit(1);
      }

      console.log('✅ Coverage integration completed successfully');

    } catch (error) {
      console.error('Coverage integration failed:', error);
      process.exit(1);
    }
  }

  convertJestCoverage(jestCoverage) {
    const files = [];
    let totalStatements = 0;
    let coveredStatements = 0;
    let totalBranches = 0;
    let coveredBranches = 0;
    let totalFunctions = 0;
    let coveredFunctions = 0;
    let totalLines = 0;
    let coveredLines = 0;

    for (const [filePath, fileData] of Object.entries(jestCoverage)) {
      const file = {
        path: filePath,
        statements: {
          total: Object.keys(fileData.s).length,
          covered: Object.values(fileData.s).filter(count => count > 0).length,
          percentage: 0
        },
        branches: {
          total: Object.keys(fileData.b).length,
          covered: Object.values(fileData.b).filter(branches =>
            branches.some(count => count > 0)
          ).length,
          percentage: 0
        },
        functions: {
          total: Object.keys(fileData.f).length,
          covered: Object.values(fileData.f).filter(count => count > 0).length,
          percentage: 0
        },
        lines: {
          total: Object.keys(fileData.l).length,
          covered: Object.values(fileData.l).filter(count => count > 0).length,
          percentage: 0
        }
      };

      // Calculate percentages
      file.statements.percentage = file.statements.total > 0
        ? (file.statements.covered / file.statements.total) * 100
        : 100;
      file.branches.percentage = file.branches.total > 0
        ? (file.branches.covered / file.branches.total) * 100
        : 100;
      file.functions.percentage = file.functions.total > 0
        ? (file.functions.covered / file.functions.total) * 100
        : 100;
      file.lines.percentage = file.lines.total > 0
        ? (file.lines.covered / file.lines.total) * 100
        : 100;

      files.push(file);

      // Aggregate totals
      totalStatements += file.statements.total;
      coveredStatements += file.statements.covered;
      totalBranches += file.branches.total;
      coveredBranches += file.branches.covered;
      totalFunctions += file.functions.total;
      coveredFunctions += file.functions.covered;
      totalLines += file.lines.total;
      coveredLines += file.lines.covered;
    }

    return {
      total: totalStatements > 0 ? (coveredStatements / totalStatements) * 100 : 100,
      statements: totalStatements > 0 ? (coveredStatements / totalStatements) * 100 : 100,
      branches: totalBranches > 0 ? (coveredBranches / totalBranches) * 100 : 100,
      functions: totalFunctions > 0 ? (coveredFunctions / totalFunctions) * 100 : 100,
      lines: totalLines > 0 ? (coveredLines / totalLines) * 100 : 100,
      files
    };
  }
}

// Usage in package.json script
if (require.main === module) {
  const integration = new CoverageIntegration();
  integration.processCoverageReport();
}

module.exports = CoverageIntegration;
```

## ⚡ Performance Optimization

### Jest Performance Configuration

```javascript
// jest.config.performance.js
module.exports = {
  // Worker configuration
  maxWorkers: process.env.CI ? 2 : '50%',
  workerIdleMemoryLimit: '512MB',

  // Cache configuration
  cache: true,
  cacheDirectory: '<rootDir>/.jest-cache',

  // Module and transform optimizations
  transformIgnorePatterns: [
    'node_modules/(?!(some-esm-package|another-esm-package)/)'
  ],

  // Reduce filesystem operations
  watchPathIgnorePatterns: [
    '/node_modules/',
    '/coverage/',
    '/build/',
    '/.git/'
  ],

  // Memory management
  clearMocks: true,
  restoreMocks: true,
  resetMocks: false,

  // Test execution optimizations
  testTimeout: 10000,
  detectOpenHandles: false,
  forceExit: process.env.CI === 'true',

  // Coverage optimizations
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts'
  ],
  coverageProvider: 'v8' // Faster than babel
};
```

### Performance Monitoring Integration

```javascript
// performance-monitor.js
const TestFrameworkIntegrations = require('test-framework-integrations');

class JestPerformanceMonitor {
  constructor() {
    this.integration = new TestFrameworkIntegrations({
      framework: 'jest',
      profiling: {
        enabled: true,
        memoryInterval: 100,
        detectLeaks: true,
        enableCpuProfiling: false
      }
    });
    this.testMetrics = new Map();
  }

  async initialize() {
    await this.integration.initialize();
    this.startMonitoring();
  }

  startMonitoring() {
    // Monitor memory usage
    const memoryInterval = setInterval(() => {
      const usage = process.memoryUsage();
      this.integration.profiler.recordMemoryUsage(usage);
    }, 100);

    // Cleanup on process exit
    process.on('exit', () => {
      clearInterval(memoryInterval);
    });
  }

  markTestStart(testName) {
    this.testMetrics.set(testName, {
      startTime: performance.now(),
      startMemory: process.memoryUsage()
    });
  }

  markTestEnd(testName, status) {
    const metrics = this.testMetrics.get(testName);
    if (metrics) {
      const endTime = performance.now();
      const endMemory = process.memoryUsage();

      const testResult = {
        name: testName,
        status,
        duration: endTime - metrics.startTime,
        memoryDelta: {
          heapUsed: endMemory.heapUsed - metrics.startMemory.heapUsed,
          heapTotal: endMemory.heapTotal - metrics.startMemory.heapTotal
        }
      };

      // Check for performance issues
      this.checkPerformanceIssues(testResult);

      this.testMetrics.delete(testName);
    }
  }

  checkPerformanceIssues(testResult) {
    const { name, duration, memoryDelta } = testResult;

    // Check for slow tests
    if (duration > 5000) {
      console.warn(`⚠️  Slow test detected: ${name} took ${duration.toFixed(2)}ms`);
    }

    // Check for memory leaks
    if (memoryDelta.heapUsed > 10 * 1024 * 1024) { // 10MB
      console.warn(`⚠️  Potential memory leak: ${name} used ${(memoryDelta.heapUsed / 1024 / 1024).toFixed(2)}MB`);
    }
  }

  async generateReport() {
    const bottlenecks = await this.integration.analyzeBottlenecks();

    console.log('\n🔍 Performance Analysis:');

    if (bottlenecks.slowTests.length > 0) {
      console.log('\n🐌 Slowest Tests:');
      bottlenecks.slowTests.slice(0, 5).forEach((test, i) => {
        console.log(`  ${i + 1}. ${test.name}: ${test.duration.toFixed(2)}ms`);
      });
    }

    if (bottlenecks.recommendations.length > 0) {
      console.log('\n💡 Recommendations:');
      bottlenecks.recommendations.slice(0, 3).forEach((rec, i) => {
        console.log(`  ${i + 1}. [${rec.severity.toUpperCase()}] ${rec.message}`);
      });
    }
  }
}

module.exports = JestPerformanceMonitor;
```

## 🚀 CI/CD Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/jest-integration.yml
name: Jest Integration Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]

    steps:
    - uses: actions/checkout@v3

    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run Jest with Integration
      run: npm run test:integration
      env:
        CI: true
        BASELINE_FILE: ./baselines/main.json
        SAVE_BASELINE: ${{ github.ref == 'refs/heads/main' }}

    - name: Upload coverage reports
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info
        flags: jest
        name: codecov-umbrella

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: jest-results-${{ matrix.node-version }}
        path: |
          test-results/
          coverage/
          baselines/

    - name: Comment PR with results
      uses: actions/github-script@v6
      if: github.event_name == 'pull_request'
      with:
        script: |
          const fs = require('fs');
          try {
            const results = JSON.parse(fs.readFileSync('test-results/integration-summary.json', 'utf8'));
            const comment = `
            ## 🧪 Jest Integration Results

            - **Tests**: ${results.summary.passed}/${results.summary.total} passed
            - **Coverage**: ${results.coverage?.total.toFixed(2)}%
            - **Duration**: ${results.summary.duration}ms

            ${results.baseline ? `
            ### 📊 Baseline Comparison
            - Performance regressions: ${results.baseline.performance.slower.length}
            - Performance improvements: ${results.baseline.performance.faster.length}
            - Coverage change: ${results.baseline.coverage.change > 0 ? '+' : ''}${results.baseline.coverage.change.toFixed(2)}%
            ` : ''}
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
          } catch (error) {
            console.log('Could not post results comment:', error);
          }
```

### Integration Test Script

```javascript
// run-integration-tests.js
const TestFrameworkIntegrations = require('test-framework-integrations');
const { execSync } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

async function runIntegrationTests() {
  console.log('🧪 Starting Jest Integration Tests\n');

  const integration = new TestFrameworkIntegrations({
    framework: 'jest',
    coverage: true,
    profiling: true,
    baseline: process.env.BASELINE_FILE,
    reporter: ['console', 'json']
  });

  try {
    // Initialize integration
    await integration.initialize();

    // Run Jest tests
    console.log('🚀 Running Jest tests...');
    const jestResults = execSync('jest --json --coverage', {
      encoding: 'utf8',
      stdio: ['inherit', 'pipe', 'inherit']
    });

    const jestData = JSON.parse(jestResults);

    // Process results through integration
    const integrationResults = await integration.processJestResults(jestData);

    // Generate coverage reports
    if (integrationResults.coverage) {
      console.log('📊 Generating coverage reports...');
      await integration.generateCoverageReports('ci-run');
    }

    // Save baseline if on main branch
    if (process.env.SAVE_BASELINE === 'true') {
      console.log('💾 Saving baseline...');
      await integration.saveBaseline(integrationResults, 'latest');
    }

    // Compare with baseline
    if (process.env.BASELINE_FILE) {
      console.log('📈 Comparing with baseline...');
      try {
        const baselineData = JSON.parse(
          await fs.readFile(process.env.BASELINE_FILE, 'utf8')
        );
        const comparison = integration.compareWithBaseline(baselineData);
        integrationResults.baseline = comparison;
      } catch (error) {
        console.log('⚠️  Could not load baseline for comparison');
      }
    }

    // Save summary for CI
    const summaryPath = path.join(process.cwd(), 'test-results', 'integration-summary.json');
    await fs.mkdir(path.dirname(summaryPath), { recursive: true });
    await fs.writeFile(summaryPath, JSON.stringify(integrationResults, null, 2));

    // Print summary
    console.log('\n📊 Integration Test Summary:');
    console.log(`Tests: ${integrationResults.summary.passed}/${integrationResults.summary.total}`);
    console.log(`Coverage: ${integrationResults.coverage?.total.toFixed(2)}%`);
    console.log(`Duration: ${integrationResults.summary.duration}ms`);

    if (integrationResults.baseline) {
      console.log('\n📈 Baseline Comparison:');
      if (integrationResults.baseline.performance.slower.length > 0) {
        console.log(`⚠️  ${integrationResults.baseline.performance.slower.length} performance regressions`);
      }
      if (integrationResults.baseline.performance.faster.length > 0) {
        console.log(`🚀 ${integrationResults.baseline.performance.faster.length} performance improvements`);
      }
    }

    // Exit with appropriate code
    if (integrationResults.summary.failed > 0) {
      console.log('\n❌ Tests failed');
      process.exit(1);
    } else {
      console.log('\n✅ All tests passed');
    }

  } catch (error) {
    console.error('❌ Integration test failed:', error);
    process.exit(1);
  }
}

module.exports = runIntegrationTests;

// Run if called directly
if (require.main === module) {
  runIntegrationTests();
}
```

## 🔧 Troubleshooting

### Common Issues

#### Issue: Jest Tests Not Being Tracked

**Problem**: Tests run but don't appear in integration results.

**Solution**:
```javascript
// Ensure proper setup in jest.config.js
module.exports = {
  setupFilesAfterEnv: ['<rootDir>/test-framework-integration.setup.js'],
  // ... other config
};

// In test-framework-integration.setup.js
global.testIntegration = new TestFrameworkIntegrations({
  framework: 'jest',
  autoDetect: false // Explicitly set framework
});
```

#### Issue: Coverage Reports Not Generated

**Problem**: Coverage collection enabled but no reports generated.

**Solution**:
```javascript
// jest.config.js
module.exports = {
  collectCoverage: true,
  coverageReporters: ['json', 'lcov', 'text', 'html'],
  coverageDirectory: 'coverage',
  // Ensure files are included
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts'
  ]
};
```

#### Issue: Performance Profiling Not Working

**Problem**: Profiling enabled but no performance data collected.

**Solution**:
```javascript
// Enable profiling with proper configuration
const integration = new TestFrameworkIntegrations({
  framework: 'jest',
  profiling: {
    enabled: true,
    memoryInterval: 100,
    detectLeaks: true
  }
});
```

#### Issue: Memory Leaks in Tests

**Problem**: Tests cause memory leaks that affect subsequent tests.

**Solution**:
```javascript
// jest.config.js
module.exports = {
  clearMocks: true,
  restoreMocks: true,
  resetMocks: false,
  // Run each test file in isolation
  maxWorkers: 1,
  // Detect open handles
  detectOpenHandles: true,
  forceExit: true
};

// In test files, ensure cleanup
afterEach(() => {
  jest.clearAllMocks();
  // Clean up any subscriptions, timers, etc.
});
```

### Performance Tips

1. **Use V8 Coverage Provider**: Faster than Babel for modern Node.js versions
2. **Optimize Workers**: Use `maxWorkers: '50%'` for better resource utilization
3. **Cache Configuration**: Enable Jest cache for faster subsequent runs
4. **Selective Coverage**: Only collect coverage for source files, not tests
5. **Transform Optimization**: Use `transformIgnorePatterns` to skip unnecessary transforms

### Debugging

```javascript
// Enable debug logging
process.env.DEBUG = 'test-framework-integrations:*';

// Or use Jest's debug options
// jest --verbose --detectOpenHandles --runInBand
```

## 📚 Additional Resources

- **[Jest Documentation](https://jestjs.io/docs/getting-started)** - Official Jest documentation
- **[Jest Configuration](https://jestjs.io/docs/configuration)** - Complete configuration reference
- **[Testing Library](https://testing-library.com/)** - Simple and complete testing utilities
- **[Jest Community](https://github.com/jest-community)** - Community-maintained Jest packages