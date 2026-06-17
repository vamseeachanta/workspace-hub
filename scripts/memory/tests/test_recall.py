"""TDD — recall.py (#3189): keyword + class filter, deterministic cross-provider ordering."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MOD_PATH = Path(__file__).resolve().parents[1] / "recall.py"
spec = importlib.util.spec_from_file_location("recall", MOD_PATH)
mod = importlib.util.module_from_spec(spec)
sys.modules["recall"] = mod
spec.loader.exec_module(mod)  # also puts scripts/memory/ on sys.path for build_topics_index import


@pytest.fixture
def topics(tmp_path):
    d = tmp_path / "topics"
    d.mkdir()
    (d / "feedback_worktree.md").write_text(
        "---\nname: Worktree race\ndescription: git worktree gitlink hazard\ntype: feedback\n---\n"
        "worktree worktree worktree submodule gitlink\n")
    (d / "feedback_stash.md").write_text(
        "---\nname: Stash\ndescription: stash pop conflict\ntype: feedback\n---\nstash worktree once\n")
    (d / "project_x.md").write_text(
        "---\nname: Proj X\ndescription: unrelated\ntype: project\n---\nworktree mention\n")
    (d / "INDEX.md").write_text("- [x](feedback_worktree.md) worktree\n")  # must be ignored
    return d


def test_keyword_match_ranks_by_count(topics):
    hits = mod.recall(topics, ["worktree"])
    names = [h[1] for h in hits]
    assert names[0] == "feedback_worktree.md"  # most occurrences -> top
    assert "INDEX.md" not in names


def test_class_filter(topics):
    hits = mod.recall(topics, ["worktree"], cls="feedback")
    assert all(n.startswith("feedback_") for _, n, *_ in hits)
    assert "project_x.md" not in [h[1] for h in hits]


def test_no_match_empty(topics):
    assert mod.recall(topics, ["zzznomatch"]) == []


def test_deterministic_ordering_planted_oracle(topics):
    # Cross-provider parity: identical ordered set on repeat (the provider that
    # invokes recall does not change the result). Planted oracle = feedback_worktree.
    r1 = mod.recall(topics, ["worktree"])
    r2 = mod.recall(topics, ["worktree"])
    assert r1 == r2
    assert r1[0][1] == "feedback_worktree.md"


def test_tie_break_by_filename(topics):
    # two files with equal score break ties by filename (stable across providers)
    hits = mod.recall(topics, ["once", "mention"])  # one hit each in stash + project_x
    names = [h[1] for h in hits]
    assert names == sorted(names, key=lambda n: n)  # filename order among equal scores
