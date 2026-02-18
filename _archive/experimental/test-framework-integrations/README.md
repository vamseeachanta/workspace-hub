# Test Framework Integrations

A comprehensive test framework integration system that provides unified testing capabilities across Jest, Mocha, Vitest, Playwright, and Pytest with baseline tracking, coverage collection, and performance profiling.

## Features

### 🔧 Framework Adapters
- **Jest**: Custom reporter with baseline integration
- **Mocha**: Hooks integration with performance tracking
- **Vitest**: Modern testing with native ESM support
- **Playwright**: E2E testing with browser automation
- **Pytest**: Python testing with plugin integration

### 📊 Unified Test Runner
- Auto-detects available test frameworks
- Runs tests with baseline tracking
- Collects all metrics in real-time
- Handles parallel execution
- Streams results with progress updates

### 📈 Coverage Integration
- **NYC/Istanbul**: JavaScript coverage collection
- **C8/V8**: Modern Node.js coverage
- **Coverage.py**: Python coverage integration
- Merges coverage from multiple sources
- Tracks coverage trends over time

### ⚡ Performance Profiling
- Memory usage tracking with leak detection
- CPU profiling with V8 integration
- Test duration analysis
- Resource leak detection
- GC pressure monitoring

### 📋 Custom Reporters
- Baseline-aware reporting with trend analysis
- Real-time progress updates
- Failure analysis with suggestions
- Multiple output formats (console, JSON, HTML, Markdown)
- Performance recommendations

## Installation

```bash
npm install test-framework-integrations
```

### Optional Dependencies

Install the test frameworks you want to use:

```bash
# JavaScript/TypeScript frameworks
npm install --save-dev jest mocha vitest @playwright/test

# Coverage tools
npm install --save-dev nyc c8

# Python (if using Pytest adapter)
pip install pytest coverage
```

## Quick Start

### Basic Usage

```javascript
const TestFrameworkIntegrations = require('test-framework-integrations');

async function runTests() {
  // Create and initialize the test integration system
  const testIntegration = new TestFrameworkIntegrations({
    coverage: true,          // Enable coverage collection
    profiling: true,         // Enable performance profiling
    reporter: 'console',     // Use console reporter
    baseline: './baseline.json' // Compare against baseline
  });

  // Initialize (auto-detects available frameworks)
  await testIntegration.initialize();

  // Run tests with integrated coverage and profiling
  const results = await testIntegration.runTests({
    verbose: true,
    bail: false
  });

  console.log(`Tests: ${results.summary.total} (${results.summary.passed} passed)`);
  console.log(`Coverage: ${results.coverage.total.toFixed(2)}%`);

  // Save results as new baseline
  await testIntegration.saveBaseline('latest');
}

runTests().catch(console.error);
```

### Framework-Specific Usage

```javascript
// Use a specific framework adapter
const { JestAdapter } = require('test-framework-integrations').adapters;

const jestAdapter = new JestAdapter({
  coverage: true,
  profiling: true,
  baseline: './jest-baseline.json'
});

await jestAdapter.initialize();
const results = await jestAdapter.runTests();
```

### Multi-Framework Testing

```javascript
// Run tests across all detected frameworks
const results = await testIntegration.runAllFrameworks({
  coverage: true,
  parallel: false // Run sequentially for comparison
});

console.log('Multi-Framework Results:');
for (const [framework, result] of Object.entries(results.results)) {
  console.log(`${framework}: ${result.summary.passed}/${result.summary.total} passed`);
}
```

## Configuration Options

### TestFrameworkIntegrations Options

```javascript
const options = {
  rootDir: process.cwd(),           // Project root directory
  preferredFramework: 'jest',       // Preferred framework (auto-detected if not set)
  coverage: true,                   // Enable coverage collection
  profiling: true,                  // Enable performance profiling
  baseline: './baseline.json',      // Baseline file for comparison
  parallel: false,                  // Enable parallel execution
  autoDetect: true,                 // Auto-detect frameworks
  reporter: 'console',              // Reporter format(s)
  outputDir: '.test-baseline',      // Output directory for reports

  // Coverage options
  coverageProviders: ['auto'],      // Coverage providers to use
  coverageFormats: ['json', 'html'], // Coverage report formats
  coverageThreshold: {              // Coverage thresholds
    statements: 80,
    branches: 80,
    functions: 80,
    lines: 80
  },

  // Profiling options
  enableMemoryTracking: true,       // Track memory usage
  enableCpuProfiling: false,        // Enable CPU profiling
  enableGcTracking: true,           // Track garbage collection
  detectLeaks: true,                // Detect memory leaks
  memoryInterval: 100,              // Memory sampling interval (ms)

  // Reporter options
  colorOutput: true,                // Enable colored output
  showTrends: true,                 // Show trending data
  showRecommendations: true,        // Show performance recommendations
  verbose: false                    // Verbose output
};
```

