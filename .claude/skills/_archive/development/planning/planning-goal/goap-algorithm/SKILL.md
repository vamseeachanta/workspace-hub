---
name: planning-goal-goap-algorithm
description: 'Sub-skill of planning-goal: GOAP Algorithm (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# GOAP Algorithm (+2)

## GOAP Algorithm


GOAP uses A* pathfinding through state space:

1. **State Space**: All possible combinations of world facts
2. **Actions**: Transforms with preconditions and effects
3. **Heuristic**: Estimated cost to reach goal from current state
4. **Optimal Path**: Lowest-cost action sequence achieving goal

## Action Definition


```
Action: action_name
  Preconditions: {condition1: true, condition2: value}
  Effects: {new_condition: true, changed_value: new_value}
  Cost: numeric_value
  Execution: llm|code|hybrid
  Fallback: alternative_action
```

## Execution Modes


| Mode | Description | Use Case |
|------|-------------|----------|
| Focused | Direct action execution | Specific requested actions |
| Closed | Single-domain planning | Defined action set |
| Open | Creative problem solving | Novel solution discovery |
