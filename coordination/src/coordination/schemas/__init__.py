"""YAML state file schema validation.

Public API:
    validate_file(path) -> list[dict]
    load_and_validate(path) -> BaseModel
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, ValidationError

from coordination.schemas._registry import get_schema_for_file
from coordination.schemas.cc_user_insights import CCUserInsights
from coordination.schemas.learnings import LearningEntry, LearningsFile
from coordination.schemas.reflect_state import (
    ActionsTaken,
    ChecklistStatus,
    PhasesCompleted,
    ReflectChecklist,
    ReflectFiles,
    ReflectMetrics,
    ReflectState,
)
from coordination.schemas.work_queue import WorkQueueState, WorkQueueStats

__all__ = [
    # Public API
    "validate_file",
    "load_and_validate",
    # Models
    "ReflectState",
    "ReflectMetrics",
    "ReflectChecklist",
    "PhasesCompleted",
    "ActionsTaken",
    "ReflectFiles",
    "ChecklistStatus",
    "LearningEntry",
    "LearningsFile",
    "WorkQueueState",
    "WorkQueueStats",
    "CCUserInsights",
]


def validate_file(path: str | Path) -> list[dict[str, Any]]:
    """Validate a YAML state file against its schema.

    Args:
        path: Path to the YAML file.

    Returns:
        A list of error dicts. Empty list means the file is valid.
        Each error dict has keys: 'loc', 'msg', 'type'.
    """
    path = Path(path)

    schema_cls = get_schema_for_file(path.name)
    if schema_cls is None:
        return [{"loc": (), "msg": f"No schema registered for '{path.name}'", "type": "schema_lookup_error"}]

    try:
        raw = yaml.safe_load(path.read_text())
    except Exception as exc:
        return [{"loc": (), "msg": f"YAML parse error: {exc}", "type": "yaml_error"}]

    try:
        if isinstance(raw, list):
            schema_cls.model_validate(raw)
        else:
            schema_cls.model_validate(raw or {})
        return []
    except ValidationError as exc:
        return [
            {"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
            for e in exc.errors()
        ]


def load_and_validate(path: str | Path) -> BaseModel:
    """Load and validate a YAML state file, returning the model instance.

    Args:
        path: Path to the YAML file.

    Returns:
        A validated Pydantic model instance.

    Raises:
        ValueError: If no schema is registered for the file.
        yaml.YAMLError: If the file cannot be parsed.
        pydantic.ValidationError: If validation fails.
    """
    path = Path(path)

    schema_cls = get_schema_for_file(path.name)
    if schema_cls is None:
        raise ValueError(f"No schema registered for '{path.name}'")

    raw = yaml.safe_load(path.read_text())

    if isinstance(raw, list):
        return schema_cls.model_validate(raw)
    return schema_cls.model_validate(raw or {})
