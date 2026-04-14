# Unified Test Runner - Examples & Recipes

> **Real-world usage examples and integration patterns**

## Example 1: Basic Test Run

### Command

```bash
python scripts/testing/unified_test_runner.py --repos digitalmodel energy
```

### Expected Output

```
2025-01-13 22:36:45,123 - __main__ - INFO - Discovering local repositories
2025-01-13 22:36:45,456 - __main__ - INFO - Discovered 25 local repositories
2025-01-13 22:36:45,789 - __main__ - INFO - Testing 2 repositories
2025-01-13 22:36:45,890 - __main__ - INFO - Starting parallel test execution for 2 repositories
2025-01-13 22:36:45,991 - __main__ - INFO - Max workers: 5

2025-01-13 22:36:48,123 - __main__ - INFO - [1/2 50%] ✓ digitalmodel - 45 passed, 0 failed, 85.2% coverage
2025-01-13 22:36:52,456 - __main__ - INFO - [2/2 100%] ✓ energy - 32 passed, 0 failed, 78.5% coverage

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

## Example 2: Full Work Repository Suite

### Command

```bash
python scripts/testing/unified_test_runner.py --work-only --workers 8 --verbose
```

### Key Features

- Tests all work repositories
- 8 parallel repository executions
- Verbose output with detailed logging

### Expected Summary

```
Total Repositories: 15
Successful: 14 | Failed: 0 | Error: 1 | Skipped: 0
Total Tests: 1,250
Passed: 1,230 | Failed: 20 | Skipped: 5
Pass Rate: 98.4%
Average Coverage: 82.5%
Total Execution Time: 342.5s (5.7 minutes)
```

### Error Handling Example

Even with 1 error repository, the runner continues:

```
✓ digitalmodel - 45 passed, 0 failed, 85.2% coverage
✓ energy - 32 passed, 0 failed, 78.5% coverage
✗ frontierdeepwater - 10 passed, 2 failed, 75.3% coverage
✓ rock-oil-field - 28 passed, 0 failed, 82.1% coverage
⚠ worldenergydata - Environment setup failed
```

## Example 3: CI/CD Integration

### GitHub Actions Workflow

```yaml
name: Unified Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

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
          pip install pytest pytest-cov pytest-xdist uv

      - name: Run Unified Tests
        run: |
          python scripts/testing/unified_test_runner.py \
            --work-only \
            --workers 8 \
            --output ./test-results

      - name: Upload Results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: test-results/

      - name: Comment on PR
        if: github.event_name == 'pull_request'
        uses: actions/github-script@v6
        with:
          script: |
            const fs = require('fs');
            const results = JSON.parse(fs.readFileSync('./test-results/results_*.json', 'utf8'));
            const comment = `
              ## Test Results
              - **Repositories:** ${results.summary.total_repos}
              - **Success Rate:** ${results.summary.repo_success_rate.toFixed(1)}%
              - **Tests:** ${results.summary.total_passed}/${results.summary.total_tests} passed
              - **Coverage:** ${results.summary.average_coverage.toFixed(1)}%
            `;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: comment
            });
```

### Jenkins Pipeline

```groovy
pipeline {
    agent any

    stages {
        stage('Setup') {
            steps {
                sh '''
                    pip install pytest pytest-cov pytest-xdist uv
                    mkdir -p reports/test-results
                '''
            }
        }

        stage('Test') {
            steps {
                sh '''
                    python scripts/testing/unified_test_runner.py \
                        --work-only \
                        --workers 8 \
                        --output reports/test-results
                '''
            }
        }

        stage('Report') {
            steps {
                publishHTML([
                    reportDir: 'reports/test-results',
                    reportFiles: 'report_*.html',
                    reportName: 'Test Results'
                ])

                junit 'reports/test-results/*/junit.xml'
            }
        }
    }

    post {
        always {
            archiveArtifacts artifacts: 'reports/test-results/**',
                            allowEmptyArchive: true
        }
    }
}
```

## Example 4: Pre-commit Hook Integration

### Hook Script

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Run quick tests on changed repositories
CHANGED_FILES=$(git diff --cached --name-only)
CHANGED_REPOS=$(echo "$CHANGED_FILES" | cut -d'/' -f1 | sort -u)

if [ -z "$CHANGED_REPOS" ]; then
    exit 0
fi

echo "Running tests on changed repositories..."
python scripts/testing/unified_test_runner.py --repos $CHANGED_REPOS

if [ $? -ne 0 ]; then
    echo "Tests failed. Commit aborted."
    exit 1
fi

exit 0
```

### Installation

```bash
cp scripts/testing/hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
```

## Example 5: Custom Report Processing

### Extract Coverage Metrics

```python
#!/usr/bin/env python3
import json
from pathlib import Path

# Load results
results_file = Path('reports/test-results/results_*.json')
results = json.loads(results_file.read_text())

# Extract coverage data
for repo in results['results']:
    if repo['status'] == 'success':
        print(f"{repo['repo_name']}: {repo['coverage_percent']:.1f}%")

# Calculate average
avg_coverage = results['summary']['average_coverage']
print(f"\nAverage coverage: {avg_coverage:.1f}%")

# Alert if below threshold
if avg_coverage < 80:
    print("⚠️  Coverage below target (80%)")
```

