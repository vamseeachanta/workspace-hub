"""Complete manifest closure before consumption; no authority is authenticated.

Contract: docs/architecture/manifest-closure.html, v1 (2026).
Inventory and count limits are caller inputs, never inferred from a manifest.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import re
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from types import MappingProxyType


class ClosureError(ValueError):
    """Evidence does not establish the pinned dataset closure."""


@dataclass(frozen=True)
class Readback:
    contents: Mapping[str, bytes]
    receipt: Mapping[str, object]


# SHA-256 representation: resource descriptor contract, "Stable projection".
_DIGEST = re.compile(r"[0-9a-f]{64}")
_FILE_FIELDS = {"id", "role", "path", "format", "record_count", "primary_key"}
_VIEWS = {"working-tree", "staged", "fresh-checkout", "retained-original"}


def _require(condition, message):
    if not condition:
        raise ClosureError(message)


def _digest(raw):
    return hashlib.sha256(raw).hexdigest()


def _object(pairs):
    result = {}
    for key, value in pairs:
        _require(key not in result, "duplicate JSON key")
        result[key] = value
    return result


def _nonfinite(value):
    raise ClosureError("non-finite JSON number")


def _finite_float(value):
    number = float(value)
    _require(math.isfinite(number), "non-finite JSON number")
    return number


def _json(raw):
    try:
        return json.loads(
            raw,
            object_pairs_hook=_object,
            parse_constant=_nonfinite,
            parse_float=_finite_float,
        )
    except (ValueError, UnicodeError, RecursionError) as exc:
        raise ClosureError(f"invalid JSON: {exc}") from exc


def _text(value):
    return isinstance(value, str) and bool(value.strip())


def _path(value):
    _require(_text(value), "path must be nonempty")
    path = PurePosixPath(value)
    _require(
        not path.is_absolute()
        and path.as_posix() == value
        and all(part not in {".", ".."} for part in path.parts)
        and not any(char in value for char in ("\\", ":", "\x00"))
        and bool(path.parts),
        "path must be canonical and owner-relative",
    )
    return path


def _inventory(document, *, manifest):
    fields = {"version", "files"} if manifest else {"version", "files", "foreign_keys"}
    version = "manifest-closure/v1" if manifest else "manifest-closure-contract/v1"
    _require(
        isinstance(document, dict) and set(document) == fields,
        "unexpected document fields",
    )
    _require(document["version"] == version, "unsupported version")
    files = document["files"]
    _require(
        isinstance(files, list) and bool(files), "expected nonempty file inventory"
    )
    result, paths = {}, set()
    for entry in files:
        expected = _FILE_FIELDS | ({"sha256"} if manifest else set())
        _require(
            isinstance(entry, dict) and set(entry) == expected, "unexpected file fields"
        )
        _require(
            _text(entry["id"]) and _text(entry["role"]), "missing file identity or role"
        )
        _require(entry["id"] not in result, "duplicate file ID")
        _path(entry["path"])
        _require(entry["path"] not in paths, "duplicate file path")
        _require(entry["format"] in ("bytes", "json-records"), "unsupported format")
        if entry["format"] == "bytes":
            _require(
                entry["record_count"] is None and entry["primary_key"] is None,
                "byte files cannot claim record semantics",
            )
        else:
            _require(
                type(entry["record_count"]) is int
                and entry["record_count"] >= 0
                and _text(entry["primary_key"]),
                "invalid pinned record count or key",
            )
        if manifest:
            _require(
                isinstance(entry["sha256"], str) and _DIGEST.fullmatch(entry["sha256"]),
                "invalid digest syntax",
            )
        result[entry["id"]] = entry
        paths.add(entry["path"])
    return result


def _foreign_keys(contract, files):
    links = contract["foreign_keys"]
    _require(isinstance(links, list), "foreign_keys must be an explicit list")
    seen = set()
    for link in links:
        _require(
            isinstance(link, dict)
            and set(link) == {"from_file", "field", "to_file", "key"}
            and all(_text(v) for v in link.values()),
            "invalid foreign key declaration",
        )
        signature = tuple(sorted(link.items()))
        _require(signature not in seen, "duplicate foreign key declaration")
        seen.add(signature)
        for field in ("from_file", "to_file"):
            _require(
                link[field] in files and files[link[field]]["format"] == "json-records",
                "foreign key must reference counted record files",
            )
        _require(
            link["key"] == files[link["to_file"]]["primary_key"],
            "foreign key target must be a primary key",
        )
    return links


def _read(root, relative):
    current = root
    try:
        for part in _path(relative).parts:
            current = current / part
            _require(not current.is_symlink(), "symlink in payload path")
        _require(current.resolve().is_relative_to(root), "payload escapes root")
        _require(current.is_file(), "missing regular payload file")
        return current.read_bytes()
    except (OSError, RuntimeError, ValueError) as exc:
        raise ClosureError(f"payload read failed: {relative}") from exc


def _key(value):
    _require(
        type(value) in (str, int) and (not isinstance(value, str) or bool(value)),
        "record key must be a nonempty string or integer",
    )
    # Keep integer and text identities distinct; bool is excluded above.
    return type(value).__name__, value


def _records(raw, entry):
    rows = _json(raw)
    _require(
        isinstance(rows, list) and len(rows) == entry["record_count"],
        "record count differs from pinned count",
    )
    keys = set()
    for row in rows:
        _require(
            isinstance(row, dict) and entry["primary_key"] in row,
            "record primary key missing",
        )
        value = _key(row[entry["primary_key"]])
        _require(value not in keys, "duplicate record primary key")
        keys.add(value)
    return rows, keys


def readback(
    manifest_raw: bytes,
    contract_raw: bytes,
    *,
    contract_sha256: str,
    root: Path,
    view: str,
) -> Readback:
    """Validate one materialized byte view, then return those exact read bytes.

    The caller pins the contract independently and materializes each view.
    A view label does not establish Git tracking or source/publication authority.
    Inputs must remain quiescent during readback; no atomic filesystem snapshot
    is claimed. Consume contents, rather than reopening mutable payload paths.
    """
    _require(
        isinstance(contract_sha256, str) and _DIGEST.fullmatch(contract_sha256),
        "invalid contract digest syntax",
    )
    _require(_digest(contract_raw) == contract_sha256, "contract digest mismatch")
    _require(isinstance(view, str) and view in _VIEWS, "unknown byte view")
    contract, manifest = _json(contract_raw), _json(manifest_raw)
    expected = _inventory(contract, manifest=False)
    actual = _inventory(manifest, manifest=True)
    _require(
        set(expected) == set(actual), "manifest file set differs from pinned inventory"
    )
    for identifier, entry in expected.items():
        _require(
            all(actual[identifier][key] == entry[key] for key in _FILE_FIELDS),
            "manifest metadata differs from pinned inventory",
        )
    links = _foreign_keys(contract, expected)
    root = Path(root).resolve()
    _require(root.is_dir(), "owner root is not a directory")
    contents, records, keys = {}, {}, {}
    for identifier, entry in expected.items():
        raw = _read(root, entry["path"])
        _require(
            _digest(raw) == actual[identifier]["sha256"], "payload digest mismatch"
        )
        contents[identifier] = raw
        if entry["format"] == "json-records":
            records[identifier], keys[identifier] = _records(raw, entry)
    for link in links:
        for row in records[link["from_file"]]:
            _require(link["field"] in row, "foreign key field missing")
            _require(
                _key(row[link["field"]]) in keys[link["to_file"]],
                "foreign key target missing",
            )
    # Separate receipt, never inserted into the manifest being hashed.
    receipt = {
        "version": "manifest-closure-receipt/v1",
        "view": view,
        "manifest_sha256": _digest(manifest_raw),
        "contract_sha256": contract_sha256,
        "file_count": len(contents),
        "integrity": "verified",
        "authority": "not-established",
    }
    return Readback(MappingProxyType(contents), MappingProxyType(receipt))


def main(argv=None):
    """Write only a separate receipt to stdout after complete acceptance."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--contract-sha256", required=True)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--view", choices=sorted(_VIEWS), required=True)
    args = parser.parse_args(argv)
    try:
        result = readback(
            args.manifest.read_bytes(),
            args.contract.read_bytes(),
            contract_sha256=args.contract_sha256,
            root=args.root,
            view=args.view,
        )
    except (ClosureError, OSError, RuntimeError):
        # Do not disclose private paths or payload values in CLI diagnostics.
        print(
            "manifest closure failed; check contract digest, inventory and payload evidence",
            file=sys.stderr,
        )
        return 1
    print(json.dumps(dict(result.receipt), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
