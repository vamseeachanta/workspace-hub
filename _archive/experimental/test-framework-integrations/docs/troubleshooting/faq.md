# Frequently Asked Questions (FAQ)

## General Questions

### What is the Test Framework Integrations system?

The Test Framework Integrations system is a unified testing platform that provides consistent test execution, baseline tracking, performance monitoring, and reporting across multiple testing frameworks (Jest, Mocha, Pytest, Playwright, Vitest).

### Which testing frameworks are supported?

Currently supported frameworks:
- **Jest** - JavaScript/TypeScript unit and integration testing
- **Mocha** - JavaScript/TypeScript testing with flexible assertions
- **Pytest** - Python testing framework
- **Playwright** - Cross-browser end-to-end testing
- **Vitest** - Next-generation testing powered by Vite

### Can I use multiple frameworks in one project?

Yes! The system supports multi-framework configurations:

```javascript
module.exports = {
  framework: {
    type: 'multi',
    configurations: {
      unit: { type: 'jest', testDir: 'src' },
      integration: { type: 'jest', testDir: 'tests/integration' },
      e2e: { type: 'playwright', testDir: 'tests/e2e' }
    }
  }
};
```

## Installation and Setup

### How do I install the system?

```bash
# Install the integration system
npm install test-framework-integrations

# Install your preferred testing framework
npm install --save-dev jest  # or mocha, vitest, etc.
```

### Do I need to install anything globally?

No, the system works as a local dependency. However, you can install it globally for the CLI tools:

```bash
npm install -g test-framework-integrations
npx test-integration --help
```

### What Node.js version is required?

Node.js 16.0.0 or higher is required. We recommend using the latest LTS version for best performance and security.

### How do I check if everything is set up correctly?

Run the diagnostic command:

```bash
npx test-integration doctor
```

This will verify your installation, configuration, and dependencies.

## Configuration

### Where should I put my configuration file?

You can use any of these options (in order of precedence):
1. `test-integration.config.js` (recommended)
2. `test-integration.config.json`
3. `test-integration.config.yaml`
4. Configuration in `package.json` under `testIntegration`

### How do I auto-detect my testing framework?

The system automatically detects frameworks based on:
- Installed dependencies in `package.json`
- Presence of framework configuration files
- Framework-specific patterns in your codebase

To disable auto-detection:

```javascript
module.exports = {
  framework: {
    type: 'jest', // Explicitly specify framework
    autoDetect: false
  }
};
```

### Can I override configuration with environment variables?

Yes! Environment variables take precedence over config files:

```bash
export TEST_FRAMEWORK=jest
export TEST_TIMEOUT=60000
export COVERAGE_ENABLED=true
npm test
```

See the [Environment Variables Reference](../configuration/environment-variables.md) for a complete list.

### How do I configure for different environments?

Use environment-specific configuration:

```javascript
const isCI = process.env.CI === 'true';
const isDev = process.env.NODE_ENV === 'development';

module.exports = {
  execution: {
    timeout: isCI ? 60000 : 30000,
    retries: isCI ? 2 : 0,
    verbose: isDev
  },
  reporting: {
    formats: isCI ? ['json', 'junit'] : ['console', 'html']
  }
};
```

## Baseline Tracking

### What are baselines and why should I use them?

Baselines are snapshots of your test results that serve as reference points for comparison. They help detect:
- Performance regressions
- Coverage changes
- Test count variations
- Behavioral changes

### How do I create my first baseline?

```bash
# Run tests and save baseline
npx test-integration run --save-baseline main

# Or configure auto-save
```

```javascript
module.exports = {
  baseline: {
    enabled: true,
    autoSave: true
  }
};
```

### Where are baselines stored?

By default, baselines are stored in the `./baselines` directory as compressed JSON files. You can configure alternative storage:

```javascript
module.exports = {
  baseline: {
    storage: {
      type: 's3', // or 'gcs', 'azure'
      options: {
        bucket: 'my-test-baselines',
        region: 'us-east-1'
      }
    }
  }
};
```

### How do I compare against a specific baseline?

```bash
# Compare with named baseline
npx test-integration run --compare-baseline main

# Compare with latest baseline
npx test-integration run --compare-baseline latest
```

### What should I do when baseline comparison fails?

1. **Review the changes** - Check what actually changed
2. **Investigate regressions** - Determine if changes are expected
3. **Update baseline** - If changes are intentional:

```bash
npx test-integration baseline update main
```

## Performance Monitoring

### How do I enable performance monitoring?

