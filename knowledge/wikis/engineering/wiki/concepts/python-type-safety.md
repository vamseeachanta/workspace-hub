---
title: "Python Type Safety"
tags: [python, mypy, type-safety, namedtuple, strict-mode]
sources: [career-learnings-seed]
added: 2026-04-08
last_updated: 2026-04-08
---

# Python Type Safety

Using mypy strict mode and Python's type system to catch bugs at analysis time rather than runtime.

## mypy Strict Mode

Strict mode enables all optional checks. It catches most runtime errors before execution:

```bash
mypy --strict module.py
```

For standalone scripts without a `pyproject.toml`:

```bash
uv run --no-project --with mypy python -m mypy script.py
```

Key strict-mode flags (all enabled by `--strict`):

| Flag | What it catches |
|------|-----------------|
| `--disallow-untyped-defs` | Functions missing type annotations |
| `--disallow-any-generics` | Bare `list` instead of `list[str]` |
| `--warn-return-any` | Functions that accidentally return `Any` |
| `--no-implicit-optional` | `def f(x: str = None)` must be `Optional[str]` |
| `--strict-equality` | Comparing incompatible types |

## NamedTuple for Immutable Data

Prefer `NamedTuple` over `dataclass` for read-only structured data. NamedTuples are immutable, hashable, and unpackable:

```python
from typing import NamedTuple

class PipeSpec(NamedTuple):
    od: float          # outer diameter (mm)
    wt: float          # wall thickness (mm)
    grade: str         # e.g., "X65"
    smys: float        # specified minimum yield strength (MPa)

spec = PipeSpec(od=323.9, wt=12.7, grade="X65", smys=448.0)
od, wt, grade, smys = spec  # unpacking works
```

Use `dataclass` when you need mutability, `__post_init__`, or default factories.

## Narrowing Optional Types

`Path | None` (or `Optional[Path]`) must be narrowed before use. mypy enforces this:

```python
from pathlib import Path

def process(config_path: Path | None) -> str:
    # WRONG -- mypy error: "None" has no attribute "read_text"
    # return config_path.read_text()

    # Option 1: assert (zero runtime cost, raises AssertionError if None)
    assert config_path is not None
    return config_path.read_text()

    # Option 2: early return
    if config_path is None:
        return "default"
    return config_path.read_text()
```

The `assert var is not None` pattern narrows the type for mypy with negligible runtime cost. Use it when `None` indicates a programming error (not user input).

## Optional[X] vs X | None

Both are equivalent. Choose one style and be consistent within a project:

```python
# PEP 604 syntax (Python 3.10+)
def find(name: str) -> Path | None: ...

# typing module syntax (all Python 3.x)
from typing import Optional
def find(name: str) -> Optional[Path]: ...
```

## subprocess.run Type Awareness

`subprocess.run` returns `CompletedProcess` with typed attributes:

```python
import subprocess

result = subprocess.run(
    ["git", "status", "--porcelain"],
    capture_output=True,
    text=True,
    check=False,
)

# .returncode: int
# .stdout: str (when text=True)
# .stderr: str (when text=True)
if result.returncode != 0:
    raise RuntimeError(f"git failed: {result.stderr}")
```

When `check=True`, a `CalledProcessError` is raised on non-zero exit -- no need to inspect `.returncode`.

## Path Over str

Use `pathlib.Path` instead of `str` for filesystem operations. Paths provide:

- Type safety: `Path` methods are typed; string concatenation is not
- Cross-platform: `/` operator works on Windows and Unix
- Rich API: `.exists()`, `.read_text()`, `.parent`, `.suffix`

```python
from pathlib import Path

# WRONG
config = "/home/user/.config/app/settings.json"
with open(config) as f: ...

# RIGHT
config = Path.home() / ".config" / "app" / "settings.json"
text = config.read_text()
```

## Common mypy Patterns

| Pattern | Purpose |
|---------|---------|
| `TypeGuard[X]` | Custom narrowing functions |
| `@overload` | Different return types based on input |
| `Final[X]` | Constants that cannot be reassigned |
| `Literal["a", "b"]` | Restrict string values |
| `TypedDict` | Typed dictionaries (useful for JSON) |
| `Protocol` | Structural subtyping (duck typing with types) |

## Related Pages

- [Shell Scripting Patterns](shell-scripting-patterns.md) -- calling Python from shell with subprocess
- [JSONL Knowledge Stores](jsonl-knowledge-stores.md) -- typed data parsing with json.loads
- [Test-Driven Development](test-driven-development.md) -- combining mypy with pytest for full coverage

## Cross-References

- **Cross-wiki (marine-engineering)**: [Process Safety](../../../marine-engineering/wiki/concepts/process-safety.md) -- similar slugs (62%); similar titles (62%)
