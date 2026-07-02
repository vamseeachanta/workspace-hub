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
