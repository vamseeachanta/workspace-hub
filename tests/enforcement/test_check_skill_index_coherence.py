"""Tests for the skill-index coherence gate (#3208)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
MOD_PATH = REPO_ROOT / "scripts" / "enforcement" / "check-skill-index-coherence.py"


def _load():
    spec = importlib.util.spec_from_file_location("check_skill_index_coherence", MOD_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _skill(skills_dir: Path, rel: str, body: str = "x") -> None:
    d = skills_dir / rel
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(body, encoding="utf-8")


def _fixture(tmp_path: Path, curated_nodes, full_entries, *, tree=None):
    skills = tmp_path / ".claude" / "skills"
    skills.mkdir(parents=True)
    for rel, body in (tree or {}).items():
        _skill(skills, rel, body)
    kg = tmp_path / "kg.yaml"
    kg.write_text(yaml.safe_dump({"nodes": [{"id": i} for i in curated_nodes]}))
    gi = tmp_path / "gi.yaml"
    gi.write_text(yaml.safe_dump({"by_domain": {"d": curated_nodes}}))
    full = tmp_path / "full.yaml"
    full.write_text(yaml.safe_dump({"skills": full_entries}))
    return skills, kg, gi, full


def _wire(mod, skills, kg, gi, full, monkeypatch):
    monkeypatch.setattr(mod, "SKILLS_DIR", skills)
    monkeypatch.setattr(mod, "KNOWLEDGE_GRAPH", kg)
    monkeypatch.setattr(mod, "GRAPH_INDEX", gi)
    monkeypatch.setattr(mod, "FULL_INDEX", full)


# --- (a) coherence -----------------------------------------------------------

def test_a_clean_passes(tmp_path, monkeypatch):
    mod = _load()
    skills, kg, gi, full = _fixture(
        tmp_path, ["repo/alpha"],
        [{"id": "fam/alpha", "when_to_use_source": "frontmatter"}],
        tree={"fam/alpha": "x"})
    _wire(mod, skills, kg, gi, full, monkeypatch)
    monkeypatch.setattr(mod, "KNOWN_STALE_CURATED", set())
    fails: list[str] = []
    mod.check_a_coherence(fails)
    assert fails == []


def test_a_removed_skill_fails(tmp_path, monkeypatch):
    mod = _load()
    skills, kg, gi, full = _fixture(
        tmp_path, ["repo/ghost"], [{"id": "fam/alpha"}], tree={"fam/alpha": "x"})
    _wire(mod, skills, kg, gi, full, monkeypatch)
    monkeypatch.setattr(mod, "KNOWN_STALE_CURATED", set())
    fails: list[str] = []
    mod.check_a_coherence(fails)
    assert any("ghost" in f for f in fails)


def test_a_namespace_diff_does_not_false_fail(tmp_path, monkeypatch):
    # curated repo/alpha vs full fam/alpha — same basename → coherent
    mod = _load()
    skills, kg, gi, full = _fixture(
        tmp_path, ["some-repo/alpha"], [{"id": "deep/family/alpha"}],
        tree={"deep/family/alpha": "x"})
    _wire(mod, skills, kg, gi, full, monkeypatch)
    monkeypatch.setattr(mod, "KNOWN_STALE_CURATED", set())
    fails: list[str] = []
    mod.check_a_coherence(fails)
    assert fails == []


def test_a_archived_family_resolves(tmp_path, monkeypatch):
    # skill lives in an excluded _* family (not in full index) but exists in tree
    mod = _load()
    skills, kg, gi, full = _fixture(
        tmp_path, ["repo/archived-skill"], [{"id": "fam/other"}],
        tree={"fam/other": "x", "_internal/builders/archived-skill": "x"})
    _wire(mod, skills, kg, gi, full, monkeypatch)
    monkeypatch.setattr(mod, "KNOWN_STALE_CURATED", set())
    fails: list[str] = []
    mod.check_a_coherence(fails)
    assert fails == []  # found in tree despite absent from full index


def test_a_known_stale_allowlisted(tmp_path, monkeypatch):
    mod = _load()
    skills, kg, gi, full = _fixture(
        tmp_path, ["repo/ghost"], [{"id": "fam/alpha"}], tree={"fam/alpha": "x"})
    _wire(mod, skills, kg, gi, full, monkeypatch)
    monkeypatch.setattr(mod, "KNOWN_STALE_CURATED", {"repo/ghost"})
    fails: list[str] = []
    mod.check_a_coherence(fails)
    assert fails == []


# --- (b) advisory ------------------------------------------------------------

def test_b_reports_unrecognized_heading(tmp_path, monkeypatch):
    mod = _load()
    body = "---\nname: x\n---\n# When you use\nfoo\n"  # h1 + variant the generator misses
    skills, kg, gi, full = _fixture(
        tmp_path, [], [{"id": "fam/beta", "when_to_use_source": "backfill"}],
        tree={"fam/beta": body})
    _wire(mod, skills, kg, gi, full, monkeypatch)
    assert "fam/beta" in mod.check_b_advisory()


def test_b_ignores_prose_without_heading(tmp_path, monkeypatch):
    mod = _load()
    body = "use this when you need foo\n"  # prose, no heading
    skills, kg, gi, full = _fixture(
        tmp_path, [], [{"id": "fam/gamma", "when_to_use_source": "backfill"}],
        tree={"fam/gamma": body})
    _wire(mod, skills, kg, gi, full, monkeypatch)
    assert mod.check_b_advisory() == []


# --- integration: real repo is clean ----------------------------------------

def test_real_repo_passes():
    # The committed repo must satisfy the BLOCKING checks (a)+(c).
    mod = _load()
    fails: list[str] = []
    mod.check_a_coherence(fails)
    mod.check_c_determinism(fails)
    assert fails == [], fails
