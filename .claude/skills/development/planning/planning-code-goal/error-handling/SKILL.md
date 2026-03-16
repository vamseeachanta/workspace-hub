---
name: planning-code-goal-error-handling
description: 'Sub-skill of planning-code-goal: Error Handling.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Goal Infeasibility


```typescript
// Goal cannot be achieved with available resources
if (!canAchieveGoal(currentState, goalState, constraints)) {
  // Suggest achievable subset
  const achievableGoal = findMaximalAchievableSubset(goalState);
  console.log(`Full goal not achievable. Suggested: ${achievableGoal}`);

  // Identify blocking constraints
  const blockers = identifyBlockers(goalState);
  console.log(`Blocked by: ${blockers}`);
}
```
### Phase Failures


```typescript
// SPARC phase did not complete successfully
if (phaseResult.failed) {
  // Identify specific failures
  const failures = phaseResult.failedCriteria;

  // Attempt retry with adjusted parameters
  if (canRetry(failures)) {
    await retryPhase(phase, adjustedConfig);
  } else {
    // Replan from current state
    await replanFromPhase(phase);
  }
}
```
