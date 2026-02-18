# Vitest Integration Guide

## Overview

This guide covers integrating the Test Framework Integrations system with Vitest, the next-generation testing framework powered by Vite. The integration provides unified test execution, baseline tracking, and comprehensive reporting for modern JavaScript/TypeScript projects.

## Installation

### Prerequisites

- Node.js 16+ with npm/yarn/pnpm
- Vite 3.0+ (usually installed with Vitest)
- TypeScript 4.5+ (for TypeScript projects)

### Install Dependencies

```bash
# Install the integration system
npm install test-framework-integrations

# Install Vitest and related packages
npm install -D vitest @vitest/ui @vitest/coverage-v8

# For TypeScript projects
npm install -D typescript @types/node

# Optional: Additional testing utilities
npm install -D @testing-library/jest-dom happy-dom jsdom
```

### Framework-Specific Additions

```bash
# React testing
npm install -D @testing-library/react @testing-library/user-event

# Vue testing
npm install -D @vue/test-utils

# Svelte testing
npm install -D @testing-library/svelte

# Node.js testing utilities
npm install -D @vitest/environment-node
```

## Basic Configuration

### vitest.config.ts

```typescript
import { defineConfig } from 'vitest/config'
import { resolve } from 'path'

export default defineConfig({
  test: {
    // Environment setup
    environment: 'jsdom', // or 'happy-dom', 'node'
    globals: true,
    setupFiles: ['./tests/setup.ts'],

    // File patterns
    include: ['**/*.{test,spec}.{js,mjs,cjs,ts,mts,cts,jsx,tsx}'],
    exclude: ['node_modules', 'dist', '.git', '.cache'],

    // Reporters and output
    reporters: ['default', 'json', 'html'],
    outputFile: {
      json: './test-results/vitest-results.json',
      html: './test-results/index.html'
    },

    // Coverage configuration
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      reportsDirectory: './coverage',
      include: ['src/**/*'],
      exclude: [
        'src/**/*.d.ts',
        'src/**/*.test.{ts,js}',
        'src/**/*.spec.{ts,js}'
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80
        }
      }
    },

    // Performance and parallel execution
    testTimeout: 30000,
    hookTimeout: 10000,
    pool: 'threads',
    poolOptions: {
      threads: {
        singleThread: false,
        maxThreads: 4,
        minThreads: 1
      }
    },

    // Watch mode
    watchExclude: ['**/node_modules/**', '**/dist/**'],

    // Benchmarking
    benchmark: {
      reporters: ['default'],
      outputFile: './benchmarks/results.json'
    }
  },

  // Vite configuration for testing
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
      '~': resolve(__dirname, './src')
    }
  },

  // Define global variables
  define: {
    __TEST__: true,
    __VERSION__: JSON.stringify(process.env.npm_package_version)
  }
})
```

### Integration Configuration

Create `test-integration.config.js`:

```javascript
module.exports = {
  framework: 'vitest',
  testCommand: 'npx vitest run',
  testDir: 'src',
  outputDir: 'test-results',

  // Vitest-specific settings
  configFile: 'vitest.config.ts',
  mode: 'test',

  // Result parsing
  resultFile: 'test-results/vitest-results.json',
  coverageDir: 'coverage',
  benchmarkFile: 'benchmarks/results.json',

  // Baseline configuration
  baseline: {
    enabled: true,
    directory: 'baselines',
    autoSave: true,
    compareThreshold: 0.05,
    includePerformance: true
  },

  // Performance monitoring
  performance: {
    enabled: true,
    thresholds: {
      testDuration: 5000,
      suiteDuration: 30000,
      totalDuration: 300000,
      memoryUsage: 256 * 1024 * 1024
    },
    collectMetrics: ['duration', 'memory', 'cpu']
  },

  // Environment variables
  env: {
    NODE_ENV: 'test',
    CI: process.env.CI || 'false'
  },

  // Watch mode for development
  watch: {
    enabled: process.env.NODE_ENV !== 'ci',
    ignore: ['node_modules/**', 'coverage/**', 'dist/**']
  }
};
```

### Test Setup File

Create `tests/setup.ts`:

