# Environment Variables Reference

## Overview

The Test Framework Integrations system supports configuration through environment variables, allowing you to override settings without modifying configuration files. This is particularly useful for CI/CD environments and different deployment stages.

## Variable Precedence

Environment variables take precedence over configuration files in the following order:
1. Command-line arguments (highest priority)
2. Environment variables
3. Configuration files
4. Default values (lowest priority)

## Core Variables

### Framework Configuration

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `TEST_FRAMEWORK` | string | Override framework type | auto-detect | `jest`, `mocha`, `pytest` |
| `TEST_CONFIG_FILE` | string | Path to framework config | auto-detect | `jest.config.js` |
| `TEST_COMMAND` | string | Custom test command | framework default | `npm run test:unit` |
| `TEST_DIR` | string | Test directory | `tests` | `src`, `__tests__` |
| `TEST_PATTERN` | string | Test file pattern | `**/*.test.js` | `**/*.spec.ts` |

### Execution Control

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `TEST_TIMEOUT` | integer | Test timeout in ms | 30000 | 60000 |
| `TEST_RETRIES` | integer | Number of retries | 0 | 3 |
| `TEST_BAIL` | boolean | Stop on first failure | false | true |
| `TEST_VERBOSE` | boolean | Verbose output | false | true |
| `TEST_WATCH` | boolean | Enable watch mode | false | true |
| `TEST_SILENT` | boolean | Silent mode | false | true |
| `PARALLEL_WORKERS` | integer | Number of workers | CPU cores | 4 |
| `MAX_WORKERS` | integer | Alias for PARALLEL_WORKERS | CPU cores | 8 |

### Coverage Settings

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `COVERAGE_ENABLED` | boolean | Enable coverage | false | true |
| `COVERAGE_THRESHOLD` | integer | Coverage percentage | 80 | 85 |
| `COVERAGE_DIR` | string | Coverage output dir | `coverage` | `reports/coverage` |
| `COVERAGE_REPORTERS` | string | Coverage reporters | `html,json` | `html,lcov,text` |

### Baseline Configuration

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `BASELINE_ENABLED` | boolean | Enable baseline tracking | false | true |
| `BASELINE_DIR` | string | Baseline storage directory | `baselines` | `.baselines` |
| `BASELINE_AUTO_SAVE` | boolean | Auto-save baselines | false | true |
| `BASELINE_THRESHOLD` | float | Change detection threshold | 0.05 | 0.1 |
| `BASELINE_COMPRESSION` | string | Compression method | `gzip` | `brotli` |

### Performance Monitoring

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `PERFORMANCE_ENABLED` | boolean | Enable performance monitoring | false | true |
| `PERF_TEST_DURATION_LIMIT` | integer | Max test duration (ms) | 5000 | 10000 |
| `PERF_MEMORY_LIMIT` | integer | Max memory usage (bytes) | 268435456 | 536870912 |
| `PERF_CPU_LIMIT` | integer | Max CPU usage (%) | 80 | 90 |
| `PERF_PROFILING` | boolean | Enable profiling | false | true |

### Output and Reporting

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `OUTPUT_DIR` | string | Output directory | `test-results` | `reports` |
| `OUTPUT_FORMAT` | string | Report formats | `console` | `json,html,junit` |
| `REPORT_FILENAME` | string | Base report filename | `results` | `test-report` |
| `INCLUDE_SKIPPED` | boolean | Include skipped tests | true | false |
| `REPORT_TIMESTAMP` | boolean | Add timestamp | true | false |

### CI/CD Integration

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `CI` | boolean | CI environment flag | false | true |
| `CI_PROVIDER` | string | CI provider name | auto-detect | `github`, `gitlab` |
| `BUILD_NUMBER` | string | Build number | - | `123` |
| `BRANCH_NAME` | string | Git branch name | auto-detect | `main`, `feature/xyz` |
| `COMMIT_SHA` | string | Git commit SHA | auto-detect | `abc123...` |
| `PR_NUMBER` | string | Pull request number | - | `456` |

### Integration Services

| Variable | Type | Description | Default | Example |
|----------|------|-------------|---------|---------|
| `CODECOV_TOKEN` | string | Codecov upload token | - | `xxx-yyy-zzz` |
| `SONAR_TOKEN` | string | SonarQube token | - | `sqp_xxx` |
| `SLACK_WEBHOOK` | string | Slack webhook URL | - | `https://hooks.slack.com/...` |
| `DATADOG_API_KEY` | string | Datadog API key | - | `xxx123` |

