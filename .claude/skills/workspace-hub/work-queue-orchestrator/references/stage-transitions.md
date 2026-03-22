# Stage Transitions

## Group Boundaries

| Group | Stages | Runner Script |
|-------|--------|---------------|
| PLAN | 1-4 | `run-plan.sh` |
| REVIEW | 5-7 | `run-review.sh` |
| EXECUTE | 8-16 | `run-execute.sh` |
| CLOSE | 17-20 | `run-close.sh` |

## Chained Stages (Sequential in Single Prompt)

- **2 -> 3 -> 4:** Resource Intelligence -> Triage -> Plan Draft
- **8 -> 9:** Claim/Activation -> Routing

## Dispatch Entry Point

All processing starts via `scripts/work-queue/dispatch-run.sh WRK-NNN`.
Group runners must NOT be called directly without a dispatch breadcrumb.

## Parallelism

| Mode | Stages |
|------|--------|
| parallel-optional | 10 (Work Execution), 12 (TDD/Eval) |
| parallel | 5, 6, 13 (Reviews) |
| single-thread | All others |
