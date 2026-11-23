#!/usr/bin/env python3
"""Fail when staged/changed tracked files contain client identifiers.

Prevention guard for the public-repo client-PII epic (#3095, sub-issue #3099).
This is the recurrence backstop the incomplete `.legal-deny-list.yaml` failed to
provide (it lacked the active clients, so the leak passed the old gate).

DESIGN
- **Name-agnostic + leak-safe.** Client identifiers live ONLY in a PRIVATE map
  (the same `client-codename-map.yaml` the redactor uses). This script contains
  no client names, and it NEVER prints a matched client string — only the file
  and line number — because CI logs on a public repo would themselves leak.
- **Engine parity with the redactor.** It reuses `redact-client-pii.py`'s exact
  matching: "if running the redactor would change this file, the file still
  contains an un-redacted client identifier → violation." Guard and redactor can
  never disagree about what counts as a client identifier.

SOURCING the private map
- `--map <path>` or `$LEGAL_CLIENT_MAP`, else default
  `config/agents/.client-codename-map.local.yaml` (gitignored; provisioned per
  host and, in CI, written from a GitHub Actions secret).
- If the map is absent: warn and exit 0 by default (degrade-open like the other
  enforcement scripts), or exit 2 under `--strict` (CI should run strict so a
  mis-provisioned secret fails loudly rather than silently passing).

USAGE
  # pre-commit (staged files):
  uv run python scripts/legal/check-client-pii.py --staged
  # CI (PR diff):
  uv run python scripts/legal/check-client-pii.py --base-ref origin/main --strict
  # explicit files or directories (a directory expands to its tracked files;
  # a missing path or a directory with no tracked files exits 2) / all tracked:
  uv run python scripts/legal/check-client-pii.py path1 path2
  uv run python scripts/legal/check-client-pii.py --all

Bypass (logged): LEGAL_PII_ALLOW=1
"""
from __future__ import annotations

import argparse
import importlib.util
import os
import subprocess
import sys
from pathlib import Path

_ENGINE_PATH = Path(__file__).resolve().parent / "redact-client-pii.py"
_spec = importlib.util.spec_from_file_location("redact_client_pii", _ENGINE_PATH)
_engine = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = _engine
_spec.loader.exec_module(_engine)

DEFAULT_MAP = Path("config/agents/.client-codename-map.local.yaml")

# Files that legitimately reference the private map path / tooling and must not
# self-trip the guard. (They contain no client names themselves.)
SELF_EXCLUDE = {
    "scripts/legal/check-client-pii.py",
    "scripts/legal/redact-client-pii.py",
    "scripts/legal/tests/test_check_client_pii.py",
    "scripts/legal/tests/test_redact_client_pii.py",
}


class GitListingError(RuntimeError):
    """git could not produce the target list; the scan must not read as clean."""


def _git(args: list[str]) -> list[str]:
    out = _git_z([*args[:1], "-z", *args[1:]])
    if out is None:
        raise GitListingError(f"git {' '.join(args)} failed")
    return out


def _git_z(args: list[str]) -> list[str] | None:
    """NUL-separated git listing (no path quoting). None when git fails."""
    out = subprocess.run(["git", *args], capture_output=True)
    if out.returncode != 0:
        return None
    return [p for p in out.stdout.decode("utf-8", "surrogateescape").split("\0") if p]


def expand_explicit(paths: list[str]) -> tuple[list[str], list[str]]:
    """Resolve explicit path arguments to files, failing closed.

    A directory expands to the git-tracked files beneath it (recursive, tracked
    only, so a gitignored private map inside it is never read). A directory with
    no tracked files, or a path that does not exist, is an error: it must never
    read as a clean scan. Returns (files, errors).
    """
    files: list[str] = []
    errors: list[str] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            tracked = _git_z(["ls-files", "-z", "--", raw])
            if tracked is None:
                errors.append(f"{raw}: directory, and git could not list its tracked files")
                continue
            tracked = [t for t in tracked if _scannable(Path(t))]
            if not tracked:
                errors.append(f"{raw}: directory contains no tracked files")
            files.extend(tracked)
        elif _scannable(p):
            files.append(raw)
        else:
            errors.append(f"{raw}: no such file")
    return files, errors


def collect_targets(args) -> list[str]:
    if args.all:
        return _git(["ls-files"])
    if args.base_ref:
        return _git(["diff", "--name-only", "--diff-filter=ACM", f"{args.base_ref}...HEAD"])
    # default: staged (pre-commit)
    return _git(["diff", "--cached", "--name-only", "--diff-filter=ACM"])


def _scannable(path: Path) -> bool:
    """A regular file, or a symlink (scanned as its link text, like git stores it)."""
    return path.is_symlink() or path.is_file()


def violations_in(path: Path, rules) -> list[int]:
    """Return 1-based line numbers that contain a client identifier (no values).

    A symlink is scanned as its target text, which is the content git tracks;
    following it would scan an unrelated file, or nothing when it dangles.
    """
    try:
        if path.is_symlink():
            text = os.readlink(path)
        else:
            text = path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError):
        return []
    hits: list[int] = []
    for i, line in enumerate(text.splitlines(), 1):
        _, n = _engine.redact_text(line, rules)
        if n:
            hits.append(i)
    return hits


