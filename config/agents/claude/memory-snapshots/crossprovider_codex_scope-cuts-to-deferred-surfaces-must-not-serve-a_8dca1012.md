---
name: crossprovider codex scope-cuts-to-deferred-surfaces-must-not-serve-a
description: Scope cuts to deferred surfaces must not serve as evidence for in-scope fixes
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [scope, evidence, deferral]
---

When a file is explicitly excluded as deferred to a sibling issue, don't cite that excluded file as proof of the in-scope fix. Use only the actual maintained file. For example, don't prove 'path_utils.py has a missing import error' by quoting the non-package duplicate if the fix targets src/assethold/modules/.../path_utils.py.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
