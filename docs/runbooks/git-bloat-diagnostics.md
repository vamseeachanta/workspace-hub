# Git bloat diagnostics

The read-only report separates object storage, LFS storage, recovery backups and
other Git metadata. A large metadata directory alone does not establish either
unreachable objects or reclaimable history. This addresses the corrected
diagnosis in issue #3325 without removing recovery data or rewriting history.

## Revision history

| Revision | Date | Change and reason |
| --- | --- | --- |
| 1 | 2026-10-22 | Add storage accounting and proposed-target validation to distinguish backup growth from history bloat. |

## Scope and method

The implementation will cover three slices:

1. Measure the common Git directory using the existing footprint scanner, with
   separate object, LFS, recovery-backup and other byte totals. Linked worktrees
   will use the common directory rather than their small private directory.
2. Validate explicit proposed strip paths against HEAD, the index and every ref
   tip. Any exact match or descendant will block the path. Absence will indicate
   only a candidate for further review, never authorization to delete history.
3. Emit a JSON report, optional reachable-object measurement, and limitations.
   Missing evidence will be `NOT_EVALUATED`, never an invented zero or reclaim
   estimate. No ratio or size threshold will select a cleanup method.

Files: `scripts/workstations/git_bloat.py`,
`tests/workstations/test_git_bloat.py`, and this runbook. The existing footprint
helper will remain unchanged. Tests will use synthetic repositories and hand
calculations described in their docstrings. The diagnostics will perform no
cleanup, configuration changes, object writes or network operations.

## Usage

```sh
python -B scripts/workstations/git_bloat.py --repo . --timeout-seconds 60
python -B scripts/workstations/git_bloat.py --repo . --timeout-seconds 60 \
  --reachable --candidate old-output --candidate 'archived notes.txt'
```

The timeout is an explicit operational input, not an acceptance criterion. Run
against a quiescent repository. Output belongs in an authorized scratch location;
candidate paths can themselves be sensitive. Repository locations, host identity
and Git stderr are excluded from the report. Exit status indicates whether all
requested observations completed, not whether reclamation is authorized.

## Worked example

Synthetic input: object files contain 7 bytes, LFS files 11 bytes, recovery backups
13 bytes and other metadata 5 bytes. Logical file bytes total
`7 + 11 + 13 + 5 = 36`; non-object logical bytes total `11 + 13 + 5 = 29`.
These are hand-selected fixture inputs, not measurements of a real repository.
Directory entries and filesystem allocation rounding are excluded from logical
file bytes; allocated bytes are reported separately by the footprint scanner.

Suppose `archive/report.txt` appears at another branch tip, while `old-output`
appears at no tip or index entry. The first candidate is `BLOCKED_LIVE_PATH` even
if HEAD lacks it. The second is `ABSENT_FROM_TIPS`, which does not establish that
historical data is disposable. Reclaimable bytes remain `NOT_EVALUATED`: pack
delta dependencies, shared blobs, other refs and retention obligations preclude
subtracting logical byte totals to predict a rewrite's savings.

## Sources and interpretation

- [Git repository layout](https://git-scm.com/docs/gitrepository-layout), sections
  `commondir`, `objects` and `objects/info/alternates`: worktrees can share storage
  and alternate stores can hold objects outside the measured directory.
- [Git rev-parse](https://git-scm.com/docs/git-rev-parse), `--git-common-dir`:
  locate shared metadata. The existing footprint helper provides this resolution.
- [Git rev-list](https://git-scm.com/docs/git-rev-list), `--disk-usage` and `--all`:
  reachable object storage is an object measurement, not metadata-directory size.
  It is not a prediction of repacked or freshly cloned size. Reflog-only objects
  are excluded from this optional observation.
- [Git ls-tree](https://git-scm.com/docs/git-ls-tree), `-r`, `-t`, `-z`,
  `--name-only`: inspect tree paths with NUL delimiters, preserving whitespace,
  unusual names and explicit empty directories.
- [Git ls-files](https://git-scm.com/docs/git-ls-files), `--stage`, `-z`: observe
  index paths, object identities, modes and conflict stages; a content-only index
  change invalidates candidate evidence even if the path list is unchanged.
- [Git count-objects](https://git-scm.com/docs/git-count-objects), `size-pack` and
  `size-garbage`: object-store accounting has categories distinct from arbitrary
  sidecar files; no cleanup verdict follows from a total metadata-directory size.

These official manual sections were consulted on 2026-10-22. There are no
engineering coefficients, acceptance limits or inferred reclaim constants.

## Limits and later slices

Partial or shallow repositories, external alternates, redirected metadata,
inaccessible files, changing refs/index and failed Git commands prevent a complete
observation. Unknown allocations remain unknown. A report is not an atomic
snapshot, and transient changes restored during observation cannot be detected.
Candidate validation covers the selected checkout's HEAD and index plus named
refs. Detached HEADs and indexes in other linked worktrees, reflog-only states,
and historical retention obligations require separate review. An absent candidate
does not constitute a keep-list for an entire maintenance campaign.
Historical path discovery, rewrite rehearsal, before/after content parity across
all retained refs, retention decisions and measured reclamation remain later work
requiring a separately authorized maintenance operation. Existing skill commands
are not invoked by this report.
