#!/usr/bin/env python3
"""Generate the hub's Python test inventory without importing test modules."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUTPUT = Path("config/ci/hub-test-families.json")
EXCLUDED = {".git", ".venv", "venv", "__pycache__", ".pytest_cache"}


def inventory(root: Path) -> dict:
    """Group test_*.py, the Python convention in pyproject.toml (2026).

    Include nested and adjacent script tests so directories such as
    scripts/data/<tool>/tests are not silently lost. Shell harnesses are
    outside pytest's Python discovery convention and are not matrix targets.
    """
    families: dict[str, list[str]] = {}
    for base in (root / "tests", root / "scripts", root / "coordination/tests"):
        if base.is_symlink():
            continue
        for directory, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = sorted(d for d in dirs if d not in EXCLUDED
                             and not (Path(directory) / d).is_symlink())
            for name in sorted(files):
                path = Path(directory) / name
                if not name.startswith("test_") or not name.endswith(".py") or path.is_symlink():
                    continue
                rel = path.relative_to(root)
                parts = rel.parts
                if parts[0] == "scripts":
                    if len(parts) < 3:
                        continue
                    family = f"scripts/{parts[1]}/tests"
                elif parts[0] == "tests":
                    family = f"tests/{parts[1]}" if len(parts) > 2 else "tests/root"
                else:
                    family = "coordination/tests"
                families.setdefault(family, []).append(rel.as_posix())
    families = {name: sorted(paths) for name, paths in sorted(families.items())}
    return {"schema_version": 1, "pattern": "test_*.py",
            "file_count": sum(map(len, families.values())), "families": families}


def serialize(data: dict) -> str:
    return json.dumps(data, indent=2, sort_keys=True) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    target = args.output if args.output.is_absolute() else root / args.output
    expected = serialize(inventory(root))
    if args.check:
        if not target.is_file() or target.read_text(encoding="utf-8") != expected:
            print("Inventory drift: regenerate with scripts/ci/hub_test_inventory.py")
            return 1
    else:
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
