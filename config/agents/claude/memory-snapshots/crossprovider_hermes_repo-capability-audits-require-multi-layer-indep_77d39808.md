---
name: crossprovider hermes repo-capability-audits-require-multi-layer-indep
description: Repo capability audits require multi-layer independent verification
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, data-completeness, observability]
---

Single manifests (README module-index or data/catalog.yaml) diverge from actual structure. Audit must independently check module-index + data-catalog + actual files + scheduler readiness + CLI smoke-tests; divergence signals capability gaps.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
