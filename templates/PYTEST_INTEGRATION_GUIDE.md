# Pytest & Coverage Integration Guide

> Quick reference for adding pytest and coverage to any workspace-hub repository

## Quick Start (5 minutes)

### 1. Copy Test Dependencies

Open `pytest-coverage-config.toml` and copy the `[project.optional-dependencies]` section into your `pyproject.toml`:

```toml
[project.optional-dependencies]

test-core = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
]

test-standard = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "pytest-asyncio>=0.21.0,<0.24.0",
    "pytest-mock>=3.11.0,<4.0.0",
]

test-advanced = [
    # ... see template
]

dev = [
    # ... see template
]
```

**Choose one group based on project complexity:**
- **Simple projects**: Use `test-core`
- **Most projects**: Use `test-standard`
- **Complex projects**: Use `test-advanced`

### 2. Copy Pytest Configuration

Copy `[tool.pytest.ini_options]` from the template:

```toml
[tool.pytest.ini_options]
testpaths = ["tests", "test"]
python_files = ["test_*.py", "*_test.py", "tests.py"]
# ... rest of config
```

### 3. Copy Coverage Configuration

Copy all `[tool.coverage.*]` sections:

```toml
[tool.coverage.run]
source = ["src", "app"]
# ... rest of config

[tool.coverage.report]
# ... set fail_under based on your tier (see below)

[tool.coverage.html]
# ...

[tool.coverage.xml]
# ...

[tool.coverage.json]
# ...
```

### 4. Set Coverage Threshold (IMPORTANT)

In `[tool.coverage.report]`, set `fail_under` based on your repository tier:

**Work/Production Repositories (Tier 1):**
```toml
fail_under = 85  # Higher standard for production
```

**Active Development Repositories (Tier 2):**
```toml
fail_under = 80  # Standard for active work
```

**Maintenance Repositories (Tier 3):**
```toml
fail_under = 80  # Same standard, less frequent testing
```

### 5. Install Dependencies

```bash
# Install test dependencies (choose one group)
uv pip install -e ".[test-standard]"

# Or install everything including dev tools
uv pip install -e ".[test-standard,dev]"
```

## Testing Your Setup

### Run basic tests:
```bash
pytest
```

### Run with coverage report:
```bash
pytest --cov
```

### Generate HTML coverage report:
```bash
pytest --cov --cov-report=html
# Open: htmlcov/index.html
```

### Run specific test markers:
```bash
pytest -m unit                    # Unit tests only
pytest -m "not slow"              # Skip slow tests
pytest -m integration             # Integration tests
pytest -m "unit and not slow"     # Combination
```

### Run with parallel execution (if using test-advanced):
```bash
pytest -n auto                    # Auto-detect CPU cores
pytest -n 4                       # Explicit 4 workers
```

### Run benchmarks (if using test-advanced):
```bash
pytest -m benchmark --benchmark-only
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Tests

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
        uv pip install -e ".[test-standard]"

    - name: Run tests with coverage
      run: |
        pytest --cov --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        files: ./coverage.xml
        fail_ci_if_error: true
```

### Coverage Check (Blocking PR)

```yaml
    - name: Check coverage threshold
      run: |
        pytest --cov --cov-fail-under=80
        # Will fail if coverage < 80%
```

## Test Organization Structure

```
repository/
├── src/                          # Source code
│   └── modules/
│       └── my_module/
│           ├── __init__.py
│           └── core.py
│
├── tests/                        # Test files
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures & config
│   │
│   ├── unit/                    # Unit tests (isolated)
│   │   ├── test_module.py
│   │   └── test_core.py
│   │
│   ├── integration/             # Integration tests (multiple components)
│   │   └── test_workflow.py
│   │
│   ├── performance/             # Performance tests (benchmarks)
│   │   └── test_performance.py
│   │
│   └── fixtures/                # Test data & utilities
│       ├── sample_data.json
│       └── mock_responses.json
│
├── .coverage                     # Coverage database (auto-generated)
├── htmlcov/                      # HTML coverage report (auto-generated)
├── coverage.xml                  # XML coverage report (CI/CD)
└── pyproject.toml               # Configuration (modified)
```

## Writing Tests - Quick Examples

### Unit Test

```python
import pytest
from src.modules.calculator import add

def test_add_positive_numbers():
    """Test adding two positive numbers."""
    result = add(2, 3)
    assert result == 5

def test_add_negative_numbers():
    """Test adding negative numbers."""
    result = add(-2, -3)
    assert result == -5
```

### Test with Markers

```python
import pytest

@pytest.mark.unit
def test_fast_operation():
    """Fast unit test."""
    assert True

@pytest.mark.slow
def test_slow_operation():
    """Slow test that takes time."""
    import time
    time.sleep(5)
    assert True

@pytest.mark.integration
def test_database_operation():
    """Integration test with database."""
    assert True
```

### Async Test (requires pytest-asyncio)

```python
import pytest

@pytest.mark.asyncio
async def test_async_operation():
    """Test async function."""
    result = await some_async_function()
    assert result == expected
```

### Test with Mocking (requires pytest-mock)

```python
def test_with_mock(mocker):
    """Test using mocked dependency."""
    mock_db = mocker.patch('module.database')
    mock_db.query.return_value = [1, 2, 3]

    result = function_that_uses_db()
    assert result == [1, 2, 3]
```

