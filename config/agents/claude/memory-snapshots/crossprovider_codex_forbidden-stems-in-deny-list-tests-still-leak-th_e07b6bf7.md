---
name: crossprovider codex forbidden-stems-in-deny-list-tests-still-leak-th
description: Forbidden stems in deny-list tests still leak them through the codebase
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [privacy, testing, information-leakage]
---

Encoding private filenames/paths in test assertions or deny-list literals—even as items meant to be rejected—still discloses the stems to anyone reading the code. Use generic placeholders or split fixtures into public/private instead.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
