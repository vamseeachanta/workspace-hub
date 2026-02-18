# Installation Guide

Complete installation instructions for Test Framework Integrations across different environments and platforms.

## 📋 System Requirements

### Minimum Requirements
- **Node.js**: 14.0.0 or higher
- **npm**: 6.14.0 or higher (comes with Node.js)
- **Memory**: 2GB RAM minimum, 4GB recommended
- **Storage**: 100MB free space

### Supported Platforms
- **Operating Systems**: Windows 10+, macOS 10.15+, Linux (Ubuntu 18.04+, CentOS 7+)
- **Architectures**: x64, ARM64 (Apple Silicon)
- **Container Platforms**: Docker, Podman, Kubernetes

### Supported Testing Frameworks
- **Jest**: 27.0.0 or higher
- **Mocha**: 9.0.0 or higher
- **Vitest**: 0.20.0 or higher
- **Playwright**: 1.20.0 or higher
- **Pytest**: 6.0.0 or higher (with Node.js bridge)

## 🚀 Installation Methods

### Option 1: NPM (Recommended)

#### Local Installation (Project-specific)
```bash
# Install as development dependency
npm install --save-dev test-framework-integrations

# Install peer dependencies (choose your testing frameworks)
npm install --save-dev jest mocha vitest @playwright/test

# Install coverage tools (optional)
npm install --save-dev nyc c8 coverage
```

#### Verify Installation
```bash
# Check if installed correctly
npm list test-framework-integrations

# Run basic test
npx test-framework-integrations --version
```

### Option 2: Yarn

```bash
# Install with Yarn
yarn add --dev test-framework-integrations

# Install peer dependencies
yarn add --dev jest mocha vitest @playwright/test

# Install coverage tools
yarn add --dev nyc c8
```

### Option 3: Global Installation

```bash
# Install globally for CLI usage
npm install -g test-framework-integrations

# Verify global installation
test-framework-integrations --version
```

### Option 4: pnpm

```bash
# Install with pnpm
pnpm add --save-dev test-framework-integrations

# Install peer dependencies
pnpm add --save-dev jest mocha vitest @playwright/test
```

## 📦 Package Manager Configuration

### NPM Configuration

#### .npmrc (Project-level)
```ini
# .npmrc - Optional optimizations
registry=https://registry.npmjs.org/
save-exact=true
package-lock=true
optional=false
```

#### Package.json Scripts
```json
{
  "scripts": {
    "test": "test-framework-integrations",
    "test:coverage": "test-framework-integrations --coverage",
    "test:baseline": "test-framework-integrations --baseline ./baseline.json",
    "test:multi": "test-framework-integrations --all-frameworks",
    "test:performance": "test-framework-integrations --profiling"
  },
  "devDependencies": {
    "test-framework-integrations": "^1.0.0",
    "jest": "^29.5.0",
    "mocha": "^10.2.0",
    "vitest": "^0.30.0",
    "@playwright/test": "^1.32.0"
  }
}
```

### Yarn Configuration

#### .yarnrc.yml (Yarn v2+)
```yaml
# .yarnrc.yml
nodeLinker: node-modules
enableGlobalCache: true
compressionLevel: mixed
```

#### yarn.lock Handling
```bash
# Ensure consistent installations
yarn install --frozen-lockfile

# Update dependencies
yarn upgrade test-framework-integrations
```

## 🐳 Docker Installation

### Dockerfile Example

```dockerfile
# Dockerfile
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    python3 \
    make \
    g++ \
    git

# Copy package files
COPY package*.json ./

# Install Node.js dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Install test dependencies
RUN npm install --save-dev test-framework-integrations

# Copy application code
COPY . .

# Create test script
RUN echo '#!/bin/sh\nnode -e "require(\"test-framework-integrations\").run()"' > /usr/local/bin/test-integration && \
    chmod +x /usr/local/bin/test-integration

# Default command
CMD ["test-integration"]
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  test-runner:
    build: .
    volumes:
      - ./src:/app/src:ro
      - ./tests:/app/tests:ro
      - ./reports:/app/reports
    environment:
      - NODE_ENV=test
      - CI=true
    command: npm run test:integration

  test-with-coverage:
    extends: test-runner
    command: npm run test:coverage
    volumes:
      - ./coverage:/app/coverage

  playwright-tests:
    image: mcr.microsoft.com/playwright:v1.32.0-focal
    working_dir: /app
    volumes:
      - .:/app
    command: npm run test:e2e
```

