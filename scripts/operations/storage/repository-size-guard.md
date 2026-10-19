# Repository size guard

`repository_size_guard.py` supplies the first part of G1 in issue #4085.
It checks the logical blob bytes of one immutable Git tree. The command reads
Git metadata and an explicit policy; it does not change files, advance a
baseline, fetch content, prune data, or install enforcement in a caller.

## Policy and calculation

All three policy fields are required:

- `max_total_bytes`: nonnegative integer total budget, supplied from a reviewed
  baseline. Keeping or lowering this input implements a size ratchet; the
  command does not authenticate or update that baseline.
- `max_file_bytes`: nonnegative integer ordinary file cap.
- `exceptions`: exact tree-relative paths mapped to nonnegative integer caps.
  An exception remains bounded and still contributes to the total budget.

There are no default byte limits. The issue's MB wording does not distinguish
binary and decimal units, so conversion and acceptance limits remain explicit
inputs. Boolean, fractional, negative, missing, duplicate and unknown policy
fields are rejected. Paths must be canonical relative paths. Matching is literal
and case-sensitive; wildcard characters have no special meaning.

Let `s(p)` be the uncompressed blob size in bytes at path `p`, as documented by
[Git git-ls-tree(1), version 2.42.0 (2023), Output Format][tree-format]. The check defines
`T = sum(s(p))` over all blob entries. Separate paths to the same object each
contribute their blob size. A symlink contributes its stored target-text bytes,
without following the target. This is a logical tree budget, excluding history,
Git metadata, compression, filesystem allocation and untracked files.

For total cap `B`, ordinary cap `F` and exception mapping `E`, block when
`T > B` or when any `s(p) > E.get(p, F)`. These comparisons implement the
explicit budget rule in issue #4085; equality passes. Integer arithmetic is
used throughout. No physical engineering coefficients or implicit acceptance
limits enter the calculation.

The following policy is synthetic test data, not a recommended budget. Its
expected outcomes are hand-calculated in
`tests/operations/storage/test_repository_size_guard.py`: two files of five
bytes total ten bytes and pass; three files of four, four and three bytes total
eleven and block. A seven-byte exception still counts toward the total.

```json
{
  "max_total_bytes": 10,
  "max_file_bytes": 5,
  "exceptions": {"data/a": 7}
}
```

## Command and exit status

```bash
python scripts/operations/storage/repository_size_guard.py \
  --repo "$REPOSITORY" --policy "$SIZE_POLICY" --revision HEAD
```

`--revision` defaults to `HEAD` and accepts a commit or tree reference. It is
resolved to a tree object once, then inspected with `git ls-tree -r -l -z
--full-tree`. NUL-delimited parsing preserves spaces, tabs and newlines in
filenames. Git repository-binding environment variables are removed for child
commands. Replacement objects are disabled, and Git transports are denied using
the empty `GIT_ALLOW_PROTOCOL` list documented in [git(1), version 2.42.0,
Environment Variables][git-environment].
A missing object in a partial clone produces an unknown outcome instead of a
network fetch. Missing tools and Git errors do not disclose their raw stderr.

The command emits one JSON object. Evaluated results include `status`,
`total_bytes`, `max_total_bytes`, `file_count`, `total_exceeded`, and a list of
per-path `violations` with measured and limiting bytes. Unknown results contain
`status` and a fixed-category `reason`.

| Exit | Status | Interpretation |
| --- | --- | --- |
| 0 | PASS | The inspected tree meets every supplied cap. |
| 1 | BLOCK | The total budget or an individual cap is exceeded. |
| 2 | NOT_EVALUATED | A required policy, tool, tree or blob size is unavailable. |

Argument syntax errors also exit 2 through the argument parser. Submodules
produce `NOT_EVALUATED`: Gitlinks do not supply their content sizes. A caller
shall accept only exit 0 when enforcing a budget.

## Verification and remaining scope

Tests use synthetic records, independently stated integer arithmetic and
object-only disposable repositories. They do not commit or index files, change
the inspected repository, contact a remote, or need a mounted test filesystem.
The existing hosted storage-test step discovers this test module; its hosted
result remains pending until publication.

Later slices may establish and protect reviewed baseline manifests, integrate
this check into callers, measure physical/history size, and implement the
remaining storage guards. This slice does not install a size policy for the
current repository or certify the provenance of caller-supplied limits.

[tree-format]: https://git-scm.com/docs/git-ls-tree/2.42.0#_output_format
[git-environment]: https://raw.githubusercontent.com/git/git/v2.42.0/Documentation/git.txt
