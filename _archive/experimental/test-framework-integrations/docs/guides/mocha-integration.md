# Mocha Integration Guide

Complete guide for integrating Test Framework Integrations with Mocha, the flexible JavaScript testing framework.

## 📚 Overview

Mocha is a feature-rich JavaScript test framework running on Node.js and in the browser. This guide covers:
- **Installation and Setup**: Getting Mocha working with Test Framework Integrations
- **Configuration**: Optimizing Mocha for baseline tracking and coverage
- **Advanced Features**: Custom reporters, hooks, and performance monitoring
- **Best Practices**: Tips for optimal Mocha integration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Mocha and Test Framework Integrations
npm install --save-dev mocha test-framework-integrations

# Install assertion library (choose one)
npm install --save-dev chai  # BDD/TDD assertion library
# or
npm install --save-dev should  # Expressive assertion library
# or use Node.js built-in assert

# Optional: Coverage and utilities
npm install --save-dev nyc c8 mocha-multi-reporters
```

### 2. Basic Configuration

Create `.mocharc.json`:

```json
{
  "require": ["test-framework-integration/mocha-setup"],
  "reporter": "spec",
  "timeout": 30000,
  "recursive": true,
  "spec": "test/**/*.test.js",
  "ignore": ["test/fixtures/**/*.js"],
  "exit": true,
  "bail": false,
  "grep": "",
  "invert": false,
  "full-trace": false,
  "inline-diffs": false,
  "reporter-options": {
    "maxDiffSize": 8192
  }
}
```

Or using JavaScript configuration `.mocharc.js`:

```javascript
// .mocharc.js
module.exports = {
  require: ['test-framework-integration/mocha-setup'],
  reporter: 'spec',
  timeout: 30000,
  recursive: true,
  spec: 'test/**/*.test.js',
  ignore: ['test/fixtures/**/*.js'],
  exit: true,

  // Custom setup
  setup: function() {
    // Custom initialization logic
  }
};
```

### 3. Setup Integration

Create `test-framework-integration/mocha-setup.js`:

```javascript
// test-framework-integration/mocha-setup.js
const TestFrameworkIntegrations = require('test-framework-integrations');
const chai = require('chai');

// Global test integration instance
global.testIntegration = new TestFrameworkIntegrations({
  framework: 'mocha',
  coverage: true,
  profiling: true,
  baseline: process.env.BASELINE_FILE || './baseline.json',
  reporter: 'console'
});

// Set up chai expectations globally
global.expect = chai.expect;
global.should = chai.should();

// Initialize integration before all tests
before(async function() {
  this.timeout(10000); // Allow time for initialization
  await global.testIntegration.initialize();
});

// Cleanup after all tests
after(async function() {
  if (global.testIntegration) {
    await global.testIntegration.stopTests();
  }
});

// Hook into Mocha events for tracking
beforeEach(function() {
  if (global.testIntegration) {
    global.testIntegration.emit('testStarted', {
      testName: this.currentTest.title,
      suite: this.currentTest.parent.title
    });
  }
});

afterEach(function() {
  if (global.testIntegration) {
    global.testIntegration.emit('testCompleted', {
      testName: this.currentTest.title,
      suite: this.currentTest.parent.title,
      status: this.currentTest.state,
      duration: this.currentTest.duration,
      error: this.currentTest.err?.message
    });
  }
});
```

### 4. Update Package.json Scripts

```json
{
  "scripts": {
    "test": "mocha",
    "test:watch": "mocha --watch",
    "test:coverage": "nyc mocha",
    "test:integration": "node run-mocha-integration.js",
    "test:baseline": "BASELINE_FILE=./baseline.json mocha",
    "test:debug": "mocha --inspect-brk",
    "test:grep": "mocha --grep"
  }
}
```

## 🔧 Advanced Configuration

### Comprehensive Mocha Configuration

```javascript
// .mocharc.js
const TestFrameworkIntegrations = require('test-framework-integrations');

