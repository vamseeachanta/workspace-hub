# Design Patterns Rules

> Use patterns intentionally. Prefer simplicity over cleverness.

## Allowed Patterns

### Dependency Injection
- Inject dependencies through constructors
- Enables testing and flexibility
- Use interfaces over concrete types
- See `.claude/docs/design-patterns-examples.md` for examples

### Factory Pattern
- Use when object creation is complex
- Encapsulate creation logic
- Return interfaces, not concrete types

### Observer/Event Pattern
- Decouple components through events
- Use for cross-cutting concerns
- Document event contracts clearly

### Repository Pattern
- Abstract data access behind interfaces
- Single source of truth for entity access
- Keep business logic out of repositories

### Strategy Pattern
- Encapsulate algorithms as interchangeable objects
- Use when behavior varies by context
- Prefer composition over conditionals

## Prohibited Patterns

### God Objects
- No class should know or do everything
- Split by responsibility
- Maximum 10 public methods per class

### Circular Dependencies
- Module A must not import Module B if B imports A
- Use dependency inversion to break cycles
- Events can help decouple

### Singletons (Generally)
- Avoid global mutable state
- Prefer dependency injection
- Exception: Immutable configuration

### Magic Numbers/Strings
- No unexplained literals in code
- Use named constants
- Document the meaning

## Error Handling

### Fail Fast
- Validate inputs at boundaries
- Throw early, catch late
- Don't swallow exceptions silently

### Error Types
- Use specific exception types
- Include context in error messages
- Preserve stack traces when re-throwing

### Recovery Strategy
- Catch recoverable errors with fallback; let fatal errors propagate
- See `.claude/docs/design-patterns-examples.md` for examples

### Never Return Null for Collections
- Return empty list/dict instead of None
- Reduces null checks in calling code

## Logging Standards

### Log Levels
- **ERROR**: Something failed, needs attention
- **WARN**: Unexpected but handled situation
- **INFO**: Significant business events
- **DEBUG**: Detailed diagnostic info

### What to Log
- Request/response boundaries
- External service calls
- Authentication events
- Error conditions with context

### What NOT to Log
- Sensitive data (passwords, tokens, PII)
- High-frequency events without sampling
- Duplicate information

### Structured Logging
- Use key-value pairs in `extra` dict for machine-parseable logs
- See `.claude/docs/design-patterns-examples.md` for examples

## SOLID Principles

Apply SRP, OCP, LSP, ISP, DIP. See `.claude/docs/design-patterns-examples.md` for examples.

## Research Before Building

Check for an official API before building scrapers or estimators. Example: Claude has `GET /api/oauth/usage`. Always find the canonical data source first.
