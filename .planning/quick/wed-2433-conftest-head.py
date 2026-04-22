"""
Pytest configuration with performance tracking and common fixtures.

This module provides:
- Performance tracking hooks
- Common fixtures for all tests
- Test collection filtering
"""

import os
import shutil
import sys
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Callable, Dict

import numpy as np
import pandas as pd
import pytest

# Fix pandas/pyarrow compatibility issue with pytest-cov JSON reporting.
# pandas 3.0+ uses pyarrow string backend by default, which can cause
# ArrowTypeError during pytest session finish when coverage data is serialized.
pd.options.mode.string_storage = "python"

# Add src directory to sys.path so pytest can resolve validators module
# (validators is a top-level package at src/validators/, separate from worldenergydata)
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from worldenergydata.testing.performance import TestPerformanceTracker

# ==============================================================================
# COMMON FIXTURES - Available to all tests
# ==============================================================================


@pytest.fixture
def project_root() -> Path:
    """Return the project root directory."""
    return Path(__file__).parent.parent


@pytest.fixture
def test_data_dir(project_root: Path) -> Path:
    """Return the test data directory, creating it if needed."""
    test_data = project_root / "tests" / "fixtures"
    test_data.mkdir(parents=True, exist_ok=True)
    return test_data


@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Return a temporary directory for test files (auto-cleaned)."""
    return tmp_path


@pytest.fixture
def sample_production_data() -> pd.DataFrame:
    """Generate sample production data for testing.

    Returns a DataFrame with 36 months of production data mimicking
    BSEE production report format.
    """
    np.random.seed(42)  # Reproducible results

    # Generate 36 months of data
    n_months = 36
    base_date = datetime(2022, 1, 1)
    dates = [base_date + timedelta(days=30 * i) for i in range(n_months)]

    # Simulate declining production
    initial_oil = 10000  # bbls/month
    decline_rate = 0.05  # 5% monthly decline

    oil_production = [
        initial_oil * (1 - decline_rate) ** i + np.random.normal(0, 500)
        for i in range(n_months)
    ]
    oil_production = [max(0, p) for p in oil_production]

    # Gas production with GOR ~ 2000 scf/bbl
    gas_production = [
        oil * 2000 + np.random.normal(0, 100000) for oil in oil_production
    ]
    gas_production = [max(0, g) for g in gas_production]

    # Water production increases over time
    water_production = [
        1000 * (1.02**i) + np.random.normal(0, 200) for i in range(n_months)
    ]
    water_production = [max(0, w) for w in water_production]

    df = pd.DataFrame(
        {
            "production_date": dates,
            "api_well_number": "608124003301",
            "oil_production_bbl": oil_production,
            "gas_production_mcf": gas_production,
            "water_production_bbl": water_production,
            "days_on_production": [
                28 + np.random.randint(-3, 4) for _ in range(n_months)
            ],
            "status": ["PRODUCING"] * n_months,
        }
    )

    return df


@pytest.fixture
def sample_well_data() -> Dict[str, Any]:
    """Generate sample well data for testing.

    Returns a dictionary mimicking BSEE well header data.
    """
    return {
        "api_well_number": "608124003301",
        "well_name": "JULIA A-001",
        "field": "JULIA",
        "block": "GC 627",
        "area": "GREEN CANYON",
        "water_depth_ft": 7087.0,
        "total_depth_ft": 23500.0,
        "spud_date": datetime(2021, 3, 15),
        "completion_date": datetime(2021, 11, 20),
        "operator": "SHELL OFFSHORE INC",
        "well_status": "PRODUCING",
        "well_type": "OIL",
        "reservoir": "MIOCENE",
        "latitude": 27.8501,
        "longitude": -90.3422,
    }


@pytest.fixture
def reset_environment():
    """Reset environment variables after test.

    Saves current environment, allows test to modify it,
    then restores original environment after test completes.
    """
    original_env = os.environ.copy()
    yield
    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest.fixture
def assert_dataframe_equal() -> Callable:
    """Provide a helper function for DataFrame equality assertion.

    Returns a callable that compares two DataFrames with detailed error messages.
    """

    def _assert_equal(
        df1: pd.DataFrame,
        df2: pd.DataFrame,
        check_dtype: bool = True,
        check_index: bool = True,
    ) -> None:
        """Assert two DataFrames are equal.

        Args:
            df1: First DataFrame
            df2: Second DataFrame
            check_dtype: Whether to check column dtypes
            check_index: Whether to check index equality

        Raises:
            AssertionError: If DataFrames are not equal
        """
        # Check shape
        assert df1.shape == df2.shape, f"Shape mismatch: {df1.shape} vs {df2.shape}"

        # Check columns
        assert list(df1.columns) == list(
            df2.columns
        ), f"Column mismatch: {list(df1.columns)} vs {list(df2.columns)}"

        # Check dtypes
        if check_dtype:
            for col in df1.columns:
                assert (
                    df1[col].dtype == df2[col].dtype
                ), f"Dtype mismatch for column {col}: {df1[col].dtype} vs {df2[col].dtype}"

        # Check index
        if check_index:
            assert df1.index.equals(df2.index), "Index mismatch"

        # Check values
        pd.testing.assert_frame_equal(df1, df2, check_dtype=check_dtype)

    return _assert_equal


@pytest.fixture
def mock_excel_file(tmp_path: Path) -> Path:
    """Create a mock Excel file for testing.

    Creates a simple Excel file with sample data.
    """
    excel_path = tmp_path / "test_data.xlsx"

    # Create sample data
    df = pd.DataFrame(
        {
            "api_well_number": ["608124003301", "608124003302"],
            "oil_bbls": [10000.0, 8000.0],
            "gas_mcf": [20000000.0, 16000000.0],
        }
    )

    df.to_excel(excel_path, index=False)
    return excel_path


@pytest.fixture
def mock_yaml_config(tmp_path: Path) -> Path:
    """Create a mock YAML config file for testing."""
    import yaml

    yaml_path = tmp_path / "config.yml"
    config = {
        "meta": {
            "library": "worldenergydata",
            "basename": "test_config",
            "mode": "enhanced",
        },
        "data": {"well": True, "production": True, "war": False},
        "processing": {"in_memory": True, "chunk_size": 10000},
    }

    with open(yaml_path, "w") as f:
        yaml.dump(config, f)

    return yaml_path


@pytest.fixture
def sample_csv_file(tmp_path: Path, sample_production_data: pd.DataFrame) -> Path:
    """Create a sample CSV file from production data."""
    csv_path = tmp_path / "production_data.csv"
    sample_production_data.to_csv(csv_path, index=False)
    return csv_path


# ==============================================================================
# PERFORMANCE TRACKING
# ==============================================================================

# Initialize global tracker
_performance_tracker = None


def pytest_configure(config):
    """Configure pytest with performance tracking."""
    global _performance_tracker

    # Initialize performance tracker
    db_path = Path(".test_performance.db")
    _performance_tracker = TestPerformanceTracker(db_path)

    # Register as plugin
    config.pluginmanager.register(_performance_tracker, "performance_tracker")


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    """Called before test setup."""
    if _performance_tracker:
        _performance_tracker.start_test(item.nodeid)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Called to create test report."""
    outcome = yield
    report = outcome.get_result()

    # Only record on test call (not setup/teardown)
    if report.when == "call" and _performance_tracker:
        _performance_tracker.end_test(item.nodeid, report)


