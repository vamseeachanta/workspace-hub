#!/usr/bin/env python3
"""Check archived marine skills for public-safe residual identifiers.

This file intentionally contains no real client, vessel, contractor, project,
person, or account names. The checks use generic patterns so the public guard
does not preserve the sensitive strings it is meant to prevent.

Limit: this script cannot detect a name that stands outside a label line, such
as prose, table cells, file names, option names, or identifiers. A clean result
is not evidence that names are absent; a manual full read-through of the files
is still required.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_SUBTREE = REPO_ROOT / (
    ".claude/_archive/2026-10-09-l8/.claude/skills/engineering/marine-offshore"
)

SLASH = chr(47)
BACKSLASH = chr(92)

RULES = {
    "drive_abs": re.compile(r"(?<![A-Za-z])[A-Za-z]:(?!//)" + r"[\\/]" + r"[^\s`\"')]+"),
    "unc_share": re.compile(re.escape(BACKSLASH * 2) + r"[^\\/\s]+[\\/][^\\/\s]+"),
    "home_path": re.compile(
        r"("
        + re.escape(SLASH)
        + r"(home|Users)"
        + re.escape(SLASH)
        + r"[^/\s]+"
        + re.escape(SLASH)
        + r"|[A-Za-z]:"
        + re.escape(BACKSLASH)
        + r"Users"
        + re.escape(BACKSLASH)
        + r"[^\\\s]+"
        + re.escape(BACKSLASH)
        + r")"
    ),
    "mount_path": re.compile(
        re.escape(SLASH)
        + r"(mnt|media|Volumes)"
        + re.escape(SLASH)
        + r"[^/\s]+"
        + re.escape(SLASH)
    ),
    "codename_mapping": re.compile(
        r"(?i)(['\"][^'\"]+['\"]\s*(=|->|\bis\b)\s*"
        r"(Client|Vessel|Contractor|Project)\s+[A-Z]\b)"
    ),
}

LABEL_RE = re.compile(
    r"(?i)^\s*(?:[-*]\s*)?(client|vessel|operator|project|contractor)\s*:\s*(.+?)\s*$"
)
CODENAME_RE = re.compile(r"^(Client|Vessel|Contractor|Project)\s+[A-Z]$")
PLACEHOLDER_RE = re.compile(r"^<[^>\n]+>$")
NEUTRAL_DESCRIPTIONS = {
    "a deepwater drillship",
    "a semi-submersible operator",
    "a floating production unit",
    "an installation vessel",
    "a generic offshore asset",
    "a public reference case",
}

# Explicit exceptions are keyed by (repo-relative file path, rule). Each entry
# must include a one-line justification. No directory blanket exemptions.
ALLOWLIST: dict[tuple[str, str], str] = {}


def is_text_file(path: Path) -> bool:
    try:
        path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False
    return True


def allowed_label_value(value: str) -> bool:
    stripped = value.strip().strip("'\"")
    if CODENAME_RE.match(stripped) or PLACEHOLDER_RE.match(stripped):
        return True
    if stripped.lower() in NEUTRAL_DESCRIPTIONS:
        return True
    if stripped.startswith(("{", "[", "$", "`")):
        return True
    return False


def is_typed_signature_parameter(label: str, value: str) -> bool:
    stripped = value.strip()
    if not stripped.endswith(","):
        return False
    if not re.fullmatch(r"[A-Za-z_][\w.]*(?:\[[^\]\n]+\])?,", stripped):
        return False
    return label.lower() in {"client", "vessel", "operator", "project", "contractor"}


def rules_for_line(line: str) -> list[str]:
    matches = [name for name, pattern in RULES.items() if pattern.search(line)]
    label_match = LABEL_RE.match(line)
    if (
        label_match
        and not is_typed_signature_parameter(label_match.group(1), label_match.group(2))
        and not allowed_label_value(label_match.group(2))
    ):
        matches.append("label_identifier")
    return matches


def iter_files(root: Path) -> list[Path]:
    if root.is_file():
        return [root]
    return sorted(p for p in root.rglob("*") if p.is_file() and is_text_file(p))


def repo_relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def scan(root: Path) -> list[tuple[Path, int, str]]:
    violations: list[tuple[Path, int, str]] = []
    for path in iter_files(root):
        rel = repo_relative(path)
        text = path.read_text(encoding="utf-8")
        for line_number, line in enumerate(text.splitlines(), 1):
            for rule in rules_for_line(line):
                if (rel, rule) not in ALLOWLIST:
                    violations.append((path, line_number, rule))
    return violations


def self_test() -> int:
    slash = SLASH
    backslash = BACKSLASH
    cases = [
        ("drive_abs", "tool root is " + "Q:" + slash + "example"),
        ("unc_share", "share " + backslash * 2 + "server" + backslash + "share"),
        ("home_path", "root " + slash + "home" + slash + "person" + slash + "repo"),
        ("home_path", "root " + "C:" + backslash + "Users" + backslash + "person" + backslash),
        ("mount_path", "root " + slash + "mnt" + slash + "disk" + slash + "repo"),
        ("codename_mapping", '"Example Name" -> Client A'),
        ("label_identifier", "client: Example Name"),
    ]
    for expected, text in cases:
        if expected not in rules_for_line(text):
            print(f"self-test failed: {expected} did not fire", file=sys.stderr)
            return 1
    allowed = [
        "public reference: https://example.org/docs",
        "client: Client A",
        "vessel: Vessel A",
        "operator: a semi-submersible operator",
        "project: <project-name>",
        "vessel: { length: 300.0 }",
        "    vessel: OrcFxAPI.OrcaFlexObject,",
    ]
    for text in allowed:
        if rules_for_line(text):
            print("self-test failed: allowed form was rejected", file=sys.stderr)
            return 1
    print("archived marine skill check self-test OK")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("subtree", nargs="?", default=str(DEFAULT_SUBTREE))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    root = Path(args.subtree)
    if not root.exists():
        print(f"check-archived-marine-skills: path not found: {root}", file=sys.stderr)
        return 2

    violations = scan(root)
    for path, line_number, rule in violations:
        print(f"{path.as_posix()}:{line_number}: RULE {rule}")
    if violations:
        print(
            f"check-archived-marine-skills: {len(violations)} violation(s) found",
            file=sys.stderr,
        )
        return 1
    print("check-archived-marine-skills: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