```typescript
import { expect, afterEach, beforeAll, afterAll } from 'vitest'
import { cleanup } from '@testing-library/react'
import * as matchers from '@testing-library/jest-dom/matchers'

// Extend Vitest matchers
expect.extend(matchers)

// Global test utilities
declare global {
  interface Window {
    __TEST_INTEGRATION__: any
  }
}

// Performance monitoring
interface TestMetrics {
  startTime: number
  startMemory: number
  name: string
}

const testMetrics = new Map<string, TestMetrics>()

// Setup test environment
beforeAll(() => {
  // Initialize integration system
  if (typeof window !== 'undefined') {
    window.__TEST_INTEGRATION__ = {
      baselines: new Map(),
      performance: new Map(),
      currentTest: null
    }
  }
})

// Cleanup after each test
afterEach(() => {
  cleanup()

  // Clear any timers, mocks, etc.
  vi.clearAllMocks()
  vi.clearAllTimers()
})

// Performance monitoring hooks
export function startPerformanceMonitoring(testName: string) {
  const startTime = performance.now()
  const startMemory = performance.memory?.usedJSHeapSize || 0

  testMetrics.set(testName, {
    startTime,
    startMemory,
    name: testName
  })
}

export function endPerformanceMonitoring(testName: string) {
  const metrics = testMetrics.get(testName)
  if (!metrics) return null

  const endTime = performance.now()
  const endMemory = performance.memory?.usedJSHeapSize || 0

  const result = {
    name: testName,
    duration: endTime - metrics.startTime,
    memoryDelta: endMemory - metrics.startMemory,
    timestamp: new Date().toISOString()
  }

  testMetrics.delete(testName)
  return result
}

// Baseline comparison utilities
export function saveBaseline(name: string, data: any) {
  if (typeof window !== 'undefined' && window.__TEST_INTEGRATION__) {
    window.__TEST_INTEGRATION__.baselines.set(name, {
      data,
      timestamp: new Date().toISOString()
    })
  }
}

export function getBaseline(name: string) {
  if (typeof window !== 'undefined' && window.__TEST_INTEGRATION__) {
    return window.__TEST_INTEGRATION__.baselines.get(name)?.data
  }
  return null
}

// Custom test utilities
export function createMockApiResponse<T>(data: T, delay = 100) {
  return new Promise<T>((resolve) => {
    setTimeout(() => resolve(data), delay)
  })
}

export function waitForNextTick() {
  return new Promise(resolve => process.nextTick(resolve))
}

// Error boundary for React components
export function createErrorBoundary() {
  return class ErrorBoundary extends React.Component {
    constructor(props: any) {
      super(props)
      this.state = { hasError: false }
    }

    static getDerivedStateFromError() {
      return { hasError: true }
    }

    componentDidCatch(error: Error, errorInfo: any) {
      console.error('Test Error Boundary:', error, errorInfo)
    }

    render() {
      if ((this.state as any).hasError) {
        return React.createElement('div', null, 'Something went wrong.')
      }
      return (this.props as any).children
    }
  }
}
```

## Advanced Configuration

### Custom Integration Runner

Create `vitest-integration.js`:

