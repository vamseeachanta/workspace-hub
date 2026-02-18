# Interactive Examples and Code Samples

## Overview

This directory contains comprehensive examples and code samples that demonstrate the capabilities of the Test Framework Integrations system. Each example is designed to be runnable and includes detailed explanations of the concepts being demonstrated.

## Getting Started with Examples

### Prerequisites

```bash
# Clone the repository
git clone https://github.com/test-framework-integrations/test-framework-integrations.git
cd test-framework-integrations

# Install dependencies
npm install

# Install example dependencies
cd docs/examples
npm install
```

### Running Examples

Each example can be run independently:

```bash
# Run a specific example
npm run example:basic-usage
npm run example:jest-integration
npm run example:performance-monitoring

# Run all examples
npm run examples:all

# Interactive example selector
npm run examples:interactive
```

## Example Categories

### 1. Basic Usage Examples

#### [Basic Test Execution](./basic-usage/)

Demonstrates the simplest way to use the Test Framework Integrations system.

```javascript
// examples/basic-usage/basic-test.js
const TestFrameworkIntegrations = require('test-framework-integrations');

async function runBasicTest() {
  const integration = new TestFrameworkIntegrations({
    framework: {
      type: 'jest'
    },
    execution: {
      coverage: true
    }
  });

  await integration.initialize();

  const results = await integration.runTests({
    testPaths: ['tests/sample.test.js']
  });

  console.log('Test Results:', results.summary);
}

runBasicTest().catch(console.error);
```

#### [Configuration Examples](./configuration/)

Shows different configuration patterns and their use cases.

```javascript
// examples/configuration/development.config.js
module.exports = {
  framework: {
    type: 'jest',
    testDir: 'src',
    testPattern: '**/*.test.{js,ts}'
  },
  execution: {
    mode: 'parallel',
    maxWorkers: 2,
    watch: true,
    coverage: true
  },
  baseline: {
    enabled: true,
    autoSave: true
  },
  reporting: {
    formats: ['console', 'html'],
    detailed: true
  }
};
```

### 2. Framework Integration Examples

#### [Jest Integration](./frameworks/jest/)

Complete Jest integration with custom reporters and setup.

```javascript
// examples/frameworks/jest/jest.config.js
module.exports = {
  testEnvironment: 'node',
  collectCoverage: true,
  coverageDirectory: 'coverage',
  coverageReporters: ['html', 'json', 'lcov'],

  // Integration with Test Framework Integrations
  reporters: [
    'default',
    ['test-framework-integrations/reporters/jest', {
      outputFile: 'test-results/jest-results.json',
      includeConsoleOutput: true
    }]
  ],

  setupFilesAfterEnv: ['<rootDir>/test-setup.js']
};
```

#### [Mocha Integration](./frameworks/mocha/)

Mocha integration with custom hooks and reporting.

```javascript
// examples/frameworks/mocha/.mocharc.json
{
  "require": ["test-framework-integrations/hooks/mocha"],
  "reporter": "test-framework-integrations/reporters/mocha",
  "timeout": 10000,
  "recursive": true,
  "spec": "tests/**/*.test.js"
}
```

#### [Playwright Integration](./frameworks/playwright/)

End-to-end testing with Playwright and cross-browser support.

```javascript
// examples/frameworks/playwright/playwright.config.ts
import { defineConfig } from '@playwright/test';
import { PlaywrightIntegration } from 'test-framework-integrations/adapters/playwright';

export default defineConfig({
  testDir: './tests',

  use: {
    baseURL: 'http://localhost:3000',
    trace: 'on-first-retry',
  },

  // Integration configuration
  reporter: [
    ['html'],
    ['test-framework-integrations/reporters/playwright', {
      outputFile: 'test-results/playwright-results.json'
    }]
  ],

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
  ],
});
```

### 3. Advanced Configuration Examples

#### [Multi-Framework Setup](./advanced/multi-framework/)

