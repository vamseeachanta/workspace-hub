---
name: crossprovider codex security-critical-parsers-require-exact-byte-lev
description: Security-critical parsers require exact byte-level validation grammars
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, input-validation, parsers, git-object-safety]
---

Structural acceptance of commits, config keys, or recovery artifacts is insufficient; specify exact permitted byte ranges, encodings, length bounds, and forbidden characters before implementation. Permissive parsers can authorize unsafe semantics while passing stated test cases.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