### Running in Docker

```bash
# Build image
docker build -t my-app-tests .

# Run tests
docker run --rm -v $(pwd)/reports:/app/reports my-app-tests

# Run with coverage
docker run --rm -v $(pwd)/coverage:/app/coverage my-app-tests npm run test:coverage

# Interactive mode
docker run -it --rm -v $(pwd):/app my-app-tests sh
```

## ☸️ Kubernetes Deployment

### Job Configuration

```yaml
# k8s-test-job.yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: test-framework-integration
spec:
  template:
    spec:
      containers:
      - name: test-runner
        image: my-app-tests:latest
        command: ["npm", "run", "test:integration"]
        resources:
          requests:
            memory: "1Gi"
            cpu: "500m"
          limits:
            memory: "2Gi"
            cpu: "1000m"
        env:
        - name: NODE_ENV
          value: "test"
        - name: CI
          value: "true"
        volumeMounts:
        - name: test-results
          mountPath: /app/reports
      volumes:
      - name: test-results
        persistentVolumeClaim:
          claimName: test-results-pvc
      restartPolicy: Never
  backoffLimit: 3
```

### Deploy to Kubernetes

```bash
# Apply job
kubectl apply -f k8s-test-job.yaml

# Monitor job
kubectl get jobs -w

# Get logs
kubectl logs job/test-framework-integration

# Get results
kubectl cp test-framework-integration-xxx:/app/reports ./reports
```

## 🔧 Framework-Specific Setup

### Jest Setup

```bash
# Install Jest dependencies
npm install --save-dev jest @types/jest jest-environment-node

# Optional: Coverage and reporting
npm install --save-dev @jest/reporters jest-html-reporters
```

#### jest.config.js
```javascript
module.exports = {
  testEnvironment: 'node',
  collectCoverageFrom: [
    'src/**/*.{js,ts}',
    '!src/**/*.d.ts',
  ],
  coverageDirectory: 'coverage',
  coverageReporters: ['text', 'lcov', 'html'],
  testMatch: [
    '**/__tests__/**/*.(js|ts)',
    '**/*.(test|spec).(js|ts)'
  ],
  setupFilesAfterEnv: ['<rootDir>/test-framework-integration.setup.js']
};
```

### Mocha Setup

```bash
# Install Mocha dependencies
npm install --save-dev mocha chai nyc

# Optional: Reporters
npm install --save-dev mocha-multi-reporters mochawesome
```

#### .mocharc.json
```json
{
  "require": ["test-framework-integration/mocha-setup"],
  "reporter": "spec",
  "timeout": 30000,
  "recursive": true,
  "spec": "test/**/*.test.js"
}
```

### Playwright Setup

```bash
# Install Playwright
npm install --save-dev @playwright/test

# Install browsers
npx playwright install
```

#### playwright.config.js
```javascript
module.exports = {
  testDir: './tests',
  timeout: 30000,
  fullyParallel: true,
  reporter: [
    ['html'],
    ['test-framework-integrations/playwright-reporter']
  ],
  use: {
    trace: 'on-first-retry',
    screenshot: 'only-on-failure'
  },
  projects: [
    { name: 'chromium', use: { ...devices['Desktop Chrome'] } },
    { name: 'firefox', use: { ...devices['Desktop Firefox'] } },
    { name: 'webkit', use: { ...devices['Desktop Safari'] } }
  ]
};
```

### Vitest Setup

```bash
# Install Vitest
npm install --save-dev vitest @vitest/ui

# Optional: Coverage
npm install --save-dev @vitest/coverage-c8
```

#### vitest.config.js
```javascript
import { defineConfig } from 'vitest/config';

export default defineConfig({
  test: {
    globals: true,
    environment: 'node',
    coverage: {
      reporter: ['text', 'json', 'html'],
      exclude: ['node_modules/', 'test/']
    },
    setupFiles: ['./test-framework-integration.setup.js']
  }
});
```

### Python/Pytest Setup

```bash
# Install Python dependencies
pip install pytest pytest-json-report pytest-cov

# Install Node.js bridge
npm install --save-dev pytest-node-bridge
```

#### pytest.ini
```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    --json-report
    --json-report-file=.test-results/pytest-report.json
    --cov=src
    --cov-report=html
    --cov-report=json
```

