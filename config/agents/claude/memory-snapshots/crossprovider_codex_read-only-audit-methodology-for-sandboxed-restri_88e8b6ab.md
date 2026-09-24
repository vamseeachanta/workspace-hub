---
name: crossprovider codex read-only-audit-methodology-for-sandboxed-restri
description: Read-only audit methodology for sandboxed/restricted environments
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [operational, sandboxing, audit-methodology, verification]
---

When environment is sandboxed or read-only, keep all work read-only: no file mutations, no implicit state changes. Use GitHub connectors for external metadata, verify findings via diff/inspection only, document what *cannot* be checked due to sandbox limits, and surface blockers explicitly rather than fabricating findings.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
