# Job Queue Worktree Footprint Analysis

## Summary

Four Git layouts are measured on a disposable, synthetic repository. The linked
worktree adds no object storage; it still contains a full checkout and separate
administrative files. Production storage savings remain unestablished. The
versioned queue scripts remain integration examples; live integration must
preserve job execution and concurrency controls.

## Revision History

| Revision | Date | What Changed | Why |
|---|---:|---|---|
| 0 | 2026-10-14 | Initial footprint note for the versioned queue scripts. | The queue needed a reviewed path to reduce accumulated worktree storage. |
| 1 | 2026-10-15 | Recast as a measurement plan and correct integration claims. | Storage measurements and live installation remain unestablished. |
| 2 | 2026-10-20 | Add a reproducible stand-in comparison and cleanup regressions. | Distinguish measured byte counts from production storage assumptions. |

## Source Basis

| Item | Result |
|---|---|
| Script source of truth | The pump, runner, launchers, and limits file were live local queue files and were not versioned in this repository before this change. |
| Live digests | Installation records digests before changing live files. No live-file digest is established here. |
| Live mutation | The live files were read only; installation is not performed by this change. |

## Footprint

The measurement tool is `scripts/operations/job_queue_footprint.py`. It clones a
local source into a new experiment directory and creates a linked worktree from
that disposable full clone. The original source is read only. Existing experiment
directories are refused; no worktree, branch or data is removed by the tool.
The shallow clone uses file transport so its depth request is honored. The full
and sparse clones disable object hardlinks so their storage is independent.

The recorded run used Git 2.43.0 on 2026-10-20. The fixture has two revisions and
three tracked files: `README.md`, `selected/item.txt`, and `excluded/item.txt`.
At the measured revision their contents are respectively `abcd` plus newline,
`xy` plus newline, and `z` plus newline. Independent payload calculation:
5 + 3 + 2 = 10 bytes. Cone-mode selection of `selected` also retains the root
file, so the sparse payload is 5 + 3 = 8 bytes. These counts come from the literal
fixture in `scripts/operations/tests/test_job_queue_footprint.py`.

| Layout | Payload (bytes) | Metadata (bytes) | Incremental objects (bytes) | Reachable commits |
|---|---:|---:|---:|---:|
| Full clone | 10 | 28521 | 751 | 2 |
| Linked worktree | 10 | 745 | 0 | 2 |
| Depth-one clone | 10 | 29644 | 1799 | 1 |
| Sparse full-history clone | 8 | 28843 | 751 | 2 |

Table 1. Logical file sizes at the time of measurement; object bytes are included
in metadata, not added to it. Linked metadata is excluded from the full-clone
metadata row to avoid double counting.

The retained numerical output is [the measurement record](examples/job-queue-footprint.json).
The linked increment is payload plus its metadata: 10 + 745 = 755 bytes for this
fixture, with the full clone already present. The full-clone increment is
10 + 28521 = 28531 bytes. These are arithmetic sums of measured file lengths;
filesystem allocation, peak usage, generated files, environments and caches are
excluded. Metadata depends on path length, Git configuration and repository
format; the byte totals are observations, not portable acceptance constants.
The shallow clone is larger here because packed-object overhead dominates the
tiny fixture. No production ranking follows from that row.

## Reproduction and sources

Run the fixture test in a new scratch directory, then run the tool on its source:

```sh
python -m pytest scripts/operations/tests/test_job_queue_footprint.py \
  -k layouts -p no:cacheprovider --basetemp=<scratch>/fixture
python scripts/operations/job_queue_footprint.py \
  <scratch>/fixture/test_layouts_have_independentl0/source \
  <scratch>/new-experiment --sparse-path selected
```

Use a new destination on every invocation. Inspect JSON on standard output;
the tool retains all experiment directories for subsequent review. Invalid
sparse selections are rejected before an experiment directory is created.

The public Git manuals were opened successfully on 2026-10-20:

- [git-clone, options `--no-hardlinks` and `--depth`](https://git-scm.com/docs/git-clone).
- [git-worktree, shared repository and administrative files](https://git-scm.com/docs/git-worktree).
- [git-sparse-checkout, cone-mode directory handling](https://git-scm.com/docs/git-sparse-checkout).

These sources establish the Git methods; the fixture establishes expected byte
counts. No standards-derived engineering equation or coefficient is used.
Production full, shallow and sparse clone comparisons remain NOT_EVALUATED.
Live installation requires review and disposable integration checks from
`scripts/operations/job-queue-windows/INSTALL.md`.

## Path Limit

The runner checks the candidate worktree root, generated job folder name, and longest tracked path before creating a worktree. A candidate path at or above 260 characters is refused with a clear message. The test suite includes a stand-in over-limit path and a stand-in path that remains below the limit.