```javascript
const TestFrameworkIntegrations = require('test-framework-integrations');
const { spawn } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

class VitestIntegration {
  constructor(config) {
    this.config = config;
    this.integration = new TestFrameworkIntegrations(config);
    this.metrics = {
      tests: [],
      performance: {},
      coverage: null,
      benchmarks: null
    };
  }

  async runTests(options = {}) {
    try {
      // Initialize integration system
      await this.integration.initialize();

      // Build Vitest command
      const command = this.buildVitestCommand(options);

      // Run tests with monitoring
      const results = await this.runWithMonitoring(command, options);

      // Process and enhance results
      await this.processResults(results);

      // Save baseline if requested
      if (options.saveBaseline) {
        await this.saveBaseline(options.baselineName || 'default', results);
      }

      return results;
    } catch (error) {
      console.error('Vitest integration error:', error);
      throw error;
    }
  }

  buildVitestCommand(options) {
    const args = ['vitest'];

    // Add run mode (default for CI)
    if (!options.watch && !options.ui) {
      args.push('run');
    }

    // Add UI mode
    if (options.ui) {
      args.push('--ui');
    }

    // Add coverage
    if (options.coverage !== false) {
      args.push('--coverage');
    }

    // Add reporter
    if (options.reporter) {
      args.push('--reporter', options.reporter);
    } else {
      args.push('--reporter=default', '--reporter=json');
    }

    // Add test patterns
    if (options.testPathPattern) {
      args.push(options.testPathPattern);
    }

    // Add configuration file
    if (this.config.configFile) {
      args.push('--config', this.config.configFile);
    }

    // Add environment variables
    const env = { ...process.env, ...this.config.env };

    return { command: 'npx', args, env };
  }

  async runWithMonitoring(command, options) {
    return new Promise((resolve, reject) => {
      const startTime = Date.now();
      let stdout = '';
      let stderr = '';

      const process = spawn(command.command, command.args, {
        env: command.env,
        stdio: ['pipe', 'pipe', 'pipe']
      });

      process.stdout.on('data', (data) => {
        stdout += data.toString();
        if (options.onOutput) {
          options.onOutput(data.toString(), 'stdout');
        }
      });

      process.stderr.on('data', (data) => {
        stderr += data.toString();
        if (options.onOutput) {
          options.onOutput(data.toString(), 'stderr');
        }
      });

      process.on('close', async (code) => {
        const endTime = Date.now();
        const duration = endTime - startTime;

        try {
          // Load test results
          const results = await this.loadVitestResults();

          results.execution = {
            exitCode: code,
            duration,
            stdout,
            stderr
          };

          resolve(results);
        } catch (error) {
          reject(error);
        }
      });

      process.on('error', reject);
    });
  }

  async loadVitestResults() {
    const results = {
      framework: 'vitest',
      timestamp: new Date().toISOString(),
      tests: [],
      summary: {}
    };

    // Load main test results
    try {
      const resultData = await fs.readFile(this.config.resultFile, 'utf8');
      const vitestResults = JSON.parse(resultData);

      results.tests = vitestResults.testResults || [];
      results.summary = vitestResults.numTotalTests ? {
        total: vitestResults.numTotalTests,
        passed: vitestResults.numPassedTests,
        failed: vitestResults.numFailedTests,
        skipped: vitestResults.numPendingTests,
        todo: vitestResults.numTodoTests
      } : {};

    } catch (error) {
      console.warn('Could not load Vitest results:', error.message);
    }

    // Load coverage data
    try {
      const coverageFile = path.join(this.config.coverageDir, 'coverage-final.json');
      const coverageData = await fs.readFile(coverageFile, 'utf8');
      results.coverage = JSON.parse(coverageData);
    } catch (error) {
      console.warn('Could not load coverage data:', error.message);
    }

    // Load benchmark data
    try {
      if (this.config.benchmarkFile) {
        const benchmarkData = await fs.readFile(this.config.benchmarkFile, 'utf8');
        results.benchmarks = JSON.parse(benchmarkData);
      }
    } catch (error) {
      console.warn('Could not load benchmark data:', error.message);
    }

    return results;
  }

  async processResults(results) {
    // Calculate additional metrics
    if (results.tests.length > 0) {
      const durations = results.tests
        .filter(test => test.duration)
        .map(test => test.duration);

      if (durations.length > 0) {
        results.performance = {
          averageDuration: durations.reduce((a, b) => a + b, 0) / durations.length,
          maxDuration: Math.max(...durations),
          minDuration: Math.min(...durations),
          totalDuration: durations.reduce((a, b) => a + b, 0)
        };
      }
    }

    // Process coverage metrics
    if (results.coverage) {
      const coverageMetrics = this.calculateCoverageMetrics(results.coverage);
      results.coverageMetrics = coverageMetrics;
    }

    // Add integration metadata
    results.integration = {
      version: require('test-framework-integrations/package.json').version,
      config: this.config,
      timestamp: new Date().toISOString()
    };

    return results;
  }

  calculateCoverageMetrics(coverage) {
    const metrics = {
      lines: { total: 0, covered: 0, percentage: 0 },
      functions: { total: 0, covered: 0, percentage: 0 },
      branches: { total: 0, covered: 0, percentage: 0 },
      statements: { total: 0, covered: 0, percentage: 0 }
    };

    Object.values(coverage).forEach(file => {
      if (file.lines) {
        metrics.lines.total += file.lines.total || 0;
        metrics.lines.covered += file.lines.covered || 0;
      }
      if (file.functions) {
        metrics.functions.total += file.functions.total || 0;
        metrics.functions.covered += file.functions.covered || 0;
      }
      if (file.branches) {
        metrics.branches.total += file.branches.total || 0;
        metrics.branches.covered += file.branches.covered || 0;
      }
      if (file.statements) {
        metrics.statements.total += file.statements.total || 0;
        metrics.statements.covered += file.statements.covered || 0;
      }
    });

    // Calculate percentages
    Object.keys(metrics).forEach(key => {
      const metric = metrics[key];
      metric.percentage = metric.total > 0 ? (metric.covered / metric.total) * 100 : 0;
    });

    return metrics;
  }

  async saveBaseline(name, data) {
    return await this.integration.saveBaseline(name, {
      framework: 'vitest',
      timestamp: new Date().toISOString(),
      ...data
    });
  }

  async compareWithBaseline(name, currentData) {
    return await this.integration.compareWithBaseline(name, currentData);
  }

  async runBenchmarks(options = {}) {
    const command = {
      command: 'npx',
      args: ['vitest', 'bench', '--reporter=json'],
      env: { ...process.env, ...this.config.env }
    };

    if (this.config.configFile) {
      command.args.push('--config', this.config.configFile);
    }

    return await this.runWithMonitoring(command, options);
  }
}

module.exports = VitestIntegration;
```

