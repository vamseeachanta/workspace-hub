# Test Performance Tracking Specification

This document defines the test performance tracking system for @specs/testing/comprehensive-test-plan/spec.md

> Created: 2025-08-19
> Version: 1.0.0

## Overview

Implement comprehensive tracking of test execution performance to identify slowdowns, optimize test suite execution, and maintain fast feedback cycles. The system collects timing data, analyzes trends, and automatically detects performance regressions.

## Performance Metrics to Track

### Primary Metrics

| Metric | Description | Target | Alert Threshold |
|--------|-------------|--------|-----------------|
| Total Test Time | Complete suite execution | < 20 min | > 25 min |
| Unit Test Time | All unit tests | < 5 min | > 7 min |
| Integration Test Time | All integration tests | < 15 min | > 20 min |
| Average Test Time | Per test average | < 0.5s | > 1s |
| Slowest Test | Single slowest test | < 10s | > 15s |
| Setup/Teardown Time | Fixture overhead | < 20% total | > 30% |
| Parallel Efficiency | Speedup from parallelization | > 3x | < 2x |

### Secondary Metrics

| Metric | Description | Tracking Purpose |
|--------|-------------|------------------|
| Test Count | Number of tests | Growth tracking |
| Skip Rate | Tests skipped | Health indicator |
| Retry Rate | Tests requiring retry | Flakiness indicator |
| Memory Usage | Peak memory during tests | Resource optimization |
| CPU Utilization | Average CPU usage | Parallelization tuning |
| I/O Wait Time | Time waiting for I/O | Bottleneck identification |

## Implementation Architecture

### Data Collection Layer

```python
import time
import psutil
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional
import pytest

class TestPerformanceCollector:
    """Collects detailed test performance metrics."""
    
    def __init__(self, storage_path: Path = Path(".test-performance")):
        self.storage_path = storage_path
        self.storage_path.mkdir(exist_ok=True)
        self.current_run = {
            "start_time": None,
            "end_time": None,
            "tests": [],
            "environment": self._capture_environment()
        }
    
    def _capture_environment(self) -> dict:
        """Capture test environment details."""
        return {
            "python_version": sys.version,
            "pytest_version": pytest.__version__,
            "cpu_count": psutil.cpu_count(),
            "memory_total": psutil.virtual_memory().total,
            "platform": platform.platform(),
            "git_commit": self._get_git_commit()
        }
    
    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_protocol(self, item, nextitem):
        """Hook to measure individual test performance."""
        test_metrics = {
            "name": item.nodeid,
            "start_time": time.perf_counter(),
            "start_memory": psutil.Process().memory_info().rss
        }
        
        # Execute test
        outcome = yield
        
        # Collect metrics
        test_metrics.update({
            "end_time": time.perf_counter(),
            "duration": time.perf_counter() - test_metrics["start_time"],
            "end_memory": psutil.Process().memory_info().rss,
            "memory_delta": psutil.Process().memory_info().rss - test_metrics["start_memory"],
            "outcome": outcome.get_result(),
            "markers": [m.name for m in item.iter_markers()]
        })
        
        self.current_run["tests"].append(test_metrics)
    
    def save_run(self):
        """Save performance data for current run."""
        timestamp = datetime.now().isoformat()
        output_file = self.storage_path / f"run_{timestamp}.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.current_run, f, indent=2)
```

### Performance Analysis Engine

