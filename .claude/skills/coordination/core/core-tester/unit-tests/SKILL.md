---
name: core-tester-unit-tests
description: 'Sub-skill of core-tester: Unit Tests (+3).'
version: 1.0.0
category: coordination
type: reference
scripts_exempt: true
---

# Unit Tests (+3)

## Unit Tests


```typescript
describe('UserService', () => {
  let service: UserService;
  let mockRepository: jest.Mocked<UserRepository>;

  beforeEach(() => {
    mockRepository = createMockRepository();
    service = new UserService(mockRepository);
  });


*See sub-skills for full details.*

## Integration Tests


```typescript
describe('User API Integration', () => {
  let app: Application;
  let database: Database;

  beforeAll(async () => {
    database = await setupTestDatabase();
    app = createApp(database);
  });


*See sub-skills for full details.*

## E2E Tests


```typescript
describe('User Registration Flow', () => {
  it('should complete full registration process', async () => {
    await page.goto('/register');

    await page.fill('[name="email"]', 'newuser@example.com');
    await page.fill('[name="password"]', 'SecurePass123!');
    await page.click('button[type="submit"]');

    await page.waitForURL('/dashboard');
    expect(await page.textContent('h1')).toBe('Welcome!');
  });
});
```

## Edge Case Testing


```typescript
describe('Edge Cases', () => {
  // Boundary values
  it('should handle maximum length input', () => {
    const maxString = 'a'.repeat(255);
    expect(() => validate(maxString)).not.toThrow();
  });

  // Empty/null cases
  it('should handle empty arrays gracefully', () => {

*See sub-skills for full details.*
