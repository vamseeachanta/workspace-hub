# pytest.ini Quick Reference Card

> Print this card and keep it visible while testing!
> Last Updated: 2025-01-13

## Installation (One-Time Setup)

```bash
# Install pytest and plugins
pip install pytest pytest-cov pytest-asyncio pytest-mock pytest-xdist pytest-timeout

# Copy appropriate tier template to your repo root
cp pytest.tier2.ini pytest.ini  # Change tier based on your repo

# Verify setup
pytest --co

# Run your first tests
pytest tests/ -v
```

## Test Markers (Mark Every Test)

```python
# PRIMARY: Choose exactly one per test

@pytest.mark.unit              # Fast, single function
@pytest.mark.integration       # Components interact
@pytest.mark.e2e              # Complete workflow

# SECONDARY: Add as needed

@pytest.mark.slow             # Takes >2 seconds
@pytest.mark.flaky            # Sometimes fails
@pytest.mark.database         # Needs database
@pytest.mark.api              # Makes API calls
@pytest.mark.selenium         # Browser automation
@pytest.mark.llm              # LLM API calls
```

## Common Commands

```bash
# RUN TESTS
pytest                        # Run all tests
pytest tests/unit/            # Run specific directory
pytest tests/test_file.py     # Run single file
pytest -k "keyword"           # Run tests matching name

# BY MARKER
pytest -m unit                # Run only unit tests
pytest -m "unit or integration"  # Run unit OR integration
pytest -m "not slow"          # Skip slow tests
pytest -m "not (api or selenium)"  # Skip multiple

# COVERAGE
pytest --cov=src --cov-report=html  # Generate HTML report
pytest --cov --cov-fail-under=80    # Check threshold
open htmlcov/index.html       # View in browser (macOS)
xdg-open htmlcov/index.html   # View in browser (Linux)

# PARALLEL
pytest -n auto                # Use all CPU cores
pytest -n 4                   # Use 4 workers
pytest -n 8                   # Use 8 workers

# DEBUGGING
pytest -v                     # Verbose output
pytest -s                     # Show print() output
pytest --tb=short             # Short traceback
pytest -x                     # Stop on first failure
pytest --pdb                  # Drop to debugger on failure
pytest --lf                   # Run last failed tests
pytest --ff                   # Failed first, then others

# PERFORMANCE
pytest --durations=10         # Show slowest 10 tests
pytest --benchmark-only       # Run only benchmarks
```

## Development Workflow

### During Coding (Fast Feedback)

```bash
# Only run fast unit tests
pytest -m unit

# Or skip slow tests
pytest -m "not slow"

# Show specific test failures
pytest -v -x

# Run with debugging
pytest -s --tb=short
```

### Before Committing

```bash
# Run full unit + integration suite
pytest -m "unit or integration"

# Check coverage meets threshold
pytest --cov --cov-report=html

# Fix any coverage gaps by opening htmlcov/index.html
open htmlcov/index.html
```

### Before Merging PR

```bash
# Run complete test suite
pytest -n 8                   # Parallel for speed

# Check coverage threshold
pytest --cov --cov-fail-under=80

# Verify no flaky tests
pytest --tb=short             # Show full output
```

## Coverage Thresholds by Tier

| Tier | Threshold | Repos |
|------|-----------|-------|
| **1** | 85% | digitalmodel, energy, frontierdeepwater |
| **2** | 80% | aceengineercode, assetutilities, worldenergydata |
| **3** | 75% | All others |

**Check your repo's tier:**
```bash
# Tier 1 repos: Must have 85%+
pytest --cov --cov-fail-under=85

# Tier 2 repos: Must have 80%+
pytest --cov --cov-fail-under=80

# Tier 3 repos: Must have 75%+
pytest --cov --cov-fail-under=75
```

## Fixtures (Reusable Setup)

```python
import pytest

# Basic fixture
@pytest.fixture
def sample_data():
    return {"key": "value"}

# Fixture with cleanup
@pytest.fixture
def temp_file():
    f = open("temp.txt", "w")
    yield f
    f.close()

# Use in tests
def test_something(sample_data, temp_file):
    assert sample_data["key"] == "value"
```

## Quick Examples

### Unit Test (Fast)
```python
@pytest.mark.unit
def test_calculate():
    result = add(2, 3)
    assert result == 5
```

### Integration Test (Moderate)
```python
@pytest.mark.integration
def test_user_workflow(db_session):
    user = User(name="Test")
    db_session.add(user)
    db_session.commit()
    assert user.id is not None
```

### Async Test
```python
@pytest.mark.unit
async def test_async_function():
    result = await get_data()
    assert result is not None
```

### Slow Test
```python
@pytest.mark.unit
@pytest.mark.slow
def test_complex_algorithm():
    result = slow_computation()
    assert result > 0
```

### Flaky Test (Rerun)
```python
@pytest.mark.integration
@pytest.mark.flaky
def test_async_operation():
    # Run with: pytest --reruns 3
    pass
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Unknown marker error | Add marker to `markers =` in pytest.ini |
| Tests hang | Check `timeout = 300` setting |
| Coverage not enforced | Add `--cov-fail-under=80` to `addopts` |
| Async tests fail | Install: `pip install pytest-asyncio` |
| Parallel tests fail | Use fixtures instead of shared state |
| Can't find tests | Verify directory is `tests/` and files are `test_*.py` |

## CI/CD Pipeline Commands

```bash
# GitHub Actions
pytest -n 8 --cov --cov-fail-under=80

# Tier 1 (stricter)
pytest -n 4 --cov --cov-fail-under=85

# Tier 2 (balanced)
pytest -n 8 --cov --cov-fail-under=80

# Tier 3 (relaxed)
pytest -n 12 --cov --cov-fail-under=75
```

## pytest.ini Key Settings

```ini
# Coverage threshold
fail_under = 80

# Test timeout in seconds
timeout = 300

# Parallel workers (install pytest-xdist first)
addopts = -n 8

# Async mode
asyncio_mode = auto

# All markers
markers =
    unit: Fast single function tests
    integration: Component interaction tests
    e2e: Complete workflow tests
    slow: Tests taking >2 seconds
    flaky: Non-deterministic tests
    database: Tests requiring database
    api: Tests making API calls
```

## Performance Tips

```bash
# Use parallel execution (speeds up tests 4-8x)
pytest -n 8

# Skip slow tests during development
pytest -m "not slow"

# Run only specific test files
pytest tests/unit/test_critical.py

# Run tests that failed last
pytest --lf

# Show slowest tests
pytest --durations=10
```

## Coverage Report Inspection

```bash
# Terminal output shows missing lines:
# src/module.py: 45, 67, 89  (not covered)

# HTML report shows visual coverage:
pytest --cov --cov-report=html
open htmlcov/index.html
# Red = uncovered, green = covered

# Focus on improving critical paths first
# Review untested error handling
# Add tests for complex logic
```

## Before You Commit

```bash
# Complete checklist:
□ pytest -m unit                    # Unit tests pass
□ pytest -m "unit or integration"   # Integration tests pass
□ pytest --cov --cov-report=html    # Coverage at threshold
□ open htmlcov/index.html           # Review coverage gaps
□ pytest -n 8                       # Parallel tests pass
□ git add <files>
□ git commit -m "message"
□ git push
```

---

**Save this card! Reference it during development.**

For full documentation: @docs/templates/PYTEST_DEPLOYMENT_GUIDE.md
