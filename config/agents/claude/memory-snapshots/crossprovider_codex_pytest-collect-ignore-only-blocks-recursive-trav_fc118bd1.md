---
name: crossprovider codex pytest-collect-ignore-only-blocks-recursive-trav
description: pytest collect_ignore only blocks recursive traversal, not explicit file arguments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [pytest, testing, tooling-quirk]
---

A root-level `collect_ignore` in pytest.ini prevents whole-repo recursive collection but does NOT protect against explicit file path targeting like `pytest scripts/test_foo.py`. This incomplete protection makes it both leaky and hostile to exact-file test isolation strategies.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
