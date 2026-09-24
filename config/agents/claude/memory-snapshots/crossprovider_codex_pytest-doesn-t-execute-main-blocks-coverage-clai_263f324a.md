---
name: crossprovider codex pytest-doesn-t-execute-main-blocks-coverage-clai
description: pytest doesn't execute __main__ blocks; coverage claims on main-only code are false
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [python-patterns, pytest, testing-gaps]
---

The pytest runner never reaches `__main__` blocks, so version detection or diagnostics there are untested. Don't use `__main__`-only behavior as evidence that code is covered. Move such logic into importable modules and call from fixtures or tests.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
