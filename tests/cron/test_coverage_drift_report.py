"""Tests for scripts/cron/coverage-drift-report.sh — TDD per #2315 plan."""

import os
import subprocess
from pathlib import Path
from textwrap import dedent

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "coverage-drift-report.sh"


def _coverage_xml(line_rate: float) -> str:
    return dedent(f"""\
        <?xml version="1.0" ?>
        <coverage line-rate="{line_rate}" branch-rate="0" version="7.4.0" timestamp="0">
          <packages/>
        </coverage>
    """)


def _run(tmp_path: Path, repos: dict[str, float | None], baseline: str | None,
         env_extra: dict | None = None):
    """
    repos: {repo_name: line_rate_or_None} — None means no coverage.xml file.
    baseline: text of last month's report, or None for no baseline.
    """
    out_dir = tmp_path / "out"
    repos_root = tmp_path / "repos"
    repos_root.mkdir(parents=True, exist_ok=True)
    repo_list = []
    for name, rate in repos.items():
        repo_dir = repos_root / name
        repo_dir.mkdir(parents=True, exist_ok=True)
        repo_list.append(f"{name}:{repo_dir}")
        if rate is not None:
            (repo_dir / "coverage.xml").write_text(_coverage_xml(rate))

    if baseline is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "coverage-drift-2026-03.md").write_text(baseline)

    env = os.environ.copy()
    env["COVERAGE_DRIFT_OUT_DIR"] = str(out_dir)
    env["COVERAGE_DRIFT_MONTH"] = "2026-04"
    env["COVERAGE_DRIFT_PREV_MONTH"] = "2026-03"
    env["COVERAGE_DRIFT_REPOS"] = ",".join(repo_list)
    env["REPO_ROOT"] = str(tmp_path)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        ["bash", str(SCRIPT)],
        env=env, capture_output=True, text=True, timeout=15,
    )
    return r, out_dir / "coverage-drift-2026-04.md"


def _baseline(rows: dict[str, float]) -> str:
    lines = [
        "# coverage-drift — 2026-03",
        "",
        "**Status:** GREEN — seed baseline.",
        "",
        "## Per-repo coverage",
        "",
        "| Repo | This month | Last month | Δ (pp) | Flag |",
        "|------|-----------|-----------|--------|------|",
    ]
    for name, pct in rows.items():
        lines.append(f"| {name} | {pct:.1f}% | — | — | |")
    lines.append("")
    return "\n".join(lines)


def test_coverage_drift_green_when_stable(tmp_path):
    baseline = _baseline({"repo_a": 80.0, "repo_b": 75.0})
    r, report = _run(tmp_path, {"repo_a": 0.799, "repo_b": 0.751}, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** GREEN" in body


def test_coverage_drift_yellow_when_warn(tmp_path):
    baseline = _baseline({"repo_a": 80.0})
    r, report = _run(tmp_path, {"repo_a": 0.778}, baseline)  # 77.8% = −2.2pp
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** YELLOW" in body


def test_coverage_drift_red_when_block(tmp_path):
    baseline = _baseline({"repo_a": 80.0})
    r, report = _run(tmp_path, {"repo_a": 0.70}, baseline)  # 70% = −10pp
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** RED" in body


def test_coverage_drift_parses_coverage_xml(tmp_path):
    baseline = _baseline({"repo_a": 85.0})
    r, report = _run(tmp_path, {"repo_a": 0.8475}, baseline)  # 84.75%
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "84.8%" in body or "84.75%" in body


def test_coverage_drift_handles_missing_baseline(tmp_path):
    r, report = _run(tmp_path, {"repo_a": 0.80}, baseline=None)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "Status:** GREEN" in body
    assert "—" in body  # last-month column empty
    assert "repo_a" in body


def test_coverage_drift_handles_missing_coverage_xml(tmp_path):
    baseline = _baseline({"repo_a": 80.0})
    r, report = _run(tmp_path, {"repo_a": None}, baseline)
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "no data" in body
