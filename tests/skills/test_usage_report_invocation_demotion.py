"""Unit test for #2320 usage-signal demotion hook in skill-usage-report.py."""

from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).parent, text=True
    ).strip()
)
REPORT_PATH = REPO_ROOT / "scripts" / "skills" / "skill-usage-report.py"


@pytest.fixture
def report():
    spec = importlib.util.spec_from_file_location("skill_usage_report", REPORT_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["skill_usage_report"] = mod
    spec.loader.exec_module(mod)
    return mod


def _make_tiers():
    return {
        "hot": [{"skill": "alive/hot", "reference_count": 10}],
        "warm": [{"skill": "unused/warm", "reference_count": 2}],
        "cold": [{"skill": "unused/cold", "reference_count": 1}],
        "dead": [{"skill": "unused/dead", "reference_count": 0}],
    }


def test_demotes_unused_when_coverage_sufficient(report):
    tiers = _make_tiers()
    inv = {
        "alive/hot":   {"session_count": 5, "coverage_days": 20},
        "unused/warm": {"session_count": 0, "coverage_days": 20},
        "unused/cold": {"session_count": 0, "coverage_days": 20},
    }
    demoted = report.apply_invocation_demotion(tiers, inv)
    assert demoted == 2
    # unused/warm should move warm -> cold; unused/cold should move cold -> dead.
    warm_skills = [e["skill"] for e in tiers["warm"]]
    cold_skills = [e["skill"] for e in tiers["cold"]]
    dead_skills = [e["skill"] for e in tiers["dead"]]
    assert "unused/warm" not in warm_skills
    assert "unused/warm" in cold_skills
    assert "unused/cold" not in cold_skills
    assert "unused/cold" in dead_skills
    # alive/hot must stay put.
    assert "alive/hot" in [e["skill"] for e in tiers["hot"]]


def test_does_not_demote_when_coverage_insufficient(report):
    tiers = _make_tiers()
    inv = {"unused/warm": {"session_count": 0, "coverage_days": 5}}
    demoted = report.apply_invocation_demotion(tiers, inv)
    assert demoted == 0
    assert "unused/warm" in [e["skill"] for e in tiers["warm"]]


def test_load_invocation_data_missing_file_returns_empty(report, tmp_path):
    out = report.load_invocation_data(tmp_path / "does-not-exist.json")
    assert out == {}


def test_load_invocation_data_reshapes_rows(report, tmp_path):
    f = tmp_path / "inv.json"
    f.write_text(json.dumps({
        "coverage_days": 20,
        "rows": [
            {"skill": "a/b", "session_count_available_days": 3},
            {"skill": "c/d", "session_count_available_days": 0},
        ],
    }))
    out = report.load_invocation_data(f)
    assert out["a/b"] == {"session_count": 3, "coverage_days": 20}
    assert out["c/d"] == {"session_count": 0, "coverage_days": 20}
