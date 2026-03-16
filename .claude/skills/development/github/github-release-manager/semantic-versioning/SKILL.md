---
name: github-release-manager-semantic-versioning
description: 'Sub-skill of github-release-manager: Semantic Versioning (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Semantic Versioning (+2)

## Semantic Versioning


```javascript
const versionStrategy = {
    major: "Breaking changes or architecture overhauls",
    minor: "New features, GitHub integration, swarm enhancements",
    patch: "Bug fixes, documentation updates, dependency updates",
    coordination: "Cross-package version alignment"
}
```

## Multi-Stage Validation


```javascript
const validationStages = [
    "unit_tests",           // Individual package testing
    "integration_tests",    // Cross-package integration
    "performance_tests",    // Performance regression detection
    "compatibility_tests",  // Version compatibility validation
    "documentation_tests",  // Documentation accuracy verification
    "deployment_tests"      // Deployment simulation
]
```

## Rollback Strategy


```javascript
const rollbackPlan = {
    triggers: ["test_failures", "deployment_issues", "critical_bugs"],
    automatic: ["failed_tests", "build_failures"],
    manual: ["user_reported_issues", "performance_degradation"],
    recovery: "Previous stable version restoration"
}
```
