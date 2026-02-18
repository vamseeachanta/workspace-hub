# Troubleshooting Guide

## Overview

This guide helps you diagnose and resolve common issues when using the Test Framework Integrations system. Issues are organized by category with step-by-step solutions and prevention strategies.

## Quick Diagnosis

### System Health Check

Run the built-in diagnostic command:

```bash
npx test-integration doctor
```

This will check:
- ✅ Framework detection
- ✅ Configuration validation
- ✅ Dependencies
- ✅ Environment setup
- ✅ Baseline storage
- ✅ Performance monitoring

### Common Issue Categories

| Category | Description | Frequency |
|----------|-------------|-----------|
| [**Installation**](#installation-issues) | Package installation and setup | High |
| [**Configuration**](#configuration-issues) | Config file and environment | High |
| [**Framework Detection**](#framework-detection-issues) | Auto-detection problems | Medium |
| [**Performance**](#performance-issues) | Slow execution and monitoring | Medium |
| [**Baseline**](#baseline-issues) | Baseline creation and comparison | Medium |
| [**Coverage**](#coverage-issues) | Code coverage collection | Medium |
| [**Reporting**](#reporting-issues) | Output generation problems | Low |
| [**CI/CD**](#cicd-issues) | Continuous integration | Low |

## Installation Issues

### Package Not Found

**Symptoms:**
```bash
Error: Cannot find module 'test-framework-integrations'
```

**Solutions:**

1. **Install the package:**
   ```bash
   npm install test-framework-integrations
   # or
   npm install -g test-framework-integrations
   ```

2. **Check installation location:**
   ```bash
   npm list test-framework-integrations
   npm list -g test-framework-integrations
   ```

3. **Clear npm cache:**
   ```bash
   npm cache clean --force
   npm install
   ```

### Dependency Conflicts

**Symptoms:**
```bash
npm ERR! peer dep missing: jest@^29.0.0
npm ERR! conflicting dependencies
```

**Solutions:**

1. **Install peer dependencies:**
   ```bash
   npm install --save-dev jest@^29.0.0
   # Check package.json for required versions
   ```

2. **Use npm ls to check conflicts:**
   ```bash
   npm ls
   npm ls --depth=0
   ```

3. **Force resolution (package.json):**
   ```json
   {
     "overrides": {
       "jest": "^29.0.0"
     }
   }
   ```

### Node.js Version Issues

**Symptoms:**
```bash
Error: Requires Node.js >=16.0.0
```

**Solutions:**

1. **Check Node.js version:**
   ```bash
   node --version
   npm --version
   ```

2. **Upgrade Node.js:**
   ```bash
   # Using nvm
   nvm install 18
   nvm use 18

   # Or download from nodejs.org
   ```

3. **Use .nvmrc file:**
   ```bash
   echo "18" > .nvmrc
   nvm use
   ```

## Configuration Issues

### Invalid Configuration File

**Symptoms:**
```bash
Error: Invalid configuration in test-integration.config.js
ValidationError: "framework.type" must be one of [jest, mocha, pytest, playwright, vitest]
```

**Solutions:**

1. **Validate configuration:**
   ```bash
   npx test-integration config --validate
   ```

2. **Use configuration schema:**
   ```javascript
   // test-integration.config.js
   /** @type {import('test-framework-integrations').Config} */
   module.exports = {
     framework: {
       type: 'jest' // Must be valid framework
     }
   };
   ```

3. **Check JSON syntax:**
   ```bash
   # For JSON config files
   npx jsonlint test-integration.config.json
   ```

### Environment Variable Issues

**Symptoms:**
```bash
Warning: Invalid value for TEST_TIMEOUT: 'invalid'
Using default value: 30000
```

**Solutions:**

1. **Check environment variables:**
   ```bash
   npx test-integration config --show-env
   ```

2. **Validate variable types:**
   ```bash
   # Correct formats
   export TEST_TIMEOUT=30000
   export COVERAGE_ENABLED=true
   export OUTPUT_FORMAT=json,html
   ```

3. **Use .env file validation:**
   ```bash
   # Install dotenv-cli for validation
   npm install -g dotenv-cli
   dotenv -e .env -- npx test-integration config --validate
   ```

### Missing Configuration File

**Symptoms:**
```bash
Warning: No configuration file found, using defaults
```

**Solutions:**

1. **Create configuration file:**
   ```bash
   npx test-integration init
   ```

2. **Specify config file:**
   ```bash
   npx test-integration --config custom.config.js
   ```

3. **Use package.json configuration:**
   ```json
   {
     "testIntegration": {
       "framework": {
         "type": "jest"
       }
     }
   }
   ```

## Framework Detection Issues

### Framework Not Detected

**Symptoms:**
```bash
Warning: Could not detect testing framework
Falling back to: jest
```

**Solutions:**

1. **Explicit framework configuration:**
   ```javascript
   module.exports = {
     framework: {
       type: 'jest', // Explicitly set framework
       configFile: 'jest.config.js'
     }
   };
   ```

2. **Check framework dependencies:**
   ```bash
   npm list jest mocha playwright pytest vitest
   ```

3. **Verify framework config files:**
   ```bash
   ls -la jest.config.* mocha.opts .mocharc.* playwright.config.* pytest.ini vitest.config.*
   ```

### Multiple Frameworks Detected

**Symptoms:**
```bash
Warning: Multiple frameworks detected: jest, mocha
Using: jest
```

**Solutions:**

1. **Specify primary framework:**
   ```javascript
   module.exports = {
     framework: {
       type: 'jest', // Primary framework
       autoDetect: false
     }
   };
   ```

2. **Use multi-framework configuration:**
   ```javascript
   module.exports = {
     framework: {
       type: 'multi',
       configurations: {
         unit: { type: 'jest' },
         e2e: { type: 'playwright' }
       }
     }
   };
   ```

### Framework Version Mismatch

**Symptoms:**
```bash
Error: Jest version 28.1.0 is not compatible
Required: ^29.0.0
```

**Solutions:**

1. **Update framework version:**
   ```bash
   npm install --save-dev jest@^29.0.0
   npm update
   ```

2. **Check version constraints:**
   ```bash
   npm outdated
   npm audit
   ```

3. **Use compatible version:**
   ```javascript
   module.exports = {
     framework: {
       type: 'jest',
       version: '^28.0.0' // Adjust constraint
     }
   };
   ```

## Performance Issues

### Slow Test Execution

**Symptoms:**
- Tests taking longer than expected
- High memory usage
- CPU utilization at 100%

**Diagnosis:**

```bash
# Enable performance monitoring
export PERFORMANCE_ENABLED=true
export DEBUG=test-integration:performance
npm test
```

**Solutions:**

1. **Optimize parallel execution:**
   ```javascript
   module.exports = {
     execution: {
       mode: 'parallel',
       maxWorkers: 4, // Adjust based on CPU cores
     }
   };
   ```

2. **Increase timeouts:**
   ```javascript
   module.exports = {
     execution: {
       timeout: 60000, // Increase from default 30s
     },
     performance: {
       thresholds: {
         testDuration: 10000 // Individual test limit
       }
     }
   };
   ```

3. **Memory optimization:**
   ```bash
   # Increase Node.js memory limit
   export NODE_OPTIONS="--max-old-space-size=4096"
   npm test
   ```

### Memory Leaks

**Symptoms:**
```bash
FATAL ERROR: Ineffective mark-compacts near heap limit
Allocation failed - JavaScript heap out of memory
```

**Solutions:**

1. **Monitor memory usage:**
   ```javascript
   module.exports = {
     performance: {
       enabled: true,
       collectMetrics: ['memory'],
       thresholds: {
         memoryUsage: 512 * 1024 * 1024 // 512MB limit
       }
     }
   };
   ```

2. **Enable garbage collection:**
   ```bash
   export NODE_OPTIONS="--expose-gc --max-old-space-size=4096"
   npm test
   ```

3. **Cleanup test files:**
   ```javascript
   // In test setup
   afterEach(() => {
     // Clear mocks
     jest.clearAllMocks();
     // Force garbage collection
     if (global.gc) global.gc();
   });
   ```

### Hanging Tests

**Symptoms:**
- Tests never complete
- Process doesn't exit
- Open handles detected

**Solutions:**

1. **Enable handle detection:**
   ```javascript
   module.exports = {
     execution: {
       detectOpenHandles: true,
       forceExit: true
     }
   };
   ```

2. **Debug open handles:**
   ```bash
   # For Jest
   npm test -- --detectOpenHandles --forceExit
   ```

3. **Manual cleanup:**
   ```javascript
   // In test teardown
   afterAll(async () => {
     // Close database connections
     await database.close();
     // Clear timers
     clearInterval(someInterval);
     // Close servers
     await server.close();
   });
   ```

## Baseline Issues

### Baseline Creation Failed

**Symptoms:**
```bash
Error: Failed to save baseline to ./baselines/
ENOENT: no such file or directory
```

**Solutions:**

1. **Create baseline directory:**
   ```bash
   mkdir -p baselines
   chmod 755 baselines
   ```

2. **Check permissions:**
   ```bash
   ls -la baselines/
   # Should show write permissions
   ```

3. **Configure baseline storage:**
   ```javascript
   module.exports = {
     baseline: {
       enabled: true,
       directory: 'baselines',
       autoSave: true
     }
   };
   ```

### Baseline Comparison Errors

**Symptoms:**
```bash
Error: Baseline comparison failed
TypeError: Cannot read property 'performance' of undefined
```

**Solutions:**

1. **Verify baseline format:**
   ```bash
   # Check baseline file structure
   cat baselines/latest.json | jq '.'
   ```

2. **Reset corrupted baselines:**
   ```bash
   # Backup and recreate
   mv baselines baselines.backup
   mkdir baselines
   npm test # Will create new baseline
   ```

3. **Configure comparison tolerance:**
   ```javascript
   module.exports = {
     baseline: {
       compareThreshold: 0.1, // 10% tolerance
       comparison: {
         tolerance: {
           performance: 0.15,
           coverage: 0.05
         }
       }
     }
   };
   ```

### Baseline Storage Issues

**Symptoms:**
```bash
Error: S3 upload failed
AccessDenied: Access Denied
```

**Solutions:**

1. **Check storage configuration:**
   ```javascript
   module.exports = {
     baseline: {
       storage: {
         type: 's3',
         options: {
           bucket: 'my-baselines',
           region: 'us-east-1',
           accessKeyId: process.env.AWS_ACCESS_KEY_ID,
           secretAccessKey: process.env.AWS_SECRET_ACCESS_KEY
         }
       }
     }
   };
   ```

2. **Verify credentials:**
   ```bash
   aws configure list
   aws s3 ls s3://my-baselines/
   ```

3. **Fallback to filesystem:**
   ```javascript
   module.exports = {
     baseline: {
       storage: {
         type: 'filesystem',
         path: './baselines'
       }
     }
   };
   ```

## Coverage Issues

### Coverage Not Collected

**Symptoms:**
```bash
Warning: No coverage data collected
Coverage report will be empty
```

**Solutions:**

1. **Enable coverage:**
   ```javascript
   module.exports = {
     execution: {
       coverage: true
     },
     reporting: {
       coverage: {
         enabled: true
       }
     }
   };
   ```

2. **Check framework coverage setup:**
   ```javascript
   // For Jest
   module.exports = {
     collectCoverage: true,
     coverageDirectory: 'coverage',
     collectCoverageFrom: [
       'src/**/*.{js,ts}',
       '!src/**/*.test.{js,ts}'
     ]
   };
   ```

3. **Verify instrumentation:**
   ```bash
   # Check if source files are instrumented
   npm test -- --verbose
   ```

### Coverage Thresholds Failed

**Symptoms:**
```bash
Error: Coverage threshold for statements (75%) not met: 60%
```

**Solutions:**

1. **Adjust thresholds:**
   ```javascript
   module.exports = {
     rules: {
       coverage: {
         global: {
           statements: 60, // Lower threshold temporarily
           branches: 55,
           functions: 60,
           lines: 60
         }
       }
     }
   };
   ```

2. **Identify uncovered code:**
   ```bash
   # Generate detailed coverage report
   npm test -- --coverage --verbose
   open coverage/lcov-report/index.html
   ```

3. **Exclude files from coverage:**
   ```javascript
   // In framework config
   coveragePathIgnorePatterns: [
     '/node_modules/',
     '/test/',
     '/dist/'
   ]
   ```

### Invalid Coverage Data

**Symptoms:**
```bash
Error: Coverage data is malformed
SyntaxError: Unexpected token in JSON
```

**Solutions:**

1. **Clear coverage cache:**
   ```bash
   rm -rf coverage/
   rm -rf .nyc_output/
   npm test
   ```

2. **Check coverage tools:**
   ```bash
   npm list nyc istanbul @jest/coverage
   ```

3. **Regenerate coverage:**
   ```bash
   npm test -- --coverage --no-cache
   ```

## Reporting Issues

### Report Generation Failed

**Symptoms:**
```bash
Error: Failed to generate HTML report
ENOENT: no such file or directory, open 'template.html'
```

**Solutions:**

1. **Check output directory:**
   ```bash
   mkdir -p test-results
   chmod 755 test-results
   ```

2. **Verify report format:**
   ```javascript
   module.exports = {
     reporting: {
       formats: ['json', 'html'], // Valid formats
       outputDir: 'test-results'
     }
   };
   ```

3. **Use built-in templates:**
   ```javascript
   module.exports = {
     reporting: {
       formats: ['html'],
       template: 'default' // Use built-in template
     }
   };
   ```

### Report Files Missing

**Symptoms:**
```bash
Warning: Expected report file not found
test-results/results.json does not exist
```

**Solutions:**

1. **Check write permissions:**
   ```bash
   ls -la test-results/
   touch test-results/test-write
   rm test-results/test-write
   ```

2. **Debug report generation:**
   ```bash
   export DEBUG=test-integration:reporting
   npm test
   ```

3. **Manual report generation:**
   ```bash
   npx test-integration report --input results.json --format html
   ```

## CI/CD Issues

### CI Build Failures

**Symptoms:**
```bash
Error: Tests failed in CI environment
Exit code: 1
```

**Solutions:**

1. **Check CI configuration:**
   ```yaml
   # GitHub Actions
   - name: Run tests
     run: npm test
     env:
       CI: true
       NODE_ENV: test
   ```

2. **Adjust CI timeouts:**
   ```javascript
   module.exports = {
     execution: {
       timeout: process.env.CI ? 60000 : 30000,
       retries: process.env.CI ? 2 : 0
     }
   };
   ```

3. **Enable CI-specific settings:**
   ```javascript
   const isCI = process.env.CI === 'true';

   module.exports = {
     execution: {
       bail: isCI, // Stop on first failure in CI
       silent: isCI, // Reduce output in CI
       maxWorkers: isCI ? 2 : 4
     }
   };
   ```

### Artifact Upload Issues

**Symptoms:**
```bash
Error: Failed to upload test artifacts
HTTP 403: Forbidden
```

**Solutions:**

1. **Check CI permissions:**
   ```yaml
   # GitHub Actions
   permissions:
     contents: read
     actions: write
   ```

2. **Verify artifact paths:**
   ```yaml
   - name: Upload test results
     uses: actions/upload-artifact@v3
     with:
       name: test-results
       path: |
         test-results/
         coverage/
   ```

3. **Debug CI environment:**
   ```bash
   env | grep -E "(CI|GITHUB|GITLAB)"
   ```

## Debug Mode

### Enable Debug Logging

```bash
# Enable all debug output
export DEBUG=test-integration:*
npm test

# Specific categories
export DEBUG=test-integration:config,test-integration:performance
npm test
```

### Debug Configuration

```javascript
module.exports = {
  debug: {
    enabled: true,
    categories: ['config', 'execution', 'reporting'],
    outputFile: 'debug.log'
  }
};
```

### Verbose Output

```bash
# Maximum verbosity
npm test -- --verbose --debug
```

## Getting Help

### Diagnostic Information

Run this command to collect diagnostic information:

```bash
npx test-integration doctor --output diagnosis.json
```

### Support Channels

1. **GitHub Issues**: Report bugs and feature requests
2. **Discussions**: Ask questions and share solutions
3. **Documentation**: Check the latest documentation
4. **Stack Overflow**: Tag questions with `test-framework-integrations`

### Issue Template

When reporting issues, include:

```markdown
## Environment
- Node.js version: `node --version`
- npm version: `npm --version`
- Package version: `npm list test-framework-integrations`
- Operating System:
- Framework: jest/mocha/pytest/playwright/vitest

## Configuration
```javascript
// Your test-integration.config.js
```

## Steps to Reproduce
1.
2.
3.

## Expected Behavior

## Actual Behavior

## Error Messages
```
Error log here
```

## Additional Context
```

This comprehensive troubleshooting guide should help users quickly identify and resolve common issues with the Test Framework Integrations system.