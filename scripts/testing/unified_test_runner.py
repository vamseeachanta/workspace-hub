#!/usr/bin/env python3
"""
ABOUTME: Unified test runner for parallel pytest execution across 25+ repositories
ABOUTME: Aggregates coverage metrics, test results, and generates HTML/XML reports

Multi-repository pytest orchestrator with pytest-xdist support.

Features:
- Parallel execution of 5 repositories simultaneously
- Automatic UV virtual environment creation and setup
- Per-repository test isolation and reporting
- Unified HTML coverage report aggregation
- JUnit XML output for CI/CD integration
- Real-time progress indicators with status table
- Comprehensive error handling and recovery

Author: Claude Code
Version: 1.0.0
"""

import argparse
import json
import logging
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Tuple
from xml.etree import ElementTree as ET
from html import escape

# ============================================================================
# Configuration & Logging Setup
# ============================================================================

WORKSPACE_ROOT = Path(__file__).parent.parent.parent
DEFAULT_CONFIG = WORKSPACE_ROOT / "config" / "repos.conf"
DEFAULT_OUTPUT = WORKSPACE_ROOT / "reports" / "test-results"
MAX_PARALLEL_REPOS = 5
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
    ]
)
logger = logging.getLogger(__name__)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class TestResult:
    """Represents a single repository test execution result."""

    repo_name: str
    repo_path: Path
    status: str  # "success", "failed", "error", "skipped"
    test_count: int = 0
    passed_count: int = 0
    failed_count: int = 0
    skipped_count: int = 0
    coverage_percent: float = 0.0
    execution_time: float = 0.0
    error_message: Optional[str] = None
    junit_file: Optional[Path] = None
    coverage_file: Optional[Path] = None
    log_file: Optional[Path] = None

    def to_dict(self) -> dict:
        """Convert to dictionary, handling Path objects."""
        data = asdict(self)
        data['repo_path'] = str(self.repo_path)
        data['junit_file'] = str(self.junit_file) if self.junit_file else None
        data['coverage_file'] = str(self.coverage_file) if self.coverage_file else None
        data['log_file'] = str(self.log_file) if self.log_file else None
        return data


@dataclass
class AggregatedResults:
    """Aggregated results from all test runs."""

    total_repos: int = 0
    successful_repos: int = 0
    failed_repos: int = 0
    error_repos: int = 0
    skipped_repos: int = 0
    total_tests: int = 0
    total_passed: int = 0
    total_failed: int = 0
    total_skipped: int = 0
    average_coverage: float = 0.0
    total_execution_time: float = 0.0
    results: List[TestResult] = field(default_factory=list)

    def calculate_metrics(self) -> None:
        """Calculate aggregated metrics from individual results."""
        self.total_repos = len(self.results)
        self.successful_repos = sum(1 for r in self.results if r.status == "success")
        self.failed_repos = sum(1 for r in self.results if r.status == "failed")
        self.error_repos = sum(1 for r in self.results if r.status == "error")
        self.skipped_repos = sum(1 for r in self.results if r.status == "skipped")

        self.total_tests = sum(r.test_count for r in self.results)
        self.total_passed = sum(r.passed_count for r in self.results)
        self.total_failed = sum(r.failed_count for r in self.results)
        self.total_skipped = sum(r.skipped_count for r in self.results)

        coverage_values = [r.coverage_percent for r in self.results if r.coverage_percent > 0]
        self.average_coverage = sum(coverage_values) / len(coverage_values) if coverage_values else 0.0

        self.total_execution_time = sum(r.execution_time for r in self.results)

    def success_rate(self) -> float:
        """Calculate test pass rate."""
        if self.total_tests == 0:
            return 0.0
        return (self.total_passed / self.total_tests) * 100

    def repo_success_rate(self) -> float:
        """Calculate repository success rate."""
        if self.total_repos == 0:
            return 0.0
        return (self.successful_repos / self.total_repos) * 100


# ============================================================================
# Repository Discovery & Configuration
# ============================================================================