Running multiple testing frameworks in a single project.

```javascript
// examples/advanced/multi-framework/test-integration.config.js
module.exports = {
  framework: {
    type: 'multi',
    configurations: {
      unit: {
        type: 'jest',
        testDir: 'src',
        testPattern: '**/*.test.js',
        coverage: true
      },
      integration: {
        type: 'jest',
        testDir: 'tests/integration',
        testPattern: '**/*.integration.test.js',
        setupFiles: ['./tests/integration/setup.js']
      },
      e2e: {
        type: 'playwright',
        testDir: 'tests/e2e',
        testPattern: '**/*.e2e.test.js'
      }
    }
  },
  execution: {
    mode: 'sequential', // Run frameworks sequentially
    coverage: true
  },
  baseline: {
    enabled: true,
    directory: 'baselines',
    autoSave: true
  }
};

// Usage
const integration = new TestFrameworkIntegrations(config);

// Run all frameworks
await integration.runTests();

// Run specific framework
await integration.runTests({ framework: 'unit' });
```

#### [Performance Monitoring](./advanced/performance/)

Comprehensive performance monitoring and alerting setup.

```javascript
// examples/advanced/performance/performance.config.js
module.exports = {
  framework: {
    type: 'jest'
  },
  performance: {
    enabled: true,
    collectMetrics: ['duration', 'memory', 'cpu'],
    thresholds: {
      testDuration: 5000,
      suiteDuration: 30000,
      memoryUsage: 256 * 1024 * 1024
    },
    profiling: {
      enabled: true,
      sampleRate: 1000,
      outputFormat: 'json'
    },
    monitoring: {
      realTime: true,
      interval: 1000,
      alerts: {
        enabled: true,
        thresholdMultiplier: 1.5,
        channels: ['console', 'webhook']
      }
    }
  },
  baseline: {
    enabled: true,
    includePerformance: true,
    comparison: {
      tolerance: {
        performance: 0.1, // 10% tolerance
        memory: 0.2       // 20% tolerance
      }
    }
  }
};
```

### 4. Baseline Management Examples

#### [Baseline Creation and Comparison](./baseline/basic/)

Basic baseline management workflows.

```javascript
// examples/baseline/basic/baseline-demo.js
const TestFrameworkIntegrations = require('test-framework-integrations');

async function baselineDemo() {
  const integration = new TestFrameworkIntegrations({
    framework: { type: 'jest' },
    baseline: {
      enabled: true,
      directory: 'baselines',
      autoSave: false // Manual control for demo
    }
  });

  await integration.initialize();

  // Run tests and create baseline
  console.log('Creating initial baseline...');
  const initialResults = await integration.runTests({
    testPaths: ['tests/stable.test.js']
  });

  await integration.saveBaseline('main-v1.0', initialResults);
  console.log('Baseline saved as "main-v1.0"');

  // Simulate code changes and compare
  console.log('\nRunning tests after changes...');
  const newResults = await integration.runTests({
    testPaths: ['tests/stable.test.js']
  });

  const comparison = await integration.compareWithBaseline('main-v1.0', newResults);

  if (comparison.hasChanges) {
    console.log('Changes detected:');
    comparison.differences.forEach(diff => {
      console.log(`- ${diff.field}: ${diff.oldValue} → ${diff.newValue}`);
    });
  } else {
    console.log('No significant changes detected');
  }
}

baselineDemo().catch(console.error);
```

#### [Advanced Baseline Storage](./baseline/storage/)

Using different storage backends for baselines.

```javascript
// examples/baseline/storage/s3-storage.js
module.exports = {
  framework: { type: 'jest' },
  baseline: {
    enabled: true,
    storage: {
      type: 's3',
      options: {
        bucket: 'my-test-baselines',
        region: 'us-east-1',
        prefix: 'project-name',
        encryption: 'AES256'
      }
    },
    compression: 'gzip',
    retention: {
      maxAge: '30d',
      maxCount: 50
    }
  }
};
```

