---
name: core-coder-mcp-tools
description: 'Sub-skill of core-coder: MCP Tools (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# MCP Tools (+3)

## MCP Tools


```javascript
// Report implementation status
  action: "store",
  key: "swarm/coder/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "coder",
    status: "implementing",
    feature: "user authentication",
    files: ["auth.service.ts", "auth.controller.ts"],

*See sub-skills for full details.*

## Performance Monitoring


```javascript
// Track implementation metrics
  type: "code",
  iterations: 10
}

// Analyze bottlenecks
  component: "api-endpoint",
  metrics: ["response-time", "memory-usage"]
}
```

## Hooks


```bash
# Pre-execution
echo "💻 Coder agent implementing: $TASK"
if grep -q "test\|spec" <<< "$TASK"; then
  echo "⚠️  Remember: Write tests first (TDD)"
fi

# Post-execution
echo "✨ Implementation complete"
if [ -f "package.json" ]; then
  npm run lint --if-present
fi
```

## Related Skills


- [core-researcher](../core-researcher/SKILL.md) - Provides context and findings
- [core-tester](../core-tester/SKILL.md) - Validates implementation
- [core-reviewer](../core-reviewer/SKILL.md) - Reviews code quality
- [core-planner](../core-planner/SKILL.md) - Provides task breakdown
