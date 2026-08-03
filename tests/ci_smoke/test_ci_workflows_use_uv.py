from __future__ import annotations

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


def test_baseline_workflow_uses_uv_managed_test_environment() -> None:
    text = BASELINE.read_text(encoding="utf-8")

    assert "uv sync --group dev" in text
    assert "uv run python -m pytest tests/test_deduplication_fix.py" in text
    assert "uv run python -m pytest tests/ci_smoke/" in text
    assert "pip install pytest" not in text


def test_enforcement_workflow_uses_uv_managed_test_environment() -> None:
    text = ENFORCEMENT.read_text(encoding="utf-8")

    assert "uv sync --group dev" in text
    assert "uv run python -m pytest tests/ci_smoke/test_workspace_hub_importable.py" in text
    assert "pip install pytest" not in text