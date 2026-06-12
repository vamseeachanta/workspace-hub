# 2026-06-02 Freshness Audit Lessons

## Context
Scheduled tier-1 indexing freshness audit for `/mnt/local-analysis/workspace-hub` covering `workspace-hub`, `digitalmodel`, `assetutilities`, and `aceengineer-website`.

## Durable lessons

### Compaction-resume verification
When a cron freshness audit is compacted after the latest report was already written, do not rerun the full scan by default. First read back `docs/reports/tier-1-indexing-freshness-latest.md` and verify it is current, coherent, and internally consistent. Then gather final `stat`, `sha256sum`, and targeted `git status --short <report>` evidence for delivery.

### Sibling checkout fallback changes status evidence
For `/mnt/local-analysis/workspace-hub`, nested tier-1 checkouts may be absent. Use sibling paths (`/mnt/local-analysis/digitalmodel`, `/mnt/local-analysis/assetutilities`, `/mnt/local-analysis/aceengineer-website`) as fallback before concluding canonical surfaces are missing. This can correct stale all-red reports caused by scanning only under the workspace-hub checkout.

### Active broken link can make an otherwise complete repo red
A repo with all required canonical surfaces present can still fail freshness if an inspected canonical surface contains an active broken routing/reference link. On 2026-06-02, `digitalmodel` had `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/digitalmodel-operator-map.md`, and `docs/registry/module-routing.yaml`, with registry paths validating, but was red because `README.md:73` linked to missing `specs/data-needs.yaml`.

### Final delivery shape
For cron delivery, summarize artifact path, portfolio status, per-repo statuses, material drift, and exact verification evidence. Do not duplicate the full report body if the report itself was refreshed and verified.

## 2026-06-02 status baseline
- `workspace-hub`: red — missing repo-local operator map and registry; active broken legacy `.agent-os` links in `docs/README.md`; cache/runtime noise.
- `digitalmodel`: red — all required canonical surfaces present and registry validates, but active broken `README.md:73 -> specs/data-needs.yaml`; cache/runtime noise.
- `assetutilities`: yellow — required surfaces present and registry validates; remaining issue is source-path cache noise.
- `aceengineer-website`: red — missing `docs/registry/module-routing.yaml`; test-path cache noise.

## Verification evidence pattern
After all report writes/patches are complete, run:

```bash
stat -c '%n %s bytes %y' docs/reports/tier-1-indexing-freshness-latest.md
sha256sum docs/reports/tier-1-indexing-freshness-latest.md
git status --short docs/reports/tier-1-indexing-freshness-latest.md
```

Keep exact values in the final cron response rather than embedding them in the report before final edits.
