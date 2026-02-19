# Design Patterns — Code Examples

> Full examples extracted from `.claude/rules/patterns.md`. Rules live there; examples live here.

## Dependency Injection

```python
class UserService:
    def __init__(self, repository: UserRepository, notifier: Notifier):
        self.repository = repository
        self.notifier = notifier
```

## Factory Pattern

```python
def create_payment_processor(type: str) -> PaymentProcessor:
    if type == "stripe":
        return StripeProcessor(config.stripe_key)
    elif type == "paypal":
        return PayPalProcessor(config.paypal_key)
    raise ValueError(f"Unknown processor: {type}")
```

## Observer/Event Pattern

```python
event_bus.subscribe("user.created", send_welcome_email)
event_bus.subscribe("user.created", create_analytics_profile)
```

## Error Handling — Recovery Strategy

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

## Logging — Structured Logging

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

- **SRP** (Single Responsibility): One reason to change per class; split when responsibilities diverge.
- **OCP** (Open/Closed): Open for extension, closed for modification; use interfaces and composition.
- **LSP** (Liskov Substitution): Subtypes must be substitutable; don't violate base class contracts.
- **ISP** (Interface Segregation): Many specific interfaces over one general; clients shouldn't depend on unused methods.
- **DIP** (Dependency Inversion): Depend on abstractions, not concretions; high-level modules define interfaces.

## Test Naming Conventions

Format: `test_<what>_<scenario>_<expected_outcome>`

Examples:
- `test_user_login_with_valid_credentials_succeeds`
- `test_payment_with_insufficient_funds_raises_error`
- `test_search_with_empty_query_returns_all_results`

## Test Structure — Arrange-Act-Assert

```python
def test_example():
    # Arrange - set up test data and dependencies
    user = create_test_user()

    # Act - perform the action being tested
    result = user.authenticate(valid_password)

    # Assert - verify the outcome
    assert result.is_authenticated
```
