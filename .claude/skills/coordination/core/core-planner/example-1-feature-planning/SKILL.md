---
name: core-planner-example-1-feature-planning
description: 'Sub-skill of core-planner: Example 1: Feature Planning (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Example 1: Feature Planning (+1)

## Example 1: Feature Planning


```javascript
// Spawn planner for feature breakdown
Task("Planner", "Create execution plan for user dashboard feature", "planner")

// Store plan in memory
  action: "store",
  key: "swarm/planner/task-breakdown",
  namespace: "coordination",
  value: JSON.stringify({
    main_task: "user-dashboard",

*See sub-skills for full details.*

## Example 2: Parallel Task Orchestration


```javascript
// Orchestrate parallel execution
  task: "Implement authentication system",
  strategy: "parallel",
  priority: "high",
  maxAgents: 5
}

// Monitor progress
  taskId: "auth-implementation"
}
```
