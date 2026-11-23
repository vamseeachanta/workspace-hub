# Testing Framework Standards

> **Version:** 1.0.0
> **Last Updated:** 2025-10-22
> **Status:** Mandatory for all workspace-hub repositories

## Overview

This document defines mandatory testing standards for all 26 repositories in workspace-hub. All modules must achieve minimum 80% test coverage with a target of continuous improvement toward 90%+.

## Testing Framework Selection

### Python Repositories

**Primary Framework:** pytest

**Why pytest:**
- Rich plugin ecosystem (pytest-cov, pytest-mock, pytest-asyncio)
- Fixture system for test setup/teardown
- Parameterized testing support
- Clear, readable test output
- Excellent integration with CI/CD

**Required Packages:**
```txt
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-mock>=3.11.1
pytest-asyncio>=0.21.0  # For async tests
pytest-benchmark>=4.0.0  # For performance tests
```

**Installation:**
```bash
uv pip install pytest pytest-cov pytest-mock pytest-asyncio pytest-benchmark
```

### JavaScript/TypeScript Repositories

**Primary Framework:** Jest

**Why Jest:**
- Zero-config for most projects
- Built-in code coverage
- Snapshot testing
- Mocking utilities
- Parallel test execution

**Required Packages:**
```json
{
  "devDependencies": {
    "jest": "^29.6.0",
    "@types/jest": "^29.5.3",
    "ts-jest": "^29.1.1"
  }
}
```

### Bash/Shell Script Repositories

**Primary Framework:** bats-core

**Why bats-core:**
- TAP-compliant output
- Simple syntax
- Good for CLI testing
- Integration test support

**Installation:**
```bash
# Via package manager
npm install -g bats

# Or via git submodule
git submodule add https://github.com/bats-core/bats-core.git tests/bats
```

## Test Organization

### Directory Structure

```
repository/
├── src/
│   └── modules/
│       └── module_name/
│           ├── __init__.py
│           └── core.py
├── tests/
│   ├── unit/
│   │   └── test_module_name.py
│   ├── integration/
│   │   └── test_module_integration.py
│   ├── performance/
│   │   └── test_module_performance.py
│   ├── fixtures/
│   │   └── sample_data.json
│   ├── conftest.py  # pytest fixtures
│   └── __init__.py
├── pytest.ini
└── .coveragerc
```

### File Naming Conventions

- **Unit tests:** `test_<module_name>.py` or `<module_name>_test.py`
- **Integration tests:** `test_<feature>_integration.py`
- **Performance tests:** `test_<feature>_performance.py`
- **Test fixtures:** `conftest.py` (pytest) or `fixtures/` directory

## Test Types

### 1. Unit Tests

**Purpose:** Test individual functions/methods in isolation

**Requirements:**
- Test single units of code
- Mock external dependencies
- Fast execution (< 100ms per test)
- No file I/O or network calls
- Deterministic results

**Example (Python):**
```python
import pytest
from src.modules.data_processing import clean_data

def test_clean_data_removes_nulls():
    """Test that clean_data removes null values."""
    input_data = [1, 2, None, 4, None, 6]
    expected = [1, 2, 4, 6]

    result = clean_data(input_data)

    assert result == expected

def test_clean_data_handles_empty_list():
    """Test that clean_data handles empty input."""
    result = clean_data([])
    assert result == []

@pytest.mark.parametrize("input_data,expected", [
    ([1, 2, 3], [1, 2, 3]),
    ([None, None], []),
    ([1, None, 2], [1, 2])
])
def test_clean_data_parametrized(input_data, expected):
    """Parametrized test for various inputs."""
    assert clean_data(input_data) == expected
```

### 2. Integration Tests

**Purpose:** Test interaction between components

**Requirements:**
- Test component integration
- Use real dependencies where possible
- Test data flow between modules
- Verify error propagation
- Test external API interactions

**Example (Python):**
```python
import pytest
from src.modules.pipeline import DataPipeline
from src.modules.storage import DataStore

@pytest.fixture
def pipeline():
    """Create pipeline with real dependencies."""
    store = DataStore(":memory:")  # Use in-memory DB
    pipeline = DataPipeline(store)
    yield pipeline
    pipeline.cleanup()

def test_pipeline_end_to_end(pipeline):
    """Test complete data processing pipeline."""
    input_data = {"values": [1, 2, 3, 4, 5]}

    result = pipeline.process(input_data)

    assert result["status"] == "success"
    assert result["processed_count"] == 5
    assert pipeline.store.get_count() == 5

def test_pipeline_error_handling(pipeline):
    """Test pipeline handles errors gracefully."""
    invalid_data = {"invalid_key": "value"}

    result = pipeline.process(invalid_data)

    assert result["status"] == "error"
    assert "error_message" in result
```

### 3. Performance Tests

**Purpose:** Ensure code meets performance requirements

**Requirements:**
- Run on every commit (CI/CD)
- Fail if thresholds exceeded
- Track performance trends
- Test with realistic data sizes
- Measure time and memory

