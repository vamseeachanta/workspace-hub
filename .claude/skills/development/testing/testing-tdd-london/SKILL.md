---
name: testing-tdd-london
description: TDD London School (mockist) specialist for mock-driven, outside-in development.
  Use for behavior verification testing, contract-driven development, testing object
  collaborations, or when focusing on HOW objects interact rather than WHAT they contain.
version: 1.0.0
category: development
type: hybrid
capabilities:
- mock_driven_development
- outside_in_tdd
- behavior_verification
- contract_testing
- interaction_testing
- swarm_test_coordination
tools:
- Read
- Write
- Bash
- Task
related_skills:
- testing-production
- planning-code-goal
- webapp-testing
hooks:
  pre: "echo \"TDD London School session starting...\"\nif command -v npx >/dev/null\
    \ 2>&1; then\n  echo \"Coordinating with swarm test agents...\"\nfi\n"
  post: "echo \"London School TDD complete - mocks verified\"\nif [ -f \"package.json\"\
    \ ]; then\n  npm test --if-present\nfi\n"
requires: []
see_also:
- testing-tdd-london-london-vs-chicago-school
- testing-tdd-london-1-outside-in-development
- testing-tdd-london-metrics-success-criteria
- testing-tdd-london-mcp-tools
tags: []
---

# Testing Tdd London

## Quick Start

```typescript
// 1. Start with acceptance test (outside)
describe('User Registration', () => {
  it('should register new user successfully', async () => {
    const mockRepository = { save: jest.fn().mockResolvedValue({ id: '123' }) };
    const mockNotifier = { sendWelcome: jest.fn() };

    const service = new UserService(mockRepository, mockNotifier);
    await service.register({ email: 'test@example.com' });

    // 2. Verify behavior (interactions)
    expect(mockRepository.save).toHaveBeenCalledWith(
      expect.objectContaining({ email: 'test@example.com' })
    );
    expect(mockNotifier.sendWelcome).toHaveBeenCalledWith('123');
  });
});
```

## When to Use

- Testing object collaborations and message passing
- Contract-driven development with clear interfaces
- Outside-in development starting from user behavior
- When isolation of units is critical
- Service orchestration testing
- Testing HOW objects work together (not WHAT they contain)

## Prerequisites

- Understanding of mock objects vs stubs
- Jest, Vitest, or similar testing framework with mocking support
- Clear separation of concerns in architecture
- Dependency injection pattern in codebase

## References

- [London School TDD](https://github.com/testdouble/contributing-tests/wiki/London-school-TDD)
- [Mocks Aren't Stubs](https://martinfowler.com/articles/mocksArentStubs.html)
- [Growing Object-Oriented Software](http://www.growing-object-oriented-software.com/)

## Version History

- **1.0.0** (2026-01-02): Initial release - converted from tdd-london-swarm agent

## Sub-Skills

- [Configuration](configuration/SKILL.md)
- [Example 1: Service Orchestration Test (+2)](example-1-service-orchestration-test/SKILL.md)
- [Mock Management (+2)](mock-management/SKILL.md)

## Sub-Skills

- [Execution Checklist](execution-checklist/SKILL.md)
- [Error Handling](error-handling/SKILL.md)

## Sub-Skills

- [London vs Chicago School (+2)](london-vs-chicago-school/SKILL.md)
- [1. Outside-In Development (+2)](1-outside-in-development/SKILL.md)
- [Metrics & Success Criteria](metrics-success-criteria/SKILL.md)
- [MCP Tools (+2)](mcp-tools/SKILL.md)
