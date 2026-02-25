"""Pydantic schema for .claude/state/cc-user-insights.yaml"""

from __future__ import annotations

from pydantic import BaseModel, Field


class CCUserInsights(BaseModel):
    """Top-level schema for cc-user-insights.yaml."""

    model_config = {"extra": "allow"}

    last_reviewed: str
    versions_covered: str
    review_date: str
    general: list[str] = Field(default_factory=list)
    specific: list[str] = Field(default_factory=list)
