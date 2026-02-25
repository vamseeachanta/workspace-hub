# Testing Templates Implementation Guide

This guide provides step-by-step instructions for implementing the baseline testing standards in your projects.

## Quick Reference

| Project Type | Templates Needed | Setup Time |
|-------------|------------------|------------|
| **Python Only** | pytest.ini, .coveragerc, python-tests.yml | 15 mins |
| **Node.js Only** | jest.config.js, node-tests.yml | 10 mins |
| **Multi-language** | All templates + combined-tests.yml | 30 mins |
| **Existing Project** | Gradual migration approach | 1-2 hours |

## Implementation Scenarios

### Scenario 1: New Python Project

#### Step 1: Choose Configuration Approach

**Option A: pytest.ini + .coveragerc (Recommended for simplicity)**
```bash
# Copy templates
cp docs/testing-templates/pytest.ini.template pytest.ini
cp docs/testing-templates/coveragerc.template .coveragerc
cp docs/testing-templates/requirements-test.txt.template requirements-test.txt
```

**Option B: pyproject.toml (Recommended for modern projects)**
```bash
# Copy templates and merge into your pyproject.toml
cat docs/testing-templates/pyproject.toml.pytest.template >> pyproject.toml
cat docs/testing-templates/pyproject.toml.coverage.template >> pyproject.toml
cp docs/testing-templates/requirements-test.txt.template requirements-test.txt
```

#### Step 2: Create Test Structure
```bash
# Create test directory structure
mkdir -p tests/{unit,integration,fixtures}

# Copy test configuration
cp docs/testing-templates/conftest.py.template tests/conftest.py

# Create first test
cat > tests/unit/test_example.py << 'EOF'
import pytest

def test_example():
    """Example test to verify setup."""
    assert True

@pytest.mark.unit
def test_with_marker():
    """Test with unit marker."""
    assert 1 + 1 == 2
EOF
```

#### Step 3: Install Dependencies
```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install test dependencies
pip install -r requirements-test.txt

# Install your project in development mode
pip install -e .
```

#### Step 4: Verify Setup
```bash
# Run tests
pytest

# Check coverage
pytest --cov=src --cov-report=html

# View coverage report
open htmlcov/index.html  # On macOS
# Or navigate to htmlcov/index.html in your browser
```

#### Step 5: Setup CI/CD
```bash
# Copy GitHub Actions workflow
mkdir -p .github/workflows
cp docs/testing-templates/python-tests.yml.template .github/workflows/python-tests.yml

# Customize workflow (edit .github/workflows/python-tests.yml)
# - Update Python versions
# - Adjust paths if needed
# - Configure environment variables
```

### Scenario 2: New Node.js Project

#### Step 1: Choose Configuration Approach

**Option A: jest.config.js (Recommended for complex setups)**
```bash
# Copy templates
cp docs/testing-templates/jest.config.js.template jest.config.js
cp docs/testing-templates/jest.setup.js.template tests/setup.js
cp docs/testing-templates/babel.config.js.template babel.config.js
```

**Option B: package.json (Recommended for simple projects)**
```bash
# Merge Jest configuration from template into package.json
# Copy the "jest" section from package.json.jest.template
```

#### Step 2: Install Dependencies
```bash
# Install Jest and testing utilities
npm install --save-dev \
  jest \
  @testing-library/jest-dom \
  @testing-library/react \
  @testing-library/user-event \
  jest-environment-jsdom \
  babel-jest \
  @babel/preset-env \
  @babel/preset-react

# For TypeScript projects, also install:
# @types/jest ts-jest @babel/preset-typescript
```

#### Step 3: Update package.json Scripts
```json
{
  "scripts": {
    "test": "jest",
    "test:watch": "jest --watch",
    "test:coverage": "jest --coverage",
    "test:ci": "jest --ci --coverage --maxWorkers=2",
    "test:debug": "node --inspect-brk node_modules/.bin/jest --runInBand"
  }
}
```

#### Step 4: Create Test Structure
```bash
# Create test directories
mkdir -p tests/{unit,integration} src/__tests__

# Create first test
cat > src/__tests__/example.test.js << 'EOF'
describe('Example Test Suite', () => {
  test('should pass basic test', () => {
    expect(1 + 1).toBe(2);
  });

  test('should work with async operations', async () => {
    const result = await Promise.resolve('success');
    expect(result).toBe('success');
  });
});
EOF
```

#### Step 5: Verify Setup
```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage

# View coverage report
open coverage/lcov-report/index.html
```

#### Step 6: Setup CI/CD
```bash
# Copy GitHub Actions workflow
mkdir -p .github/workflows
cp docs/testing-templates/node-tests.yml.template .github/workflows/node-tests.yml
```