## Environment-Specific Configurations

### Development Environment

```bash
# .env.development
TEST_FRAMEWORK=jest
TEST_WATCH=true
TEST_VERBOSE=true
COVERAGE_ENABLED=true
BASELINE_ENABLED=true
BASELINE_AUTO_SAVE=true
PERFORMANCE_ENABLED=false
OUTPUT_FORMAT=console,html
```

### Testing Environment

```bash
# .env.test
TEST_FRAMEWORK=jest
TEST_TIMEOUT=10000
TEST_RETRIES=1
COVERAGE_ENABLED=true
COVERAGE_THRESHOLD=70
BASELINE_ENABLED=true
PERFORMANCE_ENABLED=true
OUTPUT_FORMAT=json,html
```

### CI Environment

```bash
# .env.ci
CI=true
TEST_FRAMEWORK=jest
TEST_TIMEOUT=30000
TEST_RETRIES=2
TEST_BAIL=true
COVERAGE_ENABLED=true
COVERAGE_THRESHOLD=80
BASELINE_ENABLED=true
BASELINE_AUTO_SAVE=false
PERFORMANCE_ENABLED=true
PERF_TEST_DURATION_LIMIT=5000
OUTPUT_FORMAT=json,junit
PARALLEL_WORKERS=4
```

### Production Environment

```bash
# .env.production
CI=true
TEST_FRAMEWORK=jest
TEST_TIMEOUT=60000
TEST_RETRIES=3
TEST_BAIL=true
COVERAGE_ENABLED=true
COVERAGE_THRESHOLD=85
BASELINE_ENABLED=true
PERFORMANCE_ENABLED=true
OUTPUT_FORMAT=json,junit,html
PARALLEL_WORKERS=8
CODECOV_TOKEN=${CODECOV_TOKEN}
SLACK_WEBHOOK=${SLACK_WEBHOOK}
```

## Dynamic Environment Variables

### Git Integration

These variables are automatically detected from Git when available:

```bash
# Auto-detected Git variables
GIT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
GIT_COMMIT=$(git rev-parse HEAD)
GIT_AUTHOR=$(git log -1 --pretty=format:'%an')
GIT_MESSAGE=$(git log -1 --pretty=format:'%s')
```

### CI Provider Detection

Variables automatically set based on CI provider:

#### GitHub Actions

```bash
CI=true
CI_PROVIDER=github
BRANCH_NAME=${GITHUB_REF_NAME}
COMMIT_SHA=${GITHUB_SHA}
PR_NUMBER=${GITHUB_EVENT_PULL_REQUEST_NUMBER}
BUILD_NUMBER=${GITHUB_RUN_NUMBER}
```

#### GitLab CI

```bash
CI=true
CI_PROVIDER=gitlab
BRANCH_NAME=${CI_COMMIT_REF_NAME}
COMMIT_SHA=${CI_COMMIT_SHA}
PR_NUMBER=${CI_MERGE_REQUEST_IID}
BUILD_NUMBER=${CI_PIPELINE_ID}
```

#### Jenkins

```bash
CI=true
CI_PROVIDER=jenkins
BRANCH_NAME=${GIT_BRANCH}
COMMIT_SHA=${GIT_COMMIT}
BUILD_NUMBER=${BUILD_NUMBER}
```

## Variable Validation

### Type Conversion

Environment variables are automatically converted to appropriate types:

```javascript
// String to boolean
TEST_VERBOSE=true     // → true
TEST_VERBOSE=false    // → false
TEST_VERBOSE=1        // → true
TEST_VERBOSE=0        // → false

// String to number
TEST_TIMEOUT=30000    // → 30000
PARALLEL_WORKERS=4    // → 4

// String to array
OUTPUT_FORMAT=json,html,junit  // → ['json', 'html', 'junit']
```

### Validation Rules

Invalid values will result in warnings and fallback to defaults:

```bash
# Invalid values
TEST_TIMEOUT=invalid  # Warning: Invalid timeout, using default 30000
PARALLEL_WORKERS=-1   # Warning: Invalid worker count, using default
COVERAGE_THRESHOLD=150 # Warning: Coverage threshold > 100%, using 100%
```

## Environment Files

### .env File Support

The system automatically loads `.env` files in the following order:

1. `.env.local` (highest priority, should be in .gitignore)
2. `.env.${NODE_ENV}` (e.g., `.env.test`, `.env.development`)
3. `.env`

