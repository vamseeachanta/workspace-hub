"""TDD — scripts/ai/build_skill_index.py (#3190): full-tree index, precedence, determinism."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MOD = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "build_skill_index.py"
spec = importlib.util.spec_from_file_location("build_skill_index", MOD)
mod = importlib.util.module_from_spec(spec)
sys.modules["build_skill_index"] = mod
spec.loader.exec_module(mod)


def _skill(d: Path, rel: str, text: str):
    p = d / rel / "SKILL.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


@pytest.fixture
def skills(tmp_path):
    d = tmp_path / "skills"
    d.mkdir()
    _skill(d, "dev/fm", "---\nname: FM\nwhen_to_use: [alpha, beta]\n---\nbody\n")
    _skill(d, "dev/sec", "---\nname: Sec\ndescription: d\n---\n## When to Use\n- gamma delta\n## Other\nx\n")
    _skill(d, "ops/trig", "---\nname: Trig\n---\n## Trigger\nepsilon\n")
    _skill(d, "ops/back", "---\nname: Back\ndescription: zeta backfill\n---\nno section here\n")
    _skill(d, "_archive/old", "---\nname: Old\n---\n## When to Use\nshould be skipped\n")
    return d


def _by_id(entries):
    return {e["id"]: e for e in entries}


def test_scans_active_excludes_archive(skills):
    e = _by_id(mod.build_entries(skills))
    assert set(e) == {"dev/fm", "dev/sec", "ops/trig", "ops/back"}
    assert "_archive/old" not in e


def test_when_to_use_precedence_and_source(skills):
    e = _by_id(mod.build_entries(skills))
    assert e["dev/fm"]["when_to_use_source"] == "frontmatter"
    assert "alpha" in e["dev/fm"]["when_to_use"]
    assert e["dev/sec"]["when_to_use_source"] == "section"
    assert "gamma" in e["dev/sec"]["when_to_use"]
    assert e["ops/trig"]["when_to_use_source"] == "trigger"
    assert "epsilon" in e["ops/trig"]["when_to_use"]
    assert e["ops/back"]["when_to_use_source"] == "backfill"
    assert "zeta" in e["ops/back"]["when_to_use"]  # from description


def test_family_derived(skills):
    e = _by_id(mod.build_entries(skills))
    assert e["dev/fm"]["family"] == "dev"
    assert e["ops/trig"]["family"] == "ops"


def test_sorted_by_id_and_deterministic(skills):
    ids = [x["id"] for x in mod.build_entries(skills)]
    assert ids == sorted(ids)
    assert mod.render(mod.build_entries(skills)) == mod.render(mod.build_entries(skills))


def test_no_timestamp_in_header(skills):
    import re
    assert not re.search(r"20\d\d-\d\d-\d\dT", mod.render(mod.build_entries(skills)))
