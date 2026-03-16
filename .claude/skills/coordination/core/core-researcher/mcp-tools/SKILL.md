---
name: core-researcher-mcp-tools
description: 'Sub-skill of core-researcher: MCP Tools (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# MCP Tools (+3)

## MCP Tools


```javascript
// Report research status
  action: "store",
  key: "swarm/researcher/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "researcher",
    status: "analyzing",
    focus: "authentication system",
    files_reviewed: 25,

*See sub-skills for full details.*

## Analysis Tools


```javascript
// Analyze codebase
  repo: "current",
  analysis_type: "code_quality"
}

// Track research metrics
  agentId: "researcher"
}
```

## Hooks


```bash
# Pre-execution
echo "🔍 Research agent investigating: $TASK"
memory_store "research_context_$(date +%s)" "$TASK"

# Post-execution
echo "📊 Research findings documented"
memory_search "research_*" | head -5
```

## Related Skills


- [core-coder](../core-coder/SKILL.md) - Uses research for implementation
- [core-tester](../core-tester/SKILL.md) - Uses research for test scenarios
- [core-reviewer](../core-reviewer/SKILL.md) - Uses research for context
- [core-planner](../core-planner/SKILL.md) - Uses research for task planning
