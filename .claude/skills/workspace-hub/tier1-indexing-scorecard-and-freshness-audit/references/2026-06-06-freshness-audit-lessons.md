# 2026-06-06 Freshness Audit Lessons

## Context
Scheduled tier-1 indexing freshness audit for `/mnt/local-analysis/workspace-hub` covering `workspace-hub`, `digitalmodel`, `assetutilities`, and `aceengineer-website`.

## Durable lessons

### Sibling fallback can correct stale generator reports
The requested workspace tree may not contain nested checkouts for all tier-1 repos. On this run, `/mnt/local-analysis/workspace-hub/{digitalmodel,assetutilities,aceengineer-website}` were absent, while sibling checkouts under `/mnt/local-analysis/<repo>` existed and contained canonical routing surfaces. A stale generated latest report had marked those repos as missing all surfaces. The correct behavior was to use sibling fallback, explicitly state that fallback was used, and rewrite the latest report rather than preserving stale missing-surface claims.

### Preserve status-level baseline while correcting evidence
Status-level baseline remained unchanged:
- `workspace-hub`: red — missing repo-local operator map and module-routing registry; active broken `.agent-os/product/*` links in `docs/README.md`; root/index/runtime noise.
- `digitalmodel`: red — required surfaces present in sibling checkout, but active broken `README.md:73 -> specs/data-needs.yaml`; source/docs cache noise.
- `assetutilities`: yellow — required surfaces present and inspected canonical links clean; trusted-path Python cache noise remains.
- `aceengineer-website`: red — missing `docs/registry/module-routing.yaml`; test/script cache noise.

### Report should call out stale generated-report correction
When the stable latest report contains generated stale content, explicitly say it was corrected. On this run, the report included a note that prior claims of missing all canonical surfaces for `digitalmodel`, `assetutilities`, and `aceengineer-website` were stale because sibling fallback checkouts contained the surfaces.

### Final cron closeout evidence shape
Concise final response should include: refreshed artifact path, timestamp, file size, SHA256, git status for the report, no-new-cron confirmation, per-repo statuses, and the 2026-04-22 assumption verdict. Do not duplicate the entire report body in cron delivery.
