---
name: crossprovider codex mixed-missing-defaulted-audit-states-violate-ass
description: Mixed missing/defaulted audit states violate assumption contracts
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-validation, contract-violation, edge-case-risk]
---

When a report audit carries both `missing_fields` and `defaulted_fields`, early returns from the missing branch prevent explicit assumption markers (e.g., `oil_tonnes_to_bbl_assumes_default_factor`) from being emitted. The contract requires explicit assumptions whenever defaults are used; mixed states silently drop that marker. Validation allows this state but the output contract is violated. Check branch logic, not just presence validators.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
