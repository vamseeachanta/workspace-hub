---
name: plan-review-adversarial-hardening
version: 1.0.0
category: software-development
description: Class-level workflow for plan-review hardening, adversarial review reruns, artifact grounding, approval hygiene, and prompt/path drift recovery.
tags: [plan-review, adversarial-review, github, workflow]
---

# Plan Review Adversarial Hardening

## When to Use
Use when a GitHub plan, implementation plan, or review artifact must survive adversarial review across Codex/Gemini/Claude/Hermes; when reviewer prompts become stale; when artifacts must be inlined because tools cannot read paths; or when plan approval/governance state drifts.

## Class-Level Workflow
1. Re-sync live issue/repo state before generating prompts or review artifacts.
2. Ground reviewers on absolute paths or inline artifacts when filesystem access is unreliable.
3. Separate governance/state findings from substantive plan blockers.
4. Refresh prompts after every material plan edit; never rerun reviewers against stale prompt files.
5. Preserve empty/no-tools review evidence explicitly so later agents know whether the run failed, found nothing, or lacked access.
6. If provider fanout returns only `UNAVAILABLE` artifacts, do not call that a review pass. Keep the issue in `status:plan-review` only as a blocked holding state, add a governance artifact/comment that names the provider/tooling failures, and state that implementation remains blocked pending user approval or a later review retry.
7. Before approval, reconcile plan body, issue state, review artifacts, and attestation comments. The plan/index/comment must not imply no-MAJOR review evidence exists when it does not.
8. When local git/status/commit operations hang because provider review processes spawned stuck `git status`/hook work, use narrow process inspection and, if necessary, GitHub API commits for docs-only plan artifacts; then verify remote content via API before posting issue comments.
9. When resuming a `status:plan-review` audit from a handoff, read the latest preserved provider artifacts first, patch the plan against exact MAJOR findings, then explicitly keep approval blocked until a fresh post-patch review returns no MAJORs or the user grants a named waiver. Local plan edits alone are not approval evidence.
10. In dirty operational repos, report the narrow intentional diff separately from the broad dirty tree. Do not reset/clean unrelated modified or untracked artifacts; verify approval markers are absent/present before changing labels or creating `.planning/plan-approved/<issue>.md`.
11. For Codex review reruns with prior stdin-stall signatures, prefer EOF-safe prompt-file/stdin-closed invocation patterns and verify the fanout runner behavior before launching long provider waves.
12. Session reference: `references/post-major-plan-hardening-with-dirty-tree.md` captures a concrete 2026-04-30 example of patching two MAJOR-reviewed plans without mutating approvals.
13. In evidence-gate reruns, do not let a structural validator overclaim semantic proof. If the validator checks counts, required fields, URL shape, and deny/contact regexes, describe it that way and leave official-domain/legal/privacy semantics to explicit reviewer/manual spot-checks unless encoded directly.
14. Before promoting a plan after iterative reruns, commit durable provider artifacts and synthesis to the repo; `/tmp` fanout outputs are useful working evidence but are not sufficient durable gate evidence when the plan AC requires archived review files.
15. If `git push` or pre-push hooks time out after partial output, verify `HEAD` versus `origin/main` before rerunning reviewers or claiming the remote was updated.
16. Session reference: `references/evidence-gate-rerun-and-remote-verification.md` captures the evidence-validator, artifact-archive, and remote-SHA verification pattern from a 2026-04-30 #2554 GTM plan-review loop.

## Consolidated Session Learnings

The `references/` directory contains archived narrow skills absorbed during the 2026-04-29 umbrella consolidation pass. Use the subsections below as the class-level index, then open the named reference when a case-specific recipe is needed.
## Absorbed Narrow Skills (2026-04-29)

### `absolute-path-review-dispatch-guard`

- Former skill demoted to `references/absolute-path-review-dispatch-guard.md`.
- Preserved insight: Prevent Codex/Gemini adversarial review dispatch failures caused by relative prompt-file paths and background workdir drift.

### `absolute-path-review-prompt-dispatch`

