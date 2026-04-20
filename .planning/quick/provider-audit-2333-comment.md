New drift-triage evidence from the refreshed provider-session audit:

Codex and Hermes "unmapped path drift" is not a single class of problem. The current top offenders split into at least three buckets:

1. True stale workspace-hub paths
- examples: `docs/plans/2026-04-10-llm-wiki-resource-doc-repo-integration-blueprint.md`, `scripts/hooks/pre-push.sh`, `.planning/quick/review-2239.md`
- sampled live in the current checkout: all missing
- these should stay in the actionable repo-drift bucket

2. Cross-repo / sibling-repo relative paths currently counted as workspace-hub repo drift
- examples: `digitalmodel/specs/module-registry.yaml`, `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py`, `digitalmodel/docs/...`
- these are not valid repo-local paths in the current workspace-hub checkout
- recommendation: split them into a separate cross-repo/sibling-repo bucket

3. Non-filesystem resource identifiers currently counted as repo-missing
- example: `github://vamseeachanta/workspace-hub/issues/2249`
- recommendation: classify `github://...` URIs as symbolic/external, not repo-local missing files

There is also a Codex cluster of probable other-repo or generated-site paths being counted as workspace-hub drift:
- `content/demos/index.html`
- `content/partials/head-common.html`
- `package.json`
- `build.js`
- `vercel.json`
- `examples/demos/gtm/output/*.html`

Sampled live in the current checkout: these are missing from workspace-hub, but they recur in Codex native rollout exports while the exported repo is still `workspace-hub`, which strongly suggests classification noise rather than pure stale-path debt.

Recommendation for #2333 scope:
- add explicit classification for `github://...` resource URIs
- add a sibling-repo / cross-repo-relative bucket distinct from true repo-local missing paths
- keep deleted workspace-hub paths in the actionable remediation stream

Related artifact:
- `docs/reports/2026-04-20-provider-audit-followup-bundle.md`