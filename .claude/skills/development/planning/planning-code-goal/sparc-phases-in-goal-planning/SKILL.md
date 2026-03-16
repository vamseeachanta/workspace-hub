---
name: planning-code-goal-sparc-phases-in-goal-planning
description: 'Sub-skill of planning-code-goal: SPARC Phases in Goal Planning (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# SPARC Phases in Goal Planning (+2)

## SPARC Phases in Goal Planning


| Phase | GOAP Role | Deliverables |
|-------|-----------|--------------|
| Specification | Define goal state | Requirements, acceptance criteria |
| Pseudocode | Plan actions | Algorithms, state transitions |
| Architecture | Structure solution | Components, interfaces |
| Refinement | Iterate with TDD | Tests, implementation |
| Completion | Validate goal | Deployment, metrics |

## Code State Analysis


```javascript
current_state = {
  test_coverage: 45,
  performance_score: 'C',
  tech_debt_hours: 120,
  features_complete: ['auth', 'user-mgmt'],
  bugs_open: 23
}

goal_state = {

*See sub-skills for full details.*

## Milestone Definition


```typescript
interface CodeMilestone {
  id: string;
  description: string;
  sparc_phase: 'specification' | 'pseudocode' | 'architecture' | 'refinement' | 'completion';
  preconditions: string[];
  deliverables: string[];
  success_criteria: Metric[];
  estimated_hours: number;
  dependencies: string[];
}
```
