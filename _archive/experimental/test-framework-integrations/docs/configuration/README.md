# Configuration Reference

## Overview

The Test Framework Integrations system provides flexible configuration options to customize test execution, reporting, performance monitoring, and baseline management. This reference covers all available configuration options and their usage.

## Configuration Files

### Primary Configuration

The main configuration file can be one of:
- `test-integration.config.js` (JavaScript)
- `test-integration.config.json` (JSON)
- `test-integration.config.yaml` (YAML)
- Configuration in `package.json` under the `testIntegration` key

### Framework-Specific Configuration

Each testing framework may have additional configuration:
- **Jest**: `jest.config.js`
- **Mocha**: `.mocharc.json`
- **Pytest**: `pytest.ini` or `pyproject.toml`
- **Playwright**: `playwright.config.ts`
- **Vitest**: `vitest.config.ts`

## Quick Reference

| Section | Description | Required |
|---------|-------------|----------|
| [`framework`](#framework-configuration) | Testing framework settings | ✅ |
| [`execution`](#execution-configuration) | Test execution options | ❌ |
| [`baseline`](#baseline-configuration) | Baseline tracking settings | ❌ |
| [`performance`](#performance-configuration) | Performance monitoring | ❌ |
| [`reporting`](#reporting-configuration) | Output and reporting | ❌ |
| [`environment`](#environment-configuration) | Environment variables | ❌ |
| [`plugins`](#plugins-configuration) | Plugin system settings | ❌ |
| [`rules`](#rules-configuration) | Custom rules and thresholds | ❌ |
| [`integrations`](#integrations-configuration) | Third-party integrations | ❌ |

## Configuration Sections

### Framework Configuration

Core framework settings that determine how tests are executed.

```javascript
{
  "framework": {
    "type": "jest",              // Required: jest|mocha|pytest|playwright|vitest
    "version": "^29.0.0",        // Framework version constraint
    "autoDetect": true,          // Auto-detect framework from project
    "fallback": "jest",          // Fallback if detection fails
    "configFile": "jest.config.js", // Framework config file path
    "testCommand": "npm test",   // Custom test command
    "testDir": "tests",          // Test directory
    "testPattern": "**/*.test.js", // Test file pattern
    "setupFiles": ["./setup.js"], // Setup files to run before tests
    "teardownFiles": ["./teardown.js"] // Cleanup files after tests
  }
}
```

### Execution Configuration

Settings that control how tests are executed.

```javascript
{
  "execution": {
    "mode": "parallel",          // parallel|sequential|adaptive
    "maxWorkers": 4,             // Maximum parallel workers
    "timeout": 30000,            // Default test timeout (ms)
    "retries": 2,                // Number of retries for failed tests
    "bail": false,               // Stop on first failure
    "verbose": true,             // Verbose output
    "watch": false,              // Watch mode
    "coverage": true,            // Enable coverage collection
    "silent": false,             // Suppress console output
    "forceExit": false,          // Force exit after tests
    "detectOpenHandles": true,   // Detect open handles preventing exit
    "passWithNoTests": false,    // Pass when no tests found
    "skipUnchanged": false,      // Skip tests for unchanged files
    "updateSnapshots": false,    // Update snapshots
    "clearCache": false          // Clear cache before running
  }
}
```

### Baseline Configuration

Configuration for baseline tracking and comparison.

```javascript
{
  "baseline": {
    "enabled": true,             // Enable baseline functionality
    "directory": "baselines",    // Directory to store baselines
    "autoSave": true,            // Automatically save new baselines
    "autoLoad": true,            // Automatically load existing baselines
    "compareThreshold": 0.05,    // Threshold for detecting changes (5%)
    "includePerformance": true,  // Include performance in baselines
    "includeCoverage": true,     // Include coverage in baselines
    "compression": "gzip",       // Compression method: none|gzip|brotli
    "retention": {
      "maxAge": "30d",           // Maximum age of baselines
      "maxCount": 100,           // Maximum number of baselines
      "cleanupInterval": "1d"    // Cleanup interval
    },
    "comparison": {
      "strict": false,           // Strict comparison mode
      "ignoreFields": [],        // Fields to ignore in comparison
      "tolerance": {
        "performance": 0.1,      // 10% tolerance for performance
        "coverage": 0.02,        // 2% tolerance for coverage
        "testCount": 0           // No tolerance for test count changes
      }
    },
    "storage": {
      "type": "filesystem",     // filesystem|s3|gcs|azure
      "path": "./baselines",    // Storage path
      "options": {}             // Storage-specific options
    }
  }
}
```

### Performance Configuration

Settings for performance monitoring and profiling.

```javascript
{
  "performance": {
    "enabled": true,             // Enable performance monitoring
    "collectMetrics": [          // Metrics to collect
      "duration",
      "memory",
      "cpu",
      "network"
    ],
    "thresholds": {
      "testDuration": 5000,      // Max test duration (ms)
      "suiteDuration": 30000,    // Max suite duration (ms)
      "totalDuration": 300000,   // Max total duration (ms)
      "memoryUsage": 268435456,  // Max memory usage (bytes)
      "cpuUsage": 80,            // Max CPU usage (%)
      "networkRequests": 100     // Max network requests
    },
    "profiling": {
      "enabled": false,          // Enable detailed profiling
      "sampleRate": 1000,        // Profiling sample rate (Hz)
      "includeNodeModules": false, // Profile node_modules
      "outputFormat": "json"     // Output format: json|cpuprofile
    },
    "monitoring": {
      "realTime": false,         // Real-time monitoring
      "interval": 1000,          // Monitoring interval (ms)
      "alerts": {
        "enabled": true,         // Enable performance alerts
        "thresholdMultiplier": 1.5, // Alert when threshold exceeded by 1.5x
        "channels": ["console"]  // Alert channels: console|webhook|email
      }
    },
    "benchmarks": {
      "enabled": false,          // Enable benchmark tests
      "iterations": 100,         // Number of benchmark iterations
      "warmupIterations": 10,    // Warmup iterations
      "compareWithBaseline": true // Compare with baseline
    }
  }
}
```

### Reporting Configuration

Output and reporting options.

```javascript
{
  "reporting": {
    "formats": [                 // Output formats
      "json",
      "html",
      "junit",
      "console"
    ],
    "outputDir": "test-results", // Output directory
    "filename": "results",       // Base filename
    "includeSkipped": true,      // Include skipped tests
    "includePending": false,     // Include pending tests
    "includePassedAssertions": false, // Include passed assertions
    "timestamp": true,           // Add timestamp to reports
    "detailed": true,            // Include detailed information
    "summary": true,             // Include summary section
    "coverage": {
      "enabled": true,           // Include coverage in reports
      "formats": ["html", "json"], // Coverage report formats
      "directory": "coverage",   // Coverage output directory
      "watermarks": {            // Coverage watermarks
        "statements": [50, 80],
        "functions": [50, 80],
        "branches": [50, 80],
        "lines": [50, 80]
      }
    },
    "performance": {
      "enabled": true,           // Include performance data
      "charts": true,            // Generate performance charts
      "trends": true,            // Show performance trends
      "baseline": true           // Compare with baseline
    },
    "notifications": {
      "enabled": false,          // Enable notifications
      "channels": [],            // Notification channels
      "conditions": [            // When to send notifications
        "failure",
        "regression"
      ]
    }
  }
}
```

### Environment Configuration

Environment variables and runtime settings.

```javascript
{
  "environment": {
    "node": {
      "version": ">=16.0.0",     // Required Node.js version
      "flags": [                 // Node.js flags
        "--max-old-space-size=4096"
      ]
    },
    "variables": {               // Environment variables
      "NODE_ENV": "test",
      "CI": "false",
      "DEBUG": "app:*"
    },
    "paths": {
      "node_modules": "./node_modules",
      "cache": "./.cache",
      "temp": "./tmp"
    },
    "limits": {
      "maxMemory": "2GB",        // Memory limit
      "maxDuration": "30m",      // Maximum execution time
      "maxFiles": 10000          // Maximum number of files
    }
  }
}
```

### Plugins Configuration

Plugin system configuration.

```javascript
{
  "plugins": {
    "enabled": ["reporter", "baseline"], // Enabled plugins
    "disabled": ["notifications"],        // Disabled plugins
    "autoLoad": true,                    // Auto-load plugins
    "searchPaths": [                     // Plugin search paths
      "./plugins",
      "./node_modules"
    ],
    "configuration": {                   // Plugin-specific configuration
      "reporter": {
        "customTemplate": "./templates/report.html"
      },
      "baseline": {
        "uploadToS3": true,
        "s3Bucket": "my-baselines"
      }
    }
  }
}
```

### Rules Configuration

Custom rules and validation thresholds.

```javascript
{
  "rules": {
    "coverage": {
      "global": {
        "statements": 80,          // Minimum statement coverage
        "branches": 75,            // Minimum branch coverage
        "functions": 80,           // Minimum function coverage
        "lines": 80                // Minimum line coverage
      },
      "perFile": {
        "statements": 70,          // Per-file minimums
        "branches": 65,
        "functions": 70,
        "lines": 70
      }
    },
    "performance": {
      "regressionThreshold": 0.15, // 15% performance regression limit
      "absoluteThresholds": {
        "testDuration": 10000,     // Max test duration
        "memoryUsage": 100000000   // Max memory usage
      }
    },
    "quality": {
      "maxTestFileSize": "50KB",   // Maximum test file size
      "maxTestsPerFile": 100,      // Maximum tests per file
      "requireDescriptions": true, // Require test descriptions
      "forbiddenPatterns": [       // Forbidden code patterns
        "console.log",
        "debugger"
      ]
    },
    "dependencies": {
      "allowedPackages": [],       // Whitelist of allowed packages
      "blockedPackages": [],       // Blacklist of blocked packages
      "maxDependencies": 1000      // Maximum number of dependencies
    }
  }
}
```

### Integrations Configuration

Third-party service integrations.

```javascript
{
  "integrations": {
    "ci": {
      "provider": "github",       // CI provider: github|gitlab|jenkins|azure
      "uploadArtifacts": true,    // Upload test artifacts
      "commentOnPR": true,        // Comment on pull requests
      "failOnRegression": true    // Fail CI on performance regression
    },
    "codecov": {
      "enabled": true,            // Enable Codecov integration
      "token": "${CODECOV_TOKEN}", // Codecov token (use env var)
      "flags": ["unit", "integration"] // Coverage flags
    },
    "sonarqube": {
      "enabled": false,           // Enable SonarQube integration
      "serverUrl": "https://sonar.example.com",
      "projectKey": "my-project"
    },
    "slack": {
      "enabled": false,           // Enable Slack notifications
      "webhook": "${SLACK_WEBHOOK}",
      "channels": ["#testing"],
      "mentions": ["@team"]
    },
    "datadog": {
      "enabled": false,           // Enable Datadog metrics
      "apiKey": "${DATADOG_API_KEY}",
      "tags": ["env:test", "team:qa"]
    }
  }
}
```

## Configuration Examples

### Minimal Configuration

```javascript
// test-integration.config.js
module.exports = {
  framework: {
    type: 'jest'
  }
};
```

### Development Configuration

```javascript
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
  performance: {
    enabled: true,
    thresholds: {
      testDuration: 10000
    }
  },
  reporting: {
    formats: ['console', 'html'],
    detailed: true
  }
};
```

### Production Configuration

```javascript
module.exports = {
  framework: {
    type: 'jest',
    testDir: 'tests',
    testPattern: '**/*.{test,spec}.{js,ts}'
  },
  execution: {
    mode: 'parallel',
    maxWorkers: 4,
    timeout: 30000,
    retries: 2,
    coverage: true,
    bail: true
  },
  baseline: {
    enabled: true,
    autoSave: true,
    compareThreshold: 0.03,
    compression: 'gzip',
    storage: {
      type: 's3',
      options: {
        bucket: 'my-test-baselines',
        region: 'us-east-1'
      }
    }
  },
  performance: {
    enabled: true,
    thresholds: {
      testDuration: 5000,
      totalDuration: 300000
    },
    monitoring: {
      alerts: {
        enabled: true,
        channels: ['webhook']
      }
    }
  },
  reporting: {
    formats: ['json', 'html', 'junit'],
    coverage: {
      enabled: true,
      formats: ['html', 'cobertura'],
      watermarks: {
        statements: [70, 90],
        functions: [70, 90],
        branches: [60, 85],
        lines: [70, 90]
      }
    }
  },
  rules: {
    coverage: {
      global: {
        statements: 85,
        branches: 80,
        functions: 85,
        lines: 85
      }
    },
    performance: {
      regressionThreshold: 0.1
    }
  },
  integrations: {
    ci: {
      provider: 'github',
      uploadArtifacts: true,
      commentOnPR: true
    },
    codecov: {
      enabled: true
    }
  }
};
```

### Multi-Framework Configuration

```javascript
module.exports = {
  framework: {
    type: 'multi',
    configurations: {
      unit: {
        type: 'jest',
        testDir: 'src',
        testPattern: '**/*.test.js'
      },
      integration: {
        type: 'jest',
        testDir: 'tests/integration',
        testPattern: '**/*.integration.test.js'
      },
      e2e: {
        type: 'playwright',
        testDir: 'tests/e2e',
        testPattern: '**/*.e2e.test.js'
      }
    }
  },
  execution: {
    mode: 'sequential',
    coverage: true
  },
  baseline: {
    enabled: true,
    autoSave: true
  },
  reporting: {
    formats: ['html', 'json'],
    outputDir: 'test-results'
  }
};
```

## Environment Variables

The following environment variables can override configuration:

| Variable | Description | Default |
|----------|-------------|---------|
| `TEST_FRAMEWORK` | Override framework type | - |
| `TEST_TIMEOUT` | Override test timeout | 30000 |
| `TEST_RETRIES` | Override retry count | 0 |
| `COVERAGE_ENABLED` | Enable/disable coverage | true |
| `BASELINE_ENABLED` | Enable/disable baseline | true |
| `PERFORMANCE_ENABLED` | Enable/disable performance | true |
| `PARALLEL_WORKERS` | Number of parallel workers | CPU cores |
| `OUTPUT_DIR` | Output directory | test-results |
| `VERBOSE` | Verbose output | false |
| `CI` | CI mode | false |

## Configuration Validation

The system validates configuration files and provides helpful error messages:

```javascript
// Invalid configuration example
{
  "framework": {
    "type": "invalid-framework"  // ❌ Unknown framework
  },
  "execution": {
    "maxWorkers": -1             // ❌ Invalid value
  },
  "performance": {
    "thresholds": {
      "testDuration": "invalid"  // ❌ Should be number
    }
  }
}
```

Validation errors will include:
- Field name and path
- Expected type/value
- Suggested corrections
- Documentation links

## Advanced Configuration

### Dynamic Configuration

```javascript
// test-integration.config.js
const os = require('os');
const isCI = process.env.CI === 'true';

module.exports = {
  framework: {
    type: 'jest'
  },
  execution: {
    maxWorkers: isCI ? os.cpus().length : 2,
    timeout: isCI ? 60000 : 30000,
    verbose: !isCI
  },
  baseline: {
    enabled: true,
    autoSave: !isCI  // Don't auto-save in CI
  },
  reporting: {
    formats: isCI ? ['json', 'junit'] : ['console', 'html']
  }
};
```

### Configuration Merging

Configurations are merged in the following order:
1. Default configuration
2. Global configuration file
3. Project configuration file
4. Package.json configuration
5. Environment variables
6. Command-line arguments

### Configuration Schema

The complete configuration schema is available as JSON Schema at:
- `/docs/configuration/schema.json`
- Online: `https://test-framework-integrations.dev/schema`

This allows for IDE autocompletion and validation in supported editors.