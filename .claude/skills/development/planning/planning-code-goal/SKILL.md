---
name: planning-code-goal
description: Code-centric Goal-Oriented Action Planning integrated with SPARC methodology.
  Use for feature implementation planning, performance optimization goals, testing
  strategy development, or any software development objective requiring systematic
  breakdown with measurable success criteria.
version: 1.0.0
category: development
type: hybrid
capabilities:
- feature_implementation_planning
- performance_optimization
- testing_strategy_design
- sparc_integration
- milestone_tracking
- success_metrics
- tdd_workflow
- api_development
tools:
- Read
- Write
- Bash
- Task
related_skills:
- planning-goal
- sparc-workflow
- testing-tdd-london
hooks:
  pre: 'echo "Starting SPARC-GOAP code planning session..."

    echo "Mapping SPARC phases to GOAP milestones..."

    '
  post: 'echo "Code goal planning complete - milestones defined"

    '
requires: []
see_also:
- planning-code-goal-sparc-phases-in-goal-planning
- planning-code-goal-implementation-pattern
- planning-code-goal-code-quality-metrics
- planning-code-goal-mcp-tools
tags: []
---

# Planning Code Goal

## Quick Start

```bash
# Define code goal
Goal: Implement OAuth2 authentication

# SPARC-GOAP generates phased plan:
Phase 1 (Specification): Define requirements, acceptance criteria
Phase 2 (Pseudocode): Design algorithms, state machines
Phase 3 (Architecture): Design components, API contracts
Phase 4 (Refinement): TDD implementation cycles
Phase 5 (Completion): Integration, validation, deployment

# Execute with SPARC commands
```

## When to Use

- Feature implementation requiring systematic breakdown
- Performance optimization with measurable targets
- Testing strategy development with coverage goals
- API development with clear contract definitions
- Database evolution with migration planning
- Technical debt reduction with incremental milestones

## Prerequisites

- Understanding of SPARC methodology phases
- Clear definition of desired outcome
- Access to codebase for state analysis
- Measurable success criteria

## References

- [GOAP in Game AI](https://en.wikipedia.org/wiki/Goal-oriented_action_planning)
- [TDD Best Practices](https://martinfowler.com/bliki/TestDrivenDevelopment.html)

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from code-goal-planner agent

## Sub-Skills

- [Configuration](configuration/SKILL.md)
- [Example 1: Feature Implementation Plan (+2)](example-1-feature-implementation-plan/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [SPARC Phases in Goal Planning (+2)](sparc-phases-in-goal-planning/SKILL.md)
- [Implementation Pattern](implementation-pattern/SKILL.md)
- [Code Quality Metrics (+2)](code-quality-metrics/SKILL.md)
- [MCP Tools (+2)](mcp-tools/SKILL.md)