- Former skill demoted to `references/absolute-path-review-prompt-dispatch.md`.
- Preserved insight: Prevent adversarial review dispatch failures caused by relative prompt paths, superseded background sessions, and stale completion notices when launching Codex/Gemini review jobs.

### `adversarial-review-prompt-refresh-guard`

- Former skill demoted to `references/adversarial-review-prompt-refresh-guard.md`.
- Preserved insight: Prevent stale plan/code review prompts from being sent to Codex/Gemini after the underlying artifact changed.

### `adversarial-review-rerun-prompt-refresh`

- Former skill demoted to `references/adversarial-review-rerun-prompt-refresh.md`.
- Preserved insight: Prevent stale rerun reviews by regenerating provider prompt files from the latest plan or diff before every adversarial review rerun.

### `approval-stage-plan-hygiene`

- Former skill demoted to `references/approval-stage-plan-hygiene.md`.
- Preserved insight: Prevent approval-stage adversarial review churn by keeping plans implementation-focused, schema-complete, and free of stale review-process narration.

### `approval-stage-plan-review-sweep`

- Former skill demoted to `references/approval-stage-plan-review-sweep.md`.
- Preserved insight: Run an approval-stage adversarial cross-review sweep across multiple GitHub issues, drafting any missing canonical plan artifacts before dispatching Codex/Gemini reviews.

### `artifact-inline-local-plan-rereview`

- Former skill demoted to `references/artifact-inline-local-plan-rereview.md`.
- Preserved insight: Prevent stale Codex/Gemini findings by rerunning plan review against the exact revised local artifact inline when summary prompts keep anchoring on remote/main plan content.

### `artifact-inline-no-tools-plan-review`

- Former skill demoted to `references/artifact-inline-no-tools-plan-review.md`.
- Preserved insight: Recover adversarial plan reviews on large or sandbox-hostile repos by embedding grounded facts + full plan text directly in a compact prompt and explicitly forbidding reviewer tool use.

### `artifact-inline-plan-rereview`

- Former skill demoted to `references/artifact-inline-plan-rereview.md`.
- Preserved insight: Recover adversarial plan reviews when providers keep reading stale remote/main content instead of the revised local artifact.

### `artifact-inline-plan-review-for-local-draft-revisions`

- Former skill demoted to `references/artifact-inline-plan-review-for-local-draft-revisions.md`.
- Preserved insight: Prevent false MAJOR plan-review findings when Codex/Gemini review stale remote/main artifacts instead of the revised local draft.

### `avoid-empty-review-artifact-evidence-in-plan-redrafts`

- Former skill demoted to `references/avoid-empty-review-artifact-evidence-in-plan-redrafts.md`.
- Preserved insight: Keep plan redrafts truthful during adversarial rerun loops by never citing zero-byte or not-yet-generated review artifacts as resolved evidence.

### `compact-no-tools-plan-review-recovery`

- Former skill demoted to `references/compact-no-tools-plan-review-recovery.md`.
- Preserved insight: Recover adversarial plan reviews in large or tool-constrained repos by using compact self-contained prompts that forbid tool use and rely only on embedded grounded facts plus the plan text.

### `iterative-plan-hardening-with-adversarial-waves`

- Former skill demoted to `references/iterative-plan-hardening-with-adversarial-waves.md`.
- Preserved insight: Tighten a draft plan through repeated Codex/Gemini adversarial review waves without prematurely advancing it to plan-review.

### `iterative-plan-redraft-semantic-guardrails`

- Former skill demoted to `references/iterative-plan-redraft-semantic-guardrails.md`.
- Preserved insight: Harden a repeatedly re-reviewed documentation/contract plan after adversarial reviewers keep finding semantic gaps despite new test rows.

### `plan-draft-review-artifact-truthfulness-and-issue-body-alignment`

- Former skill demoted to `references/plan-draft-review-artifact-truthfulness-and-issue-body-alignment.md`.
- Preserved insight: Keep plan drafts truthful during adversarial review loops by verifying real provider artifact state on disk and aligning the GitHub issue body to the bounded plan tranche before claiming approval-readiness.

