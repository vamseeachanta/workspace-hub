---
name: planning-goal-mcp-tools
description: 'Sub-skill of planning-goal: MCP Tools (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# MCP Tools (+2)

## MCP Tools


```javascript
// Orchestrate GOAP plan across swarm
  task: "execute_goap_plan",
  strategy: "adaptive",
  priority: "high"
});

// Store successful patterns
  action: "store",
  namespace: "goap-patterns",
  key: "deployment_plan_v1",
  value: JSON.stringify(successfulPlan)
});
```

## Hooks


```bash
# Pre-task: Initialize GOAP session

# Post-task: Store learned patterns
```

## Related Skills


- [planning-code-goal](../planning-code-goal/SKILL.md) - SPARC-enhanced code planning
- [sparc-workflow](../../../workspace-hub/sparc-workflow/SKILL.md) - Structured development
- [agent-orchestration](../../../workspace-hub/agent-orchestration/SKILL.md) - Swarm coordination
