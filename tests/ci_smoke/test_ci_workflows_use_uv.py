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


def _pip_cache_offenders(text: str) -> list[str]:
    """Jobs that cache pip on setup-python while installing only through uv.

    ``actions/setup-python`` with ``cache: pip`` registers a post-job step that
    saves ``~/.cache/pip``. A job that installs everything through ``uv sync``
    never populates that directory, so the post step errors with "Cache folder
    path is retrieved for pip but doesn't exist on disk" and **fails the whole
    job even when every test passed**.

    That is the worst shape a CI failure can take: a red job whose test steps
    are all green. It reads as a real regression, and because this repo
    declares no required checks, one red non-required check puts every PR at
    ``mergeStateStatus == UNSTABLE`` -- which `.claude/rules/merge-authorization.md`
    rule 7 forbids an agent merging from. A caching hint that saves nothing can
    deadlock the merge queue repo-wide.

    Scoped **per job, and to the setup-python step specifically**, by parsing
    the YAML rather than scanning text. A whole-file regex would reject a
    legitimate mixed workflow -- one uv-managed job beside a genuinely
    pip-managed one that must cache pip -- and would blame setup-python for a
    ``cache:`` key belonging to some other action. The rule enforced here is the
    operational one: *no pip cache on a setup-python step in a job whose
    installs are uv-only.*
    """
    import yaml

    doc = yaml.safe_load(text) or {}
    offenders = []
    for job_name, job in (doc.get("jobs") or {}).items():
        steps = (job or {}).get("steps") or []
        runs = " \n".join(str(st.get("run", "")) for st in steps if isinstance(st, dict))
        installs_with_uv = re.search(r"uv sync\b", runs) is not None
        populates_pip = re.search(r"\bpip install\b", runs) is not None
        if not installs_with_uv or populates_pip:
            continue  # not uv-only, so a pip cache may be legitimate here
        for st in steps:
            if not isinstance(st, dict):
                continue
            if not str(st.get("uses", "")).startswith("actions/setup-python"):
                continue
            if str(((st.get("with") or {}).get("cache", ""))).strip().lower() == "pip":
                offenders.append(job_name)
    return offenders


def _assert_no_pip_cache_when_uv_installs(text: str, workflow: str) -> None:
    offenders = _pip_cache_offenders(text)
    assert not offenders, (
        f"{workflow}: job(s) {offenders} install dependencies only with uv but "
        "set `cache: pip` on actions/setup-python. Nothing populates "
        "~/.cache/pip, so the post-job cache step errors and fails the job "
        "despite passing tests. Drop the cache key, or cache uv."
    )


def test_baseline_workflow_does_not_cache_pip_it_never_populates() -> None:
    _assert_no_pip_cache_when_uv_installs(
        BASELINE.read_text(encoding="utf-8"), "baseline-check.yml"
    )


def test_enforcement_workflow_does_not_cache_pip_it_never_populates() -> None:
    _assert_no_pip_cache_when_uv_installs(
        ENFORCEMENT.read_text(encoding="utf-8"), "enforcement-gate.yml"
    )


_SETUP_PY = "      - uses: actions/setup-python@v5\n        with:\n          cache: %s\n"


def _wf(*jobs: str) -> str:
    return "jobs:\n" + "".join(jobs)


def _job(name: str, cache: str | None, install: str) -> str:
    step = _SETUP_PY % cache if cache is not None else ""
    return f"  {name}:\n    steps:\n{step}      - run: {install}\n"


def test_pip_cache_guard_catches_every_spelling_on_a_uv_only_job() -> None:
    """A loosened matcher is only an improvement while it still catches the defect.

    Same guard as `test_dev_group_assertion_rejects_a_missing_uv_sync`.
    """
    for spelling in ("'pip'", '"pip"', "pip"):
        wf = _wf(_job("test", spelling, "uv sync --frozen --group dev"))
        assert _pip_cache_offenders(wf) == ["test"], f"missed spelling {spelling}"


def test_pip_cache_guard_allows_a_genuinely_pip_managed_job() -> None:
    """A job that really uses pip may cache pip; the guard must stay quiet."""
    assert _pip_cache_offenders(
        _wf(_job("legacy", "'pip'", "pip install -r requirements.txt"))
    ) == []


def test_pip_cache_guard_does_not_false_positive_on_a_mixed_workflow() -> None:
    """The whole-file regex this replaced would have failed this shape.

    Job A is uv-only with no pip cache; job B genuinely uses pip and caches it.
    Scanning the file as one string would see `uv sync` and `cache: pip` both
    present and reject a correct workflow. Job scoping is what makes the guard
    safe to apply to files that may grow new jobs later.
    """
    mixed = _wf(
        _job("uv_job", None, "uv sync --frozen --group dev"),
        _job("pip_job", "'pip'", "pip install -r requirements.txt"),
    )
    assert _pip_cache_offenders(mixed) == []


def test_pip_cache_guard_blames_only_the_offending_job() -> None:
    mixed = _wf(
        _job("clean_uv", None, "uv sync --frozen --group dev"),
        _job("broken_uv", "'pip'", "uv sync --frozen --group dev"),
        _job("pip_job", "'pip'", "pip install -r requirements.txt"),
    )
    assert _pip_cache_offenders(mixed) == ["broken_uv"]


def test_pip_cache_guard_ignores_a_cache_key_on_another_action() -> None:
    """The message blames setup-python, so the matcher must prove it is that step."""
    wf = (
        "jobs:\n  test:\n    steps:\n"
        "      - uses: some/other-action@v1\n        with:\n          cache: 'pip'\n"
        "      - run: uv sync --frozen --group dev\n"
    )
    assert _pip_cache_offenders(wf) == []


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