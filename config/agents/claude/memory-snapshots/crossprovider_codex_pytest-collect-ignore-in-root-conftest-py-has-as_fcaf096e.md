---
name: crossprovider codex pytest-collect-ignore-in-root-conftest-py-has-as
description: pytest collect_ignore in root conftest.py has asymmetric semantics
metadata:
  type: reference
  source: codex
  bridged: 2026-08-12
  tags: [pytest, collection-mechanics, conftest, path-semantics]
---

A root conftest.py with collect_ignore blocks recursive repo-wide traversal but not explicit path arguments. Exact-file targeting (pytest scripts/file.py) still collects tests, while directory targeting (pytest scripts/) can still collect top-level script tests and may error. The blocking only applies to implicit recursive discovery, not deliberate path specification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
