---
name: core-tester-mcp-tools
description: 'Sub-skill of core-tester: MCP Tools (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# MCP Tools (+3)

## MCP Tools


```javascript
// Report test status
  action: "store",
  key: "swarm/tester/status",
  namespace: "coordination",
  value: JSON.stringify({
    agent: "tester",
    status: "running tests",
    test_suites: ["unit", "integration", "e2e"],
    timestamp: Date.now()

*See sub-skills for full details.*

## Performance Testing


```javascript
// Run performance benchmarks
  type: "test",
  iterations: 100
}

// Monitor test execution
  format: "detailed"
}
```

## Hooks


```bash
# Pre-execution
echo "🧪 Tester agent validating: $TASK"
if [ -f "jest.config.js" ] || [ -f "vitest.config.ts" ]; then
  echo "✓ Test framework detected"
fi

# Post-execution
echo "📋 Test results summary:"
npm test -- --reporter=json 2>/dev/null | jq '.numPassedTests, .numFailedTests' 2>/dev/null || echo "Tests completed"
```

## Related Skills


- [core-coder](../core-coder/SKILL.md) - Provides implementation to test
- [core-reviewer](../core-reviewer/SKILL.md) - Reviews test quality
- [core-researcher](../core-researcher/SKILL.md) - Provides edge cases
- [core-planner](../core-planner/SKILL.md) - Test planning

Remember: Tests are a safety net that enables confident refactoring and prevents regressions. Invest in good tests--they pay dividends in maintainability. Coordinate with other agents through memory.

---
