# Playwright Integration Guide

Complete guide for integrating Test Framework Integrations with Playwright, the modern end-to-end testing framework.

## 📚 Overview

Playwright is a framework for Web Testing and Automation that allows testing Chromium, Firefox and WebKit with a single API. This guide covers:
- **Installation and Setup**: Getting Playwright working with Test Framework Integrations
- **Configuration**: Optimizing Playwright for baseline tracking and performance monitoring
- **Advanced Features**: Custom reporters, parallel execution, and cross-browser testing
- **Best Practices**: Tips for optimal Playwright integration

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Install Playwright and Test Framework Integrations
npm install --save-dev @playwright/test test-framework-integrations

# Install browsers
npx playwright install

# Optional: Additional utilities
npm install --save-dev @playwright/test-reporter @playwright/experimental-ct-react
```

### 2. Basic Configuration

Create `playwright.config.js`:

```javascript
// playwright.config.js
const { defineConfig, devices } = require('@playwright/test');
const TestFrameworkIntegrations = require('test-framework-integrations');

module.exports = defineConfig({
  // Test directory
  testDir: './tests',

  // Parallel execution
  fullyParallel: true,

  // Fail the build on CI if you accidentally left test.only in the source code
  forbidOnly: !!process.env.CI,

  // Retry on CI only
  retries: process.env.CI ? 2 : 0,

  // Opt out of parallel tests on CI
  workers: process.env.CI ? 1 : undefined,

  // Test timeout
  timeout: 30 * 1000,

  // Global test setup
  globalSetup: require.resolve('./tests/global-setup.js'),
  globalTeardown: require.resolve('./tests/global-teardown.js'),

  // Configure expect options
  expect: {
    timeout: 5000,
    toHaveScreenshot: { threshold: 0.2, mode: 'pixel' },
    toMatchSnapshot: { threshold: 0.2 }
  },

  // Reporter configuration
  reporter: [
    ['html'],
    ['json', { outputFile: 'test-results/results.json' }],
    [require.resolve('./tests/reporters/integration-reporter.js')]
  ],

  // Global test configuration
  use: {
    // Browser options
    headless: true,
    viewport: { width: 1280, height: 720 },
    ignoreHTTPSErrors: true,

    // Capture options
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    trace: 'on-first-retry',

    // Base URL for tests
    baseURL: process.env.BASE_URL || 'http://localhost:3000',

    // Test Framework Integration options
    testIntegration: {
      enabled: true,
      coverage: false, // Usually not needed for E2E tests
      profiling: true,
      baseline: process.env.BASELINE_FILE
    }
  },

  // Configure projects for major browsers
  projects: [
    {
      name: 'chromium',
      use: {
        ...devices['Desktop Chrome'],
        // Enable additional Chrome features
        launchOptions: {
          args: ['--disable-dev-shm-usage', '--disable-gpu']
        }
      },
    },
    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },
    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },

    // Mobile browsers
    {
      name: 'Mobile Chrome',
      use: { ...devices['Pixel 5'] },
    },
    {
      name: 'Mobile Safari',
      use: { ...devices['iPhone 12'] },
    },

    // Branded browsers
    {
      name: 'Microsoft Edge',
      use: { ...devices['Desktop Edge'], channel: 'msedge' },
    },
    {
      name: 'Google Chrome',
      use: { ...devices['Desktop Chrome'], channel: 'chrome' },
    },
  ],

  // Run your local dev server before starting the tests
  webServer: {
    command: 'npm run start',
    url: 'http://localhost:3000',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000,
  },
});
```

### 3. Global Setup

Create `tests/global-setup.js`:

```javascript
// tests/global-setup.js
const TestFrameworkIntegrations = require('test-framework-integrations');

async function globalSetup(config) {
  console.log('🎭 Setting up Playwright Integration...');

  // Initialize Test Framework Integration
  global.testIntegration = new TestFrameworkIntegrations({
    framework: 'playwright',
    coverage: false, // E2E tests typically don't need code coverage
    profiling: true,
    baseline: process.env.BASELINE_FILE || './baseline.json',
    reporter: 'console'
  });

  try {
    await global.testIntegration.initialize();
    console.log('✅ Playwright Integration initialized');
  } catch (error) {
    console.error('❌ Failed to initialize Playwright Integration:', error);
    throw error;
  }

  // Setup test data, start services, etc.
  await setupTestData();
  await startServices();
}

