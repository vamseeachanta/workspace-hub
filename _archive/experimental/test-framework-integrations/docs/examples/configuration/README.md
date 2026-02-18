# Configuration Examples

This directory contains comprehensive examples of different configuration patterns for the Test Framework Integrations system. Each example demonstrates specific configuration scenarios and their practical applications.

## Available Examples

### 1. Environment-Specific Configurations

#### [Development Configuration](./development.config.js)
Optimized for local development with watch mode, detailed reporting, and fast feedback.

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
    coverage: true,
    verbose: true
  },
  baseline: {
    enabled: true,
    autoSave: true,
    directory: 'baselines'
  },
  performance: {
    enabled: true,
    thresholds: {
      testDuration: 10000 // Relaxed for development
    }
  },
  reporting: {
    formats: ['console', 'html'],
    detailed: true,
    includeSkipped: true
  }
};
```

#### [Production Configuration](./production.config.js)
Optimized for CI/CD environments with strict thresholds and comprehensive reporting.

```javascript
module.exports = {
  framework: {
    type: 'jest',
    testDir: 'src',
    testPattern: '**/*.{test,spec}.{js,ts}'
  },
  execution: {
    mode: 'parallel',
    maxWorkers: 4,
    timeout: 30000,
    retries: 2,
    bail: true,
    coverage: true
  },
  baseline: {
    enabled: true,
    autoSave: false,
    compareThreshold: 0.03,
    storage: {
      type: 's3',
      options: {
        bucket: 'test-baselines-prod',
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
  rules: {
    coverage: {
      global: {
        statements: 85,
        branches: 80,
        functions: 85,
        lines: 85
      }
    }
  },
  reporting: {
    formats: ['json', 'junit', 'html'],
    outputDir: 'test-results',
    coverage: {
      enabled: true,
      formats: ['html', 'cobertura']
    }
  },
  integrations: {
    ci: {
      provider: 'github',
      uploadArtifacts: true
    },
    codecov: {
      enabled: true
    }
  }
};
```

### 2. Framework-Specific Configurations

#### [Multi-Framework Configuration](./multi-framework.config.js)
Running multiple testing frameworks in a coordinated manner.

```javascript
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
        testPattern: '**/*.e2e.test.js',
        browsers: ['chromium', 'firefox']
      },
      api: {
        type: 'mocha',
        testDir: 'tests/api',
        testPattern: '**/*.api.test.js',
        timeout: 10000
      }
    }
  },
  execution: {
    mode: 'sequential',
    coverage: true
  },
  baseline: {
    enabled: true,
    includePerformance: true
  },
  reporting: {
    formats: ['json', 'html'],
    aggregated: true
  }
};
```

### 3. Advanced Feature Configurations

#### [Performance Monitoring Configuration](./performance-monitoring.config.js)
Comprehensive performance monitoring and alerting setup.

```javascript
module.exports = {
  framework: { type: 'jest' },
  performance: {
    enabled: true,
    collectMetrics: ['duration', 'memory', 'cpu', 'network'],
    thresholds: {
      testDuration: 5000,
      suiteDuration: 30000,
      totalDuration: 300000,
      memoryUsage: 256 * 1024 * 1024,
      cpuUsage: 80
    },
    profiling: {
      enabled: true,
      sampleRate: 1000,
      includeNodeModules: false,
      outputFormat: 'json'
    },
    monitoring: {
      realTime: true,
      interval: 1000,
      alerts: {
        enabled: true,
        thresholdMultiplier: 1.5,
        channels: ['console', 'webhook', 'slack']
      }
    },
    benchmarks: {
      enabled: true,
      iterations: 100,
      warmupIterations: 10,
      compareWithBaseline: true
    }
  },
  baseline: {
    enabled: true,
    includePerformance: true,
    comparison: {
      tolerance: {
        performance: 0.1,
        memory: 0.2
      }
    }
  }
};
```

#### [Baseline Management Configuration](./baseline-management.config.js)
Advanced baseline storage, comparison, and retention settings.

```javascript
module.exports = {
  framework: { type: 'jest' },
  baseline: {
    enabled: true,
    directory: 'baselines',
    autoSave: true,
    autoLoad: true,
    compareThreshold: 0.05,
    includePerformance: true,
    includeCoverage: true,
    compression: 'gzip',

    retention: {
      maxAge: '30d',
      maxCount: 100,
      cleanupInterval: '1d'
    },

    comparison: {
      strict: false,
      ignoreFields: ['timestamp', 'duration'],
      tolerance: {
        performance: 0.15,
        coverage: 0.02,
        testCount: 0
      }
    },

    storage: {
      type: 'multi',
      providers: [
        {
          name: 'primary',
          type: 's3',
          options: {
            bucket: 'test-baselines',
            region: 'us-east-1',
            prefix: 'project-name'
          }
        },
        {
          name: 'backup',
          type: 'filesystem',
          options: {
            path: './baselines-backup'
          }
        }
      ]
    }
  }
};
```

### 4. Plugin Configurations

#### [Custom Plugins Configuration](./plugins.config.js)
Integration with custom plugins and third-party services.

```javascript
module.exports = {
  framework: { type: 'jest' },

  plugins: {
    enabled: [
      'slack-reporter',
      'custom-storage',
      'performance-analyzer',
      'security-scanner'
    ],

    autoLoad: true,
    searchPaths: ['./plugins', './node_modules'],

    configuration: {
      'slack-reporter': {
        webhookUrl: process.env.SLACK_WEBHOOK_URL,
        channels: ['#testing', '#ci-cd'],
        conditions: {
          onFailure: true,
          onSuccess: false,
          onRegression: true
        },
        messageFormat: 'detailed'
      },

      'custom-storage': {
        provider: 'mongodb',
        connectionString: process.env.MONGODB_URL,
        database: 'test-results',
        collection: 'baselines'
      },

      'performance-analyzer': {
        enabled: true,
        algorithms: ['trend-analysis', 'anomaly-detection'],
        alertThreshold: 0.2,
        historicalDataDays: 30
      },

      'security-scanner': {
        enabled: process.env.NODE_ENV === 'production',
        scanTypes: ['dependency-check', 'code-analysis'],
        severity: 'medium',
        failOnIssues: true
      }
    }
  }
};
```

### 5. Specialized Use Cases

#### [Microservices Configuration](./microservices.config.js)
Testing strategy for microservices architecture.

```javascript
module.exports = {
  framework: {
    type: 'multi',
    configurations: {
      // Individual service tests
      'user-service': {
        type: 'jest',
        testDir: 'services/user-service/tests',
        testPattern: '**/*.test.js',
        coverage: true,
        setupFiles: ['./services/user-service/test-setup.js']
      },

      'order-service': {
        type: 'jest',
        testDir: 'services/order-service/tests',
        testPattern: '**/*.test.js',
        coverage: true,
        setupFiles: ['./services/order-service/test-setup.js']
      },

      'payment-service': {
        type: 'jest',
        testDir: 'services/payment-service/tests',
        testPattern: '**/*.test.js',
        coverage: true,
        setupFiles: ['./services/payment-service/test-setup.js']
      },

      // Contract tests
      contracts: {
        type: 'jest',
        testDir: 'tests/contracts',
        testPattern: '**/*.contract.test.js',
        setupFiles: ['./tests/contracts/setup.js']
      },

      // Integration tests
      integration: {
        type: 'jest',
        testDir: 'tests/integration',
        testPattern: '**/*.integration.test.js',
        timeout: 30000,
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
    mode: 'adaptive', // Parallel for unit tests, sequential for integration
    maxWorkers: 6,
    coverage: true
  },

  baseline: {
    enabled: true,
    includePerformance: true,
    comparison: {
      tolerance: {
        performance: 0.2, // Higher tolerance for microservices
        coverage: 0.05
      }
    }
  },

  reporting: {
    formats: ['json', 'html', 'junit'],
    aggregated: true,
    serviceBreakdown: true
  }
};
```

#### [Legacy Migration Configuration](./legacy-migration.config.js)
Gradual migration from legacy test systems.

```javascript
module.exports = {
  framework: {
    type: 'multi',
    configurations: {
      // Keep running legacy tests during migration
      legacy: {
        type: 'custom',
        testCommand: './scripts/run-legacy-tests.sh',
        resultParser: 'legacy-xml',
        timeout: 120000
      },

      // New modern tests
      modern: {
        type: 'jest',
        testDir: 'tests/modern',
        testPattern: '**/*.test.js',
        coverage: true
      },

      // Parallel validation tests
      validation: {
        type: 'jest',
        testDir: 'tests/validation',
        testPattern: '**/*.validation.test.js',
        setupFiles: ['./tests/validation/setup.js']
      }
    }
  },

  execution: {
    mode: 'parallel',
    coverage: true
  },

  baseline: {
    enabled: true,
    comparison: {
      crossFramework: true, // Compare results across frameworks
      tolerance: {
        testCount: 5, // Allow some variance during migration
        coverage: 0.1
      }
    }
  },

  migration: {
    enabled: true,
    strategy: 'gradual',
    phases: [
      { name: 'baseline', frameworks: ['legacy'] },
      { name: 'parallel', frameworks: ['legacy', 'modern'] },
      { name: 'validation', frameworks: ['modern', 'validation'] },
      { name: 'cutover', frameworks: ['modern'] }
    ],
    currentPhase: process.env.MIGRATION_PHASE || 'parallel'
  }
};
```

## Configuration Validation

Each configuration example includes validation to ensure correctness:

```javascript
// validation-example.js
const { validateConfiguration } = require('test-framework-integrations');

function validateConfig(config) {
  try {
    const result = validateConfiguration(config);

    if (result.isValid) {
      console.log('✅ Configuration is valid');
      return true;
    } else {
      console.log('❌ Configuration validation failed:');
      result.errors.forEach(error => {
        console.log(`  - ${error.field}: ${error.message}`);
      });
      return false;
    }
  } catch (error) {
    console.error('Configuration validation error:', error.message);
    return false;
  }
}

// Usage
const config = require('./development.config.js');
validateConfig(config);
```

## Dynamic Configuration

Examples of runtime configuration based on environment:

```javascript
// dynamic.config.js
const os = require('os');

function createDynamicConfig() {
  const isCI = process.env.CI === 'true';
  const nodeEnv = process.env.NODE_ENV || 'development';
  const cpuCount = os.cpus().length;

  return {
    framework: {
      type: process.env.TEST_FRAMEWORK || 'jest'
    },

    execution: {
      mode: 'parallel',
      maxWorkers: isCI ? Math.min(cpuCount, 4) : Math.max(1, cpuCount - 1),
      timeout: isCI ? 60000 : 30000,
      retries: isCI ? 2 : 0,
      bail: isCI,
      coverage: nodeEnv !== 'development'
    },

    baseline: {
      enabled: true,
      autoSave: !isCI,
      storage: isCI ? {
        type: 's3',
        options: {
          bucket: process.env.BASELINE_BUCKET,
          region: process.env.AWS_REGION
        }
      } : {
        type: 'filesystem',
        path: './baselines'
      }
    },

    reporting: {
      formats: isCI ? ['json', 'junit'] : ['console', 'html'],
      verbose: nodeEnv === 'development'
    }
  };
}

module.exports = createDynamicConfig();
```

## Running Configuration Examples

```bash
# Validate a configuration
node validate-config.js development.config.js

# Test with specific configuration
TEST_CONFIG=production.config.js npm test

# Compare configurations
node compare-configs.js development.config.js production.config.js

# Generate configuration from template
node generate-config.js --template microservices --env production
```

These configuration examples provide comprehensive templates for various use cases and deployment scenarios, helping users quickly adapt the Test Framework Integrations system to their specific needs.