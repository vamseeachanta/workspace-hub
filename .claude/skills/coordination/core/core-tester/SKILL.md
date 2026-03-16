---
name: core-tester
description: Comprehensive testing and quality assurance specialist for ensuring code
  quality through testing strategies
version: 1.0.0
category: coordination
type: agent
capabilities:
- unit_testing
- integration_testing
- e2e_testing
- performance_testing
- security_testing
tools:
- Read
- Write
- Edit
- Bash
- Glob
- Grep
related_skills:
- core-coder
- core-reviewer
- core-researcher
- core-planner
hooks:
  pre: "echo \"\U0001F9EA Tester agent validating: $TASK\"\n# Check test environment\n\
    if [ -f \"jest.config.js\" ] || [ -f \"vitest.config.ts\" ]; then\n  echo \"\u2713\
    \ Test framework detected\"\nfi\n"
  post: "echo \"\U0001F4CB Test results summary:\"\nnpm test -- --reporter=json 2>/dev/null\
    \ | jq '.numPassedTests, .numFailedTests' 2>/dev/null || echo \"Tests completed\"\
    \n"
requires: []
see_also:
- core-tester-test-pyramid
- core-tester-unit-tests
- core-tester-metrics-success-criteria
- core-tester-mcp-tools
tags: []
---

# Core Tester

## Quick Start

```javascript
// Spawn tester agent
Task("Tester agent", "Create comprehensive tests for [feature]", "tester")

// Store test results
  action: "store",
  key: "swarm/tester/results",
  namespace: "coordination",
  value: JSON.stringify({ passed: 145, failed: 0, coverage: "87%" })
}
```

## When to Use

- Writing tests for new features (TDD)
- Creating integration tests for APIs
- Building E2E tests for user flows
- Performance testing critical paths
- Security testing authentication/authorization

## Prerequisites

- Test framework installed (Jest, Vitest, etc.)
- Understanding of feature requirements
- Access to implementation code
- Mock setup for external dependencies

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from tester.md agent

## Sub-Skills

- [Performance Testing (+1)](performance-testing/SKILL.md)
- [Example 1: TDD Workflow (+1)](example-1-tdd-workflow/SKILL.md)
- [Best Practices](best-practices/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Test Pyramid (+2)](test-pyramid/SKILL.md)
- [Unit Tests (+3)](unit-tests/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+3)](mcp-tools/SKILL.md)