### `plan-governance-vs-execution-boundary-for-adversarial-review`

- Former skill demoted to `references/plan-governance-vs-execution-boundary-for-adversarial-review.md`.
- Preserved insight: Keep stale-approval/governance remediation out of execution-path pseudocode, TDD, files-to-change, and deliverable acceptance when hardening a GitHub issue plan under adversarial review.

### `plan-rerun-review-state-sync`

- Former skill demoted to `references/plan-rerun-review-state-sync.md`.
- Preserved insight: Keep iterative plan-review reruns truthful by syncing prompt files, canonical review artifacts, and the plan's own review-summary narrative after each adversarial wave.

### `plan-rerun-state-revalidation`

- Former skill demoted to `references/plan-rerun-state-revalidation.md`.
- Preserved insight: Revalidate live plan state before rerunning adversarial review or resuming from a handoff so review prompts do not encode stale approval/artifact assumptions.

### `plan-review-approval-shortlist-audit`

- Former skill demoted to `references/plan-review-approval-shortlist-audit.md`.
- Preserved insight: Audit a status:plan-review queue to identify true approval candidates without being fooled by stale labels, conditional review summaries, or unresolved prerequisite blockers.

### `plan-review-artifact-authority-and-approval-drift`

- Former skill demoted to `references/plan-review-artifact-authority-and-approval-drift.md`.
- Preserved insight: Keep iterative plan-review artifacts truthful when external reruns overtake self-reviews or stale approval signals remain on older revisions.

### `plan-review-fanout-runner-drift-recovery`

- Former skill demoted to `references/plan-review-fanout-runner-drift-recovery.md`.
- Preserved insight: Recover plan-review waves when provider wrapper/cwd/date drift creates false MAJOR or UNAVAILABLE artifacts instead of substantive review.

### `provider-unavailable-plan-review-holding-pattern`

- Session reference: `references/provider-unavailable-plan-review-holding-pattern.md`.
- Preserved insight: When all providers return `UNAVAILABLE`, `status:plan-review` may be used only as a blocked human-review holding state; publish a truthful governance artifact/comment and keep implementation blocked until user approval or review retry.

### `plan-review-handoff-verification`

- Former skill demoted to `references/plan-review-handoff-verification.md`.
- Preserved insight: Verify a parked GitHub issue plan-review handoff across live labels, local markers, README rows, canonical review artifacts, and stale plan-body evidence before reporting next action.

### `plan-review-prompt-refresh-after-plan-edits`

- Former skill demoted to `references/plan-review-prompt-refresh-after-plan-edits.md`.
- Preserved insight: Refresh reviewer prompt files from the latest on-disk plan before every adversarial re-review. Prevents Codex/Gemini from critiquing stale plan text after local edits.

### `plan-review-queue-governance-cleanup`

- Former skill demoted to `references/plan-review-queue-governance-cleanup.md`.
- Preserved insight: Clean a stale `status:plan-review` queue by separating missing-plan drift from real review blockers, posting governance comments, removing stale labels, and materializing durable review artifacts for delegated/Hermes reviews.

### `plan-review-rerun-cli-drift-and-git-contention`

- Former skill demoted to `references/plan-review-rerun-cli-drift-and-git-contention.md`.
- Preserved insight: Recover iterative plan-review work when provider CLI wrappers drift, fresh reviews expose stale governance text, and active git pre-push processes make committing unsafe.

### `planning-lane-cross-review-permission-fallback`

- Former skill demoted to `references/planning-lane-cross-review-permission-fallback.md`.
- Preserved insight: Handle overnight planning-only lanes where plan revision/editing works but real cross-provider review dispatch is permission-blocked.

### `provider-review-prompt-path-guard`

- Former skill demoted to `references/provider-review-prompt-path-guard.md`.
- Preserved insight: Prevent adversarial review dispatch failures caused by sandbox/tmp path mismatches and provider CLI working-directory drift when launching Codex or Gemini with prompt files.

### `re-review-local-plan-artifact-grounding`

