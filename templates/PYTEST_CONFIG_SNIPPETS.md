# Pytest Configuration Snippets

> Copy-paste ready configurations for different repository types

## One-Minute Setup

Pick your repository type and copy the entire config into your `pyproject.toml`:

---

## 1. MINIMAL CONFIG (Starting Out)

Use this if you're just getting started with testing.

```toml
# Test Dependencies
[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
]

# Pytest Configuration
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = "--verbose --tb=short"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "slow: Slow tests",
]

# Coverage Configuration (Tier 2-3: fail_under = 80)
[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*", "*/test_*.py", "*/venv/*"]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
show_missing = true
fail_under = 80
```

---

## 2. STANDARD CONFIG (Most Projects)

Use this for typical Python projects with async support and mocking.

```toml
# Test Dependencies
[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "pytest-asyncio>=0.21.0,<0.24.0",
    "pytest-mock>=3.11.0,<4.0.0",
]

# Pytest Configuration
[tool.pytest.ini_options]
testpaths = ["tests", "test"]
python_files = ["test_*.py", "*_test.py", "tests.py"]
python_classes = ["Test*", "*Tests"]
python_functions = ["test_*", "*_test"]
minversion = "7.0"

addopts = [
    "--verbose",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--timeout=300",
    "--durations=10",
    "--color=yes",
]

markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (multiple components)",
    "performance: Performance benchmarks",
    "slow: Slow tests (deselect with '-m \"not slow\"')",
    "asyncio: Async/await tests",
    "external: Tests requiring external services",
]

filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
]

# Coverage Configuration (Tier 2-3: fail_under = 80)
[tool.coverage.run]
source = ["src", "app"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
    "*/env/*",
    "setup.py",
    "*/migrations/*",
    "*/conftest.py",
    "*/__init__.py",
]
branch = true
parallel = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "if typing.TYPE_CHECKING:",
    "@abstract",
    "@abstractmethod",
    "if self.debug:",
    "if settings.debug:",
    "pass",
    "\\.\\.\\.",
]
precision = 2
show_missing = true
skip_covered = false
skip_empty = false
fail_under = 80

[tool.coverage.html]
directory = "htmlcov"
show_contexts = true

[tool.coverage.xml]
output = "coverage.xml"

[tool.coverage.json]
output = "coverage.json"
show_contexts = true
```

---

## 3. ADVANCED CONFIG (Complex Projects)

Use this for production systems with benchmarking, property testing, and parallel execution.

```toml
# Test Dependencies
[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "pytest-asyncio>=0.21.0,<0.24.0",
    "pytest-mock>=3.11.0,<4.0.0",
    "pytest-benchmark>=4.0.0,<5.0.0",
    "hypothesis>=6.92.0,<7.0.0",
    "pytest-xdist>=3.5.0,<4.0.0",
]

# Pytest Configuration
[tool.pytest.ini_options]
testpaths = ["tests", "test"]
python_files = ["test_*.py", "*_test.py", "tests.py"]
python_classes = ["Test*", "*Tests"]
python_functions = ["test_*", "*_test"]
minversion = "7.0"

addopts = [
    "--verbose",
    "--strict-markers",
    "--strict-config",
    "--tb=short",
    "--timeout=300",
    "--durations=10",
    "--color=yes",
    "--cov=src",
    "--cov-report=term-missing",
]

markers = [
    "unit: Unit tests (fast, isolated)",
    "integration: Integration tests (multiple components)",
    "performance: Performance benchmarks",
    "slow: Slow tests (deselect with '-m \"not slow\"')",
    "asyncio: Async/await tests",
    "benchmark: pytest-benchmark performance tests",
    "property: Property-based tests with Hypothesis",
    "external: Tests requiring external services",
    "security: Security-focused tests",
    "regression: Regression tests for bug fixes",
]

filterwarnings = [
    "error",
    "ignore::UserWarning",
    "ignore::DeprecationWarning",
    "ignore::PendingDeprecationWarning",
]

# Coverage Configuration (Tier 1: fail_under = 85)
[tool.coverage.run]
source = ["src", "app"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/__pycache__/*",
    "*/venv/*",
    "*/.venv/*",
    "*/env/*",
    "*/virtualenv/*",
    "setup.py",
    "*/migrations/*",
    "*/conftest.py",
    "*/__init__.py",
]
branch = true
parallel = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "if typing.TYPE_CHECKING:",
    "@abstract",
    "@abstractmethod",
    "if self.debug:",
    "if settings.debug:",
    "if sys.platform",
    "if sys.version_info",
    "pass",
    "\\.\\.\\.",
]
precision = 2
show_missing = true
skip_covered = false
skip_empty = false
fail_under = 85  # Higher threshold for Tier 1

[tool.coverage.html]
directory = "htmlcov"
show_contexts = true

[tool.coverage.xml]
output = "coverage.xml"

[tool.coverage.json]
output = "coverage.json"
show_contexts = true

# Benchmark Configuration
[tool.pytest.benchmark]
skip = false
disable_gc = true
min_time = 0.000005
max_time = 1.0
min_rounds = 5
timer = "perf_counter"
calibration_precision = 10
warmup = false
warmup_iterations = 100000

# Hypothesis Configuration
[tool.hypothesis]
max_examples = 100
deadline = 800
database_file = ".hypothesis/examples"
verbosity = "normal"
print_blob = false
```

---

## 4. MINIMAL DATA SCIENCE CONFIG (Jupyter/Notebooks)

For repositories with notebooks, exploratory code, and data pipelines.