async function setupTestData() {
  // Initialize test database, create test users, etc.
  console.log('📊 Setting up test data...');
}

async function startServices() {
  // Start external services if needed
  console.log('🚀 Starting services...');
}

module.exports = globalSetup;
```

Create `tests/global-teardown.js`:

```javascript
// tests/global-teardown.js
async function globalTeardown(config) {
  console.log('🧹 Cleaning up Playwright Integration...');

  // Cleanup integration
  if (global.testIntegration) {
    await global.testIntegration.stopTests();
  }

  // Cleanup test data and services
  await cleanupTestData();
  await stopServices();

  console.log('✅ Cleanup complete');
}

async function cleanupTestData() {
  console.log('🗑️  Cleaning up test data...');
}

async function stopServices() {
  console.log('⏹️  Stopping services...');
}

module.exports = globalTeardown;
```

### 4. Custom Playwright Reporter

Create `tests/reporters/integration-reporter.js`:

```javascript
// tests/reporters/integration-reporter.js
const TestFrameworkIntegrations = require('test-framework-integrations');

class PlaywrightIntegrationReporter {
  constructor(options = {}) {
    this.options = options;
    this.integration = null;
    this.results = {
      tests: [],
      summary: {
        total: 0,
        passed: 0,
        failed: 0,
        skipped: 0,
        flaky: 0,
        duration: 0
      }
    };
  }

  async onBegin(config, suite) {
    console.log('🎭 Playwright Integration Reporter - Starting tests');

    // Initialize integration
    this.integration = new TestFrameworkIntegrations({
      framework: 'playwright',
      profiling: true,
      baseline: process.env.BASELINE_FILE,
      reporter: 'console'
    });

    try {
      await this.integration.initialize();
    } catch (error) {
      console.error('Failed to initialize integration:', error);
    }

    // Count total tests
    this.results.summary.total = suite.allTests().length;
    console.log(`📊 Running ${this.results.summary.total} tests`);
  }

  onTestBegin(test, result) {
    if (this.integration) {
      this.integration.emit('testStarted', {
        testName: test.title,
        suite: test.parent?.title || 'root',
        project: result.workerIndex,
        browser: test.project()?.name
      });
    }
  }

  onTestEnd(test, result) {
    const testResult = {
      name: test.title,
      suite: test.parent?.title || 'root',
      status: this.mapPlaywrightStatus(result.status),
      duration: result.duration,
      browser: test.project()?.name,
      retry: result.retry,
      error: result.error?.message,
      attachments: result.attachments.length
    };

    this.results.tests.push(testResult);

    // Update summary
    switch (result.status) {
      case 'passed':
        this.results.summary.passed++;
        break;
      case 'failed':
        this.results.summary.failed++;
        break;
      case 'skipped':
        this.results.summary.skipped++;
        break;
      case 'timedOut':
        this.results.summary.failed++;
        break;
      case 'interrupted':
        this.results.summary.failed++;
        break;
    }

    if (result.retry > 0 && result.status === 'passed') {
      this.results.summary.flaky++;
    }

    // Emit to integration
    if (this.integration) {
      this.integration.emit('testCompleted', testResult);
    }
  }

