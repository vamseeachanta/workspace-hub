---
name: crossprovider codex soft-status-flags-lack-auditability-use-explicit
description: Soft status flags lack auditability — use explicit markers
metadata:
  type: reference
  source: codex
  bridged: 2026-07-01
  tags: [planning, governance, auditability]
---

Plans using conditional status (e.g., `ready=false` unless some condition) lack audit trails and are hard to verify. Define explicit marker files with required fields that validators check deterministically.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