## 🔒 Security Configuration

### Dependency Security

```bash
# Audit dependencies
npm audit

# Fix vulnerabilities
npm audit fix

# Check for outdated packages
npm outdated
```

### Environment Variables

```bash
# .env.test
NODE_ENV=test
TEST_TIMEOUT=30000
COVERAGE_THRESHOLD=80
BASELINE_DIR=./.test-baselines
REPORTS_DIR=./reports

# Security: Never commit sensitive data
TEST_API_KEY=your-test-api-key
TEST_DATABASE_URL=postgresql://test:test@localhost:5432/testdb
```

### Security Best Practices

```javascript
// test-security.config.js
module.exports = {
  // Restrict file access
  allowedPaths: ['./src', './tests', './reports'],

  // Disable dangerous features in test environment
  disableEval: true,
  disableRequire: ['fs', 'child_process'],

  // Network restrictions
  allowNetworkAccess: false,
  allowedHosts: ['localhost', '127.0.0.1'],

  // Timeout limits
  maxTestDuration: 300000, // 5 minutes
  maxMemoryUsage: '2GB'
};
```

## 🚨 Troubleshooting Installation

### Common Issues

#### Permission Errors
```bash
# Fix npm permissions (Unix/Linux/macOS)
sudo chown -R $(whoami) ~/.npm

# Alternative: Use npx for global packages
npx test-framework-integrations --version
```

#### Node.js Version Issues
```bash
# Check Node.js version
node --version

# Update Node.js (using nvm)
nvm install node
nvm use node

# Or download from nodejs.org
```

#### Missing Dependencies
```bash
# Install all peer dependencies
npm install --save-dev $(npm info test-framework-integrations peerDependencies --json | jq -r 'keys[]')

# Check missing dependencies
npm list --depth=0
```

#### Platform-Specific Issues

**Windows:**
```cmd
# Install build tools
npm install --global windows-build-tools

# Or use Visual Studio Build Tools
npm config set msvs_version 2019
```

**macOS:**
```bash
# Install Xcode command line tools
xcode-select --install

# Install using Homebrew
brew install node
```

**Linux:**
```bash
# Ubuntu/Debian
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# CentOS/RHEL
curl -sL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install nodejs npm
```

### Verification Commands

```bash
# Verify installation
node --version
npm --version
npx test-framework-integrations --version

# Test basic functionality
npx test-framework-integrations --help

# Run diagnostics
npx test-framework-integrations --doctor
```

## 📊 Performance Optimization

### Installation Optimization

```bash
# Use CI optimizations
npm ci --only=production

# Reduce package size
npm install --no-optional --no-audit --no-fund

# Cache dependencies
npm config set cache ~/.npm-cache
```

### Memory Management

```javascript
// package.json
{
  "scripts": {
    "test": "node --max-old-space-size=4096 node_modules/.bin/test-framework-integrations"
  }
}
```

## 📝 Post-Installation Setup

### Create Configuration File

```javascript
// test-integration.config.js
module.exports = {
  rootDir: __dirname,
  frameworks: {
    preferred: 'jest',
    fallback: ['vitest', 'mocha']
  },
  coverage: {
    enabled: true,
    threshold: {
      statements: 80,
      branches: 70,
      functions: 80,
      lines: 80
    }
  },
  profiling: {
    enabled: true,
    memoryInterval: 100,
    detectLeaks: true
  },
  reporters: ['console', 'json'],
  baseline: {
    enabled: true,
    directory: './.test-baselines'
  }
};
```

### Initialize Project

```bash
# Generate initial configuration
npx test-framework-integrations --init

# Create baseline
npx test-framework-integrations --create-baseline

# Verify setup
npx test-framework-integrations --verify
```

## 🎉 Next Steps

1. **[Quick Start Guide](./QUICK_START.md)**: Get up and running immediately
2. **[Configuration Reference](./configuration/)**: Customize your setup
3. **[Integration Guides](./guides/)**: Framework-specific configuration
4. **[API Documentation](./api/)**: Programmatic usage

## 🆘 Getting Help

- **Documentation**: [Full Documentation](./README.md)
- **Issues**: [GitHub Issues](https://github.com/your-org/test-framework-integrations/issues)
- **Community**: [Discussions](https://github.com/your-org/test-framework-integrations/discussions)
- **Support**: [Support Guidelines](./SUPPORT.md)