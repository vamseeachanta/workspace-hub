---
name: crossprovider codex path-safety-in-security-scanners-requires-fail-c
description: Path safety in security scanners requires fail-closed repo-bounding
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [security, scanner-design, path-validation]
---

Effective scanner path safety isn't just validating paths exist—it must actively reject symlinks, absolute paths, and full traversal, then fail closed on repo boundary violations. Allow-lists of directories work; deny-lists don't.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