  async onEnd(result) {
    this.results.summary.duration = result.duration;

    console.log('\n🎭 Playwright Integration Results:');
    console.log(`✅ Passed: ${this.results.summary.passed}`);
    console.log(`❌ Failed: ${this.results.summary.failed}`);
    console.log(`⏸️  Skipped: ${this.results.summary.skipped}`);
    console.log(`🔄 Flaky: ${this.results.summary.flaky}`);
    console.log(`⏱️  Duration: ${this.results.summary.duration}ms`);

    if (this.integration) {
      // Convert to integration format
      const integrationResults = this.convertPlaywrightResults();

      // Save baseline if requested
      if (process.env.SAVE_BASELINE === 'true') {
        await this.integration.saveBaseline(integrationResults, 'latest');
        console.log('💾 Baseline saved');
      }

      // Compare with baseline
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

  mapPlaywrightStatus(status) {
    const statusMap = {
      'passed': 'passed',
      'failed': 'failed',
      'skipped': 'skipped',
      'timedOut': 'failed',
      'interrupted': 'failed'
    };
    return statusMap[status] || 'unknown';
  }

  convertPlaywrightResults() {
    return {
      framework: {
        name: 'playwright',
        version: require('@playwright/test/package.json').version,
        adapter: 'PlaywrightAdapter'
      },
      tests: this.results.tests,
      summary: {
        ...this.results.summary,
        success: this.results.summary.failed === 0
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

module.exports = PlaywrightIntegrationReporter;
```

### 5. Update Package.json Scripts

```json
{
  "scripts": {
    "test:e2e": "playwright test",
    "test:e2e:headed": "playwright test --headed",
    "test:e2e:debug": "playwright test --debug",
    "test:e2e:ui": "playwright test --ui",
    "test:e2e:chrome": "playwright test --project=chromium",
    "test:e2e:firefox": "playwright test --project=firefox",
    "test:e2e:webkit": "playwright test --project=webkit",
    "test:e2e:mobile": "playwright test --project='Mobile Chrome'",
    "test:e2e:integration": "node run-playwright-integration.js",
    "test:e2e:baseline": "BASELINE_FILE=./baseline.json playwright test",
    "test:e2e:report": "playwright show-report"
  }
}
```

## 🧪 Test Examples

### Basic Page Test

```javascript
// tests/homepage.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Homepage', () => {
  test('should display welcome message', async ({ page }) => {
    await page.goto('/');

    await expect(page.locator('h1')).toContainText('Welcome');
    await expect(page.locator('nav')).toBeVisible();
  });

  test('should navigate to about page', async ({ page }) => {
    await page.goto('/');

    await page.click('text=About');
    await expect(page).toHaveURL('/about');
    await expect(page.locator('h1')).toContainText('About Us');
  });

  test('should be responsive', async ({ page }) => {
    // Test desktop view
    await page.setViewportSize({ width: 1200, height: 800 });
    await page.goto('/');
    await expect(page.locator('.desktop-nav')).toBeVisible();

    // Test mobile view
    await page.setViewportSize({ width: 375, height: 667 });
    await expect(page.locator('.mobile-nav')).toBeVisible();
    await expect(page.locator('.desktop-nav')).toBeHidden();
  });
});
```

### Form Interaction Test

```javascript
// tests/contact-form.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Contact Form', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/contact');
  });

  test('should submit form successfully', async ({ page }) => {
    // Fill form
    await page.fill('[data-testid="name"]', 'John Doe');
    await page.fill('[data-testid="email"]', 'john@example.com');
    await page.fill('[data-testid="message"]', 'Hello, this is a test message.');

    // Submit form
    await page.click('[data-testid="submit"]');

    // Verify success
    await expect(page.locator('.success-message')).toBeVisible();
    await expect(page.locator('.success-message')).toContainText('Thank you for your message');
  });

  test('should validate required fields', async ({ page }) => {
    // Try to submit empty form
    await page.click('[data-testid="submit"]');

    // Check validation messages
    await expect(page.locator('[data-testid="name-error"]')).toContainText('Name is required');
    await expect(page.locator('[data-testid="email-error"]')).toContainText('Email is required');
    await expect(page.locator('[data-testid="message-error"]')).toContainText('Message is required');
  });

  test('should validate email format', async ({ page }) => {
    await page.fill('[data-testid="name"]', 'John Doe');
    await page.fill('[data-testid="email"]', 'invalid-email');
    await page.fill('[data-testid="message"]', 'Test message');

    await page.click('[data-testid="submit"]');

    await expect(page.locator('[data-testid="email-error"]')).toContainText('Please enter a valid email');
  });
});
```

### Performance-Aware Test

```javascript
// tests/performance.spec.js
const { test, expect } = require('@playwright/test');

