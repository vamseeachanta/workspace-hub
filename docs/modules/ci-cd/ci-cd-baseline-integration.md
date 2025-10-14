# CI/CD Baseline Testing Integration

A comprehensive CI/CD integration system for baseline testing with multi-platform support, advanced error handling, and real-time notifications.

## 🚀 Features

### ✅ GitHub Actions Workflows
- **Baseline Check Workflow**: Automated testing on push/PR with matrix builds
- **Scheduled Audit Workflow**: Daily and weekly comprehensive baseline audits
- **PR Comment Integration**: Automatic result comments with detailed metrics
- **Baseline Update Workflow**: Automatic baseline file updates on successful tests

### 🪝 Pre-commit Hooks
- **Local Validation**: Fast baseline checks before commits
- **Auto-fix Capabilities**: Automatic code formatting and issue resolution
- **Quick Feedback Loop**: Immediate feedback for developers
- **Selective Testing**: Smart test selection based on changed files

### 🐳 Docker Configuration
- **Multi-stage Builds**: Optimized container images with caching
- **Security Hardened**: Non-root user execution and minimal attack surface
- **Monitoring Ready**: Built-in Prometheus metrics and health checks
- **Service Orchestration**: Complete testing environment with Redis and PostgreSQL

### 🔄 Multi-Platform CI/CD Support
- **Jenkins**: Enterprise-grade pipeline with advanced retry logic
- **GitLab CI**: Comprehensive pipeline with parallel execution and caching
- **CircleCI**: High-performance workflows with optimal resource usage
- **Azure DevOps**: Enterprise integration with advanced reporting

### 🔔 Notification System
- **Multi-channel Support**: Slack, Discord, Microsoft Teams, Email
- **Smart Notifications**: Context-aware messaging based on test results
- **Retry Logic**: Robust delivery with exponential backoff
- **Template System**: Customizable message formats and branding

### 🛡️ Error Handling & Resilience
- **Circuit Breaker Pattern**: Automatic failure isolation and recovery
- **Exponential Backoff**: Smart retry strategies for different error types
- **Comprehensive Logging**: Structured logging with multiple output formats
- **Metrics Collection**: Real-time performance and error metrics

## 📁 Directory Structure

```
.
├── .github/workflows/
│   ├── baseline-check.yml          # Main CI workflow
│   └── baseline-audit.yml          # Scheduled audit workflow
├── .pre-commit-config.yaml         # Pre-commit hooks configuration
├── docker/
│   ├── Dockerfile.baseline-test    # Testing environment
│   ├── docker-compose.baseline.yml # Complete stack
│   └── monitoring/                 # Prometheus & Grafana configs
├── scripts/
│   ├── hooks/                      # Pre-commit hook scripts
│   │   ├── baseline-validation.sh
│   │   ├── baseline-quick-check.sh
│   │   └── baseline-auto-fix.sh
│   ├── ci/                         # CI/CD platform configurations
│   │   ├── jenkins/Jenkinsfile
│   │   ├── gitlab/.gitlab-ci.yml
│   │   ├── circleci/config.yml
│   │   └── azure/azure-pipelines.yml
│   ├── notifications/              # Notification system
│   │   ├── webhook-manager.js
│   │   └── email-notifier.py
│   └── utils/                      # Utility scripts
│       ├── error-handler.js
│       ├── logger.js
│       └── config-validator.js
└── docs/
    └── ci-cd-baseline-integration.md  # This documentation
```

## 🚀 Quick Start

### 1. Initial Setup

```bash
# Install pre-commit hooks
npm install -g pre-commit
pre-commit install

# Validate configuration
node scripts/utils/config-validator.js

# Test Docker environment
docker-compose -f docker/docker-compose.baseline.yml up --build
```

### 2. Environment Variables

Create a `.env` file or set the following environment variables:

