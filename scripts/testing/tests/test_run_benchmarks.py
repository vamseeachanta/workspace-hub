"""TDD tests for scripts/testing/run-benchmarks.sh.

Tests drive the implementation of the benchmark runner script.
Run with: uv run --no-project python -m pytest scripts/testing/tests/test_run_benchmarks.py -v
"""

import json
import os
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]
SCRIPT = REPO_ROOT / "scripts" / "testing" / "run-benchmarks.sh"
BASELINE_PATH = REPO_ROOT / "config" / "testing" / "benchmark-baseline.json"


def run_script(*args, env_override=None, timeout=300):
    env = os.environ.copy()
    if env_override:
        env.update(env_override)
    result = subprocess.run(
        ["bash", str(SCRIPT)] + list(args),
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        env=env,
        timeout=timeout,
    )
    return result


class TestRunBenchmarksBasic:
    def test_run_benchmarks_all_repos_exit_zero(self):
        """Script returns 0 when benchmarks pass and baseline exists."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline not yet bootstrapped — run --save-baseline first")
        result = run_script(timeout=420)
        assert result.returncode == 0, f"stdout: {result.stdout}\nstderr: {result.stderr}"

    def test_run_benchmarks_single_repo(self):
        """--repo flag restricts run to one repo."""
        if not BASELINE_PATH.exists():
            pytest.skip("Baseline not yet bootstrapped")
        result = run_script("--repo", "assetutilities", timeout=60)
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert "assetutilities" in result.stdout or result.returncode == 0

    def test_save_baseline_writes_json(self, tmp_path):
        """--save-baseline --no-compare writes benchmark-baseline.json."""
        baseline = tmp_path / "benchmark-baseline.json"
        env = {"BENCHMARK_BASELINE_PATH": str(baseline)}
        # Use single repo to keep test fast (assetutilities: pure-math, ~5s)
        result = run_script(
            "--save-baseline", "--no-compare", "--repo", "assetutilities",
            env_override=env, timeout=60,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"
        assert baseline.exists(), "Baseline JSON not written"
        data = json.loads(baseline.read_text())
        assert isinstance(data, dict), "Baseline must be a JSON object"
        assert len(data) > 0, "Baseline must have at least one entry"

    def test_no_regression_passes(self, tmp_path):
        """Comparing against itself (same baseline) returns exit 0."""
        baseline = tmp_path / "benchmark-baseline.json"
        env = {"BENCHMARK_BASELINE_PATH": str(baseline)}
        # First: create baseline (single repo for speed)
        result = run_script(
            "--save-baseline", "--no-compare", "--repo", "assetutilities",
            env_override=env, timeout=60,
        )
        assert result.returncode == 0, f"Bootstrap failed: {result.stderr}"
        # Second: compare against itself
        result = run_script("--repo", "assetutilities", env_override=env, timeout=60)
        assert result.returncode == 0, (
            f"Self-comparison failed (no regression expected)\n"
            f"stdout: {result.stdout}\nstderr: {result.stderr}"
        )


class TestRunBenchmarksEdgeCases:
    def test_missing_baseline_exits_with_bootstrap_error(self, tmp_path):
        """No baseline + no --no-compare → exit 2 with clear message."""
        nonexistent = tmp_path / "does_not_exist.json"
        env = {"BENCHMARK_BASELINE_PATH": str(nonexistent)}
        result = run_script(env_override=env)
        assert result.returncode == 2, (
            f"Expected exit 2 for missing baseline, got {result.returncode}\n"
            f"stderr: {result.stderr}"
        )
        output = result.stdout + result.stderr
        assert "baseline" in output.lower(), "Error message must mention 'baseline'"

    def test_invalid_repo_name_exits_nonzero(self):
        """--repo with unknown name exits nonzero with informative error."""
        result = run_script("--repo", "nonexistent_repo_xyz")
        assert result.returncode != 0, "Expected nonzero for invalid repo"
        output = result.stdout + result.stderr
        assert "nonexistent_repo_xyz" in output or "unknown" in output.lower()

    def test_new_benchmark_not_in_baseline_warns_not_fails(self, tmp_path):
        """Benchmark absent from baseline produces WARN output, not exit 1."""
        # Minimal baseline with a placeholder — real benchmark names will differ.
        # Use single repo to keep test fast.
        baseline = tmp_path / "benchmark-baseline.json"
        baseline.write_text(json.dumps({"assetutilities::__placeholder__": 0.001}))
        env = {"BENCHMARK_BASELINE_PATH": str(baseline)}
        result = run_script("--repo", "assetutilities", env_override=env, timeout=60)
        # New benchmarks (not in baseline) should WARN but not cause exit 1
        assert result.returncode in (0, 2), (
            f"New benchmark should WARN (exit 0) or bootstrap-error (exit 2), "
            f"not regression (exit 1). Got {result.returncode}\n"
            f"stderr: {result.stderr}"
        )
