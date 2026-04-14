# Unified Test Runner - Multi-Repository Pytest Orchestrator

> **Version:** 1.0.0
> **Created:** 2025-01-13
> **Status:** Production-ready
> **Language:** Python 3.9+

## Overview

The Unified Test Runner is a production-grade Python script that orchestrates parallel pytest execution across 25+ independent Git repositories with the following capabilities:

- **Parallel Execution:** Run tests on 5 repositories simultaneously (configurable)
- **Isolated Environments:** UV-based virtual environment creation per repository
- **Comprehensive Reporting:** Aggregated HTML coverage reports + per-repo JUnit XML
- **Real-Time Monitoring:** Progress indicators with status table
- **Error Resilience:** Continues execution on failures, captures all metrics
- **CI/CD Ready:** JSON output format for programmatic integration

## Architecture

### Core Components

```python
TestResult              # Individual repository test metrics
AggregatedResults       # Unified metrics across all repos
Repository Discovery   # Load from repos.conf
Environment Setup      # UV virtual environment creation
Test Execution        # Pytest with xdist parallelization
Report Generation     # HTML + JSON output formats
```

### Execution Flow

```
1. Load Repository Configuration (repos.conf)
2. Filter by criteria (work/personal/specific)
3. Check for tests in each repository
4. Setup UV environments (parallel)
   ↓
5. Execute pytest (parallel, max 5 repos)
   - Test discovery and execution
   - Coverage collection (pytest-cov)
   - JUnit XML generation
   ↓
6. Parse Results
   - Extract metrics from JUnit XML
   - Extract coverage from JSON
   ↓
7. Generate Reports
   - Aggregate HTML report
   - Per-repo JSON results
```

## Installation & Setup

### Prerequisites

```bash
# Required system packages
python3.9+
pip or uv (package manager)

# Required Python packages
pip install pytest pytest-cov pytest-xdist
```

### Quick Setup

```bash
# 1. Navigate to workspace root
cd /mnt/github/workspace-hub

# 2. Install dependencies globally
pip install pytest pytest-cov pytest-xdist

# 3. Make script executable (already done)
chmod +x scripts/testing/unified_test_runner.py

# 4. Create output directory
mkdir -p reports/test-results
```

## Usage

### Basic Commands

```bash
# Run tests on all repositories
python scripts/testing/unified_test_runner.py

# Run tests on work repositories only
python scripts/testing/unified_test_runner.py --work-only

# Run tests on specific repositories
python scripts/testing/unified_test_runner.py --repos digitalmodel energy aceengineer-admin

# Run with custom worker count
python scripts/testing/unified_test_runner.py --workers 10

# Verbose output
python scripts/testing/unified_test_runner.py --verbose

# Custom output directory
python scripts/testing/unified_test_runner.py --output ./custom-results
```

### Advanced Usage

```bash
# Test personal repositories with 8 workers
python scripts/testing/unified_test_runner.py --personal-only --workers 8

# Test specific repos with verbose output
python scripts/testing/unified_test_runner.py \
  --repos digitalmodel energy \
  --verbose \
  --workers 3

# Using custom config file
python scripts/testing/unified_test_runner.py \
  --config config/custom-repos.conf \
  --output reports/custom-results
```

## Output & Reports

### Directory Structure

```
reports/test-results/
├── report_20250113_223615.html    # Main aggregated report
├── results_20250113_223615.json   # Machine-readable results
└── [repo_name]/                   # Per-repository results
    ├── junit.xml                  # JUnit test results
    ├── coverage.json              # Coverage metrics
    └── test.log                   # Execution log
```

### HTML Report Features

The generated HTML report includes:

- **Executive Summary:**
  - Total repositories tested
  - Repository success rate
  - Total tests executed
  - Test pass rate
  - Average code coverage
  - Total execution time

- **Interactive Results Table:**
  - Repository name with status indicator
  - Test counts (passed/failed)
  - Code coverage percentage
  - Execution time per repository
  - Sortable and filterable columns

- **Visual Design:**
  - Professional gradient header
  - Color-coded status badges
  - Responsive grid layout
  - Mobile-friendly design

### JSON Results Format

```json
{
  "timestamp": "20250113_223615",
  "summary": {
    "total_repos": 25,
    "successful_repos": 23,
    "failed_repos": 1,
    "error_repos": 1,
    "skipped_repos": 0,
    "total_tests": 1250,
    "total_passed": 1230,
    "total_failed": 20,
    "total_skipped": 5,
    "average_coverage": 82.5,
    "success_rate": 98.4,
    "repo_success_rate": 92.0,
    "total_execution_time": 342.5
  },
  "results": [
    {
      "repo_name": "digitalmodel",
      "repo_path": "/mnt/github/workspace-hub/digitalmodel",
      "status": "success",
      "test_count": 45,
      "passed_count": 45,
      "failed_count": 0,
      "skipped_count": 0,
      "coverage_percent": 85.2,
      "execution_time": 12.4,
      "error_message": null,
      "junit_file": "reports/test-results/digitalmodel/junit.xml",
      "coverage_file": "reports/test-results/digitalmodel/coverage.json",
      "log_file": "reports/test-results/digitalmodel/test.log"
    },
    ...
  ]
}
```

