#!/usr/bin/env python3
"""Rewrite fleet snapshot machine names to logical fleet labels (owner decision C18).

The fleet-daily-collector commits docs/reports/fleet-snapshots/<date>.json to
this PUBLIC repository. Physical machine hostnames must never land there; the
public form is the logical fleet label (ace-win-1, ace-linux-1, ...). The map
from physical name to label is private and is read at run time:

    --map PATH, else $FLEET_LABEL_MAP, else ~/.config/workspace-hub/fleet-label-map.txt

Map format, one entry per line, ``#`` starts a comment:

    <physical-name>  <logical-label>

Every label must be an approved public label (``is_public_label``): a logical
name from config/workstations/registry.yaml (ace-win-1, ace-linux-1, gpu-claw,
...) or, for hosts the registry does not list, a neutral label -- the collector
VM is ``fleet-collector``, a MacBook is ``mac-N`` and a Spark node is
``spark-N``. Every label is also accepted as a name, so a labelled snapshot
passes unchanged. A registry name that is already public is declared with an
identity line (``ace-linux-1  ace-linux-1``); an identity line for any other
name is refused. Matching is case-insensitive.

A branch value can carry a fragment of a physical name (``port/<fragment>-x``).
Each distinctive token of a physical name (four or more characters, not part
of any label) is rewritten to that host's label inside branch values; a token
shared by two hosts is ambiguous and is not rewritten.

Fail closed: a missing or malformed map, a label that is not an approved
public label, a machine name the map does not know, a mapped physical name or
one of its fragments left anywhere else in the file, or any Windows-hostname
shaped fragment leaves the file untouched and exits 2. Diagnostics never print a machine name, because the
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

# Approved public labels. Registry logical names plus the neutral labels for
# hosts the registry does not list (collector VM, MacBook, Spark node).
LABEL_RE = re.compile(
    r"^(?:ace-(?:linux|win)-[0-9]+|gpu-claw|fleet-collector|mac-[0-9]+|spark-[0-9]+)$")

# A fragment shaped like a physical Windows hostname (the suffix the identifier
# gate's windows-hostname rule keys on), anywhere in the rendered snapshot.
HOSTNAME_SHAPE_RE = re.compile(
    r"(?i)(?<![a-z0-9])(?:rds|ansys|ws|host|fs|srv|dc)[0-9]{2,}(?![0-9])")

_TOKEN_SPLIT = re.compile(r"[-_.]")


def is_public_label(value: object) -> bool:
    return isinstance(value, str) and bool(LABEL_RE.match(value))


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
        if not is_public_label(parts[1]):
            raise LabelError(f"label map line {n}: label is not an approved public label")
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


def fragments(table: dict[str, str]) -> dict[str, str | None]:
    """Distinctive tokens of each physical name -> its label (None if ambiguous)."""
    label_tokens = {t for lab in table.values() for t in _TOKEN_SPLIT.split(lab.casefold())}
    out: dict[str, str | None] = {}
    for phys, label in table.items():
        if phys == label.casefold():
            continue
        for tok in _TOKEN_SPLIT.split(phys):
            if len(tok) < 4 or tok in label_tokens:
                continue
            if tok in out and out[tok] != label:
                out[tok] = None
            else:
                out.setdefault(tok, label)
    return out


def _bounded(token: str, word_chars: str) -> re.Pattern[str]:
    return re.compile(rf"(?<![{word_chars}]){re.escape(token)}(?![{word_chars}])",
                      re.IGNORECASE)


def relabel_branch(branch: str, table: dict[str, str]) -> str:
    for phys, label in table.items():
        if phys != label.casefold():
            # Branch words are joined by '-' and '/', so only alphanumerics bound a name.
            branch = _bounded(phys, "A-Za-z0-9").sub(label, branch)
    for tok, label in fragments(table).items():
        if label is not None:
            branch = _bounded(tok, "A-Za-z0-9").sub(label, branch)
    return branch


def public_host_values_ok(data: dict) -> bool:
    """Every host value is an approved label and no hostname shape remains."""
    gen = data.get("generated_by")
    if isinstance(gen, str) and gen.strip() and not is_public_label(gen.split()[0]):
        return False
    machines = data.get("machines")
    if not isinstance(machines, list):
        return False
    if not all(isinstance(m, dict) and is_public_label(m.get("name")) for m in machines):
        return False
    return not HOSTNAME_SHAPE_RE.search(json.dumps(data, ensure_ascii=False))


def relabel(data: dict, table: dict[str, str]) -> dict:
    machines = data.get("machines")
    if not isinstance(machines, list):
        raise LabelError("snapshot has no 'machines' list")
    for i, m in enumerate(machines):
        if not isinstance(m, dict) or "name" not in m:
            raise LabelError(f"machines[{i}]: entry has no name")
        m["name"] = _label(m["name"], table, f"machines[{i}]")
        if isinstance(m.get("branch"), str):
            m["branch"] = relabel_branch(m["branch"], table)
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
    for tok in fragments(table):
        if _bounded(tok, "A-Za-z0-9").search(text):
            raise LabelError("a fragment of a mapped physical name remains in the snapshot")
    if HOSTNAME_SHAPE_RE.search(text):
        raise LabelError("a hostname-shaped fragment remains in the snapshot")


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
    labelled = relabel(data, table)
    out = render(labelled)
    assert_no_physical(out, table)
    if not public_host_values_ok(json.loads(out)):
        raise LabelError("a host value is not an approved public label")
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