### Framework-Specific Options

#### Jest Adapter
```javascript
const jestOptions = {
  // Standard options plus:
  testTimeout: 30000,               // Test timeout
  maxWorkers: 4,                    // Number of workers
  bail: false,                      // Stop on first failure
  watch: false,                     // Watch mode
  testNamePattern: 'user',          // Test name filter
  testPathPattern: 'components'     // Test path filter
};
```

#### Mocha Adapter
```javascript
const mochaOptions = {
  // Standard options plus:
  timeout: 5000,                    // Test timeout
  retries: 0,                       // Number of retries
  grep: 'api',                      // Test filter pattern
  recursive: true,                  // Recursive test discovery
  bail: false                       // Stop on first failure
};
```

#### Vitest Adapter
```javascript
const vitestOptions = {
  // Standard options plus:
  environment: 'node',              // Test environment
  threads: true,                    // Use threads
  minThreads: 1,                    // Minimum threads
  maxThreads: 4,                    // Maximum threads
  testTimeout: 10000,               // Test timeout
  watch: false                      // Watch mode
};
```

#### Playwright Adapter
```javascript
const playwrightOptions = {
  // Standard options plus:
  browser: 'chromium',              // Browser to use
  headed: false,                    // Run in headed mode
  debug: false,                     // Debug mode
  workers: 1,                       // Number of workers
  retries: 0,                       // Number of retries
  timeout: 30000,                   // Test timeout
  trace: false,                     // Enable tracing
  video: 'retain-on-failure',      // Video recording
  screenshot: 'only-on-failure'    // Screenshot capture
};
```

#### Pytest Adapter
```javascript
const pytestOptions = {
  // Standard options plus:
  markers: 'unit',                  // Test markers
  keyword: 'test_user',             // Keyword filter
  maxfail: 1,                       // Maximum failures
  timeout: 300,                     // Test timeout
  workers: 1,                       // Number of workers (pytest-xdist)
  verbose: true                     // Verbose output
};
```

## API Reference

### TestFrameworkIntegrations

Main class that orchestrates test execution with integrated coverage, profiling, and reporting.

#### Methods

- `initialize()` - Initialize the system and detect frameworks
- `discoverTests()` - Discover all test files
- `runTests(options)` - Run tests with integrated features
- `runAllFrameworks(options)` - Run tests across all frameworks
- `stopTests()` - Stop running tests
- `getDetectedFrameworks()` - Get information about detected frameworks
- `switchFramework(framework)` - Switch to a different framework
- `compareWithBaseline(baseline)` - Compare results with baseline
- `generateCoverageReports(name)` - Generate coverage reports
- `analyzeBottlenecks()` - Analyze performance bottlenecks
- `saveBaseline(label)` - Save current results as baseline
- `getCurrentMetrics()` - Get current performance metrics

### UnifiedTestRunner

Handles test execution across different frameworks with auto-detection.

#### Events

- `initialization` - System initialization status
- `detection` - Framework detection progress
- `frameworkDetected` - Framework detected
- `adapterSelected` - Framework adapter selected
- `testStarted` - Test execution started
- `testOutput` - Test output received
- `runCompleted` - Test run completed
- `error` - Error occurred

### CoverageIntegrator

Unifies coverage collection across different providers.

#### Methods

- `initialize()` - Initialize coverage collection
- `collectCoverage(framework, command, options)` - Collect coverage
- `mergeCoverage(frameworks)` - Merge coverage from multiple sources
- `generateReports(coverage, name)` - Generate coverage reports
- `checkThresholds(coverage)` - Check coverage against thresholds
- `saveBaseline(coverage, label)` - Save coverage baseline
- `getCoverageTrends(days)` - Get coverage trends

