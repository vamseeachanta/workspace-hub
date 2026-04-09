---
name: test-fixer
category: development
description: Safe workflow for fixing bulk test assertion failures in existing test suites — collection errors mask deeper problems, replace_all corrupts, fix source first then tests
---

# Test Fixer — Bulk Test Failure Resolution

## When to Use

- 5+ failing tests in an existing test suite
- Collection errors masking real test failures
- Assertion mismatches between tests and evolved source code
- Async test framework misconfiguration

## Critical: Fix Collection Errors FIRST

Collection errors (ImportError, ModuleNotFoundError) cause pytest to stop collecting and skip subsequent test files. The "2 errors" you see initially may mask 50+ real failures.

**Workflow:**
1. Run `pytest --collect-only -q` to see only collection errors
2. Fix import paths, missing dependencies, pytest.ini markers one at a time
3. Re-run `pytest -q --tb=line | grep FAILED` to reveal the FULL failure count

```bash
# Step 1: Check collection, then full run
uv run python -m pytest tests/ --collect-only -q 2>&1 | grep -E "^ERROR"
# Fix each one
uv run python -m pytest tests/ -q --tb=line 2>&1 | grep "^FAILED"
```

## Strategy: Categorize Before Fixing

Group failures by root cause, then fix each category:
1. **Async/framework config** — 1-2 file changes fix many tests (install pytest-asyncio, add markers)
2. **Import paths** — hardcoded /mnt/github/github/... to /mnt/local-analysis/... (1 fix per file)
3. **Assertion mismatches** — output text changed, method names changed (1+ fix per assertion)
4. **Missing methods** — tests call APIs that no longer exist (requires source change or test deletion)
5. **Mock failures** — exception types don't match what source catches

**Fix ordering:** categories 1→2 fix many at once, then 3→5 per-file.

## Safe Patching Patterns

### NEVER use replace_all=True with short strings

```python
# CATASTROPHIC: replaces ALL occurrences including in unrelated methods
patch(mode="replace", old_string='    assert "25%" in output', replace_all=True)
```

### DO include 3+ lines of surrounding context

```python
# SAFE: context makes it unique
patch(mode="replace", old_string="""        progress.update_percentage(25)
            output = mock_stdout.getvalue()
        
        assert "25%" in output""", new_string="""...""")
```

### Use write_file for complex multi-fix scripts

When `patch()` fails due to string escaping (multiline with quotes, braces), write a fix script:

```python
# Write to file, then execute
write_file("/tmp/fix_tests.py", fix_script_content)
terminal(command="python3 /tmp/fix_tests.py")
```

**WARNING:** Python f-strings break when the script content contains `{}`. Use `r"""..."""` raw strings for the script content to avoid this.

### Alternative: sed on line numbers

```bash
sed -i '124old_line/new_line/' tests/agent_os/commands/test_file.py
```

## Common Failure Patterns and Fixes

### Async tests: "async def functions are not natively supported"
- **Fix**: `uv pip install pytest-asyncio`, add `asyncio_mode = auto` to pytest.ini, ensure `pytest.mark.asyncio` marker exists

### ModuleNotFoundError with hardcoded paths
- **Fix**: Convert hardcoded paths to relative using `os.path.join(os.path.dirname(__file__), '...')`

### Assertion mismatches (expected X, got Y)
- **Probe actual API first**: `uv run python3 -c "from module import Class; c = Class(); print(repr(c.method()))"`
- **Then update test** to match actual behavior — don't guess

### AttributeError: object has no attribute
- Source API evolved; method removed. Either restore it in source or delete/skip the test.

### execute() crashes: "unhashable type: 'slice'"
- Root cause: source `execute(args: List[str])` called `parser.parse(args)` which does `args[1:]`, but tests pass `dict`.
- **Fix source** to accept both: `if isinstance(args, dict): parsed = dict_to_args(args); else: parsed = self.parser.parse(args)`

## Subagent Gotchas for Test Fixing

### delegate_task IS viable for test fixing — with caveats

The subagent's `patch`/`terminal` calls **DO execute on the real filesystem** (not a sandbox). However:

1. **Subagent summaries are USELESS** — 1-2 sentences despite consuming M of tokens. Always `git diff` or re-run tests after.
2. **Subagents OVERREACH** — they modify unrelated files (result ymls, agent configs). Always `git diff --stat` and `git checkout -- <unrelated>`.
3. **Max iterations kill progress** — always check how many failures remain when a subagent exits.

### Subagent delegate_task vs execute_code for test fixing

| Approach | Pros | Cons |
|----------|------|------|
| **execute_code + write_file patch script** | Full control, no summary loss, single call | Script file writing needed, f-string escaping traps |
| **delegate_task** | Subagent can reason about test/source alignment | 99% summary loss, may overreach, max iterations |
| **Direct patch() calls** | Precise, safe | Tedious for many fixes, escaping issues with multiline |

**Recommendation for >20 fixes**: delegate_task to do initial work, then `git diff --stat` to verify, then direct patches for remaining.

## The replace_all Anti-Pattern (SEVERE)

`replace_all=True` with generic substrings like `'assert "25%"'` corrupts UNRELATED test methods. Real incident: replacing `"25%"` in a 645-line test file broke 6 additional tests. If you MUST use `replace_all`, verify every changed line in `git diff` before committing.

