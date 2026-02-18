# Pytest Integration Guide

## Overview

This guide covers integrating the Test Framework Integrations system with Pytest for Python testing environments. The integration provides unified test execution, baseline tracking, and comprehensive reporting for Python projects.

## Installation

### Prerequisites

- Python 3.7+ with pip
- Node.js 16+ (for the integration system)
- Pytest 6.0+

### Install Dependencies

```bash
# Install the integration system
npm install test-framework-integrations

# Install Python dependencies
pip install pytest pytest-json-report pytest-html pytest-cov
```

### Optional Dependencies

For enhanced functionality:

```bash
# Performance monitoring
pip install pytest-benchmark pytest-profiling

# Parallel execution
pip install pytest-xdist

# Mocking support
pip install pytest-mock

# Advanced reporting
pip install pytest-metadata pytest-emoji
```

## Basic Configuration

### pytest.ini Configuration

```ini
[tool:pytest]
# Test discovery
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*

# Output formatting
addopts =
    --json-report
    --json-report-file=test-results.json
    --html=reports/report.html
    --self-contained-html
    --cov=src
    --cov-report=html:reports/coverage
    --cov-report=json:coverage.json
    --strict-markers
    -v

# Markers for test categorization
markers =
    unit: Unit tests
    integration: Integration tests
    e2e: End-to-end tests
    slow: Slow running tests
    performance: Performance tests
    smoke: Smoke tests
```

### Integration Configuration

Create `test-integration.config.js`:

```javascript
module.exports = {
  framework: 'pytest',
  testCommand: 'python -m pytest',
  testDir: 'tests',
  outputDir: 'test-results',

  // Pytest-specific settings
  pythonPath: process.env.PYTHON_PATH || 'python',
  virtualEnv: process.env.VIRTUAL_ENV,

  // Result parsing
  resultFile: 'test-results.json',
  coverageFile: 'coverage.json',

  // Baseline configuration
  baseline: {
    enabled: true,
    directory: 'baselines',
    autoSave: true,
    compareThreshold: 0.05
  },

  // Performance monitoring
  performance: {
    enabled: true,
    thresholds: {
      testDuration: 30000,
      totalDuration: 300000,
      memoryUsage: 512 * 1024 * 1024
    }
  },

  // Reporting
  reporting: {
    formats: ['json', 'html', 'junit'],
    includeSkipped: true,
    includePending: false
  }
};
```

## Advanced Configuration

### Custom Pytest Plugin

Create `conftest.py` for advanced integration:

```python
import pytest
import json
import time
import psutil
import os
from datetime import datetime

# Global test metadata
test_session_data = {
    'start_time': None,
    'tests': [],
    'performance': {},
    'environment': {}
}

@pytest.fixture(scope='session', autouse=True)
def test_session_setup():
    """Setup test session with integration system."""
    global test_session_data

    test_session_data['start_time'] = datetime.now().isoformat()
    test_session_data['environment'] = {
        'python_version': os.sys.version,
        'platform': os.name,
        'working_directory': os.getcwd(),
        'virtual_env': os.environ.get('VIRTUAL_ENV'),
        'cpu_count': os.cpu_count(),
        'memory_total': psutil.virtual_memory().total
    }

    yield

    # Save session data
    with open('test-session.json', 'w') as f:
        json.dump(test_session_data, f, indent=2)

@pytest.fixture(autouse=True)
def test_performance_monitor(request):
    """Monitor individual test performance."""
    start_time = time.time()
    start_memory = psutil.Process().memory_info().rss

    yield

    end_time = time.time()
    end_memory = psutil.Process().memory_info().rss

    duration = end_time - start_time
    memory_delta = end_memory - start_memory

    test_data = {
        'name': request.node.name,
        'file': str(request.node.fspath),
        'duration': duration,
        'memory_usage': memory_delta,
        'timestamp': datetime.now().isoformat()
    }

    test_session_data['tests'].append(test_data)

@pytest.hookimpl(tryfirst=True)
def pytest_configure(config):
    """Configure pytest with integration settings."""
    # Add custom markers
    config.addinivalue_line(
        "markers", "baseline: Mark test for baseline comparison"
    )
    config.addinivalue_line(
        "markers", "performance: Mark test for performance tracking"
    )

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Generate enhanced test reports."""
    outcome = yield
    report = outcome.get_result()

    # Add custom attributes
    if hasattr(item, 'performance_data'):
        report.performance = item.performance_data

    if hasattr(item, 'baseline_data'):
        report.baseline = item.baseline_data

class PerformanceCollector:
    """Collect performance metrics during test execution."""

    def __init__(self):
        self.metrics = {}

    def start_collection(self, test_name):
        self.metrics[test_name] = {
            'start_time': time.time(),
            'start_memory': psutil.Process().memory_info().rss,
            'start_cpu': psutil.cpu_percent()
        }

    def end_collection(self, test_name):
        if test_name in self.metrics:
            metrics = self.metrics[test_name]
            metrics.update({
                'end_time': time.time(),
                'end_memory': psutil.Process().memory_info().rss,
                'end_cpu': psutil.cpu_percent()
            })

            # Calculate deltas
            metrics['duration'] = metrics['end_time'] - metrics['start_time']
            metrics['memory_delta'] = metrics['end_memory'] - metrics['start_memory']

            return metrics

        return None

# Global performance collector
performance_collector = PerformanceCollector()
```

