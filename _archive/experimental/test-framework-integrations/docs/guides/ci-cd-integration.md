# CI/CD Integration Guide

Complete guide for integrating Test Framework Integrations with various CI/CD platforms and deployment pipelines.

## 📚 Overview

This guide covers how to integrate Test Framework Integrations into your CI/CD workflows across different platforms:
- **GitHub Actions**: Complete workflows for all testing frameworks
- **GitLab CI**: Pipeline configurations and best practices
- **Jenkins**: Pipeline scripts and integrations
- **Azure DevOps**: Build and release pipelines
- **CircleCI**: Configuration and optimization
- **Docker**: Containerized testing environments

## 🎯 General CI/CD Principles

### Environment Variables

Essential environment variables for CI/CD:

```bash
# Framework selection
PREFERRED_FRAMEWORK=jest
FRAMEWORK_FALLBACK_ORDER=jest,vitest,mocha

# Baseline management
BASELINE_FILE=./baselines/main.json
SAVE_BASELINE=true
BASELINE_DIRECTORY=./baselines

# Coverage settings
COVERAGE_ENABLED=true
COVERAGE_THRESHOLD_STATEMENTS=90
COVERAGE_THRESHOLD_BRANCHES=85
COVERAGE_THRESHOLD_FUNCTIONS=90
COVERAGE_THRESHOLD_LINES=90

# Performance monitoring
PROFILING_ENABLED=true
PERFORMANCE_BUDGET_MS=5000
MEMORY_LEAK_DETECTION=true

# Reporting
REPORTER_FORMAT=console,json,html
OUTPUT_DIRECTORY=./test-results

# CI-specific settings
CI=true
NODE_ENV=test
```

### Universal CI Script

Create `scripts/ci-test.js` for consistent CI execution:

```javascript
// scripts/ci-test.js
const TestFrameworkIntegrations = require('test-framework-integrations');
const fs = require('fs').promises;
const path = require('path');

class CITestRunner {
  constructor() {
    this.options = {
      framework: process.env.PREFERRED_FRAMEWORK,
      coverage: process.env.COVERAGE_ENABLED === 'true',
      profiling: process.env.PROFILING_ENABLED === 'true',
      baseline: process.env.BASELINE_FILE,
      reporter: (process.env.REPORTER_FORMAT || 'console').split(','),
      outputDir: process.env.OUTPUT_DIRECTORY || './test-results'
    };

    this.integration = new TestFrameworkIntegrations(this.options);
  }

  async run() {
    try {
      console.log('🚀 Starting CI Test Execution');
      console.log(`Environment: ${process.env.NODE_ENV}`);
      console.log(`Framework: ${this.options.framework || 'auto-detect'}`);
      console.log(`Coverage: ${this.options.coverage}`);
      console.log(`Profiling: ${this.options.profiling}`);

      // Initialize integration
      await this.integration.initialize();

      // Display detected frameworks
      const frameworks = this.integration.getDetectedFrameworks();
      console.log(`\nDetected frameworks: ${frameworks.map(f => f.name).join(', ')}`);

      // Run tests
      const results = await this.integration.runTests({
        bail: process.env.CI === 'true',
        verbose: process.env.VERBOSE === 'true'
      });

      // Process results
      await this.processResults(results);

      // Check if tests passed
      if (results.summary.failed > 0) {
        console.error(`\n❌ ${results.summary.failed} tests failed`);
        process.exit(1);
      } else {
        console.log(`\n✅ All ${results.summary.passed} tests passed`);
      }

    } catch (error) {
      console.error('❌ CI test execution failed:', error);
      process.exit(1);
    }
  }

  async processResults(results) {
    // Save results
    await this.saveResults(results);

    // Check coverage thresholds
    if (results.coverage) {
      await this.checkCoverageThresholds(results.coverage);
    }

    // Check performance budget
    if (results.profiling) {
      await this.checkPerformanceBudget(results.profiling);
    }

    // Handle baseline comparison
    await this.handleBaseline(results);

    // Generate reports
    await this.generateReports(results);
  }

  async saveResults(results) {
    const outputDir = this.options.outputDir;
    await fs.mkdir(outputDir, { recursive: true });

    // Save detailed results
    await fs.writeFile(
      path.join(outputDir, 'test-results.json'),
      JSON.stringify(results, null, 2)
    );

    // Save summary for quick access
    const summary = {
      framework: results.framework.name,
      timestamp: results.timestamp,
      summary: results.summary,
      coverage: results.coverage ? {
        total: results.coverage.total,
        statements: results.coverage.statements,
        branches: results.coverage.branches,
        functions: results.coverage.functions,
        lines: results.coverage.lines
      } : null,
      baseline: results.baseline ? {
        regressions: results.baseline.performance.slower.length,
        improvements: results.baseline.performance.faster.length,
        coverageChange: results.baseline.coverage.change
      } : null
    };

    await fs.writeFile(
      path.join(outputDir, 'summary.json'),
      JSON.stringify(summary, null, 2)
    );
  }

  async checkCoverageThresholds(coverage) {
    const thresholds = {
      statements: parseFloat(process.env.COVERAGE_THRESHOLD_STATEMENTS || 90),
      branches: parseFloat(process.env.COVERAGE_THRESHOLD_BRANCHES || 85),
      functions: parseFloat(process.env.COVERAGE_THRESHOLD_FUNCTIONS || 90),
      lines: parseFloat(process.env.COVERAGE_THRESHOLD_LINES || 90)
    };

    const failures = [];

    Object.entries(thresholds).forEach(([metric, threshold]) => {
      const actual = coverage[metric];
      if (actual < threshold) {
        failures.push({
          metric,
          actual: actual.toFixed(2),
          threshold: threshold.toFixed(2)
        });
      }
    });

    if (failures.length > 0) {
      console.error('\n❌ Coverage thresholds not met:');
      failures.forEach(failure => {
        console.error(`  ${failure.metric}: ${failure.actual}% (required: ${failure.threshold}%)`);
      });

      if (process.env.COVERAGE_STRICT === 'true') {
        process.exit(1);
      }
    } else {
      console.log('\n✅ All coverage thresholds met');
    }
  }

  async checkPerformanceBudget(profiling) {
    const budget = parseInt(process.env.PERFORMANCE_BUDGET_MS || 5000);
    const slowTests = profiling.tests?.filter(test => test.duration > budget) || [];

    if (slowTests.length > 0) {
      console.warn('\n⚠️  Performance budget exceeded:');
      slowTests.forEach(test => {
        console.warn(`  ${test.testName}: ${test.duration}ms (budget: ${budget}ms)`);
      });

      if (process.env.PERFORMANCE_STRICT === 'true') {
        process.exit(1);
      }
    }
  }

  async handleBaseline(results) {
    // Save baseline if requested
    if (process.env.SAVE_BASELINE === 'true') {
      const label = process.env.BASELINE_LABEL || 'ci-' + Date.now();
      await this.integration.saveBaseline(results, label);
      console.log(`💾 Baseline saved: ${label}`);
    }

    // Compare with existing baseline
    if (process.env.BASELINE_FILE && results.baseline) {
      console.log('\n📈 Baseline Comparison:');

      if (results.baseline.performance.slower.length > 0) {
        console.log(`⚠️  Performance regressions: ${results.baseline.performance.slower.length}`);
        results.baseline.performance.slower.slice(0, 3).forEach(test => {
          console.log(`  ${test.name}: +${test.regression}ms`);
        });
      }

      if (results.baseline.performance.faster.length > 0) {
        console.log(`🚀 Performance improvements: ${results.baseline.performance.faster.length}`);
      }

      if (results.baseline.coverage.change !== 0) {
        const sign = results.baseline.coverage.change > 0 ? '+' : '';
        console.log(`📊 Coverage change: ${sign}${results.baseline.coverage.change.toFixed(2)}%`);
      }
    }
  }

  async generateReports(results) {
    if (results.coverage && this.options.reporter.includes('html')) {
      await this.integration.generateCoverageReports('ci-run');
      console.log('📊 Coverage reports generated');
    }

    if (results.profiling) {
      const bottlenecks = this.integration.analyzeBottlenecks();
      await fs.writeFile(
        path.join(this.options.outputDir, 'performance-analysis.json'),
        JSON.stringify(bottlenecks, null, 2)
      );
      console.log('⚡ Performance analysis saved');
    }
  }
}

// Run if called directly
if (require.main === module) {
  const runner = new CITestRunner();
  runner.run();
}

module.exports = CITestRunner;
```

