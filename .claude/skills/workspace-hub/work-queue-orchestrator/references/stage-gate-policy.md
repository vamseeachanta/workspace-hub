# Stage Gate Policy

## Hard Gates (Human Approval Required)

| Stage | Name | Exit Artifact | Mechanism |
|-------|------|---------------|-----------|
| 1 | Capture | `user-review-capture.yaml` (`scope_approved: true`) | pre_exit_hook |
| 5 | User Review - Plan Draft | `user-review-plan-draft.yaml` | human_gate field |
| 7 | User Review - Plan Final | `plan-final-review.yaml` (`confirmed_by` human) | human_gate field |
| 17 | User Review - Implementation | `user-review-close.yaml` | human_gate field |

Note: Stage 1 has `human_gate: false` in its contract but enforces approval via a `pre_exit_hook` (wait-for-approval.sh). Stages 5, 7, 17 use the `human_gate: true` field.

## Rules

- **R-25 (Hard gate):** Stages 1, 5, 7, 17 — agent MUST STOP and wait. Silence != approval.
- **R-26 (Continue):** After Stage 7 approval, execute Stages 8-16 without asking.
- **R-27 (Conditional pause):** Any auto-proceed stage with P1 finding, scope change, or irreversible risk — pause and await direction.

## Plan-Mode Gates

| Stage | When |
|-------|------|
| 4 Plan Draft | Before first lifecycle HTML write |
| 6 Cross-Review | Before synthesizing 3-provider verdicts |
| 10 Work Execution | Before implementation file writes |
| 13 Agent Cross-Review | Before recording implementation verdict |

## Deterministic Check

```bash
scripts/work-queue/is-human-gate.sh <N>   # exit 0=STOP, exit 1=CONTINUE
```
