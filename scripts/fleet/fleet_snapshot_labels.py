#!/usr/bin/env python3
"""Rewrite fleet snapshot machine names to logical fleet labels (owner decision C18).

The fleet-daily-collector commits docs/reports/fleet-snapshots/<date>.json to
this PUBLIC repository. Physical machine hostnames must never land there; the
public form is the logical fleet label (ace-win-1, ace-linux-1, ...). The map
from physical name to label is private and is read at run time:

    --map PATH, else $FLEET_LABEL_MAP, else ~/.config/workspace-hub/fleet-label-map.txt

Map format, one entry per line, ``#`` starts a comment:

    <physical-name>  <logical-label>

Every label is also accepted as a name, so a labelled snapshot passes
unchanged. Any other public name is declared with an identity line
(``ace-linux-1  ace-linux-1``). Matching is case-insensitive.

Fail closed: a missing or malformed map, a machine name the map does not know,
or a mapped physical name left anywhere else in the file leaves the file
untouched and exits 2. Diagnostics never print a machine name, because the
collector's log may be copied into public surfaces.

The collector runs this on the snapshot before ``git add`` and skips the commit
when it exits non-zero:

    python3 scripts/fleet/fleet_snapshot_labels.py "$SNAPSHOT" || exit 1

``--check`` writes nothing and exits 1 when a rewrite is needed.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
import tempfile
from pathlib import Path

MAP_ENV = "FLEET_LABEL_MAP"
DEFAULT_MAP = Path("~/.config/workspace-hub/fleet-label-map.txt")


class LabelError(Exception):
    """A fail-closed condition. The message never carries a machine name."""


def map_path(arg: str | None) -> Path:
    if arg:
        return Path(arg)
    env = os.environ.get(MAP_ENV)
    if env:
        return Path(env)
    return DEFAULT_MAP.expanduser()


def load_map(path: Path) -> dict[str, str]:
    if not path.is_file():
        raise LabelError("label map not found; refusing to publish without it")
    table: dict[str, str] = {}
    for n, raw in enumerate(path.read_text(encoding="utf-8-sig").splitlines(), 1):
        line = raw.split("#", 1)[0].strip()
        if not line:
            continue
        parts = line.split()
        if len(parts) != 2:
            raise LabelError(f"label map line {n}: expected '<physical> <label>'")
        key = parts[0].casefold()
        if key in table:
            raise LabelError(f"label map line {n}: duplicate physical name")
        table[key] = parts[1]
    if not table:
        raise LabelError("label map is empty")
    # Every label is itself a known public name, so an already-labelled
    # snapshot passes unchanged.
    for label in list(table.values()):
        table.setdefault(label.casefold(), label)
    return table


def _label(name: object, table: dict[str, str], where: str) -> str:
    if not isinstance(name, str) or name.casefold() not in table:
        raise LabelError(f"{where}: machine name is not in the label map")
    return table[name.casefold()]


def relabel(data: dict, table: dict[str, str]) -> dict:
    machines = data.get("machines")
    if not isinstance(machines, list):
        raise LabelError("snapshot has no 'machines' list")
    for i, m in enumerate(machines):
        if not isinstance(m, dict) or "name" not in m:
            raise LabelError(f"machines[{i}]: entry has no name")
        m["name"] = _label(m["name"], table, f"machines[{i}]")
    gen = data.get("generated_by")
    if isinstance(gen, str) and gen.strip():
        head, sep, rest = gen.partition(" ")
        data["generated_by"] = _label(head, table, "generated_by") + sep + rest
    return data


def assert_no_physical(text: str, table: dict[str, str]) -> None:
    for phys, label in table.items():
        if phys == label.casefold():
            continue
        rx = re.compile(r"(?<![A-Za-z0-9-])" + re.escape(phys) + r"(?![A-Za-z0-9-])",
                        re.IGNORECASE)
        if rx.search(text):
            raise LabelError("a mapped physical name remains in the snapshot")


def render(data: dict) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def process(path: Path, table: dict[str, str], check: bool) -> bool:
    """Return True when the file needed (check) or received (write) a rewrite."""
    try:
        original = path.read_text(encoding="utf-8")
        data = json.loads(original)
    except (OSError, ValueError) as exc:
        raise LabelError(f"{path.name}: unreadable snapshot ({type(exc).__name__})")
    if not isinstance(data, dict):
        raise LabelError(f"{path.name}: snapshot is not a JSON object")
    out = render(relabel(data, table))
    assert_no_physical(out, table)
    if json.loads(out) == json.loads(original):
        return False
    if check:
        return True
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".fleet-label-", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(out)
        os.replace(tmp, path)
    except BaseException:
        if os.path.exists(tmp):
            os.unlink(tmp)
        raise
    return True


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n", 1)[0])
    ap.add_argument("snapshots", nargs="+")
    ap.add_argument("--map", help=f"private label map (else ${MAP_ENV}, else {DEFAULT_MAP})")
    ap.add_argument("--check", action="store_true", help="write nothing; exit 1 if a rewrite is needed")
    args = ap.parse_args(argv)
    try:
        table = load_map(map_path(args.map))
        changed = [p for p in args.snapshots if process(Path(p), table, args.check)]
    except LabelError as exc:
        print(f"fleet_snapshot_labels: {exc}", file=sys.stderr)
        return 2
    for p in changed:
        print(f"fleet_snapshot_labels: {'needs labels' if args.check else 'labelled'}: {Path(p).name}")
    return 1 if (args.check and changed) else 0


if __name__ == "__main__":
    sys.exit(main())