test.describe('Performance Tests', () => {
  test('should load homepage within performance budget', async ({ page }) => {
    const startTime = Date.now();

    // Navigate to page
    await page.goto('/', { waitUntil: 'networkidle' });

    const loadTime = Date.now() - startTime;

    // Performance assertions
    expect(loadTime).toBeLessThan(3000); // Should load within 3 seconds

    // Check Core Web Vitals
    const metrics = await page.evaluate(() => {
      return new Promise((resolve) => {
        new PerformanceObserver((list) => {
          const entries = list.getEntries();
          const vitals = {};

          entries.forEach((entry) => {
            switch (entry.name) {
              case 'first-contentful-paint':
                vitals.fcp = entry.value;
                break;
              case 'largest-contentful-paint':
                vitals.lcp = entry.value;
                break;
              case 'cumulative-layout-shift':
                vitals.cls = entry.value;
                break;
            }
          });

          resolve(vitals);
        }).observe({ entryTypes: ['paint', 'largest-contentful-paint', 'layout-shift'] });

        // Fallback timeout
        setTimeout(() => resolve({}), 5000);
      });
    });

    // Assert Core Web Vitals
    if (metrics.fcp) {
      expect(metrics.fcp).toBeLessThan(1800); // FCP should be under 1.8s
    }
    if (metrics.lcp) {
      expect(metrics.lcp).toBeLessThan(2500); // LCP should be under 2.5s
    }
    if (metrics.cls) {
      expect(metrics.cls).toBeLessThan(0.1); // CLS should be under 0.1
    }
  });

  test('should handle large data sets efficiently', async ({ page }) => {
    const startTime = Date.now();

    // Navigate to page with large dataset
    await page.goto('/users?limit=1000');

    // Wait for table to load
    await page.waitForSelector('[data-testid="users-table"]');
    await page.waitForFunction(
      () => document.querySelectorAll('[data-testid="user-row"]').length > 0
    );

    const renderTime = Date.now() - startTime;

    // Should render large dataset within reasonable time
    expect(renderTime).toBeLessThan(5000);

    // Check if virtualization is working (only visible rows rendered)
    const totalRows = await page.locator('[data-testid="user-row"]').count();
    expect(totalRows).toBeLessThan(100); // Should virtualize to ~50-100 visible rows
  });
});
```

### Cross-Browser Test

```javascript
// tests/cross-browser.spec.js
const { test, expect, devices } = require('@playwright/test');

// Test across different browsers
['chromium', 'firefox', 'webkit'].forEach(browserName => {
  test.describe(`Cross-browser tests - ${browserName}`, () => {
    test.use({
      ...devices['Desktop Chrome'],
      browserName
    });

    test('should work consistently across browsers', async ({ page, browserName }) => {
      await page.goto('/');

      // Basic functionality should work the same
      await expect(page.locator('h1')).toBeVisible();
      await expect(page.locator('nav')).toBeVisible();

      // Test browser-specific features
      if (browserName === 'webkit') {
        // Safari-specific tests
        await expect(page.locator('.safari-feature')).toBeVisible();
      }

      // Screenshot comparison across browsers
      await expect(page).toHaveScreenshot(`homepage-${browserName}.png`);
    });

    test('should handle JavaScript features', async ({ page, browserName }) => {
      await page.goto('/interactive');

      // Test ES6+ features
      await page.click('[data-testid="modern-js-button"]');
      await expect(page.locator('[data-testid="result"]')).toContainText('Success');

      // Test async/await
      await page.click('[data-testid="async-button"]');
      await page.waitForSelector('[data-testid="async-result"]');
      await expect(page.locator('[data-testid="async-result"]')).toContainText('Loaded');
    });
  });
});
```

### Mobile-Specific Tests

```javascript
// tests/mobile.spec.js
const { test, expect, devices } = require('@playwright/test');

test.describe('Mobile Tests', () => {
  test.use({ ...devices['iPhone 12'] });

  test('should work on mobile devices', async ({ page }) => {
    await page.goto('/');

    // Test mobile navigation
    await page.click('[data-testid="mobile-menu-button"]');
    await expect(page.locator('[data-testid="mobile-menu"]')).toBeVisible();

    // Test touch interactions
    await page.tap('[data-testid="touch-button"]');
    await expect(page.locator('[data-testid="touch-result"]')).toBeVisible();
  });

  test('should handle swipe gestures', async ({ page }) => {
    await page.goto('/gallery');

    // Get initial image
    const initialImage = await page.locator('[data-testid="current-image"]').getAttribute('src');

    // Swipe left
    await page.touchscreen.tap(300, 400);
    await page.mouse.move(300, 400);
    await page.mouse.down();
    await page.mouse.move(100, 400);
    await page.mouse.up();

    // Wait for swipe animation
    await page.waitForTimeout(500);

    // Verify image changed
    const newImage = await page.locator('[data-testid="current-image"]').getAttribute('src');
    expect(newImage).not.toBe(initialImage);
  });

  test('should handle device orientation', async ({ page }) => {
    // Portrait mode
    await page.setViewportSize({ width: 375, height: 667 });
    await page.goto('/');
    await expect(page.locator('[data-testid="portrait-layout"]')).toBeVisible();

    // Landscape mode
    await page.setViewportSize({ width: 667, height: 375 });
    await expect(page.locator('[data-testid="landscape-layout"]')).toBeVisible();
  });
});
```

## 🔧 Advanced Configuration

### Fixtures and Page Object Model

```javascript
// tests/fixtures/base.js
const { test as base, expect } = require('@playwright/test');