### Property-Based Test (requires hypothesis)

```python
from hypothesis import given, strategies as st

@given(st.integers())
def test_property_addition(x):
    """Property: x + 0 = x (always true)."""
    assert x + 0 == x
```

## Common Commands

| Command | Purpose |
|---------|---------|
| `pytest` | Run all tests |
| `pytest -v` | Verbose output |
| `pytest -k test_name` | Run matching tests |
| `pytest tests/unit/` | Run specific directory |
| `pytest -m unit` | Run tests with marker |
| `pytest --co` | Show test collection (don't run) |
| `pytest --cov` | Run with coverage |
| `pytest --cov --cov-report=html` | HTML coverage report |
| `pytest --cov --cov-report=term-missing` | Show missing lines |
| `pytest -n auto` | Parallel execution (4 workers) |
| `pytest --pdb` | Drop to debugger on failure |
| `pytest -x` | Stop on first failure |
| `pytest --lf` | Run last failed tests |
| `pytest --failed-first` | Run failed tests first |
| `pytest --durations=10` | Show 10 slowest tests |

## Troubleshooting

### Issue: "No tests collected"

**Solution**: Ensure test files follow naming pattern:
- ✅ `test_module.py` or `module_test.py`
- ❌ `check_module.py` or `validate_module.py`

### Issue: "ModuleNotFoundError: No module named 'src'"

**Solution**: Install package in editable mode:
```bash
uv pip install -e .
```

### Issue: Coverage threshold check fails

**Solution**: Either:
1. Increase test coverage by writing more tests
2. Lower `fail_under` threshold in pyproject.toml
3. Add exclusions to `exclude_lines` in coverage config

### Issue: Tests hang or timeout

**Solution**: Check for:
- Infinite loops in code
- Blocking network calls (mock them)
- Missing test timeout setting

Tests are configured with `--timeout=300` (5 minutes default).

### Issue: Async tests fail with "Event loop is closed"

**Solution**: Ensure pytest-asyncio is installed:
```bash
uv pip install pytest-asyncio
```

## Repository Tier Configuration

### Tier 1: Work/Production Repositories
Examples: digitalmodel, energy, frontierdeepwater, aceengineercode

```toml
[tool.coverage.report]
fail_under = 85  # Higher threshold
```

Additional requirements:
- All new code must have tests
- Coverage must not decrease
- Integration tests required for features

### Tier 2: Active Development Repositories
Examples: aceengineer-website, hobbies, sd-work

```toml
[tool.coverage.report]
fail_under = 80  # Standard threshold
```

Requirements:
- New features should have tests
- Coverage should not decrease
- Can defer comprehensive testing initially

### Tier 3: Maintenance Repositories
Examples: doris, saipem, OGManufacturing

```toml
[tool.coverage.report]
fail_under = 80  # Standard threshold (lower activity)
```

Requirements:
- Bug fixes should have tests
- No regression in coverage
- Testing can be less comprehensive

## Advanced Usage

### Skip Tests at Runtime

```python
@pytest.mark.skip(reason="Not implemented yet")
def test_future_feature():
    pass

@pytest.mark.skipif(sys.version_info < (3, 10), reason="Requires Python 3.10+")
def test_modern_feature():
    pass
```

### Fixtures for Test Setup

```python
import pytest

@pytest.fixture
def sample_data():
    """Provide sample data for tests."""
    return {"key": "value", "number": 42}

def test_with_fixture(sample_data):
    """Test using fixture."""
    assert sample_data["number"] == 42
```

### Custom Markers

Add to `pyproject.toml` and use:

```python
@pytest.mark.custom_marker
def test_custom():
    pass
```

## Coverage Report Formats

### Terminal Report (default)
```bash
pytest --cov
```

### HTML Report (for browser viewing)
```bash
pytest --cov --cov-report=html
open htmlcov/index.html
```

### XML Report (for CI/CD)
```bash
pytest --cov --cov-report=xml
# Upload to Codecov, CircleCI, etc.
```

### JSON Report (for programmatic access)
```bash
pytest --cov --cov-report=json
# Parse coverage.json programmatically
```

## Resources

- **pytest docs**: https://docs.pytest.org/
- **Coverage.py docs**: https://coverage.readthedocs.io/
- **pytest-cov docs**: https://pytest-cov.readthedocs.io/
- **Hypothesis docs**: https://hypothesis.readthedocs.io/
- **pytest-asyncio docs**: https://pytest-asyncio.readthedocs.io/

## Quick Checklist

- [ ] Copy `[project.optional-dependencies]` to pyproject.toml
- [ ] Copy `[tool.pytest.ini_options]` to pyproject.toml
- [ ] Copy all `[tool.coverage.*]` sections to pyproject.toml
- [ ] Set `fail_under` based on repository tier (80 or 85)
- [ ] Create `tests/` directory with test files
- [ ] Run `uv pip install -e ".[test-standard]"`
- [ ] Run `pytest --cov` to verify setup
- [ ] Add pytest to CI/CD pipeline
- [ ] Create `tests/conftest.py` for shared fixtures
- [ ] Write tests for new code

---

**Updated**: 2025-01-13
**Part of**: workspace-hub testing standards
