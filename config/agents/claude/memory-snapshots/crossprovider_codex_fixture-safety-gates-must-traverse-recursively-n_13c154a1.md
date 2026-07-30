---
name: crossprovider codex fixture-safety-gates-must-traverse-recursively-n
description: Fixture safety gates must traverse recursively, not just direct children
metadata:
  type: reference
  source: codex
  bridged: 2026-07-04
  tags: [security, test-fixtures, gates]
---

Directory-level bans (e.g., no raw workbooks, no private data, no leaked confidential) that only check `base.iterdir()` will miss nested violations. A file at `fixtures/nested/leak.xlsx` bypasses a ban that scans `fixtures/`. Use recursive `os.walk()` or `pathlib.rglob()` with symlink rejection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