def scan_text(text: str, rules, label: str) -> int:
    """Scan arbitrary text (a commit message, PR title/body) for client identifiers.

    Reuses the redactor engine so the guard never disagrees with the redactor.
    NEVER prints the matched text — only the caller-supplied `label` (e.g.
    "commit <sha>", "PR metadata"), so public CI logs can't leak the value.
    Returns 1 if an identifier is present, else 0.
    """
    _, n = _engine.redact_text(text, rules)
    if n:
        print(f"✖ Client identifier found in {label} — blocked (#3095/#3099).", file=sys.stderr)
        print("  (value withheld — public logs would leak it; remove the client name "
              "from the message/metadata, or squash-merge to drop it from history.)", file=sys.stderr)
        print("Bypass (discouraged): LEGAL_PII_ALLOW=1", file=sys.stderr)
        return 1
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--map", type=Path, default=Path(os.environ.get("LEGAL_CLIENT_MAP", DEFAULT_MAP)))
    ap.add_argument("--base-ref", help="scan files changed vs this ref (CI/PR mode)")
    ap.add_argument("--staged", action="store_true", help="scan staged files (pre-commit mode)")
    ap.add_argument("--all", action="store_true", help="scan all tracked files")
    ap.add_argument("--message-file", type=Path,
                    help="scan the text in this file (e.g. a commit message — the commit-msg hook's $1) instead of tracked files")
    ap.add_argument("--stdin", action="store_true",
                    help="scan text read from stdin (e.g. PR title/body, commit-range messages) instead of tracked files")
    ap.add_argument("--source", default=None,
                    help="label for the scanned text in messages (e.g. 'commit <sha>', 'PR metadata'); the matched value is never printed")
    ap.add_argument("--strict", action="store_true", help="fail (exit 2) if the private map is missing")
    ap.add_argument("paths", nargs="*", help="explicit files or directories to scan")
    args = ap.parse_args()

    if os.environ.get("LEGAL_PII_ALLOW") == "1":
        print("legal-client-pii: bypassed via LEGAL_PII_ALLOW=1", file=sys.stderr)
        return 0

    if not args.map.is_file():
        msg = f"legal-client-pii: private client map not found at {args.map}"
        if args.strict:
            print(f"{msg} — FAILING (strict). Provision it from the private archive / CI secret.", file=sys.stderr)
            return 2
        print(f"{msg} — skipping (degrade-open). #3099 CI gate is the strict backstop.", file=sys.stderr)
        return 0

    rules = _engine.load_rules(args.map)

    # Text mode (#3169): scan a commit message / PR metadata instead of files.
    if args.message_file is not None or args.stdin:
        if args.message_file is not None:
            try:
                text = args.message_file.read_text(encoding="utf-8")
            except OSError as e:
                msg = f"legal-client-pii: cannot read --message-file {args.message_file}: {e}"
                print(msg, file=sys.stderr)
                return 2 if args.strict else 0
            label = args.source or str(args.message_file)
        else:
            text = sys.stdin.read()
            label = args.source or "stdin"
        return scan_text(text, rules, label)

    target_errors: list[str] = []
    if args.paths:
        targets, target_errors = expand_explicit(args.paths)
    else:
        try:
            targets = collect_targets(args)
        except GitListingError as exc:
            print(f"✖ legal-client-pii: {exc} — failing closed (no target list, nothing scanned).",
                  file=sys.stderr)
            return 2

    bad: list[tuple[str, list[int]]] = []
    scanned = 0
    for rel in targets:
        if rel in SELF_EXCLUDE:
            continue
        fp = Path(rel)
        if not _scannable(fp):
            continue
        scanned += 1
        lines = violations_in(fp, rules)
        if lines:
            bad.append((rel, lines))

    if bad:
        print("✖ Client identifier(s) found in tracked file(s) — blocked (#3095/#3099).", file=sys.stderr)
        print("  (values withheld — public CI logs would leak them; codename-redact before committing.)", file=sys.stderr)
        for rel, lines in bad:
            shown = ",".join(map(str, lines[:10])) + (" …" if len(lines) > 10 else "")
            print(f"  {rel}: line(s) {shown}", file=sys.stderr)
        print("\nFix: uv run python scripts/legal/redact-client-pii.py --map <private-map> <file>", file=sys.stderr)
        print("Bypass (discouraged): LEGAL_PII_ALLOW=1", file=sys.stderr)

    if target_errors:
        print("✖ legal-client-pii: explicit target(s) could not be scanned — failing closed "
              "(a scan that read nothing is not a pass).", file=sys.stderr)
        for err in target_errors:
            print(f"  {err}", file=sys.stderr)
        return 2

    if bad:
        return 1

    print(f"✓ legal-client-pii: {scanned} file(s) scanned, clean.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