// Extend base test with custom fixtures
const test = base.extend({
  // Custom page fixture with common setup
  appPage: async ({ page }, use) => {
    // Setup authentication, common headers, etc.
    await page.addInitScript(() => {
      window.localStorage.setItem('test-mode', 'true');
    });

    await page.goto('/');
    await use(page);
  },

  // API client fixture
  apiClient: async ({ request }, use) => {
    const client = {
      async createUser(userData) {
        return await request.post('/api/users', { data: userData });
      },
      async getUser(id) {
        return await request.get(`/api/users/${id}`);
      },
      async deleteUser(id) {
        return await request.delete(`/api/users/${id}`);
      }
    };
    await use(client);
  },

  // Test data fixture
  testData: async ({}, use) => {
    const data = {
      users: [
        { name: 'John Doe', email: 'john@example.com' },
        { name: 'Jane Smith', email: 'jane@example.com' }
      ],
      products: [
        { name: 'Product 1', price: 99.99 },
        { name: 'Product 2', price: 149.99 }
      ]
    };
    await use(data);
  }
});

module.exports = { test, expect };
```

### Page Object Model

```javascript
// tests/pages/HomePage.js
class HomePage {
  constructor(page) {
    this.page = page;

    // Selectors
    this.header = page.locator('header');
    this.navigation = page.locator('nav');
    this.welcomeMessage = page.locator('h1');
    this.searchBox = page.locator('[data-testid="search"]');
    this.searchButton = page.locator('[data-testid="search-button"]');
  }

  async goto() {
    await this.page.goto('/');
    await this.page.waitForLoadState('networkidle');
  }

  async search(query) {
    await this.searchBox.fill(query);
    await this.searchButton.click();
    await this.page.waitForLoadState('networkidle');
  }

  async navigateTo(section) {
    await this.navigation.locator(`text=${section}`).click();
    await this.page.waitForLoadState('networkidle');
  }

  async getWelcomeText() {
    return await this.welcomeMessage.textContent();
  }

  async isNavigationVisible() {
    return await this.navigation.isVisible();
  }
}

module.exports = HomePage;
```

```javascript
// tests/example-with-pom.spec.js
const { test, expect } = require('./fixtures/base');
const HomePage = require('./pages/HomePage');

test.describe('Homepage with Page Object Model', () => {
  test('should display welcome message', async ({ appPage }) => {
    const homePage = new HomePage(appPage);
    await homePage.goto();

    const welcomeText = await homePage.getWelcomeText();
    expect(welcomeText).toContain('Welcome');

    const isNavVisible = await homePage.isNavigationVisible();
    expect(isNavVisible).toBe(true);
  });

  test('should perform search', async ({ appPage }) => {
    const homePage = new HomePage(appPage);
    await homePage.goto();
    await homePage.search('test query');

    await expect(appPage.locator('[data-testid="search-results"]')).toBeVisible();
  });
});
```

## ⚡ Performance Optimization

### Parallel Test Execution

```javascript
// playwright.config.parallel.js
module.exports = {
  // Enable full parallelization
  fullyParallel: true,

  // Configure workers
  workers: process.env.CI ? 2 : undefined,

  // Optimize for parallel execution
  use: {
    // Isolate tests
    contextOptions: {
      ignoreHTTPSErrors: true,
    },

    // Faster test execution
    actionTimeout: 10000,
    navigationTimeout: 30000,
  },

  // Projects for parallel browser testing
  projects: [
    {
      name: 'chromium-desktop',
      use: { ...devices['Desktop Chrome'] },
      testMatch: '**/*.spec.js'
    },
    {
      name: 'firefox-desktop',
      use: { ...devices['Desktop Firefox'] },
      testMatch: '**/*.spec.js'
    },
    {
      name: 'webkit-desktop',
      use: { ...devices['Desktop Safari'] },
      testMatch: '**/*.spec.js'
    },
    {
      name: 'mobile-chrome',
      use: { ...devices['Pixel 5'] },
      testMatch: '**/mobile.*.spec.js'
    }
  ],

  // Optimize test sharding
  shard: process.env.CI ? { total: 4, current: 1 } : undefined
};
```

### Performance Monitoring

```javascript
// tests/helpers/performance-monitor.js
class PlaywrightPerformanceMonitor {
  constructor(page) {
    this.page = page;
    this.metrics = new Map();
  }

