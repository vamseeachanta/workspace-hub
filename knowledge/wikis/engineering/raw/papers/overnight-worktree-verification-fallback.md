# Archived Skill: `overnight-worktree-verification-fallback`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/overnight-worktree-verification-fallback`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/overnight-worktree-verification-fallback`
Consolidation date: 2026-04-29

---

---
name: overnight-worktree-verification-fallback
description: Verify overnight multi-worktree Claude batches when auto-sync, duplicate-lane convergence, and sandbox-blocked review create misleading local state or review provenance.
triggers:
  - Overnight Claude batch uses fresh worktrees plus auto-sync or hook-driven push behavior
  - Morning verification shows local worktree HEAD disagrees with origin/main
  - Two lanes may have converged on the same deterministic implementation
  - Planning-only worker produced review artifacts but could not run real cross-provider review
---

# Overnight worktree verification fallback

Use this after overnight parallel Claude runs in workspace-hub-style repos.

## Core problems this skill handles
1. A worker lands a commit on `origin/main`, but the isolated worktree remains at an older local `HEAD`.
2. A second worker verifies the same issue and correctly decides not to push because the change already landed elsewhere.
3. A planning-only worker cannot run `scripts/review/cross-review.sh` due to sandbox permissions, yet still writes review artifacts.
4. Morning verification can be misled by stale local worktrees, empty logs, or self-review artifacts that look like true cross-provider review.

## Verification protocol for each overnight lane

1. Check the background process outcome and save the worker's own summary.
2. Verify the canonical repo state, not just the worker worktree:
   - `git fetch origin main`
   - compare `HEAD` and `origin/main`
   - inspect the claimed landed commit on `origin/main`
3. If the worktree is stale, do not treat stale grep results as proof of failure.
   - verify the landed commit/content from the canonical repo or a fresh checkout
   - only then decide whether the issue truly landed
4. For implementation lanes, confirm all of:
   - commit hash exists on remote main
   - expected content is present
   - issue comment/closeout exists
   - issue state matches the evidence
5. For verification-only duplicate lanes:
   - accept `landed-but-blocked` or `already-landed` as a successful outcome if the worker correctly avoided a duplicate push
   - preserve the evidence comment rather than forcing a second implementation

## Auto-sync / hook-push gotcha

Some repos auto-push after commit via hooks or sync automation.

Observed failure mode:
- worker reports commit hash landed on `origin/main`
- explicit `git push origin HEAD:main` says `Everything up-to-date`
- local worktree `HEAD` is still the pre-run commit

Interpretation:
- the worker's local checkout may not have been fast-forwarded after the auto-push
- remote main is authoritative for morning verification

Required morning check:
```bash
git fetch origin main
git rev-parse --short HEAD
git rev-parse --short origin/main
git show --stat <claimed-commit>
```

## Duplicate-lane convergence rule

When two lanes target the same deterministic transformation:
- the first lane may land the change
- the second lane should fetch before editing
- if the second lane can prove origin/main is byte-identical to the approved transform, that lane should not push

Treat this as success, not wasted work, when the second lane:
- detects the landed state early
- avoids a duplicate commit
- posts verification evidence on the issue
- leaves the issue in the correct state (closed or still open if residual blockers remain)

## Sandboxed planning-review fallback rule

If a planning-only lane cannot run `scripts/review/cross-review.sh`:
- do NOT present the resulting artifacts as true cross-provider review
- every fallback artifact must contain a provenance note stating it is a single-author adversarial self-review
- every GitHub issue update must disclose that real cross-provider review is still required
- keep the issue in `status:plan-review`
- queue a real unsandboxed cross-review pass before any move to `status:plan-approved`

Acceptable fallback output:
- revised plan text
- self-review artifacts with provenance note
- issue comment summarizing what appears retired vs what still needs real review

Not acceptable:
- claiming Codex/Gemini/Claude review happened when only one author reviewed
- treating self-review artifacts as approval-equivalent

## Morning scoreboard template

For each lane classify as one of:
- `completed-and-closed`
- `landed-but-still-blocked`
- `already-landed-no-new-push`
- `planning-advanced-still-plan-review`
- `failed-needs-rerun`

Then include:
- issue number
- landed commit(s)
- current issue state
- evidence source (remote commit, CI run, GH comment, child issue)
- next action if still open

## Good outcomes from this pattern
- #2437-style: implementation landed on main, issue closed, child follow-ons created, stale worktree ignored after remote verification
- #2442-style: P1/P2 already landed elsewhere, verifier lane proves byte-identical state and leaves issue open with residual blocker follow-up
- #2441/#2443/#2444-style: plans improved, but artifacts explicitly disclose self-review provenance and issues remain in `status:plan-review`

## Anti-patterns to avoid
- trusting stale local worktree grep over `origin/main`
- closing an issue because a worker claimed success without verifying remote content and issue comments
- treating self-review `-r3.md` artifacts as cross-provider approval evidence
- creating duplicate implementation commits when a deterministic change already landed
