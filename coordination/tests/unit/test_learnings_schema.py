"""Tests for LearningsFile schema validation."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from coordination.schemas.learnings import LearningEntry, LearningsFile


@pytest.mark.unit
class TestLearningEntry:
    def test_valid_entry(self):
        e = LearningEntry(
            pattern="chore: remove legacy .claude/CLAUDE.md",
            repos="aceengineer-admin,aceengineer-website",
            score=0.35,
            date=datetime(2026, 1, 27, 5, 0, 28),
        )
        assert e.pattern == "chore: remove legacy .claude/CLAUDE.md"
        assert e.score == 0.35

    def test_bare_decimal_score(self):
        """Scores like .304 (no leading zero) should be coerced."""
        e = LearningEntry(
            pattern="test",
            repos="repo",
            score=".304",
            date=datetime(2026, 1, 28),
        )
        assert e.score == pytest.approx(0.304)

    def test_score_out_of_range_high(self):
        with pytest.raises(ValidationError):
            LearningEntry(
                pattern="test",
                repos="repo",
                score=1.5,
                date=datetime(2026, 1, 28),
            )

    def test_score_out_of_range_low(self):
        with pytest.raises(ValidationError):
            LearningEntry(
                pattern="test",
                repos="repo",
                score=-0.1,
                date=datetime(2026, 1, 28),
            )

    def test_score_boundaries(self):
        e0 = LearningEntry(pattern="t", repos="r", score=0.0, date=datetime(2026, 1, 1))
        assert e0.score == 0.0
        e1 = LearningEntry(pattern="t", repos="r", score=1.0, date=datetime(2026, 1, 1))
        assert e1.score == 1.0

    def test_none_repos_coerced(self):
        e = LearningEntry(
            pattern="test",
            repos=None,
            score=0.5,
            date=datetime(2026, 1, 28),
        )
        assert e.repos == ""

    def test_missing_pattern_rejected(self):
        with pytest.raises(ValidationError):
            LearningEntry(
                repos="repo",
                score=0.5,
                date=datetime(2026, 1, 28),
            )

    def test_extra_fields_allowed(self):
        e = LearningEntry(
            pattern="test",
            repos="repo",
            score=0.5,
            date=datetime(2026, 1, 28),
            source="git",
        )
        assert e.pattern == "test"


@pytest.mark.unit
class TestLearningsFile:
    def test_valid_list(self):
        data = [
            {
                "pattern": "chore: sync",
                "repos": "repo1,repo2",
                "score": 0.5,
                "date": "2026-01-27T05:00:28-06:00",
            },
            {
                "pattern": "feat: add feature",
                "repos": "repo3",
                "score": 0.8,
                "date": "2026-01-28T05:00:00-06:00",
            },
        ]
        lf = LearningsFile.model_validate(data)
        assert len(lf.root) == 2
        assert lf.root[0].pattern == "chore: sync"

    def test_empty_list(self):
        lf = LearningsFile.model_validate([])
        assert len(lf.root) == 0

    def test_invalid_entry_in_list(self):
        data = [
            {
                "pattern": "valid",
                "repos": "repo",
                "score": 0.5,
                "date": "2026-01-27T05:00:00Z",
            },
            {
                "pattern": "invalid score",
                "repos": "repo",
                "score": 2.0,
                "date": "2026-01-27T05:00:00Z",
            },
        ]
        with pytest.raises(ValidationError):
            LearningsFile.model_validate(data)

    def test_bare_decimal_in_list(self):
        data = [
            {
                "pattern": "test",
                "repos": "repo",
                "score": ".304",
                "date": "2026-01-28T05:00:30-06:00",
            },
        ]
        lf = LearningsFile.model_validate(data)
        assert lf.root[0].score == pytest.approx(0.304)
