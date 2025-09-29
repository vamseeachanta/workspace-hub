# Baseline Tracking Engine

A comprehensive TypeScript library for tracking, comparing, and reporting on test metrics, code coverage, and performance data across different versions of your codebase.

## Features

- **📊 Metrics Collection**: Parse test results from Jest, Mocha, NYC, and custom formats
- **📈 Coverage Tracking**: Monitor code coverage metrics with detailed file-level analysis
- **🚀 Performance Monitoring**: Track performance metrics and detect regressions
- **🎯 Baseline Management**: Create, manage, and version baselines with retention policies
- **🔍 Intelligent Comparison**: Compare current metrics against baselines with configurable thresholds
- **⚙️ Flexible Rules Engine**: Define custom rules with progressive improvement targets
- **📋 Multi-format Reports**: Generate reports in JSON, HTML, Markdown, and CSV formats
- **📊 Trend Analysis**: Analyze metric trends over time with statistical insights
- **🔧 Configuration Management**: YAML/JSON configuration with validation and templates

## Quick Start

### Installation

```bash
npm install baseline-tracking-engine
```

### Basic Usage

```typescript
import { BaselineTrackingEngine } from 'baseline-tracking-engine';

// Initialize the engine
const engine = new BaselineTrackingEngine({
  configPath: './baseline-config.yml'
});

await engine.initialize();

// Collect current metrics
const snapshot = await engine.collectMetrics(
  'run-123',
  'main',
  'abc123',
  'production',
  '1.0.0'
);

// Create or compare against baseline
const baseline = await engine.getDefaultBaseline('main', 'production');
if (!baseline) {
  // Create initial baseline
  await engine.createBaseline('Production v1.0.0', snapshot, {
    isDefault: true,
    tags: ['production', 'v1.0.0']
  });
} else {
  // Compare against baseline
  const report = await engine.compareAgainstDefault(snapshot);

  // Generate reports
  const files = await engine.generateReport(report);
  console.log('Reports generated:', files);
}
```

## Core Components

### 1. Baseline Manager

Manages baseline storage, versioning, and retrieval:

```typescript
// Create baseline from metrics
const baseline = await engine.createBaseline('Release v2.0', snapshot, {
  isDefault: true,
  tags: ['release', 'stable'],
  metadata: { version: '2.0.0' }
});

// List baselines with filters
const baselines = await engine.listBaselines({
  branch: 'main',
  environment: 'production',
  tags: ['stable']
});

// Set as default
await engine.setDefaultBaseline('baseline-id');
```

### 2. Metrics Collector

Parses various test and coverage formats:

```typescript
// Configure multiple parsers
const config = {
  parsers: {
    jest: {
      enabled: true,
      resultsPath: './test-results.json',
      coveragePath: './coverage'
    },
    mocha: {
      enabled: true,
      resultsPath: './mocha-results.json',
      format: 'json'
    },
    nyc: {
      enabled: true,
      coveragePath: './coverage'
    }
  },
  performance: {
    enabled: true,
    sources: ['./performance-metrics.json']
  }
};
```

### 3. Comparison Engine

Compares metrics with statistical analysis:

```typescript
// Compare with options
const report = await engine.compareAgainstBaseline(current, baselineId, {
  includeUnchanged: false,
  precisionDigits: 2,
  excludeMetrics: ['tests.duration']
});

// Analyze trends
const trend = await engine.analyzeTrend(snapshots, 'coverage.lines.percentage');
console.log(`Trend: ${trend.trend}, Slope: ${trend.slope}`);
```

### 4. Rule Engine

Define configurable threshold rules:

```typescript
// Add custom rule
await engine.addRule({
  id: 'coverage-rule',
  name: 'Minimum Line Coverage',
  metric: 'coverage.lines.percentage',
  type: 'absolute',
  comparison: 'gte',
  value: 80,
  severity: 'error',
  progressive: false,
  enabled: true
});

// Create from templates
await engine.createRulesFromTemplate('coverage_basic');
await engine.createRulesFromTemplate('test_quality');

// Progressive improvement
const targets = await engine.createProgressiveTargets(snapshot);
await engine.updateProgressiveRules(targets);
```