### JUnit XML Output

Each repository generates a standard JUnit XML file compatible with:
- GitHub Actions
- GitLab CI
- Jenkins
- CircleCI
- Azure Pipelines

## Features in Detail

### Parallel Execution with pytest-xdist

The test runner uses pytest-xdist for intelligent parallelization:

```python
# Executes with automatic worker detection
pytest_args = [
    "pytest",
    "tests",
    "-n", "auto",  # xdist parallelization
    ...
]
```

**Benefits:**
- Automatic CPU core detection
- Per-repository test parallelization
- Cross-repository batch parallelization (5 repos max)
- Efficient resource utilization

### UV Environment Management

Automatically creates isolated Python environments per repository:

```bash
# For each repository with pyproject.toml:
uv venv .venv                    # Create virtual environment
uv pip install -e .              # Install package + dependencies
uv pip install pytest pytest-cov  # Install testing tools
```

**Features:**
- Fast environment creation (UV is 10-100x faster than venv)
- Deterministic dependency resolution
- Cached dependency downloads
- Automatic cleanup ready

### Coverage Aggregation

Collects and aggregates coverage metrics:

```python
# Coverage collection strategy:
# 1. Run pytest with coverage collection
pytest_args.extend([
    "--cov",
    f"--cov-report=json:{coverage_file}",
    "--cov-report=json"
])

# 2. Parse JSON output
coverage_data['totals']['percent_covered']

# 3. Aggregate across all repos
average_coverage = sum(coverage_values) / len(coverage_values)
```

### Error Handling & Resilience

The runner continues execution even when repositories fail:

```python
# Status codes:
"success"  # All tests passed
"failed"   # Some tests failed
"error"    # Execution error (env setup, timeout, etc.)
"skipped"  # No tests found

# Continues with next repository on any failure
# Captures error message for debugging
```

## Configuration

### Repository Configuration (repos.conf)

```ini
# Format: repo_name=git_url

# Example entries (auto-populated):
digitalmodel=https://github.com/vamseeachanta/digitalmodel.git
energy=https://github.com/vamseeachanta/energy.git
aceengineer-admin=https://github.com/vamseeachanta/aceengineer-admin

# Only local repositories are tested
# (must exist in workspace-hub directory)
```

### Per-Repository pytest Configuration

Each repository can have its own pytest configuration:

**pyproject.toml:**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py", "*_test.py"]
addopts = "-ra --strict-markers"
markers = [
    "slow: marks tests as slow",
    "integration: marks tests as integration tests",
]
```

**pytest.ini:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
addopts = -ra --strict-markers
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
```

## Examples

### Example 1: Test All Work Repositories

```bash
python scripts/testing/unified_test_runner.py --work-only
```

**Output:**
```
2025-01-13 22:36:45 - __main__ - INFO - Discovered 25 local repositories
2025-01-13 22:36:45 - __main__ - INFO - Testing 15 repositories
2025-01-13 22:36:45 - __main__ - INFO - Starting parallel test execution for 15 repositories
2025-01-13 22:36:45 - __main__ - INFO - Max workers: 5
2025-01-13 22:36:48 - __main__ - INFO - [1/15 7%] ✓ digitalmodel - 45 passed, 0 failed, 85.2% coverage
2025-01-13 22:36:52 - __main__ - INFO - [2/15 13%] ✓ energy - 32 passed, 0 failed, 78.5% coverage
...
```

### Example 2: Test Specific Repositories

```bash
python scripts/testing/unified_test_runner.py \
  --repos digitalmodel energy frontierdeepwater \
  --verbose
```

### Example 3: Integration with CI/CD

```bash
#!/bin/bash
# ci-test-runner.sh

# Run tests
python scripts/testing/unified_test_runner.py \
  --work-only \
  --output ./ci-results \
  --workers 8

# Check results
if [ $? -eq 0 ]; then
  echo "All tests passed!"
  exit 0
else
  echo "Tests failed!"
  exit 1
fi
```

## Troubleshooting

### Issue: "No repositories found"

**Cause:** No local repositories in workspace-hub directory

**Solution:**
```bash
# Clone repositories first
python scripts/repository_sync.py clone work

# Or specify specific repos
python scripts/testing/unified_test_runner.py --repos digitalmodel
```

### Issue: "Environment setup failed"

**Cause:** Missing UV or pyproject.toml issues

