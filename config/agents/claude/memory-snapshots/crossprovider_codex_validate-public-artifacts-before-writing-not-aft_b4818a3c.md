---
name: crossprovider codex validate-public-artifacts-before-writing-not-aft
description: Validate public artifacts before writing, not after
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-safety, atomic-writes, validation-ordering, cleanup]
---

Public artifact generators must validate constraints before replacing output files. Writing first leaves corrupt artifacts if validation fails; re-running the generator doesn't clean them up. Pattern: validate → then write atomically.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
