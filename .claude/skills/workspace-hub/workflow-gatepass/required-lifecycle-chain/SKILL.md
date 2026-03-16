---
name: workflow-gatepass-required-lifecycle-chain
description: 'Sub-skill of workflow-gatepass: Required Lifecycle Chain.'
version: 1.0.6
category: workspace-hub
type: reference
scripts_exempt: true
---

# Required Lifecycle Chain

## Required Lifecycle Chain


1. Capture. **Stage 1 exit gate:** `user-review-capture.yaml` with `scope_approved: true`
   required before Stage 2. Route A may use `n/a: true` with non-empty `n/a_reason`.
2. Resource Intelligence.
3. Triage.
4. Plan Draft.
5. User Review - Plan (Draft) as an interactive agent-user plan dialogue within this stage:
   - ask tough clarifying questions,
   - challenge weak assumptions and surface tradeoffs,
   - think hard and research hard before progressing,
   - research tests/evals from available Resource Intelligence and Document
     Intelligence artifacts,
   - seek user review of proposed tests/evals and ask user to add/adjust
     tests/evals before progression,
   - open completed HTML in default browser and push review docs to `origin`.
   - **HARD GATE**: Stage 5→6 is enforced by canonical checker (WRK-1017):
     `uv run --no-project python scripts/work-queue/verify-gate-evidence.py --stage5-check WRK-NNN`
     All official Stage 6 entrypoints call this checker. Activation controlled by
     `scripts/work-queue/stage5-gate-config.yaml`.
6. Cross-Review.
7. User Review - Plan (Final) with completed HTML opened in default browser and review docs pushed to `origin`.
8. Claim / Activation.
9. Work-Queue Routing Skill (`/work` path).
10. Work Execution.
11. Artifact Generation.
12. TDD / Eval.
13. Agent Cross-Review (implementation evidence review).
14. Verify Gate Evidence.
15. Future Work Synthesis.
16. Resource Intelligence Update.
17. User Review - Implementation (close package) with completed HTML opened in default browser and review docs pushed to `origin`.
18. Reclaim (conditional when continuity breaks).
19. Close.
20. Archive.
