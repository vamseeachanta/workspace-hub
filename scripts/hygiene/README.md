# Inventory of work files outside repositories

`inventory.py` inventories regular-file metadata outside repository roots and
configured cache directories. It uses Python 3.11's standard library and Git.
It reads the configuration, filesystem metadata and repository state, then writes
only the requested output file. It does not move, archive or delete files.

## Configuration

Pass a JSON object using `--config cfg.json`; no configuration is inferred from
the computer running the command. Relative `root` values resolve against the
current working directory. Relative `repos` entries resolve against `root`.

| Key | Type | Meaning |
| --- | --- | --- |
| `root` | required nonempty string | Directory to scan; recorded exactly as given. |
| `repos` | list of directory strings, default empty | Roots to prune and query. If empty, discover `.git` directories and files, including worktrees; check enclosing repositories before walking. |
| `cache_allow` | list of strings, default empty | Case-sensitive `fnmatchcase` patterns matched against directory names or root-relative POSIX paths. Matching directories are pruned. |
| `max_files` | required nonnegative integer | Maximum stray regular files; exceeding it is an error, never a truncated successful inventory. |
| `follow_symlinks` | boolean, default false | Follow links only within the resolved root. Directory identities prevent loops and repeated directory traversal. |
| `categories` | optional object | Replaces the extension conventions below. Keys are category names; values contain `extensions` and/or `names` lists. |
| `unpushed_hours` | finite nonnegative number, default 24 | Age threshold for locally reachable commits absent from locally recorded remote refs. |

The defaults of 24 hours, skipped links, 20 largest files and a strictly-greater
threshold comparison are local implementation conventions defined by this document.
Issue #4220 requests the inventory but does not specify these values; no accessible
source for the previously cited implementation slices has been established.
`max_files` is an input, rather than an assumed capacity or acceptance limit.
A zero bound permits an empty inventory only.

The conventional category names are `script`, `document`, `data`, `image`,
`archive`, `log`, `build output`, and `unknown`. The plain extension lists in
`DEFAULT_CATEGORIES` are conventions, not standards or content validation.
Matching uses case-insensitive exact names first, then the final extension;
unmatched files, including extensionless files, are `unknown`. For example,
`categories` can be `{"document": {"extensions": [".note"], "names": ["readme"]}}`.
An extension starts with a dot. Duplicate case-insensitive mappings are errors.
An omitted category rule contributes no mappings to a replacement table.

## Worked example

From the repository root, run the following Python script with `python -I`.
`TMPDIR` must name a writable temporary directory. The example leaves its
configuration, tree and manifest there for inspection. The invocation uses the
exact argument list shown in the script, with generated temporary paths.

```python
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

scanner = Path("scripts/hygiene/inventory.py").resolve()
base = Path(tempfile.mkdtemp(prefix="inventory-example-", dir=os.environ["TMPDIR"]))
root = base / "tree"
(root / "notes").mkdir(parents=True)
(root / "repo").mkdir()
git_env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
subprocess.run(["git", "init", "--quiet", str(root / "repo")], env=git_env, check=True)
(root / "repo" / "inside.md").write_bytes(b"ignored")
(root / ".cache").mkdir()
(root / ".cache" / "cached").write_bytes(b"ignored")
(root / "notes" / "draft.md").write_bytes(b"abc")
# Hand-worked example: one file, three bytes, mtime ten Unix seconds.
os.utime(root / "notes" / "draft.md", (10, 10))
# The bound is the hand-counted one-file example, not an operational default.
(base / "cfg.json").write_text(json.dumps({
    "root": "tree", "repos": [], "cache_allow": [".cache"], "max_files": 1
}), encoding="utf-8", newline="\n")
subprocess.run([
    sys.executable, "-I", str(scanner),
    "--config", "cfg.json", "--out", "manifest.json"
], cwd=base, check=True)
```

The command form is `python -I scripts/hygiene/inventory.py --config cfg.json
--out manifest.json`. This excerpt omits the varying generation timestamp and
aggregate objects, which are described below:

```json
{
  "schema": 1,
  "root": "tree",
  "files": [
    {"category": "document", "mtime": 10.0, "path": "notes/draft.md", "size": 3}
  ],
  "repos": [
    {"path": "repo", "dirty_count": 1, "unpushed_old_count": 0, "remote_ref_count": 0}
  ]
}
```

The stdout summary is:

```text
stray_files=1 bytes=3 repositories=1
```

Hand calculation: the repository and cache files are excluded. The sole stray
contains `abc`, giving count 1, bytes 3, oldest and newest mtime 10. Its category
and top-level directory are `document` and `notes`; each has the same totals.
The repository has one untracked file and no commits or remote refs.

