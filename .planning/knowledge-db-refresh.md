# Knowledge DB Refresh — Stale Entry Cleanup

**Date:** 2026-03-25
**DB:** `/mnt/ace/.ace-knowledge/index.db` (1.2 GB)
**Backup:** `/mnt/ace/.ace-knowledge/index.db.bak`
**Script:** `.planning/scripts/knowledge-db-cleanup.py`

## Summary

| Metric | Count |
|---|---|
| Total records | 1,188,891 |
| Valid (active) | 1,160,637 |
| Stale (removed) | 28,254 |
| Symlinks | 0 |
| Dangling symlinks | 0 |
| **Stale %** | **2.4%** |

Scan completed in 33.8s (~40k rows/s).

## Schema Changes

Two columns added to `assets`:
- `status TEXT DEFAULT 'active'` — values: `active`, `removed`, `symlink`
- `canonical_path TEXT` — resolved path for symlinks (unused this run)

## Stale Entries Breakdown

| Folder | Stale Count |
|---|---|
| `/mnt/ace/0000 O&G/` | 27,343 |
| `/mnt/ace/_ss_repo/` | 911 |

All 28,254 stale entries are files that no longer exist on disk, likely removed during the dedup cleanup passes.

## Orphaned Related Records

| Table | Orphaned Rows |
|---|---|
| `standards` | 27,335 |
| `formulas` | 0 |
| `code_patterns` | 0 |
| `cross_references` | 0 |
| `asset_tags` | 0 |

## Next Steps

1. **Purge stale rows** (optional) — `DELETE FROM assets WHERE status='removed'` and cascade to `standards` table. This would reclaim ~2.4% of DB space.
2. **VACUUM** — after purge, run `VACUUM` to compact the DB file.
3. **Re-index FTS** — rebuild `assets_fts` to exclude removed entries:
   ```sql
   INSERT INTO assets_fts(assets_fts) VALUES('rebuild');
   ```
4. **Periodic health check** — re-run the script after future file reorganizations.
