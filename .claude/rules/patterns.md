# Design Patterns Rules

> Use patterns intentionally. Prefer simplicity over cleverness.

## Allowed Patterns

### Dependency Injection
- Inject dependencies through constructors
- Enables testing and flexibility
- Use interfaces over concrete types
```python
class UserService:
    def __init__(self, repository: UserRepository, notifier: Notifier):
        self.repository = repository
        self.notifier = notifier
```

### Factory Pattern
- Use when object creation is complex
- Encapsulate creation logic
- Return interfaces, not concrete types
```python
def create_payment_processor(type: str) -> PaymentProcessor:
    if type == "stripe":
        return StripeProcessor(config.stripe_key)
    elif type == "paypal":
        return PayPalProcessor(config.paypal_key)
    raise ValueError(f"Unknown processor: {type}")
```

### Observer/Event Pattern
- Decouple components through events
- Use for cross-cutting concerns
- Document event contracts clearly
```python
event_bus.subscribe("user.created", send_welcome_email)
event_bus.subscribe("user.created", create_analytics_profile)
```

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
```python
try:
    result = risky_operation()
except RecoverableError as e:
    logger.warning(f"Recoverable error: {e}, using fallback")
    result = fallback_value()
except FatalError as e:
    logger.error(f"Fatal error: {e}")
    raise
```

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
```python
logger.info(
    "Order processed",
    extra={
        "order_id": order.id,
        "user_id": user.id,
        "amount": order.total,
        "duration_ms": elapsed
    }
)
```

## SOLID Principles

### Single Responsibility
- One reason to change per class
- Split when responsibilities diverge

### Open/Closed
- Open for extension, closed for modification
- Use interfaces and composition

### Liskov Substitution
- Subtypes must be substitutable
- Don't violate base class contracts

### Interface Segregation
- Many specific interfaces over one general
- Clients shouldn't depend on unused methods

### Dependency Inversion
- Depend on abstractions, not concretions
- High-level modules define interfaces
