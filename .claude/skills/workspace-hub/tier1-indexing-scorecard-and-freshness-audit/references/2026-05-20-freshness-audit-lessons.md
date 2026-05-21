# 2026-05-20 Tier-1 Freshness Audit Lessons

## Context
Scheduled daily freshness audit for `/mnt/local-analysis/workspace-hub` covering tier-1 repos: `workspace-hub`, `digitalmodel`, `assetutilities`, and `aceengineer-website`.

## Durable lessons

### 1. Deduplicate generated broken-reference evidence before finalizing
The freshness generator can emit the same broken Markdown target more than once when the same line/link is discovered through multiple scan paths. Before final delivery:
- read back the generated report section/table,
- collapse duplicate `(repo, source file, line, target)` findings,
- preserve the issue once as confirmed evidence.

Observed case: `digitalmodel/README.md:73` -> `specs/data-needs.yaml` was generated twice, then manually deduplicated in both the status table and detailed section.

### 2. Final verification belongs after all report edits
If the report is patched after generation, run final verification only after those patches. Good final evidence for the cron response:
- `git status --short -- docs/reports/tier-1-indexing-freshness-latest.md`
- `stat -c 'path=%n size=%s mtime=%y' docs/reports/tier-1-indexing-freshness-latest.md`
- `sha256sum docs/reports/tier-1-indexing-freshness-latest.md`

This avoids reporting stale file size/mtime/hash values from the pre-patch report.

### 3. Status continuity remained unchanged
Status-level baseline after the corrected 2026-05-20 scan:
- `workspace-hub`: RED
- `digitalmodel`: YELLOW
- `assetutilities`: YELLOW
- `aceengineer-website`: RED
- portfolio: RED

No material status-level drift was detected, but existing blockers remained material.

## Confirmed evidence snapshot

Missing routing/operator surfaces:
- `workspace-hub/docs/maps/workspace-hub-operator-map.md`
- `workspace-hub/docs/registry/module-routing.yaml`
- `aceengineer-website/docs/registry/module-routing.yaml`

Broken/stale active references:
- `workspace-hub/docs/README.md:300` -> `../.agent-os/product/mission.md`
- `workspace-hub/docs/README.md:301` -> `../.agent-os/product/tech-stack.md`
- `workspace-hub/docs/README.md:302` -> `../.agent-os/product/roadmap.md`
- `workspace-hub/docs/README.md:303` -> `../.agent-os/product/decisions.md`
- `digitalmodel/README.md:73` -> `specs/data-needs.yaml` (unique after dedupe)

Legacy-reference evidence in `workspace-hub/docs/README.md`:
- line 264
- lines 300-303

Noise counts from generated scan, useful as directional hygiene signal only:
- `workspace-hub`: 1435
- `digitalmodel`: 3626
- `assetutilities`: 637
- `aceengineer-website`: 33

## Reporting wording
Use: "no material drift detected at the status level" when statuses are unchanged but evidence was refreshed or deduplicated. Do not imply all blockers are gone.