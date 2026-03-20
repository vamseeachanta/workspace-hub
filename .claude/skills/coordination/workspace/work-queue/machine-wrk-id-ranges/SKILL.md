---
name: work-queue-machine-wrk-id-ranges
description: 'Sub-skill of work-queue: Machine WRK ID Ranges.'
version: 1.8.0
category: coordination
type: reference
scripts_exempt: true
---

# Machine WRK ID Ranges

## Machine WRK ID Ranges


Each machine owns a non-overlapping numeric range (canonical: `config/work-queue/machine-ranges.yaml`).
`next-id.sh` reads this table and enforces the floor automatically.

| Machine | Floor | Ceiling | Notes |
|---------|-------|---------|-------|
| `dev-primary` | 1 | 4999 | Primary; current IDs ~1128 |
| `licensed-win-1` | 5000 | 9999 | Windows / orcaflex |
| `dev-secondary` | 10000 | 14999 | Reserved |
| `gali-linux-compute-1` | 15000 | 19999 | Reserved |

Re-allocation: bump floor/ceiling when within 50 of ceiling.

> **ID range confusion warning**: `next-id.sh` scans ALL pending/working files including those from
> other machines. If a WRK-5000+ file exists in `pending/` (created on licensed-win-1), dev-primary
> sessions will see MAX_FILE_ID ≥ 5000 and issue IDs from that range. This is a known limitation.
> **Fix**: when in doubt, check `hostname` and compare issued ID against your machine's floor/ceiling.
> Items created on the wrong range can be renamed; update frontmatter `id:` to match the new filename.