  async startMonitoring(testName) {
    this.metrics.set(testName, {
      startTime: Date.now(),
      startMemory: await this.getMemoryUsage()
    });

    // Start performance monitoring
    await this.page.addInitScript(() => {
      window.performance.mark('test-start');
    });
  }

  async stopMonitoring(testName) {
    const metrics = this.metrics.get(testName);
    if (!metrics) return null;

    const endTime = Date.now();
    const endMemory = await this.getMemoryUsage();

    await this.page.evaluate(() => {
      window.performance.mark('test-end');
      window.performance.measure('test-duration', 'test-start', 'test-end');
    });

    const performanceEntries = await this.page.evaluate(() => {
      return JSON.stringify(performance.getEntriesByType('measure'));
    });

    const result = {
      name: testName,
      duration: endTime - metrics.startTime,
      memoryDelta: endMemory - metrics.startMemory,
      performanceEntries: JSON.parse(performanceEntries)
    };

    this.metrics.delete(testName);
    return result;
  }

  async getMemoryUsage() {
    try {
      return await this.page.evaluate(() => {
        return performance.memory ? performance.memory.usedJSHeapSize : 0;
      });
    } catch {
      return 0;
    }
  }

  async getNetworkMetrics() {
    return await this.page.evaluate(() => {
      const navigation = performance.getEntriesByType('navigation')[0];
      return {
        dns: navigation.domainLookupEnd - navigation.domainLookupStart,
        tcp: navigation.connectEnd - navigation.connectStart,
        request: navigation.responseStart - navigation.requestStart,
        response: navigation.responseEnd - navigation.responseStart,
        domComplete: navigation.domComplete - navigation.navigationStart,
        loadComplete: navigation.loadEventEnd - navigation.navigationStart
      };
    });
  }

  async getCoreWebVitals() {
    return await this.page.evaluate(() => {
      return new Promise((resolve) => {
        const vitals = {};

        new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            switch (entry.name) {
              case 'first-contentful-paint':
                vitals.fcp = entry.value;
                break;
              case 'largest-contentful-paint':
                vitals.lcp = entry.value;
                break;
            }
          });
        }).observe({ entryTypes: ['paint', 'largest-contentful-paint'] });

        // CLS tracking
        let cls = 0;
        new PerformanceObserver((list) => {
          list.getEntries().forEach((entry) => {
            if (!entry.hadRecentInput) {
              cls += entry.value;
            }
          });
          vitals.cls = cls;
        }).observe({ entryTypes: ['layout-shift'] });

        setTimeout(() => resolve(vitals), 3000);
      });
    });
  }
}

module.exports = PlaywrightPerformanceMonitor;
```

## 🚀 CI/CD Integration

### GitHub Actions Configuration

```yaml
# .github/workflows/playwright.yml
name: Playwright Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    timeout-minutes: 60
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]
        shard: [1, 2, 3, 4]

    steps:
    - uses: actions/checkout@v3

    - name: Use Node.js ${{ matrix.node-version }}
      uses: actions/setup-node@v3
      with:
        node-version: ${{ matrix.node-version }}
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Install Playwright Browsers
      run: npx playwright install --with-deps

    - name: Run Playwright tests
      run: npx playwright test --shard=${{ matrix.shard }}/4
      env:
        CI: true
        BASELINE_FILE: ./baselines/main.json
        SAVE_BASELINE: ${{ github.ref == 'refs/heads/main' }}

    - name: Upload Playwright Report
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: playwright-report-${{ matrix.node-version }}-${{ matrix.shard }}
        path: playwright-report/
        retention-days: 30

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-${{ matrix.node-version }}-${{ matrix.shard }}
        path: test-results/
        retention-days: 30

  merge-reports:
    if: always()
    needs: [test]
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3

    - name: Setup Node.js
      uses: actions/setup-node@v3
      with:
        node-version: 18
        cache: 'npm'

    - name: Install dependencies
      run: npm ci

    - name: Download all reports
      uses: actions/download-artifact@v3
      with:
        path: all-reports/

    - name: Merge reports
      run: npx playwright merge-reports --reporter html ./all-reports/playwright-report-*

    - name: Upload merged report
      uses: actions/upload-artifact@v3
      with:
        name: merged-playwright-report
        path: playwright-report/
