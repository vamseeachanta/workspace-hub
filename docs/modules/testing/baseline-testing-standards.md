# Baseline Testing Standards

> Version: 1.0.0
> Last Updated: 2025-09-28
> Scope: Universal testing standards for all repository types

## Overview

This document establishes comprehensive baseline testing standards for all repository types within the Agent OS ecosystem. These standards ensure consistent quality, maintainability, and reliability across all projects.

## Core Testing Principles

### 1. Test-Driven Development (TDD)
- Write tests before implementation
- Follow Red-Green-Refactor cycle
- Maintain test-first mindset

### 2. Coverage Requirements
- **Minimum**: 80% code coverage for all projects
- **Target**: 90% code coverage for critical components
- **Quality over Quantity**: Focus on meaningful tests, not just coverage numbers

### 3. Test Organization
- Clear directory structure
- Consistent naming conventions
- Logical test grouping
- Fast test execution

### 4. CI/CD Integration
- Automated test execution
- Coverage reporting
- Quality gates
- Fast feedback loops

## Python Projects Baseline

### Configuration Files

#### Option 1: pytest.ini Configuration
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    --strict-markers
    --strict-config
    --verbose
    --cov=src
    --cov-report=term-missing
    --cov-report=html:htmlcov
    --cov-report=xml
    --cov-fail-under=80
markers =
    unit: Unit tests
    integration: Integration tests
    slow: Slow running tests
    api: API tests
```

#### Option 2: pyproject.toml Configuration
```toml
# pyproject.toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = [
    "--strict-markers",
    "--strict-config",
    "--verbose",
    "--cov=src",
    "--cov-report=term-missing",
    "--cov-report=html:htmlcov",
    "--cov-report=xml",
    "--cov-fail-under=80"
]
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow running tests",
    "api: API tests"
]
```

### Coverage Configuration

#### .coveragerc Configuration
```ini
# .coveragerc
[run]
source = src
omit =
    */tests/*
    */test_*
    */__pycache__/*
    */venv/*
    */env/*
    */migrations/*
    */settings/*
    */manage.py
    */wsgi.py
    */asgi.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    if self.debug:
    if settings.DEBUG
    raise AssertionError
    raise NotImplementedError
    if 0:
    if __name__ == .__main__.:
    class .*\bProtocol\):
    @(abc\.)?abstractmethod

[html]
directory = htmlcov
```

#### Alternative: pyproject.toml Coverage Config
```toml
# pyproject.toml
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*",
    "*/__pycache__/*",
    "*/venv/*",
    "*/env/*",
    "*/migrations/*"
]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "if self.debug:",
    "if settings.DEBUG",
    "raise AssertionError",
    "raise NotImplementedError",
    "if 0:",
    "if __name__ == .__main__.:",
    "class .*\\bProtocol\\):",
    "@(abc\\.)?abstractmethod"
]

[tool.coverage.html]
directory = "htmlcov"
```

### Directory Structure
```
project/
├── src/
│   └── module/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   ├── unit/
│   │   ├── __init__.py
│   │   └── test_main.py
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_api.py
│   └── fixtures/
│       ├── __init__.py
│       └── conftest.py
├── pytest.ini (or pyproject.toml)
├── .coveragerc (or coverage in pyproject.toml)
└── requirements-test.txt
```

### Test Dependencies
```txt
# requirements-test.txt
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-asyncio>=0.21.0
pytest-xdist>=3.2.0
coverage[toml]>=7.0.0
```

## JavaScript/Node.js Projects Baseline

### Jest Configuration

#### jest.config.js
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'node',
  testMatch: [
    '**/__tests__/**/*.(js|jsx|ts|tsx)',
    '**/*.(test|spec).(js|jsx|ts|tsx)'
  ],
  testPathIgnorePatterns: [
    '/node_modules/',
    '/dist/',
    '/build/',
    '/coverage/'
  ],
  collectCoverageFrom: [
    'src/**/*.(js|jsx|ts|tsx)',
    '!src/**/*.d.ts',
    '!src/index.js',
    '!src/**/__tests__/**',
    '!src/**/*.test.*',
    '!src/**/*.spec.*'
  ],
  coverageDirectory: 'coverage',
  coverageReporters: [
    'text',
    'text-summary',
    'html',
    'lcov',
    'clover'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  setupFilesAfterEnv: ['<rootDir>/tests/setup.js'],
  moduleNameMapping: {
    '^@/(.*)$': '<rootDir>/src/$1'
  },
  verbose: true,
  bail: false,
  clearMocks: true,
  restoreMocks: true
};
```

#### Alternative: package.json Configuration
```json
{
  "jest": {
    "testEnvironment": "node",
    "testMatch": [
      "**/__tests__/**/*.(js|jsx|ts|tsx)",
      "**/*.(test|spec).(js|jsx|ts|tsx)"
    ],
    "collectCoverageFrom": [
      "src/**/*.(js|jsx|ts|tsx)",
      "!src/**/*.d.ts",
      "!src/**/__tests__/**",
      "!src/**/*.test.*"
    ],
    "coverageThreshold": {
      "global": {
        "branches": 80,
        "functions": 80,
        "lines": 80,
        "statements": 80
      }
    },
    "coverageDirectory": "coverage",
    "coverageReporters": ["text", "html", "lcov"]
  }
}
```

