# 2026-05-25 Freshness Audit Lessons

## Context
Scheduled tier-1 indexing freshness audit for `/mnt/local-analysis/workspace-hub` covering:
- `workspace-hub`
- `digitalmodel`
- `assetutilities`
- `aceengineer-website`

The live scan found the stable latest report still carried stale generator output that treated `digitalmodel` and `assetutilities` as RED/missing all surfaces, while live sibling checkouts showed both had the required canonical surfaces.

## Durable lessons

1. **Treat the existing latest report as suspect input, not authority.**
   If `docs/reports/tier-1-indexing-freshness-latest.md` is stale/all-red, rewrite it from live evidence instead of preserving or lightly patching stale counts.

2. **Call out report-content drift separately from repo-status drift.**
   The correct wording for this run was: no material drift at the status level, but the previous latest report content was stale and corrected. This avoids both false alarm and false silence.

3. **Sibling fallback remains necessary.**
   For `/mnt/local-analysis/workspace-hub`, `digitalmodel`, `assetutilities`, and `aceengineer-website` may be sibling checkouts under `/mnt/local-analysis/<repo>` rather than nested under `/mnt/local-analysis/workspace-hub/<repo>`. Use sibling fallback for evidence, and mention it in the report.

4. **Current status-level baseline remained unchanged.**
   - `workspace-hub`: RED — missing repo-local operator map and module-routing registry; stale active links in `docs/README.md`.
   - `digitalmodel`: YELLOW — required surfaces present; `README.md:73 -> specs/data-needs.yaml` broken; operator-map historical slice reference still repo-local ambiguous.
   - `assetutilities`: YELLOW — required surfaces present; cache/runtime noise only.
   - `aceengineer-website`: RED — missing `docs/registry/module-routing.yaml`.

5. **Verification can be latest-only unless the task explicitly asks for a dated copy.**
   The user-requested artifact was `docs/reports/tier-1-indexing-freshness-latest.md`; dated copies are useful but not mandatory for this scheduled task unless explicitly requested or already part of the run contract.

## Evidence snapshot

- `workspace-hub` present surfaces: `AGENTS.md`, `README.md`, `docs/README.md`; missing `docs/maps/workspace-hub-operator-map.md`, `docs/registry/module-routing.yaml`.
- `workspace-hub/docs/README.md` active stale/broken references: lines 300-303 to retired product-doc paths; line 264 stale legacy configuration mention.
- `digitalmodel` present surfaces: all required canonical surfaces; broken `README.md:73 -> specs/data-needs.yaml`.
- `digitalmodel/docs/maps/digitalmodel-operator-map.md:9` references `docs/maps/digitalmodel-orcawave-orcaflex-operator-map.md`; target absent in repo-local checkout but present under workspace-level maps.
- `assetutilities` present surfaces: all required canonical surfaces; no broken/stale canonical references detected after false-positive filtering.
- `aceengineer-website` present surfaces: `AGENTS.md`, `README.md`, `docs/README.md`, `docs/maps/aceengineer-website-operator-map.md`; missing `docs/registry/module-routing.yaml`.

## Closeout evidence pattern

Latest-only verification shape:

```text
M docs/reports/tier-1-indexing-freshness-latest.md
path=docs/reports/tier-1-indexing-freshness-latest.md size=<bytes> mtime=<timestamp>
<sha256>  docs/reports/tier-1-indexing-freshness-latest.md
```