@pytest.hookimpl(trylast=True)
def pytest_sessionfinish(session, exitstatus):
    """Called after test session finishes."""
    if _performance_tracker:
        summary = _performance_tracker.get_session_summary()

        print("\n" + "=" * 60)
        print("Test Performance Summary")
        print("=" * 60)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"Total Duration: {summary['total_duration']:.2f}s")
        print(f"Average Duration: {summary['avg_duration']:.3f}s")
        print(f"Success Rate: {summary['success_rate']:.1f}%")

        # Check for regressions
        from worldenergydata.testing.performance import PerformanceAnalyzer

        analyzer = PerformanceAnalyzer(_performance_tracker.db)
        regressions = analyzer.detect_regressions(lookback_days=7)

        if regressions:
            print("\n⚠️  Performance Regressions Detected:")
            for reg in regressions[:3]:
                print(f"  - {reg['test_name']}: {reg['regression_factor']:.2f}x slower")

        print("=" * 60)


# Skip collection of experimental/archived test files
def pytest_ignore_collect(collection_path, config):
    """Skip collection of experimental and archived test files.

    Test directory structure (2025-01):
        tests/
        ├── unit/           # Module-grouped unit tests
        │   ├── bsee/
        │   ├── fdas/
        │   ├── marine_safety/
        │   ├── hse/
        │   ├── reporting/
        │   ├── vessel_hull_models/
        │   └── well_production_dashboard/
        ├── integration/    # Integration tests
        │   └── modules/
        ├── e2e/            # End-to-end tests
        ├── fixtures/       # Test fixtures
        ├── helpers/        # Test helpers
        └── _archived/      # Legacy tests (not collected)
            ├── legacy/
            └── validation_runs/
    """
    import re

    path_str = str(collection_path)
    basename = collection_path.name

    # Skip query_*.py files (exploratory scripts)
    if basename.startswith("query_") and basename.endswith("_test.py"):
        return True

    # Skip _archive and _archived directories and all subdirectories (consolidated 2025-01)
    if "/_archive/" in path_str or path_str.endswith("/_archive"):
        return True
    if "/_archived/" in path_str or path_str.endswith("/_archived"):
        return True

    # Legacy pattern - keep for backward compatibility
    if "_archived_tests" in path_str:
        return True

    # Skip 2025-* dated experimental directories
    if re.search(r"202\d-\d{2}-\d{2}", basename):
        return True

    # Skip directories explicitly listed in norecursedirs but not being honored
    excluded_patterns = [
        "comprehensive-report-system",
        "financial-analysis-sme-code",
        "well-data-verification",
        "/legacy/",
        "legacy_",
        "custom_scripts",
    ]

    for pattern in excluded_patterns:
        if pattern in path_str:
            return True

    return False
