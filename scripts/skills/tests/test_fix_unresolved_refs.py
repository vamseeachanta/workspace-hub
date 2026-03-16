#!/usr/bin/env python3
"""Tests for fix_unresolved_refs.py."""
import tempfile
import yaml
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from fix_unresolved_refs import build_skill_index, find_unresolved_refs, fix_ref


def _write_skill(tmp: Path, rel_path: str, frontmatter: dict, body: str = "") -> Path:
    """Helper: write a SKILL.md with given frontmatter under tmp/rel_path."""
    p = tmp / rel_path / "SKILL.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    fm = yaml.dump(frontmatter, default_flow_style=False)
    p.write_text(f"---\n{fm}---\n{body}")
    return p


def test_build_index_finds_all_skills():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / ".claude" / "skills"
        _write_skill(root, "ai/prompting/foo", {"name": "foo", "description": "Foo skill"})
        _write_skill(root, "data/bar", {"name": "bar", "description": "Bar skill"})
        idx = build_skill_index(root)
        assert "foo" in idx
        assert "bar" in idx
        assert idx["foo"].name == "SKILL.md"


def test_find_unresolved_refs_detects_broken():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / ".claude" / "skills"
        _write_skill(root, "ai/alpha", {
            "name": "alpha",
            "description": "Alpha",
            "related_skills": ["beta", "nonexistent"],
        })
        _write_skill(root, "data/beta", {"name": "beta", "description": "Beta"})
        idx = build_skill_index(root)
        unresolved = find_unresolved_refs(root, idx)
        assert len(unresolved) == 1
        assert unresolved[0]["skill"] == "alpha"
        assert "nonexistent" in unresolved[0]["unresolved"]
        assert "beta" not in unresolved[0]["unresolved"]


def test_find_unresolved_refs_clean():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / ".claude" / "skills"
        _write_skill(root, "ai/alpha", {
            "name": "alpha",
            "description": "Alpha",
            "related_skills": ["beta"],
        })
        _write_skill(root, "data/beta", {"name": "beta", "description": "Beta"})
        idx = build_skill_index(root)
        assert find_unresolved_refs(root, idx) == []


def test_fix_ref_removes_broken_ref():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / ".claude" / "skills"
        p = _write_skill(root, "ai/alpha", {
            "name": "alpha",
            "description": "Alpha",
            "related_skills": ["beta", "nonexistent"],
        })
        _write_skill(root, "data/beta", {"name": "beta", "description": "Beta"})
        idx = build_skill_index(root)
        result = fix_ref(p, ["nonexistent"], apply=True)
        assert result["removed"] == ["nonexistent"]
        content = p.read_text()
        meta = yaml.safe_load(content.split("---", 2)[1])
        assert "nonexistent" not in meta["related_skills"]
        assert "beta" in meta["related_skills"]


def test_fix_ref_dry_run_no_write():
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp) / ".claude" / "skills"
        p = _write_skill(root, "ai/alpha", {
            "name": "alpha",
            "description": "Alpha",
            "related_skills": ["nonexistent"],
        })
        original = p.read_text()
        result = fix_ref(p, ["nonexistent"], apply=False)
        assert result["removed"] == ["nonexistent"]
        assert p.read_text() == original
