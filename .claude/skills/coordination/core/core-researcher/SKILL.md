---
name: core-researcher
description: Deep research and information gathering specialist for thorough investigation,
  pattern analysis, and knowledge synthesis
version: 1.0.0
category: coordination
type: agent
capabilities:
- code_analysis
- pattern_recognition
- documentation_research
- dependency_tracking
- knowledge_synthesis
tools:
- Read
- Glob
- Grep
- Bash
- WebSearch
- WebFetch
related_skills:
- core-coder
- core-tester
- core-reviewer
- core-planner
hooks:
  pre: "echo \"\U0001F50D Research agent investigating: $TASK\"\nmemory_store \"research_context_$(date\
    \ +%s)\" \"$TASK\"\n"
  post: "echo \"\U0001F4CA Research findings documented\"\nmemory_search \"research_*\"\
    \ | head -5\n"
requires: []
see_also:
- core-researcher-research-methodology
- core-researcher-research-output-format
- core-researcher-research-checklist
- core-researcher-example-1-codebase-analysis
- core-researcher-metrics-success-criteria
- core-researcher-mcp-tools
- core-researcher-collaboration-guidelines
tags: []
---

# Core Researcher

## Quick Start

```javascript
// Spawn researcher agent
Task("Researcher agent", "Analyze [codebase/topic] and document findings", "researcher")

// Store research findings
  action: "store",
  key: "swarm/shared/research-findings",
  namespace: "coordination",
  value: JSON.stringify({ patterns: [], dependencies: [], recommendations: [] })
}
```

## When to Use

- Analyzing unfamiliar codebases
- Researching best practices for implementation
- Mapping dependencies and relationships
- Identifying patterns and anti-patterns
- Synthesizing knowledge for team consumption

## Prerequisites

- Access to codebase or documentation
- Search tools available (Glob, Grep)
- Memory coordination enabled
- Understanding of project context

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from researcher.md agent

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Best Practices](best-practices/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [Research Methodology (+1)](research-methodology/SKILL.md)
- [Research Output Format (+4)](research-output-format/SKILL.md)
- [Research Checklist](research-checklist/SKILL.md)
- [Example 1: Codebase Analysis (+1)](example-1-codebase-analysis/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+3)](mcp-tools/SKILL.md)
- [Collaboration Guidelines](collaboration-guidelines/SKILL.md)
