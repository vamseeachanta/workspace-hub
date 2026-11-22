# Reviewed file moves

The planner consumes an inventory of stray files and proposes repository
destinations. Dry-run is the default. Applying a reviewed plan copies and verifies
each file before removing its original name. Undo uses the same protocol.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| 1 | 2026-10-22 | Add proposals, summaries, verified moves, staging and undo to preserve stray work files in repositories. |
| 2 | 2026-10-24 | Refuse unterminated logs before resume, write text with UTF-8 and LF, and reject directory reparse points to preserve recovery boundaries. |

## Inputs and conventions

The runtime requires Python 3.11 or later and only the standard library. Git is
required only for `--git-add`. All locations come from runtime inputs.

Inventory schema 1 is the contract supplied with issue #4221, extending #4220:

```json
{
  "schema": 1,
  "root": "<absolute temporary tree>",
  "repos": [{"path": "repos/notes", "name": "notes"}],
  "files": [{"path": "loose/a.txt", "size": 3,
             "mtime": "2026-01-01T00:00:00Z", "category": "work"}]
}
```

`root` is an existing absolute directory without symlinks. File and repository
paths are relative to it, with POSIX separators. Repository names are unique.
Inventory timestamps and categories are descriptive; content hashes and sizes
control apply. A file already inside a declared repository is rejected as an
invalid stray-file inventory. The planner does not discover repositories.

Configuration is a JSON object:

```json
{
  "rules": [{"match": "loose", "repo": "notes", "dest": "docs"}],
  "default_repo": "notes",
  "ignore": ["*.cache"]
}
```

- `rules` is an ordered list; the first matching rule wins. `match` containing
  `*`, `?` or `[` uses case-sensitive `fnmatchcase` over the whole relative path.
  Other matches are exact paths or directory prefixes at component boundaries.
  For example, `loose` matches `loose/a.txt`, whereas `loo` does not.
- `repo` names an inventory repository. `dest` is a directory relative to that
  repository; `.` means its root. The source basename is preserved.
- `default_repo` is optional and places otherwise unmatched basenames at that
  repository's root. Without it, unmatched files remain in the plan and are
  never moved.
- `ignore` is an optional list of case-sensitive globs. Ignored files contribute
  only to the ignored count. An empty `rules` list is allowed.
- Absolute paths, traversal, backslashes, colons, control characters, `.git`
  components (including case aliases), trailing dots or spaces, reserved device
  names, symlinks and Windows reparse points are refused at endpoints and their
  ancestors, including root ancestors and file reparse points. Repository directories must exist. Destination parent directories may be created during apply.

The plan records `schema`, `kind`, `root`, `repos`, `entries` and `summary`.
Each entry has `source`, `repo`, `dest`, `size`, `reason` and `status`. Matched
regular files also receive `sha256` and `conflicts`. Rule indices are zero-based;
default assignments use `reason: "default_repo"`. Status is `ready`, `conflict`
or `unmatched`. Sources and destinations are relative to the inventory root.
Existing destinations and multiple sources targeting one destination flag all
affected entries as conflicts. No suffix or alternate target is invented.

The summary contains count and bytes per repository, total bytes, conflicts,
unmatched and ignored counts. Counts include conflicted proposals; total bytes
include unmatched files and exclude ignored files. Human-readable output and
the JSON summary describe the same totals. A dry-run writes only `--out`;
it never creates destination directories. Output creation is exclusive: use a
new filename to preserve an earlier plan.

## Worked example

Run the following block from the repository root. It creates a temporary tree
and keeps all inputs, plans and logs there. `EXAMPLE_DIR` may select a new example
directory; otherwise the standard temporary directory facility selects it.
The fixture contains the ASCII bytes `abc`, so its independent byte total is
one file of three bytes. No engineering acceptance limit is assumed.

```sh
set -eu
TOOL="$PWD/scripts/hygiene/plan_moves.py"
EXAMPLE="${EXAMPLE_DIR:-$(python -I -c 'import tempfile; print(tempfile.mkdtemp(prefix="move-example-"))')}"
export EXAMPLE
python -I - <<'PY'
import json
import os
from pathlib import Path

example = Path(os.environ["EXAMPLE"])
root = example / "tree"
(root / "repos/notes").mkdir(parents=True)
(root / "loose").mkdir()
(root / "loose/a.txt").write_bytes(b"abc")
manifest = {
    "schema": 1,  # Issue #4221: inventory schema version 1.
    "root": str(root),
    "repos": [{"path": "repos/notes", "name": "notes"}],
    "files": [{"path": "loose/a.txt", "size": len(b"abc"),
               "mtime": "2026-01-01T00:00:00Z", "category": "work"}],
}
rules = {"rules": [{"match": "loose", "repo": "notes", "dest": "docs"}]}
(example / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8", newline="\n")
(example / "rules.json").write_text(json.dumps(rules), encoding="utf-8", newline="\n")
PY
git init --quiet "$EXAMPLE/tree/repos/notes"
python -I "$TOOL" --manifest "$EXAMPLE/manifest.json" --config "$EXAMPLE/rules.json" --out "$EXAMPLE/plan.json"
# Inspect plan.json before computing and supplying its confirmation token.
TOKEN="$(python -I -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$EXAMPLE/plan.json")"
python -I "$TOOL" --apply "$EXAMPLE/plan.json" --log "$EXAMPLE/apply.log.jsonl" --confirm "$TOKEN"
python -I "$TOOL" --undo-from-log "$EXAMPLE/apply.log.jsonl" --out "$EXAMPLE/undo.json"
UNDO_TOKEN="$(python -I -c 'import hashlib,sys; print(hashlib.sha256(open(sys.argv[1], "rb").read()).hexdigest())' "$EXAMPLE/undo.json")"
python -I "$TOOL" --apply "$EXAMPLE/undo.json" --log "$EXAMPLE/undo.log.jsonl" --confirm "$UNDO_TOKEN"
python -I - <<'PY'
import os
from pathlib import Path

root = Path(os.environ["EXAMPLE"]) / "tree"
assert (root / "loose/a.txt").read_bytes() == b"abc"
assert not (root / "repos/notes/docs/a.txt").exists()
print("Example completed.")
PY
```

