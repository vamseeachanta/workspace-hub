---
name: testing-tdd-london-mcp-tools
description: 'Sub-skill of testing-tdd-london: MCP Tools (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# MCP Tools (+2)

## MCP Tools


```javascript
// Store successful test patterns
  action: "store",
  namespace: "test-patterns",
  key: "order_processing_mocks",
  value: JSON.stringify(mockDefinitions)
});

// Share contracts across swarm
  action: "store",
  namespace: "test-contracts",
  key: "user_service_contract",
  value: JSON.stringify(userServiceContract)
});
```

## Hooks


```bash
# Pre-test: Coordinate with swarm

# Post-test: Share results
```

## Related Skills


- [testing-production](../testing-production/SKILL.md) - Production validation
- [planning-code-goal](../../planning/planning-code-goal/SKILL.md) - TDD integration in SPARC
- [webapp-testing](../../webapp-testing/SKILL.md) - Web application testing
