# Drive Index Refresh

This directory owns the workspace-hub refresh path for drive-local file indexes.

## Ace Knowledge Provenance

The original `.ace-knowledge` builder is not lost. It lives in the
`aceengineer-admin` repository as the `aceengineer_admin.knowledge` package, with
the Click CLI group `aceengineer-admin knowledge`.

The live design spec is tracked at:

`.planning/archive/modules/ace-knowledge-index-system.md`

That file was originally added as `specs/modules/ace-knowledge-index-system.md`
in commit `963f20cde` and later archived by the R100 rename in `2b1a8d779`.

Workspace-hub does not vendor the extraction/anonymizer package. The refresh
owned here is metadata-only, in-place, and constrained to the `assets` table:
`build_drive_index.py --drive ace --incremental --prune`.

Refreshes must not clobber aceengineer-admin-owned extraction columns such as
`title`, `discipline`, `extraction_status`, `content_hash`, or `last_extracted`.

## Manual refresh

From the repository root, run one configured document index refresh:

```bash
uv run --with pyyaml python scripts/data/drive-index/build_drive_index.py \
  --config scripts/data/drive-index/drive-index-config.yaml \
  --drive <configured-drive> --incremental --prune
```

Select a drive key from the configuration and confirm its roots and database
before running. The scheduled shell entry point accepts the same drive key:
`bash scripts/data/drive-index/refresh-drive-index.sh <configured-drive>`.
The shell entry point also accepts `cad` for the CAD readability index.
`DRIVE_INDEX_CONFIG` selects an external profile file for the wrapper and its
builder. The database and failure-state destination come from that same
profile. This permits a scheduled runner to use corrected local roots without
embedding private paths in the repository. The selected profile must retain
every intended source; a missing root is reported as a coverage failure.
Its scan root defaults to the primary document profile's configured canonical
prefix; `DRIVE_INDEX_CAD_ROOT` overrides that root. CAD output is placed in
`_cad-index` under the selected root. The builder receives `--raw` for the scan
TSV, `--dedup` for the directory containing the optional deletion log and GLB
manifest, and `--out` for the readability TSV.
Success and failure status use the same `refresh-state.json` under the selected
root's `_cad-index` directory; failures do not update another root's state.

## Refresh status and scan errors

`refresh-state.json` beside the document database reports the latest refresh:

- `ok`: the scan completed without errors.
- `partial`: at least one asset row was added or updated, but errors occurred.
  All successfully written rows are committed and searchable.
- `failed`: errors occurred and no asset row was added or updated. An unchanged
  file skipped by an incremental refresh does not count as a written row.

`error_count` gives the total number of scan or row-write errors. `scan_errors`
records each affected path and reason. The same details are appended to
`refresh-errors.jsonl` with the scan timestamp and emitted to standard error.
The JSON state describes the latest run; the log retains earlier errors.
If the diagnostic log cannot be opened or written, successful asset writes are
still committed. The scan error and diagnostic I/O failure are emitted to
standard error. `logging_error_count` and `logging_errors` record diagnostic
failures separately from `error_count` and `scan_errors` in the latest state;
the `error` summary includes both counts. A subsequent complete refresh clears
the latest diagnostic failures.
These local diagnostics contain source paths and require the same access
controls as the database.

Pruning is suppressed for the entire refresh when any error occurs, or when
`--limit` restricts traversal. Previously indexed files in unreadable folders
remain active. Resolve the recorded errors and run a complete refresh to resume
pruning. Existing rows remain available after a failed scan. Scan errors are
reported through the state file and a nonzero metadata-command exit. Successful
rows are committed before exit; the wrapper records a failure notification and
retains the builder's detailed diagnostics. Check `status` before treating a
scan as complete.

## Search migration without rescanning

The FTS index includes title, description, anonymized title, stored asset path
and filename. Path tokens include parent folders and numeric directory names.
Queries use SQLite FTS5 token matching; quote filenames containing punctuation.

Opening an older database through the builder atomically replaces its legacy
FTS table and rebuilds it from stored asset rows. To migrate and rebuild only
search data without traversing source folders, run:

```bash
uv run --with pyyaml python scripts/data/drive-index/build_drive_index.py \
  --config scripts/data/drive-index/drive-index-config.yaml \
  --drive <configured-drive> --rebuild-fts
```

Asset IDs, extracted metadata and other tables are preserved. This command
requires database write access and does not update refresh timestamps. Rebuilding
search data does not establish that the underlying file inventory is current.