### Integration with Test Framework Integrations

Create `run-tests.js`:

```javascript
const TestFrameworkIntegrations = require('test-framework-integrations');
const fs = require('fs');
const path = require('path');

class PytestIntegration {
  constructor(config) {
    this.config = config;
    this.integration = new TestFrameworkIntegrations(config);
  }

  async runTests(options = {}) {
    try {
      // Initialize integration
      await this.integration.initialize();

      // Build pytest command
      const command = this.buildPytestCommand(options);

      // Run tests through integration system
      const results = await this.integration.runTests({
        command,
        framework: 'pytest',
        ...options
      });

      // Process Python-specific results
      await this.processResults(results);

      return results;
    } catch (error) {
      console.error('Pytest integration error:', error);
      throw error;
    }
  }

  buildPytestCommand(options) {
    const baseCommand = [this.config.pythonPath, '-m', 'pytest'];

    // Add test paths
    if (options.testPaths) {
      baseCommand.push(...options.testPaths);
    } else {
      baseCommand.push(this.config.testDir);
    }

    // Add markers
    if (options.markers) {
      baseCommand.push('-m', options.markers);
    }

    // Add coverage
    if (options.coverage !== false) {
      baseCommand.push('--cov=src', '--cov-report=json');
    }

    // Add performance monitoring
    if (options.performance) {
      baseCommand.push('--benchmark-json=benchmark.json');
    }

    // Add parallel execution
    if (options.parallel) {
      baseCommand.push('-n', options.parallel.toString());
    }

    // Add output format
    baseCommand.push(
      '--json-report',
      `--json-report-file=${this.config.resultFile}`
    );

    return baseCommand.join(' ');
  }

  async processResults(results) {
    // Load pytest JSON results
    const pytestResults = await this.loadPytestResults();

    // Merge with integration results
    results.pytest = pytestResults;

    // Process coverage data
    if (fs.existsSync('coverage.json')) {
      results.coverage = JSON.parse(fs.readFileSync('coverage.json', 'utf8'));
    }

    // Process performance data
    if (fs.existsSync('benchmark.json')) {
      results.performance = JSON.parse(fs.readFileSync('benchmark.json', 'utf8'));
    }

    // Process session data
    if (fs.existsSync('test-session.json')) {
      results.session = JSON.parse(fs.readFileSync('test-session.json', 'utf8'));
    }

    return results;
  }

  async loadPytestResults() {
    if (!fs.existsSync(this.config.resultFile)) {
      throw new Error(`Pytest results file not found: ${this.config.resultFile}`);
    }

    const rawResults = JSON.parse(fs.readFileSync(this.config.resultFile, 'utf8'));

    return {
      summary: rawResults.summary,
      tests: rawResults.tests,
      collectors: rawResults.collectors,
      duration: rawResults.duration,
      exitcode: rawResults.exitcode
    };
  }

  async saveBaseline(name, data) {
    return await this.integration.saveBaseline(name, {
      framework: 'pytest',
      timestamp: new Date().toISOString(),
      ...data
    });
  }

  async compareWithBaseline(name, currentData) {
    return await this.integration.compareWithBaseline(name, currentData);
  }
}

module.exports = PytestIntegration;
```

