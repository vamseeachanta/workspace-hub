# OrcaFlex execution and model-family handoff

Tracking: [execution 3831](https://github.com/vamseeachanta/workspace-hub/issues/3831), [documentation PR 3832](https://github.com/vamseeachanta/workspace-hub/pull/3832), [repair PR 2081](https://github.com/vamseeachanta/digitalmodel/pull/2081), [portfolio 3601](https://github.com/vamseeachanta/workspace-hub/issues/3601).

## Verified state

- SSH to the primary Linux producer works. Local OrcaFlex 11.6c API/licence and direct smoke passed.
- The user authorized continuing the proposed sequence. The bounded repair for [digitalmodel 1564](https://github.com/vamseeachanta/digitalmodel/issues/1564) and [2051](https://github.com/vamseeachanta/digitalmodel/issues/2051) is committed/pushed at `ce372809`, branch `bugfix/orcaflex-batch-reliability`, draft PR 2081.
- The patched engine CLI completed a generic line's statics/dynamics, saved/reloaded its simulation and returned four finite tension samples: PASS/exit zero. One process; internal solver thread limits are not enforced.
- Final focused suite: 54 passed, one skipped. Overlapping converter check: 20 passed, two skipped; counts are not additive. Source hashes and sanitized proof are in digitalmodel's report. Skipped native-corpus fixtures remain a coverage gap.
- Three subagent lanes handled tests, methodology/skill routing and review. Claude/Codex plan reviews occurred. Claude code findings and source-based dispositions are recorded; its full-source follow-up was unavailable. Independent final Codex review approved the bounded repair. No unanimous approval or deployment certification is claimed.
- Existing skills, the legacy queue README and digitalmodel operator map now route to the [runbook](../solver/orcaflex-execution-runbook.html), [strategy](../reports/2026-09-09-orcaflex-fea-strategy.html) and [measured evidence](../reports/2026-09-09-orcaflex-execution-evidence.md).

## Ordered next work

Continuation checkpoint: the [integration readiness report](../reports/2026-09-09-orcaflex-integration-readiness.html) records live CI and deployment gaps. Documentation merge conflict was resolved in `cc3747c66`, preserving upstream skill corrections; all 16 reported checks passed at that head. Digitalmodel PR 2081 has 30 successful checks. Neither PR was merged into main.

Claude's adversarial plan review found preservation, stale-approved-work discovery and integration-gate defects. Revision 5 addresses them. Claude r2 confirmed textual closure but retained MAJOR because its tool-disabled context could not independently verify supplied evidence. Main rechecked PR metadata, artifact existence, backup digest and admin source trees; the [structured disposition](../../scripts/review/results/2026-09-09-orcaflex-next-disposition.md) preserves the actual verdict. Codex approved advisory preparation only. No consensus/deployment approval is inferred.

1. Integrate the repair after owner review; repeat acceptance against the integrated revision before deployment.
2. Reconcile the execution plan's existing Deckhand trust, host, resource and result-return child owners. Inventory tasks/consumers, pin the release/environment, and verify process stop/lock ownership before replacement. The broader plan remains draft; never self-apply approval labels.
3. Prove one case in the intended Windows task context, then submit the same case from Linux through Deckhand's repository-backed queue. Capture origin/target, attempt identity, revisions, resources, verdict and saved-result readback. SSH alone does not satisfy this step.
4. Reuse typed specifications, MonolithicExtractor and generators for corpus/residual audit. Reconcile stale issue claims; preserve unsupported fields explicitly.
5. Qualify native equivalence and model-family benchmarks; then beam/plate FE, balanced global-to-local load transfer and campaigns. [digitalmodel 2080](https://github.com/vamseeachanta/digitalmodel/issues/2080) tracks adapter element/material fidelity. Follow the full strategy issue map.

## Cleanup audit and boundaries

- CLEAN: actual-path legal scans, local HTML links and diff checks passed. No new stash. Local/remote review-prompt scratch removed. Production tasks retain Running/Ready states; no task/environment configuration changed.
- EXPECTED: two isolated worktrees, pushed branches and draft PRs retained for integration review. Generic proof directories `orcaflex-batch-proof-3ytc_ubo` and `orcaflex-batch-proof-4cc0glvu` remain in the current user's temporary directory; sanitized evidence is committed. Private portfolio inventory and Deckhand raw export remain local; do not publish raw private issue bodies.
- EXPECTED: private Windows task exports and digest manifest are retained in local temporary directory `orcaflex-release-preflight-128a8ff5023f4824897e2aa397004757`. Four Linux untracked entries are backed up in `/tmp/codex-3831-deckhand-preserve-i3az0ebp`; manifest digest is in the structured disposition. Preserve these backups until the approved rollout and post-cutover identity checks finish. They contain private paths and must not be published.
- EXPECTED: seven pre-existing digitalmodel benchmark modifications, six workspace-hub stashes and unrelated main-checkout state/session reports preserved. Deckhand working tree is clean; its divergent local commit is preserved. Other sibling worktrees belong to separate work.
- UNEXPECTED: no new untraced task residue in the scoped audit; this was not a full-machine cleanup.

Legal caveat: named-repo scanning resolved an empty path and falsely passed. Actual digitalmodel scanning used explicit-root `--all --diff-only` in the isolated hub worktree without initialized submodules. Reproduction and workaround limits were posted to [workspace-hub 3804](https://github.com/vamseeachanta/workspace-hub/issues/3804).

External actions: pushed draft branches, created repair PR 2081 and posted issue checkpoints. No production queue request, merge, deployment, email or chat notification. No issue auto-closure or self-applied approval label.
