# 2026-06-10 Freshness Audit Lessons

## Context
Scheduled tier-1 indexing freshness audit for `/mnt/local-analysis/workspace-hub` covering `workspace-hub`, `digitalmodel`, `assetutilities`, and `aceengineer-website`.

## Durable lessons

### Do not trust the existing latest report when it is stale
The local `docs/reports/tier-1-indexing-freshness-latest.md` can lag behind the live baseline. On 2026-06-10 it still showed a 2026-06-01 timestamp and stale all-red/missing-surface evidence even though later reference files existed. In scheduled freshness mode, read it for context, but regenerate from live canonical surfaces before preserving any status or broken-link counts.

### Current 2026-06-10 status-level baseline
Preserve this baseline unless live evidence changes:
- `workspace-hub`: red — missing `docs/maps/workspace-hub-operator-map.md`, missing `docs/registry/module-routing.yaml`, active broken `.agent-os/product/*` links in `docs/README.md:300-303`, and root/source cache/runtime noise.
- `digitalmodel`: red — required canonical surfaces present in sibling checkout, but `README.md:73 -> specs/data-needs.yaml` is broken and trusted `src/` cache noise remains.
- `assetutilities`: yellow — required canonical surfaces present, no confirmed broken canonical-surface links, but trusted `src/` cache noise remains.
- `aceengineer-website`: red — missing `docs/registry/module-routing.yaml`; test cache noise remains; no confirmed broken canonical-surface links.

### Scan machine-readable registries separately from Markdown links
For repos with `docs/registry/module-routing.yaml`, scan path-like registry values independently from Markdown links and filter wildcard/example tokens. On 2026-06-10, both `digitalmodel` and `assetutilities` registries had no confirmed broken literal path references after filtering.

### State scorecard assumption drift precisely
For the 2026-04-22 tier-1 indexing scorecard, distinguish portfolio-level assumptions from repo-specific details:
- Portfolio-level assumption still holds when the overall tier-1 portfolio remains partial/red.
- Repo-specific details may need revision when missing surfaces have since been added.
- Do not keep reporting `assetutilities` as red if live evidence only supports trusted-path noise with all required canonical surfaces present; report yellow.

### Final verification shape
For cron delivery, include only concise evidence: artifact path, report timestamp, size, SHA256, pathspec-limited git status for the report, no-new-cron confirmation, per-repo statuses, and 2026-04-22 assumption verdict. Avoid duplicating the full report body.
