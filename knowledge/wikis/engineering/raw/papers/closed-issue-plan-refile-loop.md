# Archived Skill: `closed-issue-plan-refile-loop`

Original path: `/home/vamsee/.hermes/skills/coordination/closed-issue-plan-refile-loop`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/coordination/closed-issue-plan-refile-loop`
Consolidation date: 2026-04-29

---

---
name: closed-issue-plan-refile-loop
description: Reopen and re-drive a previously closed GitHub plan issue after review/governance blockers are fixed, without prematurely restoring approval state.
version: 1.0.0
category: coordination
tags: [planning, github, review, governance, refile]
---

# Closed-Issue Plan Re-file Loop

Use when a plan issue was previously closed or parked because of review infrastructure limits, governance drift, or other meta blockers, and you need to revive it safely.

## When this fits
- A plan issue was closed with preserved artifacts
- A later infrastructure/governance fix makes re-review worthwhile
- You need to reopen the issue, revise the plan, run a fresh adversarial review wave, and avoid falsely surfacing it as approval-ready

## Core pattern

1. Recover prior state
- Read the preserved local plan
- Read prior review artifacts and closure/governance comments
- Verify live issue state with `gh issue view`
- Verify current repo reality for any facts the old plan depended on

2. Rewrite as a conservative re-file draft
- Keep the same canonical local plan file if it is still the source of truth
- Change the header/status to `draft`, not `plan-review`
- Add revision history explaining why the new draft exists
- Remove stale claims about prior issue state, missing artifacts, or old blocker assumptions
- Convert previous review findings into explicit plan sections/contracts instead of leaving them as comments only

3. Reopen the GitHub issue before fresh review
- Reopen with a comment explaining the re-file basis
- Reopening does NOT imply the plan is approval-ready

4. Run a fresh adversarial review wave immediately
- Generate new provider artifacts (at minimum Codex; Gemini if available)
- Treat fresh MAJOR findings as authoritative over the reopened state
- Expect iterative tightening; a reopened issue often still needs multiple passes

5. Keep governance state conservative until the review wave is green
- Do NOT restore `status:plan-review` just because the issue was reopened
- Do NOT recreate approval-ready posture while fresh review still returns MAJOR
- Post a governance comment summarizing the latest artifacts and current blocker themes
- Update `docs/plans/README.md` to reflect the reopened draft state, e.g. `draft (vN re-file in progress)`

6. Commit only the planning artifacts
- Stage explicit paths only
- Commit plan file + README row + new review artifacts together
- Push and verify `origin/main` contains the new planning state

## Practical lessons
- Reopening an issue is cheap; restoring approval-state labels is not. Separate those actions.
- Fresh review artifacts outrank stale closed-state summaries.
- A preserved plan file can remain the canonical path, but its header and README row must be updated to match the reopened draft reality.
- A GitHub comment linking fresh review artifacts is important so the live issue reflects why it is reopened yet still not approval-ready.

## Minimal verification
- `gh issue view NNN --json state,labels,comments`
- `git status --short`
- `git rev-parse HEAD origin/main`
- confirm new review artifact files exist
- confirm README row matches the reopened/draft state

## Example outcomes
Good end state after a first re-file pass:
- issue reopened
- local plan revised to `draft`
- fresh Codex/Gemini review artifacts added
- governance comment posted
- no `status:plan-review` label yet if MAJOR findings remain

Only after the fresh review wave is approval-ready should the issue advance back into the normal `status:plan-review` -> user approval flow.
