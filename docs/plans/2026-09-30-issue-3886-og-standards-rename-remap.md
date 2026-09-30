# Plan for #3886: og-standards — add rename/remap mode

> **Status:** draft
> **Complexity:** T2
> **Date:** 2026-09-30
> **Issue:** https://github.com/vamseeachanta/workspace-hub/issues/3886
> **Client:** N/A
> **Lane:** lane:claude
> **Review artifacts:** scripts/review/results/2026-09-30-plan-3886-claude.md

---

## Resource Intelligence Summary

### Existing repo code

- EXISTS: `scripts/data/og-standards/inventory.py` (399 lines) — `INSERT OR IGNORE INTO documents` at line 263 prevents any update to `target_path` on rename; `argparse` at lines 364–378 defines only `--config` and `--force` (no `--scan-only`); schema defines `target_path TEXT` at line 82 and `content_hash TEXT` at line 74.
- EXISTS: `scripts/data/og-standards/catalog.py` (695 lines) — `INSERT OR REPLACE INTO documents_fts` at line 77 re-inserts FTS rows without clearing stale entries first; the `CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts` at line 66 is not rebuilt on update.
- EXISTS: `scripts/data/og-standards/og-ingest` (bash CLI) — `scan` subcommand calls `python inventory.py --scan-only` at line 101; `inventory.py` has no such argument, so this call fails with argparse error.
- EXISTS: `scripts/data/og-standards/config.yaml` — `source_directories` points to `/mnt/ace/0000 O&G/...` paths that no longer hold the content (content moved to `raw/` per issue body).
- EXISTS: `data/document-index/standards-transfer-ledger.yaml` — 436 standards entries; uses `doc_path` field; downstream paths would contain stale renames.
- MISSING (new — this plan creates): `scripts/data/og-standards/rename.py` — rename/remap mode

### Standards

Not applicable — this is a data pipeline issue.

### LLM Wiki pages consulted

No relevant wiki pages — og-standards is a local library pipeline, not a standards-transfer wiki topic.

### Documents consulted

