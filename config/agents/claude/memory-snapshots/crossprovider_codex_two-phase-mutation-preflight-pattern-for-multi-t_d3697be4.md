---
name: crossprovider codex two-phase-mutation-preflight-pattern-for-multi-t
description: Two-phase mutation preflight pattern for multi-target writes
metadata:
  type: reference
  source: codex
  bridged: 2026-06-22
  tags: [multi-target-writes, atomicity, error-recovery]
---

Separate validation phase that checks ALL targets/paths/permissions/git-tracked status before ANY writes. Leave no partial state on early failure. Validate pages, datasets, report destinations all together, then write all together. Enables clean recovery.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
