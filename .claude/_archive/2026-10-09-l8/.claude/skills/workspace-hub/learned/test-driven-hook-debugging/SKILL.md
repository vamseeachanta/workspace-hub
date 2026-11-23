---
name: test-driven-hook-debugging
description: Debugging and fixing shell hooks by writing isolated test suites first, then using test failures to pinpoint logic bugs
version: 1.0.0
source: auto-extracted
extracted: 2026-04-10
metadata:
  tags: ["testing", "shell-scripting", "debugging", "hooks", "TDD"]
---

# Test-Driven Hook Debugging

When a shell hook has subtle logic bugs (e.g., git operations failing silently in non-repo contexts), write a focused test suite in Python using `subprocess` to call the hook in controlled scenarios. Run tests to see the failure mode, then trace the gap between test expectations and hook behavior. Use guard clauses (e.g., `git rev-parse --git-dir` before `git log`) to handle edge cases. Re-run tests atomically after each fix to confirm the change. This approach isolates the bug and prevents regressions better than manual testing.