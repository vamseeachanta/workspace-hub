---
name: core-coder-1-understand-requirements
description: 'Sub-skill of core-coder: 1. Understand Requirements (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# 1. Understand Requirements (+3)

## 1. Understand Requirements


- Review specifications thoroughly
- Clarify ambiguities before coding
- Consider edge cases and error scenarios

## 2. Design First


- Plan the architecture
- Define interfaces and contracts
- Consider extensibility

## 3. Test-Driven Development


```typescript
// Write test first
describe('UserService', () => {
  it('should calculate discount correctly', () => {
    const user = createMockUser({ purchases: 10 });
    const discount = service.calculateDiscount(user);
    expect(discount).toBe(0.1);
  });
});

// Then implement
calculateDiscount(user: User): number {
  return user.purchases >= 10 ? 0.1 : 0;
}
```

## 4. Incremental Implementation


- Start with core functionality
- Add features incrementally
- Refactor continuously