## 🐙 GitHub Actions

### Complete Workflow for All Frameworks

```yaml
# .github/workflows/test-integration.yml
name: Test Framework Integration

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM

env:
  NODE_VERSION: '18.x'
  COVERAGE_THRESHOLD: 90
  PERFORMANCE_BUDGET: 5000

jobs:
  # Detect and validate configuration
  setup:
    runs-on: ubuntu-latest
    outputs:
      frameworks: ${{ steps.detect.outputs.frameworks }}
      matrix: ${{ steps.matrix.outputs.matrix }}
    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Detect frameworks
        id: detect
        run: |
          FRAMEWORKS=$(node -e "
            const TFI = require('test-framework-integrations');
            const tfi = new TFI();
            tfi.initialize().then(() => {
              const frameworks = tfi.getDetectedFrameworks().map(f => f.name);
              console.log(JSON.stringify(frameworks));
            });
          ")
          echo "frameworks=$FRAMEWORKS" >> $GITHUB_OUTPUT

      - name: Generate test matrix
        id: matrix
        run: |
          MATRIX=$(echo '${{ steps.detect.outputs.frameworks }}' | jq -c '{framework: .}')
          echo "matrix=$MATRIX" >> $GITHUB_OUTPUT

  # Unit and integration tests
  test:
    needs: setup
    runs-on: ubuntu-latest
    strategy:
      matrix: ${{ fromJson(needs.setup.outputs.matrix) }}
      fail-fast: false

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run tests with ${{ matrix.framework }}
        run: node scripts/ci-test.js
        env:
          PREFERRED_FRAMEWORK: ${{ matrix.framework }}
          COVERAGE_ENABLED: true
          PROFILING_ENABLED: true
          BASELINE_FILE: ./baselines/${{ github.base_ref || 'main' }}.json
          SAVE_BASELINE: ${{ github.ref == 'refs/heads/main' }}
          COVERAGE_THRESHOLD_STATEMENTS: ${{ env.COVERAGE_THRESHOLD }}
          COVERAGE_THRESHOLD_BRANCHES: 85
          COVERAGE_THRESHOLD_FUNCTIONS: ${{ env.COVERAGE_THRESHOLD }}
          COVERAGE_THRESHOLD_LINES: ${{ env.COVERAGE_THRESHOLD }}
          PERFORMANCE_BUDGET_MS: ${{ env.PERFORMANCE_BUDGET }}

      - name: Upload test results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: test-results-${{ matrix.framework }}
          path: |
            test-results/
            coverage/
          retention-days: 30

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v4
        if: matrix.framework == 'jest'
        with:
          file: ./coverage/lcov.info
          flags: ${{ matrix.framework }}
          name: codecov-${{ matrix.framework }}
          token: ${{ secrets.CODECOV_TOKEN }}

  # End-to-end tests (if Playwright is detected)
  e2e:
    needs: setup
    runs-on: ubuntu-latest
    if: contains(needs.setup.outputs.frameworks, 'playwright')

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright browsers
        run: npx playwright install --with-deps

      - name: Start application
        run: |
          npm run start &
          npx wait-on http://localhost:3000

      - name: Run Playwright tests
        run: node scripts/ci-test.js
        env:
          PREFERRED_FRAMEWORK: playwright
          BASELINE_FILE: ./baselines/e2e-${{ github.base_ref || 'main' }}.json
          SAVE_BASELINE: ${{ github.ref == 'refs/heads/main' }}

      - name: Upload E2E results
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: e2e-results
          path: |
            test-results/
            playwright-report/
          retention-days: 30

  # Multi-framework comparison
  compare:
    needs: [setup, test]
    runs-on: ubuntu-latest
    if: always()

    steps:
      - uses: actions/checkout@v4

      - name: Download all test results
        uses: actions/download-artifact@v4
        with:
          path: all-results/

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: ${{ env.NODE_VERSION }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Generate comparison report
        run: node scripts/compare-frameworks.js
        env:
          RESULTS_DIR: ./all-results

      - name: Comment PR with results
        uses: actions/github-script@v7
        if: github.event_name == 'pull_request'
        with:
          script: |
            const fs = require('fs');
            try {
              const comparison = JSON.parse(fs.readFileSync('comparison-report.json', 'utf8'));

              let comment = `## 🧪 Test Framework Comparison\n\n`;
              comment += `| Framework | Tests | Coverage | Duration |\n`;
              comment += `|-----------|-------|----------|----------|\n`;

              comparison.frameworks.forEach(fw => {
                comment += `| ${fw.name} | ${fw.passed}/${fw.total} | ${fw.coverage}% | ${fw.duration}ms |\n`;
              });

              if (comparison.recommendations.length > 0) {
                comment += `\n### 💡 Recommendations\n`;
                comparison.recommendations.forEach(rec => {
                  comment += `- ${rec}\n`;
                });
              }

              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: comment
              });
            } catch (error) {
              console.log('Could not generate comparison comment:', error);
            }

  # Quality gates
  quality-gate:
    needs: [test, e2e]
    runs-on: ubuntu-latest
    if: always()

    steps:
      - name: Check test results
        run: |
          if [ "${{ needs.test.result }}" != "success" ]; then
            echo "❌ Unit tests failed"
            exit 1
          fi

          if [ "${{ needs.e2e.result }}" == "failure" ]; then
            echo "❌ E2E tests failed"
            exit 1
          fi

          echo "✅ All quality gates passed"
