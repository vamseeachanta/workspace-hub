---
name: crossprovider codex idempotence-must-be-re-tested-after-code-structu
description: Idempotence must be re-tested after code structure refactoring
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [shell-scripts, testing, idempotence]
---

Moving a function body outside its shell parent—even without logic changes—can alter variable scope and execution context, breaking idempotence. Test idempotence again after structural refactors, not just after semantic logic changes.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
