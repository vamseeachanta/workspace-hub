# Design Patterns Rules

> Use patterns intentionally. Prefer simplicity over cleverness.

## Scripts Over LLM Judgment (Hard Rule)

**Deterministic scripts and code are superior to LLM prose.**

- When a script exists for a decision, gate check, or enforcement action → **call the script**
- Never substitute LLM reasoning where a verifiable, repeatable script can run
- **When no script exists yet and the operation is repeatable → create the script first, then call it**
- LLM judgment is only the fallback when a script cannot reasonably be written
- Corollary: if a rule matters, encode it in a script/hook — skill prose is context-rot prone

### Create Scripts to Avoid LLM Overheads (Hard Rule)

When an operation will recur or involves non-trivial logic, **write a script** instead of
performing it inline via LLM reasoning. LLM prose is slow, non-deterministic, and not
auditable — a script runs in milliseconds, produces the same output every time, and can
be version-controlled and tested.

**25% Repetition Rule (Hard Rule):** If there is a ≥25% chance the operation will be performed again — in the same WRK, a future WRK, or by another agent — **write a script instead of reasoning inline**. The cost of writing a 10-line script is always less than the cost of a second LLM pass over the same work.

**Signals that a script is required:**
- The operation could be expressed as a shell/Python one-liner or short program
- The result is consumed again in a future session or by another tool
- The operation involves parsing, counting, filtering, or transforming data
- The same reasoning would need to be repeated across repos or files
- Any doubt whether this will recur → assume it will; write the script

**Do not:**
- Re-derive facts LLM-style that a script already computes (e.g. gate coverage %)
- Write multi-paragraph LLM analysis when `grep | wc -l` would suffice
- Generate structured data (YAML/JSON) by hand when a script can produce it deterministically

Examples:
- Gate verification → `verify-gate-evidence.py WRK-NNN` (not LLM judgment)
- Lifecycle HTML → `generate-html-review.py WRK-NNN --lifecycle` (not ad-hoc generation)
- Stage exit → `exit_stage.py WRK-NNN N` (not LLM checklist)
- Legal scan → `legal-sanity-scan.sh` (not LLM review)
- API docstring coverage → `api-audit.py <repo> <src>` (not manual file-by-file review)

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
