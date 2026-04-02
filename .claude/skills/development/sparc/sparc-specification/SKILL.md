---
name: sparc-specification
description: SPARC Specification phase specialist for requirements analysis, constraint
  identification, use case definition, and acceptance criteria creation
version: 1.0.0
category: development
type: hybrid
capabilities:
- requirements_gathering
- constraint_analysis
- acceptance_criteria
- scope_definition
- stakeholder_analysis
tools:
- Read
- Write
- Edit
- Grep
- Glob
related_skills:
- sparc-pseudocode
- sparc-architecture
- sparc-refinement
hooks:
  pre: 'echo "SPARC Specification phase initiated"

    memory_store "sparc_phase" "specification"

    memory_store "spec_start_$(date +%s)" "Task: $TASK"

    '
  post: 'echo "Specification phase complete"

    memory_store "spec_complete_$(date +%s)" "Specification documented"

    '
requires: []
tags: []
---

# Sparc Specification

## Quick Start

```bash
# Invoke SPARC Specification phase

# Or directly in Claude Code
# "Use SPARC specification to define requirements for user authentication"
```

## When to Use

- Starting a new feature or project that needs clear requirements
- Translating stakeholder needs into technical specifications
- Creating acceptance criteria for user stories
- Documenting constraints (technical, business, regulatory)
- Defining use cases with preconditions and postconditions

## Prerequisites

- Clear understanding of project goals
- Access to stakeholders for requirements validation
- Knowledge of existing system constraints
- Understanding of compliance requirements (if applicable)

## References

- [Gherkin Syntax](https://cucumber.io/docs/gherkin/)
- [IEEE 830 SRS Standard](https://standards.ieee.org/)

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from agent to skill format

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [SPARC Specification Phase (+1)](sparc-specification-phase/SKILL.md)
- [Requirements Document Structure (+3)](requirements-document-structure/SKILL.md)
- [Configuration](configuration/SKILL.md)
- [Example 1: API Requirements](example-1-api-requirements/SKILL.md)
- [1.1 Purpose (+2)](11-purpose/SKILL.md)
- [2.1 Authentication (+1)](21-authentication/SKILL.md)
- [3.1 Performance (+2)](31-performance/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+2)](mcp-tools/SKILL.md)
