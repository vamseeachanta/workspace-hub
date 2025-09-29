const { test, expect } = require('@playwright/test');
const BaselineService = require('../../src/services/baseline-service');
const MockFactory = require('../fixtures/mock-factories');
const fs = require('fs').promises;
const path = require('path');

test.describe('Complete Baseline Workflow E2E Tests', () => {
  let baselineService;
  let testProject;
  
  test.beforeAll(async () => {
    // Setup test service instance
    baselineService = new BaselineService({
      database: {
        connectionString: process.env.TEST_DB_URL || 'sqlite://memory'
      },
      logger: { level: 'error' } // Reduce noise in tests
    });
    
    await baselineService.initialize();
    
    // Create test project structure
    testProject = {
      root: path.join(__dirname, '../temp/e2e-project'),
      src: path.join(__dirname, '../temp/e2e-project/src'),
      tests: path.join(__dirname, '../temp/e2e-project/tests')
    };
    
    await fs.mkdir(testProject.root, { recursive: true });
    await fs.mkdir(testProject.src, { recursive: true });
    await fs.mkdir(testProject.tests, { recursive: true });
  });
  
  test.afterAll(async () => {
    await baselineService.cleanup();
    
    try {
      await fs.rmdir(testProject.root, { recursive: true });
    } catch (error) {
      console.warn('E2E cleanup warning:', error.message);
    }
  });

  test('should create baseline, run tests, and generate comparison report', async ({ page }) => {
    // Step 1: Create a new baseline
    const baselineData = {
      name: 'E2E Test Baseline',
      description: 'End-to-end test baseline',
      projectId: 'e2e-project',
      branch: 'main',
      commit: 'initial-commit-123'
    };
    
    const baseline = await baselineService.createBaseline(baselineData);
    expect(baseline.id).toBeDefined();
    expect(baseline.name).toBe('E2E Test Baseline');
    
    // Step 2: Create sample test files
    const testFileContent = `
      describe('E2E Sample Tests', () => {
        test('should pass basic assertion', () => {
          expect(1 + 1).toBe(2);
        });
        
        test('should handle async operations', async () => {
          const result = await Promise.resolve(42);
          expect(result).toBe(42);
        });
        
        test('should validate string operations', () => {
          const text = 'Hello World';
          expect(text).toContain('World');
          expect(text.length).toBe(11);
        });
      });
    `;
    
    await fs.writeFile(
      path.join(testProject.tests, 'sample.test.js'),
      testFileContent
    );
    
    // Step 3: Run tests and collect metrics
    const testRunner = baselineService.getTestRunner('jest');
    const testResults = await testRunner.runTests({
      projectRoot: testProject.root,
      testDir: testProject.tests
    });
    
    expect(testResults.success).toBe(true);
    expect(testResults.metrics.testCount).toBe(3);
    expect(testResults.metrics.passCount).toBe(3);
    expect(testResults.metrics.passRate).toBe(100);
    
    // Step 4: Store baseline metrics
    const baselineMetrics = {
      testCount: testResults.metrics.testCount,
      passRate: testResults.metrics.passRate,
      coverage: testResults.metrics.coverage || {
        lines: 85.0,
        branches: 80.0,
        functions: 90.0,
        statements: 85.0
      },
      performance: {
        averageExecutionTime: 150.0,
        totalDuration: testResults.metrics.totalDuration || 450
      }
    };
    
    await baselineService.updateBaselineMetrics(baseline.id, baselineMetrics);
    
    // Step 5: Simulate a new test run with changes
    const newTestFileContent = `
      describe('E2E Modified Tests', () => {
        test('should pass basic assertion', () => {
          expect(1 + 1).toBe(2);
        });
        
        test('should handle async operations', async () => {
          const result = await Promise.resolve(42);
          expect(result).toBe(42);
        });
        
        test('should validate string operations', () => {
          const text = 'Hello World';
          expect(text).toContain('World');
          expect(text.length).toBe(11);
        });
        
        test('should handle new feature', () => {
          const feature = { enabled: true, value: 'test' };
          expect(feature.enabled).toBe(true);
          expect(feature.value).toBe('test');
        });
        
        test('should fail intentionally', () => {
          expect(false).toBe(true); // This will fail
        });
      });
    `;
    
    await fs.writeFile(
      path.join(testProject.tests, 'modified.test.js'),
      newTestFileContent
    );
    
    // Step 6: Run modified tests
    const newTestResults = await testRunner.runTests({
      projectRoot: testProject.root,
      testDir: testProject.tests
    });
    
    expect(newTestResults.metrics.testCount).toBe(5); // Added 2 new tests
    expect(newTestResults.metrics.failCount).toBe(1); // One intentional failure
    expect(newTestResults.metrics.passRate).toBe(80); // 4 passed out of 5
    
    // Step 7: Create comparison
    const currentMetrics = {
      testCount: newTestResults.metrics.testCount,
      passRate: newTestResults.metrics.passRate,
      coverage: {
        lines: 82.0, // Slightly lower
        branches: 75.0, // Lower
        functions: 88.0, // Lower
        statements: 83.0 // Lower
      },
      performance: {
        averageExecutionTime: 180.0, // Slower
        totalDuration: newTestResults.metrics.totalDuration || 900
      }
    };
    
    const comparison = await baselineService.compareMetrics(
      baseline.id,
      currentMetrics,
      {
        branch: 'feature/new-tests',
        commit: 'feature-commit-456'
      }
    );
    
    expect(comparison.id).toBeDefined();
    expect(comparison.summary.overallStatus).toBe('degradation');
    expect(comparison.violations.length).toBeGreaterThan(0);
    
    // Verify specific metric changes
    expect(comparison.metrics.passRate.status).toBe('degradation');
    expect(comparison.metrics.passRate.change).toBe(-20); // 100 -> 80
    expect(comparison.metrics.coverage.lines.status).toBe('degradation');
    
    // Step 8: Generate comprehensive report
    const reportGenerator = baselineService.getReportGenerator();
    const report = await reportGenerator.generateSummaryReport(
      comparison,
      baseline,
      {
        format: 'html',
        fileName: 'e2e-comparison-report.html',
        includeCharts: true,
        includeTestDetails: true
      }
    );
    
    expect(report.fileName).toBe('e2e-comparison-report.html');
    expect(report.format).toBe('html');
    expect(report.size).toBeGreaterThan(0);
    
    // Verify report file exists
    const reportPath = path.join(baselineService.config.reportsDir, report.fileName);
    const reportExists = await fs.access(reportPath).then(() => true).catch(() => false);
    expect(reportExists).toBe(true);
    
    // Step 9: Verify alert generation
    const alerts = await baselineService.getAlertsForComparison(comparison.id);
    expect(alerts.length).toBeGreaterThan(0);
    
    const criticalAlerts = alerts.filter(alert => alert.severity === 'critical');
    expect(criticalAlerts.length).toBeGreaterThan(0);
    
    // Verify pass rate alert
    const passRateAlert = alerts.find(alert => 
      alert.type === 'threshold_violation' && 
      alert.metadata?.metric === 'passRate'
    );
    expect(passRateAlert).toBeDefined();
    expect(passRateAlert.title).toContain('Pass Rate');
  });

  test('should handle multiple test frameworks in same project', async ({ page }) => {
    // Create baseline for multi-framework project
    const baseline = await baselineService.createBaseline({
      name: 'Multi-Framework Baseline',
      projectId: 'multi-framework-project',
      branch: 'main',
      commit: 'multi-commit-789'
    });
    
    // Create Jest tests
    const jestTestContent = `
      describe('Jest Tests', () => {
        test('jest test 1', () => expect(true).toBe(true));
        test('jest test 2', () => expect(1).toBe(1));
      });
    `;
    
    await fs.writeFile(
      path.join(testProject.tests, 'jest.test.js'),
      jestTestContent
    );
    
    // Create Mocha tests  
    const mochaTestContent = `
      const { expect } = require('chai');
      
      describe('Mocha Tests', () => {
        it('mocha test 1', () => expect(true).to.be.true);
        it('mocha test 2', () => expect(1).to.equal(1));
      });
    `;
    
    await fs.writeFile(
      path.join(testProject.tests, 'mocha.test.js'),
      mochaTestContent
    );
    
    // Run tests with multiple frameworks
    const frameworks = ['jest', 'mocha'];
    const aggregatedResults = {
      testCount: 0,
      passCount: 0,
      failCount: 0,
      frameworks: []
    };
    
    for (const framework of frameworks) {
      const runner = baselineService.getTestRunner(framework);
      const results = await runner.runTests({
        projectRoot: testProject.root,
        testDir: testProject.tests,
        pattern: `**/${framework}.test.js`
      });
      
      aggregatedResults.testCount += results.metrics.testCount;
      aggregatedResults.passCount += results.metrics.passCount;
      aggregatedResults.failCount += results.metrics.failCount;
      aggregatedResults.frameworks.push({
        framework,
        results: results.metrics
      });
    }
    
    expect(aggregatedResults.testCount).toBe(4); // 2 Jest + 2 Mocha
    expect(aggregatedResults.passCount).toBe(4);
    expect(aggregatedResults.failCount).toBe(0);
    expect(aggregatedResults.frameworks).toHaveLength(2);
    
    // Store aggregated metrics as baseline
    const multiFrameworkMetrics = {
      testCount: aggregatedResults.testCount,
      passRate: (aggregatedResults.passCount / aggregatedResults.testCount) * 100,
      coverage: { lines: 90.0, branches: 85.0, functions: 95.0, statements: 88.0 },
      frameworks: aggregatedResults.frameworks
    };
    
    await baselineService.updateBaselineMetrics(baseline.id, multiFrameworkMetrics);
    
    const updatedBaseline = await baselineService.getBaseline(baseline.id);
    expect(updatedBaseline.metrics.frameworks).toHaveLength(2);
  });

  test('should integrate with CI/CD pipeline simulation', async ({ page }) => {
    // Simulate CI/CD pipeline integration
    const pipelineBaseline = await baselineService.createBaseline({
      name: 'CI/CD Pipeline Baseline',
      projectId: 'pipeline-project',
      branch: 'main',
      commit: 'pipeline-commit-abc'
    });
    
    // Simulate webhook trigger
    const webhookPayload = {
      event: 'pull_request',
      action: 'opened',
      pull_request: {
        number: 456,
        head: {
          sha: 'pr-commit-def',
          ref: 'feature/ci-integration'
        },
        base: {
          sha: 'pipeline-commit-abc',
          ref: 'main'
        }
      }
    };
    
    // Process webhook and trigger baseline comparison
    const webhookResult = await baselineService.processWebhook(webhookPayload);
    expect(webhookResult.shouldTriggerBaseline).toBe(true);
    expect(webhookResult.baselineId).toBe(pipelineBaseline.id);
    expect(webhookResult.prNumber).toBe(456);
    
    // Simulate test execution in CI environment
    const ciTestResults = {
      testCount: 25,
      passCount: 23,
      failCount: 2,
      skipCount: 0,
      passRate: 92.0,
      coverage: {
        lines: 88.5,
        branches: 82.0,
        functions: 94.0,
        statements: 87.0
      },
      performance: {
        averageExecutionTime: 235.0,
        totalDuration: 5875,
        memoryUsage: 145.0
      }
    };
    
    // Create comparison with CI results
    const ciComparison = await baselineService.compareMetrics(
      pipelineBaseline.id,
      ciTestResults,
      {
        branch: 'feature/ci-integration',
        commit: 'pr-commit-def',
        pullRequest: 456,
        ciProvider: 'github-actions',
        buildNumber: 'run-123'
      }
    );
    
    expect(ciComparison.metadata.pullRequest).toBe(456);
    expect(ciComparison.metadata.ciProvider).toBe('github-actions');
    
    // Generate CI-specific report
    const reportGenerator = baselineService.getReportGenerator();
    const ciReport = await reportGenerator.generateSummaryReport(
      ciComparison,
      pipelineBaseline,
      {
        format: 'json',
        fileName: 'ci-comparison-report.json',
        includeMetadata: true,
        includeCIInfo: true
      }
    );
    
    expect(ciReport.format).toBe('json');
    
    // Verify CI status update simulation
    const statusUpdate = await baselineService.generateCIStatus(ciComparison);
    expect(statusUpdate.state).toMatch(/success|failure|pending/);
    expect(statusUpdate.description).toContain('baseline comparison');
    expect(statusUpdate.targetUrl).toContain('/reports/');
  });

  test('should handle performance regression detection', async ({ page }) => {
    // Create performance-focused baseline
    const perfBaseline = await baselineService.createBaseline({
      name: 'Performance Baseline',
      projectId: 'performance-project',
      branch: 'main',
      commit: 'perf-baseline-123'
    });
    
    // Set baseline with good performance metrics
    const baselineMetrics = {
      testCount: 50,
      passRate: 98.0,
      coverage: { lines: 92.0, branches: 88.0, functions: 96.0, statements: 91.0 },
      performance: {
        averageExecutionTime: 120.0,
        slowestTest: 1500.0,
        fastestTest: 15.0,
        memoryUsage: 80.0,
        cpuUsage: 25.0
      }
    };
    
    await baselineService.updateBaselineMetrics(perfBaseline.id, baselineMetrics);
    
    // Simulate performance regression
    const degradedMetrics = {
      testCount: 52, // Added tests
      passRate: 96.0, // Slightly lower
      coverage: { lines: 90.0, branches: 85.0, functions: 94.0, statements: 89.0 },
      performance: {
        averageExecutionTime: 280.0, // Much slower
        slowestTest: 8500.0, // Very slow test
        fastestTest: 18.0,
        memoryUsage: 150.0, // Higher memory
        cpuUsage: 65.0 // Higher CPU
      }
    };
    
    const perfComparison = await baselineService.compareMetrics(
      perfBaseline.id,
      degradedMetrics,
      {
        branch: 'feature/performance-test',
        commit: 'perf-regression-456'
      }
    );
    
    // Verify performance degradation detection
    expect(perfComparison.summary.overallStatus).toBe('degradation');
    expect(perfComparison.metrics.performance.averageExecutionTime.status).toBe('degradation');
    expect(perfComparison.metrics.performance.memoryUsage.status).toBe('degradation');
    
    // Check for performance-specific violations
    const perfViolations = perfComparison.violations.filter(v => 
      v.type === 'performance_regression'
    );
    expect(perfViolations.length).toBeGreaterThan(0);
    
    // Verify alert severity for performance regressions
    const perfAlerts = await baselineService.getAlertsForComparison(perfComparison.id);
    const criticalPerfAlerts = perfAlerts.filter(alert => 
      alert.severity === 'critical' && 
      alert.type === 'performance_degradation'
    );
    expect(criticalPerfAlerts.length).toBeGreaterThan(0);
    
    // Generate performance-focused report
    const reportGenerator = baselineService.getReportGenerator();
    const perfReport = await reportGenerator.generateDetailedReport({
      comparison: perfComparison,
      baseline: perfBaseline,
      format: 'html',
      includePerformanceCharts: true,
      includeMemoryAnalysis: true,
      includeTrendAnalysis: true
    });
    
    expect(perfReport.format).toBe('html');
    expect(perfReport.sections).toContain('performance_analysis');
  });
});