## Usage Examples

### Basic Test Execution

```javascript
const PytestIntegration = require('./run-tests');
const config = require('./test-integration.config');

async function runPytestSuite() {
  const pytest = new PytestIntegration(config);

  try {
    const results = await pytest.runTests({
      testPaths: ['tests/unit', 'tests/integration'],
      markers: 'not slow',
      coverage: true,
      parallel: 4
    });

    console.log('Test Results:', results.summary);
    console.log('Coverage:', results.coverage.totals);

    // Save baseline
    await pytest.saveBaseline('main-branch', results);

  } catch (error) {
    console.error('Test execution failed:', error);
    process.exit(1);
  }
}

runPytestSuite();
```

### Performance Testing

```python
import pytest
import time
import random

@pytest.mark.performance
def test_algorithm_performance():
    """Test algorithm performance with baseline comparison."""

    # Simulate algorithm execution
    start_time = time.time()

    # Your algorithm here
    data = [random.randint(1, 1000) for _ in range(10000)]
    sorted_data = sorted(data)

    end_time = time.time()
    duration = end_time - start_time

    # Performance assertions
    assert duration < 1.0, f"Algorithm too slow: {duration}s"
    assert len(sorted_data) == 10000

    # Store performance data for baseline
    pytest.current_performance = {
        'duration': duration,
        'data_size': len(data),
        'memory_used': len(sorted_data) * 8  # Approximate
    }

@pytest.mark.baseline
def test_api_response_time():
    """Test API response time with baseline tracking."""

    start_time = time.time()

    # Simulate API call
    time.sleep(0.1)  # Mock API delay
    response = {'status': 'success', 'data': [1, 2, 3]}

    end_time = time.time()
    response_time = end_time - start_time

    # Assertions
    assert response['status'] == 'success'
    assert response_time < 0.5

    # Baseline data
    pytest.current_baseline = {
        'response_time': response_time,
        'response_size': len(str(response))
    }
```

### Parameterized Testing with Baselines

```python
import pytest

@pytest.mark.parametrize("input_size,expected_complexity", [
    (100, 0.001),
    (1000, 0.01),
    (10000, 0.1),
])
@pytest.mark.performance
def test_scaling_performance(input_size, expected_complexity):
    """Test algorithm scaling with different input sizes."""

    start_time = time.time()

    # Simulate algorithm
    data = list(range(input_size))
    result = sum(x * x for x in data)

    duration = time.time() - start_time

    # Performance assertion
    assert duration < expected_complexity, f"Performance degraded for size {input_size}"

    # Store metrics
    pytest.current_performance = {
        'input_size': input_size,
        'duration': duration,
        'complexity_ratio': duration / expected_complexity
    }
```

## CI/CD Integration

### GitHub Actions

```yaml
name: Python Tests with Integration

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.8, 3.9, '3.10', 3.11]

    steps:
    - uses: actions/checkout@v4

    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}

    - name: Set up Node.js
      uses: actions/setup-node@v4
      with:
        node-version: '18'

    - name: Install Python dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-json-report pytest-cov pytest-html

    - name: Install integration system
      run: npm install test-framework-integrations

    - name: Run tests with integration
      run: |
        node run-tests.js

    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results-python-${{ matrix.python-version }}
        path: |
          test-results.json
          reports/
          coverage.json

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
      with:
        file: coverage.json
```

### Docker Integration

```dockerfile
# Dockerfile.test
FROM python:3.11-slim

WORKDIR /app

# Install Node.js for integration system
RUN apt-get update && apt-get install -y nodejs npm

# Install Python dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install pytest pytest-json-report pytest-cov pytest-html

# Install integration system
COPY package.json .
RUN npm install

# Copy test configuration
COPY test-integration.config.js .
COPY conftest.py .
COPY run-tests.js .

# Copy source and tests
COPY src/ src/
COPY tests/ tests/

# Run tests
CMD ["node", "run-tests.js"]
```

## Best Practices

### Test Organization

