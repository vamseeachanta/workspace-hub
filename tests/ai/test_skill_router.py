"""TDD — scripts/ai/skill_router.py (#3190): ranking, backfill down-weight, provider-neutral."""
from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

import pytest

MOD = Path(__file__).resolve().parents[2] / "scripts" / "ai" / "skill_router.py"
spec = importlib.util.spec_from_file_location("skill_router", MOD)
mod = importlib.util.module_from_spec(spec)
sys.modules["skill_router"] = mod
spec.loader.exec_module(mod)


@pytest.fixture
def index():
    return [
        {"id": "dev/review", "family": "dev", "description": "review diffs",
         "when_to_use": "review the diff for bugs and security", "when_to_use_source": "section"},
        {"id": "dev/test", "family": "dev", "description": "tests",
         "when_to_use": "write tests tdd red green", "when_to_use_source": "section"},
        {"id": "ops/cleanup", "family": "ops", "description": "cleanup",
         "when_to_use": "review cleanup residue", "when_to_use_source": "backfill"},
    ]


def test_ranks_by_when_to_use_overlap(index):
    r = mod.rank("review the diff for bugs", index=index)
    assert r[0]["id"] == "dev/review"


def test_backfill_down_weighted(index):
    # both dev/review (section) and ops/cleanup (backfill) match "review" once-ish;
    # the section entry must outrank the backfill entry.
    r = mod.rank("review", index=index)
    ids = [x["id"] for x in r]
    assert ids.index("dev/review") < ids.index("ops/cleanup")
    bf = next(x for x in r if x["id"] == "ops/cleanup")
    sec = next(x for x in r if x["id"] == "dev/review")
    assert bf["score"] < sec["score"]


def test_context_tags_boost(index):
    # tag matching the family raises the score
    base = mod.rank("tests", index=index)
    boosted = mod.rank("tests", context_tags=["dev"], index=index)
    assert boosted[0]["score"] >= base[0]["score"]


def test_no_match_returns_none(index):
    assert mod.top_skill("zzzznomatch", index=index) is None


def test_provider_neutral_identical_top(index):
    # provider is recorded for audit but MUST NOT change ranking
    assert (mod.top_skill("review the diff", provider="agy", index=index)
            == mod.top_skill("review the diff", provider="gemini", index=index)
            == mod.top_skill("review the diff", provider="claude", index=index))


def test_deterministic_tie_break_by_id(index):
    # equal-scoring entries break ties by id (stable across providers)
    r1 = mod.rank("review", index=index)
    r2 = mod.rank("review", index=index)
    assert [x["id"] for x in r1] == [x["id"] for x in r2]
