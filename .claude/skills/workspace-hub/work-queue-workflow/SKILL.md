---
name: work-queue-workflow
description: >
  Explicit entrypoint skill for the WRK work-queue lifecycle workflow. Points to
  the canonical work-queue process and gatepass enforcement sequence.
version: 1.0.2
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
   Stage 5 is an agent-user interactive plan-mode session:
   - ask tough clarifying questions,
   - challenge weak assumptions and surface tradeoffs,
   - think hard and research hard before allowing progression to stage 6,
   - research tests/evals from available Resource Intelligence and Document
     Intelligence artifacts,
   - seek user review of proposed tests/evals and ask user to add/adjust
     tests/evals before moving forward.
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
