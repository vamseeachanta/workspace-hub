"""TDD tests for scripts/skills/skill-invocation-scanner.py (#2320).

Fixture-driven: tests/skills/fixtures/sample_session.jsonl provides a
minimal but representative session log with a PII-bearing file path
(to verify PII-safe output), a malformed line, events with and without
skill_name, multiple sessions, and 5 calendar days of coverage.
"""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"],
        cwd=Path(__file__).parent,
        text=True,
    ).strip()
)
SCANNER_PATH = REPO_ROOT / "scripts" / "skills" / "skill-invocation-scanner.py"
FIXTURE_SESSION = Path(__file__).parent / "fixtures" / "sample_session.jsonl"


def _load_scanner():
    """Import the scanner script as a module (it has a hyphen in its filename)."""
    spec = importlib.util.spec_from_file_location("skill_invocation_scanner", SCANNER_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["skill_invocation_scanner"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def scanner():
    assert SCANNER_PATH.exists(), f"scanner not yet written: {SCANNER_PATH}"
    return _load_scanner()


@pytest.fixture
def sessions_dir(tmp_path):
    """Copy the fixture into an isolated dir so scanner picks it up by glob."""
    d = tmp_path / "sessions"
    d.mkdir()
    (d / "session_20260405.jsonl").write_bytes(FIXTURE_SESSION.read_bytes())
    return d


@pytest.fixture
def skills_root(tmp_path):
    """Minimal .claude/skills/ replica with three skills."""
    root = tmp_path / "skills"
    for skill_dir in ("foo/alpha", "bar/beta", "never/invoked"):
        p = root / skill_dir
        p.mkdir(parents=True)
        (p / "SKILL.md").write_text(f"---\nname: {skill_dir}\n---\nbody\n")
    return root


def test_scan_counts_event_when_skill_name_present(scanner, sessions_dir):
    event_ts, session_ts, coverage_days = scanner.scan_sessions(sessions_dir)
    assert len(event_ts["foo/alpha"]) == 4
    assert len(event_ts["bar/beta"]) == 1


def test_scan_ignores_events_without_skill_name(scanner, sessions_dir):
    event_ts, _, _ = scanner.scan_sessions(sessions_dir)
    for sn in event_ts:
        assert sn, "empty skill_name should never be a key"


def test_scan_counts_distinct_sessions(scanner, sessions_dir):
    _, session_ts, _ = scanner.scan_sessions(sessions_dir)
    assert len(session_ts["foo/alpha"]) == 3
    assert len(session_ts["bar/beta"]) == 1


def test_classify_zero_invocations_flags_dead(scanner, sessions_dir, skills_root):
    event_ts, session_ts, coverage = scanner.scan_sessions(sessions_dir)
    rows = scanner.classify(event_ts, session_ts, coverage, skills_root)
    never = next(r for r in rows if r["skill"] == "never/invoked")
    assert never["invocations_available_days"] == 0
    assert never["session_count_available_days"] == 0
    assert never["last_used"] is None
    assert never["days_since_last_use"] is None


def test_classify_reports_coverage_days(scanner, sessions_dir, skills_root):
    _, _, coverage = scanner.scan_sessions(sessions_dir)
    assert coverage >= 4


def test_malformed_jsonl_line_skipped(scanner, sessions_dir):
    event_ts, _, _ = scanner.scan_sessions(sessions_dir)
    assert len(event_ts["foo/alpha"]) == 4


def test_output_contains_no_file_paths(scanner, sessions_dir, skills_root, tmp_path):
    out_file = tmp_path / "out.json"
    event_ts, session_ts, coverage = scanner.scan_sessions(sessions_dir)
    rows = scanner.classify(event_ts, session_ts, coverage, skills_root)
    scanner.write_output({"coverage_days": coverage, "generated_at": "test", "rows": rows}, out_file)

    raw = out_file.read_text()
    assert "/home/user/secret.txt" not in raw
    data = json.loads(raw)
    banned_keys = {"file", "cwd", "prompt", "tool_input", "stdout", "stderr"}

    def walk(x):
        if isinstance(x, dict):
            for k, v in x.items():
                assert k not in banned_keys, f"banned key surfaced: {k}"
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(data)


def test_integration_tier_demotion_requires_coverage(scanner):
    assert scanner.should_demote(session_count=0, coverage_days=5, min_coverage=14) is False
    assert scanner.should_demote(session_count=0, coverage_days=20, min_coverage=14) is True
    assert scanner.should_demote(session_count=3, coverage_days=20, min_coverage=14) is False