```javascript
module.exports = {
  performance: {
    enabled: true,
    collectMetrics: ['duration', 'memory', 'cpu'],
    thresholds: {
      testDuration: 5000, // 5 seconds max per test
      memoryUsage: 256 * 1024 * 1024 // 256MB max
    }
  }
};
```

### What performance metrics are collected?

Available metrics:
- **Duration** - Test execution time
- **Memory** - Heap usage and garbage collection
- **CPU** - CPU utilization during tests
- **Network** - Network requests (for integration tests)
- **Disk** - I/O operations

### How do I set performance thresholds?

```javascript
module.exports = {
  performance: {
    thresholds: {
      testDuration: 10000,    // Individual test limit (ms)
      suiteDuration: 60000,   // Test suite limit (ms)
      totalDuration: 300000,  // Total execution limit (ms)
      memoryUsage: 512 * 1024 * 1024, // Memory limit (bytes)
      cpuUsage: 80           // CPU usage percentage
    }
  }
};
```

### Can I get alerts for performance regressions?

Yes! Configure performance alerts:

```javascript
module.exports = {
  performance: {
    monitoring: {
      alerts: {
        enabled: true,
        thresholdMultiplier: 1.5, // Alert at 150% of threshold
        channels: ['console', 'webhook', 'slack']
      }
    }
  }
};
```

## Coverage

### How do I enable code coverage?

```javascript
module.exports = {
  execution: {
    coverage: true
  },
  reporting: {
    coverage: {
      enabled: true,
      formats: ['html', 'json'],
      watermarks: {
        statements: [70, 85],
        functions: [70, 85],
        branches: [60, 80],
        lines: [70, 85]
      }
    }
  }
};
```

### How do I set coverage thresholds?

```javascript
module.exports = {
  rules: {
    coverage: {
      global: {
        statements: 80,
        branches: 75,
        functions: 80,
        lines: 80
      },
      perFile: {
        statements: 70,
        branches: 65,
        functions: 70,
        lines: 70
      }
    }
  }
};
```

### Why is my coverage lower than expected?

Common causes:
1. **Files not included** - Check your coverage configuration
2. **Dynamic imports** - These may not be instrumented
3. **Dead code** - Unreachable code paths
4. **Test environment** - Some code may only run in specific environments

### How do I exclude files from coverage?

```javascript
// Framework-specific configuration
// For Jest:
module.exports = {
  collectCoverageFrom: [
    'src/**/*.{js,ts}',
    '!src/**/*.test.{js,ts}',
    '!src/**/*.d.ts',
    '!src/**/index.{js,ts}'
  ]
};
```

## Reporting

### What report formats are available?

Supported formats:
- **console** - Terminal output
- **json** - Machine-readable JSON
- **html** - Interactive HTML reports
- **junit** - JUnit XML for CI systems
- **tap** - Test Anything Protocol
- **lcov** - Coverage format
- **cobertura** - Coverage format for CI

### How do I customize report output?

```javascript
module.exports = {
  reporting: {
    formats: ['html', 'json'],
    outputDir: 'test-reports',
    filename: 'test-results',
    detailed: true,
    timestamp: true,
    includeSkipped: false
  }
};
```

### Can I create custom report templates?

Yes! You can provide custom templates:

```javascript
module.exports = {
  reporting: {
    formats: ['html'],
    template: './custom-template.html',
    // Or for programmatic customization
    customReporter: './custom-reporter.js'
  }
};
```

## CI/CD Integration

### How do I integrate with GitHub Actions?

```yaml
name: Tests
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 18
      - run: npm ci
      - run: npm test
      - uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/
```

### How do I optimize for CI performance?

```javascript
const isCI = process.env.CI === 'true';

module.exports = {
  execution: {
    maxWorkers: isCI ? 2 : 4,
    timeout: isCI ? 60000 : 30000,
    retries: isCI ? 2 : 0,
    bail: isCI // Stop on first failure in CI
  }
};
```

### How do I handle flaky tests in CI?

```javascript
module.exports = {
  execution: {
    retries: 2, // Retry failed tests
    retryIf: (error) => {
      // Only retry on specific errors
      return error.message.includes('timeout') ||
             error.message.includes('network');
    }
  }
};
```

### Can I run different test suites in parallel CI jobs?

Yes! Use test sharding:

```yaml
strategy:
  matrix:
    shard: [1, 2, 3, 4]
steps:
  - run: npm test -- --shard=${{ matrix.shard }}/4
```

## Troubleshooting

### Tests are running slowly, what can I do?

1. **Enable parallel execution**:
   ```javascript
   module.exports = {
     execution: {
       mode: 'parallel',
       maxWorkers: 4
     }
   };
   ```