**Solution:**
```bash
# Install UV
pip install uv

# Check pyproject.toml validity
cd /path/to/repo
uv venv .venv
uv pip install -e .
```

### Issue: "Tests timeout"

**Default timeout:** 600 seconds per repository

**Solution:**
```bash
# For repositories with slow tests:
# 1. Add markers in pyproject.toml
# 2. Run slow tests separately
python scripts/testing/unified_test_runner.py \
  --repos slow-repo

# With verbose output
python scripts/testing/unified_test_runner.py --verbose
```

### Issue: "Pytest not found in virtual environment"

**Cause:** UV environment not properly created

**Solution:**
```bash
# Manual setup for specific repo
cd /mnt/github/workspace-hub/repo-name
uv venv .venv
uv pip install pytest pytest-cov pytest-xdist

# Re-run test runner
python scripts/testing/unified_test_runner.py --repos repo-name
```

## Performance Characteristics

### Benchmarks

| Metric | Value | Notes |
|--------|-------|-------|
| Environment Setup | ~30s per repo | First time only, cached after |
| Test Execution | ~5-20s per repo | Varies by test count |
| Parallelization | 5 repos / batch | Configurable, CPU-bound |
| Max Batch Time | ~2-3 min | Dependent on slowest repo |
| Report Generation | ~1-2s | Aggregation and HTML rendering |
| Total Run Time | ~15-30 min | For full 25-repo suite |

### Optimization Tips

1. **Increase workers for I/O-bound tests:**
   ```bash
   python scripts/testing/unified_test_runner.py --workers 10
   ```

2. **Use work-only or personal-only to reduce scope:**
   ```bash
   python scripts/testing/unified_test_runner.py --work-only
   ```

3. **Cache UV environments:**
   ```bash
   # Don't delete .venv directories between runs
   ```

4. **Parallelize within repositories:**
   ```toml
   # In pyproject.toml:
   [tool.pytest.ini_options]
   addopts = "-n auto"  # Use all CPU cores
   ```

## Integration Points

### GitHub Actions

```yaml
# .github/workflows/test.yml
- name: Run Unified Tests
  run: |
    python scripts/testing/unified_test_runner.py \
      --work-only \
      --output ./test-results

- name: Upload Results
  uses: actions/upload-artifact@v3
  with:
    name: test-results
    path: test-results/
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Optional: Run quick test on changed repos
python scripts/testing/unified_test_runner.py --verbose
```

### Monitoring Dashboard

```python
# Integrate JSON results into monitoring system
import json

with open('reports/test-results/results_*.json') as f:
    results = json.load(f)

# Send metrics to monitoring service
send_metrics(results['summary'])
```

## Development & Maintenance

### Code Structure

```python
# Core modules:
- TestResult: Data class for individual results
- AggregatedResults: Aggregation and metrics
- Repository management: Discovery, filtering
- Test execution: Run and parse results
- Report generation: HTML and JSON output
```

### Key Functions

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `load_repository_config()` | Load repos from repos.conf | Path | Dict[str, Path] |
| `run_tests()` | Execute tests for one repo | repo_name, path | TestResult |
| `execute_tests_parallel()` | Orchestrate parallel execution | repos, output_dir | AggregatedResults |
| `generate_html_report()` | Create HTML report | results | None (file) |
| `save_json_results()` | Export results as JSON | results | None (file) |

### Extension Points

1. **Add new status types:**
   ```python
   # In TestResult.status
   status: str  # Add new values like "warning", "queued"
   ```

2. **Custom report formats:**
   ```python
   def generate_csv_report(results, output_file):
       # New report format
   ```

3. **Integration with external APIs:**
   ```python
   def upload_results_to_api(results, api_url):
       # Send results to external service
   ```

## Related Documentation

- [Testing Framework Standards](./TESTING_FRAMEWORK_STANDARDS.md)
- [HTML Reporting Standards](../standards/HTML_REPORTING_STANDARDS.md)
- [Repository Sync](../cli/REPOSITORY_SYNC.md)
- [Development Workflow](../workflow/DEVELOPMENT_WORKFLOW.md)

## Support & Issues

### Getting Help

```bash
# View help message
python scripts/testing/unified_test_runner.py --help

# Run with verbose debugging
python scripts/testing/unified_test_runner.py --verbose

# Check logs in per-repo directories
cat reports/test-results/[repo-name]/test.log
```

### Reporting Issues

Include the following when reporting issues:
- Output from `--verbose` flag
- Log files from `reports/test-results/[repo]/test.log`
- Results JSON from `reports/test-results/results_*.json`
- Python version: `python --version`
- UV version: `uv --version`

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-01-13 | Initial release with full feature set |

## License

This tool is part of the workspace-hub project and follows the same license terms.

---

**Production-ready test orchestration for multi-repository Python projects! 🚀**
