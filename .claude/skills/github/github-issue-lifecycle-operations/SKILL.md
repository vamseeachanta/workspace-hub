---
name: github-issue-lifecycle-operations
version: 1.0.0
category: github
description: "Class-level GitHub issue lifecycle operations: issue creation, planning/execution routing, labels, evidence fields, roadmap anchors, closeout races, and visual planning."
tags: [github, issues, planning, closeout]
---

# Github Issue Lifecycle Operations

## When to Use
Use for GitHub issue intake, decomposition, planning, execution handoff, label/evidence automation, roadmap reuse, closeout, or cross-issue waves.

## Class-Level Workflow
1. Discover repo, existing anchors, labels, and issue state before writing.
2. Prefer durable umbrella/roadmap anchors over duplicate replacement epics.
3. Put command-heavy bodies in files to avoid shell quoting and command substitution hazards.
4. Maintain explicit evidence fields and closeout comments before state transitions.
5. If a docs-only planning commit is blocked by branch protection / required PR rules, publish the exact planning commit on a short-lived `plan/issue-<N>-...` branch, open a PR, and post the issue's final plan-review comment with the PR/branch evidence instead of treating direct-main push failure as completion.
6. Use checklist skills as support material, not separate discovery targets.
7. For user-approved batches, reconcile labels with explicit issue-number `gh issue view` loops and body-file comments; do not rely on broad comma-separated `gh issue list --search` queries for final proof. See `references/approval-label-reconciliation.md`.
8. For W0/Kanban reconciliation, classify stale WIP into closeable-landed, landed-but-externally-blocked, no-code dependency-blocked, or closed-label-drift before launching any new swarm; verify landed commits against `origin/main`, post evidence via body files, fix labels, and write a scoped report without sweeping unrelated generated dirt. See `references/w0-kanban-reconciliation-closeout.md`.

## Consolidated Session Learnings

The `references/` directory contains archived narrow skills absorbed during the 2026-04-29 umbrella consolidation pass. Use the subsections below as the class-level index, then open the named reference when a case-specific recipe is needed.
### `w0-kanban-reconciliation-closeout`

- Session reference: `references/w0-kanban-reconciliation-closeout.md`.
- Preserved insight: Before launching the next Kanban/5-hour swarm wave, reconcile stale W0/WIP items by proving landed commits, closing only fully satisfied issues, rerouting runtime/dependency blockers to `status:blocked`, cleaning closed-label drift, and committing a scoped report while leaving unrelated generated root dirt untouched.

## Absorbed Narrow Skills (2026-04-29)

### `gh-issue-creation-full-repo-and-batch-setup`

- Former skill demoted to `references/gh-issue-creation-full-repo-and-batch-setup.md`.
- Preserved insight: Create multiple related GitHub issues safely by resolving full OWNER/REPO, checking duplicates and labels first, and verifying each created issue.

### `gh-work-execution`

- Former skill demoted to `references/gh-work-execution.md`.
- Preserved insight: Canonical GitHub issue execution route after plan approval — strengthened resource intelligence, TDD-first implementation, targeted validation, adversarial review, delegation controls for Claude agent teams, GitHub progress posting, future-issue capture, and commit/push with closeout discipline.
- Repo-structure/CI readiness addendum: use `references/repo-structure-contract-gate-slices.md` for bounded Phase 1 structure-normalization issues that need approval-marker evidence, TDD contract/checker/wiring, generated-root exceptions, CI/pre-commit enforcement, generated-churn cleanup, and transactional closeout.

### `gh-work-execution-checklist`

- Former skill demoted to `references/gh-work-execution-checklist.md`.
- Preserved insight: Compact live-execution checklist companion for approved GitHub issue work. Use during active implementation as a fast operational route; gh-work-execution remains the canonical source of truth.

### `gh-work-planning`

- Former skill demoted to `references/gh-work-planning.md`.
- Preserved insight: Canonical GitHub issue planning route — issue intake, strengthened resource intelligence, repo-tracked plan artifact, adversarial review, GitHub progress posting, future-issue capture, explicit approval gate before execution, and execution-ready delegation packaging for Claude agent teams.

### `gh-work-planning-checklist`

- Former skill demoted to `references/gh-work-planning-checklist.md`.
- Preserved insight: Compact live-execution checklist companion for the canonical gh-work-planning route. Use for fast operational tracking during issue planning without replacing the full route.

### `github-comment-body-file-safety`

- Former skill demoted to `references/github-comment-body-file-safety.md`.
- Preserved insight: Prevent shell-quoting and command-substitution bugs when posting GitHub issue/PR comments or editing bodies with gh CLI.

### `github-interaction-limits-hardening`

- Former skill demoted to `references/github-interaction-limits-hardening.md`.
- Preserved insight: Lock down public GitHub repositories so only collaborators can interact with issues, PRs, comments, discussions, and other user-generated surfaces using repository interaction limits; includes expiry verification and renewal handling.

### `github-issue-automation-evidence-fields`

- Former skill demoted to `references/github-issue-automation-evidence-fields.md`.
- Preserved insight: Use when building GitHub issue classifiers, dashboards, closeout verifiers, or queue/report automation that depends on comments, approval evidence, or linked PR handoff state.

### `github-issue-closeout-race-safe`