## Manifest format

This document defines the local schema revision `1`; it is a format identifier,
not an externally standardized number. JSON object keys and file/repository
lists are sorted. Files use root-relative POSIX paths. Repository paths are
root-relative when possible; configured external and enclosing repositories retain
resolved POSIX paths. `root` retains its input spelling. `generated_utc` is an aware UTC ISO
timestamp; Python callers can supply `build_manifest(config, clock=callable)`
or `main(arguments, clock=callable)` for reproducibility. The CLI uses UTC now.
Identical metadata, configuration, repository state and clock produce identical
output bytes.

Each file has `path`, `size` in bytes, `mtime` in Unix seconds and `category`.
`totals` contains count, bytes, oldest/newest mtime and `largest_files`, together
with `categories` and `top_level` objects. Each group has the same aggregates
and its own largest-file list. A root-level file belongs to top-level `.`.
Largest-file lists contain at most 20 records, descending by size with path as
the tie-break. Empty sets have zero count/bytes, null extrema and empty lists.

Each `repos` record contains `path`, `dirty_count`, `unpushed_old_count` and
`remote_ref_count`. Status counts porcelain records, including individual
untracked files and excluding ignored files; a rename counts once. Old commits
are distinct commits reachable from any local ref or HEAD, excluding those
reachable from any remote-tracking ref, whose committer timestamp is strictly
older than the generation time minus the age threshold. A repository without
remote refs treats all its reachable commits as unpushed; an unborn repository
has no commits. Detached HEAD and local tags are included. Remote refs are an
offline observation and may be stale. The counter does not establish whether a
commit was ever uploaded to another remote or branch that was later removed.

## Exit codes

- `0`: complete manifest, with the stray count at or below `--fail-above N`
  when supplied.
- `1`: complete manifest written, stray count strictly above `N`.
- `2`: invalid arguments/configuration, nonexistent root, traversal failure,
  Git-query failure or output-write failure. No success summary is printed.

Use `--fail-above 0` to enforce an empty stray-file inventory. The threshold
counts every regular file outside excluded directories, including logs and
unknown extensions. It does not include dirty files inside repositories.
Git failures are errors, rather than invented zero counters. Error diagnostics
suppress filesystem paths and raw Git messages. Argument-parser errors use the
standard argparse diagnostics.

## Limits and sources

- No stray-file content inspection occurs. Only configuration content and Git's
  own metadata/state queries are read. Classification cannot identify secrets,
  determine value, prove ownership, or establish that a file is backed up.
- The cache allow-list and declared repository list are the maintainer's
  responsibility. With an explicit list, unlisted repositories are scanned as
  ordinary directories. Automatic discovery does not descend into a discovered
  repository or cache, so nested repositories there are not queried separately.
- Symlinks, directory junctions and other Windows reparse points are skipped by
  default. When enabled, broken/looping links and links outside the root are skipped; links into excluded directories are pruned.
  Regular-file hard links are counted per directory entry. Special files are
  excluded. Directory aliases are traversed only once in lexical traversal order.
- This is an observation, not an atomic filesystem snapshot. Concurrent changes
  may cause failure or inconsistent observations. Permission failures abort the
  inventory. A failed output write may leave an incomplete output file.
- Put output outside the scanned root; otherwise an existing manifest is itself
  a stray file. Output must not be the config file or an alias of the config file, or a symbolic link. No parent
  directories are created. A prior output remains in place if scanning fails.
- Repository queries use argument lists without a shell, clear inherited Git
  bindings, disable optional Git locks and disable filesystem-monitor hooks and
  the untracked cache. No fetch occurs. Git must be available for repo counters.

Sources (online editions retrieved 2026-10-22):

- [Python 3.11 os.scandir, stat results and os.utime](https://docs.python.org/3.11/library/os.html):
  traversal, file size/mtime and device/inode directory identity.
- [Git status, Porcelain Format Version 1](https://git-scm.com/docs/git-status):
  stable status records, NUL delimiters and rename path handling.
- [Git for-each-ref, refname field](https://git-scm.com/docs/git-for-each-ref):
  enumeration of locally recorded remote refs.
- [Git log, revision selection and pretty formats](https://git-scm.com/docs/git-log):
  `--all`, `--not`, `--remotes` and `%ct` define reachability and commit time.
- Existing repository convention: `scripts/repositories/work_surface_inventory.py`
  recognizes both `.git` directories and worktree files and emits sorted JSON.
- Issue #4220 defines the inventory scope. This document defines local defaults;
  independent hand calculations beside the tests and above define fixture totals.
