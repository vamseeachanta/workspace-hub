"""Summarize catalog evidence without treating reader hints as qualification.

Schema and suggested tools: build_cad_index.py, HEADER and READ (repository
revision supplied by the caller). No standards-derived coefficients or limits
are used. Counts and byte totals are exact sums of supplied inventory records.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from pathlib import Path
from typing import TextIO

from build_cad_index import HEADER, READ


def summarize(source: TextIO) -> dict:
    """Validate the complete catalog before returning an aggregate-only report.

    Path uniqueness is textual, with no filesystem resolution or case folding.
    References and sizes are catalog observations, not artifact verification.
    """
    reader = csv.reader(source, delimiter="\t", strict=True)
    if next(reader, None) != HEADER.rstrip("\n").split("\t"):
        raise ValueError("inventory header does not match builder schema")
    seen = set()
    formats = {}
    for number, cells in enumerate(reader, start=2):
        if len(cells) != len(HEADER.rstrip("\n").split("\t")):
            raise ValueError(f"record {number}: wrong column count")
        path, fmt, _, _, _, glb, _, _, size, _ = cells
        if not path.strip() or path in seen:
            raise ValueError(f"record {number}: missing or duplicate path")
        if fmt not in READ:
            raise ValueError(f"record {number}: unsupported format")
        if not re.fullmatch(r"[0-9]+", size):
            raise ValueError(f"record {number}: invalid nonnegative integer size")
        seen.add(path)
        group = formats.setdefault(fmt, {
            "format": fmt, "files": 0, "bytes": 0, "glb_references": 0,
            "suggested_tool": READ[fmt][2],
        })
        group["files"] += 1
        group["bytes"] += int(size)
        group["glb_references"] += bool(glb.strip())
    return {
        "schema_version": 1,
        "basis": "catalog observations; tool suggestions from build_cad_index.READ",
        "inventory": {
            key: sum(group[key] for group in formats.values())
            for key in ("files", "bytes", "glb_references")
        },
        "formats": [formats[key] for key in sorted(formats)],
        "qualification": dict.fromkeys(
            ("readability", "conversion", "geometry_fidelity", "manufacturing_acceptance"),
            "NOT_EVALUATED",
        ),
        "limitations": [
            "Catalog completeness and freshness are not established.",
            "Sizes are supplied metadata; source files are not opened.",
            "GLB references are strings; existence and conversion provenance are unverified.",
            "Suggested tools are routing hints, not verified installations or capabilities.",
            "Qualification requires source bytes, units, converter version, and use criteria.",
        ],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path, required=True)
    args = parser.parse_args(argv)
    try:
        # One read binds the digest to the bytes actually parsed, not a later file state.
        payload = args.inventory.read_bytes()
        result = summarize(io.StringIO(payload.decode("utf-8"), newline=""))
        result["source_sha256"] = hashlib.sha256(payload).hexdigest()
    except (OSError, UnicodeError):
        print("inventory could not be read as UTF-8", file=sys.stderr)
        return 1
    except (ValueError, csv.Error):
        # Parser exceptions can contain raw cells; keep diagnostics aggregate-only.
        print("inventory failed schema or record validation", file=sys.stderr)
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
