---
name: crossprovider gemini pytest-conftest-hook-overrides-ini-and-pyproject
description: pytest conftest hook overrides ini and pyproject directives
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [pytest, test-collection, migration-safety]
---

`pytest_ignore_collect()` hook in conftest.py wins over pytest.ini `norecursedirs` and pyproject.toml `collect_ignore`. Use this pattern to selectively skip broken tests during migration periods without deletion.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
