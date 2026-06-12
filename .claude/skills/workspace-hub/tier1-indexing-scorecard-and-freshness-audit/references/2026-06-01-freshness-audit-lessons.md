# 2026-06-01 Freshness Audit Lessons

## Session pattern

A scheduled freshness audit for `/mnt/local-analysis/workspace-hub` refreshed:

- `docs/reports/tier-1-indexing-freshness-latest.md`

The run was interrupted by context compaction after the report had already been written and verified. The correct recovery pattern was to read back the existing report tail and use the final `stat`/`sha256sum`/`git status` evidence already available, rather than restarting the audit or rewriting the report.

## Durable lessons

- In scheduled cron mode, if context compaction occurs after `write_file`, first verify the on-disk latest report before taking further action. Do not re-run the full scan unless the report is missing, stale, or internally inconsistent.
- Final cron delivery can be a concise artifact/evidence/status summary. It does not need to duplicate the full report body when the local report was refreshed and verified.
- Keep exact verification values (`stat`, checksum, git status) in the final cron response after all edits are complete. Avoid embedding values that may become stale inside the report itself.
- If the latest report corrects stale previous-report evidence, explicitly say what was corrected. In this run, stale all-red sibling-checkout evidence was corrected by using sibling fallbacks under `/mnt/local-analysis/<repo>` where nested checkouts were absent.

## Evidence shape from this run

- Refreshed report path: `/mnt/local-analysis/workspace-hub/docs/reports/tier-1-indexing-freshness-latest.md`
- Portfolio status remained red overall.
- Repo statuses: `workspace-hub=red`, `digitalmodel=yellow`, `assetutilities=yellow`, `aceengineer-website=red`.
- 2026-04-22 top-level scorecard assumption still held, but repo-specific assumptions needed revision because several canonical surfaces had since appeared.
