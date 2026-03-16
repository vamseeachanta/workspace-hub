---
name: sparc-refinement-example-4-complexity-reduction
description: 'Sub-skill of sparc-refinement: Example 4: Complexity Reduction.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Example 4: Complexity Reduction

## Example 4: Complexity Reduction


```typescript
// Bad: Cyclomatic complexity = 7
function processUser(user: User): void {
  if (user.age > 18) {
    if (user.country === 'US') {
      if (user.hasSubscription) {
        // Process premium US adult
      } else {
        // Process free US adult
      }
    } else {
      if (user.hasSubscription) {
        // Process premium international adult
      } else {
        // Process free international adult
      }
    }
  } else {
    // Process minor
  }
}

// Good: Cyclomatic complexity = 2
function processUser(user: User): void {
  const processor = getUserProcessor(user);
  processor.process(user);
}

function getUserProcessor(user: User): UserProcessor {
  const type = getUserType(user);
  return ProcessorFactory.create(type);
}
```
