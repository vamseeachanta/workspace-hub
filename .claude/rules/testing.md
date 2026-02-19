# Testing Rules

> TDD is mandatory. Tests drive implementation, not the other way around.

## Test-Driven Development (TDD)

### The TDD Cycle
1. **Red**: Write a failing test first
2. **Green**: Write minimal code to pass the test
3. **Refactor**: Improve code while keeping tests green

### TDD is Non-Negotiable
- No implementation code without a failing test first
- Tests define the expected behavior
- If you can't test it, reconsider the design

## Coverage Requirements

### Minimum Thresholds
- **80% overall coverage** is the target
- Critical paths require 100% coverage
- New code must not decrease coverage

### What to Cover
- All public APIs and interfaces
- Edge cases and boundary conditions
- Error handling and exception paths
- Integration points with external systems

### What Can Have Lower Coverage
- Generated code (document why)
- Simple getters/setters (if truly trivial)
- Framework boilerplate

## Test Quality

### Fix Implementation, Not Tests
- When a test fails, the implementation is wrong
- Tests are the specification
- Only modify tests when requirements change

### No Mocks (Prefer Real Data)
- Use real implementations over mocks when possible
- Mocks hide integration issues
- Test doubles allowed for: external APIs, slow operations, non-deterministic behavior
- When mocking is necessary, mock at the boundary

## Test Organization

### Naming Conventions
Format: `test_<what>_<scenario>_<expected_outcome>`. See `.claude/docs/design-patterns-examples.md` for examples.

### Test Structure (Arrange-Act-Assert)
Arrange test data, Act on the subject, Assert outcomes. See `.claude/docs/design-patterns-examples.md` for examples.

## Test Types

### Unit Tests
- Fast, isolated, no external dependencies
- One assertion per test (generally)
- Run on every commit

### Integration Tests
- Test component interactions
- Use real databases (test containers)
- Run before merge

### End-to-End Tests
- Test complete user workflows
- Slower, more brittle
- Run nightly or before release

## Test Maintenance

### Keep Tests Fast
- Unit tests: < 100ms each
- Integration tests: < 5s each
- Parallelize when possible

### Keep Tests Independent
- No shared state between tests
- Each test sets up its own data
- Order of execution should not matter

### Delete Flaky Tests
- Flaky tests erode trust
- Fix or delete within 24 hours
- Track flakiness metrics
