"""Registry mapping YAML filenames to their Pydantic schema classes."""

from __future__ import annotations

from typing import Any, Type

from pydantic import BaseModel

from coordination.schemas.cc_user_insights import CCUserInsights
from coordination.schemas.learnings import LearningsFile
from coordination.schemas.reflect_state import ReflectState
from coordination.schemas.work_queue import WorkQueueState

# Maps filename (stem or full basename) to schema class.
# Both the canonical name and common alternatives are registered.
SCHEMA_REGISTRY: dict[str, Type[BaseModel]] = {
    "reflect-state": ReflectState,
    "reflect-state.yaml": ReflectState,
    "reflect-state.yml": ReflectState,
    "learnings": LearningsFile,
    "learnings.yaml": LearningsFile,
    "learnings.yml": LearningsFile,
    "state": WorkQueueState,
    "state.yaml": WorkQueueState,
    "state.yml": WorkQueueState,
    "cc-user-insights": CCUserInsights,
    "cc-user-insights.yaml": CCUserInsights,
    "cc-user-insights.yml": CCUserInsights,
}


def get_schema_for_file(filename: str) -> Type[BaseModel] | None:
    """Look up the schema class for a given filename.

    Args:
        filename: The filename (with or without extension) or full basename.

    Returns:
        The corresponding Pydantic model class, or None if not found.
    """
    # Try exact match first
    if filename in SCHEMA_REGISTRY:
        return SCHEMA_REGISTRY[filename]

    # Try without path components
    from pathlib import Path

    basename = Path(filename).name
    if basename in SCHEMA_REGISTRY:
        return SCHEMA_REGISTRY[basename]

    stem = Path(filename).stem
    if stem in SCHEMA_REGISTRY:
        return SCHEMA_REGISTRY[stem]

    return None
