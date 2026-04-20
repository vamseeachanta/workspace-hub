# Provider audit follow-up bundle — 2026-04-20

## Scope
Follow-up on three ecosystem-strengthening actions after reviewing the latest provider-session audit and recent unassessed session logs.

## 1. submit-to-codex hotspot assessment

Current assessment: the stdin-inheritance fix in `scripts/review/submit-to-codex.sh` looks structurally sound.

Why:
- the recent claude hotspot chain points back to `scripts/review/submit-to-codex.sh`, but the live failure mode that triggered #2406 is already covered by dedicated stdin-isolation regression tests
- the remaining meaningful risk was not the original hang itself, but degraded failure handling after dispatch

Additional hardening landed in this follow-up:
- added shell regression coverage for timeout classification
- added shell regression coverage for transport/network classification
- verified the full shell suite remains green

New coverage added:
- `T30`: timeout classification keeps exit `124` and emits timeout guidance
- `T31`: transport classification keeps exit `1` and emits transport/network guidance

Verification:
- `bash tests/review/test-submit-scripts.sh`
- result: 59 passed, 0 failed

Conclusion:
- no further code-path change is currently justified in `submit-to-codex.sh`
- the next highest-value work is keeping classification/diagnostic behavior covered as the wrapper evolves

## 2. codex + hermes unmapped drift triage

### Codex drift buckets
Top codex unmapped reads are not one coherent bug; they split into three buckets:

1. probable other-repo / generated-site paths currently being counted as workspace-hub repo drift
- `content/demos/index.html`
- `content/demos/jumper-installation.html`
- `content/partials/head-common.html`
- `package.json`
- `build.js`
- `vercel.json`
- `examples/demos/gtm/output/*.html`

Observed state in current checkout:
- all sampled paths above are missing from `workspace-hub`
- they appear repeatedly in Codex native rollout exports while the exported `repo` still says `workspace-hub`

Interpretation:
- these are likely cross-repo or generated-artifact reads and should not stay in the same bucket as true workspace-hub stale paths

2. non-filesystem GitHub resource URIs currently counted as missing repo reads
- `github://vamseeachanta/workspace-hub/issues/2249`

Interpretation:
- this is a symbolic/external resource identifier, not a repo-local file path
- it should be classified outside repo-missing drift

3. genuine stale/deleted repo-local references
- `docs/reports/2026-04-17-issue-39-market-hours-signals-consumers-plan.md`

Interpretation:
- these remain actionable repo drift and should stay in the remediation stream

### Hermes drift buckets
Top hermes unmapped reads also split into multiple classes:

1. deleted/stale workspace-hub paths
- `docs/plans/2026-04-10-llm-wiki-resource-doc-repo-integration-blueprint.md`
- `scripts/hooks/pre-push.sh`
- `.planning/quick/review-2239.md`

Observed state in current checkout:
- all sampled paths above are missing from `workspace-hub`

Interpretation:
- these are legitimate stale-path drift candidates

2. cross-repo or non-workspace-hub relative paths being counted as workspace-hub repo drift
- `digitalmodel/specs/module-registry.yaml`
- `client_projects/engineering_workbooks/ballymore/jumper_manifold_to_plet/jumper_lift.py`
- `digitalmodel/docs/...`

Interpretation:
- these are not valid repo-local paths in the current checkout
- they should be split out into a separate cross-repo/sibling-repo bucket instead of inflating workspace-hub missing-file debt

3. already-separated external/worktree reads
- `/mnt/local-analysis/worktrees/...`

Interpretation:
- this bucket is already being surfaced as external; it confirms the audit is close, but not yet complete, on transient/cross-repo separation

## 3. Recommended issue linkage

### #2406
Use #2406 for submit-to-codex hardening notes only.

Add follow-up note:
- stdin-hang fix remains good
- timeout + transport classification regression coverage has now been added and validated

### #2333
Use #2333 as the main home for the codex/hermes drift-classification expansion.

Recommended scope expansion:
- classify `github://...` style URIs as symbolic/external, not repo-missing
- distinguish sibling-repo/cross-repo relative reads from true workspace-hub missing paths
- keep genuine deleted workspace-hub references in the actionable drift bucket

## Comment bundle targets
- issue `#2406`: validation hardening update
- issue `#2333`: new triage evidence for transient/cross-repo/path-classification gaps