Example `.env` file:

```bash
# Test Framework Integrations Configuration
TEST_FRAMEWORK=jest
TEST_TIMEOUT=30000
COVERAGE_ENABLED=true
BASELINE_ENABLED=true
OUTPUT_DIR=test-results

# Service integrations (use in .env.local)
CODECOV_TOKEN=your-codecov-token
SLACK_WEBHOOK=https://hooks.slack.com/your-webhook
```

### Docker Environment

For Docker deployments:

```dockerfile
# Dockerfile
FROM node:18-alpine

# Set environment variables
ENV CI=true
ENV TEST_FRAMEWORK=jest
ENV COVERAGE_ENABLED=true
ENV OUTPUT_FORMAT=json,junit

# Copy and run tests
COPY . .
RUN npm test
```

Or use docker-compose:

```yaml
# docker-compose.test.yml
version: '3.8'
services:
  test:
    build: .
    environment:
      - CI=true
      - TEST_FRAMEWORK=jest
      - COVERAGE_ENABLED=true
      - BASELINE_ENABLED=true
      - OUTPUT_FORMAT=json,junit
    volumes:
      - ./test-results:/app/test-results
```

## Security Considerations

### Sensitive Variables

Never commit sensitive variables to version control:

```bash
# .env.local (add to .gitignore)
CODECOV_TOKEN=sensitive-token
SLACK_WEBHOOK=https://hooks.slack.com/sensitive-webhook
SONAR_TOKEN=sensitive-sonar-token
DATADOG_API_KEY=sensitive-datadog-key
```

### Variable Masking

In CI environments, mask sensitive variables:

```yaml
# GitHub Actions
- name: Run tests
  env:
    CODECOV_TOKEN: ${{ secrets.CODECOV_TOKEN }}
    SLACK_WEBHOOK: ${{ secrets.SLACK_WEBHOOK }}
  run: npm test
```

## Debugging Environment Configuration

### Debug Mode

Enable debug output to see all environment variables:

```bash
DEBUG=test-integration:config npm test
```

### Configuration Dump

Use the built-in command to see resolved configuration:

```bash
npx test-integration config --show-env
```

This will output:

```json
{
  "resolved": {
    "framework": {
      "type": "jest",
      "source": "environment:TEST_FRAMEWORK"
    },
    "execution": {
      "timeout": 30000,
      "source": "environment:TEST_TIMEOUT"
    }
  },
  "environment": {
    "TEST_FRAMEWORK": "jest",
    "TEST_TIMEOUT": "30000",
    "COVERAGE_ENABLED": "true"
  }
}
```

## Best Practices

### Environment Organization

1. **Use environment-specific files**: `.env.development`, `.env.test`, `.env.production`
2. **Keep sensitive data separate**: Use `.env.local` for secrets
3. **Document required variables**: Include `.env.example` with dummy values
4. **Validate in CI**: Check for required environment variables

### Naming Conventions

1. **Use descriptive names**: `TEST_TIMEOUT` instead of `TIMEOUT`
2. **Follow patterns**: `SERVICE_ENABLED`, `SERVICE_TOKEN`, `SERVICE_URL`
3. **Group related variables**: `PERF_*` for performance settings
4. **Use boolean conventions**: `true`/`false` or `1`/`0`

### Example .env.example

```bash
# Test Framework Integrations - Environment Variables Example
# Copy to .env.local and update with actual values

# Framework Configuration
TEST_FRAMEWORK=jest
TEST_TIMEOUT=30000
TEST_RETRIES=2

# Coverage Settings
COVERAGE_ENABLED=true
COVERAGE_THRESHOLD=80

# Baseline Configuration
BASELINE_ENABLED=true
BASELINE_AUTO_SAVE=true

# Performance Monitoring
PERFORMANCE_ENABLED=true
PERF_TEST_DURATION_LIMIT=5000

# Output Configuration
OUTPUT_DIR=test-results
OUTPUT_FORMAT=console,html

# CI/CD Integration
CI=false
CI_PROVIDER=github

# Service Integrations (replace with actual values)
CODECOV_TOKEN=your-codecov-token-here
SLACK_WEBHOOK=https://hooks.slack.com/your-webhook-here
SONAR_TOKEN=your-sonar-token-here
```

This comprehensive environment variables reference provides all the information needed to configure the Test Framework Integrations system using environment variables across different environments and deployment scenarios.