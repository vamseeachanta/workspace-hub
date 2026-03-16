---
name: core-coder-example-1-basic-implementation
description: 'Sub-skill of core-coder: Example 1: Basic Implementation (+1).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Example 1: Basic Implementation (+1)

## Example 1: Basic Implementation


```typescript
// Task: Implement user discount calculation
Task("Coder", "Implement calculateUserDiscount function with TDD", "coder")

// Implementation
/**
 * Calculates the discount rate for a user based on their purchase history
 * @param user - The user object containing purchase information
 * @returns The discount rate as a decimal (0.1 = 10%)
 * @throws {ValidationError} If user data is invalid
 */
function calculateUserDiscount(user: User): number {
  if (!user || typeof user.purchases !== 'number') {
    throw new ValidationError('Invalid user data');
  }
  return user.purchases >= 10 ? 0.1 : 0;
}
```


## Example 2: API Implementation with Error Handling


```typescript
// Task: Implement REST endpoint with proper error handling
class UserController {
  constructor(private readonly userService: UserService) {}

  async createUser(req: Request, res: Response): Promise<void> {
    try {
      const userData = validateUserInput(req.body);
      const user = await this.userService.create(userData);
      res.status(201).json(user);
    } catch (error) {
      if (error instanceof ValidationError) {
        res.status(400).json({ error: error.message });
      } else {
        logger.error('Failed to create user', { error });
        res.status(500).json({ error: 'Internal server error' });
      }
    }
  }
}
```