### 5. Report Generator

Generate comprehensive reports:

```typescript
// Configure report formats
const config = {
  outputPath: './reports',
  formats: ['json', 'html', 'markdown', 'csv'],
  includeDetails: true,
  includeTrends: true,
  includeCharts: true
};

// Generate reports
const files = await engine.generateReport(report);
// Returns: { json: 'path/to/report.json', html: 'path/to/report.html', ... }
```

## Configuration

### Basic Configuration (YAML)

```yaml
version: "1.0.0"
engine:
  baseline:
    storagePath: "./baselines"
    retentionPolicy:
      maxVersions: 10
      maxAge: 30
    mergeStrategy: "latest"
    backupEnabled: true

  reporting:
    formats: ["json", "html"]
    outputPath: "./reports"
    includeDetails: true
    includeTrends: true

metricsCollector:
  parsers:
    jest:
      enabled: true
      resultsPath: "./test-results.json"
      coveragePath: "./coverage"

  performance:
    enabled: true
    sources: ["./performance-metrics.json"]

ruleEngine:
  rulesPath: "./baseline-rules.json"
  autoSave: true
  enableProgressive: true
  progressiveSteps: 5
  defaultSeverity: "warning"
```

### Configuration Templates

Use predefined templates for quick setup:

```typescript
const configManager = new ConfigManager('./config.yml');

// Apply templates
await configManager.applyTemplate('minimal');      // Basic setup
await configManager.applyTemplate('standard');     // Default setup
await configManager.applyTemplate('comprehensive'); // Full features
await configManager.applyTemplate('ci_cd');        // CI/CD optimized
```

## Rule Templates

### Coverage Rules

```typescript
// Basic coverage thresholds
await engine.createRulesFromTemplate('coverage_basic', {
  severity: 'error',
  progressive: true
});

// Creates rules for:
// - Line coverage >= 80%
// - Function coverage >= 80%
// - Branch coverage >= 70%
```

### Test Quality Rules

```typescript
// Test reliability rules
await engine.createRulesFromTemplate('test_quality', {
  severity: 'error'
});

// Creates rules for:
// - No failing tests
// - 100% pass rate
// - Coverage regression prevention
```

### Performance Rules

```typescript
// Performance monitoring
await engine.createRulesFromTemplate('performance_basic', {
  progressive: true,
  severity: 'warning'
});

// Creates rules for:
// - Test duration limits
// - Memory usage thresholds
```

## Advanced Features

### Progressive Improvement

Set up rules that gradually improve over time:

```typescript
await engine.addRule({
  id: 'progressive-coverage',
  name: 'Progressive Coverage',
  metric: 'coverage.lines.percentage',
  type: 'absolute',
  comparison: 'gte',
  value: 70,        // Starting point
  severity: 'warning',
  progressive: true, // Enable progressive mode
  enabled: true,
  metadata: {
    targetValue: 90  // Final goal
  }
});

// Calculate next targets
const targets = await engine.createProgressiveTargets(snapshot);
await engine.updateProgressiveRules(targets);
```

### Trend Analysis

Analyze metric trends across multiple snapshots:

```typescript
const snapshots = await getHistoricalSnapshots();
const analysis = await engine.analyzeTrend(snapshots, 'coverage.lines.percentage');

console.log(`
  Trend: ${analysis.trend}           // 'improving', 'declining', 'stable', 'volatile'
  Slope: ${analysis.slope}           // Rate of change
  Volatility: ${analysis.volatility} // Stability measure
  Correlation: ${analysis.correlation} // Linear correlation
`);
```

### Custom Metrics Parsers

Add support for custom metric formats:

```typescript
// Custom parser module
export default {
  async parse(filePath: string): Promise<TestResult[]> {
    const data = await readFile(filePath);
    // Parse your custom format
    return convertToTestResults(data);
  }
};

// Use in configuration
const config = {
  parsers: {
    custom: [{
      name: 'my-custom-parser',
      enabled: true,
      path: './test-results.custom',
      parser: './parsers/custom-parser.js'
    }]
  }
};
```

