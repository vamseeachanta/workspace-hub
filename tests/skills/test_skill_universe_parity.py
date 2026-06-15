"""#3139 core AC: after routing both scripts through _skill_identity, the
scanner universe == the report universe, and the _archived-induced
gmail-data-extraction collision is gone. Runs against the live .claude/skills.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(subprocess.check_output(
    ["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).parent, text=True).strip())
SKILLS_DIR = REPO / "scripts" / "skills"
LIVE_SKILLS = REPO / ".claude" / "skills"


def _load(name, path):
    if str(SKILLS_DIR) not in sys.path:
        sys.path.insert(0, str(SKILLS_DIR))
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def libs():
    ident = _load("_skill_identity", SKILLS_DIR / "_skill_identity.py")
    scanner = _load("siscan_p", SKILLS_DIR / "skill-invocation-scanner.py")
    report = _load("surep_p", SKILLS_DIR / "skill-usage-report.py")
    return ident, scanner, report


@pytest.mark.skipif(not LIVE_SKILLS.exists(), reason="no live skills tree")
def test_scanner_and_report_share_one_universe(libs):
    ident, scanner, report = libs
    canonical = set(ident.discover_skills(LIVE_SKILLS))
    # scanner uses the shared discover_skills now
    assert set(scanner.discover_skills(LIVE_SKILLS)) == canonical
    # report's scan_skills keys must equal the canonical universe
    report_keys = set(report.scan_skills(LIVE_SKILLS).keys())
    assert report_keys == canonical, (
        f"universe mismatch: only-canonical={sorted(canonical - report_keys)[:5]}, "
        f"only-report={sorted(report_keys - canonical)[:5]}")


@pytest.mark.skipif(not LIVE_SKILLS.exists(), reason="no live skills tree")
def test_no_archived_leak(libs):
    ident, _, _ = libs
    universe = ident.discover_skills(LIVE_SKILLS)
    assert not any("/_archived/" in s or s.startswith("_archived/") for s in universe)


@pytest.mark.skipif(not LIVE_SKILLS.exists(), reason="no live skills tree")
def test_gmail_data_extraction_collision_gone(libs):
    ident, _, _ = libs
    rels = [s for s in ident.discover_skills(LIVE_SKILLS)
            if ident.derive_short_name(LIVE_SKILLS / s / "SKILL.md") == "gmail-data-extraction"]
    assert rels == ["email/gmail-data-extraction"], f"collision not resolved: {rels}"