Plan entry excerpt (content digest omitted here):

```json
{"source":"loose/a.txt","repo":"notes","dest":"repos/notes/docs/a.txt",
 "size":3,"reason":0,"status":"ready","conflicts":[]}
```

Log excerpts (context and content digest omitted here):

```json
{"source":"loose/a.txt","destination":"repos/notes/docs/a.txt","result":"copied"}
{"source":"loose/a.txt","destination":"repos/notes/docs/a.txt","result":"done"}
```

Each actual line additionally records UTC `time`, `root`, `repos`, `repo`, `size`,
content `hash` and `plan_sha256`. Tests inject a clock; ordinary CLI runs use UTC.
The independently calculated expected destination appends `docs/a.txt` to
`repos/notes`, with rule index zero because that rule is first.

## Apply, staging and recovery

`--apply PLAN --log LOG --confirm TOKEN` requires the SHA-256 of the exact plan
file bytes. Even a whitespace edit needs a new token. Conflicts refuse the whole
run before moves. A confirmed plan is a filesystem instruction, so review its
root, repository declarations, paths and hashes; the token is not authorization
or a signature. Keep plans and logs private when runtime paths are sensitive.

The tool never deletes the only verified copy. It exclusively creates a copy,
flushes it, verifies size and SHA-256 against the plan, verifies the source again,
and appends a flushed `copied` receipt before removing the source name. It then
appends `done`. Neither existing files nor partial copies are overwritten or
automatically removed. Undo reverses completed moves using identical checks.
File permissions and other metadata are not preserved; verification covers bytes.

Re-run the identical apply command and log to resume. A `copied` receipt permits
finishing the removal after re-verification, including when interruption happened
after removal but before `done`. `done` steps verify the destination and skip
copying; a recreated source causes refusal. A log for a different plan is refused.
A log whose final record lacks LF is refused before resume changes any files,
even when that record contains complete JSON. A truncated log or a copy
interrupted before its `copied` receipt requires manual
inspection. The tool preserves both the log and any partial copy; it does not
truncate or repair them. Preserve a copy of the log before manual inspection.
Check the final record against the reviewed plan and the actual source and
destination bytes. If inspection establishes that only the final LF is missing,
append exactly one LF and repeat the original apply command before generating
undo. Otherwise retain both copies and the log for further inspection.

Logs use UTF-8 with LF record boundaries; existing CRLF records are readable.
The writer also refuses to extend an unterminated record. Flushes improve
durability but do not provide a transaction spanning the filesystem and log
across power loss.

Use exclusive access to the source tree, destination repositories and log during
apply. Concurrent writers, symlink swaps, changing mounts and concurrent apply
processes are outside the supported contract. Paths and content are rechecked
before removal, but portable path operations cannot exclude every concurrent
filesystem mutation. The tool does not provide a locking service.

`--git-add` is optional and off by default. It verifies the destination Git root,
queries effective `filter` attributes, refuses `filter=lfs`, and stages only the
explicit destination path using literal pathspecs. It never commits or pushes.
`staged` receipts include `staged_paths` relative to the destination repository.
If staging fails after a completed move, resume retries staging without copying.
An existing Git index is preserved except for these explicit additions. Undo does
not stage or unstage anything; inspect the index after reversing a staged move.

`--undo-from-log LOG --out undo.json` builds a reverse plan from `done` receipts,
in reverse completion order. Review and apply that new plan with its own digest
and separate log. Recreated original paths are never overwritten. Resume the
original apply before undo if its final removal has no `done` receipt yet.

## Exit codes

These CLI protocol values are defined here, rather than engineering criteria:

| Code | Meaning |
| --- | --- |
| 0 | Plan written, or apply completed; unmatched entries remain untouched. A written plan may contain conflicts for review. |
| 1 | Input, verification, filesystem, LFS or Git operation refused or failed. Completed earlier steps remain logged. |
| 2 | Invalid CLI argument combination, reported by argparse. |

## Sources and verification basis

- Issues #4221 and #4220: schema, ordered rules, dry-run, SHA-256 confirmation,
  verified moves, log, optional explicit staging and undo requirements.
- [Python 3.11 fnmatchcase](https://docs.python.org/3.11/library/fnmatch.html#fnmatch.fnmatchcase):
  case-sensitive wildcard comparisons. Prefix boundary matching is defined above.
- [Python 3.11 hashlib](https://docs.python.org/3.11/library/hashlib.html#hashlib.file_digest):
  hashing binary files. Plan digests cover the original JSON bytes.
- [Python 3.11 shutil](https://docs.python.org/3.11/library/shutil.html#shutil.copyfileobj):
  bounded default copy chunking; the tool explicitly flushes and verifies copies.
- [Python 3.11 pathlib](https://docs.python.org/3.11/library/pathlib.html#pathlib.PurePath.is_reserved):
  reserved device names are rejected independently of the current platform.
- [Git add](https://git-scm.com/docs/git-add): explicit pathspecs and literal matching.
- [Git check-attr](https://git-scm.com/docs/git-check-attr#_output): effective
  attributes and NUL-delimited output, including destination LFS detection.

The tests use synthetic temporary trees. Expected paths, rule indices, counts and
byte totals are hand calculations written in their docstrings. The worked shell
block is executed verbatim, including undo. No licensed inputs are used.
