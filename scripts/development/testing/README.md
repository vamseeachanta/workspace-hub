# Unified Test Runner - Production Test Orchestration

> **Parallel pytest execution across 25+ Python repositories**
>
> Status: ✅ Production Ready | Version: 1.0.0 | Lines: 1,052

## Quick Overview

The Unified Test Runner orchestrates parallel pytest execution across multiple repositories with professional reporting, coverage aggregation, and CI/CD integration.

```bash
# Basic usage
python unified_test_runner.py

# Test work repositories only
python unified_test_runner.py --work-only

# Test specific repositories
python unified_test_runner.py --repos digitalmodel energy

# With verbose output
python unified_test_runner.py --verbose
```

## Key Features

✅ **Parallel Execution** - Run 5 repositories simultaneously
✅ **Automatic Environments** - UV-based virtual environment setup
✅ **Coverage Aggregation** - pytest-cov with JSON output
✅ **Professional Reports** - HTML with metrics + JUnit XML
✅ **Real-Time Monitoring** - Progress indicators with status table
✅ **Error Resilience** - Continues on failures, captures all metrics
✅ **CI/CD Ready** - JSON export for programmatic integration

## Installation

```bash
# Install dependencies
pip install pytest pytest-cov pytest-xdist uv

# Create output directory
mkdir -p reports/test-results

# Script is ready to use!
python unified_test_runner.py
```

## Files

| File | Purpose | Size |
|------|---------|------|
| `unified_test_runner.py` | Main script | 1,052 lines |
| `../docs/testing/UNIFIED_TEST_RUNNER.md` | Complete guide | 400+ lines |
| `../docs/testing/QUICK_START_TEST_RUNNER.md` | Quick start | 80 lines |
| `../docs/testing/TEST_RUNNER_EXAMPLES.md` | 10 examples | 400+ lines |

## Architecture

### Components

```
unified_test_runner.py
├── Data Classes
│   ├── TestResult (individual repo metrics)
│   └── AggregatedResults (unified metrics)
├── Repository Management
│   ├── load_repository_config() - Load from repos.conf
│   ├── filter_repositories() - Filter by criteria
│   └── has_tests() - Check for test presence
├── Environment Setup
│   └── setup_environment() - Create UV venv + install
├── Test Execution
│   ├── run_tests() - Execute pytest for single repo
│   ├── _parse_junit_xml() - Extract test metrics
│   └── _parse_coverage_json() - Extract coverage
├── Orchestration
│   ├── execute_tests_parallel() - ProcessPoolExecutor
│   └── _print_progress() - Real-time indicators
└── Report Generation
    ├── generate_html_report() - Professional HTML
    ├── save_json_results() - Machine-readable JSON
    └── main() - CLI entry point
```

### Execution Flow

```
1. Load repos from config
   ↓
2. Filter by criteria
   ↓
3. Check for tests
   ↓
4. Setup environments (parallel)
   ↓
5. Execute pytest (parallel, max 5 repos)
   ├─ Test discovery & execution
   ├─ Coverage collection
   └─ JUnit XML generation
   ↓
6. Parse results
   ├─ Extract from JUnit XML
   └─ Extract from coverage JSON
   ↓
7. Generate reports
   ├─ Aggregate HTML report
   └─ Per-repo JSON results
```

## Usage Examples

### Test Single Repository
```bash
python unified_test_runner.py --repos digitalmodel
```

### Test Multiple Repositories
```bash
python unified_test_runner.py --repos digitalmodel energy aceengineer-admin
```

### Test All Work Repositories
```bash
python unified_test_runner.py --work-only
```

### Test All Personal Repositories
```bash
python unified_test_runner.py --personal-only
```

### Increase Parallelization
```bash
python unified_test_runner.py --workers 10
```

### Verbose Output
```bash
python unified_test_runner.py --verbose
```

### Custom Output Directory
```bash
python unified_test_runner.py --output ./my-results
```

## Output

### HTML Report
Professional report with metrics, status table, and visualizations
- Location: `reports/test-results/report_YYYYMMDD_HHMMSS.html`
- Features: Gradient header, metrics grid, interactive table

### JSON Results
Machine-readable results for programmatic integration
- Location: `reports/test-results/results_YYYYMMDD_HHMMSS.json`
- Includes: Summary metrics, per-repo details, timestamps

