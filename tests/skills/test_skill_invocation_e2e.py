"""#3112 end-to-end: prove the BUG-1 (emit rel-path) + BUG-2 (scanner outputs
short_name) fixes COMPOSE so apply_invocation_demotion actually fires:
a zero-session skill (≥14d coverage) demotes; a skill with real sessions does not.

Runs the REAL scanner functions + REAL report functions joined on short_name.
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).parent, text=True).strip())


def _load(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def mods():
    scanner = _load(REPO / "scripts/skills/skill-invocation-scanner.py", "siscan")
    report = _load(REPO / "scripts/skills/skill-usage-report.py", "surep")
    return scanner, report


@pytest.fixture
def skills_root(tmp_path):
    root = tmp_path / "skills"
    for rel, nm in (("eng/mooring", "Mooring Design"), ("eng/aqwa", "AQWA")):
        p = root / rel
        p.mkdir(parents=True)
        (p / "SKILL.md").write_text(f"---\nname: {nm}\n---\nbody\n")
    return root


@pytest.fixture
def sessions_dir(tmp_path):
    d = tmp_path / "sessions"
    d.mkdir()
    # aqwa: two Read events 20 days apart (rel-path emit) -> coverage 20d, 1+ session.
    # mooring: NO events -> zero sessions.
    lines = [
        {"ts": "2026-05-20T00:00:00Z", "tool": "Read", "skill_name": "eng/aqwa", "session_id": "s1"},
        {"ts": "2026-06-09T00:00:00Z", "tool": "Read", "skill_name": "eng/aqwa", "session_id": "s2"},
    ]
    (d / "session_20260609.jsonl").write_text("\n".join(json.dumps(x) for x in lines) + "\n")
    return d


def test_demotion_fires_end_to_end(mods, skills_root, sessions_dir, tmp_path):
    scanner, report = mods
    # 1) scan -> rows keyed by short_name (BUG-2 fix)
    event_ts, session_ts, coverage = scanner.scan_sessions(sessions_dir)
    rows = scanner.classify(event_ts, session_ts, coverage, skills_root)
    out = tmp_path / "inv.json"
    out.write_text(json.dumps({"coverage_days": coverage, "rows": rows}))
    assert coverage >= 14, f"need >=14d coverage to demote; got {coverage}"

    # 2) report consumes it; tiers keyed by short_name
    inv = report.load_invocation_data(str(out))
    assert inv.get("aqwa", {}).get("session_count", 0) >= 1
    assert inv.get("mooring design", {}).get("session_count", -1) == 0

    tiers = {"hot": [{"skill": "mooring design", "reference_count": 5},
                     {"skill": "aqwa", "reference_count": 5}],
             "warm": [], "cold": [], "dead": []}
    demoted = report.apply_invocation_demotion(tiers, inv)

    hot = {e["skill"] for e in tiers["hot"]}
    warm = {e["skill"] for e in tiers["warm"]}
    assert demoted == 1, f"expected exactly 1 demotion, got {demoted}"
    assert "aqwa" in hot, "skill with real sessions must NOT demote"
    assert "mooring design" in warm, "zero-session skill must demote HOT->WARM"