### 5. Plugin Examples

#### [Custom Reporter Plugin](./plugins/custom-reporter/)

Building a custom reporter plugin.

```javascript
// examples/plugins/custom-reporter/slack-reporter.js
const { Plugin } = require('test-framework-integrations');

class SlackReporterPlugin extends Plugin {
  constructor() {
    super('slack-reporter', '1.0.0');
  }

  async initialize(context) {
    this.webhookUrl = context.config.slack?.webhookUrl;
    this.context = context;

    if (!this.webhookUrl) {
      throw new Error('Slack webhook URL is required');
    }

    // Listen for test completion
    context.eventBus.on('test:complete', this.sendSlackNotification.bind(this));
  }

  async sendSlackNotification(data) {
    const { results } = data;
    const message = this.formatMessage(results);

    try {
      await fetch(this.webhookUrl, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(message)
      });

      this.context.logger.info('Slack notification sent');
    } catch (error) {
      this.context.logger.error('Failed to send Slack notification:', error);
    }
  }

  formatMessage(results) {
    const { summary } = results;
    const color = summary.failed > 0 ? 'danger' : 'good';

    return {
      attachments: [{
        color,
        title: '🧪 Test Results',
        fields: [
          { title: 'Total', value: summary.total.toString(), short: true },
          { title: 'Passed', value: summary.passed.toString(), short: true },
          { title: 'Failed', value: summary.failed.toString(), short: true },
          { title: 'Duration', value: `${results.duration}ms`, short: true }
        ]
      }]
    };
  }
}

module.exports = SlackReporterPlugin;
```

#### [Storage Plugin Example](./plugins/storage/)

Custom storage backend implementation.

```javascript
// examples/plugins/storage/redis-storage.js
const redis = require('redis');
const { StorageProvider } = require('test-framework-integrations');

class RedisStorageProvider extends StorageProvider {
  constructor(config) {
    super();
    this.client = redis.createClient(config);
    this.prefix = config.prefix || 'test-integration:';
  }

  async store(key, data) {
    const serialized = JSON.stringify(data);
    await this.client.set(`${this.prefix}${key}`, serialized);
  }

  async load(key) {
    const data = await this.client.get(`${this.prefix}${key}`);
    return data ? JSON.parse(data) : null;
  }

  async delete(key) {
    const result = await this.client.del(`${this.prefix}${key}`);
    return result > 0;
  }

  async exists(key) {
    const result = await this.client.exists(`${this.prefix}${key}`);
    return result === 1;
  }

  async list(pattern = '*') {
    const keys = await this.client.keys(`${this.prefix}${pattern}`);
    return keys.map(key => key.replace(this.prefix, ''));
  }
}

module.exports = RedisStorageProvider;
```

### 6. CI/CD Integration Examples

#### [GitHub Actions](./ci-cd/github-actions/)

Complete GitHub Actions workflow with matrix testing.

```yaml
# examples/ci-cd/github-actions/.github/workflows/test.yml
name: Test Suite

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16, 18, 20]
        test-suite: [unit, integration, e2e]

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Run ${{ matrix.test-suite }} tests
      run: npm run test:${{ matrix.test-suite }}
      env:
        CI: true
        TEST_FRAMEWORK: jest
        BASELINE_ENABLED: true
        PERFORMANCE_ENABLED: true

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.node-version }}-${{ matrix.test-suite }}
        path: |
          test-results/
          coverage/
          baselines/

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      if: matrix.test-suite == 'unit'
      with:
        file: coverage/coverage-final.json

    - name: Comment PR with results
      uses: actions/github-script@v7
      if: github.event_name == 'pull_request' && matrix.test-suite == 'unit'
      with:
        script: |
          const fs = require('fs');
          const path = 'test-results/results.json';

          if (fs.existsSync(path)) {
            const results = JSON.parse(fs.readFileSync(path));
            const comment = `
            ## Test Results 🧪

            - ✅ Passed: ${results.summary.passed}
            - ❌ Failed: ${results.summary.failed}
            - ⏭️ Skipped: ${results.summary.skipped}
            - 📊 Coverage: ${results.coverage?.overall || 'N/A'}%
            `;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
          }
```