## Usage Examples

### Basic Test Execution

```javascript
const VitestIntegration = require('./vitest-integration');
const config = require('./test-integration.config');

async function runVitestSuite() {
  const vitest = new VitestIntegration(config);

  try {
    const results = await vitest.runTests({
      coverage: true,
      reporter: 'default',
      testPathPattern: 'src/**/*.test.ts',
      saveBaseline: true,
      baselineName: 'main-branch'
    });

    console.log('Test Results:', results.summary);
    console.log('Performance:', results.performance);
    console.log('Coverage:', results.coverageMetrics);

    // Compare with previous baseline
    const comparison = await vitest.compareWithBaseline('main-branch', results);
    if (comparison.hasRegression) {
      console.warn('Performance regression detected:', comparison.regressions);
    }

  } catch (error) {
    console.error('Test execution failed:', error);
    process.exit(1);
  }
}

runVitestSuite();
```

### React Component Testing

```typescript
// Button.test.tsx
import { describe, it, expect, beforeEach } from 'vitest'
import { render, screen, fireEvent } from '@testing-library/react'
import { Button } from './Button'
import { startPerformanceMonitoring, endPerformanceMonitoring } from '../tests/setup'

describe('Button Component', () => {
  beforeEach(() => {
    startPerformanceMonitoring('Button Component')
  })

  afterEach(() => {
    const metrics = endPerformanceMonitoring('Button Component')
    if (metrics && metrics.duration > 100) {
      console.warn(`Button test took ${metrics.duration}ms - consider optimization`)
    }
  })

  it('renders with correct text', () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole('button')).toHaveTextContent('Click me')
  })

  it('handles click events', async () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    await fireEvent.click(screen.getByRole('button'))
    expect(handleClick).toHaveBeenCalledOnce()
  })

  it('applies custom styling', () => {
    render(<Button className="custom-class">Styled button</Button>)
    expect(screen.getByRole('button')).toHaveClass('custom-class')
  })

  // Performance test
  it('renders quickly with many props', () => {
    const startTime = performance.now()

    render(
      <Button
        size="large"
        variant="primary"
        disabled={false}
        loading={false}
        icon="arrow"
        data-testid="performance-button"
      >
        Complex Button
      </Button>
    )

    const renderTime = performance.now() - startTime
    expect(renderTime).toBeLessThan(10) // Should render in under 10ms
  })
})
```

### API Testing

