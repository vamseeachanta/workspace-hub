"""TDD for #3139: shared scripts/skills/_skill_identity.py — one canonical
discover_skills() + derive_short_name() for both scanner and report, with the
_archived exclusion fix.
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
LIB = SKILLS_DIR / "_skill_identity.py"


@pytest.fixture
def ident():
    assert LIB.exists(), f"shared lib not yet written: {LIB}"
    if str(SKILLS_DIR) not in sys.path:
        sys.path.insert(0, str(SKILLS_DIR))
    spec = importlib.util.spec_from_file_location("_skill_identity", LIB)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture
def tree(tmp_path):
    root = tmp_path / "skills"
    cases = {
        "dev/y": "---\nname: Y Skill\n---\n",
        "_archive/x": "---\nname: X\n---\n",
        "_core/c": "---\nname: C\n---\n",
        "_internal/i": "---\nname: I\n---\n",
        "email/_archived/gmail-data-extraction": "---\nname: gmail-data-extraction\n---\n",
        "email/gmail-data-extraction": "---\nname: gmail-data-extraction\n---\n",
        "tools/quoted": '---\nname: "Baz"\n---\n',
        "tools/no-fm": "just a body, no frontmatter\n",
    }
    for rel, body in cases.items():
        p = root / rel
        p.mkdir(parents=True)
        (p / "SKILL.md").write_text(body)
    return root


def test_discover_excludes_archive_core_internal(ident, tree):
    got = set(ident.discover_skills(tree))
    assert not any(s.startswith(("_archive/", "_core/", "_internal/")) for s in got)


def test_discover_excludes_archived_trailing_d(ident, tree):
    # The bug fix: _archived (trailing d) must be excluded too.
    got = set(ident.discover_skills(tree))
    assert "email/_archived/gmail-data-extraction" not in got
    assert "email/gmail-data-extraction" in got


def test_discover_opt_out_returns_everything(ident, tree):
    got = set(ident.discover_skills(tree, exclusions=frozenset()))
    assert "_archive/x" in got and "email/_archived/gmail-data-extraction" in got


def test_derive_short_name_from_frontmatter(ident, tree):
    assert ident.derive_short_name(tree / "dev/y/SKILL.md") == "y skill"


def test_derive_short_name_quoted(ident, tree):
    assert ident.derive_short_name(tree / "tools/quoted/SKILL.md") == "baz"


def test_derive_short_name_fallback_basename(ident, tree):
    assert ident.derive_short_name(tree / "tools/no-fm/SKILL.md") == "no-fm"


def test_no_archived_collision(ident, tree):
    # After excluding _archived, gmail-data-extraction maps to exactly one rel-path.
    rels = [s for s in ident.discover_skills(tree)
            if ident.derive_short_name(tree / s / "SKILL.md") == "gmail-data-extraction"]
    assert rels == ["email/gmail-data-extraction"]
