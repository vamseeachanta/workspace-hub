---
name: work-queue-workflow
description: >
  Explicit entrypoint skill for the WRK work-queue lifecycle workflow. Points to
  the canonical work-queue process and gatepass enforcement sequence.
version: 1.0.3
updated: 2026-03-05
category: workspace-hub
triggers:
  - work-queue workflow
  - wrk workflow
  - /work workflow
  - lifecycle workflow
related_skills:
  - coordination/workspace/work-queue
  - workspace-hub/workflow-gatepass
  - workspace-hub/workflow-html
  - workspace-hub/session-start
  - workspace-hub/session-end
capabilities:
  - workflow-entrypoint
  - lifecycle-routing
  - gatepass-handoff
requires:
  - .claude/work-queue/process.md
invoke: work-queue-workflow
---
# Work-Queue Workflow

This skill is a clear entrypoint for users who ask for the "work-queue workflow".
It delegates to canonical `work-queue` and `workflow-gatepass` contracts.

Operating principle: **humans steer, agents execute**.
Every stage should explicitly track whether a human decision is required.

## Start-to-Finish Chain

1. Run `session-start`.
2. Use `/work` to select/create the WRK item.
3. Ensure plan exists and user approval explicitly names WRK ID.
4. Run the canonical **20-stage lifecycle** (Capture -> Archive) from
   `workflow-gatepass`.
   At **stages 5, 7, 11, 17, 19** run `generate-html-review.py --type <artifact_type>`
   (see `workflow-html` SKILL for artifact types and section catalog).
   **STOP — Stage 5 is a BLOCKING interactive gate. Do NOT call `cross-review`
   (Stage 6), do NOT set `plan_reviewed: true`, and do NOT progress to Stage 7
   until the user has responded in this session with explicit approval or revision
   requests. Presenting the HTML artifact and waiting silently is NOT sufficient —
   the user must actively respond.**

   Stage 5 is an agent-user interactive plan-mode session:
   - Open the plan-draft HTML in the default browser (`xdg-open <html-path>`) AND
     push to origin BEFORE presenting any recommendation to the user.
   - Walk the draft plan section-by-section with the user — this is a dialogue,
     not a one-way artifact drop.
   - Ask tough clarifying questions; do not accept silence as approval.
   - Challenge weak assumptions and surface tradeoffs explicitly.
   - Think hard and research hard before allowing progression to stage 6.
   - Research tests/evals from available Resource Intelligence and Document
     Intelligence artifacts.
   - Seek user review of proposed tests/evals and ask user to add/adjust
     tests/evals before moving forward.
   - Write `assets/WRK-<id>/evidence/user-review-plan-draft.yaml` capturing all
     user decisions (scope in/out, acceptance-criteria changes, risks, approve-
     as-is vs revise-and-rerun). This artifact is required for gate verification.

   **Stage 5 checklist — ALL must be true before advancing to Stage 6:**
   - [ ] Plan HTML opened in browser (`xdg-open`)
   - [ ] HTML pushed to origin and publish evidence logged
   - [ ] Interactive walk-through completed section-by-section with user
   - [ ] User has responded (not just "ok" — explicit scope/criteria/risk decisions)
   - [ ] `user-review-plan-draft.yaml` written with decision log
   - [ ] Plan artifacts updated from user decisions

   Stage 5→6 transition is enforced by the canonical checker (WRK-1017):
   ```bash
   uv run --no-project python scripts/work-queue/verify-gate-evidence.py --stage5-check WRK-NNN
   ```
   Activation is controlled by `scripts/work-queue/stage5-gate-config.yaml`.
   All four official Stage 6 entrypoints (`plan.sh`, `cross-review.sh`, `claim-item.sh`,
   `close-item.sh`) call this checker and block on exit 1 (predicate fail) or exit 2
   (infra fail). Policy text and executable gate must stay aligned.

   User-review checkpoints (stages 5/7/17) must include explicit review of the
   HTML **Gate-Pass Stage Status** section (stage-by-stage table + summary) before
   presenting final recommendations to the user.
   User-review checkpoints (stages 5/7/17) must include default-browser open and
   origin publish evidence for the canonical warm-parchment HTML artifact.
5. Verify close gate evidence and integrated/repo tests (3-5 pass records).
6. Close and archive using queue scripts.

Do not use shortened lifecycle variants for execution governance. This entrypoint
must always resolve to the canonical 20-stage chain.

## Source of Truth

- Process contract: `.claude/work-queue/process.md`
- Execution workflow: `coordination/workspace/work-queue/SKILL.md`
- Gate enforcement: `workspace-hub/workflow-gatepass/SKILL.md`

## Version History

- **1.0.4** (2026-03-07): Contract alignment — link Stage 5 policy to canonical checker (WRK-1017)
  - Added executable gate reference: `verify-gate-evidence.py --stage5-check`
  - All four official Stage 6 entrypoints now listed as callers
- **1.0.3** (2026-03-05): Stage 5 enforced as hard blocking gate (WRK-1017)
  - Added STOP — BLOCK marker and explicit blocking language for Stage 5
  - Added Stage 5 checklist (6 items, all required before Stage 6)
  - Documented `user-review-plan-draft.yaml` as required gate-verification artifact
- **1.0.2** (2026-03-05): Initial captured version

## Practical Lessons (WRK-690)

- Always run the workflow through shared scripts (`session.sh`, `work.sh`,
  `plan.sh`, `execute.sh`, `review.sh`, close/archive scripts) so signal logs are
  consistent across orchestrators.
- Refresh weekly gate-analysis before presenting coverage conclusions:
  1) `build-session-gate-analysis.py` 2) `audit-session-signal-coverage.py`.
- Treat per-agent coverage gaps as workflow defects even if aggregate metrics pass.
- In multi-agent parallel execution, keep WRK boundaries strict: unrelated changes
  from other active agents are non-blocking and must be documented (not reverted)
  in the current WRK as out-of-scope side effects.
- Keep AGENTS concise and map-like; use repo-local docs as system-of-record.
- Favor mechanical enforcement (scripts/linters/tests) over prose-only rules.
- Throughput policy: fast merges are acceptable only with bounded-risk controls
  (rollback path, follow-up WRK capture, recurring cleanup/refactor runs).
