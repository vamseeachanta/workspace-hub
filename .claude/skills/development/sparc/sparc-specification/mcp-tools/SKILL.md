---
name: sparc-specification-mcp-tools
description: 'Sub-skill of sparc-specification: MCP Tools (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# MCP Tools (+2)

## MCP Tools


```javascript
// Store specification phase start
  action: "store",
  key: "sparc/specification/status",
  namespace: "coordination",
  value: JSON.stringify({
    phase: "specification",
    status: "in_progress",
    timestamp: Date.now()
  })
}
```

## Hooks


```bash
# Pre-specification hook

# Post-specification hook
```

## Related Skills


- [sparc-pseudocode](../sparc-pseudocode/SKILL.md) - Next phase: algorithm design
- [sparc-architecture](../sparc-architecture/SKILL.md) - System design phase
- [sparc-refinement](../sparc-refinement/SKILL.md) - TDD implementation phase
