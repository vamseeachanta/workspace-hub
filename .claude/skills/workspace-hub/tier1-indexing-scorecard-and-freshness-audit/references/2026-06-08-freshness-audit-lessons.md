# 2026-06-08 Freshness Audit Lessons

## Context
Scheduled tier-1 indexing freshness audit for `/mnt/local-analysis/workspace-hub` covering `workspace-hub`, `digitalmodel`, `assetutilities`, and `aceengineer-website`.

## Durable lessons

### Correct stale generated latest reports with sibling fallback evidence
The stable latest report can regress if a generator scans only nested paths under `/mnt/local-analysis/workspace-hub/<repo>` and misses sibling fallback checkouts. On this run, the existing report from 2026-06-07 marked `digitalmodel`, `assetutilities`, and `aceengineer-website` as missing all canonical surfaces. The correct action was to rewrite the latest report using sibling fallback paths under `/mnt/local-analysis/<repo>`, explicitly calling out the stale generated-report correction.

### Preserve status-level baseline while updating exact evidence
Status-level baseline remained unchanged:
- `workspace-hub`: red — missing repo-local operator map and module-routing registry; active broken `.agent-os/product/*` links in `docs/README.md`; root/index/runtime noise.
- `digitalmodel`: red — required canonical surfaces present in sibling checkout, but active broken `README.md:73 -> specs/data-needs.yaml`; trusted-path cache noise.
- `assetutilities`: yellow — required surfaces present, no confirmed broken canonical-surface links; trusted-path Python cache noise remains.
- `aceengineer-website`: red — missing `docs/registry/module-routing.yaml`; test cache noise.

### Re-check old scorecard assumptions, do not blindly repeat them
The 2026-04-22 scorecard remains valid at portfolio level (partial readiness only), but repo-specific assumptions should be revised when current evidence shows stronger surfaces. Current revisions observed:
- `digitalmodel` now has `docs/README.md`, repo-local operator map, and `docs/registry/module-routing.yaml`.
- `assetutilities` now has the full canonical surface set and no confirmed broken canonical-surface links; current status is yellow, not red.
- `assetutilities` backup artifact evidence from 2026-04-22 was stale for this checkout: no `*.bak` or `*.orig` files were found under `src`.
- `aceengineer-website` now has `docs/README.md` and a repo-local operator map; registry remains missing.

### Cron closeout evidence shape
Final cron response should stay concise: refreshed artifact path, timestamp, file size, SHA256, git status, no-new-cron confirmation, per-repo statuses, and 2026-04-22 assumption verdict. Do not duplicate the full report body.
