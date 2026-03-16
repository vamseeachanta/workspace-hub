---
name: core-planner-plan-output-format
description: 'Sub-skill of core-planner: Plan Output Format (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Plan Output Format (+1)

## Plan Output Format


```yaml
plan:
  objective: "Clear description of the goal"
  phases:
    - name: "Phase Name"
      tasks:
        - id: "task-1"
          description: "What needs to be done"
          agent: "Which agent should handle this"
          dependencies: ["task-ids"]

*See sub-skills for full details.*

## Task Decomposition Example


```yaml
# Example: Implement User Authentication
plan:
  objective: "Implement secure user authentication system"
  phases:
    - name: "Research & Design"
      tasks:
        - id: "auth-1"
          description: "Research authentication best practices"
          agent: "researcher"

*See sub-skills for full details.*
