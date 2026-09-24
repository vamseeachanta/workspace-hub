---
name: crossprovider codex case-sensitivity-in-path-rglob-on-posix-systems
description: Case-sensitivity in Path.rglob on POSIX systems
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [glob-patterns, posix-portability, file-enumeration]
---

`Path.rglob('*.pdf')` is case-sensitive on POSIX filesystems and will miss uppercase `.PDF` files. Independent validation with case-insensitive `find -iname` can verify actual corpus coverage and catch this edge case.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
