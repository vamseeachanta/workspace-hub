# WRK-642 Claude Test Matrix

| Case | Payload | Prompt | Invocation | Timeout | Goal |
|---|---|---|---|---|---|
| C1 | minimal-schema-target.md | strict-reviewer-prompt.md | direct claude -p | 30s | Control case: minimal valid review |
| C2 | compact-wrk-624-review-input.md | strict-reviewer-prompt.md | direct claude -p | 30s | Compact targeted review |
| C3 | compact-wrk-624-review-input.md | plan-review.md | submit-to-claude.sh | 30s | Wrapper with compact payload |
| C4 | specs/wrk/WRK-624/plan.md | strict-reviewer-prompt.md | direct claude -p | 30s | Full payload with strict prompt |
| C5 | specs/wrk/WRK-624/plan.md | plan-review.md | submit-to-claude.sh | 30s | Current operational path |
| C6 | compact-wrk-624-review-input.md | strict-reviewer-prompt.md | submit-to-claude.sh | 60s | Compact payload with extra time |
