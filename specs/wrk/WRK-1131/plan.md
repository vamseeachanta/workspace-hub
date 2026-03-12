# WRK-1131 Plan — Feature Layer Process

## Mission
Implement the feature WRK lifecycle process: stage contracts, workflow skill updates,
validate-queue-state.sh, close-item.sh guard, whats-next.sh bypass, and new-feature.sh
coordinating status rewrite.

## Acceptance Criteria

| # | Criterion |
|---|-----------|
| AC1 | stage-09-routing.yaml has feature_routing: block documenting Step 9b |
| AC2 | close-item.sh guards type:feature close with feature-close-check.sh |
| AC3 | stage-07-user-review-plan-final.yaml references feature-decomposition.yaml |
| AC4 | validate-queue-state.sh accepts coordinating as valid status |
| AC5 | work-queue-workflow SKILL.md has Feature WRK Lifecycle section |
| AC6 | whats-next.sh bypasses category filter for coordinating feature WRKs |
| P1  | new-feature.sh sets status:coordinating after scaffolding children |

## Tests / Evals

| what | type | expected |
|------|------|----------|
| stage-09 feature_routing key | happy | PASS |
| validate-queue-state coordinating fixture | happy | no invalid status error |
| feature-close-check exits 1 when child unarchived | edge | exit 1 |
| whats-next bypasses --category for coordinating | happy | WRK appears |
| new-feature.sh sets coordinating | happy | status:coordinating in frontmatter |
