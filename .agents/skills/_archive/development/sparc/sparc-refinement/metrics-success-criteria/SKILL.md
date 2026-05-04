---
name: sparc-refinement-metrics-success-criteria
description: 'Sub-skill of sparc-refinement: Metrics & Success Criteria.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Metrics & Success Criteria

## Metrics & Success Criteria


```javascript
// Jest configuration for coverage
module.exports = {
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  },
  coveragePathIgnorePatterns: [
    '/node_modules/',
    '/test/',
    '/dist/'
  ]
};
```

- Code coverage: >= 80%
- Cyclomatic complexity: < 10
- All tests passing
- No performance regressions
- Error handling for all failure paths