### Scenario 3: Multi-language Project

#### Step 1: Project Structure Setup
```bash
# Create multi-language directory structure
mkdir -p {backend,frontend,tests,shared}

# Backend (Python)
cd backend
cp ../docs/testing-templates/pytest.ini.template pytest.ini
cp ../docs/testing-templates/coveragerc.template .coveragerc
mkdir -p tests/{unit,integration}

# Frontend (Node.js)
cd ../frontend
cp ../docs/testing-templates/jest.config.js.template jest.config.js
mkdir -p tests/{unit,integration}

# Shared resources
cd ../shared
mkdir -p {fixtures,schemas,utils}

# Integration tests
cd ../tests
mkdir -p {api,e2e,system}
```

#### Step 2: Shared Test Infrastructure
```bash
# Copy Docker Compose for test services
cp docs/testing-templates/docker-compose.test.yml.template docker-compose.test.yml

# Create shared test configuration
mkdir -p tests/config
cat > tests/config/test-config.js << 'EOF'
export const testConfig = {
  api: {
    baseUrl: process.env.API_BASE_URL || 'http://localhost:8000',
    timeout: 10000
  },
  database: {
    postgres: {
      host: 'localhost',
      port: 5433,
      database: 'test_db'
    }
  }
};
EOF
```

#### Step 3: Setup Combined CI/CD
```bash
# Copy combined workflow
mkdir -p .github/workflows
cp docs/testing-templates/combined-tests.yml.template .github/workflows/combined-tests.yml

# Customize paths and configuration in the workflow file
```

#### Step 4: Create Test Scripts
```bash
# Create master test runner
mkdir -p scripts
cat > scripts/test-all.sh << 'EOF'
#!/bin/bash
set -e

echo "🚀 Starting multi-language test suite..."

# Start test services
docker-compose -f docker-compose.test.yml up -d
sleep 5

# Backend tests
if [ -d "backend" ]; then
    echo "Running backend tests..."
    cd backend
    pytest --cov=src --cov-report=xml:../coverage-backend.xml
    cd ..
fi

# Frontend tests
if [ -d "frontend" ]; then
    echo "Running frontend tests..."
    cd frontend
    npm test -- --coverage
    cd ..
fi

# Integration tests
echo "Running integration tests..."
cd tests
npm run test:integration

# Cleanup
docker-compose -f docker-compose.test.yml down

echo "✅ All tests completed!"
EOF

chmod +x scripts/test-all.sh
```

### Scenario 4: Migrating Existing Project

#### Step 1: Assessment
```bash
# Assess current testing setup
echo "Current test files:"
find . -name "*test*" -type f | head -20

echo "Current test dependencies:"
grep -E "(test|jest|pytest|mocha)" package.json requirements*.txt 2>/dev/null || echo "None found"

echo "Current coverage:"
# Look for existing coverage reports
ls -la coverage/ htmlcov/ .coverage coverage.xml 2>/dev/null || echo "No coverage reports found"
```

#### Step 2: Gradual Migration Plan

**Phase 1: Add Configuration (Week 1)**
```bash
# Add test configuration without breaking existing tests
cp docs/testing-templates/pytest.ini.template pytest.ini.new
cp docs/testing-templates/jest.config.js.template jest.config.js.new

# Review and merge with existing configuration
# Move .new files to actual filenames when ready
```

**Phase 2: Improve Test Structure (Week 2)**
```bash
# Organize existing tests
mkdir -p tests/{unit,integration,fixtures}

# Move existing tests to appropriate directories
# Update import paths as needed
```

**Phase 3: Add Coverage (Week 3)**
```bash
# Add coverage configuration
cp docs/testing-templates/coveragerc.template .coveragerc

# Install coverage tools
pip install coverage pytest-cov  # Python
npm install --save-dev jest      # Node.js (if not already installed)
```

**Phase 4: CI/CD Integration (Week 4)**
```bash
# Add GitHub Actions workflow
mkdir -p .github/workflows
cp docs/testing-templates/python-tests.yml.template .github/workflows/tests.yml

# Gradually enable features:
# 1. Start with basic test execution
# 2. Add coverage reporting
# 3. Add quality gates
# 4. Add advanced features
```

## Customization Guide

### Python Projects

#### Customize pytest.ini
```ini
# Example customizations
[tool:pytest]
# Change test discovery
testpaths = custom_tests src

# Add custom markers
markers =
    slow: marks tests as slow
    api: marks tests as API tests
    database: marks tests as database tests
    your_custom_marker: description

# Adjust coverage settings
addopts =
    --cov=your_package
    --cov-fail-under=85  # Increase threshold
    --strict-markers
```

