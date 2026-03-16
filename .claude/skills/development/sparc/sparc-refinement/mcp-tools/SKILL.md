---
name: sparc-refinement-mcp-tools
description: 'Sub-skill of sparc-refinement: MCP Tools (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# MCP Tools (+2)

## MCP Tools


```javascript
// Store refinement phase progress
  action: "store",
  key: "sparc/refinement/metrics",
  namespace: "coordination",
  value: JSON.stringify({
    coverage: 85,
    testsPass: true,
    complexity: 8,
    timestamp: Date.now()
  })
}
```

## Hooks


```bash
# Pre-refinement hook (run tests)
npm test --if-present

# Post-refinement hook (verify coverage)
npm run test:coverage
```

## Related Skills


- [sparc-specification](../sparc-specification/SKILL.md) - Requirements phase
- [sparc-pseudocode](../sparc-pseudocode/SKILL.md) - Algorithm design phase
- [sparc-architecture](../sparc-architecture/SKILL.md) - System design phase
