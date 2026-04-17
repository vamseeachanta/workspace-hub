"""Tests for scripts/cron/ecosystem-rework-retriage.sh — TDD per #2319 plan."""

import json
import os
import subprocess
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "cron" / "ecosystem-rework-retriage.sh"


def _baseline(issues: list[tuple[str, str]]) -> str:
    """Build a fake ecosystem-rework report with Tier-1 rows."""
    lines = [
        "# Ecosystem Rework Candidates — 2026-Q1",
        "",
        "Scope: test fixture.",
        "",
        "## Tier 1 — Top 10 (highest leverage)",
        "",
        "| # | Issue | Title | Mode | Recurrence | Why now |",
        "|---|-------|-------|------|-----------|---------|",
    ]
    for i, (ref, title) in enumerate(issues, 1):
        lines.append(f"| {i} | {ref} | {title} | rework | one-shot | test |")
    lines.append("")
    return "\n".join(lines)


def _run(tmp_path: Path, baseline: str | None, states: dict, env_extra: dict | None = None):
    """
    states: {"wh#1839": {"state": "closed", "days_since_activity": 2, "commits": 5},
             "wh#1803": {"state": "open",   "days_since_activity": 10, "commits": 3},
             ...}
    """
    out_dir = tmp_path / "out"
    if baseline is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "2026-04-16-ecosystem-rework-candidates.md").write_text(baseline)

    states_path = tmp_path / "states.json"
    states_path.write_text(json.dumps(states))

    env = os.environ.copy()
    env["ECOSYSTEM_OUT_DIR"] = str(out_dir)
    env["ECOSYSTEM_QUARTER"] = "2026-Q2"
    env["ECOSYSTEM_ISSUE_STATES"] = str(states_path)
    env["REPO_ROOT"] = str(tmp_path)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(
        ["bash", str(SCRIPT)],
        env=env, capture_output=True, text=True, timeout=15,
    )
    return r, out_dir / "ecosystem-rework-2026-Q2.md"


def test_retriage_finds_last_quarter_report(tmp_path):
    baseline = _baseline([("wh#1", "First candidate")])
    r, report = _run(tmp_path, baseline, {"wh#1": {"state": "open", "days_since_activity": 2, "commits": 0}})
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "2026-04-16-ecosystem-rework-candidates.md" in body or "baseline" in body.lower()


def test_retriage_marks_shipped(tmp_path):
    baseline = _baseline([("wh#100", "Shipped issue")])
    r, report = _run(tmp_path, baseline, {
        "wh#100": {"state": "closed", "days_since_activity": 5, "commits": 8},
    })
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    delta = body.split("## Delta vs last quarter", 1)[1].split("## ", 1)[0]
    # find the wh#100 row
    rows = [ln for ln in delta.splitlines() if "wh#100" in ln]
    assert rows, "no row for wh#100"
    assert "shipped" in rows[0].lower()


def test_retriage_marks_in_progress(tmp_path):
    baseline = _baseline([("wh#101", "In progress")])
    r, report = _run(tmp_path, baseline, {
        "wh#101": {"state": "open", "days_since_activity": 3, "commits": 4},
    })
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    delta = body.split("## Delta vs last quarter", 1)[1].split("## ", 1)[0]
    rows = [ln for ln in delta.splitlines() if "wh#101" in ln]
    assert rows
    assert "in progress" in rows[0].lower() or "in-progress" in rows[0].lower()


def test_retriage_marks_stalled(tmp_path):
    baseline = _baseline([("wh#102", "Stalled issue")])
    r, report = _run(tmp_path, baseline, {
        "wh#102": {"state": "open", "days_since_activity": 120, "commits": 0},
    })
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    delta = body.split("## Delta vs last quarter", 1)[1].split("## ", 1)[0]
    rows = [ln for ln in delta.splitlines() if "wh#102" in ln]
    assert rows
    assert "stalled" in rows[0].lower()


def test_retriage_status_band_on_stalled(tmp_path):
    # 4 stalled → warn=2, block=6 → YELLOW
    baseline = _baseline([(f"wh#{200 + i}", "Issue") for i in range(4)])
    states = {f"wh#{200 + i}": {"state": "open", "days_since_activity": 150, "commits": 0}
              for i in range(4)}
    r, report = _run(tmp_path, baseline, states)
    body = report.read_text()
    assert "Status:** YELLOW" in body


def test_retriage_detects_new_candidate(tmp_path):
    baseline = _baseline([("wh#300", "Existing")])
    states = {
        "wh#300": {"state": "open", "days_since_activity": 3, "commits": 2},
        "wh#999": {"state": "open", "days_since_activity": 1, "commits": 0, "new": True,
                   "title": "Newly opened candidate"},
    }
    r, report = _run(tmp_path, baseline, states)
    body = report.read_text()
    new_sec = body.split("## New Tier-1 candidates", 1)[1].split("## ", 1)[0]
    assert "wh#999" in new_sec


def test_retriage_handles_first_run(tmp_path):
    r, report = _run(tmp_path, baseline=None, states={})
    assert r.returncode == 0, r.stderr
    body = report.read_text()
    assert "first run" in body.lower() or "baseline" in body.lower()