```bash
# Required
NODE_ENV=test
BASELINE_LOG_LEVEL=INFO
BASELINE_THRESHOLD=85

# Optional - Notifications
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/...
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
SMTP_HOST=smtp.gmail.com
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

# Optional - CI/CD
GITHUB_TOKEN=ghp_...
DOCKER_REGISTRY=your-registry.com
```

### 3. Package.json Scripts

Add these scripts to your `package.json`:

```json
{
  "scripts": {
    "test:baseline:unit": "jest --config=jest.baseline.config.js --testPathPattern=unit",
    "test:baseline:integration": "jest --config=jest.baseline.config.js --testPathPattern=integration",
    "test:baseline:performance": "jest --config=jest.baseline.config.js --testPathPattern=performance",
    "test:baseline:security": "jest --config=jest.baseline.config.js --testPathPattern=security",
    "test:baseline:all": "npm run test:baseline:unit && npm run test:baseline:integration",
    "lint:check": "eslint . --ext .js,.ts,.jsx,.tsx",
    "lint:fix": "eslint . --ext .js,.ts,.jsx,.tsx --fix",
    "health-check": "node scripts/utils/health-check.js"
  }
}
```

## 🔧 Configuration

### GitHub Actions Configuration

The workflows automatically trigger on:
- **Push to main/develop branches**
- **Pull requests to main/develop**
- **Manual workflow dispatch**
- **Scheduled runs** (daily at 2 AM, weekly on Monday at 6 AM)

Key environment variables in workflows:
```yaml
env:
  NODE_VERSION: '18'
  PYTHON_VERSION: '3.11'
  BASELINE_THRESHOLD: '85'
  MAX_RETRIES: '3'
```

### Pre-commit Hook Configuration

Configure in `.pre-commit-config.yaml`:
```yaml
repos:
  - repo: local
    hooks:
      - id: baseline-validation
        name: Baseline Validation
        entry: scripts/hooks/baseline-validation.sh
        language: script
        stages: [commit, push]
        files: \.(js|ts|jsx|tsx|py|json|md)$
```

### Docker Environment

The Docker setup includes:
- **Multi-stage builds** for optimization
- **Security scanning** with non-root users
- **Health checks** for service monitoring
- **Volume caching** for performance

### Notification Configuration

Create `webhook-config.json`:
```json
{
  "webhooks": [
    {
      "name": "team-slack",
      "type": "slack",
      "url": "https://hooks.slack.com/services/..."
    },
    {
      "name": "alerts-discord",
      "type": "discord",
      "url": "https://discord.com/api/webhooks/..."
    }
  ],
  "maxRetries": 3,
  "timeout": 10000
}
```

## 📊 Monitoring & Metrics

### Built-in Metrics
- **Test execution time and success rates**
- **Error frequency and categorization**
- **Circuit breaker status and recovery**
- **Resource usage and performance**

### Dashboard Access
- **Grafana Dashboard**: `http://localhost:3001` (when using Docker Compose)
- **Prometheus Metrics**: `http://localhost:9090`
- **Log Aggregation**: Loki at `http://localhost:3100`

### Custom Metrics

Add custom metrics in your tests:
```javascript
const { logger } = require('./scripts/utils/logger');

logger.logPerformance('test_execution', {
  duration: 1250,
  score: 95,
  testCount: 42
});
```

## 🔍 Troubleshooting

### Common Issues

1. **Pre-commit hooks failing**
   ```bash
   # Check hook permissions
   ls -la scripts/hooks/
   chmod +x scripts/hooks/*.sh

   # Test hooks individually
   scripts/hooks/baseline-quick-check.sh file.js
   ```

2. **Docker build failures**
   ```bash
   # Check Docker daemon
   docker info

   # Rebuild with no cache
   docker-compose -f docker/docker-compose.baseline.yml build --no-cache
   ```

3. **Notification delivery issues**
   ```bash
   # Test webhook configuration
   node scripts/notifications/webhook-manager.js test-webhook <url> --type slack

   # Test email configuration
   python scripts/notifications/email-notifier.py test --config email-config.json
   ```

