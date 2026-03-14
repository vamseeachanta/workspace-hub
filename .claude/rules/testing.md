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

## Verified Test Data Sources

### Standards & Textbooks First
- Use worked examples from engineering standards (API RP, DNV-RP, ISO) as test assertions
- Textbook problems with known solutions are ideal TDD inputs (verified, peer-reviewed)
- Dark intelligence archives (`knowledge/dark-intelligence/`) contain extracted inputs/outputs from legacy calculations — use `use_as_test: true` entries
- Research briefs (`specs/capability-map/research-briefs/`) list worked examples per discipline

### Sourcing Priority
1. Standard worked examples (highest confidence — published, peer-reviewed)
2. University coursework solutions (verified by instructor)
3. Dark intelligence extractions (verified against original Excel/tool output)
4. Hand-derived examples (lowest confidence — use only as last resort)

## Test Organization

### Naming Conventions
Format: `test_<what>_<scenario>_<expected_outcome>`. See `.claude/docs/design-patterns-examples.md` for examples.

### Test Structure (Arrange-Act-Assert)
Arrange test data, Act on the subject, Assert outcomes. See `.claude/docs/design-patterns-examples.md` for examples.

## Test Types
- **Unit**: fast, isolated, no external deps — run every commit
- **Integration**: real databases, test containers — run before merge
- **E2E**: full workflows, slower — run nightly

## Test Maintenance
- Unit tests < 100ms, integration < 5s; parallelize when possible
- No shared state; each test sets up its own data
- Flaky tests: fix or delete within 24 hours