### Send Metrics to Monitoring Service

```python
#!/usr/bin/env python3
import json
import requests
from pathlib import Path

# Load results
results = json.loads(Path('reports/test-results/results_*.json').read_text())

# Send to monitoring service
metrics = {
    'timestamp': results['timestamp'],
    'total_repos': results['summary']['total_repos'],
    'success_rate': results['summary']['repo_success_rate'],
    'test_pass_rate': results['summary']['success_rate'],
    'average_coverage': results['summary']['average_coverage'],
    'total_tests': results['summary']['total_tests'],
}

response = requests.post(
    'https://monitoring.example.com/api/metrics',
    json=metrics,
    headers={'Authorization': 'Bearer TOKEN'}
)

print(f"Metrics sent: {response.status_code}")
```

## Example 6: Performance Monitoring

### Track Test Execution Time Trends

```python
#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime

results_dir = Path('reports/test-results')

# Aggregate results from multiple runs
execution_times = {}

for results_file in sorted(results_dir.glob('results_*.json')):
    data = json.loads(results_file.read_text())

    for repo in data['results']:
        repo_name = repo['repo_name']
        if repo_name not in execution_times:
            execution_times[repo_name] = []

        execution_times[repo_name].append({
            'timestamp': data['timestamp'],
            'time': repo['execution_time']
        })

# Detect performance regressions
for repo, times in execution_times.items():
    if len(times) >= 2:
        latest = times[-1]['time']
        average = sum(t['time'] for t in times[:-1]) / (len(times) - 1)
        regression = ((latest - average) / average) * 100

        if regression > 20:
            print(f"⚠️  {repo}: +{regression:.1f}% slower ({latest:.1f}s vs {average:.1f}s avg)")
        elif regression < -20:
            print(f"✓ {repo}: -{abs(regression):.1f}% faster ({latest:.1f}s vs {average:.1f}s avg)")
```

## Example 7: Selective Testing by Category

### Test Only High-Priority Repositories

```bash
# Test only production-critical work repositories
python scripts/testing/unified_test_runner.py \
    --repos digitalmodel energy frontierdeepwater \
    --workers 4 \
    --verbose
```

### Test Only Modified Repositories

```bash
#!/bin/bash
# test-changed.sh

CHANGED=$(git diff main...HEAD --name-only | cut -d'/' -f1 | sort -u)

if [ -z "$CHANGED" ]; then
    echo "No changes detected"
    exit 0
fi

python scripts/testing/unified_test_runner.py --repos $CHANGED
```

### Test by Size Category

```bash
# Test only small/fast repositories
python scripts/testing/unified_test_runner.py \
    --repos hobbies investments sabithaandkrishnaestates \
    --workers 10

# Test larger repositories with fewer workers
python scripts/testing/unified_test_runner.py \
    --repos digitalmodel energy frontierdeepwater \
    --workers 3
```

## Example 8: Debugging Failed Tests

### Capture Full Test Output

```bash
# Run with verbose output to see all details
python scripts/testing/unified_test_runner.py \
    --repos problem-repo \
    --verbose

# Check detailed test log
cat reports/test-results/problem-repo/test.log

# View JUnit XML for failure details
cat reports/test-results/problem-repo/junit.xml
```

### Re-run Specific Test

```bash
cd /mnt/github/workspace-hub/problem-repo

# Activate environment
source .venv/bin/activate

# Run specific test with full output
pytest tests/ -vv --tb=long -k "test_failing_function"
```

## Example 9: Reporting & Analytics

### Generate Weekly Test Report

```bash
#!/bin/bash
# generate-weekly-report.sh

WEEK=$(date +%Y-W%V)
REPORT_DIR="reports/weekly/${WEEK}"

mkdir -p "${REPORT_DIR}"

python scripts/testing/unified_test_runner.py \
    --output "${REPORT_DIR}" \
    --work-only

# Generate summary
echo "## Weekly Test Report - ${WEEK}" > "${REPORT_DIR}/README.md"
echo "" >> "${REPORT_DIR}/README.md"

# Extract key metrics
python3 << 'EOF'
import json
from pathlib import Path

results = json.loads(Path("${REPORT_DIR}/results_*.json").read_text())
summary = results['summary']

print(f"- Total Repositories: {summary['total_repos']}")
print(f"- Success Rate: {summary['repo_success_rate']:.1f}%")
print(f"- Average Coverage: {summary['average_coverage']:.1f}%")
print(f"- Total Tests: {summary['total_tests']}")
EOF
```

## Example 10: Custom Test Configuration

### Repository-Specific Overrides

**Project A (pyproject.toml):**
```toml
[tool.pytest.ini_options]
testpaths = ["tests"]
addopts = "-ra --strict-markers -n auto"
minversion = "6.0"
```

**Project B (pytest.ini):**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
addopts = -ra --tb=short --disable-warnings
markers =
    slow: marks tests as slow
    db: marks tests as database tests
```

Both will be respected by the unified test runner!

---

**Ready for advanced usage! 🚀**
