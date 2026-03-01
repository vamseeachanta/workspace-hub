#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys

SUPPORTED_SCHEMA_VERSION = "1.0.0"


def extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise ValueError(f"Missing pattern: {pattern}")
    return match.group(1).strip().strip('"').strip("'")


def extract_list(key: str, text: str) -> list[str]:
    inline_match = re.search(rf"^\s*{re.escape(key)}:\s*\[(.*?)\]\s*$", text, re.MULTILINE)
    if inline_match:
        body = inline_match.group(1).strip()
        if not body:
            return []
        return [item.strip().strip('"').strip("'") for item in body.split(",") if item.strip()]

    block_match = re.search(rf"^\s*{re.escape(key)}:\s*\n((?:\s+- .*\n)*)", text, re.MULTILINE)
    if not block_match:
        return []
    block = block_match.group(1)
    items = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip().strip('"').strip("'"))
    return items


def render_markdown(yaml_rel: str, yaml_text: str) -> str:
    schema_version = extract(r'^schema_version:\s*"?(.*?)"?$', yaml_text)
    target_window = extract(r'^target_window:\s*"?(.*?)"?$', yaml_text)
    target_start = extract(r'^target_start:\s*"?(.*?)"?$', yaml_text)
    read_threshold = extract(r"^\s+documents_read_threshold_percent:\s*(.*?)$", yaml_text)
    measurement_owner = extract(r"^\s+measurement_owner:\s*(.*?)$", yaml_text)
    measurement_process = extract(r"^\s+measurement_process:\s*(.*?)$", yaml_text)
    docs_in_scope = extract(r"^\s+documents_in_scope:\s*(.*?)$", yaml_text)
    docs_read = extract(r"^\s+documents_marked_read:\s*(.*?)$", yaml_text)
    docs_read_pct = extract(r"^\s+documents_marked_read_percent:\s*(.*?)$", yaml_text)
    calculations = extract_list("key_calculations_implemented", yaml_text)
    followups = extract_list("followup_wrks", yaml_text)
    calc_text = ", ".join(calculations) if calculations else "none yet"
    followup_text = ", ".join(followups) if followups else "none yet"

    return f"""# Resource Intelligence Maturity

Canonical state: [{yaml_rel}]({yaml_rel})

## Summary

- Schema version: {schema_version}
- Target window: {target_window}
- Target start: {target_start}
- Target: >{read_threshold}% of tracked documents marked read
- Measurement owner: {measurement_owner}
- Measurement process: {measurement_process}
- Target: key calculations implemented in the repo ecosystem or linked to follow-on WRKs

## Current Status

- Documents in scope: {docs_in_scope}
- Documents marked read: {docs_read}
- Documents marked read percent: {docs_read_pct}
- Key calculations implemented: {calc_text}
- Follow-up WRKs: {followup_text}

This Markdown file is generated from the YAML ledger. The YAML ledger remains authoritative.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--yaml", required=True)
    parser.add_argument("--markdown", required=True)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()

    yaml_path = pathlib.Path(args.yaml)
    md_path = pathlib.Path(args.markdown)
    repo_root = pathlib.Path(
        subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    )
    yaml_path = yaml_path.resolve()
    md_path = md_path.resolve()
    yaml_text = yaml_path.read_text()
    yaml_rel = str(yaml_path.relative_to(repo_root))
    try:
        schema_version = extract(r'^schema_version:\s*"?(.*?)"?$', yaml_text)
        canonical_md = extract(r"^\s+canonical_markdown_ref:\s*(.*?)$", yaml_text)
        extract(r"^\s+measurement_owner:\s*(.*?)$", yaml_text)
        extract(r"^\s+measurement_process:\s*(.*?)$", yaml_text)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    if schema_version != SUPPORTED_SCHEMA_VERSION:
        sys.stderr.write(
            f"Unsupported schema_version in maturity ledger: "
            f"expected {SUPPORTED_SCHEMA_VERSION}, got {schema_version}\n"
        )
        return 1
    actual_md_rel = str(md_path.relative_to(repo_root))
    if canonical_md != actual_md_rel:
        sys.stderr.write(
            f"Markdown path does not match YAML tracking.canonical_markdown_ref: "
            f"expected {canonical_md}, got {actual_md_rel}\n"
        )
        return 1

    expected = render_markdown(yaml_rel, yaml_text)

    if args.check:
        actual = md_path.read_text() if md_path.exists() else ""
        if actual != expected:
            sys.stderr.write("Markdown summary is out of sync with YAML ledger\n")
            return 1
        return 0

    md_path.write_text(expected)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