- Former skill demoted to `references/github-issue-closeout-race-safe.md`.
- Preserved insight: Close GitHub issues without losing the evidence comment when multiple agents or races may close the issue concurrently.

### `github-issue-label-audit-and-command-bundles`

- Former skill demoted to `references/github-issue-label-audit-and-command-bundles.md`.
- Preserved insight: Safely turn drafted issue bodies into reusable gh issue create commands by auditing repo labels, exact duplicates, and auth first.

### `github-issue-label-existence-audit`

- Former skill demoted to `references/github-issue-label-existence-audit.md`.
- Preserved insight: Prevent GitHub issue creation failures by auditing exact label existence, duplicate titles, and partial-create risk before calling gh issue create.

### `github-roadmap-anchor-reuse`

- Former skill demoted to `references/github-roadmap-anchor-reuse.md`.
- Preserved insight: Reuse and reopen existing roadmap/epic GitHub issues instead of fragmenting work across duplicate replacement epics; retarget children and link active issues for continuity.

### `github-visual-planning-issues`

- Former skill demoted to `references/github-visual-planning-issues.md`.
- Preserved insight: Create review-friendly GitHub planning issues that supersede stale/seasonal issues and include source-backed image thumbnails for faster human review.

### `issue-tree-decomposition`

- Former skill demoted to `references/issue-tree-decomposition.md`.
- Preserved insight: Break a large umbrella GitHub issue into a layered tree of focused follow-on issues using read-only subagent analysis, then create the issues locally and update docs/parent issue with the issue map.

### `roadmap-anchor-issue-governance`

- Former skill demoted to `references/roadmap-anchor-issue-governance.md`.
- Preserved insight: Reopen and reuse the original roadmap/umbrella issue as the governance anchor; create new issues only for genuinely missing scoped work, then retarget/link all execution issues back to the anchor.

### `roadmap-issue-reopen-retarget-balance`

- Former skill demoted to `references/roadmap-issue-reopen-retarget-balance.md`.
- Preserved insight: Reopen existing roadmap anchors, close replacement epics, retarget new child issues, and add sequencing/de-dup comments so GitHub roadmap work preserves continuity and execution quality.

### `roadmap-to-github-issue-wave`

- Former skill demoted to `references/roadmap-to-github-issue-wave.md`.
- Preserved insight: Turn a roadmap/readiness review into a de-duplicated GitHub epic + child issue set with verification and explicit scope boundaries.

### `closed-issue-plan-refile-loop`

- Former skill demoted to `references/closed-issue-plan-refile-loop.md`.
- Preserved insight: Reopen and re-drive a previously closed GitHub plan issue after review/governance blockers are fixed, without prematurely restoring approval state.

### `preserved-plan-refile-with-attested-review-wave`

- Former skill demoted to `references/preserved-plan-refile-with-attested-review-wave.md`.
- Preserved insight: Reopen a previously closed GitHub issue with a preserved local plan, rewrite it into a conservative draft, and drive iterative attested adversarial review waves until it is truly approval-ready.

### `single-terminal-gh-issue-prompts`

- Former skill demoted to `references/single-terminal-gh-issue-prompts.md`.
- Preserved insight: Generate live issue-specific Claude prompts for a single terminal, with repo-aware path contracts and plan-gate safety checks.

### `plan-resubmit-wave-prompts`

- Former skill demoted to `references/plan-resubmit-wave-prompts.md`.
- Preserved insight: Run a planning-only multi-terminal wave to harden blocked `status:plan-review` issues for fresh adversarial re-review, with zero implementation work and explicit path ownership.

### `parallel-plan-drafting-worktrees`

- Former skill demoted to `references/parallel-plan-drafting-worktrees.md`.
- Preserved insight: Draft multiple follow-up GitHub issue plans in parallel using isolated git worktrees plus background Claude Code print-mode runs, while keeping governance-safe boundaries and avoiding shared-file contention.

### `parallel-approved-issue-worktrees`

- Former skill demoted to `references/parallel-approved-issue-worktrees.md`.
- Preserved insight: Launch approved GitHub issue implementation in parallel using isolated git worktrees, committed execution-pack prompts, local plan-approved markers, and direct background Claude runs when delegate_task workers are unreliable for real repo writes.

### `plan-gated-issue-execution-wave`

- Former skill demoted to `references/plan-gated-issue-execution-wave.md`.
- Preserved insight: Execute a multi-issue architecture/planning wave in a plan-gated repo, then safely transition approved issues into implementation with file-based Claude prompts, local approval markers, subprocess monitoring, and cleanup handling for sandbox/hook edge cases.

### `continuous-planning-pipeline`

- Former skill demoted to `references/continuous-planning-pipeline.md`.
- Preserved insight: Maintain a standing day/night GitHub issue pipeline so agents always have planned, reviewed, user-approved work for overnight execution and next-day QA/approval.

### `plan-automation-contracts`

- Former skill demoted to `references/plan-automation-contracts.md`.
- Preserved insight: Tighten plans for scheduled/reporting workflows and multi-source detectors so adversarial review can verify runtime, publication, and normalization behavior.

### `next-wave-handoff-bundle`

- Former skill demoted to `references/next-wave-handoff-bundle.md`.
- Preserved insight: Build a docs-only execution handoff bundle after a completed implementation wave — follow-up issue drafts, scoped authorization note, deploy checklist, operator note, copy/paste command bundle, and incremental commit hygiene.
