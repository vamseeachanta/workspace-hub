"""Tests for WorkQueueState schema validation."""

import pytest
from datetime import datetime
from pydantic import ValidationError

from coordination.schemas.work_queue import WorkQueueStats, WorkQueueState


@pytest.mark.unit
class TestWorkQueueStats:
    def test_valid(self):
        s = WorkQueueStats(total_captured=65, total_processed=11, total_archived=11)
        assert s.total_captured == 65
        assert s.total_processed == 11

    def test_defaults(self):
        s = WorkQueueStats()
        assert s.total_captured == 0
        assert s.total_processed == 0
        assert s.total_archived == 0

    def test_negative_rejected(self):
        with pytest.raises(ValidationError):
            WorkQueueStats(total_captured=-1)


@pytest.mark.unit
class TestWorkQueueState:
    def test_valid_full(self):
        s = WorkQueueState(
            last_id=65,
            last_processed=None,
            created_at=datetime(2026, 1, 29),
            stats={"total_captured": 65, "total_processed": 11, "total_archived": 11},
        )
        assert s.last_id == 65
        assert s.last_processed is None
        assert s.stats.total_captured == 65

    def test_valid_with_last_processed(self):
        s = WorkQueueState(
            last_id=65,
            last_processed=60,
            created_at="2026-01-29T00:00:00Z",
        )
        assert s.last_processed == 60

    def test_negative_last_id_rejected(self):
        with pytest.raises(ValidationError):
            WorkQueueState(
                last_id=-1,
                created_at=datetime(2026, 1, 29),
            )

    def test_missing_created_at_rejected(self):
        with pytest.raises(ValidationError):
            WorkQueueState(last_id=10)

    def test_extra_fields_allowed(self):
        s = WorkQueueState(
            last_id=1,
            created_at=datetime(2026, 1, 29),
            new_field="value",
        )
        assert s.last_id == 1

    def test_default_stats(self):
        s = WorkQueueState(
            last_id=1,
            created_at=datetime(2026, 1, 29),
        )
        assert s.stats.total_captured == 0
