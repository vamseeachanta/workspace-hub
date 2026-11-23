#!/usr/bin/env python3
"""Report supplied promotion evidence; never authenticate decisions or rights.

Evidence mechanisms follow durable-vs-transient-knowledge-boundary.md Section 7.4.
The normalized input adapter is documented in promotion-trail-report.md.
Only the CLI's explicitly named manifest is read; linked artifacts are not opened.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys


def _relative(root: Path, value: object) -> bool:
    """Accept canonical relative file locators, optionally with an opaque fragment."""
    if not isinstance(value, str) or not value or value != value.strip():
        return False
    if any(character.isspace() for character in value):
        return False
    if any(character in value for character in "\\:%?[]()"):
        return False
    path, separator, fragment = value.partition("#")
    if separator and (not fragment or "#" in fragment):
        return False
    parts = path.split("/")
    if any(part in {"", ".", ".."} for part in parts):
        return False
    relative = PurePosixPath(path)
    # A suffix distinguishes file references from unqualified identity slugs.
    if relative.is_absolute() or not relative.suffix:
        return False
    try:
        return (root / path).resolve().is_relative_to(root)
    except (OSError, RuntimeError, ValueError):
        return False


def _source(root: Path, value: object) -> bool:
    if not isinstance(value, str):
        return False
    # Positive decimal issue references and opaque explicit document identities.
    return bool(re.fullmatch(r"#[1-9][0-9]*|doc_key:[A-Za-z0-9][A-Za-z0-9_.:-]*", value)) or _relative(root, value)


def _trail(root: Path, mechanism: str, locator: object, raw: object) -> dict:
    errors = []
    if not _relative(root, locator):
        errors.append("invalid evidence locator")
    values = raw if isinstance(raw, list) else [raw]
    if not values or any(not _source(root, value) for value in values):
        errors.append("invalid promoted_from")
    return {"mechanism": mechanism, "locator": locator,
            "sources": sorted({value for value in values if _source(root, value)}),
            "errors": errors}


def _records(document: dict, key: str, *, required: bool = False) -> list:
    records = document.get(key, None if required else [])
    if not isinstance(records, list) or any(not isinstance(record, dict) for record in records):
        raise ValueError(f"{key} must be an array of objects")
    return records


def _identity(value: object) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_.:-]*", value))


def report(root: Path, document: dict) -> list[dict]:
    """Classify explicit records without reading pages or resolving source identities.

    Invalid document structure raises ValueError. Invalid evidence attached to a
    known page is retained and makes that page ambiguous, even if another trail
    is valid. Missing metadata is never an implicit legacy declaration.
    """
    root = Path(root).resolve()
    if not root.is_dir() or not isinstance(document, dict):
        raise ValueError("root must be a directory and input must be an object")
    if set(document) - {"pages", "page_logs", "registry"}:
        raise ValueError("unknown input collection")
    pages = _records(document, "pages", required=True)
    evidence = {}
    identities = {}
    for page in pages:
        if set(page) - {"page", "doc_key", "promoted_from", "legacy"}:
            raise ValueError("unknown page field")
        name = page.get("page")
        if not _relative(root, name) or "#" in name or name in evidence:
            raise ValueError("page must be a unique root-relative file path")
        evidence[name] = []
        if "doc_key" in page:
            key = page["doc_key"]
            if not _identity(key) or key in identities:
                raise ValueError("page doc_key must be a unique nonempty identity")
            identities[key] = name
        if "promoted_from" in page:
            evidence[name].append(_trail(root, "metadata", name + "#promoted_from", page["promoted_from"]))
        if "legacy" in page:
            legacy = page["legacy"]
            errors = []
            if not isinstance(legacy, dict):
                legacy = {}
                errors.append("legacy must contain reason and locator")
            if set(legacy) - {"reason", "locator"}:
                errors.append("unknown legacy field")
            reason = legacy.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                errors.append("legacy requires a nonempty reason")
            locator = legacy.get("locator")
            if not _relative(root, locator):
                errors.append("invalid legacy locator")
            evidence[name].append({"mechanism": "legacy", "locator": locator,
                                   "reason": reason, "sources": [], "errors": errors})

    for collection, mechanism, target in (("page_logs", "page_log", "page"),
                                           ("registry", "registry", "doc_key")):
        for record in _records(document, collection):
            if set(record) - {target, "locator", "promoted_from"}:
                raise ValueError("unknown backlink field")
            key = record.get(target)
            if not isinstance(key, str):
                raise ValueError("backlink target must be a string")
            name = identities.get(key) if mechanism == "registry" else key
            if name not in evidence:
                raise ValueError("backlink target is not an explicitly supplied page")
            evidence[name].append(_trail(root, mechanism, record.get("locator"), record.get("promoted_from")))

    results = []
    for name, trails in sorted(evidence.items()):
        trails = sorted(trails, key=lambda item: (item["mechanism"], json.dumps(item, sort_keys=True)))
        errors = {error for trail in trails for error in trail["errors"]}
        lineage = [trail for trail in trails if trail["mechanism"] != "legacy"]
        legacy = [trail for trail in trails if trail["mechanism"] == "legacy"]
        source_sets = {tuple(trail["sources"]) for trail in lineage}
        # Compare complete sets: a synthesis and a single-source claim differ.
        if len(source_sets) > 1:
            errors.add("conflicting source sets")
        if legacy and lineage:
            errors.add("legacy declaration conflicts with promotion evidence")
        status = "ambiguous" if errors else "legacy" if legacy else "traced" if lineage else "missing"
        results.append({"page": name, "status": status,
                        "sources": sorted({source for trail in lineage for source in trail["sources"]}),
                        "evidence": trails, "errors": sorted(errors)})
    return results


def _unique_object(pairs: list) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON field")
        result[key] = value
    return result


def _invalid_constant(value: str) -> None:
    raise ValueError("non-finite JSON value")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("manifest", help="root-relative JSON input file")
    args = parser.parse_args(argv)
    try:
        root = args.root.resolve()
        if not _relative(root, args.manifest) or "#" in args.manifest:
            raise ValueError("manifest must be a root-relative file path")
        document = json.loads((root / args.manifest).read_text(encoding="utf-8"),
                              object_pairs_hook=_unique_object, parse_constant=_invalid_constant)
        results = report(root, document)
    except (OSError, UnicodeError, ValueError, RuntimeError):
        # File-system exceptions can contain private paths; do not echo them.
        print("invalid input: check manifest shape and root-relative locators", file=sys.stderr)
        return 2  # argparse convention: invalid input, distinct from report status.
    print(json.dumps(results, indent=2, sort_keys=True))
    return 0  # Successful reporting never acts as a promotion gate.


if __name__ == "__main__":
    sys.exit(main())