**Example (Python with pytest-benchmark):**
```python
import pytest
from src.modules.algorithms import sort_large_dataset

def test_sort_performance(benchmark):
    """Ensure sorting completes within time limit."""
    data = list(range(10000, 0, -1))  # Worst case

    result = benchmark(sort_large_dataset, data)

    assert len(result) == 10000
    assert result == sorted(data)

    # Performance assertion
    assert benchmark.stats['mean'] < 0.5  # Must complete in < 500ms

@pytest.mark.benchmark(group="data-processing")
def test_data_processing_memory(benchmark):
    """Test memory efficiency of data processing."""
    large_dataset = [{"id": i, "data": "x" * 100} for i in range(1000)]

    result = benchmark(process_data, large_dataset)

    assert len(result) == 1000
```

**Performance Test Configuration:**
```ini
# pytest.ini
[tool:pytest]
markers =
    performance: Performance benchmark tests
    slow: Tests that take > 1 second

# Fail if performance tests exceed thresholds
benchmark_max_time = 0.5
benchmark_warmup = true
```

## Test Coverage Requirements

### Minimum Coverage Targets

| Coverage Type | Minimum | Target | Enforcement |
|--------------|---------|--------|-------------|
| Line Coverage | 80% | 90% | CI/CD fails < 80% |
| Branch Coverage | 75% | 85% | CI/CD warns < 75% |
| Function Coverage | 85% | 95% | CI/CD warns < 85% |

### Coverage Configuration

**Python (.coveragerc):**
```ini
[run]
source = src/
omit =
    */tests/*
    */venv/*
    */__pycache__/*
    */site-packages/*

[report]
precision = 2
show_missing = True
skip_covered = False

fail_under = 80

[html]
directory = htmlcov
```

**JavaScript (jest.config.js):**
```javascript
module.exports = {
  collectCoverage: true,
  coverageDirectory: "coverage",
  coverageReporters: ["text", "lcov", "html"],
  coverageThresholds: {
    global: {
      branches: 75,
      functions: 85,
      lines: 80,
      statements: 80
    }
  },
  collectCoverageFrom: [
    "src/**/*.{js,ts,tsx}",
    "!src/**/*.d.ts",
    "!src/**/*.test.{js,ts,tsx}"
  ]
};
```

### Running Coverage

**Python:**
```bash
# Run tests with coverage
pytest --cov=src --cov-report=html --cov-report=term

# Generate HTML report
pytest --cov=src --cov-report=html
open htmlcov/index.html

# Fail if below threshold
pytest --cov=src --cov-fail-under=80
```

**JavaScript:**
```bash
# Run tests with coverage
npm test -- --coverage

# View HTML report
open coverage/lcov-report/index.html
```

## Test Execution

### Local Development

**Run all tests:**
```bash
# Python
pytest

# JavaScript
npm test

# Bash
bats tests/
```

**Run specific test types:**
```bash
# Python
pytest tests/unit/                    # Unit tests only
pytest tests/integration/             # Integration tests only
pytest -m performance                 # Performance tests only
pytest -k "test_specific_function"   # Match by name

# JavaScript
npm test -- tests/unit/              # Unit tests only
npm test -- --testPathPattern=integration  # Integration tests
```

**Watch mode (continuous testing):**
```bash
# Python
pytest-watch

# JavaScript
npm test -- --watch
```

### CI/CD Integration

**GitHub Actions (.github/workflows/test.yml):**
```yaml
name: Test Suite

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'

    - name: Install dependencies
      run: |
        pip install uv
        uv pip install -r requirements.txt
        uv pip install pytest pytest-cov

    - name: Run tests with coverage
      run: |
        pytest --cov=src --cov-report=xml --cov-report=term --cov-fail-under=80

    - name: Run performance tests
      run: |
        pytest -m performance --benchmark-only

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        fail_ci_if_error: true
```

## Test Data Management

### Fixtures and Test Data

**Location:** `tests/fixtures/`

**Organization:**
```
tests/
└── fixtures/
    ├── sample_data.json
    ├── test_config.yaml
    ├── mock_responses/
    │   ├── api_success.json
    │   └── api_error.json
    └── expected_outputs/
        └── processed_data.json
```

**Usage (Python):**
```python
import pytest
import json
from pathlib import Path

@pytest.fixture
def sample_data():
    """Load sample data fixture."""
    fixture_path = Path(__file__).parent / "fixtures" / "sample_data.json"
    with open(fixture_path) as f:
        return json.load(f)

def test_with_fixture(sample_data):
    """Test using fixture data."""
    result = process_data(sample_data)
    assert result is not None
```

### Mock Data Guidelines

- Use realistic data that represents production scenarios
- Include edge cases and boundary conditions
- Version control all test fixtures
- Document expected data formats
- Keep fixtures minimal but representative

## Test Assertions

### Best Practices

**1. Clear and Specific:**
```python
# ❌ Bad: Generic assertion
assert result

# ✅ Good: Specific assertion
assert result["status"] == "success"
assert len(result["items"]) == 5
```

**2. Descriptive Error Messages:**
```python
# ❌ Bad: No context
assert value > 0

# ✅ Good: Context provided
assert value > 0, f"Expected positive value, got {value}"
```

