---
name: github-swarm-issue-issue-templates-for-swarms
description: 'Sub-skill of github-swarm-issue: Issue Templates for Swarms.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Issue Templates for Swarms

## Issue Templates for Swarms


```yaml
# .github/ISSUE_TEMPLATE/swarm-task.yml
name: Swarm Task
description: Create a task for AI swarm processing
body:
  - type: dropdown
    id: topology
    attributes:
      label: Swarm Topology
      options:
        - mesh (collaborative)
        - hierarchical (structured)
        - ring (sequential)
        - star (centralized)
    validations:
      required: true

  - type: input
    id: agents
    attributes:
      label: Required Agents
      placeholder: "coder, tester, analyst"

  - type: textarea
    id: description

*See sub-skills for full details.*
