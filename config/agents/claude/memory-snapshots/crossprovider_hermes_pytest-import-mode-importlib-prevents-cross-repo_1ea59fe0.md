---
name: crossprovider hermes pytest-import-mode-importlib-prevents-cross-repo
description: pytest import-mode=importlib prevents cross-repo test collection collision
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [pytest, test-suite, multi-repo, import-collision]
---

When a shared workspace contains multiple nested repos with same-named `tests/` packages, pytest's default namespace import mode merges them on sys.path. Use `--import-mode=importlib` in pytest.ini or CLI to isolate each repo's test package and prevent collection from unintended directories.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
