# Quick Start: Unified Test Runner

> **5-minute setup and first run**

## Installation (2 minutes)

```bash
# 1. Ensure pytest and dependencies are installed
pip install pytest pytest-cov pytest-xdist uv

# 2. Navigate to workspace-hub
cd /mnt/github/workspace-hub

# 3. Create output directory
mkdir -p reports/test-results
```

## First Run (3 minutes)

### Test One Repository

```bash
python scripts/testing/unified_test_runner.py --repos digitalmodel
```

**Output:**
```
2025-01-13 22:36:45 - __main__ - INFO - Discovered 25 local repositories
2025-01-13 22:36:45 - __main__ - INFO - Testing 1 repositories
2025-01-13 22:36:45 - __main__ - INFO - Starting parallel test execution
...
✓ digitalmodel - 45 passed, 0 failed, 85.2% coverage

HTML report: reports/test-results/report_20250113_223645.html
JSON report: reports/test-results/results_20250113_223645.json
```

### Test Multiple Repositories

```bash
python scripts/testing/unified_test_runner.py --repos digitalmodel energy aceengineer-admin
```

### Test All Work Repositories

```bash
python scripts/testing/unified_test_runner.py --work-only
```

## View Results

```bash
# Open HTML report in browser
open reports/test-results/report_*.html

# Or view JSON results
cat reports/test-results/results_*.json | python -m json.tool
```

## Common Tasks

### Run Tests with Progress Tracking

```bash
python scripts/testing/unified_test_runner.py --verbose
```

### Increase Parallel Workers

```bash
# Default: 5 repositories at a time
# Increase to 10:
python scripts/testing/unified_test_runner.py --workers 10
```

### Test Only Personal Repos

```bash
python scripts/testing/unified_test_runner.py --personal-only
```

### Create Custom Report Location

```bash
python scripts/testing/unified_test_runner.py \
  --output ./my-test-results \
  --repos digitalmodel
```

## Next Steps

1. **Read Full Documentation:**
   ```bash
   cat docs/modules/testing/UNIFIED_TEST_RUNNER.md
   ```

2. **Integrate with CI/CD:**
   - Add to GitHub Actions workflow
   - Add to pre-commit hook
   - Add to release pipeline

3. **Monitor Results:**
   - Parse JSON output
   - Send metrics to monitoring service
   - Create custom dashboards

4. **Customize for Your Repos:**
   - Edit pytest.ini in each repository
   - Configure coverage targets
   - Add performance markers

## Troubleshooting

### "pytest: command not found"

```bash
pip install pytest pytest-cov pytest-xdist
```

### "No repositories found"

```bash
# Check repos exist locally
ls /mnt/github/workspace-hub/digitalmodel

# Clone if missing
python scripts/repository_sync.py clone work
```

### Tests won't run

```bash
# Check repository has tests
ls /mnt/github/workspace-hub/[repo-name]/tests/

# Run with verbose to see errors
python scripts/testing/unified_test_runner.py --repos [repo-name] --verbose
```

---

**Ready to test! 🚀**
