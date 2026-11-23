---
name: planning-goal-example-1-software-deployment
description: 'Sub-skill of planning-goal: Example 1: Software Deployment (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Example 1: Software Deployment (+2)

## Example 1: Software Deployment


```yaml
current_state:
  code_written: true
  tests_written: false
  tests_passed: false
  built: false
  deployed: false
  monitoring: false

goal_state:

*See sub-skills for full details.*

## Example 2: Complex Refactoring


```yaml
current_state:
  legacy_code: true
  documented: false
  tested: false
  refactored: false

goal_state:
  refactored: true
  tested: true

*See sub-skills for full details.*

## Example 3: OODA Loop Monitoring


```typescript
// Observe-Orient-Decide-Act loop during execution
async function executeWithOODA(plan: Plan): Promise<Result> {
  for (const action of plan.actions) {
    // OBSERVE: Check current state
    const currentState = await observeState();

    // ORIENT: Analyze deviations
    const deviation = analyzeDeviation(currentState, expectedState);


*See sub-skills for full details.*
