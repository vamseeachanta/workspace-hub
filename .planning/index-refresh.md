# Index Refresh: Ghost Entry Removal (2026-03-26)

## Context
Post-dedup cleanup moved/deleted files, leaving ghost entries in `index-merged.jsonl` (paths referencing files that no longer exist on disk).

## Audit Results
| Metric | Value |
|---|---|
| Total records (before) | 635,058 |
| Ghost entries removed | 7,647 |
| Live records (after) | 627,411 |
| Ghost rate | 1.2% |
| API metadata (kept) | 8 |

### Ghosts by source
| Source | Count | Root cause |
|---|---|---|
| ace_project | 6,095 | Files moved during O&G-Standards consolidation (old `/mnt/ace/0000 O&G/` paths) |
| riser_eng_job | 1,426 | Riser engineering job cleanup |
| og_standards | 122 | Standards DB references pre-migration paths |
| workspace_spec | 4 | Spec files removed during workspace cleanup |

## Actions Taken
1. Ran `ghost-audit.py` against `index-merged.jsonl` -- validated every `path` field with `os.path.exists()`
2. Wrote `index-clean.jsonl` (627,411 records, ghost-free)
3. Spot-checked first/last 5 records -- all confirmed to exist on disk
4. Backed up originals:
   - `index.jsonl.bak-20260326` (1,049,644 lines, pre-merge raw index)
   - `index-merged.jsonl.bak-20260326` (635,058 lines, merged with ghosts)
5. Replaced both `index.jsonl` and `index-merged.jsonl` with clean version

## Files
- Audit script: `scripts/data/document-index/ghost-audit.py`
- Clean index: `data/document-index/index-clean.jsonl`
- Backups: `data/document-index/index.jsonl.bak-20260326`, `data/document-index/index-merged.jsonl.bak-20260326`

## Next steps
- Re-run `phase-a-index.py --force` when all NFS mounts are verified (will rebuild from scratch, naturally excluding missing files)
- Remove backup files after confirming downstream consumers work with clean index
