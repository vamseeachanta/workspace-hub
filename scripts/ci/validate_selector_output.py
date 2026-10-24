"""Validate the line-based selector contract defined in issue #4227.

Names use an explicit ASCII allowlist suitable for check and artifact names.
The minimum include count is one, as required by the nonempty-matrix contract.
"""

import argparse
import json
import re
from pathlib import Path


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON key")
        result[key] = value
    return result


def reject_constant(_value):
    raise ValueError("non-finite JSON value")


def validate(text: str) -> int:
    """Return the include count, or raise ValueError/TypeError for a broken contract."""
    outputs = {}
    for line in text.splitlines():
        key, separator, value = line.partition("=")
        if separator and key in {"matrix", "scope"}:
            if key in outputs:
                raise ValueError("duplicate selector output")
            outputs[key] = value
    if outputs.get("scope") not in {"full", "modules", "skip"}:
        raise ValueError("scope must be full, modules or skip")
    if "matrix" not in outputs:
        raise ValueError("matrix output is required")
    matrix = json.loads(
        outputs["matrix"], object_pairs_hook=unique_object, parse_constant=reject_constant,
    )
    if not isinstance(matrix, dict):
        raise TypeError("matrix must be an object")
    include = matrix.get("include")
    if not isinstance(include, list) or not include:
        raise ValueError("matrix.include must be a nonempty list")
    for key, value in matrix.items():
        if key == "include":
            continue
        if key == "exclude":
            if not isinstance(value, list) or any(not isinstance(v, dict) for v in value):
                raise ValueError("matrix.exclude must be a list of objects")
        elif not isinstance(value, list) or not value:
            raise ValueError("matrix axes must be nonempty lists")
    names = set()
    for entry in include:
        if not isinstance(entry, dict):
            raise TypeError("include entries must be objects")
        name = entry.get("name")
        if not isinstance(name, str) or re.fullmatch(r"[A-Za-z0-9_.-]+", name) is None:
            raise ValueError("names must be nonempty ASCII letters, digits, underscores, dots or hyphens")
        if name in names:
            raise ValueError("include names must be unique")
        names.add(name)
        targets = entry.get("targets")
        if not isinstance(targets, str) or not targets.strip():
            raise ValueError("targets must be a nonempty string")
        if entry.get("mode") not in ("xdist", "seq"):
            raise ValueError("mode must be xdist or seq")
    return len(include)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("selector_output", type=Path)
    parser.add_argument("--github-output", type=Path)
    parser.add_argument("--advisory", action="store_true")
    args = parser.parse_args()
    size = 0  # Fail closed until the contract has been validated (issue #4227).
    failed = False
    try:
        size = validate(args.selector_output.read_text(encoding="utf-8"))
    except (ValueError, TypeError, OSError):
        # Do not echo untrusted selector text into an Actions annotation.
        print(("::warning::" if args.advisory else "::error::") + "invalid selector output contract")
        failed = True
    if args.github_output:
        with args.github_output.open("a", encoding="utf-8") as output:
            output.write(f"matrix-size={size}\n")
    return int(failed and not args.advisory)


if __name__ == "__main__":
    raise SystemExit(main())
