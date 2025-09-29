/**
 * Basic usage example for Baseline Tracking Engine
 */

import { BaselineTrackingEngine } from '../src';

async function basicExample() {
  console.log('🚀 Starting Basic Baseline Tracking Example\n');

  // Initialize the engine
  const engine = new BaselineTrackingEngine({
    configPath: './baseline-config.yml'
  });

  try {
    // Initialize the engine
    await engine.initialize();
    console.log('✅ Engine initialized successfully');

    // Collect current metrics
    console.log('\n📊 Collecting current metrics...');
    const currentSnapshot = await engine.collectMetrics(
      'example-run-1',
      'main',
      'abc123def',
      'production',
      '1.0.0',
      {
        buildNumber: 42,
        triggeredBy: 'ci-pipeline'
      }
    );

    console.log(`📈 Metrics collected:
    - Tests: ${currentSnapshot.tests.summary.total} total, ${currentSnapshot.tests.summary.passed} passed
    - Coverage: ${currentSnapshot.coverage.lines.percentage.toFixed(2)}% line coverage
    - Performance metrics: ${currentSnapshot.performance.length} collected`);

    // Check if we have a default baseline
    console.log('\n🎯 Checking for default baseline...');
    let defaultBaseline = await engine.getDefaultBaseline('main', 'production');

    if (!defaultBaseline) {
      console.log('📝 No default baseline found. Creating one...');

      // Create a baseline from current metrics
      defaultBaseline = await engine.createBaseline(
        'Production Baseline v1.0.0',
        currentSnapshot,
        {
          isDefault: true,
          tags: ['production', 'v1.0.0', 'initial'],
          metadata: {
            createdBy: 'basic-example',
            purpose: 'Initial production baseline'
          }
        }
      );

      console.log(`✅ Baseline created: ${defaultBaseline.name} (ID: ${defaultBaseline.id})`);
    } else {
      console.log(`✅ Found default baseline: ${defaultBaseline.name}`);

      // Compare against the baseline
      console.log('\n🔍 Comparing current metrics against baseline...');
      const report = await engine.compareAgainstDefault(currentSnapshot);

      console.log(`📋 Comparison Results:
      - Overall Status: ${report.overallStatus.toUpperCase()}
      - Rules Evaluated: ${report.summary.total}
      - Passed: ${report.summary.passed}
      - Failed: ${report.summary.failed}
      - Warnings: ${report.summary.warnings}`);

      // Show significant changes
      const significantChanges = report.comparisons.filter(
        comp => Math.abs(comp.deltaPercentage) > 5 && comp.status !== 'unchanged'
      );

      if (significantChanges.length > 0) {
        console.log('\n📊 Significant Changes (>5%):');
        significantChanges.forEach(change => {
          const icon = change.status === 'improved' ? '📈' : '📉';
          console.log(`  ${icon} ${change.metric}: ${change.deltaPercentage.toFixed(2)}% change`);
        });
      }

      // Show recommendations
      if (report.recommendations.length > 0) {
        console.log('\n💡 Recommendations:');
        report.recommendations.slice(0, 3).forEach((rec, index) => {
          console.log(`  ${index + 1}. ${rec}`);
        });
      }

      // Generate reports
      console.log('\n📄 Generating reports...');
      const generatedFiles = await engine.generateReport(report);

      console.log('✅ Reports generated:');
      Object.entries(generatedFiles).forEach(([format, filePath]) => {
        console.log(`  - ${format.toUpperCase()}: ${filePath}`);
      });
    }

    // Show available rules
    console.log('\n⚙️ Current Rules:');
    const rules = await engine.getRules();
    if (rules.length === 0) {
      console.log('  No rules configured yet.');

      // Create some basic rules
      console.log('\n📝 Creating basic rules...');
      await engine.createRulesFromTemplate('coverage_basic');
      await engine.createRulesFromTemplate('test_quality');

      const newRules = await engine.getRules();
      console.log(`✅ Created ${newRules.length} rules from templates`);
    } else {
      rules.slice(0, 3).forEach(rule => {
        console.log(`  - ${rule.name}: ${rule.metric} ${rule.comparison} ${rule.value} (${rule.severity})`);
      });
      if (rules.length > 3) {
        console.log(`  ... and ${rules.length - 3} more`);
      }
    }

    // Health check
    console.log('\n🏥 Performing health check...');
    const health = await engine.healthCheck();
    console.log(`System Status: ${health.status.toUpperCase()}`);

    if (health.status === 'unhealthy') {
      console.log('❌ Issues found:');
      Object.entries(health.components).forEach(([component, status]) => {
        if (status.status === 'unhealthy') {
          console.log(`  - ${component}: ${status.message}`);
        }
      });
    }

    console.log('\n🎉 Basic example completed successfully!');

  } catch (error) {
    console.error('❌ Error during execution:', error.message);

    if (error.code) {
      console.error(`Error Code: ${error.code}`);
    }

    process.exit(1);
  } finally {
    // Cleanup
    await engine.shutdown();
  }
}

// Run the example
if (require.main === module) {
  basicExample().catch(console.error);
}

export { basicExample };