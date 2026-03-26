# Provenance Layer Integration -- Completion Summary

**Date:** 2026-03-26
**Status:** Complete

## What was done

Ran the provenance migration on the production document index using `provenance.py`'s
streaming merge mode (`merge_provenance_streaming`).

## Test results

All 23 unit tests passed (pytest, Python 3.11.14):
- 16 tests for `merge_provenance` (in-memory API)
- 4 tests for `merge_provenance_streaming` (file-based)
- 3 tests for `apply_provenance_to_pipeline` (integration hook)

## Migration stats

| Metric | Value |
|---|---|
| Input file | `data/document-index/index.jsonl` |
| Output file | `data/document-index/index-merged.jsonl` |
| Input records | 1,049,644 |
| Output records | 635,058 |
| Records eliminated | 414,586 (39.5%) |
| Unique content hashes | 151,573 |
| Hash groups with duplicates | 93,221 |
| Records without content hash | 483,485 (CAD, API metadata, etc.) |
| Records with provenance array | 635,058 (100% of output) |
| Records with multi-source provenance | 93,221 |
| Max provenance entries on one record | 796 |
| Input file size | 600 MB |
| Output file size | 661 MB |

Output file is larger despite fewer records because each record now carries a
`provenance` array with source/path/host/discovered metadata for every location
where the document was found.

## Integration status

- `phase-a-index.py` already imports `apply_provenance_to_pipeline` from `provenance.py`
  and uses it in the main pipeline (replaces legacy `deduplicate_records`)
- The standalone CLI (`python provenance.py <index> [--output] [--dry-run]`) works
  for batch migration of existing index files
- The merged output preserves all enrichment fields (domain, status, target_repos,
  readability, path_category, remapped_by, etc.) by merging from secondary records

## Next steps

- Replace `index.jsonl` with `index-merged.jsonl` when ready to cut over
- Downstream consumers that key by `path` need to switch to `content_hash` keying
- Consider pruning the record with 796 provenance entries (likely a common template file)
