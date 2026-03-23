---
name: work-queue-machine-wrk-id-ranges
description: 'Sub-skill of work-queue: Machine WRK ID Ranges.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Machine WRK ID Ranges

> **DEPRECATED (WRK-5097, 2026-03-23):** Machine-partitioned ranges are no longer
> the primary ID allocation mechanism. New WRK IDs are derived from GitHub issue
> numbers via `scripts/work-queue/gh-next-id.sh`. This eliminates cross-machine
> conflicts entirely. The ranges below are retained for legacy reference only.

## Machine WRK ID Ranges (Legacy)

Each machine previously owned a non-overlapping numeric range (canonical: `config/work-queue/machine-ranges.yaml`).
`next-id.sh` reads this table and enforces the floor automatically.

| Machine | Floor | Ceiling | Notes |
|---------|-------|---------|-------|
| `dev-primary` | 1 | 4999 | Primary; current IDs ~1128 |
| `licensed-win-1` | 5000 | 9999 | Windows / orcaflex |
| `dev-secondary` | 10000 | 14999 | Reserved |
| `gali-linux-compute-1` | 15000 | 19999 | Reserved |

## New ID Allocation (WRK-5097)

- **Online:** `gh-next-id.sh --title "..."` creates a GitHub issue and returns the number as the WRK ID.
- **Offline:** Falls back to `WRK-LOCAL-YYYYMMDD-HHMMSS-{hostname}`. Promote with `promote-local-ids.sh`.
- **All issues** created in `vamseeachanta/workspace-hub` regardless of `target_repos`.
