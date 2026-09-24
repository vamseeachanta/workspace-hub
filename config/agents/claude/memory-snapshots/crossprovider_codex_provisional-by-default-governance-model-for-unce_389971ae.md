---
name: crossprovider codex provisional-by-default-governance-model-for-unce
description: Provisional-by-default governance model for uncertain data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-governance, verification-workflow, quality-assurance]
---

Mark all extracted tables parse_status = 'provisional-unverified' (parsed) or 'raw-unverified' (raw layout); never 'verified' until human confirmation. Maintain a systematic verification queue (CSV with all provisional/raw tables) to enable later batch human review. Prevents accidental use of unverified extracts as ground truth.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
