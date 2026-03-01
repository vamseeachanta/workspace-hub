#!/usr/bin/env python3
from __future__ import annotations

import argparse
import pathlib
import re
import sys


def extract(pattern: str, text: str) -> str:
    match = re.search(pattern, text, re.MULTILINE)
    if not match:
        raise ValueError(f"Missing pattern: {pattern}")
    return match.group(1).strip().strip('"')


def extract_list(key: str, text: str) -> list[str]:
    match = re.search(rf"^{re.escape(key)}:\s*\n((?:\s+- .*\n)*)", text, re.MULTILINE)
    if not match:
        return []
    block = match.group(1)
    items = []
    for line in block.splitlines():
        line = line.strip()
        if line.startswith("- "):
            items.append(line[2:].strip().strip('"'))
    return items


def render_markdown(yaml_rel: str, yaml_text: str) -> str:
    target_window = extract(r'^target_window:\s*"?(.*?)"?$', yaml_text)
    read_threshold = extract(r"^\s+documents_read_threshold_percent:\s*(.*?)$", yaml_text)
    docs_in_scope = extract(r"^\s+documents_in_scope:\s*(.*?)$", yaml_text)
    docs_read = extract(r"^\s+documents_marked_read:\s*(.*?)$", yaml_text)
    docs_read_pct = extract(r"^\s+documents_marked_read_percent:\s*(.*?)$", yaml_text)
    calculations = extract_list("  key_calculations_implemented", yaml_text)
    followups = extract_list("  followup_wrks", yaml_text)
    calc_text = ", ".join(calculations) if calculations else "none yet"
    followup_text = ", ".join(followups) if followups else "none yet"

    return f"""# Resource Intelligence Maturity

Canonical state: [{pathlib.Path(yaml_rel).name}]({pathlib.Path(yaml_rel).name})

## Summary

- Target window: {target_window}
- Target: >{read_threshold}% of tracked documents marked read
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
    yaml_text = yaml_path.read_text()
    yaml_rel = str(yaml_path).replace(str(pathlib.Path.cwd()) + "/", "")
    canonical_md = extract(r"^\s+canonical_markdown_ref:\s*(.*?)$", yaml_text)
    actual_md_rel = str(md_path).replace(str(pathlib.Path.cwd()) + "/", "")
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
