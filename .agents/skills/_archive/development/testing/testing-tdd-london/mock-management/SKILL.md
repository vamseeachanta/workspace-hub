---
name: testing-tdd-london-mock-management
description: 'Sub-skill of testing-tdd-london: Mock Management (+2).'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Mock Management (+2)

## Mock Management

- Keep mocks simple and focused on single behavior
- Verify interactions, not implementation details
- Use `jest.fn()` for behavior verification
- Avoid over-mocking internal details
- Reset mocks between tests


## Contract Design

- Define clear interfaces through mock expectations
- Focus on object responsibilities and collaborations
- Use mocks to DRIVE design decisions
- Keep contracts minimal and cohesive


## Common Pitfalls


```typescript
// BAD: Over-mocking internal details
const mock = {
  _internalState: {},
  _privateMethod: jest.fn()  // Don't mock private methods
};

// GOOD: Mock only public interface
const mock = {
  publicMethod: jest.fn().mockReturnValue(expectedResult)
};

// BAD: Verifying too many implementation details
expect(mock.method).toHaveBeenCalledTimes(3);  // Fragile

// GOOD: Verify essential behavior
expect(mock.method).toHaveBeenCalledWith(expectedArgs);
```