#### Customize .coveragerc
```ini
# Example customizations
[run]
source = your_package  # Change source directory

omit =
    */your_package/settings/*
    */your_package/migrations/*
    your_custom_exclusions/*

[report]
# Custom exclusions
exclude_lines =
    pragma: no cover
    your_custom_pragma
```

### Node.js Projects

#### Customize jest.config.js
```javascript
// Example customizations
module.exports = {
  // Custom test environment
  testEnvironment: 'jsdom', // For React/DOM testing

  // Custom module mapping
  moduleNameMapping: {
    '^@components/(.*)$': '<rootDir>/src/components/$1',
    '^@utils/(.*)$': '<rootDir>/src/utils/$1',
    '^@/(.*)$': '<rootDir>/src/$1'
  },

  // Custom coverage thresholds
  coverageThreshold: {
    global: {
      branches: 85,
      functions: 85,
      lines: 85,
      statements: 85
    },
    './src/critical/': {
      branches: 95,
      functions: 95,
      lines: 95,
      statements: 95
    }
  },

  // Custom setup files
  setupFilesAfterEnv: [
    '<rootDir>/tests/setup.js',
    '<rootDir>/tests/custom-matchers.js'
  ]
};
```

### GitHub Actions

#### Customize CI/CD Workflows
```yaml
# Example customizations
name: Custom Tests

on:
  push:
    branches: [ main, develop, staging ]  # Add your branches
    paths:
      - 'src/**'
      - 'custom-path/**'  # Add your paths

env:
  # Custom environment variables
  CUSTOM_VAR: value
  API_BASE_URL: https://api.example.com

jobs:
  test:
    strategy:
      matrix:
        # Customize versions
        python-version: ['3.9', '3.10', '3.11']
        node-version: ['18.x', '20.x']
        os: [ubuntu-latest, windows-latest]  # Add/remove OS

    steps:
    # Custom dependency installation
    - name: Install system dependencies
      run: |
        sudo apt-get update
        sudo apt-get install -y your-dependencies

    # Custom test commands
    - name: Run custom tests
      run: |
        your-custom-test-command
        pytest custom-args
```

## Troubleshooting

### Common Issues and Solutions

#### Issue: Tests not discovered
```bash
# Python
pytest --collect-only  # See what tests are discovered
pytest -v tests/       # Run specific directory

# Node.js
jest --listTests       # See what tests are discovered
jest --testNamePattern="pattern"  # Run specific tests
```

#### Issue: Coverage not working
```bash
# Python
pytest --cov-report=html --cov-report=term-missing
# Check .coveragerc configuration

# Node.js
jest --coverage --verbose
# Check jest.config.js collectCoverageFrom
```

#### Issue: Tests timeout
```bash
# Python
pytest --timeout=60    # Increase timeout

# Node.js
jest --testTimeout=10000  # Increase timeout in jest.config.js
```

#### Issue: Import/path errors
```bash
# Python
pip install -e .      # Install project in development mode
# Check sys.path in tests

# Node.js
# Check moduleNameMapping in jest.config.js
# Verify babel configuration
```

### Performance Optimization

#### Speed up test execution
```bash
# Python
pytest -n auto        # Parallel execution (pytest-xdist)
pytest --lf           # Last failed tests only
pytest --ff           # Failed first

# Node.js
jest --maxWorkers=50%  # Parallel execution
jest --onlyChanged     # Only changed files
jest --watch           # Watch mode
```

#### Optimize CI/CD
```yaml
# Cache dependencies
- uses: actions/cache@v3
  with:
    path: ~/.cache/pip  # Python
    # path: ~/.npm      # Node.js
    key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}

# Run tests in parallel
strategy:
  matrix:
    test-group: [unit, integration, e2e]
```

## Best Practices Summary

### Development Workflow
1. **Write tests first** (TDD approach)
2. **Run tests frequently** (watch mode)
3. **Keep tests fast** (< 100ms for unit tests)
4. **Isolate tests** (no dependencies between tests)
5. **Use descriptive names** (test intent should be clear)

### Maintenance
1. **Review test coverage** regularly
2. **Update dependencies** monthly
3. **Remove obsolete tests** during refactoring
4. **Monitor test performance** (execution time)
5. **Keep test data fresh** (realistic fixtures)

### Team Collaboration
1. **Document test conventions** in team guidelines
2. **Review tests in code reviews**
3. **Share test utilities** across team
4. **Maintain consistent structure** across projects
5. **Communicate test failures** quickly

---

*For project-specific implementation help, refer to your project's testing documentation or reach out to the development team.*