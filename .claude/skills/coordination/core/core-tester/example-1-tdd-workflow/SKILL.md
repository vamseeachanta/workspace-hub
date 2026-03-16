---
name: core-tester-example-1-tdd-workflow
description: 'Sub-skill of core-tester: Example 1: TDD Workflow (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Example 1: TDD Workflow (+1)

## Example 1: TDD Workflow


```typescript
// Step 1: Write failing test
describe('calculateDiscount', () => {
  it('should return 10% discount for users with 10+ purchases', () => {
    const user = { purchases: 15 };
    expect(calculateDiscount(user)).toBe(0.1);
  });
});

// Step 2: Run test (fails)
// Step 3: Implement minimal code
function calculateDiscount(user) {
  return user.purchases >= 10 ? 0.1 : 0;
}

// Step 4: Run test (passes)
// Step 5: Refactor if needed
```


## Example 2: Complete Test Suite


```typescript
/**
 * @test User Registration
 * @description Validates the complete user registration flow
 * @prerequisites
 *   - Database is empty
 *   - Email service is mocked
 * @steps
 *   1. Submit registration form with valid data
 *   2. Verify user is created in database
 *   3. Check confirmation email is sent
 *   4. Validate user can login
 * @expected User successfully registered and can access dashboard
 */
describe('User Registration', () => {
  it('should register user successfully', async () => {
    // Implementation
  });
});
```
