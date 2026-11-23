#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["pyyaml"]
# ///
"""Tests for scripts/skills/generate_skills_index.py.

Core invariant: every `path:` the generator emits exists in the committed tree, so the
`scripts/curation/audit_skill_currency.py` `index_dangling` metric is 0. Verified two ways:
  * on a self-contained sandbox git fixture (deterministic, no repo coupling), and
  * against the live regenerated `.claude/skills-index.yaml` (regression guard).
"""
from __future__ import annotations

import importlib.util
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
GEN = REPO / "scripts" / "skills" / "generate_skills_index.py"


def _load_generator():
    spec = importlib.util.spec_from_file_location("generate_skills_index", GEN)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _git(repo: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(repo), *args], check=True,
                   capture_output=True, text=True)


def _skill(root: Path, rel: str, name: str | None, desc: str | None) -> None:
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    fm = ["---"]
    if name is not None:
        fm.append(f"name: {name}")
    if desc is not None:
        fm.append(f"description: {desc}")
    fm.append("---")
    p.write_text("\n".join(fm) + "\n# body\n", encoding="utf-8")


def _make_fixture(tmp_path: Path) -> Path:
    repo = tmp_path / "wh"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "t@t.t")
    _git(repo, "config", "user.name", "t")
    # first-class, valid → INCLUDED
    _skill(repo, ".claude/skills/data/cleaner/SKILL.md", "cleaner", "Clean data")
    _skill(repo, ".claude/skills/ai/router/SKILL.md", "router", "Route requests")
    # top-level skill (its own category) → INCLUDED
    _skill(repo, ".claude/skills/loneskill/SKILL.md", "loneskill", "Standalone")
    # deeper than first-class → EXCLUDED (bundled sub-skill)
    _skill(repo, ".claude/skills/data/cleaner/sub/SKILL.md", "sub", "Nested")
    # missing description → EXCLUDED
    _skill(repo, ".claude/skills/ai/nodesc/SKILL.md", "nodesc", None)
    # _archive namespace → EXCLUDED
    _skill(repo, ".claude/skills/_archive/old/SKILL.md", "old", "Retired")
    _git(repo, "add", "-A")
    _git(repo, "commit", "-q", "-m", "fixture")
    # untracked first-class skill (valid frontmatter, but NOT committed) → EXCLUDED
    _skill(repo, ".claude/skills/data/untracked/SKILL.md", "untracked", "Not committed")
    return repo


def test_no_dangling_paths_on_fixture(tmp_path):
    gen = _load_generator()
    repo = _make_fixture(tmp_path)
    categories = gen.build_categories(repo)
    emitted = {sk["path"] for c in categories for sk in c["skills"]}
    # exactly the three first-class, committed, well-formed skills
    assert emitted == {
        ".claude/skills/data/cleaner/SKILL.md",
        ".claude/skills/ai/router/SKILL.md",
        ".claude/skills/loneskill/SKILL.md",
    }
    # the audit's invariant: every emitted path is in the committed tree (no dangling)
    committed = set(gen.committed_skill_md(repo))
    assert emitted <= committed
    assert not (emitted - committed)


def test_counts_match_skill_lists_on_fixture(tmp_path):
    gen = _load_generator()
    repo = _make_fixture(tmp_path)
    categories = gen.build_categories(repo)
    for c in categories:
        assert c["count"] == len(c["skills"])
    names = [c["name"] for c in categories]
    assert names == sorted(names)  # categories alphabetical


def test_render_round_trips_and_has_header(tmp_path):
    gen = _load_generator()
    repo = _make_fixture(tmp_path)
    text = gen.render(gen.build_categories(repo))
    assert text.startswith("# Skills Index for workspace-hub\n")
    assert yaml.safe_load(text)["categories"]  # valid YAML


def test_live_index_has_zero_dangling():
    """Regression guard: the committed live index must have no dangling paths."""
    index = REPO / ".claude" / "skills-index.yaml"
    if not index.exists():
        return
    data = yaml.safe_load(index.read_text()) or {}
    index_paths = {sk.get("path") for c in (data.get("categories") or [])
                   for sk in (c.get("skills") or []) if sk.get("path")}
    gen = _load_generator()
    committed = set(gen.committed_skill_md(REPO))
    dangling = index_paths - committed
    assert not dangling, f"dangling index paths: {sorted(dangling)[:10]}"


if __name__ == "__main__":
    sys.exit(__import__("pytest").main([__file__, "-q"]))