### Validation & Health Checks

Built-in validation and monitoring:

```typescript
// Validate data
const isValidSnapshot = await engine.validateSnapshot(snapshot);
const isValidBaseline = await engine.validateBaseline(baseline);
const isValidRule = await engine.validateRule(rule);

// Health check
const health = await engine.healthCheck();
if (health.status === 'unhealthy') {
  console.log('Issues:', health.components);
}

// Configuration validation
const configManager = new ConfigManager('./config.yml');
const validation = configManager.validateConfig(config);
if (!validation.valid) {
  console.log('Errors:', validation.errors);
  console.log('Warnings:', validation.warnings);
}
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Baseline Tracking
on: [push, pull_request]

jobs:
  baseline-check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '18'

      - name: Install dependencies
        run: npm ci

      - name: Run tests
        run: npm test -- --coverage

      - name: Baseline comparison
        run: |
          npx baseline-tracking-engine compare \
            --branch ${{ github.ref_name }} \
            --commit ${{ github.sha }} \
            --environment "ci" \
            --version ${{ github.run_number }}

      - name: Upload reports
        uses: actions/upload-artifact@v3
        with:
          name: baseline-reports
          path: reports/
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any
    stages {
        stage('Test & Coverage') {
            steps {
                sh 'npm test -- --coverage'
            }
        }
        stage('Baseline Check') {
            steps {
                script {
                    sh """
                        npx baseline-tracking-engine compare \
                            --branch ${env.BRANCH_NAME} \
                            --commit ${env.GIT_COMMIT} \
                            --environment production \
                            --version ${env.BUILD_NUMBER}
                    """
                }
            }
        }
    }
    post {
        always {
            publishHTML([
                allowMissing: false,
                alwaysLinkToLastBuild: true,
                keepAll: true,
                reportDir: 'reports',
                reportFiles: '*.html',
                reportName: 'Baseline Report'
            ])
        }
    }
}
```

## API Reference

### BaselineTrackingEngine

Main orchestrator class for all operations.

#### Methods

- `initialize()`: Initialize the engine and load configuration
- `collectMetrics(id, branch, commit, env, version, metadata?)`: Collect current metrics
- `createBaseline(name, snapshot, options?)`: Create new baseline
- `loadBaseline(id)`: Load existing baseline
- `compareAgainstBaseline(snapshot, baselineId, options?)`: Compare against specific baseline
- `compareAgainstDefault(snapshot, options?)`: Compare against default baseline
- `generateReport(report)`: Generate reports in configured formats
- `addRule(rule)`: Add threshold rule
- `updateRule(id, updates)`: Update existing rule
- `getRules(filter?)`: Get rules with optional filtering
- `healthCheck()`: Check system health
- `shutdown()`: Cleanup resources

### ConfigManager

Manages configuration loading, validation, and templates.

#### Methods

- `loadConfig()`: Load configuration from file
- `saveConfig(config?)`: Save configuration to file
- `updateConfig(updates)`: Update specific configuration sections
- `validateConfig(config)`: Validate configuration against schema
- `getConfigTemplates()`: Get available configuration templates
- `applyTemplate(name, overrides?)`: Apply configuration template
- `createBackup()`: Create configuration backup
- `restoreFromBackup(path)`: Restore from backup

## Examples

See the `/examples` directory for complete usage examples:

- `basic-usage.ts`: Simple baseline tracking workflow
- `advanced-configuration.ts`: Advanced features and configuration
- `ci-cd-integration.ts`: Continuous integration examples
- `custom-parsers.ts`: Custom metrics parser examples

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

MIT License - see LICENSE file for details.

## Support

- 📚 [Documentation](./docs/)
- 🐛 [Issue Tracker](https://github.com/your-repo/baseline-tracking-engine/issues)
- 💬 [Discussions](https://github.com/your-repo/baseline-tracking-engine/discussions)