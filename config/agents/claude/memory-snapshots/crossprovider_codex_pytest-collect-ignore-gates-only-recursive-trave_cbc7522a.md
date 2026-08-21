---
name: crossprovider codex pytest-collect-ignore-gates-only-recursive-trave
description: pytest collect_ignore gates only recursive traversal, not explicit targeting
metadata:
  type: reference
  source: codex
  bridged: 2026-08-15
  tags: [pytest, conftest, test-gating, configuration]
---

Root conftest.py with collect_ignore blocks recursive repo collection but does NOT block explicit pytest <file> or pytest <dir> invocations. Directory targeting still descends into gated subtrees and triggers collection errors. Use only for recursive-traversal protection; explicit paths bypass the gate.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