```python
import pandas as pd
import numpy as np
from scipy import stats

class TestPerformanceAnalyzer:
    """Analyzes test performance trends and detects regressions."""
    
    def __init__(self, data_path: Path):
        self.data_path = data_path
        self.history = self._load_history()
    
    def _load_history(self) -> pd.DataFrame:
        """Load historical performance data."""
        runs = []
        for run_file in self.data_path.glob("run_*.json"):
            with open(run_file) as f:
                run_data = json.load(f)
                for test in run_data["tests"]:
                    test["run_timestamp"] = run_file.stem.replace("run_", "")
                    runs.append(test)
        return pd.DataFrame(runs)
    
    def detect_slowdowns(self, threshold: float = 1.5) -> List[Dict]:
        """Detect tests that have slowed down significantly."""
        slowdowns = []
        
        for test_name in self.history['name'].unique():
            test_history = self.history[self.history['name'] == test_name]
            
            if len(test_history) < 5:
                continue
            
            # Calculate rolling average
            recent_avg = test_history.tail(5)['duration'].mean()
            historical_avg = test_history.head(-5)['duration'].mean()
            
            if recent_avg > historical_avg * threshold:
                slowdowns.append({
                    "test": test_name,
                    "recent_avg": recent_avg,
                    "historical_avg": historical_avg,
                    "slowdown_factor": recent_avg / historical_avg
                })
        
        return slowdowns
    
    def identify_bottlenecks(self, top_n: int = 10) -> pd.DataFrame:
        """Identify the slowest tests that dominate execution time."""
        latest_run = self.history[
            self.history['run_timestamp'] == self.history['run_timestamp'].max()
        ]
        
        total_time = latest_run['duration'].sum()
        
        bottlenecks = latest_run.nlargest(top_n, 'duration').copy()
        bottlenecks['percent_of_total'] = (bottlenecks['duration'] / total_time * 100)
        bottlenecks['cumulative_percent'] = bottlenecks['percent_of_total'].cumsum()
        
        return bottlenecks[['name', 'duration', 'percent_of_total', 'cumulative_percent']]
    
    def calculate_trends(self, window: int = 10) -> Dict:
        """Calculate performance trends over time."""
        trends = {}
        
        # Group by run
        run_summaries = self.history.groupby('run_timestamp').agg({
            'duration': ['sum', 'mean', 'max', 'count']
        })
        
        # Calculate trends
        if len(run_summaries) >= window:
            recent = run_summaries.tail(window)
            older = run_summaries.head(-window)
            
            trends['total_time_trend'] = (
                recent['duration']['sum'].mean() / 
                older['duration']['sum'].mean() - 1
            ) * 100
            
            trends['avg_time_trend'] = (
                recent['duration']['mean'].mean() / 
                older['duration']['mean'].mean() - 1
            ) * 100
            
            trends['test_count_trend'] = (
                recent['duration']['count'].mean() / 
                older['duration']['count'].mean() - 1
            ) * 100
        
        return trends
```

### Performance Dashboard

```python
class TestPerformanceDashboard:
    """Generate performance reports and visualizations."""
    
    def __init__(self, analyzer: TestPerformanceAnalyzer):
        self.analyzer = analyzer
    
    def generate_report(self) -> str:
        """Generate comprehensive performance report."""
        report = []
        report.append("=" * 60)
        report.append("TEST PERFORMANCE REPORT")
        report.append("=" * 60)
        
        # Latest run summary
        latest_run = self.analyzer.history[
            self.analyzer.history['run_timestamp'] == 
            self.analyzer.history['run_timestamp'].max()
        ]
        
        report.append(f"\n📊 LATEST RUN SUMMARY")
        report.append(f"  Total Tests: {len(latest_run)}")
        report.append(f"  Total Time: {latest_run['duration'].sum():.2f}s")
        report.append(f"  Average Time: {latest_run['duration'].mean():.3f}s")
        report.append(f"  Slowest Test: {latest_run['duration'].max():.2f}s")
        
        # Bottlenecks
        bottlenecks = self.analyzer.identify_bottlenecks(5)
        report.append(f"\n🐌 TOP 5 SLOWEST TESTS")
        for _, row in bottlenecks.iterrows():
            report.append(
                f"  {row['name'][:50]}: {row['duration']:.2f}s "
                f"({row['percent_of_total']:.1f}% of total)"
            )
        
        # Slowdowns detected
        slowdowns = self.analyzer.detect_slowdowns()
        if slowdowns:
            report.append(f"\n⚠️  PERFORMANCE REGRESSIONS DETECTED")
            for slowdown in slowdowns[:5]:
                report.append(
                    f"  {slowdown['test'][:50]}: "
                    f"{slowdown['slowdown_factor']:.1f}x slower"
                )
        
        # Trends
        trends = self.analyzer.calculate_trends()
        if trends:
            report.append(f"\n📈 PERFORMANCE TRENDS (last 10 runs)")
            report.append(f"  Total Time: {trends.get('total_time_trend', 0):+.1f}%")
            report.append(f"  Average Time: {trends.get('avg_time_trend', 0):+.1f}%")
            report.append(f"  Test Count: {trends.get('test_count_trend', 0):+.1f}%")
        
        return "\n".join(report)
    
    def generate_html_dashboard(self) -> str:
        """Generate interactive HTML dashboard."""
        import plotly.graph_objects as go
        from plotly.subplots import make_subplots
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Test Duration Over Time',
                'Duration Distribution',
                'Slowest Tests',
                'Performance Trends'
            )
        )
        
        # Add traces for each subplot
        # ... (visualization code)
        
        return fig.to_html()
```

### Optimization Recommendations

