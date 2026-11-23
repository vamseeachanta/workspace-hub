"""Pydantic schema for .claude/state/memory/patterns/learnings.yaml"""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, RootModel, field_validator


class LearningEntry(BaseModel):
    """A single learning entry from the learnings YAML file."""

    model_config = {"extra": "allow"}

    pattern: str
    repos: str = ""
    score: float = Field(ge=0.0, le=1.0)
    date: datetime

    @field_validator("score", mode="before")
    @classmethod
    def coerce_bare_decimal(cls, v: object) -> object:
        """Handle bare decimals like .304 that YAML may parse as strings."""
        if isinstance(v, str):
            return float(v)
        return v

    @field_validator("repos", mode="before")
    @classmethod
    def coerce_repos(cls, v: object) -> str:
        """Handle repos field that might be None or non-string."""
        if v is None:
            return ""
        return str(v)


class LearningsFile(RootModel[list[LearningEntry]]):
    """Root model for learnings.yaml (bare list at root)."""

    pass