module.exports = {
  // Test file patterns
  spec: [
    'test/**/*.test.js',
    'test/**/*.spec.js'
  ],
  ignore: [
    'test/fixtures/**',
    'test/helpers/**',
    'node_modules/**'
  ],

  // Execution options
  recursive: true,
  parallel: false, // Set to true for parallel execution
  jobs: process.env.CI ? 2 : 4,
  timeout: 30000,
  slow: 2000,
  bail: false,
  exit: true,

  // Reporting
  reporter: 'spec',
  'reporter-option': [
    'maxDiffSize=8192'
  ],

  // Global setup
  require: [
    'test-framework-integration/mocha-setup',
    'test/helpers/global-setup.js'
  ],

  // Environment
  'node-option': [
    'experimental-loader=./test/loader.js',
    'max-old-space-size=4096'
  ],

  // Coverage integration (when using nyc)
  extension: ['js', 'jsx', 'ts', 'tsx'],

  // Watch mode
  'watch-files': ['src/**/*.js', 'test/**/*.js'],
  'watch-ignore': ['node_modules/**', 'coverage/**'],

  // Browser testing (when needed)
  ui: 'bdd', // or 'tdd', 'qunit', 'exports'
  grep: process.env.GREP || '',
  invert: false
};
```

### Custom Mocha Reporter for Integration

Create `test/reporters/integration-reporter.js`:

```javascript
// test/reporters/integration-reporter.js
const Mocha = require('mocha');
const TestFrameworkIntegrations = require('test-framework-integrations');

const {
  EVENT_RUN_BEGIN,
  EVENT_RUN_END,
  EVENT_TEST_BEGIN,
  EVENT_TEST_END,
  EVENT_SUITE_BEGIN,
  EVENT_SUITE_END,
  EVENT_TEST_FAIL,
  EVENT_TEST_PASS
} = Mocha.Runner.constants;

class IntegrationReporter {
  constructor(runner, options) {
    this.runner = runner;
    this.options = options;
    this.integration = null;
    this.stats = {
      suites: 0,
      tests: 0,
      passes: 0,
      pending: 0,
      failures: 0,
      start: null,
      end: null,
      duration: 0
    };

    this.setupEventListeners();
  }

  async setupEventListeners() {
    // Initialize integration
    this.integration = new TestFrameworkIntegrations({
      framework: 'mocha',
      coverage: true,
      profiling: true,
      baseline: process.env.BASELINE_FILE,
      reporter: 'console'
    });

    await this.integration.initialize();

    // Mocha event listeners
    this.runner
      .on(EVENT_RUN_BEGIN, () => this.onRunBegin())
      .on(EVENT_RUN_END, () => this.onRunEnd())
      .on(EVENT_SUITE_BEGIN, (suite) => this.onSuiteBegin(suite))
      .on(EVENT_SUITE_END, (suite) => this.onSuiteEnd(suite))
      .on(EVENT_TEST_BEGIN, (test) => this.onTestBegin(test))
      .on(EVENT_TEST_END, (test) => this.onTestEnd(test))
      .on(EVENT_TEST_PASS, (test) => this.onTestPass(test))
      .on(EVENT_TEST_FAIL, (test, err) => this.onTestFail(test, err));
  }

  onRunBegin() {
    this.stats.start = new Date();
    console.log('🧪 Mocha Integration Reporter - Test Run Started');

    if (this.integration) {
      this.integration.emit('runStarted', {
        framework: 'mocha',
        timestamp: this.stats.start.toISOString()
      });
    }
  }

