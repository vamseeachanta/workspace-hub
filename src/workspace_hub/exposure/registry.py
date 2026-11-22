"""Read the configured private JSON registry without logging private contents."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .policy import ExposureError, RegistryRecord


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ExposureError("Duplicate registry key")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ExposureError("Non-finite registry value")


def load_registry(path: str | Path | None = None) -> dict[str, RegistryRecord]:
    """Load schema v1 from an explicit path or DATA_REGISTRY_PATH; never discover."""
    configured = path if path is not None else os.environ.get("DATA_REGISTRY_PATH")
    if not configured:
        raise ExposureError("Configure a private registry path")
    try:
        data = json.loads(
            Path(configured).read_text(encoding="utf-8"),
            object_pairs_hook=_unique_object,
            parse_constant=_reject_constant,
        )
        if (
            type(data) is not dict
            or set(data) != {"schema_version", "records"}
            or type(data["schema_version"]) is not int
            or data["schema_version"] != 1
            or type(data["records"]) is not list
        ):
            raise ExposureError("Invalid registry envelope")
        records = {}
        for item in data["records"]:
            record = RegistryRecord.from_dict(item)
            identity = record.to_dict()["id"]
            if identity in records:
                raise ExposureError("Duplicate registry identity")
            records[identity] = record
        return records
    except (OSError, ValueError, TypeError, RecursionError):
        raise ExposureError(
            "Private registry could not be loaded or validated"
        ) from None