```typescript
// api.test.ts
import { describe, it, expect, beforeAll, afterAll } from 'vitest'
import { setupServer } from 'msw/node'
import { rest } from 'msw'
import { apiClient } from './api-client'

const server = setupServer(
  rest.get('/api/users', (req, res, ctx) => {
    return res(ctx.json([
      { id: 1, name: 'John Doe', email: 'john@example.com' },
      { id: 2, name: 'Jane Smith', email: 'jane@example.com' }
    ]))
  }),

  rest.post('/api/users', (req, res, ctx) => {
    const newUser = req.body as any
    return res(ctx.json({ id: 3, ...newUser }))
  })
)

beforeAll(() => server.listen())
afterAll(() => server.close())

describe('API Client', () => {
  it('fetches users successfully', async () => {
    const startTime = performance.now()

    const users = await apiClient.getUsers()

    const responseTime = performance.now() - startTime

    expect(users).toHaveLength(2)
    expect(users[0]).toMatchObject({
      id: 1,
      name: 'John Doe',
      email: 'john@example.com'
    })

    // Performance assertion
    expect(responseTime).toBeLessThan(100)

    // Save baseline data
    saveBaseline('api-users-response-time', {
      responseTime,
      userCount: users.length
    })
  })

  it('creates user successfully', async () => {
    const newUser = { name: 'Bob Johnson', email: 'bob@example.com' }

    const createdUser = await apiClient.createUser(newUser)

    expect(createdUser).toMatchObject({
      id: 3,
      ...newUser
    })
  })

  it('handles network errors gracefully', async () => {
    server.use(
      rest.get('/api/users', (req, res, ctx) => {
        return res.networkError('Network error')
      })
    )

    await expect(apiClient.getUsers()).rejects.toThrow('Network error')
  })
})
```

### Benchmark Testing

```typescript
// performance.bench.ts
import { bench, describe } from 'vitest'
import { fibonacci, bubbleSort, quickSort } from './algorithms'

describe('Algorithm Performance', () => {
  bench('fibonacci(30)', () => {
    fibonacci(30)
  })

  bench('fibonacci(35)', () => {
    fibonacci(35)
  })

  bench('bubble sort 1000 items', () => {
    const array = Array.from({ length: 1000 }, () => Math.random())
    bubbleSort([...array])
  })

  bench('quick sort 1000 items', () => {
    const array = Array.from({ length: 1000 }, () => Math.random())
    quickSort([...array])
  })

  // Comparison benchmark
  bench('array methods vs for loops', () => {
    const data = Array.from({ length: 10000 }, (_, i) => i)

    // Using array methods
    const result1 = data
      .filter(x => x % 2 === 0)
      .map(x => x * 2)
      .reduce((sum, x) => sum + x, 0)

    // Using for loops
    let result2 = 0
    for (let i = 0; i < data.length; i++) {
      if (data[i] % 2 === 0) {
        result2 += data[i] * 2
      }
    }
  })
})
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Vitest Integration Tests

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

    steps:
    - name: Checkout code
      uses: actions/checkout@v4

    - name: Setup Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v4
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: |
        npm ci
        npm install test-framework-integrations

    - name: Run tests with integration
      run: |
        node vitest-integration.js
      env:
        CI: true
        NODE_ENV: test

    - name: Run benchmarks
      run: |
        npx vitest bench --reporter=json
      continue-on-error: true

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-node-${{ matrix.node-version }}
        path: |
          test-results/
          coverage/
          benchmarks/

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        directory: ./coverage

    - name: Comment PR with results
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v7
      with:
        script: |
          const fs = require('fs');
          if (fs.existsSync('test-results/vitest-results.json')) {
            const results = JSON.parse(fs.readFileSync('test-results/vitest-results.json'));
            const summary = results.summary;

            const comment = \`
            ## Test Results 🧪

            - ✅ Passed: \${summary.passed}
            - ❌ Failed: \${summary.failed}
            - ⏭️ Skipped: \${summary.skipped}
            - 📊 Total: \${summary.total}

            **Coverage**: Available in artifacts
            **Performance**: Check benchmark results
            \`;

            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
          }
```

### Docker Integration

```dockerfile
# Dockerfile.test
FROM node:18-alpine

WORKDIR /app

# Install system dependencies
RUN apk add --no-cache git

# Copy package files
COPY package*.json ./
COPY vitest.config.ts ./
COPY test-integration.config.js ./

# Install dependencies
RUN npm ci

# Install integration system
RUN npm install test-framework-integrations

# Copy source files
COPY src/ ./src/
COPY tests/ ./tests/

# Copy integration runner
COPY vitest-integration.js ./

# Create output directories
RUN mkdir -p test-results coverage benchmarks

# Run tests
CMD ["node", "vitest-integration.js"]
```

## Best Practices

### Test Organization