```

### Framework-Specific Workflows

#### Jest-specific workflow:

```yaml
# .github/workflows/jest.yml
name: Jest Tests

on:
  push:
    paths:
      - 'src/**'
      - 'test/**'
      - '__tests__/**'
      - 'jest.config.*'

jobs:
  jest:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [16.x, 18.x, 20.x]

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run Jest with integration
        run: |
          npm run test:integration
        env:
          CI: true
          PREFERRED_FRAMEWORK: jest
          COVERAGE_ENABLED: true
          BASELINE_FILE: ./baselines/jest-main.json

      - name: Jest coverage comment
        uses: MishaKav/jest-coverage-comment@main
        if: github.event_name == 'pull_request'
        with:
          coverage-summary-path: coverage/coverage-summary.json
```

#### Playwright-specific workflow:

```yaml
# .github/workflows/playwright.yml
name: Playwright Tests

on:
  push:
    paths:
      - 'src/**'
      - 'tests/**'
      - 'playwright.config.*'

jobs:
  playwright:
    timeout-minutes: 60
    runs-on: ubuntu-latest
    strategy:
      matrix:
        shard: [1, 2, 3, 4]

    steps:
      - uses: actions/checkout@v4

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: '18.x'
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Install Playwright Browsers
        run: npx playwright install --with-deps

      - name: Run Playwright tests
        run: npx playwright test --shard=${{ matrix.shard }}/4
        env:
          PREFERRED_FRAMEWORK: playwright
          BASELINE_FILE: ./baselines/playwright-main.json

      - name: Upload Playwright Report
        uses: actions/upload-artifact@v4
        if: always()
        with:
          name: playwright-report-${{ matrix.shard }}
          path: playwright-report/
          retention-days: 30
```

## 🦊 GitLab CI

### Complete GitLab CI Configuration

```yaml
# .gitlab-ci.yml
stages:
  - setup
  - test
  - e2e
  - quality
  - deploy

variables:
  NODE_VERSION: "18"
  COVERAGE_THRESHOLD: "90"
  PERFORMANCE_BUDGET: "5000"

# Cache configuration
.cache_template: &cache_template
  cache:
    key:
      files:
        - package-lock.json
    paths:
      - node_modules/
      - .npm/

# Base job template
.test_template: &test_template
  <<: *cache_template
  image: node:${NODE_VERSION}
  before_script:
    - npm ci --cache .npm --prefer-offline

# Setup and framework detection
setup:
  <<: *test_template
  stage: setup
  script:
    - npm ci
    - node -e "
        const TFI = require('test-framework-integrations');
        const tfi = new TFI();
        tfi.initialize().then(() => {
          const frameworks = tfi.getDetectedFrameworks();
          console.log('Detected frameworks:', frameworks.map(f => f.name).join(', '));
        });
      "
  artifacts:
    paths:
      - node_modules/
    expire_in: 1 hour

# Unit tests with parallel framework execution
.test_framework:
  <<: *test_template
  stage: test
  dependencies:
    - setup
  script:
    - node scripts/ci-test.js
  artifacts:
    when: always
    paths:
      - test-results/
      - coverage/
    reports:
      junit: test-results/junit.xml
      coverage_report:
        coverage_format: cobertura
        path: coverage/cobertura-coverage.xml
    expire_in: 1 week
  coverage: '/Statements\s*:\s*(\d+(?:\.\d+)?)%/'

test:jest:
  extends: .test_framework
  variables:
    PREFERRED_FRAMEWORK: "jest"
    COVERAGE_ENABLED: "true"
    PROFILING_ENABLED: "true"
    BASELINE_FILE: "./baselines/jest-main.json"
  only:
    changes:
      - "src/**/*"
      - "test/**/*"
      - "__tests__/**/*"
      - "jest.config.*"
      - "package*.json"

test:mocha:
  extends: .test_framework
  variables:
    PREFERRED_FRAMEWORK: "mocha"
    COVERAGE_ENABLED: "true"
    PROFILING_ENABLED: "true"
    BASELINE_FILE: "./baselines/mocha-main.json"
  only:
    changes:
      - "src/**/*"
      - "test/**/*"
      - ".mocharc.*"
      - "package*.json"

