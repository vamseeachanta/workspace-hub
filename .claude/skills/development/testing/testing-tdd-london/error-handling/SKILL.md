---
name: testing-tdd-london-error-handling
description: 'Sub-skill of testing-tdd-london: Error Handling.'
version: 1.0.0
category: development
type: reference
scripts_exempt: true
---

# Error Handling

## Error Handling


### Missing Mock Verification


```typescript
// Always verify mocks were called as expected
afterEach(() => {
  // Fail if any mock was called unexpectedly
  expect(unexpectedCallsDetected()).toBe(false);
});

// Use strict mocks
const strictMock = jest.fn().mockImplementation(() => {
  throw new Error('Unexpected call');
});
```
### Mock Leakage Between Tests


```typescript
// Always reset mocks
beforeEach(() => {
  jest.clearAllMocks();  // Clears call history
  // or
  jest.resetAllMocks();  // Also resets implementation
});
```
