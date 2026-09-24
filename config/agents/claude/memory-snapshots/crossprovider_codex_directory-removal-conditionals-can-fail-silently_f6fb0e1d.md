---
name: crossprovider codex directory-removal-conditionals-can-fail-silently
description: Directory-removal conditionals can fail silently on wrong assumptions
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [deletion, directory-hygiene, conditional-logic]
---

Plans with "remove directory if empty" logic must verify actual directory contents before execution. Removing 2 items from a 9-item directory won't trigger intended conditional parent removal, causing silent failures.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
