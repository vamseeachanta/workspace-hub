# Archived Skill: `approval-stage-plan-review-sweep`

Original path: `/home/vamsee/.hermes/skills/software-development/approval-stage-plan-review-sweep`
Archived into: `/home/vamsee/.hermes/skills/.archive/umbrella-2026-04-29/software-development/approval-stage-plan-review-sweep`
Consolidation date: 2026-04-29

---

---
name: approval-stage-plan-review-sweep
description: Run an approval-stage adversarial cross-review sweep across multiple GitHub issues, drafting any missing canonical plan artifacts before dispatching Codex/Gemini reviews.
version: 1.0.0
author: Hermes Agent
category: software-development
tags: [planning, review, adversarial, codex, gemini, github, governance]
---

# Approval-Stage Plan Review Sweep

Use when the user asks to adversarially cross-review multiple issues for approval readiness in one pass.

## Why this exists
A common failure mode in approval-stage sweeps is trying to review issue bodies or stale partial drafts directly, even when a canonical `docs/plans/...` artifact is missing. That produces low-value review churn and breaks the repo's planning workflow.

## Required preflight
For each target issue:
1. Verify the canonical local plan file exists under `docs/plans/`.
2. Verify the issue has an index row in `docs/plans/README.md`.
3. If the plan artifact is missing, draft the missing canonical plan first and add the README row before any provider review.
4. If the plan exists but the prompt file is stale, regenerate the review prompt from the current on-disk plan text.

Do not treat a raw GitHub issue body as approval-ready substitute for a missing plan artifact.

## Recommended workflow
1. Enumerate target issue numbers.
2. Check `docs/plans/` for matching issue plan files.
3. Check `docs/plans/README.md` for matching index rows.
4. Draft/index any missing plans.
5. Generate fresh per-issue prompt files in `.planning/quick/`.
6. Dispatch Codex and Gemini reviews in parallel using the repo's review wrappers:
   - `scripts/review/submit-to-codex.sh`
   - `scripts/review/submit-to-gemini.sh`
7. Save canonical artifacts under `scripts/review/results/YYYY-MM-DD-plan-<issue>-<provider>.md`.
8. Create a consolidated summary note listing verdicts and approval blockers.
9. If using Hermes `delegate_task` to parallelize a sweep, remember the default concurrency cap may be lower than the user's requested lane count. In this environment, `max_concurrent_children` was 3, so a requested 4-lane sweep had to be implemented as two top-level parallel calls (3-task batch + 1-task batch). Do not promise a single 4-task `delegate_task` call without checking the actual cap first.
10. After synthesizing the verdicts, post a short GitHub comment on each issue summarizing approval readiness and top blockers, then only surface links as "for approval" if the plan is genuinely approval-ready. If every issue is still MAJOR / not approval-ready, explicitly say there are no approval links yet.
11. When a plan finally converges, do one last bookkeeping pass before calling it approval-ready:
   - refresh the plan header `Review artifacts:` line to the latest converged timestamped artifact set
   - refresh the Artifact Map review-artifact rows to the same timestamped set
   - update the `Adversarial Review Summary` table + wave summary to the final converged verdicts
   - post a dedicated GitHub convergence comment with the final provider verdicts and the latest artifact links
   - if the user later approves the issue on GitHub, verify whether the matching local `.planning/plan-approved/<issue>.md` marker exists; create it if missing so GitHub and local approval state stay synchronized

## Prompt requirements
Every review prompt should explicitly say:
- reviewer is adversarial
- do not praise or restate
- approval requires affirmative verification
- cite exact file paths / plan sections / quoted claims
- treat attested evidence as authoritative when present
- focus on approval-stage readiness, not implementation style

## Output expectations
For each issue, capture:
- Codex verdict
- Gemini verdict
- overall status (`approval-ready` or `not approval-ready`)
- 3-5 top blocker themes

For the full sweep, save a consolidated note with:
- verdict table by issue/provider
- common blocker clusters
- recommended next action (redraft, rerun review, or move to `status:plan-review`)

## Practical rules
- A single `MAJOR` blocks approval-stage readiness.
- If both providers return `MAJOR`, do not post the plan for approval.
- If the plan itself already contains a prior `FAIL / re-draft required` review summary, treat that as a strong sign the draft must be rewritten before another approval push.
- Keep raw provider logs in `.planning/quick/` and canonical review artifacts in `scripts/review/results/`.
- Do NOT cite the current-wave review artifacts inside the plan as if they already prove the blockers are resolved. During the rerun, those files may still be empty or not yet regenerated, and reviewers can correctly flag that as misleading evidence. In the redraft, refer to those findings as prior-review inputs and say fresh external re-review is still pending.
- Do NOT make `remain in draft` part of the acceptance criteria for an approval-stage plan. That creates a gate contradiction: the same artifact is trying to be approval-ready while asserting that staying draft is success. Instead, keep the file status conservative as `draft`, but make the acceptance criteria about plan content; note separately that fresh external re-review is required before promotion to `status:plan-review`.
- Treat attestation scope narrowly. The plan-attestation block reliably proves issue state and file existence, but it does not automatically prove arbitrary file contents, quoted lines, or semantic claims unless those excerpts are actually embedded. Avoid writing `attested` content claims for line-level behavior unless the evidence block truly includes that content.
- When reviewers challenge broad globs like `.claude/rules/**` or other open-ended scan universes, prefer replacing them with explicit fixed file lists for the approval-stage draft. This makes the test surface falsifiable and avoids execution-time scope drift.
- If the issue title/scope is about one non-actionable family (for example transient worktree/scratch-path reads), do not let the plan silently pivot to a neighboring family (for example generated-site paths) without explicitly preserving and testing the original scope. Reviewers will treat that as scope hijack.

## Good fit
- Reviewing 2-10 related plan issues in one batch
- Approval-stage queue cleanup
- Governance sweeps where some issues have plan drift or missing artifacts

## Not for
- Implementation/code review after commits (use the general multi-provider review workflow)
- Single-issue planning from scratch when no review sweep is requested
