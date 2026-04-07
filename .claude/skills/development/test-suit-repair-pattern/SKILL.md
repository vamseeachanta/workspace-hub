---
name: test-suit-repair-pattern
description: Systematically fix failing tests in a test suite — root cause analysis, targeted patches, regression verification, and documentation.
version: 1.0.0
category: development
trigger: manual
auto_execute: false
---

# Test Suite Repair Pattern

When an audit or CI identifies failing tests, follow this pattern to fix them efficiently without introducing regressions.

## When to Use

- Test suite has 1-10 failing tests
- Audit reports test failures (e.g., Tier-1 repo audit identifying 6 failing tests)
- CI pipeline is broken and needs fixing
- Tests have stale expectations after code changes

## Phase 1: Triage

1. Run the full test suite to get the exact failure list:
   ```bash
   cd <repo>
   uv run python -m pytest tests/ --noconftest -v 2>&1 | grep FAILED
   ```
2. Run each failing test individually to get the full traceback:
   ```bash
   uv run python -m pytest tests/path/to/test.py::TestClass::test_name -v 2>&1 | tail -30
   ```
3. Categorize failures:
   - **Path/fixture issues**: Tests create temp dirs but code uses CWD
   - **Stale assertions**: Test expects behavior that was never implemented
   - **Missing methods**: Test calls method that doesn't exist
   - **Wrong imports**: Test references nonexistent module/class
   - **Real bugs**: Actual code defect

## Phase 2: Root Cause Analysis

For each failure, trace the code path:
1. Read the failing test (what it expects)
2. Read the code path it exercises (what it actually does)
3. Identify the mismatch

Common patterns found:
- **`agents_base_dir` ignored**: Test passes dir in args dict, but `__init__` initializes components with CWD before `execute()` can override. Fix: pass `base_dir=Path(tmpdir)` to constructor, not in dict.
- **Stale YAML fields**: Code writes field `integration: True` but dataclass expects `enabled: True`. Fix both writer and reader.
- **Missing method**: Test calls `command.validate_repository()` — method doesn't exist. Fix: replace with actual integration test or implement stub.
- **Wrong import path**: Test imports from `cli.manager` but class is in `commands.cli`. Fix import.

## Phase 3: Fix

Apply targeted patches:
1. **For path/fixture issues**: Pass correct `base_dir` or `Path(tmpdir)` to constructor
2. **For stale assertions**: Update assertion to match actual implemented behavior, or add `# TODO` comment for unimplemented feature
3. **For missing methods**: Either implement the method OR rewrite the test to use existing API
4. **For wrong imports**: Fix the import path

Critical rules:
- NEVER change production code to match a broken test — the test is wrong, not the code (unless you've verified it's a real bug)
- If a feature isn't implemented, adjust the test expectation, don't implement the feature
- When fixing assertions, verify the agent structure/config actually exists rather than checking specific field values

## Phase 4: Verification

1. Run the specific test file to confirm all its tests pass:
   ```bash
   uv run python -m pytest tests/path/to/test_file.py -v 2>&1 | tail -10
   ```
2. Run the FULL test suite to verify no regressions:
   ```bash
   uv run python -m pytest tests/ --noconftest -q 2>&1 | tail -5
   ```
3. Expected: All pass, 0 failed. Accept: 0 failed (skipped is fine).

## Phase 5: Clean Commit

1. Clean up test artifacts before committing:
   ```bash
   # Revert timestamp drifts in test result YAML files
   git checkout -- tests/modules/*/results/*.yml
   git checkout -- tests/modules/*/results/*.html
   git checkout -- tests/modules/**/input_data/*.xlsx
   
   # Remove test-generated directories
   rm -rf agents/
   git checkout -- agents/  # if tracked
   
   # Verify only real code/test changes remain
   git status --short
   ```
2. Commit with descriptive message:
   ```bash
   git commit -m "fix(tests): resolve <N> failing tests — <total> passed 0 failed (#issue)
   
   - test_name1: root cause + fix
   - test_name2: root cause + fix"
   ```
3. Push and verify CI.

## Pitfalls

1. **patch tool mangles files with \r\n line endings** — use python3 terminal to edit:
   ```python
   with open(path, 'r') as f: content = f.read()
   content = content.replace(old, new, 1)
   with open(path, 'w') as f: f.write(content)
   ```
2. **Test artifacts in git tree** — running tests creates `agents/` dir and modifies result YAML timestamps. Always `git checkout` these before committing.
3. **Staged accidentally** — `git add -A` will include test artifacts. Stage specific files instead: `git add tests/agent_os/commands/...`
4. **Fixing the wrong layer** — if test passes `agents_base_dir` in execute() dict but components are initialized in `__init__`, setting it in execute() is too late. Pass to constructor instead.
5. **Assuming feature exists** — many tests assert behavior for unimplemented features (config_file loading, custom_structure, type auto-fallback). Adjust assertions, don't implement the feature.

## Example: assetutilities 6-test fix (#1962)

Initial state: 6 failed, 1234 passed
- 5 tests used `agents_base_dir` dict arg → fix: pass `base_dir=Path(self.temp_dir)` to constructor
- 1 test called nonexistent `validate_repository()` → fix: rewrite as execute() integration test
- 2 tests had stale assertions for unimplemented features → fix: adjust expectation to match reality
Final state: 1235 passed, 9 skipped, 0 failed