---
name: crossprovider codex authority-hierarchy-for-infrastructure-runbooks-
description: Authority hierarchy for infrastructure runbooks: registry → runbook → helpers → local state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [infrastructure-docs, authority-hierarchy]
---

Canonical infrastructure documentation should reference the workstation registry or config as the source of truth without copying point-in-time data (e.g., IP addresses) into runbook prose. Executable helpers and machine-local secrets follow, not precede, the documented authority.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
