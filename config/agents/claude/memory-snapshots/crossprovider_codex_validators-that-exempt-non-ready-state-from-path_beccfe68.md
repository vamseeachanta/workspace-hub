---
name: crossprovider codex validators-that-exempt-non-ready-state-from-path
description: Validators that exempt non-ready state from path/status checks allow coordination drift to pass silently
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [validation, tooling-gaps, coordination-risk]
---

Coordination metadata (split registry, plan references) can become stale without triggering validation failures if the validator skips full checks for non-ready rows. Manual reconciliation between plan state and coordination metadata is required before status transitions.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
