# Job Queue Worktree Footprint Measurement Plan

## Summary

This plan defines measurements for comparing shared-clone worktrees with separate clones. No storage measurements have been established. Any storage comparison remains conditional until the table is populated. The versioned queue scripts are integration examples; live integration must preserve job execution and concurrency controls.

## Revision History

| Revision | Date | What Changed | Why |
|---|---:|---|---|
| 0 | 2026-10-14 | Initial footprint note for the versioned queue scripts. | The queue needed a reviewed path to reduce accumulated worktree storage. |
| 1 | 2026-10-15 | Recast as a measurement plan and correct integration claims. | Storage measurements and live installation remain unestablished. |

## Source Basis

| Item | Result |
|---|---|
| Script source of truth | The pump, runner, launchers, and limits file were live local queue files and were not versioned in this repository before this change. |
| Live digests | Installation records digests before changing live files. No live-file digest is established here. |
| Live mutation | The live files were read only; installation is not performed by this change. |

## Footprint

The measurement route is documented for the reviewer because the live queue and private repository names are not public text. The worktree size is measured with list-only folder traversal. Shared object stores are measured with `git count-objects -vH`. Scratch clone experiments are retained until the maintainers authorize their disposition.

| Repository Class | Worktree Size | Per-Worktree Metadata | Shared Object Store | Worktree Count | Basis |
|---|---:|---:|---:|---:|---|
| Public operations repository | Not established in this run | Not established in this run | Not established in this run | Not established in this run | Live measurement was not completed before implementation verification. |
| Restricted knowledge repositories | Not established in this run | Not established in this run | Not established in this run | Not established in this run | Public reporting aggregates this class and omits repository names. |
| Scratch fresh full clone | Not established in this run | n/a | Not established in this run | n/a | Network clone experiments are not required for installation. |
| Scratch shallow clone | Not established in this run | n/a | Not established in this run | n/a | Shallow history can break tests and base-moved checks that need history. |
| Scratch partial clone | Not established in this run | n/a | Not established in this run | n/a | Missing blobs can defer network access into tests or hooks. |
| Scratch sparse checkout | Not established in this run | n/a | Not established in this run | n/a | Sparse paths can omit hooks, tests, or files a job later needs. |

The answer to the maintainer's storage question is therefore conditional on the measured rows. A worktree of the shared clone is expected to use the least per-job object storage because it reuses the shared object store; a fresh clone is expected to consume more space but isolates object maintenance. The proposed integration would keep shared-clone worktrees and remove eligible finished worktrees after successful publication and slot release. These examples do not establish that this integration has been installed.

## Path Limit

The runner checks the candidate worktree root, generated job folder name, and longest tracked path before creating a worktree. A candidate path at or above 260 characters is refused with a clear message. The test suite includes a stand-in over-limit path and a stand-in path that remains below the limit.
