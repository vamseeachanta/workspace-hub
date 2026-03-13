# WRK Lifecycle Stages — Visual Reference

## Stage Flow (Mermaid)

```mermaid
flowchart TD
    S1["1 Capture"]:::hard
    S2["2 Resource Intelligence"]
    S3["3 Triage"]
    S4["4 Plan Draft"]
    S5["5 User Review — Plan Draft"]:::hard
    S6["6 Cross-Review"]
    S7["7 User Review — Plan Final"]:::hard
    S8["8 Claim / Activation"]
    S9["9 Work-Queue Routing"]
    S10["10 Work Execution"]
    S11["11 Artifact Generation"]
    S12["12 TDD / Eval"]
    S13["13 Agent Cross-Review"]
    S14["14 Verify Gate Evidence"]
    S15["15 Future Work Synthesis"]
    S16["16 Resource Intelligence Update"]
    S17["17 User Review — Close"]:::hard
    S18["18 Reclaim"]
    S19["19 Close"]
    S20["20 Archive"]

    S1 --> S2 --> S3 --> S4 --> S5
    S5 --> S6 --> S7
    S7 -->|"approved → auto-proceed 8-16"| S8
    S8 --> S9 --> S10 --> S11 --> S12
    S12 --> S13 --> S14 --> S15 --> S16
    S16 --> S17
    S17 --> S18 --> S19 --> S20

    classDef hard fill:#e74c3c,color:#fff,stroke:#c0392b,stroke-width:2px
    classDef default fill:#3498db,color:#fff,stroke:#2980b9
```

## Legend

| Color | Meaning |
|-------|---------|
| Red | **Hard gate** — agent MUST stop and wait for explicit user approval |
| Blue | Auto-proceed — agent continues without asking |

## Gate Details

| Hard Gate | Exit Artifact | Rule |
|-----------|--------------|------|
| Stage 1 | `user-review-capture.yaml` (`scope_approved: true`) | R-25 |
| Stage 5 | `user-review-plan-draft.yaml` | R-25 |
| Stage 7 | `plan-final-review.yaml` (`confirmed_by` human) | R-25 |
| Stage 17 | `user-review-close.yaml` | R-25 |

## Conditional Pause (R-27)

Any auto-proceed stage pauses if: P1 finding, scope change, or irreversible risk.

## Route Variants

- **Route A**: lighter execution (stages 10-12), one cross-review pass
- **Route B**: standard execution, multi-provider cross-review
- **Route C**: deeper execution/testing, stricter cross-review finding closure

All routes share the same 20-stage structure.

## Source Skills

- [`work-queue-workflow/SKILL.md`](../../skills/workspace-hub/work-queue-workflow/SKILL.md)
- [`workflow-gatepass/SKILL.md`](../../skills/workspace-hub/workflow-gatepass/SKILL.md)
