---
name: sparc-refinement
description: SPARC Refinement phase specialist for iterative improvement through TDD,
  code optimization, refactoring, performance tuning, and quality improvement
version: 1.0.0
category: development
type: hybrid
capabilities:
- code_optimization
- test_development
- refactoring
- performance_tuning
- quality_improvement
tools:
- Read
- Write
- Edit
- Grep
- Glob
- Bash
related_skills:
- sparc-specification
- sparc-pseudocode
- sparc-architecture
hooks:
  pre: 'echo "SPARC Refinement phase initiated"

    memory_store "sparc_phase" "refinement"

    # Run initial tests

    npm test --if-present || echo "No tests yet"

    '
  post: 'echo "Refinement phase complete"

    # Run final test suite

    npm test || echo "Tests need attention"

    memory_store "refine_complete_$(date +%s)" "Code refined and tested"

    '
requires: []
see_also:
- sparc-refinement-sparc-refinement-phase
- sparc-refinement-red-phase-write-failing-tests
- sparc-refinement-metrics-success-criteria
- sparc-refinement-mcp-tools
tags: []
---

# Sparc Refinement

## Quick Start

```bash
# Invoke SPARC Refinement/TDD phase

# Or directly in Claude Code
# "Use SPARC refinement to implement login with TDD approach"
```

## When to Use

- Implementing features using Test-Driven Development (TDD)
- Refactoring code while maintaining test coverage
- Optimizing performance of existing code
- Improving error handling and resilience
- Enhancing code quality and documentation

## Prerequisites

- Completed architecture phase with clear component design
- Testing framework configured (Jest, pytest, etc.)
- Understanding of TDD red-green-refactor cycle
- Knowledge of code quality metrics

## References

- [Test-Driven Development](https://martinfowler.com/bliki/TestDrivenDevelopment.html)
- [Refactoring Guru](https://refactoring.guru/)
- [Jest Documentation](https://jestjs.io/docs/getting-started)

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from agent to skill format

## Sub-Skills

- [Configuration](configuration/SKILL.md)
- [Example 1: Performance Optimization (+2)](example-1-performance-optimization/SKILL.md)
- [Example 4: Complexity Reduction](example-4-complexity-reduction/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [SPARC Refinement Phase (+1)](sparc-refinement-phase/SKILL.md)
- [Red Phase - Write Failing Tests (+2)](red-phase-write-failing-tests/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+2)](mcp-tools/SKILL.md)