### PerformanceProfiler

Monitors test performance including memory, CPU, and timing.

#### Methods

- `initialize()` - Initialize profiler
- `startProfiling()` - Start performance monitoring
- `stopProfiling()` - Stop profiling and generate report
- `markTestStart(testName, metadata)` - Mark test start
- `markTestEnd(testName, result)` - Mark test end
- `getCurrentMetrics()` - Get current performance metrics
- `analyzeBottlenecks()` - Analyze performance bottlenecks

### BaselineReporter

Custom reporter with baseline comparison and trend analysis.

#### Methods

- `initialize()` - Initialize reporter
- `onRunStart(data)` - Handle test run start
- `onTestOutput(data)` - Handle test output
- `onTestComplete(test)` - Handle individual test completion
- `onRunComplete(results)` - Handle test run completion
- `onRunFailed(error)` - Handle run failure

## Examples

### Performance Monitoring

```javascript
const testIntegration = new TestFrameworkIntegrations({
  profiling: true,
  reporter: 'json'
});

await testIntegration.initialize();

// Monitor performance in real-time
const testPromise = testIntegration.runTests();

const monitoringInterval = setInterval(() => {
  const metrics = testIntegration.getCurrentMetrics();
  if (metrics) {
    console.log(`Memory: ${(metrics.memory.process.heapUsed / 1024 / 1024).toFixed(2)}MB`);
    console.log(`GC events: ${metrics.gc.recentEvents}`);
  }
}, 1000);

const results = await testPromise;
clearInterval(monitoringInterval);

// Analyze bottlenecks
const bottlenecks = testIntegration.analyzeBottlenecks();
console.log('Slowest tests:', bottlenecks.slowTests);
```

### Coverage Tracking

```javascript
const testIntegration = new TestFrameworkIntegrations({
  coverage: true,
  coverageThreshold: {
    statements: 90,
    branches: 85,
    functions: 90,
    lines: 90
  }
});

await testIntegration.initialize();
const results = await testIntegration.runTests();

// Check coverage thresholds
if (results.coverage) {
  const thresholdCheck = testIntegration.coverage.checkThresholds(results.coverage);
  if (!thresholdCheck.passed) {
    console.log('Coverage thresholds not met:', thresholdCheck.failures);
  }
}

// Generate HTML coverage report
await testIntegration.generateCoverageReports('detailed');
```

### Baseline Comparison

```javascript
// Load previous baseline
const previousBaseline = JSON.parse(fs.readFileSync('./baseline.json', 'utf8'));

const testIntegration = new TestFrameworkIntegrations({
  baseline: previousBaseline,
  reporter: ['console', 'html']
});

await testIntegration.initialize();
const results = await testIntegration.runTests();

// Compare with baseline
const comparison = testIntegration.compareWithBaseline(previousBaseline);

if (comparison.testsChanged.length > 0) {
  console.log('Tests changed since baseline:');
  comparison.testsChanged.forEach(test => {
    console.log(`${test.name}: ${test.from} → ${test.to}`);
  });
}

if (comparison.performance.slower.length > 0) {
  console.log('Tests slower than baseline:');
  comparison.performance.slower.forEach(test => {
    console.log(`${test.name}: +${test.regression}ms`);
  });
}
```

## Error Handling

The system provides comprehensive error handling with fallbacks:

```javascript
try {
  await testIntegration.runTests();
} catch (error) {
  if (error.message.includes('No compatible test frameworks detected')) {
    console.log('Please install a supported test framework (Jest, Mocha, Vitest, Playwright, or Pytest)');
  } else if (error.message.includes('Coverage provider not available')) {
    console.log('Please install a coverage tool (nyc, c8, or coverage.py)');
  } else {
    console.error('Test execution failed:', error.message);
  }
}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for your changes
4. Ensure all tests pass
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Changelog

### v1.0.0
- Initial release
- Support for Jest, Mocha, Vitest, Playwright, and Pytest
- Unified test runner with auto-detection
- Coverage integration with multiple providers
- Performance profiling with leak detection
- Baseline-aware reporting with trend analysis
- Comprehensive error handling and fallbacks