  async onRunEnd() {
    this.stats.end = new Date();
    this.stats.duration = this.stats.end - this.stats.start;

    console.log('\n📊 Mocha Integration Results:');
    console.log(`✅ Passed: ${this.stats.passes}`);
    console.log(`❌ Failed: ${this.stats.failures}`);
    console.log(`⏸️  Pending: ${this.stats.pending}`);
    console.log(`⏱️  Duration: ${this.stats.duration}ms`);

    if (this.integration) {
      // Convert Mocha results to integration format
      const integrationResults = this.convertMochaResults();

      // Process through integration system
      await this.integration.processResults(integrationResults);

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
            this.reportBaselineComparison(comparison);
          }
        } catch (error) {
          console.log('⚠️  Could not load baseline for comparison');
        }
      }
    }
  }

  onSuiteBegin(suite) {
    if (suite.title) {
      this.stats.suites++;
    }
  }

  onSuiteEnd(suite) {
    // Suite ended
  }

  onTestBegin(test) {
    this.stats.tests++;

    if (this.integration) {
      this.integration.emit('testStarted', {
        testName: test.title,
        suite: test.parent?.title || 'root',
        file: test.file
      });
    }
  }

  onTestEnd(test) {
    if (this.integration) {
      this.integration.emit('testCompleted', {
        testName: test.title,
        suite: test.parent?.title || 'root',
        status: this.mapMochaState(test.state),
        duration: test.duration,
        file: test.file,
        error: test.err?.message
      });
    }
  }

  onTestPass(test) {
    this.stats.passes++;
  }

  onTestFail(test, err) {
    this.stats.failures++;
  }

  mapMochaState(state) {
    const stateMap = {
      'passed': 'passed',
      'failed': 'failed',
      'pending': 'pending',
      undefined: 'skipped'
    };
    return stateMap[state] || 'unknown';
  }

  convertMochaResults() {
    const tests = [];

    // Extract test results from runner
    this.runner.suite.eachTest((test) => {
      tests.push({
        name: test.title,
        suite: test.parent?.title || 'root',
        status: this.mapMochaState(test.state),
        duration: test.duration,
        file: test.file,
        error: test.err?.message
      });
    });

    return {
      framework: {
        name: 'mocha',
        version: require('mocha/package.json').version,
        adapter: 'MochaAdapter'
      },
      tests,
      summary: {
        total: this.stats.tests,
        passed: this.stats.passes,
        failed: this.stats.failures,
        skipped: 0,
        pending: this.stats.pending,
        duration: this.stats.duration,
        success: this.stats.failures === 0
      },
      timestamp: new Date().toISOString()
    };
  }

  reportBaselineComparison(comparison) {
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

module.exports = IntegrationReporter;
```

To use the custom reporter:

```json
{
  "reporter": "./test/reporters/integration-reporter.js"
}
```

## 🧪 Test Examples

### Basic Mocha Test with Integration

```javascript
// test/utils.test.js
const { expect } = require('chai');
const { add, multiply } = require('../src/utils');

describe('Utils', function() {
  describe('add function', function() {
    it('should add two numbers correctly', function() {
      const result = add(2, 3);
      expect(result).to.equal(5);
    });

    it('should handle negative numbers', function() {
      const result = add(-1, 1);
      expect(result).to.equal(0);
    });
  });

  describe('multiply function', function() {
    it('should multiply two numbers correctly', function() {
      const result = multiply(3, 4);
      expect(result).to.equal(12);
    });

    it('should handle zero multiplication', function() {
      const result = multiply(5, 0);
      expect(result).to.equal(0);
    });
  });
});
```

### Async Test with Performance Tracking

```javascript
// test/api.test.js
const { expect } = require('chai');
const { fetchUserData, processLargeDataset } = require('../src/api');

describe('API Tests', function() {
  describe('fetchUserData', function() {
    it('should fetch user data within reasonable time', async function() {
      this.timeout(5000);

      const startTime = Date.now();
      const userData = await fetchUserData('123');
      const endTime = Date.now();

      expect(userData).to.be.an('object');
      expect(userData.id).to.equal('123');

      // Performance assertion
      const duration = endTime - startTime;
      expect(duration).to.be.below(2000, 'API call should complete within 2 seconds');
    });
  });

  describe('processLargeDataset', function() {
    it('should process large datasets efficiently', async function() {
      this.timeout(10000);

      // Generate test data
      const largeDataset = Array.from({ length: 10000 }, (_, i) => ({
        id: i,
        value: Math.random()
      }));

      const initialMemory = process.memoryUsage();

      const result = await processLargeDataset(largeDataset);

      const finalMemory = process.memoryUsage();
      const memoryDelta = finalMemory.heapUsed - initialMemory.heapUsed;

      expect(result).to.be.an('array');
      expect(result.length).to.equal(largeDataset.length);

      // Memory usage assertion
      expect(memoryDelta).to.be.below(50 * 1024 * 1024, 'Memory usage should be below 50MB');
    });
  });
});
```

### Hooks and Setup

```javascript
// test/database.test.js
const { expect } = require('chai');
const { Database } = require('../src/database');

describe('Database Operations', function() {
  let db;

  // Suite-level setup
  before(async function() {
    this.timeout(10000);
    db = new Database();
    await db.connect();

    // Mark start of suite for profiling
    if (global.testIntegration) {
      global.testIntegration.emit('suiteStarted', {
        suiteName: 'Database Operations'
      });
    }
  });

  // Suite-level teardown
  after(async function() {
    if (db) {
      await db.disconnect();
    }

    // Mark end of suite
    if (global.testIntegration) {
      global.testIntegration.emit('suiteCompleted', {
        suiteName: 'Database Operations'
      });
    }
  });

  // Test-level setup
  beforeEach(async function() {
    await db.clearTestData();
  });

  // Test-level teardown
  afterEach(async function() {
    // Clean up any test-specific data
    await db.cleanup();
  });

  describe('CRUD Operations', function() {
    it('should create a new record', async function() {
      const record = { name: 'Test User', email: 'test@example.com' };
      const result = await db.create('users', record);

      expect(result).to.have.property('id');
      expect(result.name).to.equal(record.name);
    });

    it('should read existing records', async function() {
      // Setup test data
      await db.create('users', { name: 'User 1', email: 'user1@example.com' });
      await db.create('users', { name: 'User 2', email: 'user2@example.com' });

      const users = await db.findAll('users');

      expect(users).to.be.an('array');
      expect(users).to.have.lengthOf(2);
    });

    it('should update existing records', async function() {
      const user = await db.create('users', { name: 'Original Name', email: 'test@example.com' });

      const updatedUser = await db.update('users', user.id, { name: 'Updated Name' });

      expect(updatedUser.name).to.equal('Updated Name');
      expect(updatedUser.email).to.equal('test@example.com');
    });

    it('should delete records', async function() {
      const user = await db.create('users', { name: 'To Delete', email: 'delete@example.com' });

      await db.delete('users', user.id);

      const deletedUser = await db.findById('users', user.id);
      expect(deletedUser).to.be.null;
    });
  });
});
```

## 🔍 Coverage Integration

### NYC (Istanbul) Configuration

Create `.nycrc.json`:

```json
{
  "extends": "@istanbuljs/nyc-config-node",
  "all": true,
  "check-coverage": true,
  "include": [
    "src/**/*.js"
  ],
  "exclude": [
    "test/**",
    "coverage/**",
    "node_modules/**",
    "**/*.spec.js",
    "**/*.test.js"
  ],
  "reporter": [
    "text",
    "html",
    "lcov",
    "json"
  ],
  "report-dir": "coverage",
  "temp-dir": ".nyc_output",
  "statements": 90,
  "branches": 85,
  "functions": 90,
  "lines": 90,
  "cache": true,
  "instrument": true,
  "sourceMap": true,
  "produce-source-map": true
}
```

### Advanced Coverage Integration

```javascript
// coverage-integration.js
const TestFrameworkIntegrations = require('test-framework-integrations');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

class MochaCoverageIntegration {
  constructor() {
    this.integration = new TestFrameworkIntegrations({
      framework: 'mocha',
      coverage: true
    });
  }

  async runTestsWithCoverage() {
    try {
      await this.integration.initialize();

      // Run Mocha with NYC coverage
      await this.executeMochaWithCoverage();

      // Process coverage report
      const coverageData = await this.processCoverageReport();

      // Save coverage baseline
      await this.integration.coverage.saveBaseline(coverageData, 'latest');

      // Check coverage thresholds
      const thresholdCheck = this.integration.coverage.checkThresholds(coverageData);

      if (!thresholdCheck.passed) {
        console.error('Coverage thresholds not met:');
        thresholdCheck.failures.forEach(failure => {
          console.error(`  ${failure.metric}: ${failure.actual}% (required: ${failure.threshold}%)`);
        });
        return false;
      }

      console.log('✅ Coverage integration completed successfully');
      return true;

    } catch (error) {
      console.error('Coverage integration failed:', error);
      return false;
    }
  }

  executeMochaWithCoverage() {
    return new Promise((resolve, reject) => {
      const nyc = spawn('nyc', ['mocha'], {
        stdio: 'inherit',
        shell: true
      });

      nyc.on('close', (code) => {
        if (code === 0) {
          resolve();
        } else {
          reject(new Error(`Mocha tests failed with exit code ${code}`));
        }
      });

      nyc.on('error', reject);
    });
  }

  async processCoverageReport() {
    try {
      const coveragePath = path.join(process.cwd(), 'coverage/coverage-final.json');
      const coverageData = JSON.parse(await fs.readFile(coveragePath, 'utf8'));

      return this.convertNycCoverage(coverageData);
    } catch (error) {
      throw new Error(`Failed to process coverage report: ${error.message}`);
    }
  }

  convertNycCoverage(nycCoverage) {
    const files = [];
    let totalStatements = 0;
    let coveredStatements = 0;
    let totalBranches = 0;
    let coveredBranches = 0;
    let totalFunctions = 0;
    let coveredFunctions = 0;
    let totalLines = 0;
    let coveredLines = 0;

    for (const [filePath, fileData] of Object.entries(nycCoverage)) {
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

module.exports = MochaCoverageIntegration;

// CLI usage
if (require.main === module) {
  const integration = new MochaCoverageIntegration();
  integration.runTestsWithCoverage().then(success => {
    process.exit(success ? 0 : 1);
  });
}
```

## ⚡ Performance Optimization

### Parallel Test Execution

```javascript
// .mocharc.parallel.js
module.exports = {
  require: ['test-framework-integration/mocha-setup'],
  reporter: 'spec',
  timeout: 30000,
  recursive: true,
  spec: 'test/**/*.test.js',

  // Parallel execution
  parallel: true,
  jobs: process.env.CI ? 2 : require('os').cpus().length - 1,

  // Parallel-safe options
  exit: true,
  bail: false,

  // Optimize for parallel execution
  'forbid-only': process.env.CI === 'true',
  'forbid-pending': process.env.CI === 'true'
};
```

### Performance Monitoring

```javascript
// test/helpers/performance-monitor.js
const TestFrameworkIntegrations = require('test-framework-integrations');

class MochaPerformanceMonitor {
  constructor() {
    this.integration = new TestFrameworkIntegrations({
      framework: 'mocha',
      profiling: {
        enabled: true,
        memoryInterval: 100,
        detectLeaks: true
      }
    });
    this.testMetrics = new Map();
  }

  async initialize() {
    await this.integration.initialize();
    this.startGlobalMonitoring();
  }

  startGlobalMonitoring() {
    // Monitor memory usage globally
    this.memoryInterval = setInterval(() => {
      const usage = process.memoryUsage();
      this.integration.profiler.recordMemoryUsage(usage);
    }, 100);

    // Monitor CPU usage
    this.cpuInterval = setInterval(() => {
      const usage = process.cpuUsage();
      this.integration.profiler.recordCpuUsage(usage);
    }, 500);

    // Cleanup on process exit
    process.on('exit', () => {
      clearInterval(this.memoryInterval);
      clearInterval(this.cpuInterval);
    });
  }

  beforeTest(test) {
    const testKey = `${test.parent.title} > ${test.title}`;
    this.testMetrics.set(testKey, {
      startTime: Date.now(),
      startMemory: process.memoryUsage(),
      startCpu: process.cpuUsage()
    });
  }

  afterTest(test) {
    const testKey = `${test.parent.title} > ${test.title}`;
    const metrics = this.testMetrics.get(testKey);

    if (metrics) {
      const endTime = Date.now();
      const endMemory = process.memoryUsage();
      const endCpu = process.cpuUsage(metrics.startCpu);

      const testResult = {
        name: testKey,
        status: test.state,
        duration: endTime - metrics.startTime,
        memoryDelta: {
          heapUsed: endMemory.heapUsed - metrics.startMemory.heapUsed,
          heapTotal: endMemory.heapTotal - metrics.startMemory.heapTotal
        },
        cpuUsage: {
          user: endCpu.user / 1000, // Convert to milliseconds
          system: endCpu.system / 1000
        }
      };

      this.analyzeTestPerformance(testResult);
      this.testMetrics.delete(testKey);
    }
  }

  analyzeTestPerformance(testResult) {
    const { name, duration, memoryDelta, cpuUsage } = testResult;

    // Check for slow tests
    if (duration > 5000) {
      console.warn(`⚠️  Slow test: ${name} took ${duration}ms`);
    }

    // Check for memory leaks
    if (memoryDelta.heapUsed > 10 * 1024 * 1024) { // 10MB
      console.warn(`⚠️  Memory leak: ${name} used ${(memoryDelta.heapUsed / 1024 / 1024).toFixed(2)}MB`);
    }

    // Check for high CPU usage
    const totalCpu = cpuUsage.user + cpuUsage.system;
    if (totalCpu > 1000) { // 1 second of CPU time
      console.warn(`⚠️  High CPU usage: ${name} used ${totalCpu.toFixed(2)}ms CPU time`);
    }
  }

  async generateReport() {
    const bottlenecks = await this.integration.analyzeBottlenecks();

    console.log('\n🔍 Performance Analysis:');

    if (bottlenecks.slowTests.length > 0) {
      console.log('\n🐌 Slowest Tests:');
      bottlenecks.slowTests.slice(0, 5).forEach((test, i) => {
        console.log(`  ${i + 1}. ${test.name}: ${test.duration}ms`);
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

// Global setup for performance monitoring
const performanceMonitor = new MochaPerformanceMonitor();

// Export for global use
global.performanceMonitor = performanceMonitor;

// Initialize before tests start
before(async function() {
  this.timeout(10000);
  await performanceMonitor.initialize();
});

// Hook into test lifecycle
beforeEach(function() {
  performanceMonitor.beforeTest(this.currentTest);
});

afterEach(function() {
  performanceMonitor.afterTest(this.currentTest);
});

// Generate report after all tests
after(async function() {
  await performanceMonitor.generateReport();
});

module.exports = MochaPerformanceMonitor;
```

## 🚀 CI/CD Integration

### GitHub Actions for Mocha

```yaml
# .github/workflows/mocha-integration.yml
name: Mocha Integration Tests

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

    - name: Run Mocha with Integration
      run: npm run test:integration
      env:
        CI: true
        BASELINE_FILE: ./baselines/main.json
        SAVE_BASELINE: ${{ github.ref == 'refs/heads/main' }}

    - name: Run Coverage
      run: npm run test:coverage

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage/lcov.info
        flags: mocha
        name: codecov-umbrella

    - name: Upload test artifacts
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: mocha-results-${{ matrix.node-version }}
        path: |
          test-results/
          coverage/
          .nyc_output/
```

### Integration Script

```javascript
// run-mocha-integration.js
const TestFrameworkIntegrations = require('test-framework-integrations');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

async function runMochaIntegration() {
  console.log('🧪 Starting Mocha Integration Tests\n');

  const integration = new TestFrameworkIntegrations({
    framework: 'mocha',
    coverage: true,
    profiling: true,
    baseline: process.env.BASELINE_FILE,
    reporter: ['console', 'json']
  });

  try {
    // Initialize integration
    await integration.initialize();

    // Run Mocha tests with coverage
    console.log('🚀 Running Mocha tests with coverage...');
    const testResults = await runMochaWithNyc();

    // Process results through integration
    const integrationResults = await integration.processMochaResults(testResults);

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

    // Save integration summary
    const summaryPath = path.join(process.cwd(), 'test-results', 'mocha-integration-summary.json');
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

function runMochaWithNyc() {
  return new Promise((resolve, reject) => {
    const args = ['--reporter', 'json', '--coverage'];
    const mocha = spawn('nyc', ['mocha', ...args], {
      stdio: ['inherit', 'pipe', 'inherit']
    });

    let output = '';
    mocha.stdout.on('data', (data) => {
      output += data.toString();
    });

    mocha.on('close', (code) => {
      try {
        const results = JSON.parse(output);
        resolve(results);
      } catch (error) {
        reject(new Error(`Failed to parse Mocha output: ${error.message}`));
      }
    });

    mocha.on('error', reject);
  });
}

module.exports = runMochaIntegration;

// Run if called directly
if (require.main === module) {
  runMochaIntegration();
}
```

## 🔧 Troubleshooting

### Common Issues

#### Issue: Tests Not Being Tracked
**Problem**: Mocha tests run but integration doesn't track them.

**Solution**:
```javascript
// Ensure proper setup in .mocharc.json
{
  "require": ["test-framework-integration/mocha-setup"]
}

// Or in test files
before(async function() {
  if (!global.testIntegration) {
    const TestFrameworkIntegrations = require('test-framework-integrations');
    global.testIntegration = new TestFrameworkIntegrations({
      framework: 'mocha'
    });
    await global.testIntegration.initialize();
  }
});
```

#### Issue: Coverage Not Working with NYC
**Problem**: Coverage reports are empty or incorrect.

**Solution**:
```json
// .nycrc.json
{
  "all": true,
  "include": ["src/**/*.js"],
  "exclude": ["test/**", "coverage/**"],
  "instrument": true,
  "cache": false
}
```

#### Issue: Parallel Tests Interfere
**Problem**: Tests fail when run in parallel but pass individually.

**Solution**:
```javascript
// Use isolated test setup
beforeEach(function() {
  // Reset global state
  // Clean up shared resources
});

afterEach(function() {
  // Ensure cleanup
});

// Or disable parallel for problematic suites
describe('Database tests', function() {
  this.timeout(0); // Disable timeout
  // Run these tests sequentially
});
```

### Performance Tips

1. **Use Parallel Execution**: Enable `parallel: true` for CPU-intensive test suites
2. **Optimize Hooks**: Keep `before`/`after` hooks lightweight
3. **Memory Management**: Clean up resources in `afterEach` hooks
4. **Selective Coverage**: Only collect coverage for source files
5. **Test Isolation**: Ensure tests don't depend on each other

## 📚 Additional Resources

- **[Mocha Documentation](https://mochajs.org/)** - Official Mocha documentation
- **[Chai Assertion Library](https://www.chaijs.com/)** - Popular assertion library for Mocha
- **[NYC Coverage](https://github.com/istanbuljs/nyc)** - Istanbul coverage tool
- **[Mocha Parallel](https://mochajs.org/#parallel-tests)** - Parallel test execution guide