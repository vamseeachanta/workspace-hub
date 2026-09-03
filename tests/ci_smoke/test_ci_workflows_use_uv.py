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


def _assert_no_pip_cache_when_uv_installs(text: str, workflow: str) -> None:
    """A uv-managed workflow must not ask setup-python to cache pip.

    ``actions/setup-python`` with ``cache: pip`` registers a post-job step that
    saves ``~/.cache/pip``. A workflow that installs everything through
    ``uv sync`` never populates that directory, so the post step errors with
    "Cache folder path is retrieved for pip but doesn't exist on disk" and
    **fails the whole job even when every test passed**.

    That is the worst shape a CI failure can take: a red job whose test steps
    are all green. It reads as a real regression, it makes every PR
    ``mergeStateStatus == UNSTABLE``, and under the repo's merge-authorization
    rule an UNSTABLE PR cannot be merged by an agent -- so a caching hint that
    saves nothing blocks the merge queue.

    Asserted as a property (uv installs => no pip cache), not as the absence of
    one literal spelling, so a future ``cache: "pip"`` or ``cache: pip`` is
    caught too.
    """
    if not re.search(r"uv sync\b", text):
        return  # not a uv-managed workflow; a pip cache may be legitimate there
    offender = re.search(r"^\s*cache:\s*['\"]?pip['\"]?\s*$", text, re.M)
    assert offender is None, (
        f"{workflow} installs dependencies with uv but declares "
        f"{offender.group(0).strip() if offender else ''} on setup-python; "
        "nothing populates ~/.cache/pip, so the post-job cache step errors and "
        "fails the job despite passing tests. Drop the cache key, or cache uv."
    )


def test_baseline_workflow_does_not_cache_pip_it_never_populates() -> None:
    _assert_no_pip_cache_when_uv_installs(
        BASELINE.read_text(encoding="utf-8"), "baseline-check.yml"
    )


def test_enforcement_workflow_does_not_cache_pip_it_never_populates() -> None:
    _assert_no_pip_cache_when_uv_installs(
        ENFORCEMENT.read_text(encoding="utf-8"), "enforcement-gate.yml"
    )


def test_pip_cache_assertion_still_catches_the_regression() -> None:
    """The property matcher must fail on the shape it was written to reject.

    Same guard as `test_dev_group_assertion_rejects_a_missing_uv_sync`: a
    loosened matcher is only an improvement while it still catches the original
    defect. All three spellings must trip it, and a non-uv workflow must not.
    """
    import pytest

    for spelling in ("cache: 'pip'", 'cache: "pip"', "cache: pip"):
        synthetic = f"steps:\n  - uses: actions/setup-python@v5\n    with:\n      {spelling}\n  - run: uv sync --frozen --group dev\n"
        with pytest.raises(AssertionError):
            _assert_no_pip_cache_when_uv_installs(synthetic, "synthetic.yml")

    # A workflow that genuinely uses pip may cache pip; the guard must stay quiet.
    _assert_no_pip_cache_when_uv_installs(
        "steps:\n  - uses: actions/setup-python@v5\n    with:\n      cache: 'pip'\n  - run: pip install pytest\n",
        "pip-based.yml",
    )


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