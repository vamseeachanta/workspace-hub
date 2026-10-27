"""Pure parsing of supplied plugin evidence; see plugin_inventory.md for the contract.

No discovery, file access, process execution, collection or publication occurs.
"""

import json
import math


class InventoryError(ValueError):
    """A fixed rule name only; input values must never enter diagnostics."""


def _object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise InventoryError("inventory.duplicate-key")
        result[key] = value
    return result


def _nonfinite(_value):
    raise InventoryError("inventory.json")


def _finite_float(value):
    number = float(value)
    if not math.isfinite(number):
        raise InventoryError("inventory.json")
    return number


def _text(value, *, token=False):
    if (not isinstance(value, str) or not value or value.strip() != value
            or not value.isprintable()
            or (token and any(char.isspace() for char in value))):
        raise InventoryError("inventory.record")
    return value


def _record(plugin_id, entry):
    if not isinstance(entry, dict):
        raise InventoryError("inventory.record")
    record = {
        "plugin_id": _text(plugin_id, token=True),
        "scope": _text(entry.get("scope"), token=True),
    }
    for source, target in (("version", "version"), ("installPath", "install_path")):
        value = entry.get(source)
        record[target] = None if value is None else _text(value)
    enabled = entry.get("enabled")
    if enabled is not None and not isinstance(enabled, bool):
        raise InventoryError("inventory.record")
    record["enabled"] = enabled
    return record


def _installed_json(payload):
    try:
        data = json.loads(payload, object_pairs_hook=_object,
                          parse_constant=_nonfinite, parse_float=_finite_float)
    except (ValueError, RecursionError) as error:
        if isinstance(error, InventoryError):
            raise
        raise InventoryError("inventory.json") from None
    if not isinstance(data, dict) or not isinstance(data.get("plugins"), dict):
        raise InventoryError("inventory.shape")
    # Supported envelope revision: the installed-json contract in plugin_inventory.md.
    if "version" in data and (type(data["version"]) is not int or data["version"] != 2):
        raise InventoryError("inventory.shape")
    records = []
    for plugin_id, entries in data["plugins"].items():
        if not isinstance(entries, list) or not entries:
            raise InventoryError("inventory.record")
        records.extend(_record(plugin_id, entry) for entry in entries)
    return records


def _captured_list(payload):
    if payload.strip() == "No plugins installed.":
        return []
    lines = [line for line in payload.replace("\r\n", "\n").split("\n") if line.strip()]
    if not lines or lines.pop(0) != "Installed plugins:":
        raise InventoryError("inventory.text")
    if not lines:
        raise InventoryError("inventory.incomplete")
    fields = {"Version": "version", "Scope": "scope", "Status": "enabled", "Path": "installPath"}
    records = []
    plugin_id = None
    entry = {}
    for line in lines:
        prefix = "  ❯ "
        if line.startswith(prefix):
            if plugin_id is not None:
                records.append(_record(plugin_id, entry))
            plugin_id = line.removeprefix(prefix)
            entry = {}
            continue
        if plugin_id is None or not line.startswith("    "):
            raise InventoryError("inventory.text")
        name, separator, value = line.removeprefix("    ").partition(": ")
        if not separator or name not in fields or fields[name] in entry:
            raise InventoryError("inventory.text")
        if name == "Status":
            states = {"✔ enabled": True, "✘ disabled": False}
            if value not in states:
                raise InventoryError("inventory.text")
            value = states[value]
        entry[fields[name]] = value
    records.append(_record(plugin_id, entry))
    return records


def parse_inventory(payload, *, input_format):
    """Return sorted records and complete/partial evidence status, or InventoryError.

    Formats are explicit: installed-json or captured-list. Missing nullable fields
    remain None; identity requires both plugin ID and scope. No state is inferred
    from an installation, and supplied paths are never resolved or accessed.
    """
    if not isinstance(payload, str):
        raise InventoryError("inventory.input")
    if input_format == "installed-json":
        records = _installed_json(payload)
    elif input_format == "captured-list":
        records = _captured_list(payload)
    else:
        raise InventoryError("inventory.format")
    seen = set()
    for record in records:
        identity = (record["plugin_id"], record["scope"])
        if identity in seen:
            raise InventoryError("inventory.duplicate")
        seen.add(identity)
    records.sort(key=lambda record: (record["plugin_id"], record["scope"]))
    complete = all(record[field] is not None for record in records
                   for field in ("version", "enabled", "install_path"))
    return {"status": "complete" if complete else "partial", "plugins": records}


def format_inventory(payload, *, input_format):
    """Return deterministic Unicode JSON with sorted keys and a trailing newline."""
    return json.dumps(parse_inventory(payload, input_format=input_format),
                      sort_keys=True, ensure_ascii=False, allow_nan=False,
                      separators=(",", ":")) + "\n"
