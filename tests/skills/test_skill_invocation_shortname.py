"""TDD for #3112 BUG-2 fix: skill-invocation-scanner must OUTPUT rows keyed by
short_name (frontmatter `name` lowercased, fallback dir basename) so the join in
skill-usage-report.apply_invocation_demotion (which keys tiers by short_name)
actually matches. Internal event-join stays on the emitted rel-path key.

Empirically, before this fix: scanner output key = rel-path, report tier key =
short_name -> .get() never matches -> demotion is a silent no-op even with data.
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(
    subprocess.check_output(
        ["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).parent, text=True
    ).strip()
)
SCANNER_PATH = REPO_ROOT / "scripts" / "skills" / "skill-invocation-scanner.py"


def _load_scanner():
    spec = importlib.util.spec_from_file_location("skill_invocation_scanner", SCANNER_PATH)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["skill_invocation_scanner"] = mod
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def scanner():
    return _load_scanner()


@pytest.fixture
def skills_root(tmp_path):
    root = tmp_path / "skills"
    # name != rel-path and != basename, to prove short_name derivation.
    p = root / "engineering" / "marine"
    p.mkdir(parents=True)
    (p / "SKILL.md").write_text("---\nname: Mooring Design\n---\nbody\n")
    # a skill with NO frontmatter name -> short_name falls back to basename.
    q = root / "tools" / "xlsx-to-python"
    q.mkdir(parents=True)
    (q / "SKILL.md").write_text("---\ndescription: x\n---\nbody\n")
    return root


def test_derive_short_name_uses_frontmatter_name(scanner, skills_root):
    md = skills_root / "engineering" / "marine" / "SKILL.md"
    assert scanner.derive_short_name(md) == "mooring design"


def test_derive_short_name_falls_back_to_basename(scanner, skills_root):
    md = skills_root / "tools" / "xlsx-to-python" / "SKILL.md"
    assert scanner.derive_short_name(md) == "xlsx-to-python"


def test_classify_outputs_short_name_key(scanner, skills_root):
    # Event emitted with the REL-PATH key (what a bash emit step produces).
    event_ts = {"engineering/marine": ["2026-06-01T00:00:00Z"]}
    session_ts = {"engineering/marine": {"s1"}}
    rows = scanner.classify(event_ts, session_ts, 20, skills_root)
    by_key = {r["skill"]: r for r in rows}
    # BUG-2 fix: output row is keyed by short_name, joinable to report tiers.
    assert "mooring design" in by_key, f"expected short_name key; got {list(by_key)}"
    assert by_key["mooring design"]["invocations_available_days"] == 1
    assert by_key["mooring design"]["session_count_available_days"] == 1