## Indentation Corruption Gotcha

Partial patch replacements inside `with`, `if`, `for`, or `try` blocks can corrupt indentation.

**After every patch**, run:
```bash
python3 -c "import py_compile; py_compile.compile('tests/test_file.py', doraise=True)"
```

Common corruption: a `replace` inside a `with` block changes only the first line of a multi-line call, leaving subsequent lines at the wrong indent.

## GitHub Issues

`gh issue create --label "phase:2"` silently fails (prints warning, still creates issue) if label doesn't exist. Always use existing labels: `gh label list | grep -E "priority|cat:"`.

## Windows Line Ending Trap (\r\n)

Files originating from Windows (e.g., `agents/`, `*_integration.py` with `\r\n`) cause the `patch` tool to produce massive spurious diffs — 700+ line diffs from a 10-line change. The patch tool doesn't handle CR/LF gracefully.

**Detection:** `cat -A filename.py` — if lines end with `^M$`, it has `\r\n`.

**Fix:** Always use Python/`sed` for these files instead of `patch`:
```python
# Read, modify, write with explicit newline handling
with open(path, 'r') as f:
    content = f.read()
content = content.replace(old_block, new_block, 1)
with open(path, 'w') as f:
    f.write(content)
```
Or use `sed -i` for single-line fixes.

## __init__ vs execute() Timing Trap

When tests pass config via dict args to `execute()` (e.g., `agents_base_dir`), but the class initializes components (generators, loaders) in `__init__` with default paths, the override will be ignored.

**Pattern to fix:**
```python
def execute(self, args):
    if isinstance(args, dict):
        base_dir = args.get("agents_base_dir")
        if base_dir:
            self.base_dir = Path(base_dir)
            self.agents_dir = self.base_dir / "agents"
            # CRITICAL: reinitialize ALL components that depend on the path
            self.structure_generator = AgentStructureGenerator(self.agents_dir)
```

**Better fix:** Pass `base_dir` to the constructor in tests instead of the dict workaround.

## SQLAlchemy PostgreSQL Models vs SQLite in CI

Tests using `PgEnum` (PostgreSQL-specific enum types) or schema-qualified columns ALWAYS fail under SQLite in-memory DB. Symptoms:
- `TypeError: 'name' is an invalid keyword argument for Model` — fixture uses old field name; model has evolved (e.g. `name` -> `company_name`)
- `RuntimeError: dictionary changed size during iteration` — source bug in code under test (fix source, not test)
- `AssertionError: assert None is not None` — computed field (IRR, etc.) returns None for test data; relax assertion or fix dataset
- `AttributeError: 'dict' object has no attribute 'data'` — API returns dict, test expects object; update assertion

**Fix strategy for PostgreSQL-only tests:**
- Skip entire test classes (not individual tests) with clear reason:

```python
@pytest.mark.skip(
    reason="PostgreSQL-specific ENUM types (PgEnum) are incompatible with SQLite in-memory DB. "
           "Run with --database marker against a real PostgreSQL instance."
)
class TestSomeModel:
    ...
```

- Always skip the WHOLE class — individual test skips miss fixture errors that trigger before the test body

**Check actual model field names FIRST before patching fixtures:**
```bash
grep -n 'Mapped\[' src/worldenergydata/module/database/models.py
```
Then update fixtures to match canonical field names (e.g. `company_name=`, `country_of_registration=`).

## Legacy Namespace Compat (worldenergydata._compat pattern)

When tests import from `worldenergydata.modules.X.Y.Z` but the canonical layout is `worldenergydata.X.Y.Z`:
- `_compat.py` handles top-level redirect (`worldenergydata.modules.bsee` -> `worldenergydata.bsee`) but NOT deep nested subpackages
- Fix deep nesting via symlink: `ln -s ../../modules/bsee/analysis/type_curves src/worldenergydata/bsee/analysis/type_curves`
- For test files with wrong prefixes (e.g. `src.worldenergydata.modules.fdas`, `sodir_module.*`), fix the test imports directly to canonical paths

**Wrong prefix patterns seen in practice:**
```python
# BAD — src. prefix invalid when package is installed
from src.worldenergydata.modules.fdas.analysis.cashflow import CashflowEngine

# BAD — stale module name no longer exists  
from sodir_module.analysis import SodirAnalyzer

# GOOD — canonical path
from worldenergydata.fdas.analysis.cashflow import CashflowEngine
from worldenergydata.sodir.analysis import SodirAnalyzer
```

## pytest.ini norecursedirs for Broken Test Dirs

When `_archive/`, `legacy/`, date-based dirs (e.g., `2025-08-*`), or project dirs contain broken tests:
- Add them to `norecursedirs` in pytest.ini — but use glob patterns like `legacy*` (not just `legacy_`) to catch plain `legacy/` dirs
- `--noconftest` disables `collect_ignore_glob` in conftest.py, so use `--ignore=` in addopts for single-file exclusions
- Scan ALL errors at once with `pytest --collect-only 2>&1 | grep "ERROR collecting"` before iteratively adding — the iterative approach wastes tokens

## Verification

After each batch of fixes:
```bash
uv run python -m pytest tests/ -q --tb=line 2>&1 | tail -5
# Should show: X failed, Y passed, Z skipped in Ns
# Track: failures should be monotonically decreasing
```
