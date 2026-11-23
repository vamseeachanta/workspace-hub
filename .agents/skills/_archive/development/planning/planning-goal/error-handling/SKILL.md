---
name: planning-goal-error-handling
description: 'Sub-skill of planning-goal: Error Handling.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Plan Generation Failures


```typescript
// No valid path exists
if (!plan) {
  // Analyze which preconditions cannot be satisfied
  const unsatisfiable = findUnsatisfiablePreconditions(goalState);
  console.error(`Cannot reach goal: missing ${unsatisfiable}`);

  // Suggest partial goals that ARE achievable
  const partialGoals = suggestAchievableSubsets(goalState);
}
```

### Execution Failures


```typescript
// Action failed during execution
if (actionResult.failed) {
  // Check if alternative action available
  if (action.fallback) {
    await executeAction(action.fallback);
  } else {
    // Replan from current state
    const newPlan = await replan(currentState, goalState);
  }
}
```