test:vitest:
  extends: .test_framework
  variables:
    PREFERRED_FRAMEWORK: "vitest"
    COVERAGE_ENABLED: "true"
    PROFILING_ENABLED: "true"
    BASELINE_FILE: "./baselines/vitest-main.json"
  only:
    changes:
      - "src/**/*"
      - "test/**/*"
      - "vitest.config.*"
      - "package*.json"

# End-to-end tests
e2e:playwright:
  <<: *test_template
  stage: e2e
  image: mcr.microsoft.com/playwright:v1.40.0-focal
  dependencies:
    - setup
  variables:
    PREFERRED_FRAMEWORK: "playwright"
    BASELINE_FILE: "./baselines/playwright-main.json"
  script:
    - npm ci
    - npx playwright test
  artifacts:
    when: always
    paths:
      - test-results/
      - playwright-report/
    expire_in: 1 week
  only:
    changes:
      - "src/**/*"
      - "tests/**/*"
      - "playwright.config.*"
      - "package*.json"

# Code quality checks
quality:coverage:
  <<: *test_template
  stage: quality
  dependencies:
    - test:jest
  script:
    - |
      COVERAGE=$(node -p "
        const coverage = require('./coverage/coverage-summary.json');
        coverage.total.statements.pct;
      ")
      echo "Coverage: $COVERAGE%"
      if (( $(echo "$COVERAGE < $COVERAGE_THRESHOLD" | bc -l) )); then
        echo "Coverage $COVERAGE% is below threshold $COVERAGE_THRESHOLD%"
        exit 1
      fi
  only:
    - main
    - merge_requests

quality:performance:
  <<: *test_template
  stage: quality
  dependencies:
    - test:jest
  script:
    - |
      node -e "
        const results = require('./test-results/test-results.json');
        const slowTests = results.tests.filter(t => t.duration > $PERFORMANCE_BUDGET);
        if (slowTests.length > 0) {
          console.log('Performance budget exceeded:');
          slowTests.forEach(t => console.log(\`  \${t.name}: \${t.duration}ms\`));
          process.exit(1);
        }
      "

# Baseline management
baseline:save:
  <<: *test_template
  stage: quality
  dependencies:
    - test:jest
    - e2e:playwright
  script:
    - node scripts/save-baseline.js
  artifacts:
    paths:
      - baselines/
  only:
    - main

# Deployment (example)
deploy:staging:
  stage: deploy
  dependencies:
    - quality:coverage
    - quality:performance
  script:
    - echo "Deploying to staging..."
    - # Deployment commands here
  environment:
    name: staging
    url: https://staging.example.com
  only:
    - main
```

### GitLab CI Scripts

Create `scripts/save-baseline.js`:

```javascript
// scripts/save-baseline.js
const TestFrameworkIntegrations = require('test-framework-integrations');
const fs = require('fs').promises;
const path = require('path');

async function saveBaselines() {
  const integration = new TestFrameworkIntegrations();
  await integration.initialize();

  const resultsDir = './test-results';
  const baselinesDir = './baselines';

  // Ensure baselines directory exists
  await fs.mkdir(baselinesDir, { recursive: true });

  // Save baselines for each framework
  const frameworks = ['jest', 'mocha', 'vitest', 'playwright'];

  for (const framework of frameworks) {
    const resultFile = path.join(resultsDir, `${framework}-results.json`);

    try {
      const results = JSON.parse(await fs.readFile(resultFile, 'utf8'));
      const baselineFile = path.join(baselinesDir, `${framework}-main.json`);

      await integration.saveBaseline(results, 'main', baselineFile);
      console.log(`✅ Saved baseline for ${framework}`);
    } catch (error) {
      console.log(`⚠️  No results found for ${framework}`);
    }
  }
}

saveBaselines().catch(console.error);
```

## 🔧 Jenkins

### Jenkinsfile for Test Integration

```groovy
// Jenkinsfile
pipeline {
    agent any

    environment {
        NODE_VERSION = '18'
        COVERAGE_THRESHOLD = '90'
        PERFORMANCE_BUDGET = '5000'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        retry(2)
    }

    stages {
        stage('Setup') {
            steps {
                script {
                    // Use Node.js
                    def nodeHome = tool name: "Node-${NODE_VERSION}", type: 'nodejs'
                    env.PATH = "${nodeHome}/bin:${env.PATH}"
                }

                // Install dependencies
                sh 'npm ci'

                // Detect frameworks
                script {
                    def frameworks = sh(
                        script: '''node -e "
                            const TFI = require('test-framework-integrations');
                            const tfi = new TFI();
                            tfi.initialize().then(() => {
                                const frameworks = tfi.getDetectedFrameworks().map(f => f.name);
                                console.log(frameworks.join(','));
                            });
                        "''',
                        returnStdout: true
                    ).trim()

                    env.DETECTED_FRAMEWORKS = frameworks
                    echo "Detected frameworks: ${frameworks}"
                }
            }
        }

        stage('Test') {
            parallel {
                stage('Jest') {
                    when {
                        expression { env.DETECTED_FRAMEWORKS.contains('jest') }
                    }
                    steps {
                        sh '''
                            export PREFERRED_FRAMEWORK=jest
                            export COVERAGE_ENABLED=true
                            export PROFILING_ENABLED=true
                            export BASELINE_FILE=./baselines/jest-main.json
                            node scripts/ci-test.js
                        '''
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'test-results/jest-results.xml'
                            publishCoverage adapters: [
                                cobertura(path: 'coverage/cobertura-coverage.xml')
                            ]
                        }
                    }
                }

                stage('Mocha') {
                    when {
                        expression { env.DETECTED_FRAMEWORKS.contains('mocha') }
                    }
                    steps {
                        sh '''
                            export PREFERRED_FRAMEWORK=mocha
                            export COVERAGE_ENABLED=true
                            export PROFILING_ENABLED=true
                            export BASELINE_FILE=./baselines/mocha-main.json
                            node scripts/ci-test.js
                        '''
                    }
                    post {
                        always {
                            publishTestResults testResultsPattern: 'test-results/mocha-results.xml'
                        }
                    }
                }

                stage('Playwright') {
                    when {
                        expression { env.DETECTED_FRAMEWORKS.contains('playwright') }
                    }
                    agent {
                        docker {
                            image 'mcr.microsoft.com/playwright:v1.40.0-focal'
                            args '--ipc=host'
                        }
                    }
                    steps {
                        sh '''
                            npm ci
                            export PREFERRED_FRAMEWORK=playwright
                            export BASELINE_FILE=./baselines/playwright-main.json
                            node scripts/ci-test.js
                        '''
                    }
                    post {
                        always {
                            publishHTML([
                                allowMissing: false,
                                alwaysLinkToLastBuild: false,
                                keepAll: true,
                                reportDir: 'playwright-report',
                                reportFiles: 'index.html',
                                reportName: 'Playwright Report'
                            ])
                        }
                    }
                }
            }
        }

        stage('Quality Gates') {
            parallel {
                stage('Coverage Check') {
                    steps {
                        script {
                            def coverage = sh(
                                script: '''node -p "
                                    try {
                                        const coverage = require('./coverage/coverage-summary.json');
                                        coverage.total.statements.pct;
                                    } catch (e) {
                                        0;
                                    }
                                "''',
                                returnStdout: true
                            ).trim() as Float

                            echo "Coverage: ${coverage}%"

                            if (coverage < env.COVERAGE_THRESHOLD as Float) {
                                error "Coverage ${coverage}% is below threshold ${env.COVERAGE_THRESHOLD}%"
                            }
                        }
                    }
                }

                stage('Performance Check') {
                    steps {
                        sh '''
                            node -e "
                                try {
                                    const results = require('./test-results/test-results.json');
                                    const slowTests = results.tests.filter(t => t.duration > ${PERFORMANCE_BUDGET});
                                    if (slowTests.length > 0) {
                                        console.log('Performance budget exceeded:');
                                        slowTests.forEach(t => console.log(\`  \${t.name}: \${t.duration}ms\`));
                                        process.exit(1);
                                    }
                                } catch (e) {
                                    console.log('No performance data available');
                                }
                            "
                        '''
                    }
                }
            }
        }

        stage('Save Baseline') {
            when {
                branch 'main'
            }
            steps {
                sh 'node scripts/save-baseline.js'

                archiveArtifacts artifacts: 'baselines/**/*.json'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'test-results/**/*', allowEmptyArchive: true
            archiveArtifacts artifacts: 'coverage/**/*', allowEmptyArchive: true
            archiveArtifacts artifacts: 'playwright-report/**/*', allowEmptyArchive: true
        }

        success {
            echo 'All tests passed successfully!'
        }

        failure {
            echo 'Tests failed. Check the logs for details.'
            emailext(
                subject: "Test Failure: ${env.JOB_NAME} - ${env.BUILD_NUMBER}",
                body: "Tests failed in ${env.BUILD_URL}",
                to: "${env.CHANGE_AUTHOR_EMAIL}"
            )
        }

        unstable {
            echo 'Tests are unstable. Review the results.'
        }
    }
}
```

## 🔵 Azure DevOps

### Azure Pipelines Configuration

```yaml
# azure-pipelines.yml
trigger:
  branches:
    include:
      - main
      - develop
  paths:
    include:
      - src/*
      - test/*
      - tests/*

pr:
  branches:
    include:
      - main
  paths:
    include:
      - src/*
      - test/*
      - tests/*

variables:
  nodeVersion: '18.x'
  coverageThreshold: 90
  performanceBudget: 5000

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: Test
  displayName: 'Test Stage'
  jobs:
  - job: DetectFrameworks
    displayName: 'Detect Test Frameworks'
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: $(nodeVersion)
      displayName: 'Install Node.js'

    - script: npm ci
      displayName: 'Install dependencies'

    - script: |
        FRAMEWORKS=$(node -e "
          const TFI = require('test-framework-integrations');
          const tfi = new TFI();
          tfi.initialize().then(() => {
            const frameworks = tfi.getDetectedFrameworks().map(f => f.name);
            console.log(JSON.stringify(frameworks));
          });
        ")
        echo "##vso[task.setvariable variable=detectedFrameworks;isOutput=true]$FRAMEWORKS"
      name: 'detectFrameworks'
      displayName: 'Detect frameworks'

  - job: TestJest
    displayName: 'Jest Tests'
    dependsOn: DetectFrameworks
    condition: contains(dependencies.DetectFrameworks.outputs['detectFrameworks.detectedFrameworks'], 'jest')
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: $(nodeVersion)
      displayName: 'Install Node.js'

    - script: npm ci
      displayName: 'Install dependencies'

    - script: |
        export PREFERRED_FRAMEWORK=jest
        export COVERAGE_ENABLED=true
        export PROFILING_ENABLED=true
        export BASELINE_FILE=./baselines/jest-main.json
        node scripts/ci-test.js
      displayName: 'Run Jest tests'

    - task: PublishTestResults@2
      condition: always()
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: 'test-results/jest-results.xml'
        testRunTitle: 'Jest Tests'

    - task: PublishCodeCoverageResults@1
      inputs:
        codeCoverageTool: 'Cobertura'
        summaryFileLocation: 'coverage/cobertura-coverage.xml'
        reportDirectory: 'coverage'

  - job: TestPlaywright
    displayName: 'Playwright E2E Tests'
    dependsOn: DetectFrameworks
    condition: contains(dependencies.DetectFrameworks.outputs['detectFrameworks.detectedFrameworks'], 'playwright')
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: $(nodeVersion)
      displayName: 'Install Node.js'

    - script: npm ci
      displayName: 'Install dependencies'

    - script: npx playwright install --with-deps
      displayName: 'Install Playwright browsers'

    - script: |
        export PREFERRED_FRAMEWORK=playwright
        export BASELINE_FILE=./baselines/playwright-main.json
        node scripts/ci-test.js
      displayName: 'Run Playwright tests'

    - task: PublishTestResults@2
      condition: always()
      inputs:
        testResultsFormat: 'JUnit'
        testResultsFiles: 'test-results/playwright-results.xml'
        testRunTitle: 'Playwright E2E Tests'

- stage: Quality
  displayName: 'Quality Gates'
  dependsOn: Test
  jobs:
  - job: QualityGates
    displayName: 'Quality Gates'
    steps:
    - task: NodeTool@0
      inputs:
        versionSpec: $(nodeVersion)
      displayName: 'Install Node.js'

    - script: npm ci
      displayName: 'Install dependencies'

    - task: DownloadBuildArtifacts@0
      inputs:
        buildType: 'current'
        downloadType: 'specific'
        downloadPath: '$(System.ArtifactsDirectory)'

    - script: |
        COVERAGE=$(node -p "
          try {
            const coverage = require('./coverage/coverage-summary.json');
            coverage.total.statements.pct;
          } catch (e) {
            0;
          }
        ")
        echo "Coverage: $COVERAGE%"
        if (( $(echo "$COVERAGE < $(coverageThreshold)" | bc -l) )); then
          echo "##vso[task.logissue type=error]Coverage $COVERAGE% is below threshold $(coverageThreshold)%"
          exit 1
        fi
      displayName: 'Check coverage threshold'

    - script: |
        node -e "
          try {
            const results = require('./test-results/test-results.json');
            const slowTests = results.tests.filter(t => t.duration > $(performanceBudget));
            if (slowTests.length > 0) {
              console.log('Performance budget exceeded:');
              slowTests.forEach(t => console.log(\`  \${t.name}: \${t.duration}ms\`));
              process.exit(1);
            }
          } catch (e) {
            console.log('No performance data available');
          }
        "
      displayName: 'Check performance budget'

- stage: Deploy
  displayName: 'Deploy Stage'
  dependsOn: Quality
  condition: and(succeeded(), eq(variables['Build.SourceBranch'], 'refs/heads/main'))
  jobs:
  - deployment: DeployToStaging
    displayName: 'Deploy to Staging'
    environment: 'staging'
    strategy:
      runOnce:
        deploy:
          steps:
          - script: echo "Deploying to staging..."
            displayName: 'Deploy application'
```

## 🟣 CircleCI

### CircleCI Configuration

```yaml
# .circleci/config.yml
version: 2.1

orbs:
  node: circleci/node@5.1.0
  codecov: codecov/codecov@3.2.4

executors:
  node-executor:
    docker:
      - image: cimg/node:18.17
    working_directory: ~/project

  playwright-executor:
    docker:
      - image: mcr.microsoft.com/playwright:v1.40.0-focal
    working_directory: ~/project

commands:
  install-dependencies:
    description: "Install Node.js dependencies with caching"
    steps:
      - restore_cache:
          keys:
            - v1-deps-{{ checksum "package-lock.json" }}
            - v1-deps-
      - run:
          name: Install dependencies
          command: npm ci
      - save_cache:
          key: v1-deps-{{ checksum "package-lock.json" }}
          paths:
            - node_modules

  run-framework-tests:
    description: "Run tests for a specific framework"
    parameters:
      framework:
        type: string
      baseline-file:
        type: string
        default: ""
    steps:
      - run:
          name: Run << parameters.framework >> tests
          command: |
            export PREFERRED_FRAMEWORK=<< parameters.framework >>
            export COVERAGE_ENABLED=true
            export PROFILING_ENABLED=true
            <<# parameters.baseline-file >>
            export BASELINE_FILE=<< parameters.baseline-file >>
            <</ parameters.baseline-file >>
            node scripts/ci-test.js
      - store_test_results:
          path: test-results
      - store_artifacts:
          path: test-results
      - store_artifacts:
          path: coverage

jobs:
  setup:
    executor: node-executor
    steps:
      - checkout
      - install-dependencies
      - run:
          name: Detect frameworks
          command: |
            FRAMEWORKS=$(node -e "
              const TFI = require('test-framework-integrations');
              const tfi = new TFI();
              tfi.initialize().then(() => {
                const frameworks = tfi.getDetectedFrameworks().map(f => f.name);
                console.log(frameworks.join(','));
              });
            ")
            echo "export DETECTED_FRAMEWORKS='$FRAMEWORKS'" >> $BASH_ENV
            echo "Detected frameworks: $FRAMEWORKS"
      - persist_to_workspace:
          root: ~/project
          paths:
            - .

  test-jest:
    executor: node-executor
    steps:
      - attach_workspace:
          at: ~/project
      - run-framework-tests:
          framework: "jest"
          baseline-file: "./baselines/jest-main.json"
      - codecov/upload:
          file: coverage/lcov.info
          flags: jest

  test-mocha:
    executor: node-executor
    steps:
      - attach_workspace:
          at: ~/project
      - run-framework-tests:
          framework: "mocha"
          baseline-file: "./baselines/mocha-main.json"

  test-vitest:
    executor: node-executor
    steps:
      - attach_workspace:
          at: ~/project
      - run-framework-tests:
          framework: "vitest"
          baseline-file: "./baselines/vitest-main.json"

  test-playwright:
    executor: playwright-executor
    steps:
      - attach_workspace:
          at: ~/project
      - run:
          name: Install dependencies (Playwright executor)
          command: npm ci
      - run-framework-tests:
          framework: "playwright"
          baseline-file: "./baselines/playwright-main.json"
      - store_artifacts:
          path: playwright-report

  quality-gates:
    executor: node-executor
    steps:
      - attach_workspace:
          at: ~/project
      - run:
          name: Check coverage threshold
          command: |
            COVERAGE=$(node -p "
              try {
                const coverage = require('./coverage/coverage-summary.json');
                coverage.total.statements.pct;
              } catch (e) {
                0;
              }
            ")
            echo "Coverage: $COVERAGE%"
            if (( $(echo "$COVERAGE < 90" | bc -l) )); then
              echo "Coverage $COVERAGE% is below threshold 90%"
              exit 1
            fi
      - run:
          name: Check performance budget
          command: |
            node -e "
              try {
                const results = require('./test-results/test-results.json');
                const slowTests = results.tests.filter(t => t.duration > 5000);
                if (slowTests.length > 0) {
                  console.log('Performance budget exceeded:');
                  slowTests.forEach(t => console.log(\`  \${t.name}: \${t.duration}ms\`));
                  process.exit(1);
                }
              } catch (e) {
                console.log('No performance data available');
              }
            "

  save-baseline:
    executor: node-executor
    steps:
      - attach_workspace:
          at: ~/project
      - run:
          name: Save baselines
          command: node scripts/save-baseline.js
      - store_artifacts:
          path: baselines

workflows:
  version: 2
  test-and-deploy:
    jobs:
      - setup

      - test-jest:
          requires:
            - setup
          filters:
            branches:
              only: /.*/

      - test-mocha:
          requires:
            - setup
          filters:
            branches:
              only: /.*/

      - test-vitest:
          requires:
            - setup
          filters:
            branches:
              only: /.*/

      - test-playwright:
          requires:
            - setup
          filters:
            branches:
              only: /.*/

      - quality-gates:
          requires:
            - test-jest
            - test-mocha
            - test-vitest
            - test-playwright
          filters:
            branches:
              only: /.*/

      - save-baseline:
          requires:
            - quality-gates
          filters:
            branches:
              only: main
```

## 🐳 Docker Integration

### Multi-stage Dockerfile for Testing

```dockerfile
# Dockerfile.test
FROM node:18-alpine AS base

# Install system dependencies for Playwright
RUN apk add --no-cache \
    chromium \
    firefox \
    webkit2gtk \
    ffmpeg

# Set environment variables
ENV PLAYWRIGHT_BROWSERS_PATH=/usr/bin
ENV PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Development stage
FROM base AS development

# Install all dependencies including dev dependencies
RUN npm ci && npm cache clean --force

# Copy source code
COPY . .

# Test stage
FROM development AS test

# Set test environment
ENV NODE_ENV=test
ENV CI=true

# Create test directories
RUN mkdir -p test-results coverage baselines

# Copy test configuration
COPY jest.config.js .
COPY playwright.config.js .
COPY .mocharc.json .

# Run tests
CMD ["node", "scripts/ci-test.js"]

# Multi-framework test stage
FROM test AS test-all-frameworks

# Test all frameworks
RUN node -e "
  const TFI = require('test-framework-integrations');
  const tfi = new TFI();
  tfi.initialize().then(async () => {
    const frameworks = tfi.getDetectedFrameworks();
    for (const fw of frameworks) {
      console.log(\`Testing with \${fw.name}...\`);
      process.env.PREFERRED_FRAMEWORK = fw.name;
      await tfi.runTests();
    }
  });
"

# Production stage
FROM base AS production

# Copy built application
COPY --from=development /app/dist ./dist
COPY --from=development /app/public ./public

EXPOSE 3000

CMD ["npm", "start"]
```

### Docker Compose for Testing

```yaml
# docker-compose.test.yml
version: '3.8'

services:
  # Base test service
  test-base:
    build:
      context: .
      dockerfile: Dockerfile.test
      target: test
    volumes:
      - ./test-results:/app/test-results
      - ./coverage:/app/coverage
      - ./baselines:/app/baselines
    environment:
      - NODE_ENV=test
      - CI=true

  # Jest tests
  test-jest:
    extends: test-base
    environment:
      - PREFERRED_FRAMEWORK=jest
      - COVERAGE_ENABLED=true
      - PROFILING_ENABLED=true
      - BASELINE_FILE=./baselines/jest-main.json
    command: ["node", "scripts/ci-test.js"]

  # Mocha tests
  test-mocha:
    extends: test-base
    environment:
      - PREFERRED_FRAMEWORK=mocha
      - COVERAGE_ENABLED=true
      - PROFILING_ENABLED=true
      - BASELINE_FILE=./baselines/mocha-main.json
    command: ["node", "scripts/ci-test.js"]

  # Playwright E2E tests
  test-playwright:
    build:
      context: .
      dockerfile: Dockerfile.test
      target: test
    volumes:
      - ./test-results:/app/test-results
      - ./playwright-report:/app/playwright-report
      - ./baselines:/app/baselines
    environment:
      - PREFERRED_FRAMEWORK=playwright
      - BASELINE_FILE=./baselines/playwright-main.json
    command: ["npx", "playwright", "test"]
    depends_on:
      - app

  # Application service for E2E tests
  app:
    build:
      context: .
      dockerfile: Dockerfile.test
      target: development
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=test
    command: ["npm", "start"]
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Test results aggregator
  test-aggregator:
    extends: test-base
    depends_on:
      - test-jest
      - test-mocha
      - test-playwright
    command: ["node", "scripts/aggregate-results.js"]
    volumes:
      - ./test-results:/app/test-results:ro
      - ./reports:/app/reports
```

### Running Tests with Docker

```bash
# Run all tests
docker-compose -f docker-compose.test.yml up --build

# Run specific framework tests
docker-compose -f docker-compose.test.yml up test-jest
docker-compose -f docker-compose.test.yml up test-playwright

# Run tests in parallel
docker-compose -f docker-compose.test.yml up --build -d test-jest test-mocha
docker-compose -f docker-compose.test.yml logs -f

# Clean up
docker-compose -f docker-compose.test.yml down -v
```

## 📊 Result Aggregation

### Framework Comparison Script

Create `scripts/compare-frameworks.js`:

```javascript
// scripts/compare-frameworks.js
const fs = require('fs').promises;
const path = require('path');

class FrameworkComparator {
  constructor(resultsDir = './all-results') {
    this.resultsDir = resultsDir;
    this.comparison = {
      frameworks: [],
      recommendations: [],
      summary: {}
    };
  }

  async compare() {
    try {
      const frameworkResults = await this.loadResults();

      // Compare frameworks
      this.comparison.frameworks = frameworkResults.map(fw => ({
        name: fw.name,
        total: fw.results.summary.total,
        passed: fw.results.summary.passed,
        failed: fw.results.summary.failed,
        coverage: fw.results.coverage?.total || 0,
        duration: fw.results.summary.duration,
        efficiency: this.calculateEfficiency(fw.results)
      }));

      // Generate recommendations
      this.generateRecommendations();

      // Create summary
      this.createSummary();

      // Save comparison report
      await fs.writeFile(
        'comparison-report.json',
        JSON.stringify(this.comparison, null, 2)
      );

      console.log('📊 Framework Comparison Report Generated');
      this.displayResults();

    } catch (error) {
      console.error('Failed to compare frameworks:', error);
      process.exit(1);
    }
  }

  async loadResults() {
    const results = [];
    const directories = await fs.readdir(this.resultsDir);

    for (const dir of directories) {
      if (dir.startsWith('test-results-')) {
        const framework = dir.replace('test-results-', '');
        const summaryPath = path.join(this.resultsDir, dir, 'summary.json');

        try {
          const summary = JSON.parse(await fs.readFile(summaryPath, 'utf8'));
          results.push({
            name: framework,
            results: summary
          });
        } catch (error) {
          console.warn(`Could not load results for ${framework}`);
        }
      }
    }

    return results;
  }

  calculateEfficiency(results) {
    // Efficiency = (passed tests / total time) * coverage factor
    const timeEfficiency = results.summary.passed / (results.summary.duration / 1000);
    const coverageFactor = (results.coverage?.total || 0) / 100;
    return timeEfficiency * (1 + coverageFactor);
  }

  generateRecommendations() {
    const frameworks = this.comparison.frameworks;

    // Find fastest framework
    const fastest = frameworks.reduce((prev, current) =>
      prev.duration < current.duration ? prev : current
    );

    // Find best coverage
    const bestCoverage = frameworks.reduce((prev, current) =>
      prev.coverage > current.coverage ? prev : current
    );

    // Find most efficient
    const mostEfficient = frameworks.reduce((prev, current) =>
      prev.efficiency > current.efficiency ? prev : current
    );

    this.comparison.recommendations = [
      `🚀 Fastest execution: ${fastest.name} (${fastest.duration}ms)`,
      `📊 Best coverage: ${bestCoverage.name} (${bestCoverage.coverage.toFixed(2)}%)`,
      `⚡ Most efficient: ${mostEfficient.name} (efficiency: ${mostEfficient.efficiency.toFixed(2)})`
    ];

    // Performance recommendations
    const slowFrameworks = frameworks.filter(fw => fw.duration > 10000);
    if (slowFrameworks.length > 0) {
      this.comparison.recommendations.push(
        `⚠️  Consider optimizing: ${slowFrameworks.map(fw => fw.name).join(', ')} (>10s execution time)`
      );
    }

    // Coverage recommendations
    const lowCoverageFrameworks = frameworks.filter(fw => fw.coverage < 80);
    if (lowCoverageFrameworks.length > 0) {
      this.comparison.recommendations.push(
        `📈 Improve coverage: ${lowCoverageFrameworks.map(fw => fw.name).join(', ')} (<80% coverage)`
      );
    }
  }

  createSummary() {
    const frameworks = this.comparison.frameworks;

    this.comparison.summary = {
      totalFrameworks: frameworks.length,
      totalTests: frameworks.reduce((sum, fw) => sum + fw.total, 0),
      totalPassed: frameworks.reduce((sum, fw) => sum + fw.passed, 0),
      totalFailed: frameworks.reduce((sum, fw) => sum + fw.failed, 0),
      averageCoverage: frameworks.reduce((sum, fw) => sum + fw.coverage, 0) / frameworks.length,
      totalDuration: frameworks.reduce((sum, fw) => sum + fw.duration, 0),
      overallSuccess: frameworks.every(fw => fw.failed === 0)
    };
  }

  displayResults() {
    console.log('\n📊 Framework Comparison Results:');
    console.table(this.comparison.frameworks);

    console.log('\n💡 Recommendations:');
    this.comparison.recommendations.forEach(rec => console.log(`  ${rec}`));

    console.log('\n📈 Summary:');
    console.log(`  Total frameworks tested: ${this.comparison.summary.totalFrameworks}`);
    console.log(`  Total tests: ${this.comparison.summary.totalTests}`);
    console.log(`  Success rate: ${(this.comparison.summary.totalPassed / this.comparison.summary.totalTests * 100).toFixed(2)}%`);
    console.log(`  Average coverage: ${this.comparison.summary.averageCoverage.toFixed(2)}%`);
    console.log(`  Total execution time: ${this.comparison.summary.totalDuration}ms`);
    console.log(`  Overall success: ${this.comparison.summary.overallSuccess ? '✅' : '❌'}`);
  }
}

// Run comparison
if (require.main === module) {
  const comparator = new FrameworkComparator(process.env.RESULTS_DIR);
  comparator.compare();
}

module.exports = FrameworkComparator;
```

## 🔧 Best Practices

### Environment Management

1. **Use Environment Variables**: Keep configuration flexible across environments
2. **Baseline Management**: Maintain separate baselines for different branches/environments
3. **Artifact Storage**: Store test results and reports for analysis
4. **Parallel Execution**: Run framework tests in parallel when possible
5. **Quality Gates**: Implement coverage and performance thresholds

### Performance Optimization

1. **Caching**: Cache dependencies and test results
2. **Selective Testing**: Run tests only for changed files when appropriate
3. **Resource Limits**: Set appropriate timeouts and resource limits
4. **Container Optimization**: Use multi-stage builds and appropriate base images

### Monitoring and Alerting

1. **Test Metrics**: Track test execution time and success rates
2. **Coverage Trends**: Monitor coverage changes over time
3. **Performance Regression**: Alert on performance degradation
4. **Flaky Test Detection**: Identify and address unstable tests

## 📚 Additional Resources

- **[GitHub Actions Documentation](https://docs.github.com/en/actions)** - GitHub Actions workflows
- **[GitLab CI Documentation](https://docs.gitlab.com/ee/ci/)** - GitLab CI/CD pipelines
- **[Jenkins Documentation](https://www.jenkins.io/doc/)** - Jenkins pipeline guides
- **[Azure DevOps Documentation](https://docs.microsoft.com/en-us/azure/devops/)** - Azure Pipelines
- **[CircleCI Documentation](https://circleci.com/docs/)** - CircleCI configuration
- **[Docker Documentation](https://docs.docker.com/)** - Docker containerization