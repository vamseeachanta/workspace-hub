"""Tests for CCUserInsights schema validation."""

import pytest
from pydantic import ValidationError

from coordination.schemas.cc_user_insights import CCUserInsights


@pytest.mark.unit
class TestCCUserInsights:
    def test_valid_full(self):
        m = CCUserInsights(
            last_reviewed="2.1.27",
            versions_covered="2.1.20 to 2.1.27",
            review_date="2026-01-30",
            general=[
                "Permission resolution improved",
                "PR session linking added",
            ],
            specific=[
                "Use --from-pr to resume work on existing PRs",
            ],
        )
        assert m.last_reviewed == "2.1.27"
        assert len(m.general) == 2
        assert len(m.specific) == 1

    def test_empty_lists(self):
        m = CCUserInsights(
            last_reviewed="1.0",
            versions_covered="1.0",
            review_date="2026-01-01",
        )
        assert m.general == []
        assert m.specific == []

    def test_missing_required_field(self):
        with pytest.raises(ValidationError):
            CCUserInsights(
                versions_covered="1.0",
                review_date="2026-01-01",
            )

    def test_extra_fields_allowed(self):
        m = CCUserInsights(
            last_reviewed="1.0",
            versions_covered="1.0",
            review_date="2026-01-01",
            notes="extra",
        )
        assert m.last_reviewed == "1.0"