### Directory Structure
```
project/
├── src/
│   ├── components/
│   │   └── Button.js
│   └── utils/
│       └── helpers.js
├── tests/
│   ├── unit/
│   │   ├── components/
│   │   │   └── Button.test.js
│   │   └── utils/
│   │       └── helpers.test.js
│   ├── integration/
│   │   └── api.test.js
│   └── setup.js
├── __tests__/
│   └── app.test.js
├── jest.config.js
└── package.json
```

### Test Dependencies
```json
{
  "devDependencies": {
    "jest": "^29.0.0",
    "@testing-library/jest-dom": "^5.16.0",
    "@testing-library/react": "^13.0.0",
    "@testing-library/user-event": "^14.0.0",
    "jest-environment-jsdom": "^29.0.0",
    "supertest": "^6.3.0"
  }
}
```

## Multi-language Projects Baseline

### Testing Strategy Per Language

#### Python + JavaScript Project
```
project/
├── backend/ (Python)
│   ├── src/
│   ├── tests/
│   ├── pytest.ini
│   └── .coveragerc
├── frontend/ (JavaScript)
│   ├── src/
│   ├── tests/
│   └── jest.config.js
├── tests/ (Integration)
│   ├── e2e/
│   └── api/
├── .github/
│   └── workflows/
│       ├── backend-tests.yml
│       ├── frontend-tests.yml
│       └── integration-tests.yml
└── coverage-combined/
```

#### Unified Coverage Reporting
```yaml
# .github/workflows/coverage-report.yml
name: Combined Coverage Report
on: [push, pull_request]

jobs:
  combined-coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Backend Coverage
        run: |
          cd backend
          pytest --cov=src --cov-report=xml

      - name: Frontend Coverage
        run: |
          cd frontend
          npm test -- --coverage --coverageReporters=cobertura

      - name: Upload Combined Coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml,./frontend/coverage/cobertura-coverage.xml
```

## CI/CD Integration Standards

### GitHub Actions Requirements

#### All Projects Must Include:
1. **Test execution on multiple OS/versions**
2. **Coverage reporting and enforcement**
3. **Quality gates (fail on coverage < 80%)**
4. **Cache optimization for dependencies**
5. **Parallel test execution where possible**
6. **Security scanning integration**

#### Workflow Triggers:
- Push to main/develop branches
- Pull requests to main/develop
- Manual workflow dispatch
- Scheduled runs (weekly for dependency updates)

### Coverage Reporting Integration

#### Required Integrations:
- **Codecov**: For coverage visualization and PR comments
- **SonarQube**: For code quality analysis (optional)
- **GitHub Code Scanning**: For security analysis

#### Coverage Enforcement:
- Fail builds on coverage drop
- Block PRs below coverage threshold
- Generate coverage reports as artifacts
- Comment coverage changes on PRs

## Quality Standards

### Test Quality Metrics

#### Test Characteristics:
- **Fast**: Unit tests < 100ms, integration tests < 5s
- **Isolated**: No dependencies between tests
- **Deterministic**: Same input always produces same output
- **Maintainable**: Clear naming and structure

#### Test Types Distribution:
- **70%**: Unit tests (fast, isolated)
- **20%**: Integration tests (component interaction)
- **10%**: End-to-end tests (full system)

### Code Quality Integration

#### Required Checks:
- **Linting**: Code style consistency
- **Type checking**: Static type validation (where applicable)
- **Security scanning**: Dependency vulnerability checks
- **Performance testing**: For critical paths

## Implementation Guidelines

### New Project Setup
1. Choose appropriate templates from `/docs/testing-templates/`
2. Copy configuration files to project root
3. Set up directory structure
4. Install testing dependencies
5. Configure CI/CD workflow
6. Write first test to validate setup

### Existing Project Migration
1. Assess current test coverage
2. Identify gaps in testing infrastructure
3. Implement baseline configuration gradually
4. Migrate existing tests to new structure
5. Improve coverage incrementally
6. Update CI/CD pipelines

### Maintenance
- Monthly dependency updates
- Quarterly coverage analysis
- Annual testing strategy review
- Continuous improvement based on metrics

## Tools and Resources

### Required Testing Tools
- **Python**: pytest, coverage, tox
- **JavaScript**: Jest, @testing-library, supertest
- **CI/CD**: GitHub Actions, codecov
- **Quality**: SonarQube, Dependabot

### Documentation Requirements
- Testing section in README
- Contribution guidelines for tests
- Test writing best practices
- Coverage reporting links

## Compliance and Monitoring

### Regular Audits
- Monthly coverage reports
- Quarterly dependency security scans
- Annual testing strategy reviews
- Continuous monitoring of test performance

### Metrics Tracking
- Test coverage percentage
- Test execution time
- Test failure rates
- Code quality scores

---

*This document serves as the foundation for all testing practices within the Agent OS ecosystem. Individual projects may extend these standards but must not fall below the baseline requirements.*