```

### Integration Script

```javascript
// run-playwright-integration.js
const TestFrameworkIntegrations = require('test-framework-integrations');
const { execSync } = require('child_process');
const fs = require('fs').promises;
const path = require('path');

async function runPlaywrightIntegration() {
  console.log('🎭 Starting Playwright Integration Tests\n');

  const integration = new TestFrameworkIntegrations({
    framework: 'playwright',
    coverage: false,
    profiling: true,
    baseline: process.env.BASELINE_FILE,
    reporter: ['console', 'json']
  });

  try {
    // Initialize integration
    await integration.initialize();

    // Run Playwright tests
    console.log('🚀 Running Playwright tests...');
    const playwrightResults = execSync('playwright test --reporter=json', {
      encoding: 'utf8',
      stdio: ['inherit', 'pipe', 'inherit']
    });

    const playwrightData = JSON.parse(playwrightResults);

    // Process results through integration
    const integrationResults = await integration.processPlaywrightResults(playwrightData);

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
    const summaryPath = path.join(process.cwd(), 'test-results', 'playwright-integration-summary.json');
    await fs.mkdir(path.dirname(summaryPath), { recursive: true });
    await fs.writeFile(summaryPath, JSON.stringify(integrationResults, null, 2));

    // Print summary
    console.log('\n📊 Integration Test Summary:');
    console.log(`Tests: ${integrationResults.summary.passed}/${integrationResults.summary.total}`);
    console.log(`Duration: ${integrationResults.summary.duration}ms`);
    console.log(`Flaky tests: ${integrationResults.summary.flaky || 0}`);

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

module.exports = runPlaywrightIntegration;

// Run if called directly
if (require.main === module) {
  runPlaywrightIntegration();
}
```

## 🔧 Troubleshooting

### Common Issues

#### Issue: Flaky Tests
**Problem**: Tests pass sometimes but fail other times.

**Solution**:
```javascript
// Use proper waits
await page.waitForSelector('[data-testid="element"]');
await page.waitForLoadState('networkidle');

// Use auto-waiting assertions
await expect(page.locator('[data-testid="element"]')).toBeVisible();

// Configure timeouts appropriately
test.setTimeout(60000);
```

#### Issue: Tests Too Slow
**Problem**: Playwright tests take too long to execute.

**Solution**:
```javascript
// Optimize test configuration
module.exports = {
  use: {
    // Faster navigation
    navigationTimeout: 15000,
    actionTimeout: 5000,

    // Disable unnecessary features
    video: 'retain-on-failure',
    screenshot: 'only-on-failure',
    trace: 'retain-on-failure'
  },

  // Enable parallel execution
  fullyParallel: true,
  workers: 4
};
```

#### Issue: Browser Launch Failures
**Problem**: Browsers fail to launch in CI environment.

**Solution**:
```javascript
// playwright.config.js
module.exports = {
  use: {
    launchOptions: {
      args: [
        '--disable-dev-shm-usage',
        '--disable-gpu',
        '--no-sandbox',
        '--disable-setuid-sandbox'
      ]
    }
  }
};
```

### Performance Tips

1. **Use Auto-waiting**: Rely on Playwright's built-in waiting mechanisms
2. **Optimize Selectors**: Use data-testid attributes for stable selectors
3. **Parallel Execution**: Enable fullyParallel for independent tests
4. **Resource Management**: Disable unnecessary video/trace collection
5. **Test Isolation**: Ensure tests don't depend on each other

## 📚 Additional Resources

- **[Playwright Documentation](https://playwright.dev/)** - Official Playwright documentation
- **[Playwright Test](https://playwright.dev/docs/test-intro)** - Test runner documentation
- **[Best Practices](https://playwright.dev/docs/best-practices)** - Playwright testing best practices
- **[CI/CD Examples](https://playwright.dev/docs/ci)** - Continuous integration examples