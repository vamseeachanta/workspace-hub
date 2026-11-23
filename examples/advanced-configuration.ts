/**
 * Advanced configuration example for Baseline Tracking Engine
 */

import { BaselineTrackingEngine, ConfigManager } from '../src';
import * as path from 'path';

async function advancedConfigurationExample() {
  console.log('🚀 Starting Advanced Configuration Example\n');

  // Create a custom config manager
  const configManager = new ConfigManager('./advanced-baseline-config.yml');

  try {
    // Check if config exists, if not create from template
    console.log('📋 Setting up advanced configuration...');

    let config;
    try {
      config = await configManager.getConfig();
      console.log('✅ Found existing configuration');
    } catch (error) {
      console.log('📝 Creating new configuration from comprehensive template...');
      config = await configManager.applyTemplate('comprehensive', {
        engine: {
          baseline: {
            storagePath: './advanced-baselines',
            retentionPolicy: {
              maxVersions: 20,
              maxAge: 90 // Keep for 3 months
            },
            mergeStrategy: 'best',
            backupEnabled: true,
            backupPath: './advanced-baselines/backups'
          },
          reporting: {
            formats: ['json', 'html', 'markdown'],
            outputPath: './advanced-reports',
            includeDetails: true,
            includeTrends: true
          }
        },
        metricsCollector: {
          parsers: {
            jest: {
              enabled: true,
              resultsPath: './coverage/test-results.json',
              coveragePath: './coverage'
            },
            mocha: {
              enabled: true,
              resultsPath: './test-output/mocha-results.json',
              format: 'json'
            },
            nyc: {
              enabled: true,
              coveragePath: './coverage'
            }
          },
          performance: {
            enabled: true,
            sources: [
              './performance/metrics.json',
              './lighthouse/results.json'
            ]
          }
        },
        ruleEngine: {
          enableProgressive: true,
          progressiveSteps: 10,
          defaultSeverity: 'warning'
        }
      });

      console.log('✅ Configuration created and saved');
    }

    // Validate the configuration
    console.log('\n🔍 Validating configuration...');
    const validation = configManager.validateConfig(config);

    if (validation.valid) {
      console.log('✅ Configuration is valid');
      if (validation.warnings.length > 0) {
        console.log('⚠️ Warnings:');
        validation.warnings.forEach(warning => console.log(`  - ${warning}`));
      }
    } else {
      console.log('❌ Configuration validation failed:');
      validation.errors.forEach(error => console.log(`  - ${error}`));
      return;
    }

    // Initialize engine with custom config
    const engine = new BaselineTrackingEngine({
      configPath: './advanced-baseline-config.yml'
    });

    await engine.initialize();
    console.log('✅ Engine initialized with advanced configuration');

    // Create advanced rules
    console.log('\n⚙️ Setting up advanced rules...');

    // Create comprehensive rules from templates
    const coverageRules = await engine.createRulesFromTemplate('coverage_basic', {
      progressive: true,
      severity: 'error'
    });

    const testRules = await engine.createRulesFromTemplate('test_quality', {
      severity: 'error'
    });

    const performanceRules = await engine.createRulesFromTemplate('performance_basic', {
      progressive: true,
      severity: 'warning'
    });

    console.log(`✅ Created rules:
    - ${coverageRules.length} coverage rules
    - ${testRules.length} test quality rules
    - ${performanceRules.length} performance rules`);

    // Add custom progressive rule
    await engine.addRule({
      id: 'custom-progressive-coverage',
      name: 'Progressive Line Coverage',
      metric: 'coverage.lines.percentage',
      type: 'absolute',
      comparison: 'gte',
      value: 75, // Start at 75%
      severity: 'warning',
      progressive: true,
      enabled: true,
      metadata: {
        targetValue: 95, // Eventually reach 95%
        description: 'Gradually improve line coverage to 95%'
      }
    });

    // Add custom performance rule with wildcard pattern
    await engine.addRule({
      id: 'memory-usage-limit',
      name: 'Memory Usage Limit',
      metric: 'performance.memory*',
      type: 'percentage',
      comparison: 'lte',
      value: 20, // Max 20% increase
      severity: 'error',
      progressive: false,
      enabled: true,
      metadata: {
        description: 'Prevent memory usage regressions'
      }
    });

    console.log('✅ Added custom advanced rules');

    // Simulate metrics collection with advanced features
    console.log('\n📊 Simulating advanced metrics collection...');

    const snapshot = await engine.collectMetrics(
      'advanced-example-1',
      'develop',
      'abc123def456',
      'staging',
      '2.0.0-beta.1',
      {
        buildNumber: 156,
        pullRequest: 42,
        branch: 'feature/advanced-metrics',
        triggeredBy: 'webhook',
        environment: {
          nodeVersion: '18.16.0',
          npmVersion: '9.5.1',
          os: 'ubuntu-20.04'
        }
      }
    );

    console.log(`📈 Advanced metrics collected:
    - Branch: ${snapshot.branch}
    - Environment: ${snapshot.environment}
    - Tests: ${snapshot.tests.summary.total} (${snapshot.tests.summary.passed} passed, ${snapshot.tests.summary.failed} failed)
    - Coverage: Lines ${snapshot.coverage.lines.percentage}%, Functions ${snapshot.coverage.functions.percentage}%
    - Performance: ${snapshot.performance.length} metrics
    - Metadata: ${Object.keys(snapshot.metadata).length} custom fields`);

    // Create baseline with comprehensive metadata
    console.log('\n🎯 Creating comprehensive baseline...');
    const baseline = await engine.createBaseline(
      'Staging Baseline v2.0.0-beta.1',
      snapshot,
      {
        isDefault: true,
        tags: ['staging', 'beta', 'feature-branch', 'comprehensive'],
        metadata: {
          createdBy: 'advanced-example',
          purpose: 'Comprehensive staging baseline with full metrics',
          buildInfo: {
            pullRequest: 42,
            branch: 'feature/advanced-metrics',
            buildNumber: 156
          },
          testingSuite: {
            jest: true,
            mocha: true,
            coverage: true,
            performance: true
          }
        }
      }
    );

    console.log(`✅ Comprehensive baseline created: ${baseline.name}`);

    // Progressive improvement simulation
    console.log('\n📈 Simulating progressive improvement...');

    const currentRules = await engine.getRules({ progressive: true });
    const progressiveTargets = await engine.createProgressiveTargets(snapshot);

    if (progressiveTargets.length > 0) {
      console.log('🎯 Progressive targets calculated:');
      progressiveTargets.forEach(target => {
        console.log(`  - ${target.ruleId}: ${target.currentValue.toFixed(2)} → ${target.nextTarget.toFixed(2)} (target: ${target.targetValue})`);
      });

      // Update progressive rules
      await engine.updateProgressiveRules(progressiveTargets);
      console.log('✅ Progressive rules updated');
    }

    // Generate rule suggestions based on current metrics
    console.log('\n💡 Generating rule suggestions...');
    const suggestions = await engine.suggestRules(snapshot);

    if (suggestions.length > 0) {
      console.log('📝 Suggested rules:');
      suggestions.forEach((suggestion, index) => {
        console.log(`  ${index + 1}. ${suggestion.name}: ${suggestion.metric} ${suggestion.comparison} ${suggestion.value}`);
      });
    } else {
      console.log('✅ No additional rules suggested - metrics look good!');
    }

    // Demonstrate trend analysis
    console.log('\n📊 Trend analysis example...');

    // Create mock historical snapshots for trend analysis
    const historicalSnapshots = [
      {
        ...snapshot,
        id: 'historical-1',
        created: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000), // 7 days ago
        coverage: {
          ...snapshot.coverage,
          lines: { ...snapshot.coverage.lines, percentage: 72 }
        }
      },
      {
        ...snapshot,
        id: 'historical-2',
        created: new Date(Date.now() - 3 * 24 * 60 * 60 * 1000), // 3 days ago
        coverage: {
          ...snapshot.coverage,
          lines: { ...snapshot.coverage.lines, percentage: 75 }
        }
      },
      snapshot // Current
    ];

    const trendAnalysis = await engine.analyzeTrend(
      historicalSnapshots,
      'coverage.lines.percentage'
    );

    console.log(`📈 Coverage trend analysis:
    - Trend: ${trendAnalysis.trend}
    - Slope: ${trendAnalysis.slope.toFixed(4)}
    - Volatility: ${(trendAnalysis.volatility * 100).toFixed(2)}%
    - Correlation: ${trendAnalysis.correlation.toFixed(3)}`);

    // Configuration management demonstration
    console.log('\n⚙️ Configuration management...');

    // Create backup
    const backupPath = await engine.createConfigBackup();
    console.log(`💾 Configuration backup created: ${backupPath}`);

    // Update configuration
    const updatedConfig = await engine.updateConfig({
      reportGenerator: {
        includeCharts: true,
        formats: ['json', 'html', 'markdown', 'csv']
      }
    });

    console.log('✅ Configuration updated with charts and CSV export');

    // Show available templates
    console.log('\n📋 Available configuration templates:');
    const templates = configManager.getConfigTemplates();
    Object.keys(templates).forEach(templateName => {
      const template = templates[templateName];
      console.log(`  - ${templateName}: ${template.reportGenerator.formats.join(', ')} formats`);
    });

    // Final health check
    console.log('\n🏥 Final health check...');
    const health = await engine.healthCheck();

    console.log(`System Status: ${health.status.toUpperCase()}`);
    Object.entries(health.components).forEach(([component, status]) => {
      const icon = status.status === 'healthy' ? '✅' : '❌';
      console.log(`  ${icon} ${component}: ${status.status}`);
      if (status.message) {
        console.log(`    ${status.message}`);
      }
    });

    console.log('\n🎉 Advanced configuration example completed successfully!');

  } catch (error) {
    console.error('❌ Error during advanced configuration:', error.message);

    if (error.code) {
      console.error(`Error Code: ${error.code}`);
    }

    if (error.details) {
      console.error('Details:', error.details);
    }

    process.exit(1);
  }
}

// Run the example
if (require.main === module) {
  advancedConfigurationExample().catch(console.error);
}

export { advancedConfigurationExample };