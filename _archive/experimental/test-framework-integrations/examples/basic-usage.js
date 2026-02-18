/**
 * Basic Usage Example
 *
 * Demonstrates how to use the Test Framework Integrations
 * with automatic framework detection and baseline tracking.
 */

const TestFrameworkIntegrations = require('../index');

async function basicExample() {
  console.log('🧪 Test Framework Integrations - Basic Example\n');

  // Create and initialize the test integration system
  const testIntegration = new TestFrameworkIntegrations({
    rootDir: process.cwd(),
    coverage: true,          // Enable coverage collection
    profiling: true,         // Enable performance profiling
    reporter: 'console',     // Use console reporter
    baseline: './baseline.json' // Compare against baseline
  });

  try {
    // Initialize the system (auto-detects available frameworks)
    console.log('🔍 Initializing and detecting test frameworks...');
    await testIntegration.initialize();

    // Show detected frameworks
    const frameworks = testIntegration.getDetectedFrameworks();
    console.log('📋 Detected frameworks:');
    frameworks.forEach(framework => {
      const activeIndicator = framework.isActive ? ' (active)' : '';
      console.log(`  - ${framework.name} v${framework.version}${activeIndicator}`);
    });
    console.log('');

    // Discover test files
    console.log('🔎 Discovering test files...');
    const testFiles = await testIntegration.discoverTests();
    console.log(`Found ${testFiles.length} test files\n`);

    // Run tests with integrated coverage and profiling
    console.log('🚀 Running tests with coverage and profiling...\n');
    const results = await testIntegration.runTests({
      verbose: true,
      bail: false
    });

    // Display results summary
    console.log('\n📊 Results Summary:');
    console.log(`  Tests: ${results.summary.total} (${results.summary.passed} passed, ${results.summary.failed} failed)`);
    console.log(`  Duration: ${results.summary.duration}ms`);

    if (results.coverage) {
      console.log(`  Coverage: ${results.coverage.total.toFixed(2)}%`);
    }

    if (results.profiling) {
      console.log(`  Performance: ${results.profiling.summary?.duration || 'N/A'}ms total`);
    }

    // Save current results as new baseline
    console.log('\n💾 Saving results as baseline...');
    await testIntegration.saveBaseline('latest');

    // Generate additional coverage reports
    if (results.coverage) {
      console.log('📋 Generating coverage reports...');
      const reportPaths = await testIntegration.generateCoverageReports('example-run');
      console.log('Coverage reports generated:', reportPaths);
    }

    console.log('\n✅ Basic example completed successfully!');

  } catch (error) {
    console.error('❌ Example failed:', error.message);
    process.exit(1);
  }
}

// Advanced usage with multiple frameworks
async function multiFrameworkExample() {
  console.log('\n🔄 Test Framework Integrations - Multi-Framework Example\n');

  const testIntegration = new TestFrameworkIntegrations({
    rootDir: process.cwd(),
    coverage: true,
    profiling: false,
    reporter: ['console', 'json', 'html'], // Multiple report formats
    parallel: false // Run frameworks sequentially for comparison
  });

  try {
    await testIntegration.initialize();

    // Run tests across all detected frameworks
    console.log('🎯 Running tests across all frameworks...');
    const multiResults = await testIntegration.runAllFrameworks({
      coverage: true
    });

    console.log('\n📊 Multi-Framework Results:');
    for (const [framework, results] of Object.entries(multiResults.results)) {
      console.log(`\n${framework}:`);
      console.log(`  Tests: ${results.summary.total} (${results.summary.passed} passed)`);
      console.log(`  Duration: ${results.summary.duration}ms`);
      if (results.coverage) {
        console.log(`  Coverage: ${results.coverage.total.toFixed(2)}%`);
      }
    }

    // Show any frameworks that failed
    if (Object.keys(multiResults.errors).length > 0) {
      console.log('\n❌ Framework Errors:');
      for (const [framework, error] of Object.entries(multiResults.errors)) {
        console.log(`  ${framework}: ${error}`);
      }
    }

    console.log('\n✅ Multi-framework example completed!');

  } catch (error) {
    console.error('❌ Multi-framework example failed:', error.message);
  }
}

