"""TDD tests for strategic scoring engine.

Tests written BEFORE implementation per TDD rules.
Fixtures: tests/strategic/fixtures/WRK-TEST-*.md
"""

import os
import sys
from pathlib import Path

import pytest
import yaml

# Add scripts dir so we can import the module
REPO_ROOT = Path(__file__).parents[2]
SCRIPTS_DIR = REPO_ROOT / "scripts" / "strategic"
sys.path.insert(0, str(SCRIPTS_DIR))

FIXTURES_DIR = Path(__file__).parent / "fixtures"
CONFIG_DIR = REPO_ROOT / "config" / "strategic-prioritization"


@pytest.fixture
def track_mapping():
    with open(CONFIG_DIR / "track-mapping.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture
def scoring_weights():
    with open(CONFIG_DIR / "scoring-weights.yaml") as f:
        return yaml.safe_load(f)


@pytest.fixture
def all_fixtures():
    """Parse all fixture WRK files."""
    from strategic_score import parse_wrk_frontmatter

    wrks = {}
    for p in sorted(FIXTURES_DIR.glob("WRK-TEST-*.md")):
        wrks[p.stem] = parse_wrk_frontmatter(p)
    return wrks


# ── Frontmatter Parsing ──────────────────────────────────────────────────


class TestParseWrkFrontmatter:
    def test_parses_basic_fields(self):
        from strategic_score import parse_wrk_frontmatter

        wrk = parse_wrk_frontmatter(FIXTURES_DIR / "WRK-TEST-001.md")
        assert wrk["id"] == "WRK-TEST-001"
        assert wrk["priority"] == "high"
        assert wrk["category"] == "engineering"
        assert wrk["status"] == "pending"

    def test_parses_blocked_by_list(self):
        from strategic_score import parse_wrk_frontmatter

        wrk = parse_wrk_frontmatter(FIXTURES_DIR / "WRK-TEST-004.md")
        assert wrk["blocked_by"] == ["WRK-TEST-001"]

    def test_parses_empty_blocked_by(self):
        from strategic_score import parse_wrk_frontmatter

        wrk = parse_wrk_frontmatter(FIXTURES_DIR / "WRK-TEST-001.md")
        assert wrk["blocked_by"] == []

    def test_returns_none_for_missing_file(self):
        from strategic_score import parse_wrk_frontmatter

        result = parse_wrk_frontmatter(FIXTURES_DIR / "WRK-NONEXISTENT.md")
        assert result is None


# ── Track Classification ─────────────────────────────────────────────────


class TestClassifyTrack:
    def test_engineering_category(self, track_mapping):
        from strategic_score import classify_track

        assert classify_track("engineering", track_mapping) == "engineering"

    def test_harness_category(self, track_mapping):
        from strategic_score import classify_track

        assert classify_track("harness", track_mapping) == "harness"

    def test_data_maps_to_market(self, track_mapping):
        from strategic_score import classify_track

        assert classify_track("data", track_mapping) == "market"

    def test_maintenance_maps_to_other(self, track_mapping):
        from strategic_score import classify_track

        assert classify_track("maintenance", track_mapping) == "other"

    def test_unknown_category_maps_to_other(self, track_mapping):
        from strategic_score import classify_track

        assert classify_track("completely-unknown", track_mapping) == "other"

    def test_slash_category(self, track_mapping):
        from strategic_score import classify_track

        assert classify_track("harness/skills", track_mapping) == "harness"


# ── RICE Scoring ─────────────────────────────────────────────────────────


class TestScoreRice:
    def test_high_priority_medium_complexity(self, scoring_weights):
        from strategic_score import score_rice

        wrk = {
            "priority": "high",
            "complexity": "medium",
            "status": "pending",
        }
        score = score_rice(wrk, scoring_weights)
        # reach=4, impact=4, confidence=3, effort=3
        # RICE = (4 * 4 * 3) / 3 = 16.0
        # Normalized to 0-100: (16 / max_possible) * 100
        # max_possible = (5*5*5)/1 = 125
        # normalized = (16/125)*100 = 12.8 — but we normalize differently
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_critical_simple_scores_highest(self, scoring_weights):
        from strategic_score import score_rice

        top = score_rice(
            {"priority": "critical", "complexity": "simple", "status": "working"},
            scoring_weights,
        )
        bottom = score_rice(
            {"priority": "low", "complexity": "complex", "status": "pending"},
            scoring_weights,
        )
        assert top > bottom

    def test_working_status_higher_confidence(self, scoring_weights):
        from strategic_score import score_rice

        working = score_rice(
            {"priority": "medium", "complexity": "medium", "status": "working"},
            scoring_weights,
        )
        pending = score_rice(
            {"priority": "medium", "complexity": "medium", "status": "pending"},
            scoring_weights,
        )
        assert working > pending


# ── WSJF Scoring ─────────────────────────────────────────────────────────


class TestScoreWsjf:
    def test_with_blocked_by(self, scoring_weights):
        from strategic_score import score_wsjf

        wrk = {
            "priority": "high",
            "complexity": "medium",
            "blocked_by": ["WRK-999"],
        }
        score = score_wsjf(wrk, scoring_weights)
        assert isinstance(score, float)
        assert 0 <= score <= 100

    def test_critical_scores_higher_than_low(self, scoring_weights):
        from strategic_score import score_wsjf

        high = score_wsjf(
            {"priority": "critical", "complexity": "simple", "blocked_by": ["X"]},
            scoring_weights,
        )
        low = score_wsjf(
            {"priority": "low", "complexity": "complex", "blocked_by": ["X"]},
            scoring_weights,
        )
        assert high > low


# ── Enablement Bonus ─────────────────────────────────────────────────────


class TestCalculateEnablement:
    def test_item_with_downstream_deps(self, all_fixtures):
        from strategic_score import calculate_enablement

        # WRK-TEST-004 is blocked_by WRK-TEST-001
        # So WRK-TEST-001 enables 1 downstream item
        count = calculate_enablement("WRK-TEST-001", all_fixtures)
        assert count == 1

    def test_item_with_no_downstream(self, all_fixtures):
        from strategic_score import calculate_enablement

        count = calculate_enablement("WRK-TEST-002", all_fixtures)
        assert count == 0


# ── Track Balance ────────────────────────────────────────────────────────


class TestCalculateTrackBalance:
    def test_balance_with_fixture_data(self, track_mapping, scoring_weights):
        from strategic_score import calculate_track_balance, classify_track

        # Simulate: 2 engineering (001,004), 1 harness (002),
        # 2 market/data (003,006), 1 other/maintenance (005)
        track_counts = {"engineering": 2, "harness": 1, "market": 2, "other": 1}
        targets = scoring_weights["track_targets"]

        balance = calculate_track_balance(track_counts, targets)

        assert "engineering" in balance
        assert "harness" in balance
        assert "market" in balance
        assert "other" in balance
        # engineering: 2/6 = 33.3%, target 50% → under_served
        assert balance["engineering"]["status"] == "under_served"
        # harness: 1/6 = 16.7%, target 20% → under_served
        assert balance["harness"]["status"] == "under_served"

    def test_empty_counts(self, scoring_weights):
        from strategic_score import calculate_track_balance

        targets = scoring_weights["track_targets"]
        balance = calculate_track_balance({}, targets)
        # All tracks should exist with 0 actual
        for track in targets:
            assert balance[track]["actual_pct"] == 0


# ── Full Scoring Pipeline ────────────────────────────────────────────────


class TestApplyBonuses:
    def test_roadmap_bonus_applied(self, scoring_weights):
        from strategic_score import apply_bonuses

        wrk = {"id": "WRK-376", "category": "engineering"}
        balance = {"engineering": {"delta": 0}}
        score = apply_bonuses(
            base=50.0,
            wrk=wrk,
            critical_ids=scoring_weights["roadmap_critical_ids"],
            enablement_count=0,
            track_balance=balance,
            track="engineering",
            weights=scoring_weights,
        )
        assert score == 50.0 + 15  # roadmap bonus

    def test_enablement_capped(self, scoring_weights):
        from strategic_score import apply_bonuses

        wrk = {"id": "WRK-999", "category": "engineering"}
        balance = {"engineering": {"delta": 0}}
        score = apply_bonuses(
            base=50.0,
            wrk=wrk,
            critical_ids=[],
            enablement_count=5,  # 5 * 10 = 50, but cap is 30
            track_balance=balance,
            track="engineering",
            weights=scoring_weights,
        )
        assert score == 50.0 + 30  # capped at 30

    def test_track_penalty_for_overserved(self, scoring_weights):
        from strategic_score import apply_bonuses

        wrk = {"id": "WRK-999", "category": "harness"}
        # harness is 15pp over target
        balance = {"harness": {"delta": 15}}
        score = apply_bonuses(
            base=50.0,
            wrk=wrk,
            critical_ids=[],
            enablement_count=0,
            track_balance=balance,
            track="harness",
            weights=scoring_weights,
        )
        # penalty = 15 * 0.5 = 7.5
        assert score == 50.0 - 7.5

    def test_score_never_below_zero(self, scoring_weights):
        from strategic_score import apply_bonuses

        wrk = {"id": "WRK-999", "category": "harness"}
        balance = {"harness": {"delta": 80}}
        score = apply_bonuses(
            base=5.0,
            wrk=wrk,
            critical_ids=[],
            enablement_count=0,
            track_balance=balance,
            track="harness",
            weights=scoring_weights,
        )
        assert score >= 0


# ── End-to-End Ranking ───────────────────────────────────────────────────


class TestRankWrks:
    def test_rank_fixtures(self, track_mapping, scoring_weights):
        from strategic_score import rank_wrks

        ranked = rank_wrks(FIXTURES_DIR, track_mapping, scoring_weights)
        assert len(ranked) >= 5  # 6 fixtures, but archived may be filtered
        # Each item has required fields
        for item in ranked:
            assert "id" in item
            assert "track" in item
            assert "strategic_score" in item
            assert "score_breakdown" in item
            assert "scoring_method" in item

    def test_ranked_in_descending_order(self, track_mapping, scoring_weights):
        from strategic_score import rank_wrks

        ranked = rank_wrks(FIXTURES_DIR, track_mapping, scoring_weights)
        scores = [r["strategic_score"] for r in ranked]
        assert scores == sorted(scores, reverse=True)

    def test_blocked_item_uses_wsjf(self, track_mapping, scoring_weights):
        from strategic_score import rank_wrks

        ranked = rank_wrks(FIXTURES_DIR, track_mapping, scoring_weights)
        wrk004 = next(r for r in ranked if r["id"] == "WRK-TEST-004")
        assert wrk004["scoring_method"] == "wsjf"