#### [Docker Integration](./ci-cd/docker/)

Containerized testing environment.

```dockerfile
# examples/ci-cd/docker/Dockerfile.test
FROM node:18-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache git

# Install Chrome for Playwright (if needed)
RUN apk add --no-cache \
    chromium \
    nss \
    freetype \
    freetype-dev \
    harfbuzz \
    ca-certificates \
    ttf-freefont

ENV PUPPETEER_SKIP_CHROMIUM_DOWNLOAD=true
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium-browser

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Create directories for outputs
RUN mkdir -p test-results coverage baselines

# Set up environment
ENV CI=true
ENV NODE_ENV=test

# Run tests
CMD ["npm", "test"]
```

```yaml
# examples/ci-cd/docker/docker-compose.test.yml
version: '3.8'

services:
  test-runner:
    build:
      context: .
      dockerfile: Dockerfile.test
    environment:
      - CI=true
      - TEST_FRAMEWORK=jest
      - BASELINE_ENABLED=true
      - PERFORMANCE_ENABLED=true
    volumes:
      - ./test-results:/app/test-results
      - ./coverage:/app/coverage
      - ./baselines:/app/baselines
    networks:
      - test-network

  redis:
    image: redis:alpine
    networks:
      - test-network

  postgres:
    image: postgres:13-alpine
    environment:
      POSTGRES_DB: testdb
      POSTGRES_USER: testuser
      POSTGRES_PASSWORD: testpass
    networks:
      - test-network

networks:
  test-network:
    driver: bridge
```

### 7. Real-World Scenarios

#### [Microservices Testing](./scenarios/microservices/)

Testing strategy for microservices architecture.

```javascript
// examples/scenarios/microservices/test-strategy.js
module.exports = {
  framework: {
    type: 'multi',
    configurations: {
      // Unit tests for each service
      'user-service': {
        type: 'jest',
        testDir: 'services/user-service/tests',
        testPattern: '**/*.test.js'
      },
      'order-service': {
        type: 'jest',
        testDir: 'services/order-service/tests',
        testPattern: '**/*.test.js'
      },

      // Integration tests
      integration: {
        type: 'jest',
        testDir: 'tests/integration',
        testPattern: '**/*.integration.test.js',
        setupFiles: ['./tests/integration/setup.js']
      },

      // End-to-end tests
      e2e: {
        type: 'playwright',
        testDir: 'tests/e2e',
        testPattern: '**/*.e2e.test.js'
      }
    }
  },

  execution: {
    mode: 'parallel',
    maxWorkers: 4
  },

  baseline: {
    enabled: true,
    comparison: {
      tolerance: {
        performance: 0.15, // 15% tolerance for microservices
        coverage: 0.05
      }
    }
  },

  reporting: {
    formats: ['json', 'html', 'junit'],
    aggregated: true // Combine results from all services
  }
};
```

#### [Legacy System Integration](./scenarios/legacy/)

Integrating with existing legacy test suites.

