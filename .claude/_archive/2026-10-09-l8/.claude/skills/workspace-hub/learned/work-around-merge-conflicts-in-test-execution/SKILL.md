---
name: work-around-merge-conflicts-in-test-execution
description: Run tests when repo has unresolved merge conflicts in config files by bypassing broken configs and executing tests directly
version: 1.0.0
source: auto-extracted
extracted: 2026-04-14
metadata:
  tags: ["testing", "merge-conflicts", "pytest", "python", "venv"]
---

# Work Around Merge Conflicts in Test Execution

When merge conflicts block `uv run` or `pytest`, locate the existing venv and run tests directly with Python, bypassing the broken `conftest.py` or `pyproject.toml`. Check venv location with `find . -name activate`, activate it, verify dependencies with `pip list`, then run tests with `python -m pytest --override-ini="..."` or execute test modules directly with `python`. This preserves test validation while avoiding conflict resolution that could affect other work.