def load_repository_config(config_file: Path) -> Dict[str, str]:
    """
    Load repository configuration from repos.conf.

    Args:
        config_file: Path to repos.conf file

    Returns:
        Dictionary mapping repo name to repo path

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If config file format is invalid
    """
    if not config_file.exists():
        raise FileNotFoundError(f"Repository config not found: {config_file}")

    repos = {}
    with open(config_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' not in line:
                continue

            repo_name, _ = line.split('=', 1)
            repo_name = repo_name.strip()

            # Check if repository exists locally
            repo_path = WORKSPACE_ROOT / repo_name
            if repo_path.is_dir():
                repos[repo_name] = repo_path

    logger.info(f"Discovered {len(repos)} local repositories")
    return repos


def filter_repositories(
    repos: Dict[str, Path],
    repo_filter: Optional[List[str]] = None,
    work_only: bool = False,
    personal_only: bool = False
) -> Dict[str, Path]:
    """
    Filter repositories based on criteria.

    Args:
        repos: All available repositories
        repo_filter: Specific repository names to include
        work_only: Include only work repositories
        personal_only: Include only personal repositories

    Returns:
        Filtered repository dictionary
    """
    if repo_filter:
        repos = {k: v for k, v in repos.items() if k in repo_filter}

    if work_only or personal_only:
        gitignore = WORKSPACE_ROOT / ".gitignore"
        if gitignore.exists():
            work_repos = set()
            personal_repos = set()

            with open(gitignore, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line.endswith('/'):
                        repo_name = line.rstrip('/')
                        if '# Work' in line or '#Work' in line:
                            work_repos.add(repo_name)
                        if '# Personal' in line or '#Personal' in line:
                            personal_repos.add(repo_name)

            if work_only:
                repos = {k: v for k, v in repos.items() if k in work_repos}
            elif personal_only:
                repos = {k: v for k, v in repos.items() if k in personal_repos}

    return repos


# ============================================================================
# Test Execution
# ============================================================================

def has_tests(repo_path: Path) -> bool:
    """
    Check if repository has tests.

    Args:
        repo_path: Path to repository

    Returns:
        True if tests directory or test files exist
    """
    tests_dir = repo_path / "tests"
    if tests_dir.is_dir():
        return True

    # Check for test_*.py files
    for file in repo_path.glob("test_*.py"):
        if file.is_file():
            return True

    return False


def setup_environment(repo_path: Path) -> bool:
    """
    Setup UV virtual environment for repository.

    Args:
        repo_path: Path to repository

    Returns:
        True if environment setup succeeded

    Note:
        Creates .venv directory with UV if pyproject.toml exists
    """
    pyproject = repo_path / "pyproject.toml"
    if not pyproject.exists():
        logger.debug(f"No pyproject.toml in {repo_path.name}, skipping environment setup")
        return True

    try:
        # Check if .venv already exists
        venv_path = repo_path / ".venv"
        if venv_path.exists():
            logger.debug(f"Virtual environment exists for {repo_path.name}")
            return True

        # Create UV virtual environment
        result = subprocess.run(
            ["uv", "venv", ".venv"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            logger.warning(f"Failed to create venv for {repo_path.name}: {result.stderr}")
            return False

        # Install dependencies
        result = subprocess.run(
            ["uv", "pip", "install", "-e", "."],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode != 0:
            logger.warning(f"Failed to install dependencies for {repo_path.name}: {result.stderr}")
            return False

        # Install test dependencies if not already included
        subprocess.run(
            ["uv", "pip", "install", "pytest", "pytest-cov", "pytest-xdist"],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=120
        )

        logger.debug(f"Environment setup complete for {repo_path.name}")
        return True

    except subprocess.TimeoutExpired:
        logger.error(f"Environment setup timeout for {repo_path.name}")
        return False
    except Exception as e:
        logger.error(f"Environment setup failed for {repo_path.name}: {e}")
        return False


def run_tests(
    repo_name: str,
    repo_path: Path,
    output_dir: Path,
    verbose: bool = False
) -> TestResult:
    """
    Execute tests for a single repository.

    Args:
        repo_name: Name of repository
        repo_path: Path to repository
        output_dir: Base output directory for results
        verbose: Enable verbose output

    Returns:
        TestResult with execution metrics

    Note:
        Creates isolated output directory per repository
        Uses pytest with xdist for parallel test execution
        Captures coverage and JUnit XML output
    """
    logger.info(f"Starting tests for {repo_name}")
    start_time = time.time()

    result = TestResult(
        repo_name=repo_name,
        repo_path=repo_path,
        status="error",
    )

    # Create repo-specific output directory
    repo_output = output_dir / repo_name
    repo_output.mkdir(parents=True, exist_ok=True)

    # Setup paths
    junit_file = repo_output / "junit.xml"
    coverage_file = repo_output / "coverage.json"
    log_file = repo_output / "test.log"

    result.junit_file = junit_file
    result.coverage_file = coverage_file
    result.log_file = log_file

    try:
        # Check if tests exist
        if not has_tests(repo_path):
            logger.info(f"No tests found for {repo_name}, skipping")
            result.status = "skipped"
            result.execution_time = time.time() - start_time
            return result

        # Setup environment
        if not setup_environment(repo_path):
            logger.warning(f"Failed to setup environment for {repo_name}")
            result.status = "error"
            result.error_message = "Environment setup failed"
            result.execution_time = time.time() - start_time
            return result

        # Build pytest command
        pytest_args = [
            "pytest",
            "tests",
            "-v",
            f"--junit-xml={junit_file}",
            "--cov",
            "--cov-report=json",
            f"--cov-report=json:{coverage_file}",
            "-n", "auto",  # xdist parallel execution
        ]

        if verbose:
            pytest_args.append("-vv")

        # Prepare environment
        env = {**dict(subprocess.os.environ)}
        venv_python = repo_path / ".venv" / "bin" / "python"
        if venv_python.exists():
            env['PATH'] = str(repo_path / ".venv" / "bin") + ":" + env.get('PATH', '')

        # Execute tests
        with open(log_file, 'w') as log:
            test_result = subprocess.run(
                pytest_args,
                cwd=repo_path,
                capture_output=True,
                text=True,
                timeout=600,
                env=env
            )

        # Write logs
        log.write("STDOUT:\n")
        log.write(test_result.stdout)
        log.write("\n\nSTDERR:\n")
        log.write(test_result.stderr)

        # Parse JUnit XML for metrics
        if junit_file.exists():
            result = _parse_junit_xml(junit_file, result)

        # Parse coverage JSON
        if coverage_file.exists():
            result = _parse_coverage_json(coverage_file, result)

        # Determine status
        result.status = "success" if test_result.returncode == 0 else "failed"
        if test_result.returncode != 0 and result.failed_count == 0:
            result.status = "error"
            result.error_message = f"Test execution failed with return code {test_result.returncode}"

        logger.info(
            f"Tests completed for {repo_name}: {result.passed_count} passed, "
            f"{result.failed_count} failed, coverage: {result.coverage_percent:.1f}%"
        )

    except subprocess.TimeoutExpired:
        result.status = "error"
        result.error_message = "Test execution timeout (600s)"
        logger.error(f"Test timeout for {repo_name}")

    except Exception as e:
        result.status = "error"
        result.error_message = str(e)
        logger.error(f"Test execution failed for {repo_name}: {e}")

    finally:
        result.execution_time = time.time() - start_time

    return result


def _parse_junit_xml(junit_file: Path, result: TestResult) -> TestResult:
    """
    Parse JUnit XML to extract test metrics.

    Args:
        junit_file: Path to JUnit XML file
        result: TestResult to update

    Returns:
        Updated TestResult with parsed metrics
    """
    try:
        tree = ET.parse(junit_file)
        root = tree.getroot()

        # Sum metrics from all test suites
        for testsuite in root.findall('.//testsuite'):
            result.test_count += int(testsuite.get('tests', 0))
            result.failed_count += int(testsuite.get('failures', 0))
            result.skipped_count += int(testsuite.get('skipped', 0))

        result.passed_count = result.test_count - result.failed_count - result.skipped_count

    except Exception as e:
        logger.warning(f"Failed to parse JUnit XML for {result.repo_name}: {e}")

    return result


def _parse_coverage_json(coverage_file: Path, result: TestResult) -> TestResult:
    """
    Parse coverage JSON to extract coverage percentage.

    Args:
        coverage_file: Path to coverage JSON file
        result: TestResult to update

    Returns:
        Updated TestResult with coverage metrics
    """
    try:
        with open(coverage_file, 'r') as f:
            coverage_data = json.load(f)

        if 'totals' in coverage_data:
            coverage_percent = coverage_data['totals'].get('percent_covered', 0.0)
            result.coverage_percent = float(coverage_percent)

    except Exception as e:
        logger.warning(f"Failed to parse coverage JSON for {result.repo_name}: {e}")

    return result


# ============================================================================
# Parallel Execution & Orchestration
# ============================================================================

def execute_tests_parallel(
    repos: Dict[str, Path],
    output_dir: Path,
    max_workers: int = MAX_PARALLEL_REPOS,
    verbose: bool = False
) -> AggregatedResults:
    """
    Execute tests across repositories in parallel.

    Args:
        repos: Dictionary of repositories
        output_dir: Output directory for results
        max_workers: Maximum parallel repository executions
        verbose: Enable verbose output

    Returns:
        AggregatedResults with all execution metrics
    """
    logger.info(f"Starting parallel test execution for {len(repos)} repositories")
    logger.info(f"Max workers: {max_workers}")

    aggregated = AggregatedResults()
    completed_count = 0

    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_repo = {
            executor.submit(
                run_tests,
                repo_name,
                repo_path,
                output_dir,
                verbose
            ): repo_name
            for repo_name, repo_path in repos.items()
        }

        # Collect results as they complete
        for future in as_completed(future_to_repo):
            repo_name = future_to_repo[future]
            completed_count += 1

            try:
                result = future.result()
                aggregated.results.append(result)
                _print_progress(completed_count, len(repos), result)

            except Exception as e:
                logger.error(f"Failed to execute tests for {repo_name}: {e}")
                aggregated.results.append(TestResult(
                    repo_name=repo_name,
                    repo_path=repos[repo_name],
                    status="error",
                    error_message=str(e)
                ))

    aggregated.calculate_metrics()
    return aggregated


def _print_progress(completed: int, total: int, result: TestResult) -> None:
    """
    Print progress indicator for test execution.

    Args:
        completed: Number of completed repositories
        total: Total number of repositories
        result: Latest result
    """
    percent = (completed / total) * 100
    status_icon = {
        "success": "✓",
        "failed": "✗",
        "error": "⚠",
        "skipped": "⊘"
    }.get(result.status, "?")

    logger.info(
        f"[{completed}/{total} {percent:.0f}%] {status_icon} {result.repo_name} - "
        f"{result.passed_count} passed, {result.failed_count} failed, "
        f"{result.coverage_percent:.1f}% coverage"
    )


# ============================================================================
# Report Generation
# ============================================================================

def generate_html_report(results: AggregatedResults, output_file: Path) -> None:
    """
    Generate unified HTML coverage and test results report.

    Args:
        results: Aggregated results from all repositories
        output_file: Output file path for HTML report

    Note:
        Creates professional HTML with CSS styling and JavaScript interactivity
    """
    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unified Test Results Report - {TIMESTAMP}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #f5f5f5;
            color: #333;
        }}

        .container {{
            max-width: 1400px;
            margin: 0 auto;
            padding: 20px;
        }}

        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            border-radius: 10px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }}

        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}

        .header p {{
            font-size: 1.1em;
            opacity: 0.9;
        }}

        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            border-left: 5px solid #667eea;
        }}

        .metric-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 10px;
        }}

        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            color: #333;
        }}

        .metric-unit {{
            font-size: 0.5em;
            color: #999;
            margin-left: 5px;
        }}

        .status-success {{ color: #22c55e; }}
        .status-failed {{ color: #ef4444; }}
        .status-error {{ color: #f97316; }}
        .status-skipped {{ color: #6b7280; }}

        .results-table {{
            background: white;
            border-radius: 10px;
            overflow: hidden;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
            margin-bottom: 40px;
        }}

        .table-header {{
            background: #f9fafb;
            padding: 20px;
            border-bottom: 1px solid #e5e7eb;
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
            gap: 15px;
            font-weight: 600;
            font-size: 0.9em;
            text-transform: uppercase;
            color: #666;
            letter-spacing: 0.5px;
        }}

        .table-row {{
            padding: 20px;
            border-bottom: 1px solid #e5e7eb;
            display: grid;
            grid-template-columns: 2fr 1fr 1fr 1fr 1fr 1fr;
            gap: 15px;
            align-items: center;
        }}

        .table-row:hover {{
            background: #f9fafb;
        }}

        .table-row:last-child {{
            border-bottom: none;
        }}

        .repo-name {{
            font-weight: 600;
            color: #333;
        }}

        .repo-name.success {{ color: #22c55e; }}
        .repo-name.failed {{ color: #ef4444; }}
        .repo-name.error {{ color: #f97316; }}
        .repo-name.skipped {{ color: #6b7280; }}

        .progress-bar {{
            width: 100%;
            height: 8px;
            background: #e5e7eb;
            border-radius: 4px;
            overflow: hidden;
        }}

        .progress-fill {{
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s ease;
        }}

        .footer {{
            text-align: center;
            color: #666;
            font-size: 0.9em;
            margin-top: 40px;
            padding: 20px;
        }}

        .timestamp {{
            color: #999;
            font-size: 0.85em;
        }}

        .badge {{
            display: inline-block;
            padding: 4px 12px;
            border-radius: 20px;
            font-size: 0.85em;
            font-weight: 600;
        }}

        .badge-success {{
            background: #d1fae5;
            color: #065f46;
        }}

        .badge-failed {{
            background: #fee2e2;
            color: #7f1d1d;
        }}

        .badge-error {{
            background: #ffedd5;
            color: #7c2d12;
        }}

        .badge-skipped {{
            background: #f3f4f6;
            color: #374151;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Test Results Report</h1>
            <p>Unified pytest execution across {results.total_repos} repositories</p>
            <p class="timestamp">Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>

        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Repositories</div>
                <div class="metric-value">{results.total_repos}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value status-success">{results.repo_success_rate():.1f}<span class="metric-unit">%</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tests</div>
                <div class="metric-value">{results.total_tests}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Pass Rate</div>
                <div class="metric-value status-success">{results.success_rate():.1f}<span class="metric-unit">%</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Coverage</div>
                <div class="metric-value status-success">{results.average_coverage:.1f}<span class="metric-unit">%</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Time</div>
                <div class="metric-value">{results.total_execution_time:.0f}<span class="metric-unit">s</span></div>
            </div>
        </div>

        <div class="results-table">
            <div class="table-header">
                <div>Repository</div>
                <div>Tests</div>
                <div>Passed</div>
                <div>Failed</div>
                <div>Coverage</div>
                <div>Time</div>
            </div>
            {_generate_table_rows(results)}
        </div>

        <div class="footer">
            <p>Unified Test Runner v1.0.0</p>
            <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>
"""

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        f.write(html_content)

    logger.info(f"HTML report generated: {output_file}")


def _generate_table_rows(results: AggregatedResults) -> str:
    """Generate HTML table rows for results."""
    rows = []

    for result in results.results:
        status_class = result.status
        badge_class = f"badge-{result.status}"

        coverage_display = f"{result.coverage_percent:.1f}%" if result.coverage_percent > 0 else "N/A"

        row = f"""
            <div class="table-row">
                <div class="repo-name {status_class}">{escape(result.repo_name)}</div>
                <div>{result.test_count}</div>
                <div class="status-success">{result.passed_count}</div>
                <div class="status-failed">{result.failed_count}</div>
                <div>{coverage_display}</div>
                <div>{result.execution_time:.1f}s</div>
            </div>
        """
        rows.append(row)

    return "".join(rows)


def save_json_results(results: AggregatedResults, output_file: Path) -> None:
    """
    Save aggregated results as JSON for programmatic access.

    Args:
        results: Aggregated results
        output_file: Output JSON file path
    """
    output_file.parent.mkdir(parents=True, exist_ok=True)

    data = {
        'timestamp': TIMESTAMP,
        'summary': {
            'total_repos': results.total_repos,
            'successful_repos': results.successful_repos,
            'failed_repos': results.failed_repos,
            'error_repos': results.error_repos,
            'skipped_repos': results.skipped_repos,
            'total_tests': results.total_tests,
            'total_passed': results.total_passed,
            'total_failed': results.total_failed,
            'total_skipped': results.total_skipped,
            'average_coverage': results.average_coverage,
            'success_rate': results.success_rate(),
            'repo_success_rate': results.repo_success_rate(),
            'total_execution_time': results.total_execution_time,
        },
        'results': [asdict(r) for r in results.results]
    }

    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2, default=str)

    logger.info(f"JSON results saved: {output_file}")


# ============================================================================
# Main Execution
# ============================================================================

def main() -> int:
    """Main entry point for unified test runner."""
    parser = argparse.ArgumentParser(
        description='Unified test runner for parallel pytest execution across multiple repositories',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python unified_test_runner.py
  python unified_test_runner.py --work-only
  python unified_test_runner.py --repos digitalmodel energy
  python unified_test_runner.py --workers 10
        """
    )

    parser.add_argument(
        '--config',
        type=Path,
        default=DEFAULT_CONFIG,
        help=f'Path to repos.conf (default: {DEFAULT_CONFIG})'
    )

    parser.add_argument(
        '--output',
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f'Output directory for results (default: {DEFAULT_OUTPUT})'
    )

    parser.add_argument(
        '--workers',
        type=int,
        default=MAX_PARALLEL_REPOS,
        help=f'Maximum parallel repositories (default: {MAX_PARALLEL_REPOS})'
    )

    parser.add_argument(
        '--repos',
        nargs='+',
        help='Specific repositories to test'
    )

    parser.add_argument(
        '--work-only',
        action='store_true',
        help='Test work repositories only'
    )

    parser.add_argument(
        '--personal-only',
        action='store_true',
        help='Test personal repositories only'
    )

    parser.add_argument(
        '--verbose',
        '-v',
        action='store_true',
        help='Enable verbose output'
    )

    args = parser.parse_args()

    try:
        # Load repositories
        logger.info("Loading repository configuration")
        all_repos = load_repository_config(args.config)

        # Filter repositories
        repos = filter_repositories(
            all_repos,
            repo_filter=args.repos,
            work_only=args.work_only,
            personal_only=args.personal_only
        )

        if not repos:
            logger.error("No repositories found matching criteria")
            return 1

        logger.info(f"Testing {len(repos)} repositories")

        # Execute tests in parallel
        results = execute_tests_parallel(
            repos,
            args.output,
            max_workers=args.workers,
            verbose=args.verbose
        )

        # Generate reports
        html_report = args.output / f"report_{TIMESTAMP}.html"
        json_report = args.output / f"results_{TIMESTAMP}.json"

        generate_html_report(results, html_report)
        save_json_results(results, json_report)

        # Print summary
        logger.info("\n" + "=" * 80)
        logger.info("TEST EXECUTION SUMMARY")
        logger.info("=" * 80)
        logger.info(f"Total Repositories: {results.total_repos}")
        logger.info(f"Successful: {results.successful_repos} | Failed: {results.failed_repos} | "
                   f"Error: {results.error_repos} | Skipped: {results.skipped_repos}")
        logger.info(f"Total Tests: {results.total_tests}")
        logger.info(f"Passed: {results.total_passed} | Failed: {results.total_failed} | "
                   f"Skipped: {results.total_skipped}")
        logger.info(f"Pass Rate: {results.success_rate():.1f}%")
        logger.info(f"Average Coverage: {results.average_coverage:.1f}%")
        logger.info(f"Total Execution Time: {results.total_execution_time:.1f}s")
        logger.info(f"\nReports generated:")
        logger.info(f"  HTML: {html_report}")
        logger.info(f"  JSON: {json_report}")
        logger.info("=" * 80)

        # Return exit code based on results
        return 0 if results.failed_repos == 0 and results.error_repos == 0 else 1

    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=args.verbose)
        return 1


if __name__ == "__main__":
    sys.exit(main())
