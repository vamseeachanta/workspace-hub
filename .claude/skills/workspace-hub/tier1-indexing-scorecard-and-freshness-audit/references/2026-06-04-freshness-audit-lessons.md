# 2026-06-04 Freshness Audit Lessons

## Context
Scheduled tier-1 indexing freshness audit for `/mnt/local-analysis/workspace-hub` covering `workspace-hub`, `digitalmodel`, `assetutilities`, and `aceengineer-website`.

## Durable lessons

### Rewrite stale generated `latest` reports, do not patch around them
The existing `docs/reports/tier-1-indexing-freshness-latest.md` can be internally stale because older generators may:
- mark sibling fallback repos as missing when nested paths are absent;
- preserve outdated issue/tracking boilerplate;
- assign repo statuses from missing-surface evidence that is no longer valid.

In scheduled freshness mode, if the existing latest report conflicts with live evidence, rewrite the report into the current canonical format rather than trying to minimally patch stale sections. Explicitly call out the correction so future readers know the prior status was stale.

### Sibling fallback path is status-critical
When `/mnt/local-analysis/workspace-hub/<repo>` is absent for `digitalmodel`, `assetutilities`, or `aceengineer-website`, inspect `/mnt/local-analysis/<repo>` before assigning missing-surface findings. Missing nested checkout alone is not a repo routing failure.

### Noise findings should be categorical in the report
Runtime/cache noise scans can produce very large evidence sets, especially in `workspace-hub` root paths and Python package trees. Include representative categories and paths in the report (`__pycache__`, `*.pyc`, `.coverage`, logs, uv/cache state), not a huge raw list. Keep exact raw scanner output out of the user-facing freshness report unless the task asks for a full inventory.

### Current status baseline remained unchanged
On 2026-06-04 the status-level baseline remained:
- `workspace-hub`: red — missing repo-local operator map and registry; active broken legacy `.agent-os` links in `docs/README.md`; root/index/runtime noise.
- `digitalmodel`: red — required canonical surfaces present, but active broken `README.md:73 -> specs/data-needs.yaml`; source/docs cache noise.
- `assetutilities`: yellow — required canonical surfaces present and inspected links clean; trusted-path Python cache/package noise remains.
- `aceengineer-website`: red — missing `docs/registry/module-routing.yaml`; test/script cache noise.

### Final delivery evidence
After writing the report, verify with final `stat`, `sha256sum`, and `git status --short <report>`. Put exact verification values in the cron final response, not in the report before hashing.