2. **Optimize test isolation**:
   ```javascript
   // Use beforeAll instead of beforeEach when possible
   beforeAll(async () => {
     // Expensive setup
   });
   ```

3. **Profile your tests**:
   ```bash
   npx test-integration run --profile
   ```

### I'm getting memory errors, how do I fix them?

1. **Increase Node.js memory limit**:
   ```bash
   export NODE_OPTIONS="--max-old-space-size=4096"
   ```

2. **Enable garbage collection**:
   ```javascript
   afterEach(() => {
     if (global.gc) global.gc();
   });
   ```

3. **Check for memory leaks**:
   ```bash
   npx test-integration run --detect-memory-leaks
   ```

### Tests pass locally but fail in CI, why?

Common causes:
1. **Timing differences** - Use appropriate timeouts
2. **Environment variables** - Ensure CI has required variables
3. **File permissions** - Check file access in CI
4. **Resource limits** - CI may have memory/CPU constraints
5. **Race conditions** - Tests may depend on execution order

### How do I debug configuration issues?

```bash
# Validate configuration
npx test-integration config --validate

# Show resolved configuration
npx test-integration config --show

# Enable debug logging
DEBUG=test-integration:* npm test
```

## Advanced Usage

### Can I write custom plugins?

Yes! The system supports custom plugins:

```javascript
// custom-plugin.js
module.exports = {
  name: 'my-custom-plugin',
  version: '1.0.0',

  beforeTestRun(config) {
    console.log('Starting tests...');
  },

  afterTestRun(results) {
    console.log(`Tests completed: ${results.summary.total}`);
  }
};

// Configuration
module.exports = {
  plugins: {
    enabled: ['./custom-plugin.js']
  }
};
```

### How do I extend the reporting system?

```javascript
// custom-reporter.js
class CustomReporter {
  constructor(config) {
    this.config = config;
  }

  generateReport(results) {
    // Custom report generation logic
    return {
      format: 'custom',
      content: this.formatResults(results)
    };
  }

  formatResults(results) {
    // Format results as needed
    return JSON.stringify(results, null, 2);
  }
}

module.exports = CustomReporter;
```

### Can I integrate with external monitoring systems?

Yes! Use webhooks or custom integrations:

```javascript
module.exports = {
  integrations: {
    datadog: {
      enabled: true,
      apiKey: process.env.DATADOG_API_KEY,
      tags: ['env:test', 'team:qa']
    },
    customWebhook: {
      url: 'https://monitoring.example.com/webhook',
      events: ['test-complete', 'regression-detected']
    }
  }
};
```

## Migration

### How do I migrate from plain Jest/Mocha/etc.?

1. **Install the integration system**:
   ```bash
   npm install test-framework-integrations
   ```

2. **Create configuration file**:
   ```bash
   npx test-integration init
   ```

3. **Update package.json scripts**:
   ```json
   {
     "scripts": {
       "test": "test-integration run",
       "test:watch": "test-integration run --watch"
     }
   }
   ```

4. **Gradually enable features**:
   ```javascript
   module.exports = {
     framework: { type: 'jest' },
     baseline: { enabled: true },
     performance: { enabled: true }
   };
   ```

### Will this break my existing tests?

No! The system is designed to be backward compatible. Your existing tests will continue to work without modification.

### How do I migrate baseline data from another system?

```bash
# Import baselines from external format
npx test-integration baseline import --format sonarqube --file baseline.json

# Convert between formats
npx test-integration baseline convert --from legacy --to current
```

## Support and Community

### Where can I get help?

1. **Documentation** - Check the comprehensive documentation
2. **GitHub Issues** - Report bugs and request features
3. **Discussions** - Ask questions and share solutions
4. **Stack Overflow** - Tag questions with `test-framework-integrations`

### How do I report a bug?

1. **Check existing issues** first
2. **Use the issue template** with:
   - Environment details
   - Configuration
   - Steps to reproduce
   - Expected vs actual behavior
3. **Include diagnostic output**:
   ```bash
   npx test-integration doctor --output diagnosis.json
   ```

### How can I contribute?

1. **Fork the repository**
2. **Create a feature branch**
3. **Write tests** for your changes
4. **Follow the coding standards**
5. **Submit a pull request**

See the [Developer Guide](../developer/README.md) for detailed contribution guidelines.

### Is there a roadmap for future features?

Yes! Check the GitHub repository for:
- **Milestones** - Planned releases
- **Projects** - Feature development boards
- **Discussions** - Feature requests and ideas

---

Can't find your question? [Ask in our discussions](https://github.com/test-framework-integrations/discussions) or [check our documentation](../README.md).