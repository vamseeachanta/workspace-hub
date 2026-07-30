---
name: crossprovider codex governance-scope-transitions-audit-all-renderers
description: Governance scope transitions audit all renderers and report generators
metadata:
  type: reference
  source: codex
  bridged: 2026-07-13
  tags: [governance, technical-debt, code-review, drift-prevention]
---

Plan reviews must check that special-case code paths (renderer branches, conditional logic, hyperlinks) keyed to resolved governance issues are actually removed during transition. Stale dead-code branches can silently re-enable the defect if conditions are reintroduced; require explicit removal tests or accept/justify retention.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
