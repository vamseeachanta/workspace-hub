---
name: core-coder-security
description: 'Sub-skill of core-coder: Security (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Security (+3)

## Security

- Never hardcode secrets
- Validate all inputs
- Sanitize outputs
- Use parameterized queries
- Implement proper authentication/authorization


## Maintainability

- Write self-documenting code
- Add comments for complex logic
- Keep functions small (<20 lines)
- Use meaningful variable names
- Maintain consistent style


## Testing

- Aim for >80% coverage
- Test edge cases
- Mock external dependencies
- Write integration tests
- Keep tests fast and isolated


## Documentation

```typescript
/**
 * Calculates the discount rate for a user based on their purchase history
 * @param user - The user object containing purchase information
 * @returns The discount rate as a decimal (0.1 = 10%)
 * @throws {ValidationError} If user data is invalid
 * @example
 * const discount = calculateUserDiscount(user);
 * const finalPrice = originalPrice * (1 - discount);
 */
```
