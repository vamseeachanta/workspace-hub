# Archived Skill: `plan-rerun-state-revalidation`

Original path: `/home/vamsee/.hermes/skills/coordination/plan-rerun-state-revalidation`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/plan-rerun-state-revalidation`
Consolidation date: 2026-04-29

---

---
name: plan-rerun-state-revalidation
description: Revalidate live plan state before rerunning adversarial review or resuming from a handoff so review prompts do not encode stale approval/artifact assumptions.
version: 1.0.0
category: coordination
tags: [planning, review, governance, handoff, drift]
related_skills:
  - issue-planning-mode
  - session-start-routine
  - multi-provider-adversarial-review
---

# Plan Rerun State Revalidation

Use when resuming a plan-hardening loop from a handoff, or before launching a fresh adversarial rerun after prior review waves.

## Why this exists

Handoffs and stale plan summaries can be directionally right but factually outdated on critical governance points:
- a local `.planning/plan-approved/<issue>.md` marker may now exist
- the GitHub issue may still carry `status:plan-approved`
- `docs/plans/README.md` may still say `draft`
- newer `scripts/review/results/*plan-<issue>*` artifacts may exist, including self-review or superseding same-day artifacts

If you copy stale assumptions into a new review prompt, reviewers will correctly flag the prompt/plan narrative itself as wrong.

## Mandatory recheck set

Before trusting the handoff or writing a rerun prompt, re-verify all of these directly:

1. Live GitHub issue labels/state
   - `gh issue view <issue> --json labels,state,...`
2. Local approval marker
   - `.planning/plan-approved/<issue>.md`
3. Local plan index row
   - `docs/plans/README.md`
4. All existing review artifacts
   - `scripts/review/results/*plan-<issue>*`
5. Current plan header and `## Adversarial Review Summary`
6. Raw provider logs if the artifact history looks inconsistent
   - `.planning/quick/review-<issue>-*.out`

## Interpretation rules

- Do not say "no approval marker exists" until you check `.planning/plan-approved/<issue>.md`.
- Do not say "only the older review triad exists" until you list all `scripts/review/results/*plan-<issue>*` artifacts.
- If approval exists but the plan changed afterward, describe it as approval-state drift / superseded approval, not absence of approval.
- If a newer self-review artifact exists, do not present it as a substitute for external cross-provider review, but do surface it so the review-artifact trail stays truthful.
- If `docs/plans/README.md` disagrees with GitHub labels or the approval marker, treat README as lagging convenience state, not authority.

## Prompt-writing rule

When building the next adversarial-review prompt:
- only include claims you re-verified in the current session
- explicitly call out approval drift if present
- avoid absolute statements about missing markers/artifacts unless rechecked live
- prefer: "live issue is X, local marker is Y, plan header says Z; review this drift as part of the plan state"

## Recommended resume sequence

1. Read the handoff
2. Recheck the six-state set above
3. Compare any preserved todo/task list against live state; after context compaction, todos may be stale relative to already-completed commits/comments/labels
4. If the gate is already complete, do a narrow verification/cleanup pass only; do not rerun reviews, repost comments, or re-apply labels just because stale todos say they are pending
5. Patch the local plan/header/review summary to match current reality when live state proves drift remains
6. Generate the fresh review prompt from the patched draft only if a material re-review is still needed
7. Run provider reruns only when the current artifact trail is missing, stale, or blocking
8. Only after any needed rerun, decide whether GitHub labels/comments/markers need rollback or promotion

### Context-compaction resume guard

When resuming after a compressed handoff, treat the summary as evidence to verify, not as a command to replay. A preserved active todo list can lag behind completed operations. Before executing pending-looking steps, check:
- whether the claimed commit is already in `git log` / pushed to `origin/main`
- whether the final GitHub comment already exists
- whether labels already match the intended gate state
- whether README/plan/review artifacts already reflect the final state
- whether `.planning/plan-approved/<issue>.md` exists or is absent as expected

If all surfaces already agree, stop at verification and final reporting. Avoid duplicate GitHub comments, duplicate label churn, and unnecessary review reruns.

If a local-only session-state file (for example `.claude/state/session-signals/*.jsonl`) remains dirty after stash restoration and is unrelated to the issue gate, classify it as session churn rather than plan work; restore or stash it separately before finalizing so the planning gate stays clean.

## Next-step triage after a dirty handoff

When a handoff is already committed/pushed but the worktree is still dirty, do not jump straight to implementation. First classify the dirty surfaces:

- If GitHub, plan header, and `docs/plans/README.md` now agree on `status:plan-review`, and the only approval drift is a locally deleted stale `.planning/plan-approved/<issue>.md`, the next logical step is a narrow governance-sync commit.
- That commit should include only the issue's governance/review-sync surfaces: stale marker deletion, plan header/review-summary updates, plan-index row update, canonical review result artifacts, and any raw review logs/prompts that those artifacts cite and that the repo convention tracks.
- Avoid bundling unrelated dirty files from other issues, provider scorecards, or session-state churn unless the user explicitly asks for a broader cleanup commit.
- After the narrow sync commit is pushed, post or verify a GitHub comment that states the issue is in `status:plan-review`, stale approval was intentionally removed, and user approval is still required before `status:plan-approved` or implementation.
- Do not recreate an approval marker or start implementation merely because reviews converged to MINOR/APPROVE; explicit user approval is still the approval gate.

## Anti-patterns

- Reusing handoff language verbatim in the new review prompt
- Assuming lack of approval because the plan file says `draft`
- Ignoring newer same-day artifacts because older canonical files already exist
- Treating self-review artifacts as external approval evidence

## Minimal verification commands

```bash
gh issue view <issue> --json labels,state,url
ls .planning/plan-approved/<issue>.md
rg -n "^\| <issue> \|" docs/plans/README.md
find scripts/review/results -maxdepth 1 -type f | sort | grep "plan-<issue>"
```
