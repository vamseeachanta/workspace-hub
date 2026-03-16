---
name: core-planner-mcp-tools
description: 'Sub-skill of core-planner: MCP Tools (+2).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# MCP Tools (+2)

## MCP Tools


```javascript
// Orchestrate complex tasks
  task: "Implement authentication system",
  strategy: "parallel",
  priority: "high",
  maxAgents: 5
}

// Share task breakdown
  action: "store",

*See sub-skills for full details.*

## Hooks


```bash
# Pre-execution
echo "🎯 Planning agent activated for: $TASK"
memory_store "planner_start_$(date +%s)" "Started planning: $TASK"

# Post-execution
echo "✅ Planning complete"
memory_store "planner_end_$(date +%s)" "Completed planning: $TASK"
```

## Related Skills


- [core-coder](../core-coder/SKILL.md) - Implements planned tasks
- [core-tester](../core-tester/SKILL.md) - Tests planned features
- [core-reviewer](../core-reviewer/SKILL.md) - Reviews deliverables
- [core-researcher](../core-researcher/SKILL.md) - Provides context
