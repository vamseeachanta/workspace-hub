#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

from _pathnorm_shim import REPO_ROOT, canonicalize_tree, load_alias_map


DEFAULT_TARGETS = (
    "scripts/data/document-index/config.yaml",
    "data/document-index/mounted-source-registry.yaml",
    "data/document-index/dde-literature-catalog.yaml",
    "data/document-index/dde-oil-gas-codes-scan.yaml",
    "data/document-index/dde-standards-inventory.yaml",
    "data/document-index/coverage-audit.yaml",
    "data/document-index/llm-wiki-external-source-priority-queue.yaml",
    "data/document-index/summary-extraction-plan.yaml",
    "data/document-index/cross-drive-dedup-report.json",
)

RETENTION_WARNING = (
    "    # WARNING: dde rows in index.jsonl survive RESUME runs only — a --force rebuild\n"
    "    # merges from {} + enabled sources and DROPS all 495,487 dde rows.\n"
    "    # Superseded 2026-07 by /mnt/dde/.dde-knowledge/index.db (#3334)\n"  # abs-path-allowed
)


def _parse_structured(path: Path, text: str) -> Any:
    if path.suffix == ".json":
        return json.loads(text)
    return yaml.safe_load(text)


def _rewrite_aliases(text: str, alias_map: dict[str, str]) -> str:
    rewritten_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        if "symlink_note:" in line and "/mnt/ace-data" in line:  # abs-path-allowed
            if "# transport-path-allowed" not in line:
                line = line.rstrip("\n") + "  # transport-path-allowed\n"
            rewritten_lines.append(line)
            continue
        if "mount_root_example:" in line and "/mnt/remote/" in line:  # abs-path-allowed
            if "# transport-path-allowed" not in line:
                line = line.rstrip("\n") + "  # transport-path-allowed\n"
            rewritten_lines.append(line)
            continue
        if "provenance_rule:" in line and "/mnt/remote/" in line:  # abs-path-allowed
            if "# transport-path-allowed" not in line:
                line = line.rstrip("\n") + "  # transport-path-allowed\n"
            rewritten_lines.append(line)
            continue
        for alias, canonical in alias_map.items():
            pattern = re.compile(re.escape(alias) + r"(?=/|[\"'\s]|$)")
            line = pattern.sub(canonical, line)
        rewritten_lines.append(line)
    return "".join(rewritten_lines)


def _canonicalize_value(value: Any, alias_map: dict[str, str]) -> Any:
    if isinstance(value, str):
        normalized = value
        for alias, canonical in alias_map.items():
            pattern = re.compile(re.escape(alias) + r"(?=/|[\"'\s]|$)")
            normalized = pattern.sub(canonical, normalized)
        return "ace-linux-2" if normalized == "dev-secondary" else normalized
    if isinstance(value, list):
        return [_canonicalize_value(item, alias_map) for item in value]
    if isinstance(value, dict):
        return {key: _canonicalize_value(item, alias_map) for key, item in value.items()}
    return value


def _dde_block_bounds(lines: list[str]) -> tuple[int, int] | None:
    start = None
    for idx, line in enumerate(lines):
        if re.match(r"^  dde_project:\s*$", line):
            start = idx
            break
    if start is None:
        return None
    end = len(lines)
    for idx in range(start + 1, len(lines)):
        if re.match(r"^  [A-Za-z0-9_]+:\s*$", lines[idx]):
            end = idx
            break
    return start, end


def _enforce_dde_disabled(text: str) -> str:
    lines = text.splitlines(keepends=True)
    bounds = _dde_block_bounds(lines)
    if bounds is None:
        return text
    start, end = bounds
    block = lines[start:end]
    block_text = "".join(block)

    if RETENTION_WARNING not in block_text:
        insert_at = None
        for offset, line in enumerate(block):
            if re.match(r"^    enabled:\s*", line):
                insert_at = start + offset
                break
        if insert_at is None:
            insert_at = start + 1
        lines[insert_at:insert_at] = RETENTION_WARNING.splitlines(keepends=True)
        end += len(RETENTION_WARNING.splitlines())

    for idx in range(start, end):
        if re.match(r"^    enabled:\s*true\s*$", lines[idx]):
            lines[idx] = "    enabled: false\n"
            break
    return "".join(lines)


def _rewrite_config_metadata(path: Path, text: str) -> str:
    if path.name == "config.yaml":
        text = _enforce_dde_disabled(text)
        text = re.sub(r"(^    host:\s*)dev-secondary(\s*$)", r"\1ace-linux-2\2", text, flags=re.MULTILINE)
    return text


def _validate_structural_equivalence(path: Path, before: str, after: str, alias_map: dict[str, str]) -> None:
    before_tree = _canonicalize_value(_parse_structured(path, before), alias_map)
    after_tree = _canonicalize_value(_parse_structured(path, after), alias_map)
    if path.name == "config.yaml":
        try:
            before_tree["sources"]["dde_project"]["enabled"] = False
        except (KeyError, TypeError):
            pass
    if canonicalize_tree(before_tree, alias_map) != canonicalize_tree(after_tree, alias_map):
        raise ValueError(f"{path}: structural parse-equivalence failed after canonical rewrite")


def migrate_file(path: Path, alias_map: dict[str, str], check: bool = False) -> bool:
    before = path.read_text()
    after = _rewrite_aliases(before, alias_map)
    after = _rewrite_config_metadata(path, after)
    if after == before:
        return False
    _validate_structural_equivalence(path, before, after, alias_map)
    if not check:
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(after)
        tmp.replace(path)
    return True


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rewrite tracked document-index paths to canonical /mnt/<drive> forms.")  # abs-path-allowed
    parser.add_argument("--check", action="store_true", help="dry-run; exit 1 if any file would change")
    parser.add_argument("--targets", nargs="*", help="target files; defaults to the approved #3337 live config/catalog set")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    alias_map = load_alias_map()
    targets = args.targets or list(DEFAULT_TARGETS)
    changed: list[Path] = []

    for target in targets:
        path = (REPO_ROOT / target).resolve() if not Path(target).is_absolute() else Path(target)
        if path.name == "index.jsonl":
            raise SystemExit("refusing to migrate frozen index.jsonl")
        if not path.exists():
            raise SystemExit(f"target not found: {path}")
        if migrate_file(path, alias_map, check=args.check):
            changed.append(path)
            print(f"would change: {path.relative_to(REPO_ROOT)}" if args.check else f"changed: {path.relative_to(REPO_ROOT)}")
        else:
            print(f"unchanged: {path.relative_to(REPO_ROOT)}")

    print(f"{len(changed)} files {'would change' if args.check else 'changed'}")
    if args.check and changed:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
