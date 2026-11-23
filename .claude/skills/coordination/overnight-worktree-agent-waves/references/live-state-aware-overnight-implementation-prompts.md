# Archived Skill: `live-state-aware-overnight-implementation-prompts`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/live-state-aware-overnight-implementation-prompts`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/live-state-aware-overnight-implementation-prompts`
Consolidation date: 2026-04-29

---

---
name: live-state-aware-overnight-implementation-prompts
description: Design overnight implementation prompts that begin with a live repo/CI precheck so workers continue from partial progress instead of replaying stale handoffs.
triggers:
  - Overnight batch includes implementation-ready GitHub issues
  - Prior sessions may already have landed part of the approved fix
  - CI-health issues are being continued across multiple sessions or phases
---

# Live-state-aware overnight implementation prompts

Use this when preparing an overnight implementation batch for issues that are already `status:plan-approved`, especially CI-health issues where one repair phase may already be on `main`.

## Problem this solves
A handoff or approved plan can be stale within hours. Another session may already have:
- landed Phase 1 of a multi-phase fix
- partially edited the target workflow/config/file set
- changed the current failure mode in CI
- converted a `0 jobs / 0s` startup failure into a real downstream test/install failure

If the overnight worker blindly replays the stale prompt, it wastes tokens, risks conflicts, and can overwrite correct progress.

## Required prompt pattern
For each implementation stream, make the worker start with an explicit precheck before editing.

Require the prompt to say:
1. inspect recent commits (`git log --oneline -N`)
2. inspect current target-file contents for whether prior phases already landed
3. inspect recent GitHub Actions runs/logs for the latest real blocker
4. classify the issue state as one of:
   - `already done`
   - `partially done`
   - `not done`
5. only apply the missing delta if the issue is `partially done`
6. close from the verification-first path if it is already done

## Best-fit cases
- CI-health issues with staged fixes (Phase 1 parse/startup unblock, Phase 2 install/test unblock, Phase 3 full green)
- repos with many parallel sessions or auto-sync churn
- child repos inside a workspace-hub umbrella where repo state diverges from hub handoff docs
- issues where the prompt references exact fix sites that may already have changed

## Prompt wording to include
Recommended language:

- "Start from live repo state rather than the stale handoff."
- "Before any edit, perform the already-done precheck from live repo + live GitHub Actions."
- "Determine explicitly: already done, partially done, or not done."
- "If partial progress already landed, apply only the missing delta instead of replaying the plan verbatim."

## What the worker should inspect
Minimum live-state sources:
- `git log --oneline -5` or similar
- direct inspection/grep of the target file(s)
- `gh run list --repo <owner/repo> --branch main --limit 5`
- `gh run view <run-id> --log` for the newest failed run when CI is involved

## Execution rule
After the precheck:
- If `already done`: gather proof, post the GitHub evidence comment, and close if acceptance is satisfied.
- If `partially done`: implement only the remaining delta, validate, push, and post the new evidence.
- If `not done`: proceed with the approved plan normally.

## Why this matters
The most common overnight failure mode is not "bad implementation" but "good implementation against yesterday's state." This pattern turns stale handoffs into continuation prompts instead of replay prompts.
