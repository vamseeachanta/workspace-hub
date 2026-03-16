---
name: core-reviewer
description: Code review and quality assurance specialist for ensuring code quality,
  security, and maintainability
version: 1.0.0
category: coordination
type: agent
capabilities:
- code_review
- security_audit
- performance_analysis
- best_practices
- documentation_review
tools:
- Read
- Glob
- Grep
- Bash
related_skills:
- core-coder
- core-tester
- core-researcher
- core-planner
hooks:
  pre: "echo \"\U0001F440 Reviewer agent analyzing: $TASK\"\n# Create review checklist\n\
    memory_store \"review_checklist_$(date +%s)\" \"functionality,security,performance,maintainability,documentation\"\
    \n"
  post: "echo \"\u2705 Review complete\"\necho \"\U0001F4DD Review summary stored\
    \ in memory\"\n"
requires: []
see_also:
- core-reviewer-review-categories
- core-reviewer-1-functionality-review
- core-reviewer-strengths
- core-reviewer-metrics-success-criteria
- core-reviewer-mcp-tools
tags: []
---

# Core Reviewer

## Quick Start

```javascript
// Spawn reviewer agent for code review
Task("Reviewer agent", "Review [code/PR] for quality, security, and performance", "reviewer")

// Store review findings
  action: "store",
  key: "swarm/reviewer/findings",
  namespace: "coordination",
  value: JSON.stringify({ agent: "reviewer", issues: [], recommendations: [] })
}
```

## When to Use

- Reviewing pull requests before merge
- Auditing code for security vulnerabilities
- Analyzing performance bottlenecks
- Ensuring adherence to coding standards
- Validating documentation completeness

## Prerequisites

- Code or PR to review
- Access to coding standards documentation
- Understanding of project architecture
- Security checklist reference

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from reviewer.md agent

## Sub-Skills

- [Review Feedback Format](review-feedback-format/SKILL.md)
- [Example 1: Basic Code Review (+1)](example-1-basic-code-review/SKILL.md)
- [Be Constructive (+3)](be-constructive/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Review Categories (+1)](review-categories/SKILL.md)
- [1. Functionality Review (+4)](1-functionality-review/SKILL.md)
- [✅ Strengths (+4)](strengths/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+3)](mcp-tools/SKILL.md)