4. **CI/CD pipeline failures**
   ```bash
   # Validate configuration
   node scripts/utils/config-validator.js

   # Check error logs
   cat .baseline-cache/logs/error-handler.log
   ```

### Debug Mode

Enable debug logging:
```bash
export BASELINE_LOG_LEVEL=DEBUG
export BASELINE_DEBUG=true
```

### Performance Issues

1. **Slow test execution**: Enable parallel testing
2. **High memory usage**: Reduce test concurrency
3. **Network timeouts**: Increase timeout values
4. **Cache misses**: Verify cache key generation

## 🚀 Advanced Features

### Circuit Breaker Pattern

Automatic failure isolation:
```javascript
const { BaselineErrorHandler } = require('./scripts/utils/error-handler');
const handler = new BaselineErrorHandler();

// Automatic circuit breaking for failing operations
await handler.executeWithRetry(riskyOperation, 'api_call');
```

### Smart Retry Logic

Different strategies for different error types:
- **Network errors**: 5 retries with exponential backoff
- **Timeout errors**: 3 retries with fixed delay
- **Validation errors**: No retries (fail fast)
- **Test failures**: 2 retries with moderate delay

### Log Aggregation

Structured logging with multiple outputs:
```javascript
const { logger } = require('./scripts/utils/logger');

logger.info('Test completed', {
  testName: 'authentication',
  duration: 1250,
  score: 95
});
```

### Custom Error Classification

Extend error handling for specific needs:
```javascript
// Add custom error types
handler.errorStrategies['CUSTOM_ERROR'] = {
  retryable: true,
  maxRetries: 2,
  retryDelay: 5000,
  exponentialBackoff: false
};
```

## 📈 Performance Optimization

### Caching Strategy
- **Docker layer caching** for faster builds
- **npm/pip dependency caching** across runs
- **Test result caching** for unchanged code
- **Baseline artifact caching** for comparison

### Parallel Execution
- **Test matrix builds** in GitHub Actions
- **Parallel hook execution** in pre-commit
- **Service parallelization** in Docker Compose
- **Multi-agent builds** in Jenkins

### Resource Management
- **Memory limits** for containers
- **CPU constraints** for fair resource sharing
- **Timeout configurations** to prevent hanging
- **Cleanup procedures** for artifact management

## 🔐 Security Considerations

### Secrets Management
- Use **GitHub Secrets** for sensitive data
- **Environment variable validation** before use
- **Webhook URL verification** for authenticity
- **Docker secret mounting** for runtime secrets

### Access Control
- **Branch protection rules** for main branches
- **Required status checks** before merging
- **Reviewer requirements** for configuration changes
- **Audit logging** for all operations

### Container Security
- **Non-root user execution** in containers
- **Minimal base images** to reduce attack surface
- **Regular security scanning** of dependencies
- **Network isolation** between services

## 🤝 Contributing

### Adding New CI/CD Platform

1. Create platform-specific configuration in `scripts/ci/<platform>/`
2. Follow existing patterns for error handling and notifications
3. Add validation rules in `config-validator.js`
4. Update documentation with platform-specific instructions

### Extending Notification Channels

1. Add new notification method in `webhook-manager.js`
2. Create appropriate payload formatters
3. Add configuration validation
4. Test with real endpoints

### Custom Error Handlers

1. Extend `BaselineErrorHandler` class
2. Define error classification rules
3. Add retry strategies for new error types
4. Include comprehensive logging

## 📚 Additional Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Pre-commit Framework](https://pre-commit.com/)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Prometheus Monitoring](https://prometheus.io/docs/)
- [Circuit Breaker Pattern](https://martinfowler.com/bliki/CircuitBreaker.html)

## 📄 License

This CI/CD integration system is part of the baseline testing framework and follows the same licensing terms as the main project.

---

**🎉 Ready to deploy reliable, scalable baseline testing with comprehensive CI/CD integration!**