// Custom configuration example
async function customConfigExample() {
  console.log('\n⚙️  Test Framework Integrations - Custom Configuration Example\n');

  // Create individual components with custom settings
  const { UnifiedTestRunner, CoverageIntegrator, PerformanceProfiler, BaselineReporter } = require('../index');

  // Custom runner configuration
  const runner = new UnifiedTestRunner({
    rootDir: process.cwd(),
    preferredFramework: 'jest', // Force specific framework
    fallbackOrder: ['jest', 'vitest', 'mocha']
  });

  // Custom coverage configuration
  const coverage = new CoverageIntegrator({
    providers: ['nyc', 'c8'], // Specific coverage providers
    formats: ['json', 'html'],
    threshold: {
      statements: 90,
      branches: 85,
      functions: 90,
      lines: 90
    }
  });

  // Custom profiler configuration
  const profiler = new PerformanceProfiler({
    enableMemoryTracking: true,
    enableCpuProfiling: false,
    enableGcTracking: true,
    memoryInterval: 50, // More frequent memory sampling
    detectLeaks: true
  });

  // Custom reporter configuration
  const reporter = new BaselineReporter({
    format: 'console',
    showTrends: true,
    showRecommendations: true,
    colorOutput: true,
    thresholds: {
      performance: { warning: 1.2, error: 2.0 },
      coverage: { warning: -2, error: -5 }
    }
  });

  try {
    // Initialize all components
    console.log('🔧 Initializing custom components...');
    await runner.initialize();
    await coverage.initialize();
    await profiler.initialize();
    await reporter.initialize();

    // Set up event handling
    reporter.onRunStart({
      framework: { name: runner.activeAdapter.framework, version: runner.activeAdapter.version }
    });

    // Start profiling
    await profiler.startProfiling();

    // Run tests
    console.log('🚀 Running tests with custom configuration...');
    const results = await runner.runTests();

    // Stop profiling
    const profilingData = await profiler.stopProfiling();
    results.profiling = profilingData;

    // Collect coverage
    const coverageData = await coverage.collectCoverage(
      runner.activeAdapter.framework,
      'npm test'
    );
    results.coverage = coverageData;

    // Generate reports
    await reporter.onRunComplete(results);

    // Analyze bottlenecks
    if (profilingData) {
      console.log('\n🔍 Performance Analysis:');
      const bottlenecks = profiler.analyzeBottlenecks();

      if (bottlenecks.slowTests.length > 0) {
        console.log('Slowest tests:');
        bottlenecks.slowTests.slice(0, 3).forEach((test, i) => {
          console.log(`  ${i + 1}. ${test.name}: ${test.duration}ms`);
        });
      }
    }

    // Check coverage thresholds
    if (coverageData) {
      const thresholdCheck = coverage.checkThresholds(coverageData);
      if (!thresholdCheck.passed) {
        console.log('\n⚠️  Coverage thresholds not met:');
        thresholdCheck.failures.forEach(failure => {
          console.log(`  ${failure.metric}: ${failure.actual.toFixed(2)}% (required: ${failure.threshold}%)`);
        });
      }
    }

    console.log('\n✅ Custom configuration example completed!');

  } catch (error) {
    console.error('❌ Custom configuration example failed:', error.message);
  }
}

// Performance monitoring example
async function performanceMonitoringExample() {
  console.log('\n⚡ Test Framework Integrations - Performance Monitoring Example\n');

  const testIntegration = new TestFrameworkIntegrations({
    profiling: true,
    coverage: false, // Disable coverage for pure performance testing
    reporter: 'json'
  });

  try {
    await testIntegration.initialize();

    console.log('🔍 Starting performance monitoring...');

    // Start tests and monitor performance in real-time
    const testPromise = testIntegration.runTests({
      verbose: false
    });

    // Monitor performance metrics while tests run
    const monitoringInterval = setInterval(() => {
      const metrics = testIntegration.getCurrentMetrics();
      if (metrics) {
        console.log(`📊 Memory: ${(metrics.memory.process.heapUsed / 1024 / 1024).toFixed(2)}MB`);
        console.log(`⏱️  Uptime: ${(metrics.uptime / 1000).toFixed(2)}s`);
        console.log(`♻️  GC events: ${metrics.gc.recentEvents}`);
        console.log('---');
      }
    }, 2000);

    // Wait for tests to complete
    const results = await testPromise;
    clearInterval(monitoringInterval);

    // Analyze performance bottlenecks
    console.log('\n🔍 Performance Bottleneck Analysis:');
    const bottlenecks = testIntegration.analyzeBottlenecks();

    if (bottlenecks.slowTests.length > 0) {
      console.log('\n🐌 Slowest Tests:');
      bottlenecks.slowTests.forEach((test, i) => {
        console.log(`  ${i + 1}. ${test.name}`);
        console.log(`     Duration: ${test.duration}ms`);
        if (test.memoryDelta) {
          console.log(`     Memory: +${(test.memoryDelta.heapUsed / 1024 / 1024).toFixed(2)}MB`);
        }
      });
    }

    if (bottlenecks.recommendations.length > 0) {
      console.log('\n💡 Performance Recommendations:');
      bottlenecks.recommendations.forEach((rec, i) => {
        console.log(`  ${i + 1}. [${rec.severity.toUpperCase()}] ${rec.message}`);
      });
    }

    console.log('\n✅ Performance monitoring example completed!');

  } catch (error) {
    console.error('❌ Performance monitoring example failed:', error.message);
  }
}

// Run examples based on command line arguments
async function main() {
  const examples = {
    basic: basicExample,
    multi: multiFrameworkExample,
    custom: customConfigExample,
    performance: performanceMonitoringExample
  };

  const exampleName = process.argv[2] || 'basic';

  if (!examples[exampleName]) {
    console.log('Available examples:');
    Object.keys(examples).forEach(name => {
      console.log(`  node basic-usage.js ${name}`);
    });
    return;
  }

  await examples[exampleName]();
}

// Run if called directly
if (require.main === module) {
  main().catch(console.error);
}

module.exports = {
  basicExample,
  multiFrameworkExample,
  customConfigExample,
  performanceMonitoringExample
};