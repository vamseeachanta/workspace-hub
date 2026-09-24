---
name: crossprovider codex output-cleanup-must-explicitly-preserve-non-doma
description: Output cleanup must explicitly preserve non-domain artifacts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [output-contract, cleanup-hazard, file-preservation]
---

Reconciliation operations that delete stale per-domain output files must include an explicit preservation rule for README, summary metadata, and other non-domain artifacts. Blanket cleanup rules (e.g., 'delete all <domain>.yaml') can remove supporting files the same run writes, breaking the output contract.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
