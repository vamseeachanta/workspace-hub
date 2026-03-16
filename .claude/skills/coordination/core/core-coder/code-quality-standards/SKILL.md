---
name: core-coder-code-quality-standards
description: 'Sub-skill of core-coder: Code Quality Standards (+2).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Code Quality Standards (+2)

## Code Quality Standards


```typescript
// ALWAYS follow these patterns:

// Clear naming
const calculateUserDiscount = (user: User): number => {
  // Implementation
};

// Single responsibility
class UserService {

*See sub-skills for full details.*

## Design Patterns


- **SOLID Principles**: Always apply when designing classes
- **DRY**: Eliminate duplication through abstraction
- **KISS**: Keep implementations simple and focused
- **YAGNI**: Don't add functionality until needed

## Performance Considerations


```typescript
// Optimize hot paths
const memoizedExpensiveOperation = memoize(expensiveOperation);

// Use efficient data structures
const lookupMap = new Map<string, User>();

// Batch operations
const results = await Promise.all(items.map(processItem));

// Lazy loading
const heavyModule = () => import('./heavy-module');
```