- Issue body [#3886](https://github.com/vamseeachanta/workspace-hub/issues/3886) — describes four-item fix: rename mode, config drift fix, real SHA-256, document-index refresh.
- `docs/plans/2026-04-24-issue-2487-inventory-readiness-spine.md` — prior inventory readiness plan; covers `target_path` schema and content pipeline ordering; no rename mode was planned.
- `data/document-index/standards-transfer-ledger.yaml` — downstream ledger with `doc_path` fields; confirms stale paths would propagate to 436 entries.
- `scripts/data/og-standards/og-ingest:101` — `python inventory.py --scan-only` call; confirmed `inventory.py` does not accept `--scan-only` (argparse at lines 364–378).

### Gaps identified

- No rename/remap mode exists anywhere in `scripts/data/og-standards/`.
- No `sha256` column exists in the `documents` table (only `content_hash` which is a different digest per issue body).
- `og-ingest scan` is currently broken (passes unknown `--scan-only` flag to `inventory.py`).
- Source roots in `config.yaml` are stale and will cause `--force` rebuild to fail immediately.

### Evidence (embedded verification)

**Issue status** (verified 2026-09-30 via `gh issue view`):
- `#3886` — OPEN — og-standards: add a rename/remap mode — renamed library files leave stale catalog, inventory DB and document-index paths

**File existence** (`ls` 2026-09-30):
- EXISTS: `scripts/data/og-standards/inventory.py`
- EXISTS: `scripts/data/og-standards/catalog.py`
- EXISTS: `scripts/data/og-standards/og-ingest`
- EXISTS: `scripts/data/og-standards/config.yaml`
- EXISTS: `data/document-index/standards-transfer-ledger.yaml`
- MISSING (new): `scripts/data/og-standards/rename.py`

**Line excerpts** (`sed -n` from live checkout):
```
inventory.py:263    INSERT OR IGNORE INTO documents
inventory.py:74     content_hash TEXT,
inventory.py:82     target_path TEXT,
inventory.py:364–378  argparse: only --config and --force defined
og-ingest:101       python inventory.py --scan-only  ← fails (no such argument)
config.yaml:6-8     source_directories: /mnt/ace/0000 O&G/...  ← stale paths
catalog.py:77       INSERT OR REPLACE INTO documents_fts(rowid, ...) ← no prior clear
```

**Gap proofs**:
```
grep -n "scan.only\|scan_only" scripts/data/og-standards/inventory.py
(no output) → confirms --scan-only is not implemented
```

**Reproduction proofs**:
N/A — this is a data pipeline gap (no automated test exists to run). Verified by code inspection that `INSERT OR IGNORE` at line 263 would silently skip a re-inserted renamed document, leaving the stale `target_path` in place. The argparse gap at lines 364–378 is a direct read of the source.

---

## Artifact Map

```
scripts/data/og-standards/
  rename.py          NEW — rename/remap mode; reads RENAME-LOG.md; updates DB; triggers FTS rebuild
  inventory.py       EDIT — add sha256 column migration; fix argparse to accept --scan-only
  og-ingest          EDIT — fix scan subcommand to not pass --scan-only to inventory.py
  config.yaml        EDIT — repoint source_directories to raw/ paths
  tests/
    test_rename.py   NEW — TDD test suite (see TDD Test List)
```

---

## Deliverable

A `rename.py` script that reads a RENAME-LOG.md (old_path → new_path + sha256), updates `target_path` in the inventory DB by row id, rebuilds the FTS5 index (`INSERT INTO documents_fts(documents_fts) VALUES('rebuild')`), and runs `catalog.py` to regenerate the catalog. Supports `--dry-run`. Fixed `og-ingest scan` subcommand (remove broken `--scan-only` passthrough). Fixed `config.yaml` source roots. Added `sha256` column migration in `inventory.py`.

---

## Pseudocode

```python
# rename.py — rename/remap mode

def parse_rename_log(path: str) -> list[RenameEntry]:
    # reads RENAME-LOG.md lines: "old_path | new_path | sha256"
    # validates: old_path in DB, sha256 matches file at new_path
    # returns list[RenameEntry(row_id, old_path, new_path, sha256)]

def apply_renames(db_path: str, entries: list[RenameEntry], dry_run: bool):
    with sqlite3.connect(db_path) as conn:
        for entry in entries:
            if not dry_run:
                conn.execute(
                    "UPDATE documents SET target_path=?, sha256=? WHERE id=?",
                    (entry.new_path, entry.sha256, entry.row_id)
                )
        # Rebuild FTS5 after all renames
        if not dry_run:
            conn.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild')")

def main():
    args = parse_args()  # --rename-log, --db, --dry-run, --run-catalog
    entries = parse_rename_log(args.rename_log)
    report_plan(entries)  # always print what would change
    if not args.dry_run:
        apply_renames(args.db, entries)
        if args.run_catalog:
            subprocess.run(["python", "catalog.py", "--config", args.config], check=True)
```

---

## Files to Change

| File | Action | Scope |
|------|--------|-------|
| `scripts/data/og-standards/rename.py` | CREATE | ~120 lines |
| `scripts/data/og-standards/tests/test_rename.py` | CREATE | ~80 lines |
| `scripts/data/og-standards/inventory.py` | EDIT | Add `sha256 TEXT` column + migration; remove `--scan-only` from `run_full_scan` path; add `--scan-only` to argparser (or remove the call from og-ingest) |
| `scripts/data/og-standards/og-ingest` | EDIT | `scan` subcommand: remove `--scan-only` passthrough; call `inventory.run_full_scan()` directly or remove the flag |
| `scripts/data/og-standards/config.yaml` | EDIT | Repoint `source_directories` to `raw/` equivalent; document the change |

---

## TDD Test List (red → green)

All tests in `scripts/data/og-standards/tests/test_rename.py` using `pytest` + `tmp_path`:

1. `test_parse_rename_log_valid` — parses a 3-column log with two entries; returns two `RenameEntry` objects with correct fields.
2. `test_parse_rename_log_missing_sha` — log line missing sha256 raises `ValueError`.
3. `test_apply_renames_updates_target_path` — in-memory SQLite DB with one document; after apply, `target_path` matches new path.
4. `test_apply_renames_dry_run_no_mutation` — dry run: `target_path` unchanged in DB.
5. `test_apply_renames_fts_rebuild_called` — after renames, `documents_fts` can be queried with new filename (proves rebuild ran).
6. `test_rename_old_path_not_in_db_raises` — entry whose old_path has no matching DB row raises `ValueError` (not silent skip).
7. `test_sha256_mismatch_raises` — entry where sha256 does not match file at new_path raises `ValueError`.
8. `test_og_ingest_scan_no_scan_only_arg` — subprocess call to `og-ingest scan` on a minimal fixture does not propagate `--scan-only` to `inventory.py` (argparse no longer errors).
9. `test_inventory_sha256_column_exists` — after running inventory on a fresh DB, `PRAGMA table_info(documents)` includes `sha256`.

---

## Acceptance Criteria

- `rename.py --dry-run --rename-log RENAME-LOG.md` prints a tabular plan of all renames with old path, new path, sha256 — and makes zero DB mutations.
- `rename.py --rename-log RENAME-LOG.md` updates `target_path` in the DB for each entry, rebuilds FTS5 without error, and runs `catalog.py` if `--run-catalog` is passed.
- `og-ingest scan` no longer passes `--scan-only` to `inventory.py`; the command completes without argparse error on a valid config.
- `inventory.py` creates a `sha256 TEXT` column in the `documents` schema on new DB; existing DBs are migrated by `ALTER TABLE ADD COLUMN IF NOT EXISTS` (or equivalent safe migration).
- All 9 named tests pass with `pytest scripts/data/og-standards/tests/test_rename.py`.
- No regression in existing `og-ingest` subcommand paths (`add`, `process`, `status`).

---

## Risks and Open Questions

- **RENAME-LOG.md format**: issue body refers to "a rename log" but format is assumed. Implementer must verify against the actual file at the library root (`/mnt/ace/O&G-Standards/RENAME-LOG.md`) before coding the parser. If the format differs, adjust `parse_rename_log()`.
- **FTS5 `rebuild` availability**: `INSERT INTO documents_fts(documents_fts) VALUES('rebuild')` requires SQLite ≥ 3.8.3. Verify `sqlite3.sqlite_version` at test time.
- **`--scan-only` in og-ingest**: the simplest fix is to remove the flag from the `og-ingest scan` call entirely. If other callers depend on the `--scan-only` semantics (scan without extracting), add a proper `--scan-only` arg to `inventory.py`'s argparser. Implementer to grep for other callers first.
- **config.yaml `raw/` path**: issue body states content moved to `raw/` but does not give the absolute path. The implementer must resolve the correct `raw/` root before changing `config.yaml`.
- **Out of scope**: re-embedding text chunks, document-index ledger refresh chain beyond `catalog.py`, SHA-256-based dedup of new documents.
