---
name: sparc-workflow
description: Apply SPARC methodology (Specification, Pseudocode, Architecture, Refinement,
  Completion) for systematic development. Use for feature development, TDD workflows,
  and structured problem-solving.
version: 1.1.0
category: coordination
type: skill
capabilities:
- specification_analysis
- pseudocode_design
- architecture_design
- tdd_implementation
- production_completion
tools:
- Bash
- Read
- Write
- Edit
- Task
related_skills:
- agent-orchestration
- compliance-check
- repo-sync
hooks:
  pre: ''
  post: ''
requires: []
see_also:
- sparc-workflow-phase-overview
- sparc-workflow-purpose
- sparc-workflow-functional-requirements
- sparc-workflow-in-scope
- sparc-workflow-acceptance-criteria
- sparc-workflow-constraints
- sparc-workflow-specification-checklist
- sparc-workflow-purpose
- sparc-workflow-main-algorithm
- sparc-workflow-helper-functions
- sparc-workflow-error-handling
- sparc-workflow-edge-cases
- sparc-workflow-complexity-analysis
- sparc-workflow-purpose
- sparc-workflow-new-components
- sparc-workflow-interface-design
- sparc-workflow-data-flow
- sparc-workflow-internal
- sparc-workflow-file-structure
- sparc-workflow-purpose
- sparc-workflow-purpose
- sparc-workflow-code-quality
- sparc-workflow-documentation
- sparc-workflow-security
- sparc-workflow-performance
- sparc-workflow-deployment
- sparc-workflow-start-sparc-workflow
- sparc-workflow-sparc-file-locations
- sparc-workflow-execution-checklist
- sparc-workflow-creating-a-spec
- sparc-workflow-specification-phase-issues
- sparc-workflow-metrics-success-criteria
- sparc-workflow-mcp-tools
tags: []
---

# Sparc Workflow

## Quick Start

```bash
# Run full SPARC development cycle

# Run TDD-focused workflow

# List available SPARC modes
```

## When to Use

- Implementing a new feature from scratch
- Complex problem requiring structured analysis before coding
- Building production-quality code with comprehensive tests
- Refactoring existing code systematically
- API or UI development requiring clear specifications

## Prerequisites

- Understanding of TDD (Test-Driven Development)
- Project with `.agent-os/` directory structure
- Access to testing framework (pytest, jest, etc.)

## Overview

SPARC is a systematic methodology for software development that ensures quality through structured phases. Each phase builds on the previous, creating well-documented, well-tested code.

## Overview

[One paragraph describing the feature]

## References

- [Agent OS Create Spec](~/.agent-os/instructions/create-spec.md)
- [Agent OS Execute Tasks](~/.agent-os/instructions/execute-tasks.md)

---

## Version History

- **1.1.0** (2026-01-02): Upgraded to SKILL_TEMPLATE_v2 format - added Quick Start, When to Use, Execution Checklist, Error Handling, Metrics, Integration Points, MCP hooks
- **1.0.0** (2024-10-15): Initial release with 5 SPARC phases, TDD integration, Claude Flow support, Agent OS integration

## Sub-Skills

- [Specification (+4)](specification/SKILL.md)

## Sub-Skills

- [Phase Overview](phase-overview/SKILL.md)
- [Purpose (+2)](purpose/SKILL.md)
- [Functional Requirements (+1)](functional-requirements/SKILL.md)
- [In Scope (+1)](in-scope/SKILL.md)
- [Acceptance Criteria](acceptance-criteria/SKILL.md)
- [Constraints](constraints/SKILL.md)
- [Specification Checklist](specification-checklist/SKILL.md)
- [Purpose (+4)](purpose/SKILL.md)
- [Main Algorithm](main-algorithm/SKILL.md)
- [Helper Functions](helper-functions/SKILL.md)
- [Error Handling](error-handling/SKILL.md)
- [Edge Cases](edge-cases/SKILL.md)
- [Complexity Analysis](complexity-analysis/SKILL.md)
- [Purpose (+2)](purpose/SKILL.md)
- [New Components (+1)](new-components/SKILL.md)
- [Interface Design](interface-design/SKILL.md)
- [Data Flow](data-flow/SKILL.md)
- [Internal (+1)](internal/SKILL.md)
- [File Structure](file-structure/SKILL.md)
- [Purpose (+3)](purpose/SKILL.md)
- [Purpose (+1)](purpose/SKILL.md)
- [Code Quality](code-quality/SKILL.md)
- [Documentation](documentation/SKILL.md)
- [Security](security/SKILL.md)
- [Performance](performance/SKILL.md)
- [Deployment](deployment/SKILL.md)
- [Start SPARC Workflow (+2)](start-sparc-workflow/SKILL.md)
- [SPARC File Locations](sparc-file-locations/SKILL.md)
- [Execution Checklist](execution-checklist/SKILL.md)
- [Creating a Spec (+1)](creating-a-spec/SKILL.md)
- [Specification Phase Issues (+2)](specification-phase-issues/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+1)](mcp-tools/SKILL.md)
