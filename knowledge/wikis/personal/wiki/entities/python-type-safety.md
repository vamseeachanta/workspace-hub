---
title: "Python Type Safety"
tags: [software, python, mypy, type-checking, namedtuple]
sources:
  - career-learnings
added: 2026-04-09
last_updated: 2026-04-09
---

# Python Type Safety

Patterns for using mypy strict mode and Python type annotations to catch runtime errors
at analysis time.

## mypy Strict Mode

Run mypy in strict mode to maximise coverage. For standalone scripts without pyproject.toml:

```
uv run --no-project --with mypy python -m mypy <script.py>
```

## Key Type Patterns

| Pattern | Usage |
|---------|-------|
| `NamedTuple` | Immutable data structures — better than dataclass for read-only data |
| `Path \| None` | Must be narrowed before use (assert or early return) |
| `Optional[X]` or `X \| None` | Use consistently throughout codebase |
| `subprocess.run` return | Includes .returncode, .stdout, .stderr |

## Type Narrowing

- `assert var is not None` narrows type for mypy without runtime cost
- Use `Path` not `str` for all filesystem operations — avoids join errors
- `subprocess.run(check=False)` then inspect `.returncode` for best-effort execution

## Design Patterns

- assert var is not None narrows type for mypy without runtime cost
- Use Path not str for all filesystem operations — avoids join errors
- subprocess.run(check=False) then inspect .returncode for best-effort

## Cross-References

- **Related entity**: [[shell-scripting-patterns]] (defensive coding in different language)
- **Related entity**: [[jsonl-knowledge-stores]] (Python scripts that read/write JSONL)