### Per-Repository Outputs
```
reports/test-results/[repo-name]/
├── junit.xml        # JUnit test results (CI/CD compatible)
├── coverage.json    # Coverage metrics JSON
└── test.log        # Full pytest execution log
```

## Example Output

```
2025-01-13 22:36:45 - __main__ - INFO - Starting parallel test execution for 2 repositories
2025-01-13 22:36:48 - __main__ - INFO - [1/2 50%] ✓ digitalmodel - 45 passed, 0 failed, 85.2% coverage
2025-01-13 22:36:52 - __main__ - INFO - [2/2 100%] ✓ energy - 32 passed, 0 failed, 78.5% coverage

================================================================================
TEST EXECUTION SUMMARY
================================================================================
Total Repositories: 2
Successful: 2 | Failed: 0 | Error: 0 | Skipped: 0
Total Tests: 77
Passed: 77 | Failed: 0 | Skipped: 0
Pass Rate: 100.0%
Average Coverage: 81.9%
Total Execution Time: 6.3s

Reports generated:
  HTML: reports/test-results/report_20250113_223615.html
  JSON: reports/test-results/results_20250113_223615.json
================================================================================
```

## CLI Options

```
usage: unified_test_runner.py [-h] [--config CONFIG] [--output OUTPUT]
                              [--workers WORKERS] [--repos REPOS [REPOS ...]]
                              [--work-only] [--personal-only] [--verbose]

options:
  -h, --help            show this help message and exit
  --config CONFIG       Path to repos.conf (default: config/repos.conf)
  --output OUTPUT       Output directory for results (default: reports/test-results)
  --workers WORKERS     Maximum parallel repositories (default: 5)
  --repos REPOS [REPOS ...]
                        Specific repositories to test
  --work-only           Test work repositories only
  --personal-only       Test personal repositories only
  --verbose, -v         Enable verbose output
```

## Integration Examples

### GitHub Actions
```yaml
- name: Run Unified Tests
  run: |
    python scripts/testing/unified_test_runner.py \
      --work-only \
      --workers 8 \
      --output ./test-results
```

### Jenkins
```groovy
stage('Test') {
    steps {
        sh '''
            python scripts/testing/unified_test_runner.py \
                --work-only \
                --workers 8
        '''
    }
}
```

### Pre-commit Hook
```bash
#!/bin/bash
python scripts/testing/unified_test_runner.py
if [ $? -ne 0 ]; then exit 1; fi
```

## Troubleshooting

### "pytest: command not found"
```bash
pip install pytest pytest-cov pytest-xdist
```

### "No repositories found"
```bash
# Ensure repos exist locally
ls /mnt/github/workspace-hub/digitalmodel
```

### "Tests timeout"
Check logs for slow tests:
```bash
cat reports/test-results/[repo]/test.log
```

### "Environment setup failed"
Check UV and pyproject.toml:
```bash
uv --version
cd [repo] && ls pyproject.toml
```

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Env setup | ~30s | Per repo, first run only |
| Test execution | 5-20s | Per repo, varies by test count |
| Parallel batch (5) | 30-60s | Slowest repo determines |
| Full 25-repo suite | 15-30 min | Includes all setup |
| Report generation | 1-2s | Pure Python |

## Requirements

- Python 3.9+
- pip or uv (package manager)
- pytest, pytest-cov, pytest-xdist
- UV (for environment management)

## Documentation

- **Complete Guide:** `../docs/testing/UNIFIED_TEST_RUNNER.md`
- **Quick Start:** `../docs/testing/QUICK_START_TEST_RUNNER.md`
- **Examples:** `../docs/testing/TEST_RUNNER_EXAMPLES.md`
- **Implementation:** `../docs/testing/IMPLEMENTATION_SUMMARY.md`

## Related Tools

- `repository_sync` - Multi-repository git operations
- `refactor-analysis.sh` - Code quality analysis
- `workspace` CLI - Unified workspace management

## Support

For help, see the documentation or run:
```bash
python unified_test_runner.py --help
```

## Version History

- **1.0.0** (2025-01-13) - Initial release with full feature set

---

**Production-ready multi-repository test orchestration! 🚀**
