---
name: crossprovider codex reconciliation-artifact-dispositions-must-preser
description: Reconciliation artifact dispositions must preserve variant/stale/local distinctions, not collapse into single state
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [reconciliation, semantics, artifact]
---

Collapsing canonical-missing, variant-exists-but-stale, and local-copy states into single 'missing' label hides maturity. Use explicit enum fields (canonical_status, variant_status, source_disposition) so artifacts reflect actual state readiness.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