```python
class TestPerformanceOptimizer:
    """Provides optimization recommendations based on performance data."""
    
    def __init__(self, analyzer: TestPerformanceAnalyzer):
        self.analyzer = analyzer
    
    def recommend_parallelization(self) -> Dict:
        """Recommend optimal parallelization strategy."""
        bottlenecks = self.analyzer.identify_bottlenecks(20)
        
        # Calculate theoretical speedup
        total_time = bottlenecks['duration'].sum()
        longest_test = bottlenecks['duration'].max()
        
        recommendations = {
            "current_serial_time": total_time,
            "theoretical_parallel_time": longest_test,
            "potential_speedup": total_time / longest_test,
            "recommended_workers": min(4, int(total_time / longest_test))
        }
        
        # Identify tests that should not be parallelized
        non_parallel = bottlenecks[
            bottlenecks['name'].str.contains('database|integration|e2e')
        ]
        
        if not non_parallel.empty:
            recommendations["serial_tests"] = non_parallel['name'].tolist()
        
        return recommendations
    
    def suggest_test_optimizations(self) -> List[Dict]:
        """Suggest specific test optimizations."""
        suggestions = []
        
        # Find tests with high setup/teardown overhead
        test_groups = self.analyzer.history.groupby('name')
        
        for test_name, group in test_groups:
            if len(group) < 5:
                continue
            
            avg_duration = group['duration'].mean()
            
            # Check for excessive duration
            if avg_duration > 1.0:
                suggestions.append({
                    "test": test_name,
                    "issue": "excessive_duration",
                    "current": avg_duration,
                    "target": 0.5,
                    "suggestion": "Consider mocking external dependencies or using smaller test data"
                })
            
            # Check for high variability (possible flakiness)
            cv = group['duration'].std() / avg_duration
            if cv > 0.3:
                suggestions.append({
                    "test": test_name,
                    "issue": "high_variability",
                    "cv": cv,
                    "suggestion": "Test may be flaky or dependent on external resources"
                })
        
        return suggestions
```

## Integration with CI/CD

### GitHub Actions Integration

```yaml
name: Test Performance Tracking

on:
  push:
    branches: [main, develop]
  pull_request:
  schedule:
    - cron: '0 0 * * 0'  # Weekly performance baseline

jobs:
  performance-tracking:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Run tests with performance tracking
      run: |
        pytest --performance-track --json-report=performance.json
    
    - name: Analyze performance
      run: |
        python -m test_performance analyze performance.json
    
    - name: Check for regressions
      run: |
        python -m test_performance check-regression \
          --baseline .performance-baseline.json \
          --current performance.json \
          --threshold 1.2
    
    - name: Upload performance data
      uses: actions/upload-artifact@v3
      with:
        name: performance-data
        path: |
          performance.json
          performance-report.html
    
    - name: Comment on PR
      if: github.event_name == 'pull_request'
      uses: actions/github-script@v6
      with:
        script: |
          const fs = require('fs');
          const report = fs.readFileSync('performance-summary.md', 'utf8');
          github.rest.issues.createComment({
            issue_number: context.issue.number,
            owner: context.repo.owner,
            repo: context.repo.repo,
            body: report
          });
```

## Performance Thresholds and Alerts

### Alert Configuration

```yaml
performance_thresholds:
  critical:
    total_time: 1800  # 30 minutes
    unit_test_time: 420  # 7 minutes
    slowdown_factor: 2.0
    
  warning:
    total_time: 1200  # 20 minutes
    unit_test_time: 300  # 5 minutes
    slowdown_factor: 1.5
    
  optimization_targets:
    p50_test_time: 0.1  # 100ms
    p90_test_time: 0.5  # 500ms
    p99_test_time: 2.0  # 2 seconds
```

### Alert Actions

| Alert Level | Trigger | Action |
|------------|---------|--------|
| Critical | Tests > 30 min | Block deployment, page on-call |
| Warning | Tests > 20 min | Create issue, notify team |
| Info | 10% slowdown | Add to weekly report |

## Reporting and Visualization

### Weekly Performance Report

```markdown
## Test Performance Report - Week of {date}

### 📊 Summary
- Total test runs: {count}
- Average duration: {duration}
- Slowest day: {day} ({time})
- Fastest day: {day} ({time})

### 🚀 Improvements
- {test_name} optimized: {old_time}s → {new_time}s (-{percent}%)

### ⚠️ Regressions
- {test_name} slowed down: {old_time}s → {new_time}s (+{percent}%)

### 🎯 Recommendations
1. Parallelize {test_group} tests (save ~{time}s)
2. Optimize {slow_test} (currently {percent}% of total time)
3. Fix flaky test {flaky_test} (failed {percent}% of runs)
```

### Performance Tracking Commands

```bash
# View current performance
/test --performance-report

# Compare with baseline
/test --performance-compare baseline.json

# Identify bottlenecks
/test --bottleneck-analysis

# Get optimization suggestions
/test --optimize-suggestions

# Set new baseline
/test --set-baseline
```

## Success Metrics

- **Execution Time**: Maintain < 5 min for unit tests
- **Regression Detection**: Catch 100% of > 20% slowdowns
- **Optimization Impact**: Reduce total test time by 30%
- **Parallel Efficiency**: Achieve > 3x speedup with 4 workers
- **Tracking Coverage**: Monitor 100% of test executions