```javascript
// examples/scenarios/legacy/migration-strategy.js
const TestFrameworkIntegrations = require('test-framework-integrations');

class LegacyMigrationStrategy {
  constructor() {
    this.integration = new TestFrameworkIntegrations({
      framework: {
        type: 'multi',
        configurations: {
          // Keep existing legacy tests
          legacy: {
            type: 'custom',
            testCommand: './run-legacy-tests.sh',
            resultParser: 'legacy-xml'
          },

          // New tests using modern framework
          modern: {
            type: 'jest',
            testDir: 'tests/modern',
            testPattern: '**/*.test.js'
          }
        }
      }
    });
  }

  async runMigrationPhase(phase) {
    switch (phase) {
      case 'baseline':
        return await this.createBaseline();
      case 'parallel':
        return await this.runParallelTests();
      case 'cutover':
        return await this.performCutover();
      default:
        throw new Error(`Unknown migration phase: ${phase}`);
    }
  }

  async createBaseline() {
    // Run legacy tests to establish baseline
    const legacyResults = await this.integration.runTests({
      framework: 'legacy'
    });

    await this.integration.saveBaseline('legacy-baseline', legacyResults);
    return legacyResults;
  }

  async runParallelTests() {
    // Run both legacy and modern tests
    const [legacyResults, modernResults] = await Promise.all([
      this.integration.runTests({ framework: 'legacy' }),
      this.integration.runTests({ framework: 'modern' })
    ]);

    // Compare results for consistency
    const comparison = this.compareTestResults(legacyResults, modernResults);
    return { legacyResults, modernResults, comparison };
  }

  async performCutover() {
    // Final validation before switching to modern tests only
    const results = await this.integration.runTests({
      framework: 'modern'
    });

    const baselineComparison = await this.integration.compareWithBaseline(
      'legacy-baseline',
      results
    );

    if (baselineComparison.hasRegression) {
      throw new Error('Regression detected during cutover');
    }

    return results;
  }

  compareTestResults(legacy, modern) {
    // Custom comparison logic for legacy vs modern test results
    return {
      coverageMatch: this.compareCoverage(legacy.coverage, modern.coverage),
      testCountMatch: legacy.summary.total === modern.summary.total,
      consistentResults: this.compareTestOutcomes(legacy.tests, modern.tests)
    };
  }
}

module.exports = LegacyMigrationStrategy;
```

## Interactive Tutorials

### Tutorial 1: Getting Started

```javascript
// examples/tutorials/01-getting-started/tutorial.js
const readline = require('readline');
const TestFrameworkIntegrations = require('test-framework-integrations');

class GettingStartedTutorial {
  constructor() {
    this.rl = readline.createInterface({
      input: process.stdin,
      output: process.stdout
    });
  }

  async run() {
    console.log('🚀 Welcome to Test Framework Integrations Tutorial!');
    console.log('This interactive tutorial will guide you through the basics.\n');

    await this.step1_introduction();
    await this.step2_configuration();
    await this.step3_runningTests();
    await this.step4_baselines();
    await this.step5_reporting();

    console.log('\n🎉 Congratulations! You\'ve completed the tutorial.');
    this.rl.close();
  }

  async step1_introduction() {
    console.log('📚 Step 1: Introduction');
    console.log('Test Framework Integrations provides unified testing across multiple frameworks.');

    await this.waitForUser('Press Enter to continue...');
  }

  async step2_configuration() {
    console.log('\n⚙️ Step 2: Configuration');
    console.log('Let\'s create a basic configuration:');

    const config = {
      framework: {
        type: 'jest'
      },
      execution: {
        coverage: true
      }
    };

    console.log(JSON.stringify(config, null, 2));

    await this.waitForUser('Press Enter to continue...');
  }

  // Additional steps...

  async waitForUser(prompt) {
    return new Promise(resolve => {
      this.rl.question(prompt, () => resolve());
    });
  }
}

// Run tutorial
new GettingStartedTutorial().run().catch(console.error);
```

### Tutorial 2: Advanced Features