```python
# tests/conftest.py
import pytest
from src.myapp import create_app, db

@pytest.fixture(scope='session')
def app():
    """Create application for testing."""
    app = create_app('testing')
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def baseline_comparison():
    """Fixture for baseline comparison tests."""
    def _compare(test_name, current_data, threshold=0.05):
        # Integration with baseline system
        baseline_data = load_baseline(test_name)
        if baseline_data:
            return compare_with_threshold(baseline_data, current_data, threshold)
        return True

    return _compare
```

### Performance Monitoring

```python
import pytest
import functools
import time
import psutil

def performance_test(max_duration=None, max_memory=None):
    """Decorator for performance testing."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Start monitoring
            start_time = time.time()
            start_memory = psutil.Process().memory_info().rss

            try:
                result = func(*args, **kwargs)
            finally:
                # End monitoring
                end_time = time.time()
                end_memory = psutil.Process().memory_info().rss

                duration = end_time - start_time
                memory_used = end_memory - start_memory

                # Check thresholds
                if max_duration and duration > max_duration:
                    pytest.fail(f"Test exceeded duration limit: {duration:.3f}s > {max_duration}s")

                if max_memory and memory_used > max_memory:
                    pytest.fail(f"Test exceeded memory limit: {memory_used} bytes > {max_memory} bytes")

                # Store performance data
                pytest.current_performance = {
                    'duration': duration,
                    'memory_used': memory_used
                }

            return result
        return wrapper
    return decorator

# Usage
@performance_test(max_duration=1.0, max_memory=50*1024*1024)
def test_heavy_computation():
    """Test that should complete within performance limits."""
    # Your test here
    pass
```

## Troubleshooting

### Common Issues

1. **Module Import Errors**
   ```bash
   # Add project root to Python path
   export PYTHONPATH="${PYTHONPATH}:$(pwd)"

   # Or use pytest's pythonpath option
   pytest --pythonpath=.
   ```

2. **JSON Report Generation**
   ```bash
   # Ensure pytest-json-report is installed
   pip install pytest-json-report

   # Check output directory permissions
   mkdir -p test-results
   chmod 755 test-results
   ```

3. **Coverage Issues**
   ```bash
   # Install coverage dependencies
   pip install pytest-cov coverage

   # Ensure source directory is correct
   pytest --cov=src --cov-report=json
   ```

### Debugging Integration

```python
# Add to conftest.py for debugging
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def debug_integration(request):
    """Debug integration issues."""
    logger.debug(f"Starting test: {request.node.name}")
    yield
    logger.debug(f"Finished test: {request.node.name}")
```

## Advanced Features

### Custom Reporters

```python
# custom_reporter.py
import pytest
import json
from datetime import datetime

class IntegrationReporter:
    """Custom reporter for integration system."""

    def __init__(self, config):
        self.config = config
        self.results = {
            'tests': [],
            'summary': {},
            'metadata': {
                'timestamp': datetime.now().isoformat(),
                'framework': 'pytest'
            }
        }

    def pytest_runtest_logreport(self, report):
        """Log test results."""
        if report.when == 'call':
            test_result = {
                'name': report.nodeid,
                'outcome': report.outcome,
                'duration': getattr(report, 'duration', 0),
                'file': str(report.fspath),
                'lineno': report.lineno
            }

            # Add performance data if available
            if hasattr(report, 'performance'):
                test_result['performance'] = report.performance

            # Add baseline data if available
            if hasattr(report, 'baseline'):
                test_result['baseline'] = report.baseline

            self.results['tests'].append(test_result)

    def pytest_sessionfinish(self, session):
        """Generate final report."""
        self.results['summary'] = {
            'total': len(self.results['tests']),
            'passed': len([t for t in self.results['tests'] if t['outcome'] == 'passed']),
            'failed': len([t for t in self.results['tests'] if t['outcome'] == 'failed']),
            'skipped': len([t for t in self.results['tests'] if t['outcome'] == 'skipped'])
        }

        # Save results
        with open('integration-report.json', 'w') as f:
            json.dump(self.results, f, indent=2)

# Register plugin
pytest_plugins = ['custom_reporter']
```

This comprehensive Pytest integration guide provides everything needed to integrate Pytest with the Test Framework Integrations system, including advanced configuration, performance monitoring, CI/CD integration, and troubleshooting guidance.