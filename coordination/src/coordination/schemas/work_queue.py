"""Pydantic schema for .claude/work-queue/state.yaml"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class WorkQueueStats(BaseModel):
    """Statistics section of the work queue state."""

    model_config = {"extra": "allow"}

    total_captured: int = Field(default=0, ge=0)
    total_processed: int = Field(default=0, ge=0)
    total_archived: int = Field(default=0, ge=0)


class WorkQueueState(BaseModel):
    """Top-level schema for work-queue/state.yaml."""

    model_config = {"extra": "allow"}

    last_id: int = Field(ge=0)
    last_processed: Optional[int] = None
    created_at: datetime
    stats: WorkQueueStats = WorkQueueStats()
