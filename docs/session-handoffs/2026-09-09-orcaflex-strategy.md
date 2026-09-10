# OrcaFlex execution and model-family handoff

Tracking: [execution 3831](https://github.com/vamseeachanta/workspace-hub/issues/3831), [documentation PR 3832](https://github.com/vamseeachanta/workspace-hub/pull/3832), [repair PR 2081](https://github.com/vamseeachanta/digitalmodel/pull/2081), [portfolio 3601](https://github.com/vamseeachanta/workspace-hub/issues/3601).

## Objectives — updated 2026-09-10

1. Reliable OrcaFlex execution from enrolled ecosystem machines through the existing licensed Windows execution lane, with truthful failure/result evidence and measured per-origin coverage.
2. Qualified FEA models for component and structure families through existing specifications, libraries and solver adapters: OrcaFlex global/slender-system response, structural FE for detailed components, and verified load transfer between them.

The merged batch repair is an accepted local software checkpoint, not deployment or engineering-model approval. No new framework or competing registry will be introduced.

## Verified state

- SSH to the primary Linux producer works. Local OrcaFlex 11.6c API/licence and direct smoke passed.
- The user authorized continuing the proposed sequence. The bounded repair for [digitalmodel 1564](https://github.com/vamseeachanta/digitalmodel/issues/1564) and [2051](https://github.com/vamseeachanta/digitalmodel/issues/2051) is committed/pushed at `ce372809`, branch `bugfix/orcaflex-batch-reliability`. Review-only commit `96014107` records Claude MINOR; PR 2081 was merged with explicit user authorization at `80da6e09b649707ef7bdb09c9d112f1650bf3d6a`. The isolated repair worktree is detached at that merged revision.
- The patched engine CLI completed a generic line's statics/dynamics, saved/reloaded its simulation and returned four finite tension samples: PASS/exit zero. One process; internal solver thread limits are not enforced.
- Final focused suite: 54 passed, one skipped. Overlapping converter check: 20 passed, two skipped; counts are not additive. Source hashes and sanitized proof are in digitalmodel's report. Skipped native-corpus fixtures remain a coverage gap.
- Three subagent lanes handled tests, methodology/skill routing and review. Claude/Codex plan reviews occurred. Claude code findings and source-based dispositions are recorded; its full-source follow-up was unavailable. Independent final Codex review approved the bounded repair. No unanimous approval or deployment certification is claimed.
- Existing skills, the legacy queue README and digitalmodel operator map now route to the [runbook](../solver/orcaflex-execution-runbook.html), [strategy](../reports/2026-09-09-orcaflex-fea-strategy.html) and [measured evidence](../reports/2026-09-09-orcaflex-execution-evidence.md).

## Ordered next work

The immediate smoke-strengthening owner is [digitalmodel 2082](https://github.com/vamseeachanta/digitalmodel/issues/2082), with its HTML plan and fake-API reproduction on branch `chore/orcaflex-smoke-2082-plan`. Seven injected invalid scenarios returned false success at merged base `80da6e09`; no licence was acquired. The plan is pushed at `ce5c7dc3` in [draft planning PR 2084](https://github.com/vamseeachanta/digitalmodel/pull/2084), with status:plan-review and owner approval pending. Codex r1 was advisory APPROVE; Claude r2 retained MAJOR for an omitted explicit Windows scope, which main corrected inline along with CI registration. Gemini was UNAVAILABLE. The actual verdicts and dispositions are preserved; no consensus is claimed. The new isolated worktree is `wt-digitalmodel-orcaflex-smoke-plan`; production source remains unchanged.

Continuation checkpoint: the [integration readiness report](../reports/2026-09-09-orcaflex-integration-readiness.html) records live CI and deployment gaps. Documentation merge conflict was resolved in `cc3747c66`, preserving upstream skill corrections; all 16 reported checks passed at that head. Digitalmodel PR 2081 has 30 successful checks. PR 2081 subsequently merged; documentation PR 3832 remains open and draft.

The user-requested Claude code-review follow-up completed with exit zero and MINOR after one timed-out attempt. It found no functional defect; missing variant IDs in summary diagnostics and extra null-spelling dump coverage remain non-blocking follow-ups in digitalmodel issue 2051. Full static-review output is in digitalmodel `docs/reviews/orcaflex-batch-claude-final-review.md`; no code changed. The actual native and CI evidence retain their separately verified source head `ce372809`.

Claude's adversarial plan review found preservation, stale-approved-work discovery and integration-gate defects. Revision 5 addresses them. Claude r2 confirmed textual closure but retained MAJOR because its tool-disabled context could not independently verify supplied evidence. Main rechecked PR metadata, artifact existence, backup digest and admin source trees; the [structured disposition](../../scripts/review/results/2026-09-09-orcaflex-next-disposition.md) preserves the actual verdict. Codex approved advisory preparation only. No consensus/deployment approval is inferred.

1. Start from accepted merged revision `80da6e09`: 54 passed, one skipped; native 11.6c statics/dynamics and saved-simulation reload returned four finite samples, PASS/exit zero. See [merged proof](../reports/2026-09-09-orcaflex-merged-proof.json). Strengthen the existing bounded smoke with RED-first tests for explicit one-thread operation, finite results and saved-simulation reload, then verify the new revision. Repair merge is no longer pending.
2. Prepare the neutral service scope and task-cutover package: exact allowed repository/fixture revision, private workdir/host mapping, effective policy and rollback evidence. Reconcile existing Deckhand trust, host, resource and result-return owners; inventory tasks/consumers and verify process-stop/lock ownership before replacement. Scope/cutover approval remains outstanding; no approval label will be self-applied.
3. After the preceding gates pass, prove the bounded smoke in the credentialed Windows task context, then submit from Linux through Deckhand's repository-backed queue. Capture origin/target, attempt identity, revisions, resources, verdict and saved-result readback. SSH and ordinary smoke success will not satisfy the separate full batch or signed-project acceptance contracts.
4. Qualify the suspended-line family, then beam/plate FE benchmarks. Reuse typed specifications, MonolithicExtractor and generators for corpus/residual audit; preserve unsupported fields and mappings explicitly. [digitalmodel 2080](https://github.com/vamseeachanta/digitalmodel/issues/2080) owns adapter element/material fidelity.
5. Qualify balanced global-to-local load transfer, then expand coupled families and campaigns within demonstrated applicability limits. Follow the existing strategy issue map and report/qualification owners.

## Cleanup audit and boundaries

- CLEAN: actual-path legal scans, local HTML links and diff checks passed. No new stash. Local/remote review-prompt scratch removed. Production tasks retain Running/Ready states; no task/environment configuration changed.
- EXPECTED: three isolated worktrees retained: execution documentation, detached merged repair, and smoke planning; repair PR 2081 is merged, documentation PR 3832 remains draft. The isolated solver worktree is detached at the merge revision for reproducibility. Generic proof directories `orcaflex-merged-proof-v79j4sey`, `orcaflex-batch-proof-3ytc_ubo` and `orcaflex-batch-proof-4cc0glvu` remain in the current user's temporary directory; sanitized evidence is committed. Private portfolio inventory and Deckhand raw export remain local; do not publish raw private issue bodies.
- EXPECTED: raw Claude smoke-plan review is retained privately in temporary directory `orcaflex-smoke-review-private`; the published transcript redacts private host/path references injected by the reviewer. All new issue/PR draft scratch was removed.
- EXPECTED: private Windows task exports and digest manifest are retained in local temporary directory `orcaflex-release-preflight-128a8ff5023f4824897e2aa397004757`. Four Linux untracked entries are backed up in `/tmp/codex-3831-deckhand-preserve-i3az0ebp`; manifest digest is in the structured disposition. Preserve these backups until the approved rollout and post-cutover identity checks finish. They contain private paths and must not be published.
- EXPECTED: seven pre-existing digitalmodel benchmark modifications, six workspace-hub stashes and unrelated main-checkout state/session reports preserved. Deckhand working tree is clean; its divergent local commit is preserved. Other sibling worktrees belong to separate work.
- UNEXPECTED: no new untraced task residue in the scoped audit; this was not a full-machine cleanup.

Legal caveat: named-repo scanning resolved an empty path and falsely passed. Actual digitalmodel scanning used explicit-root `--all --diff-only` in the isolated hub worktree without initialized submodules. Reproduction and workaround limits were posted to [workspace-hub 3804](https://github.com/vamseeachanta/workspace-hub/issues/3804).

External actions: pushed draft branches, created repair PR 2081, smoke issue 2082 and CI-discovery follow-on [2083](https://github.com/vamseeachanta/digitalmodel/issues/2083), and posted issue checkpoints. PR 2081 was merged under explicit user authorization. No production queue request, deployment, email or chat notification. No issue auto-closure or self-applied approval label.
