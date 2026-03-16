---
name: core-planner
description: Strategic planning and task orchestration agent for breaking down complex
  tasks into actionable execution plans
version: 1.0.0
category: coordination
type: agent
capabilities:
- task_decomposition
- dependency_analysis
- resource_allocation
- timeline_estimation
- risk_assessment
tools:
- Read
- Glob
- Grep
- TodoWrite
related_skills:
- core-coder
- core-tester
- core-reviewer
- core-researcher
hooks:
  pre: "echo \"\U0001F3AF Planning agent activated for: $TASK\"\nmemory_store \"planner_start_$(date\
    \ +%s)\" \"Started planning: $TASK\"\n"
  post: "echo \"\u2705 Planning complete\"\nmemory_store \"planner_end_$(date +%s)\"\
    \ \"Completed planning: $TASK\"\n"
requires: []
see_also:
- core-planner-planning-process
- core-planner-plan-output-format
- core-planner-priority-levels
- core-planner-example-1-feature-planning
- core-planner-metrics-success-criteria
- core-planner-mcp-tools
- core-planner-collaboration-guidelines
tags: []
---

# Core Planner

## Quick Start

```javascript
// Spawn planner agent
Task("Planner agent", "Break down [task] into actionable subtasks with dependencies", "planner")

// Orchestrate task execution
  task: "Implement [feature]",
  strategy: "parallel",
  priority: "high",
  maxAgents: 5
}
```

## When to Use

- Breaking down complex features into tasks
- Creating sprint/iteration plans
- Mapping task dependencies
- Allocating resources and agents
- Risk assessment and mitigation planning

## Prerequisites

- Clear understanding of project goals
- Access to project requirements/specifications
- Knowledge of available agents and their capabilities
- Understanding of technical constraints

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from planner.md agent

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Planning Process (+1)](planning-process/SKILL.md)
- [Plan Output Format (+1)](plan-output-format/SKILL.md)
- [Priority Levels (+1)](priority-levels/SKILL.md)
- [Example 1: Feature Planning (+1)](example-1-feature-planning/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+2)](mcp-tools/SKILL.md)
- [Collaboration Guidelines](collaboration-guidelines/SKILL.md)
