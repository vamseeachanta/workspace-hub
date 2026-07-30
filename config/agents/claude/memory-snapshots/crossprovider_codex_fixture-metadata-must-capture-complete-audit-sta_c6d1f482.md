---
name: crossprovider codex fixture-metadata-must-capture-complete-audit-sta
description: Fixture metadata must capture complete audit state to be regenerable
metadata:
  type: reference
  source: codex
  bridged: 2026-07-06
  tags: [fixture-design, reproducibility]
---

Scheduler fixture records only the audit's `used_factors` map, omitting the actual defaulted factor value (`7.33`). A downstream consumer regenerating from this metadata cannot reproduce the original conversion. Fixture provenance must be idempotent: everything needed to reconstruct the output must be present in metadata.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
