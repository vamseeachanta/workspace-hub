# Archived Skill: `planning-lane-cross-review-permission-fallback`

Original path: `/home/vamsee/.hermes/skills/workspace-hub-learned/planning-lane-cross-review-permission-fallback`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/workspace-hub-learned/planning-lane-cross-review-permission-fallback`
Consolidation date: 2026-04-29

---

---
name: planning-lane-cross-review-permission-fallback
description: Handle overnight planning-only lanes where plan revision/editing works but real cross-provider review dispatch is permission-blocked.
triggers:
  - Overnight/planning-only Claude lane can edit plan files and post issue comments
  - cross-review dispatch is blocked by sandbox/permission policy
  - Worker is tempted to substitute self-review for true cross-provider review
---

# Planning-lane cross-review permission fallback

Use this when a planning-only overnight worker can successfully revise plans but cannot run the repo's real cross-provider review machinery.

## Problem pattern

Observed in the 2026-04-21 CI batch for workspace-hub issues #2441, #2443, and #2444:
- the worker could revise `docs/plans/...` files
- the worker could write `scripts/review/results/...-r3.md`
- the worker could post GitHub comments
- but permission policy blocked `scripts/review/cross-review.sh`

That means the worker can produce review-shaped artifacts, but not actual Codex/Gemini/Claude cross-provider evidence.

## Required response

1. Do NOT pretend the fallback artifacts are real cross-provider review.
2. If you write fallback review artifacts, add explicit provenance language in every artifact.
3. In every issue comment, disclose that the artifacts are single-author adversarial self-review, not dispatched multi-provider review.
4. Keep the issue in `status:plan-review`.
5. Do NOT create `.planning/plan-approved/*` markers.
6. Recommend a follow-up unsandboxed review wave before any move to `status:plan-approved`.

## Minimum provenance language

Use wording equivalent to:
- "Provenance note: this artifact is a Claude-authored single-author adversarial self-review because `scripts/review/cross-review.sh` was permission-blocked in this session. It is interim signal, not real cross-provider review evidence."

## What counts as acceptable output

Acceptable overnight output:
- revised plan files
- provenance-tagged `-rN.md` review artifacts
- issue comments summarizing current blockers and explicitly disclosing the degraded review mode
- a ranking of which plans are closest to approval, with the caveat that real cross-provider review is still required

Not acceptable:
- calling the fallback artifacts "Wave N cross-provider review" without qualification
- moving the issue to `status:plan-approved`
- telling the user the plan is approval-ready based only on the fallback artifacts

## Reusable operator note

If this fallback happens, the next clean step is:
```bash
bash scripts/review/cross-review.sh docs/plans/<plan-file>.md all --type plan
```
run from an unsandboxed session with permission to invoke the provider dispatchers.

## Why this matters

The fallback self-review can still be useful for tightening plans overnight, but it must not silently downgrade the repo's governance standard. The right pattern is: preserve momentum, disclose provenance, and defer approval until real cross-provider evidence exists.