- Former skill demoted to `references/re-review-local-plan-artifact-grounding.md`.
- Preserved insight: Prevent stale adversarial re-reviews by forcing Codex/Gemini to review the exact revised local plan artifact instead of stale GitHub issue text or default-branch content.

### `split-plan-governance-vs-substance`

- Former skill demoted to `references/split-plan-governance-vs-substance.md`.
- Preserved insight: When repeated adversarial plan reviews keep returning MAJOR findings about validator mechanics, evidence bookkeeping, or governance traceability rather than the core product or mission decision, stop tightening the monolithic plan and split it into a content/decision packet and a tooling/enforcement packet.

### `stage-prompt-drift-guard`

- Former skill demoted to `references/stage-prompt-drift-guard.md`.
- Preserved insight: Audit historical stage-prompt artifact drift from Claude logs, generate a package index, and enforce only newly introduced drift in CI and local pre-push hooks.

### `ten-agent-pre-plan-review-wave`

- Former skill demoted to `references/ten-agent-pre-plan-review-wave.md`.
- Preserved insight: Launch and verify a 10-agent planning-only wave that moves open GitHub issues into status:plan-review using one isolated worktree per issue, wave-specific continuation cron, and post-run artifact-reconciliation checks.

### `user-approved-plan-state-sync`

- Former skill demoted to `references/user-approved-plan-state-sync.md`.
- Preserved insight: Reconcile GitHub and local repo state when a plan has been user-approved, including direct approval messages that require creating the local marker and moving the issue to status:plan-approved.

### `static-site-build-artifact-plan-review`

- Former skill demoted to `references/static-site-build-artifact-plan-review.md`.
- Preserved insight: Plan-review pattern for static-site fixes where the deployed artifact is generated from source files (e.g. sitemap/robots/static assets). Prevents review churn by separating durable regression checks from one-time migration verification and by validating built output, not just source files.

### `canonical-doc-contract-plan-hardening`

- Former skill demoted to `references/canonical-doc-contract-plan-hardening.md`.
- Preserved insight: Harden a documentation or mission-contract plan so adversarial reviewers cannot reject it for vague validator contracts, wrong artifact authority, or semantic drift gaps.

### `documentation-contract-plan-hardening`

- Former skill demoted to `references/documentation-contract-plan-hardening.md`.
- Preserved insight: Harden a documentation/contract plan before adversarial review by mapping every issue-scope requirement to independent acceptance criteria and tests, especially for routing/indexing contracts.

### `bounded-post-smoke-ci-hardening-plan`

- Former skill demoted to `references/bounded-post-smoke-ci-hardening-plan.md`.
- Preserved insight: Plan post-smoke CI hardening as a bounded blocker-removal tranche instead of overpromising full green. Includes issue-body alignment, follow-up split rules, honest review bookkeeping, and reliable local validation commands.

### `post-smoke-ci-plan-boundary-hardening`

- Former skill demoted to `references/post-smoke-ci-plan-boundary-hardening.md`.
- Preserved insight: Harden a CI follow-up plan after an initial smoke/unblock issue lands. Use for post-smoke red workflows where later gates surface broad lint/type debt and the plan must stay bounded, evidence-backed, and review-honest.

### `agent-work-adversarial-review`

- Former skill demoted to `references/agent-work-adversarial-review.md`.
- Preserved insight: Adversarially review the last 24h of multi-agent work by combining git history, GitHub issue state, generated analysis artifacts, governance tests, and duplicate-checked follow-up issue creation.

### `plan-exit-governance-drift-handoff`

- Former skill demoted to `references/plan-exit-governance-drift-handoff.md`.
- Preserved insight: When ending a session on an iterated plan draft, audit and document approval-state drift across GitHub labels, local approval markers, README status, and latest review verdicts.

### `mixed-ops-vs-repo-fix-plan-boundary`

- Former skill demoted to `references/mixed-ops-vs-repo-fix-plan-boundary.md`.
- Preserved insight: Plan mixed operational-vs-repo remediation issues by proving live-state classification first, then only proposing code changes for confirmed repo-owned failure paths.
