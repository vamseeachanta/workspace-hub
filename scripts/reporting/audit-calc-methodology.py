#!/usr/bin/env python3
"""Read-only structural completeness audit for calculation YAML (issue #3687).

Usage: python scripts/reporting/audit-calc-methodology.py calculation.yaml
Requires PyYAML. The committed report schema supplies section names and order:
required_fields followed by optional_sections. Optional sections contribute to
completeness without becoming mandatory for report validation.

Absent keys, nulls, whitespace-only strings and empty containers are missing.
Zero, false and nonempty containers are present. Nested fields and types are not
validated. Presence is not engineering validation.
"""

import argparse
from collections.abc import Mapping
import json
from pathlib import Path
import sys

import yaml


SCHEMA_PATH = (
    Path(__file__).resolve().parents[2]
    / "config" / "reporting" / "calculation-report-schema.yaml"
)
NOTICE = "Structural completeness only; presence is not engineering validation."


def _nonempty(value):
    """Check only the top-level value, preserving zero and false as content."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (Mapping, list, tuple, set)):
        return bool(value)
    return True


def audit(data):
    """Return section lists in schema order and a completeness percentage."""
    if not isinstance(data, Mapping):
        raise ValueError("Input root must be a mapping")
    schema = yaml.safe_load(SCHEMA_PATH.read_text(encoding="utf-8"))
    checklist = list(schema["required_fields"]) + list(schema["optional_sections"])
    present = [name for name in checklist if _nonempty(data.get(name))]
    missing = [name for name in checklist if not _nonempty(data.get(name))]
    # Percentage convention: count / total * 100, rounded to one decimal.
    percentage = round(len(present) / len(checklist) * 100, 1)
    return {
        "present": present,
        "missing": missing,
        "total": len(checklist),
        "percentage": percentage,
        "notice": NOTICE,
    }


def audit_file(path):
    """Read a single YAML mapping without changing it or rendering a report."""
    try:
        content = Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        # Do not echo paths or input contents in diagnostic output.
        raise ValueError("Cannot read input as UTF-8 YAML") from exc
    try:
        data = yaml.safe_load(content)
    except yaml.YAMLError as exc:
        raise ValueError("Invalid YAML input; expected a single YAML document") from exc
    return audit(data)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Calculation YAML to audit")
    args = parser.parse_args(argv)
    try:
        result = audit_file(args.input)
    except (ValueError, OSError, yaml.YAMLError) as exc:
        print(f"Audit error: {exc}", file=sys.stderr)
        return 1  # Conventional unsuccessful CLI exit status.
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0  # Conventional successful CLI exit status, even for missing sections.


if __name__ == "__main__":
    sys.exit(main())
