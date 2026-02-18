# Quick Start Guide

Get up and running with Test Framework Integrations in under 5 minutes.

## 🚀 Installation

### Option 1: NPM (Recommended)

```bash
npm install --save-dev test-framework-integrations
```

### Option 2: Yarn

```bash
yarn add --dev test-framework-integrations
```

### Option 3: Global Installation

```bash
npm install -g test-framework-integrations
```

## 📋 Prerequisites

- **Node.js**: 14.0.0 or higher
- **Testing Framework**: At least one of:
  - Jest (≥27.0.0)
  - Mocha (≥9.0.0)
  - Vitest (≥0.20.0)
  - Playwright (≥1.20.0)
  - Pytest (≥6.0.0)

## 🎯 Basic Usage

### 1. Create Your First Test Integration

```javascript
// test-integration.js
const TestFrameworkIntegrations = require('test-framework-integrations');

async function runTests() {
  // Initialize the system with auto-detection
  const testIntegration = new TestFrameworkIntegrations({
    coverage: true,     // Enable coverage collection
    profiling: true,    // Enable performance profiling
    reporter: 'console' // Use console reporter
  });

  try {
    // Initialize and auto-detect frameworks
    await testIntegration.initialize();

    // Run tests with integrated features
    const results = await testIntegration.runTests();

    console.log(`Tests: ${results.summary.passed}/${results.summary.total} passed`);
    console.log(`Coverage: ${results.coverage?.total.toFixed(2)}%`);

  } catch (error) {
    console.error('Test execution failed:', error.message);
  }
}

runTests();
```

### 2. Run Your Integration

```bash
node test-integration.js
```

## 📊 Expected Output

```
🔍 Initializing and detecting test frameworks...
📋 Detected frameworks:
  - jest v29.5.0 (active)
  - playwright v1.32.0

🔎 Discovering test files...
Found 12 test files

🚀 Running tests with coverage and profiling...

 PASS  src/utils.test.js
 PASS  src/components/Button.test.js
 PASS  src/api/users.test.js

📊 Results Summary:
  Tests: 24 (24 passed, 0 failed)
  Duration: 3247ms
  Coverage: 87.3%
  Performance: 3247ms total

✅ Basic example completed successfully!
```

## 🔧 Configuration Options

### Essential Options

```javascript
const testIntegration = new TestFrameworkIntegrations({
  // Basic settings
  rootDir: process.cwd(),           // Project root directory
  preferredFramework: 'jest',       // Force specific framework

  // Features
  coverage: true,                   // Enable coverage collection
  profiling: true,                  // Enable performance profiling
  baseline: './baseline.json',      // Compare with baseline

  // Output
  reporter: 'console',              // Reporter type
  outputDir: '.test-baseline',      // Output directory

  // Execution
  parallel: false,                  // Run frameworks in parallel
  bail: false,                      // Stop on first failure
  verbose: true                     // Detailed output
});
```

### Framework-Specific Configuration

```javascript
// Jest-specific options
const jestOptions = {
  preferredFramework: 'jest',
  jestConfig: {
    collectCoverageFrom: ['src/**/*.js'],
    testMatch: ['**/__tests__/**/*.js']
  }
};

// Playwright-specific options
const playwrightOptions = {
  preferredFramework: 'playwright',
  playwrightConfig: {
    projects: ['chromium', 'firefox'],
    workers: 4
  }
};
```

## 💾 Baseline Tracking

### Save Your First Baseline

```javascript
// After running tests
await testIntegration.saveBaseline('v1.0.0');
```

### Compare Against Baseline

```javascript
const testIntegration = new TestFrameworkIntegrations({
  baseline: './baselines/v1.0.0.json' // Compare with specific baseline
});

const results = await testIntegration.runTests();

// Check for regressions
if (results.baseline?.regressions.length > 0) {
  console.log('⚠️ Performance regressions detected!');
  results.baseline.regressions.forEach(regression => {
    console.log(`${regression.test}: ${regression.change}ms slower`);
  });
}
```

## 📈 Coverage Reports

### Generate Coverage Reports

```javascript
// After running tests with coverage enabled
const reportPaths = await testIntegration.generateCoverageReports('release-1.0');

console.log('Coverage reports generated:');
reportPaths.forEach(path => console.log(`  - ${path}`));
```

### Coverage Thresholds

```javascript
const testIntegration = new TestFrameworkIntegrations({
  coverage: {
    enabled: true,
    thresholds: {
      statements: 90,
      branches: 85,
      functions: 90,
      lines: 90
    }
  }
});
```

## ⚡ Performance Monitoring

### Real-time Performance Tracking

```javascript
// Start tests
const testPromise = testIntegration.runTests();

// Monitor while running
const interval = setInterval(() => {
  const metrics = testIntegration.getCurrentMetrics();
  if (metrics) {
    console.log(`Memory: ${metrics.memory.heapUsed / 1024 / 1024}MB`);
    console.log(`Uptime: ${metrics.uptime / 1000}s`);
  }
}, 1000);

// Wait for completion
await testPromise;
clearInterval(interval);

// Analyze bottlenecks
const bottlenecks = testIntegration.analyzeBottlenecks();
if (bottlenecks.slowTests.length > 0) {
  console.log('Slowest tests:', bottlenecks.slowTests.slice(0, 5));
}
```

## 🔄 Multi-Framework Testing

### Test Across All Frameworks

```javascript
// Run the same tests with different frameworks
const results = await testIntegration.runAllFrameworks({
  coverage: true
});

// Compare results
for (const [framework, result] of Object.entries(results.results)) {
  console.log(`${framework}: ${result.summary.passed}/${result.summary.total}`);
}
```

## 📝 CLI Usage

### Global Installation Usage

```bash
# Run with auto-detection
test-framework-integrations

# Specify framework
test-framework-integrations --framework jest

# Enable coverage and profiling
test-framework-integrations --coverage --profiling

# Compare with baseline
test-framework-integrations --baseline ./baseline.json

# Generate reports
test-framework-integrations --reporter html --output-dir ./reports
```

## 🛠️ Common Patterns

### CI/CD Integration

```yaml
# GitHub Actions example
- name: Run Tests with Baseline Tracking
  run: |
    npm install
    node -e "
      const TFI = require('test-framework-integrations');
      (async () => {
        const tfi = new TFI({
          coverage: true,
          baseline: './baseline.json',
          reporter: ['console', 'json']
        });
        await tfi.initialize();
        const results = await tfi.runTests();
        if (results.summary.failed > 0) process.exit(1);
        await tfi.saveBaseline('latest');
      })().catch(console.error);
    "
```

### Docker Integration

```dockerfile
# Dockerfile for testing
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run test:integration
```

## 🔍 Next Steps

1. **[Framework Integration](./guides/)**: Set up your specific testing framework
2. **[Configuration Reference](./configuration/)**: Customize advanced settings
3. **[API Documentation](./api/)**: Explore programmatic usage
4. **[Troubleshooting](./troubleshooting/)**: Solve common issues

## 💡 Pro Tips

- **Start Simple**: Begin with basic configuration, add features incrementally
- **Use Baselines**: Track performance and regression trends over time
- **Monitor Memory**: Enable profiling to catch memory leaks early
- **Automate Reports**: Generate coverage reports in your CI/CD pipeline
- **Framework Fallback**: Configure fallback order for automatic framework selection

## 🆘 Need Help?

- **Issues**: [GitHub Issues](https://github.com/your-org/test-framework-integrations/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-org/test-framework-integrations/discussions)
- **Documentation**: [Full Documentation](./README.md)
- **Examples**: [Advanced Examples](./examples/)