```javascript
// examples/tutorials/02-advanced-features/performance-tutorial.js
const TestFrameworkIntegrations = require('test-framework-integrations');

class PerformanceTutorial {
  async run() {
    console.log('📈 Performance Monitoring Tutorial');

    // Step 1: Enable performance monitoring
    const integration = new TestFrameworkIntegrations({
      framework: { type: 'jest' },
      performance: {
        enabled: true,
        collectMetrics: ['duration', 'memory'],
        thresholds: {
          testDuration: 1000, // 1 second
          memoryUsage: 50 * 1024 * 1024 // 50MB
        }
      }
    });

    await integration.initialize();

    // Step 2: Run tests with performance monitoring
    console.log('Running tests with performance monitoring...');

    const results = await integration.runTests({
      testPaths: ['examples/tutorials/02-advanced-features/sample-tests']
    });

    // Step 3: Analyze performance data
    this.analyzePerformance(results.performance);

    // Step 4: Set up alerts
    await this.setupPerformanceAlerts(integration);
  }

  analyzePerformance(performanceData) {
    console.log('\n📊 Performance Analysis:');

    const slowTests = performanceData.tests
      .filter(test => test.duration > 500)
      .sort((a, b) => b.duration - a.duration);

    if (slowTests.length > 0) {
      console.log('🐌 Slow tests detected:');
      slowTests.forEach(test => {
        console.log(`  - ${test.name}: ${test.duration}ms`);
      });
    }

    const memoryIntensive = performanceData.tests
      .filter(test => test.memoryUsage > 10 * 1024 * 1024)
      .sort((a, b) => b.memoryUsage - a.memoryUsage);

    if (memoryIntensive.length > 0) {
      console.log('🧠 Memory-intensive tests:');
      memoryIntensive.forEach(test => {
        console.log(`  - ${test.name}: ${(test.memoryUsage / 1024 / 1024).toFixed(2)}MB`);
      });
    }
  }

  async setupPerformanceAlerts(integration) {
    console.log('\n🚨 Setting up performance alerts...');

    integration.on('performance:threshold-exceeded', (data) => {
      console.log(`⚠️ Performance alert: ${data.test} exceeded ${data.metric} threshold`);
      console.log(`   Expected: ${data.threshold}, Actual: ${data.actual}`);
    });

    console.log('Performance alerts configured!');
  }
}

new PerformanceTutorial().run().catch(console.error);
```

## Example Package Scripts

```json
{
  "scripts": {
    "examples:install": "cd docs/examples && npm install",
    "examples:all": "node scripts/run-all-examples.js",
    "examples:interactive": "node scripts/interactive-examples.js",

    "example:basic-usage": "node docs/examples/basic-usage/basic-test.js",
    "example:jest-integration": "cd docs/examples/frameworks/jest && npm test",
    "example:mocha-integration": "cd docs/examples/frameworks/mocha && npm test",
    "example:playwright-integration": "cd docs/examples/frameworks/playwright && npm test",
    "example:performance-monitoring": "node docs/examples/advanced/performance/performance-demo.js",
    "example:baseline-management": "node docs/examples/baseline/basic/baseline-demo.js",
    "example:multi-framework": "node docs/examples/advanced/multi-framework/multi-demo.js",

    "tutorial:getting-started": "node docs/examples/tutorials/01-getting-started/tutorial.js",
    "tutorial:advanced": "node docs/examples/tutorials/02-advanced-features/performance-tutorial.js",

    "example:docker": "cd docs/examples/ci-cd/docker && docker-compose -f docker-compose.test.yml up",
    "example:microservices": "node docs/examples/scenarios/microservices/microservices-demo.js"
  }
}
```

## Contributing Examples

We welcome contributions of new examples and improvements to existing ones. Please follow these guidelines:

1. **Create a clear directory structure** with descriptive names
2. **Include a README.md** explaining what the example demonstrates
3. **Provide runnable code** with minimal setup required
4. **Add comments** explaining key concepts
5. **Include error handling** to make examples robust
6. **Test your examples** before submitting

### Example Template

```
examples/
├── category-name/
│   ├── example-name/
│   │   ├── README.md
│   │   ├── package.json
│   │   ├── config.js
│   │   ├── demo.js
│   │   └── tests/
│   │       └── sample.test.js
│   └── ...
```

This comprehensive examples collection provides hands-on learning experiences for all aspects of the Test Framework Integrations system, from basic usage to advanced enterprise scenarios.