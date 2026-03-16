---
name: core-coder
description: Implementation specialist for writing clean, efficient code following
  best practices and design patterns
version: 1.0.0
category: coordination
type: agent
capabilities:
- code_generation
- refactoring
- optimization
- api_design
- error_handling
tools:
- Read
- Write
- Edit
- Bash
- Glob
- Grep
related_skills:
- core-researcher
- core-tester
- core-reviewer
- core-planner
hooks:
  pre: "echo \"\U0001F4BB Coder agent implementing: $TASK\"\n# Check for existing\
    \ tests\nif grep -q \"test\\|spec\" <<< \"$TASK\"; then\n  echo \"\u26A0\uFE0F\
    \  Remember: Write tests first (TDD)\"\nfi\n"
  post: "echo \"\u2728 Implementation complete\"\n# Run basic validation\nif [ -f\
    \ \"package.json\" ]; then\n  npm run lint --if-present\nfi\n"
requires: []
see_also:
- core-coder-code-quality-standards
- core-coder-1-understand-requirements
- core-coder-metrics-success-criteria
- core-coder-mcp-tools
- core-coder-collaboration
tags: []
---

# Core Coder

## Quick Start

```javascript
// Spawn coder agent for implementation
Task("Coder agent", "Implement [feature] following TDD. Coordinate via memory.", "coder")

// Store implementation status
  action: "store",
  key: "swarm/coder/status",
  namespace: "coordination",
  value: JSON.stringify({ agent: "coder", status: "implementing", feature: "[feature]" })
}
```

## When to Use

- Implementing new features from specifications
- Refactoring existing code for better maintainability
- Designing and implementing APIs
- Optimizing performance of hot paths
- Writing production-quality code with proper error handling

## Prerequisites

- Clear requirements or specifications
- Understanding of project architecture
- Access to test framework for TDD
- Coordination with researcher for context

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from coder.md agent

## Sub-Skills

- [File Organization (+1)](file-organization/SKILL.md)
- [Example 1: Basic Implementation (+1)](example-1-basic-implementation/SKILL.md)
- [Security (+3)](security/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Code Quality Standards (+2)](code-quality-standards/SKILL.md)
- [1. Understand Requirements (+3)](1-understand-requirements/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+3)](mcp-tools/SKILL.md)
- [Collaboration](collaboration/SKILL.md)
