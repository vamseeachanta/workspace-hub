#!/usr/bin/env python3
"""Compare explicit local cross-link JSONL snapshots without discovery or writes.

Identity fields follow scripts/knowledge/wiki-cross-links.py::format_cross_links_jsonl.
Only the top-level discovered field is ignored for semantic comparison. Other
fields, including extensions and list order, are compared literally; object key
order is immaterial. Repeated identities (including identical records), duplicate
JSON keys, non-finite numbers, blank records and invalid identity fields fail.

Output is sorted by the directed identity tuple, with sorted JSON object keys.
Each record has change (added, removed or changed), before and after; an absent
payload is null. Unchanged edges produce no record. Original fields, including
discovered, are retained in before/after. Both inputs must validate before output.
Memory use is proportional to the snapshots and resulting delta.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys


IDENTITY_FIELDS = ("source_wiki", "source_page", "target_wiki", "target_page")


class InputError(ValueError):
    """An input failure with a fixed diagnostic safe for the command line."""


class ArgumentParser(argparse.ArgumentParser):
    def error(self, message):
        # argparse messages may otherwise reflect arbitrary paths or arguments.
        self.exit(2, "error: invalid arguments; use --help for usage\n")


def unique_object(pairs):
    """Reject duplicate keys before a JSON decoder can discard their evidence."""
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError("non-finite JSON constant")


def canonical_json(value):
    """Normalize object ordering without conflating JSON booleans and numbers."""
    return json.dumps(value, ensure_ascii=False, sort_keys=True, allow_nan=False)


def read_snapshot(path, role):
    """Read one local file; never include supplied paths or content in errors."""
    records = {}
    try:
        if path == "-" or not Path(path).is_file():
            raise OSError("regular local file required")
        with Path(path).open(encoding="utf-8") as source:
            for line in source:
                record = json.loads(
                    line, object_pairs_hook=unique_object,
                    parse_constant=reject_constant,
                )
                if not isinstance(record, dict):
                    raise ValueError("JSON object required")
                identity = tuple(record.get(field) for field in IDENTITY_FIELDS)
                if not all(isinstance(value, str) and value.strip()
                           for value in identity):
                    raise ValueError("nonempty identity strings required")
                # Also catches numeric overflow and unpaired Unicode surrogates
                # in extensions before any delta can reach stdout.
                canonical_json(record).encode("utf-8")
                if identity in records:
                    raise InputError(f"duplicate identity in {role} input")
                records[identity] = record
    except InputError:
        raise
    except OSError:
        raise InputError(f"cannot read {role} input") from None
    except (ValueError, UnicodeError, RecursionError):
        raise InputError(f"invalid {role} JSONL") from None
    return records


def semantic_json(record):
    return canonical_json({key: value for key, value in record.items()
                           if key != "discovered"})


def compute_delta(prior, current):
    """Yield the hand-defined set difference, sorted by directed identity."""
    for identity in sorted(prior.keys() | current.keys()):
        before, after = prior.get(identity), current.get(identity)
        if before is None:
            change = "added"
        elif after is None:
            change = "removed"
        elif semantic_json(before) != semantic_json(after):
            change = "changed"
        else:
            continue
        yield {"change": change, "before": before, "after": after}


def main(argv=None):
    parser = ArgumentParser(
        prog="compute-gap-delta.py", allow_abbrev=False,
        description=(
            "Compare local JSONL files offline. Emit identity-sorted records with "
            "change, before and after; absent payloads are null. Ignore only "
            "top-level discovered changes. Invalid input emits no delta records."
        ),
    )
    parser.add_argument("--prior", required=True, help="Prior local JSONL file")
    parser.add_argument("--current", required=True, help="Current local JSONL file")
    args = parser.parse_args(argv)
    try:
        prior = read_snapshot(args.prior, "prior")
        current = read_snapshot(args.current, "current")
    except InputError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2  # Standard command-line usage/input error status.
    output = "".join(canonical_json(record) + "\n"
                     for record in compute_delta(prior, current))
    # Explicit UTF-8 output is independent of the invoking terminal's encoding.
    sys.stdout.buffer.write(output.encode("utf-8"))
    return 0  # Standard successful command status.


if __name__ == "__main__":
    raise SystemExit(main())
