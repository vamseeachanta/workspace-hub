# 2026-05-21 Freshness Audit Lessons

## Context
Scheduled tier-1 indexing freshness audit for `/mnt/local-analysis/workspace-hub` covering:
- `workspace-hub`
- `digitalmodel`
- `assetutilities`
- `aceengineer-website`

The cron run was resumed after context compaction; the report had already been generated and patched, so the remaining work was final verification and user-facing closeout.

## Durable workflow lessons

1. **Resume from the last verified checkpoint after compaction.**
   When a handoff says the report was already generated/patched, do not rerun the full scan unless evidence is stale or inconsistent. First complete the pending verification: `git status --short`, `stat`, and `sha256sum` for the refreshed report artifacts.

2. **Verify dated and latest report artifacts are byte-identical after all edits.**
   The safe closeout pattern is:
   - patch `docs/reports/tier-1-indexing-freshness-latest.md`
   - copy/sync it to `docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md`
   - run `sha256sum` on both files
   - report the final hash only after no more edits are pending

3. **Keep status-level drift distinct from evidence refresh.**
   For 2026-05-21, the corrected status-level baseline remained unchanged:
   - `workspace-hub`: RED
   - `digitalmodel`: YELLOW
   - `assetutilities`: YELLOW
   - `aceengineer-website`: RED
   - portfolio: RED

   The right wording was: “no material drift detected at the status level.” The report still included refreshed evidence and corrected stale all-red framing from older generated reports.

4. **Treat the 2026-04-22 scorecard as historical attestation, not routing authority.**
   Current canonical authority remains the standards/contract files and live repo surfaces. The old scorecard assumptions need revision where live sibling checkouts now show complete required surfaces for `digitalmodel` and `assetutilities`.

5. **Call out generator path drift without patching it in freshness-only mode.**
   The daily report generator script still assumed nested tier-1 repo paths under `/mnt/local-analysis/workspace-hub/<repo>`, while current checkouts were siblings under `/mnt/local-analysis/<repo>`. In a freshness-only cron task, note this as a next action rather than patching code without TDD/approval.

## Final verification evidence pattern

Example final verification output shape:

```text
M docs/reports/tier-1-indexing-freshness-latest.md
?? docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md
path=docs/reports/tier-1-indexing-freshness-latest.md size=<bytes> mtime=<timestamp>
path=docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md size=<bytes> mtime=<timestamp>
<same-sha256>  docs/reports/tier-1-indexing-freshness-latest.md
<same-sha256>  docs/reports/tier-1-indexing-freshness-YYYY-MM-DD.md
```

Do not claim the dated/latest artifacts match unless the hashes are identical after final edits.

## 2026-05-21 evidence snapshot

- `workspace-hub`: RED — missing `docs/maps/workspace-hub-operator-map.md`, missing `docs/registry/module-routing.yaml`, legacy `.agent-os` links in `docs/README.md`, trusted-path noise.
- `digitalmodel`: YELLOW — required surfaces present; stale active refs remained (`README.md:73 -> specs/data-needs.yaml`; `docs/maps/digitalmodel-operator-map.md:9 -> docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`); trusted-path noise.
- `assetutilities`: YELLOW — required surfaces present; trusted-path runtime/cache/log/report noise only.
- `aceengineer-website`: RED — missing `docs/registry/module-routing.yaml`; minor trusted-path noise.
