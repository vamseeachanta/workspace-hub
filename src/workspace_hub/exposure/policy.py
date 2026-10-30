"""Surface policy; the private registry owns names and identification assessments."""

from __future__ import annotations

import json
import math
import re
import unicodedata
from collections.abc import Iterator
from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any, TypedDict


class ExposureError(ValueError):
    """Projection is refused; messages never contain private payloads."""


class Surface(StrEnum):
    INTERNAL = "internal"
    CLIENT = "client"
    PUBLIC_WEBSITE = "public_website"
    NEWSLETTER = "newsletter"
    PUBLIC_REPOSITORY = "public_repository"


class ExposedRecord(TypedDict, total=False):
    id: str
    client_id: str | None
    fields: dict[str, Any]


def _require(condition: bool, message: str = "Invalid registry record") -> None:
    if not condition:
        raise ExposureError(message)


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _fold(value: str) -> str:
    return "".join(
        c for c in unicodedata.normalize("NFKC", value).casefold() if c.isalnum()
    )


def _json_value(value: Any) -> bool:
    if value is None or type(value) in (bool, int, str):
        return True
    if type(value) is float:
        return math.isfinite(value)
    if type(value) is list:
        return all(_json_value(item) for item in value)
    if type(value) is dict:
        return all(
            type(key) is str and _json_value(item) for key, item in value.items()
        )
    return False


def _identifiers(data: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        identity
        for identity in (
            data["id"],
            data.get("client_id"),
            *(item.get("client_id") for item in data["fields"].values()),
        )
        if identity is not None
    )


def _validate_field(item: Any) -> None:
    _require(type(item) is dict)
    _require(set(item) <= {"value", "exposure_class", "kind", "codename", "client_id"})
    _require("value" in item and _json_value(item["value"]))
    _require(item.get("exposure_class") in ("public", "client", "internal"))
    _require(item.get("kind", "data") in ("data", "name", "secret", "contact"))
    if "client_id" in item:
        _require(_text(item["client_id"]))
    if item.get("kind") == "name":
        _require(_text(item["value"]) and _text(item.get("codename")))
        _require(bool(_fold(item["value"])) and bool(_fold(item["codename"])))
        _require(_fold(item["value"]) not in _fold(item["codename"]))
    else:
        _require("codename" not in item)


def _validate_record(data: Any) -> None:
    _require(type(data) is dict)
    _require(set(data) <= {"id", "client_id", "fields", "singling_out"})
    _require(_text(data.get("id")))
    _require(
        "client_id" not in data or data["client_id"] is None or _text(data["client_id"])
    )
    fields = data.get("fields")
    _require(type(fields) is dict and bool(fields))
    for name, item in fields.items():
        _require(
            isinstance(name, str) and re.fullmatch(r"[a-z][a-z0-9_]*", name) is not None
        )
        _validate_field(item)
    identifiers = tuple(_fold(identity) for identity in _identifiers(data))
    for item in fields.values():
        if item.get("kind") == "name":
            _require(
                not any(identity in _fold(item["codename"]) for identity in identifiers)
            )
    if "singling_out" not in data:
        return
    review = data["singling_out"]
    _require(type(review) is dict and set(review) == {"reviewed", "combinations"})
    _require(type(review["reviewed"]) is bool and type(review["combinations"]) is list)
    for combination in review["combinations"]:
        _require(type(combination) is list and bool(combination))
        _require(all(type(name) is str and name in fields for name in combination))
        _require(len(set(combination)) == len(combination))


@dataclass(frozen=True)
class RegistryRecord:
    """Validated JSON snapshot; private values are excluded from repr.

    Factory construction and projection both validate, so direct construction
    cannot bypass policy and mutable source dictionaries cannot change a record.
    """

    _payload: str = field(repr=False)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> RegistryRecord:
        _validate_record(data)
        return cls(json.dumps(data, ensure_ascii=False, allow_nan=False))

    def to_dict(self) -> dict[str, Any]:
        try:
            data: dict[str, Any] = json.loads(self._payload)
            _validate_record(data)
        except (TypeError, ValueError, RecursionError):
            raise ExposureError("Invalid registry record") from None
        return data


def forbidden_names(
    record: RegistryRecord, surface: Surface, client_id: str | None
) -> tuple[str, ...]:
    """Return forbidden identity, secret and contact strings for the recipient."""
    if surface == Surface.INTERNAL:
        return ()
    data = record.to_dict()
    names = tuple(
        item["value"]
        for item in data["fields"].values()
        if item.get("kind") == "name"
        and not (
            surface == Surface.CLIENT
            and client_id is not None
            and item.get("client_id", data.get("client_id")) == client_id
        )
    )
    sensitive = tuple(
        text
        for item in data["fields"].values()
        if item.get("kind") in ("secret", "contact")
        for text in _strings(item["value"])
        if text
    )
    return names + sensitive + _identifiers(data)


def _strings(value: Any) -> Iterator[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, dict):
        for key, item in value.items():
            yield key
            yield from _strings(item)
    elif isinstance(value, list):
        for item in value:
            yield from _strings(item)


def check_names(output: ExposedRecord, names: tuple[str, ...]) -> None:
    """Check all keys and nested string leaves, normalizing case and separators."""
    folded = tuple(_fold(text) for text in _strings(output))
    if any(_fold(name) in text for name in names for text in folded):
        raise ExposureError("Output contains a restricted identity")


def _project_fields(
    data: dict[str, Any], surface: Surface, client_id: str | None
) -> dict[str, Any]:
    projected: dict[str, Any] = {}
    for name, item in data["fields"].items():
        own = (
            surface == Surface.CLIENT
            and item.get("client_id", data.get("client_id")) == client_id
        )
        if surface != Surface.INTERNAL:
            if (
                item.get("kind") in ("secret", "contact")
                or item["exposure_class"] == "internal"
            ):
                continue
            if item["exposure_class"] == "client" and not own:
                continue
        value = item["value"]
        if item.get("kind") == "name" and surface != Surface.INTERNAL and not own:
            value = item["codename"]
        projected[name] = value
    return projected


def expose(
    record: RegistryRecord,
    surface: Surface | str,
    *,
    client_id: str | None = None,
) -> ExposedRecord:
    """Project without mutation; client_id is a trusted caller's recipient context.

    This function is policy, not authentication. Public projections require a
    registry assessment and reject every declared identifying field combination
    that survives filtering. No claim of inferred anonymity is made.
    """
    try:
        surface = Surface(surface)
    except (TypeError, ValueError):
        raise ExposureError("Unknown exposure surface") from None
    _require(isinstance(record, RegistryRecord))
    data = record.to_dict()
    if surface == Surface.CLIENT:
        _require(_text(client_id), "Client surface requires a recipient")
    if surface != Surface.INTERNAL:
        _require(
            data.get("singling_out", {}).get("reviewed") is True,
            "Outward exposure requires a singling-out assessment",
        )
    projected = _project_fields(data, surface, client_id)
    output: ExposedRecord = {"fields": projected}
    if surface == Surface.INTERNAL:
        output["id"] = data["id"]
        output["client_id"] = data.get("client_id")
    else:
        for combination in data["singling_out"]["combinations"]:
            _require(
                not set(combination) <= projected.keys(),
                "Refused by singling-out assessment",
            )
        check_names(output, forbidden_names(record, surface, client_id))
    return output
