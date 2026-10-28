#!/usr/bin/env python3
"""Render independently resolved commits from an explicit JSON list of refs.

Only current local refs are read. No fetch, Git write, label interpretation or
approval authentication occurs. See docs/guides/handoff-ref-table.md for usage.
"""

import argparse
import html
import json
import os
import re
import subprocess
import sys
from pathlib import Path


# Git hash-function-transition, Object names: SHA-1 has 40 hexadecimal digits;
# SHA-256 has 64. git rev-parse --verify emits a full object name.
# gitrevisions, SPECIFYING REVISIONS: special top-level revision names.
_PSEUDOREFS = {
    "HEAD", "FETCH_HEAD", "ORIG_HEAD", "MERGE_HEAD", "REBASE_HEAD",
    "REVERT_HEAD", "CHERRY_PICK_HEAD", "BISECT_HEAD", "AUTO_MERGE",
}
_COMMIT_ID = re.compile(r"(?:[0-9a-f]{40}|[0-9a-f]{64})")
_HEADER = "| Issue | Local ref | Commit ID |\n| --- | --- | --- |\n"


class RefTableError(ValueError):
    """The supplied rows cannot be resolved to an unambiguous commit table."""


def _valid_ref(ref):
    # git check-ref-format, DESCRIPTION: named refs exclude revision syntax,
    # controls, empty components, leading dots and components ending in .lock.
    return (
        isinstance(ref, str) and bool(ref) and ref != "@" and ref not in _PSEUDOREFS
        and not ref.startswith("-") and not ref.endswith(".")
        and ".." not in ref and "@{" not in ref
        and not any(char.isspace() or ord(char) < ord(" ")
                    or char == "\x7f" or char in "~^:?*[\\" for char in ref)
        and all(part and not part.startswith(".") and not part.endswith(".lock")
                for part in ref.split("/"))
    )


def _validate_rows(rows):
    if not isinstance(rows, list):
        raise RefTableError("expected a JSON list of issue/ref rows")
    issues, refs = set(), set()
    for row in rows:
        if not isinstance(row, dict) or set(row) != {"issue", "ref"}:
            raise RefTableError("each row must contain only issue and ref")
        issue, ref = row["issue"], row["ref"]
        # Issue identifiers are positive integers; booleans are not identifiers.
        if type(issue) is not int or issue <= 0 or not _valid_ref(ref):
            raise RefTableError("invalid issue number or local ref name")
        if issue in issues or ref in refs:
            raise RefTableError("duplicate issue or local ref")
        issues.add(issue)
        refs.add(ref)
    return sorted(rows, key=lambda row: row["issue"])


def _git(repo, args, run):
    # Git environment documentation: clear inherited repository/config bindings;
    # disable replacements, lazy fetching, optional locks and interactive prompts.
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(GIT_NO_REPLACE_OBJECTS="1", GIT_NO_LAZY_FETCH="1",
               GIT_OPTIONAL_LOCKS="0", GIT_TERMINAL_PROMPT="0")
    try:
        result = run(
            ["git", "-C", str(repo), "-c", "core.warnAmbiguousRefs=true",
             "rev-parse", *args],
            capture_output=True, text=True, check=True, env=env,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        # Diagnostics can contain private ref names or locations. Do not echo them.
        raise RefTableError("could not resolve a local commit ref") from exc
    if result.stderr:
        # rev-parse can report ambiguity with a successful exit status.
        raise RefTableError("could not resolve an unambiguous local commit ref")
    return result.stdout.strip()


def render_table(rows, repo, *, run=None):
    """Return a deterministic Markdown table, or raise without partial output.

    Each row gets fresh Git reads, even when commit IDs happen to be equal.
    The injected callable follows subprocess.run's interface for offline tests.
    """
    ordered = _validate_rows(rows)
    run = subprocess.run if run is None else run
    lines = [_HEADER]
    canonical_refs = set()
    for row in ordered:
        ref = row["ref"]
        canonical = _git(repo, ["--verify", "--symbolic-full-name",
                                "--end-of-options", ref], run)
        if not canonical.startswith("refs/") or not _valid_ref(canonical):
            raise RefTableError("expected an unambiguous named local ref")
        if canonical in canonical_refs:
            raise RefTableError("duplicate local ref after name resolution")
        canonical_refs.add(canonical)
        # git rev-parse, OPTIONS: --end-of-options protects untrusted operands;
        # <rev>^{commit} requires a commit (possibly through an annotated tag).
        commit = _git(repo, ["--verify", "--end-of-options", canonical + "^{commit}"], run)
        if not _COMMIT_ID.fullmatch(commit):
            raise RefTableError("expected a full immutable commit ID")
        display_ref = html.escape(ref).replace("|", "&#124;").replace("`", "&#96;")
        lines.append(f"| #{row['issue']} | <code>{display_ref}</code> | `{commit}` |\n")
    return "".join(lines)


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise RefTableError("duplicate JSON object key")
        result[key] = value
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Render commits from current local refs; conveys no approval.",
    )
    parser.add_argument("input", type=Path, help="JSON list of issue/ref objects")
    parser.add_argument("--repo", type=Path, default=Path("."), help="local Git checkout")
    args = parser.parse_args(argv)
    try:
        rows = json.loads(args.input.read_text(encoding="utf-8"),
                          object_pairs_hook=_unique_object)
        output = render_table(rows, args.repo)
    except (OSError, UnicodeError, json.JSONDecodeError, RefTableError):
        print("error: invalid input or unavailable local commit ref", file=sys.stderr)
        # POSIX exit status convention: nonzero failure, zero success.
        return 1
    sys.stdout.write(output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