**3. Use Appropriate Assertion Methods:**
```python
# Pytest assertions
assert value == expected
assert value in collection
assert value is not None
pytest.approx(3.14159, abs=0.001)  # Float comparison

# unittest assertions
self.assertEqual(value, expected)
self.assertIn(value, collection)
self.assertIsNotNone(value)
self.assertRaises(ValueError, func, args)
```

## Performance Test Standards

### Execution Requirements

**1. Run on Every Commit:**
```yaml
# .github/workflows/performance.yml
name: Performance Tests

on: [push, pull_request]

jobs:
  performance:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Run performance tests
      run: pytest -m performance --benchmark-only

    - name: Fail if threshold exceeded
      run: |
        if [ $? -ne 0 ]; then
          echo "Performance tests failed - threshold exceeded"
          exit 1
        fi
```

**2. Define Thresholds:**
```python
# conftest.py
def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "performance: Performance tests with time thresholds"
    )

# Performance thresholds
PERFORMANCE_THRESHOLDS = {
    "data_processing": 0.5,  # 500ms
    "file_operations": 1.0,   # 1 second
    "api_calls": 2.0,         # 2 seconds
}
```

**3. Track Trends:**
- Store benchmark results in CI artifacts
- Compare against baseline performance
- Alert on performance regressions
- Generate performance trend reports

## Test Documentation

### Test Docstrings

**Required Format:**
```python
def test_function_name():
    """
    Short description of what is being tested.

    Test Steps:
    1. Setup test data
    2. Execute function under test
    3. Verify expected outcome

    Expected Result:
    - Specific expected behavior

    Edge Cases Tested:
    - Empty input
    - Invalid data types
    - Boundary conditions
    """
    # Test implementation
```

### Test Coverage Reports

**Generate Reports:**
```bash
# Python HTML report
pytest --cov=src --cov-report=html
# Output: htmlcov/index.html

# JavaScript HTML report
npm test -- --coverage
# Output: coverage/lcov-report/index.html
```

**CI/CD Report Upload:**
- Upload coverage reports to Codecov or Coveralls
- Generate coverage badges for README
- Track coverage trends over time
- Fail PR if coverage decreases

## Common Patterns

### Setup and Teardown

**pytest fixtures:**
```python
import pytest

@pytest.fixture
def database():
    """Setup test database."""
    db = Database(":memory:")
    db.create_tables()
    yield db
    db.close()

@pytest.fixture(scope="session")
def app_config():
    """Load app config once per test session."""
    config = load_config("test_config.yaml")
    return config
```

**unittest setUp/tearDown:**
```python
import unittest

class TestDataProcessor(unittest.TestCase):
    def setUp(self):
        """Setup before each test."""
        self.processor = DataProcessor()
        self.test_data = [1, 2, 3, 4, 5]

    def tearDown(self):
        """Cleanup after each test."""
        self.processor.cleanup()

    def test_processing(self):
        result = self.processor.process(self.test_data)
        self.assertEqual(len(result), 5)
```

### Mocking External Dependencies

**pytest-mock:**
```python
def test_api_call(mocker):
    """Test function that makes API call."""
    # Mock external API
    mock_response = {"status": "success", "data": [1, 2, 3]}
    mocker.patch('module.requests.get', return_value=mock_response)

    result = fetch_data_from_api()

    assert result == mock_response
```

**unittest.mock:**
```python
from unittest.mock import patch, MagicMock

def test_file_operations():
    """Test file operations with mocked filesystem."""
    with patch('builtins.open', create=True) as mock_open:
        mock_open.return_value = MagicMock()

        result = read_file("test.txt")

        mock_open.assert_called_once_with("test.txt", 'r')
```

## Continuous Improvement

### Coverage Goals

1. **Initial Phase:** Achieve 80% coverage
2. **Improvement Phase:** Target 85% coverage within 3 months
3. **Excellence Phase:** Maintain 90%+ coverage

### Review Process

- Review test coverage in every PR
- Require tests for all new features
- Add tests when fixing bugs
- Refactor tests to improve clarity
- Remove obsolete tests

### Metrics Tracking

Track and report:
- Overall coverage percentage
- Coverage trends over time
- Test execution time trends
- Performance benchmark results
- Flaky test identification

## Tools and Resources

### Recommended Tools

- **Coverage Visualization:** Codecov, Coveralls
- **Test Reporting:** pytest-html, Allure
- **Performance Tracking:** pytest-benchmark, locust
- **Test Generation:** hypothesis (property-based testing)
- **Mutation Testing:** mutmut (Python), Stryker (JavaScript)

### Additional Resources

- pytest documentation: https://docs.pytest.org/
- Jest documentation: https://jestjs.io/docs/getting-started
- bats-core documentation: https://bats-core.readthedocs.io/
- Testing best practices: https://testingjavascript.com/

## Repository-Specific Adaptations

Each repository may customize:
- Additional test markers
- Custom fixtures
- Performance thresholds
- Mock strategies
- Test utilities

**Document customizations in:** `tests/README.md` per repository

---

**Compliance:** This document is mandatory for all workspace-hub repositories. Non-compliance will block PR merges.
