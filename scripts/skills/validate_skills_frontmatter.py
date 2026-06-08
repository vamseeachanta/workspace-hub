#!/usr/bin/env python3
"""Validate YAML frontmatter for workspace skill files."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import yaml


def _split_frontmatter(path: Path) -> tuple[str | None, str | None]:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except OSError as exc:
        return None, f"{path}: cannot read file: {exc}"

    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None, f"{path}: missing frontmatter start"

    end_idx: int | None = None
    for idx, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            end_idx = idx
            break

    if end_idx is None:
        return None, f"{path}: missing frontmatter end"

    return "\n".join(lines[1:end_idx]), None


def _validate_string_field(data: dict[str, Any], field: str, path: Path) -> str | None:
    value = data.get(field)
    if not isinstance(value, str):
        return f"{path}: missing or non-string {field}"
    if not value.strip():
        return f"{path}: empty {field}"
    return None


def validate_skill_file(path: Path) -> list[str]:
    frontmatter, split_error = _split_frontmatter(path)
    if split_error is not None:
        return [split_error]

    assert frontmatter is not None
    try:
        data = yaml.safe_load(frontmatter)
    except yaml.YAMLError as exc:
        return [f"{path}: invalid YAML frontmatter: {exc}"]

    if not isinstance(data, dict):
        return [f"{path}: frontmatter must be a YAML mapping"]

    errors: list[str] = []
    for field in ("name", "description"):
        error = _validate_string_field(data, field, path)
        if error is not None:
            errors.append(error)
    return errors


def find_skill_files(root: Path) -> list[Path]:
    return sorted(root.rglob("SKILL.md"))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".claude/skills")
    args = parser.parse_args(argv)

    root = Path(args.root)
    if not root.is_dir():
        print(f"Skills root not found: {root}", file=sys.stderr)
        return 2

    skill_files = find_skill_files(root)
    if not skill_files:
        print(f"No SKILL.md files found under: {root}", file=sys.stderr)
        return 2

    errors: list[str] = []
    for path in skill_files:
        errors.extend(validate_skill_file(path))

    if errors:
        for error in errors:
            print(error)
        print("Skill validation failed.")
        return 1

    print(f"Skill validation passed ({len(skill_files)} files).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