```typescript
// tests/helpers/test-utils.tsx
import { render as rtlRender } from '@testing-library/react'
import { ReactElement } from 'react'
import { ThemeProvider } from '../src/components/ThemeProvider'

// Custom render function
function render(ui: ReactElement, options = {}) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return <ThemeProvider>{children}</ThemeProvider>
  }

  return rtlRender(ui, { wrapper: Wrapper, ...options })
}

// Performance testing utilities
export function measurePerformance<T>(
  fn: () => T,
  name: string,
  threshold?: number
): T {
  const start = performance.now()
  const result = fn()
  const duration = performance.now() - start

  if (threshold && duration > threshold) {
    console.warn(`Performance warning: ${name} took ${duration}ms (threshold: ${threshold}ms)`)
  }

  // Store performance data
  if (typeof window !== 'undefined' && window.__TEST_INTEGRATION__) {
    window.__TEST_INTEGRATION__.performance.set(name, {
      duration,
      timestamp: new Date().toISOString()
    })
  }

  return result
}

// Async performance testing
export async function measureAsyncPerformance<T>(
  fn: () => Promise<T>,
  name: string,
  threshold?: number
): Promise<T> {
  const start = performance.now()
  const result = await fn()
  const duration = performance.now() - start

  if (threshold && duration > threshold) {
    console.warn(`Async performance warning: ${name} took ${duration}ms`)
  }

  return result
}

export * from '@testing-library/react'
export { render }
```

### Mock Management

```typescript
// tests/mocks/handlers.ts
import { rest } from 'msw'

export const handlers = [
  // User API
  rest.get('/api/users', (req, res, ctx) => {
    const page = req.url.searchParams.get('page') || '1'
    const limit = req.url.searchParams.get('limit') || '10'

    const users = Array.from({ length: parseInt(limit) }, (_, i) => ({
      id: (parseInt(page) - 1) * parseInt(limit) + i + 1,
      name: `User ${i + 1}`,
      email: `user${i + 1}@example.com`
    }))

    return res(
      ctx.delay(100), // Simulate network delay
      ctx.json({
        data: users,
        pagination: {
          page: parseInt(page),
          limit: parseInt(limit),
          total: 100
        }
      })
    )
  }),

  // Performance testing endpoint
  rest.get('/api/performance-test', (req, res, ctx) => {
    const delay = parseInt(req.url.searchParams.get('delay') || '0')
    return res(
      ctx.delay(delay),
      ctx.json({ message: 'Performance test response', delay })
    )
  }),

  // Error simulation
  rest.get('/api/error-test', (req, res, ctx) => {
    const errorType = req.url.searchParams.get('type')

    switch (errorType) {
      case 'network':
        return res.networkError('Network error simulation')
      case 'timeout':
        return res(ctx.delay(10000))
      case '500':
        return res(ctx.status(500), ctx.json({ error: 'Internal server error' }))
      default:
        return res(ctx.status(400), ctx.json({ error: 'Bad request' }))
    }
  })
]
```

## Troubleshooting

### Common Issues

1. **Configuration File Not Found**
   ```bash
   # Ensure vitest.config.ts exists and is properly formatted
   npx vitest --config vitest.config.ts --run
   ```

2. **Module Resolution Issues**
   ```typescript
   // Add to vitest.config.ts
   export default defineConfig({
     test: {
       alias: {
         '@': path.resolve(__dirname, './src'),
         '~': path.resolve(__dirname, './src')
       }
     }
   })
   ```

3. **Coverage Not Working**
   ```bash
   # Install coverage provider
   npm install -D @vitest/coverage-v8

   # Or use c8
   npm install -D @vitest/coverage-c8
   ```

4. **TypeScript Issues**
   ```typescript
   // Add to vitest.config.ts
   export default defineConfig({
     test: {
       typecheck: {
         enabled: true
       }
     }
   })
   ```

### Debug Configuration

```typescript
// vitest.config.debug.ts
import { defineConfig } from 'vitest/config'

export default defineConfig({
  test: {
    // Enable debug logging
    logLevel: 'info',
    reporter: ['verbose'],

    // Single thread for debugging
    pool: 'forks',
    poolOptions: {
      forks: {
        singleFork: true
      }
    },

    // Longer timeouts for debugging
    testTimeout: 60000,
    hookTimeout: 30000,

    // Debug environment
    env: {
      DEBUG: 'vitest:*',
      NODE_ENV: 'test'
    }
  }
})
```

This comprehensive Vitest integration guide provides everything needed to integrate Vitest with the Test Framework Integrations system, including modern testing patterns, performance monitoring, and CI/CD integration.