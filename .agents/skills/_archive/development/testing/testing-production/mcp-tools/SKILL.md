---
name: testing-production-mcp-tools
description: 'Sub-skill of testing-production: MCP Tools (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# MCP Tools (+2)

## MCP Tools


```javascript
// Store validation results
  action: "store",
  namespace: "production-validation",
  key: "validation_report_" + Date.now(),
  value: JSON.stringify({
    timestamp: new Date().toISOString(),
    violations: violations,
    passed: validations.passed,
    failed: validations.failed
  })
});
```

## Hooks


```bash
# Pre-deploy: Run production validation

# Post-validation: Report results
```

## Related Skills


- [testing-tdd-london](../testing-tdd-london/SKILL.md) - Unit testing with mocks
- [webapp-testing](../../webapp-testing/SKILL.md) - Web application testing
- [planning-code-goal](../../planning/planning-code-goal/SKILL.md) - Testing strategy planning
