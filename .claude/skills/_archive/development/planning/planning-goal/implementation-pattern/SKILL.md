---
name: planning-goal-implementation-pattern
description: 'Sub-skill of planning-goal: Implementation Pattern.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Implementation Pattern

## Implementation Pattern


```typescript
interface WorldState {
  [key: string]: boolean | string | number;
}

interface Action {
  name: string;
  preconditions: Partial<WorldState>;
  effects: Partial<WorldState>;
  cost: number;
  execution: 'llm' | 'code' | 'hybrid';
  tools?: string[];
  fallback?: string;
}

interface Plan {
  actions: Action[];
  totalCost: number;
  estimatedTime: string;
}

function generatePlan(
  currentState: WorldState,
  goalState: WorldState,
  availableActions: Action[]
): Plan {
  // A* search through state space
  // Returns optimal action sequence
}
```
