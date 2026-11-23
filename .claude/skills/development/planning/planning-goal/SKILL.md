---
name: planning-goal
description: Goal-Oriented Action Planning (GOAP) specialist that dynamically creates
  intelligent plans to achieve complex objectives. Use for multi-step tasks with dependencies,
  adaptive replanning, complex deployment workflows, or when a high-level goal needs
  systematic breakdown into achievable actions.
version: 1.0.0
category: development
type: hybrid
capabilities:
- dynamic_planning
- precondition_analysis
- effect_prediction
- adaptive_replanning
- goal_decomposition
- cost_optimization
- novel_solution_discovery
- mixed_execution
tools:
- Read
- Write
- Bash
- Task
related_skills:
- planning-code-goal
hooks:
  pre: 'echo "Starting GOAP planning session..."

    echo "Analyzing current state and goal state..."

    '
  post: 'echo "GOAP planning complete - action sequence generated"

    '
requires: []
tags: []
---

# Planning Goal

## Quick Start

```bash
# Define goal state and current state
Current: {code_written: true, tests_written: false, deployed: false}
Goal: {deployed: true, monitoring: true}

# GOAP generates optimal plan:
1. write_tests -> tests_written: true
2. run_tests -> tests_passed: true
3. build_application -> built: true
4. deploy_application -> deployed: true
5. setup_monitoring -> monitoring: true
```

## When to Use

- Complex multi-step tasks with dependencies requiring optimal ordering
- High-level goals needing systematic breakdown into concrete actions
- Deployment workflows with many prerequisites
- Refactoring projects requiring incremental, safe transformations
- Any task where conditions must be met before actions can execute

## Prerequisites

- Clear definition of current state (what is true now)
- Clear definition of goal state (what should be true)
- Available actions with known preconditions and effects

## References

- [GOAP in Game AI](https://en.wikipedia.org/wiki/Goal-oriented_action_planning)
- [A* Search Algorithm](https://en.wikipedia.org/wiki/A*_search_algorithm)
- [OODA Loop](https://en.wikipedia.org/wiki/OODA_loop)

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from goal-planner agent

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [GOAP Algorithm (+2)](goap-algorithm/SKILL.md)
- [Implementation Pattern](implementation-pattern/SKILL.md)
- [Configuration](configuration/SKILL.md)
- [Example 1: Software Deployment (+2)](example-1-software-deployment/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+2)](mcp-tools/SKILL.md)
