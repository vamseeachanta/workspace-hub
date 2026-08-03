from __future__ import annotations

import re
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PYPROJECT = REPO_ROOT / "pyproject.toml"
BASELINE = REPO_ROOT / ".github" / "workflows" / "baseline-check.yml"
ENFORCEMENT = REPO_ROOT / ".github" / "workflows" / "enforcement-gate.yml"


def test_pyproject_declares_uv_dev_dependencies_for_local_pytest_runs() -> None:
    text = PYPROJECT.read_text(encoding="utf-8")

    assert "[dependency-groups]" in text
    assert "dev = [" in text
    assert '"pytest>=8.0"' in text


def _assert_syncs_dev_group(text: str, workflow: str) -> None:
    """Assert the workflow installs the dev group via uv, whatever flags it uses.

    This previously asserted the literal substring ``uv sync --group dev``, which
    pins a *spelling* rather than the *property* the test is named for. Adding a
    strictly better flag -- ``uv sync --frozen --group dev``, which installs the
    lockfile without re-resolving -- broke it, while a real regression (dropping
    uv for pip) could pass simply by being worded differently.

    Match any ``uv sync`` invocation carrying ``--group dev``, so correct flags
    are free to change and the guarantee still holds.
    """
    assert re.search(r"uv sync(?:\s+--[\w-]+)*\s+--group dev\b", text), (
        f"{workflow} must install the dev group with `uv sync ... --group dev`"
    )


def test_baseline_workflow_uses_uv_managed_test_environment() -> None:
    text = BASELINE.read_text(encoding="utf-8")

    _assert_syncs_dev_group(text, "baseline-check.yml")
    assert "uv run python -m pytest tests/test_deduplication_fix.py" in text
    assert "uv run python -m pytest tests/ci_smoke/" in text
    assert "pip install pytest" not in text


def test_enforcement_workflow_uses_uv_managed_test_environment() -> None:
    text = ENFORCEMENT.read_text(encoding="utf-8")

    _assert_syncs_dev_group(text, "enforcement-gate.yml")
    assert "uv run python -m pytest tests/ci_smoke/test_workspace_hub_importable.py" in text
    assert "pip install pytest" not in text


def test_dev_group_assertion_rejects_a_missing_uv_sync() -> None:
    """The helper must still fail when uv genuinely is not used.

    A looser matcher is only an improvement if it still catches the regression
    the strict one caught. Pinning that here so the loosening cannot silently
    become a no-op.
    """
    import pytest

    with pytest.raises(AssertionError):
        _assert_syncs_dev_group("run: pip install -r requirements.txt\n", "fake.yml")

    with pytest.raises(AssertionError):
        _assert_syncs_dev_group("run: uv sync --frozen\n", "fake.yml")