```toml
# Test Dependencies
[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
]

# Pytest Configuration
[tool.pytest.ini_options]
testpaths = ["tests", "notebooks/tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = "--verbose --tb=short"
markers = [
    "unit: Unit tests",
    "integration: Integration tests",
]

# Coverage Configuration
[tool.coverage.run]
source = ["src"]
omit = [
    "*/tests/*",
    "*/test_*.py",
    "*/venv/*",
    "*/notebooks/*",
    "*/__pycache__/*",
]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
show_missing = true
fail_under = 70  # Relaxed threshold for data science
```

---

## 5. API/FASTAPI CONFIG

For FastAPI and REST API projects.

```toml
# Test Dependencies
[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "pytest-asyncio>=0.21.0,<0.24.0",
    "pytest-mock>=3.11.0,<4.0.0",
    "httpx>=0.28.0,<0.29.0",  # For testing FastAPI
]

# Pytest Configuration
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]

addopts = [
    "--verbose",
    "--strict-markers",
    "--tb=short",
    "--timeout=30",  # Shorter timeout for API tests
]

markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "api: API endpoint tests",
    "slow: Slow tests",
]

# Coverage Configuration
[tool.coverage.run]
source = ["app", "src"]
omit = [
    "*/tests/*",
    "*/venv/*",
    "*/migrations/*",
]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
    "@app.on_event",
    "@app.middleware",
]
show_missing = true
fail_under = 80
```

---

## 6. DJANGO CONFIG

For Django projects.

```toml
# Test Dependencies
[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
    "pytest-django>=4.5.0,<5.0.0",
    "pytest-mock>=3.11.0,<4.0.0",
]

# Pytest Configuration
[tool.pytest.ini_options]
DJANGO_SETTINGS_MODULE = "config.settings.test"
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]

addopts = [
    "--verbose",
    "--strict-markers",
    "--tb=short",
]

markers = [
    "unit: Unit tests",
    "integration: Integration tests",
    "db: Database tests",
    "slow: Slow tests",
]

# Coverage Configuration
[tool.coverage.run]
source = ["app"]
omit = [
    "*/tests/*",
    "*/migrations/*",
    "*/manage.py",
]
branch = true

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise NotImplementedError",
    "if __name__ == .__main__.:",
    "if TYPE_CHECKING:",
]
show_missing = true
fail_under = 80
```

---

## 7. WEB/FRONTEND CONFIG

For JavaScript/TypeScript projects (use Jest instead, but included for reference).

```toml
# For Python backend tests alongside frontend

[project.optional-dependencies]
test = [
    "pytest>=7.4.0,<9.0.0",
    "pytest-cov>=4.1.0,<5.0.0",
]

[tool.pytest.ini_options]
testpaths = ["tests/backend"]
python_files = ["test_*.py", "*_test.py"]
addopts = "--verbose --tb=short"

[tool.coverage.run]
source = ["src/backend"]
omit = ["*/tests/*", "*/venv/*"]
branch = true

[tool.coverage.report]
show_missing = true
fail_under = 80
```

---

## Tier-Based Configurations

### Change fail_under Based on Repository Tier

**Tier 1 (Work/Production)**: Use `fail_under = 85`
```toml
[tool.coverage.report]
fail_under = 85
```

Examples: digitalmodel, energy, frontierdeepwater, aceengineercode

**Tier 2 (Active Development)**: Use `fail_under = 80`
```toml
[tool.coverage.report]
fail_under = 80
```

Examples: aceengineer-website, hobbies, sd-work

**Tier 3 (Maintenance)**: Use `fail_under = 80`
```toml
[tool.coverage.report]
fail_under = 80
```

Examples: doris, saipem, OGManufacturing

---

## Quick Integration Steps

1. **Choose your config** from above (minimal, standard, advanced, etc.)
2. **Copy the entire config** into your `pyproject.toml`
3. **Adjust `fail_under`** based on your repository tier
4. **Install dependencies**: `uv pip install -e ".[test]"`
5. **Run tests**: `pytest --cov`
6. **Generate report**: `pytest --cov --cov-report=html`

---

## Common Customizations

### Change test directory name
```toml
testpaths = ["test"]  # Instead of "tests"
```

### Change source directory name
```toml
[tool.coverage.run]
source = ["lib", "app"]  # Instead of "src"
```

### Skip coverage for specific files
```toml
[tool.coverage.run]
omit = [
    "*/tests/*",
    "*/__init__.py",
    "*/settings.py",
    "*/config.py",
]
```

### Exclude more lines from coverage
```toml
[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    # Add more patterns here
]
```

### Stricter coverage threshold
```toml
[tool.coverage.report]
fail_under = 90  # Very strict
```

---

## Testing Commands for Each Config

### Minimal Config
```bash
pytest                              # Run all tests
pytest --cov                        # With coverage
pytest --cov --cov-report=html     # HTML report
```

### Standard Config
```bash
pytest                              # Run all tests
pytest -m unit                      # Unit tests only
pytest -m "not slow"                # Skip slow tests
pytest --cov --cov-report=html     # HTML coverage
pytest --asyncio-mode auto         # Async tests
```

### Advanced Config
```bash
pytest                              # Run all tests
pytest -n auto                      # Parallel (4 cores)
pytest -m benchmark --benchmark-only  # Benchmarks
pytest -m property                  # Property tests
pytest --cov --cov-report=xml      # XML for CI/CD
```

---

**Tip**: Save this file locally for quick reference when setting up new repositories!
