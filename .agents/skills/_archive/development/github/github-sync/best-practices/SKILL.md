---
name: github-sync-best-practices
description: 'Sub-skill of github-sync: Best Practices.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Best Practices

## Best Practices


### 1. Atomic Synchronization

- Use batch operations for related changes
- Maintain consistency across all sync operations
- Implement rollback mechanisms for failed syncs

### 2. Version Management

- Semantic versioning alignment
- Dependency compatibility validation
- Automated version bump coordination

### 3. Documentation Consistency

- Single source of truth for shared concepts
- Package-specific customizations in separate sections
- Automated documentation validation

### 4. Testing Integration

- Cross-package test validation before merge
- Integration test automation
- Performance regression detection
