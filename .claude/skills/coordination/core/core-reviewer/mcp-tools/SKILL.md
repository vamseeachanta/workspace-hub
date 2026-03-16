---
name: core-reviewer-mcp-tools
description: 'Sub-skill of core-reviewer: MCP Tools (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# MCP Tools (+3)

## MCP Tools


```javascript
// Report review status
  action: "store",
  key: "swarm/reviewer/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "reviewer",
    status: "reviewing",
    files_reviewed: 12,
    issues_found: {critical: 2, major: 5, minor: 8},

*See sub-skills for full details.*

## Code Analysis


```javascript
// Analyze code quality
  repo: "current",
  analysis_type: "code_quality"
}

// Run security scan
  repo: "current",
  analysis_type: "security"
}
```

## Hooks


```bash
# Pre-execution
echo "👀 Reviewer agent analyzing: $TASK"
memory_store "review_checklist_$(date +%s)" "functionality,security,performance,maintainability,documentation"

# Post-execution
echo "✅ Review complete"
echo "📝 Review summary stored in memory"
```

## Related Skills


- [core-coder](../core-coder/SKILL.md) - Provides code to review
- [core-tester](../core-tester/SKILL.md) - Validates test coverage
- [core-researcher](../core-researcher/SKILL.md) - Provides context
- [core-planner](../core-planner/SKILL.md) - Task coordination

Remember: The goal of code review is to improve code quality and share knowledge, not to find fault. Be thorough but kind, specific but constructive. Always coordinate findings through memory.

---
