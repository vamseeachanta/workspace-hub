---
name: bulk-docstring-addition
description: Add Google-style docstrings to all public functions and classes in a Python package. Uses AST parsing for precise gap detection, priority ranking by coverage ratio, and multi-file patching.
tags: [python, docstrings, documentation, refactoring, ast]
trigger: User asks to add docstrings to a package, improve documentation coverage, or add missing docstrings across multiple files.
---

# Bulk Docstring Addition

## When to Use
- User asks to add/improve docstrings across a Python package
- Documentation coverage audit reveals gaps
- Pre-release documentation cleanup

## Key Principle
**Only add docstrings — never change logic or signatures.** This is a pure documentation task.

## Step 1: Rough Coverage Scan (optional, for prioritization)

Use grep-based ratio to rank files by docstring coverage. Lower ratio = worse coverage:

```bash
cd <package_root>
for f in $(find . -name "*.py" | sort); do
  defs=$(grep -c "^\s*def \|^\s*class " "$f" 2>/dev/null || echo 0)
  docs=$(grep -c '"""' "$f" 2>/dev/null || echo 0)
  if [ "$defs" -gt 0 ]; then
    ratio=$(echo "scale=2; $docs / ($defs * 2)" | bc 2>/dev/null)
    echo "$f | defs=$defs | docs=$docs | ratio=$ratio"
  fi
done | sort -t'=' -k4 -n
```

Files with ratio < 0.70 need the most attention.

## Step 2: Precise Gap Detection with AST

This is the **critical step** — use Python's `ast` module for exact identification. Grep ratios are rough; AST parsing is authoritative.

```python
# Run via terminal heredoc (python3 << 'PYEOF' ... PYEOF)
import ast, os

base = '.'
missing = []
for root, dirs, files in os.walk(base):
    for f in files:
        if f.endswith('.py'):
            fp = os.path.join(root, f)
            try:
                with open(fp) as fh:
                    tree = ast.parse(fh.read())
            except:
                continue
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    name = node.name
                    # Skip private methods (keep dunder methods like __init__)
                    if name.startswith('_') and not name.startswith('__'):
                        continue
                    docstring = ast.get_docstring(node)
                    if not docstring:
                        kind = 'class' if isinstance(node, ast.ClassDef) else 'def'
                        missing.append((fp, node.lineno, kind, name))

print(f'Total public defs/classes missing docstrings: {len(missing)}')
for fp, line, kind, name in missing:
    print(f'{fp}:{line} {kind} {name}')
```

## Step 3: Read Files and Apply Docstrings

### Strategy
1. **Read each file** that has missing docstrings (use `read_file`)
2. **Batch by file** — use multi-file `patch` mode when possible (V4A patches)
3. **Use Google-style format** with Args, Returns, Raises, Examples sections

### Google-Style Docstring Format

```python
def function_name(arg1: str, arg2: int = 0) -> dict:
    """One-line summary of what this function does.

    Extended description if needed — explain the algorithm,
    context, or non-obvious behavior.

    Args:
        arg1: Description of arg1.
        arg2: Description of arg2.

    Returns:
        Dictionary with keys ``key1`` and ``key2`` containing
        the computed results.

    Raises:
        ValueError: If arg1 is empty.

    Examples:
        >>> result = function_name("hello", 42)
        >>> print(result["key1"])
    """
```

### Patching Approach
- Use `patch` tool in `replace` mode for targeted insertions
- For `__init__` methods: add docstring right after `def __init__(...):`
- For inner `Config` classes (Pydantic): one-line docstring is sufficient
- For inner functions (closures): brief one-liner is fine
- **Always verify** the patch tool reports lint: ok

## Step 4: Verify Zero Gaps Remain

Re-run the AST scanner from Step 2. Target: `Total public defs/classes missing docstrings: 0`

## Scaling: Parallel Subagents for Large Packages

When total file count across target packages exceeds ~50, use `delegate_task` with parallel subagents:

1. **Pre-triage first** — Quick coverage scan (Step 1) to identify which packages actually need work. Skip packages already at 100% coverage (e.g. a 2-file package with full docstrings).
2. **One subagent per package** — Up to 3 in parallel via `delegate_task(tasks=[...])`. Each subagent gets an isolated context with clear instructions.
3. **Scope by gap size** — Subagents hit iteration limits (~50 tool calls). A package with 165 files and 43 needing docstrings will only complete ~19 files before exhaustion. For large packages, tell the subagent to prioritize files with ZERO docstrings first, then lowest coverage ratio.
4. **Commit per package** — After subagents return, commit each package separately for clean git history.

### Subagent prompt template:
```
goal: Add Google-style docstrings to all public functions/classes in <pkg>/
context: Path is <full_path>. <N> files, <M> defs, <D> existing docstring markers.
         Focus on files MISSING docstrings — skip files with good coverage.
         Do NOT modify logic/imports/signatures. Only add docstrings.
toolsets: ["terminal", "file"]
```

### Lesson: Iteration budget planning
- Reading a file + patching it = ~2-3 tool calls per file
- A subagent with 50 iterations can process ~15-20 files with docstrings
- For packages with 40+ files needing work, create a follow-up issue for the remainder

## Pitfalls

1. **grep ratios mislead** — A file can have ratio=0.84 but still have missing docstrings (e.g. module-level docstrings inflate the count). Always use AST for truth.
2. **`python3 -c` with quotes** — Complex Python one-liners with nested quotes get blocked by terminal. Use heredoc (`python3 << 'PYEOF'`) or `uv run python << 'PYEOF'` instead. Some sandboxes block `python -c` with semicolons entirely.
3. **Duplicate files** — Packages often have copied/mirrored modules (e.g. `marine_analysis/` and `marine_engineering/` with identical catenary solvers). Don't forget the copies.
4. **Pydantic inner Config classes** — These are real classes that AST detects. A one-line `"""Pydantic configuration for ModelName."""` suffices.
5. **Closure/inner functions** — AST detects these too (e.g. `def run_spectrum():` inside a method). One-liner docstrings are appropriate.
6. **Non-unique match in patch** — When multiple `class Config:` or similar exist in one file, use `replace` mode with enough surrounding context to disambiguate, rather than V4A patch mode.
7. **Empty __init__.py files** — These count as files but just need a one-line module docstring. Subagents can bulk-write these with `write_file` instead of patching.
