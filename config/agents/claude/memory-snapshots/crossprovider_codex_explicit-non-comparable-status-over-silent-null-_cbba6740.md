---
name: crossprovider codex explicit-non-comparable-status-over-silent-null-
description: Explicit non-comparable status over silent null/coercion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-quality, contracts, error-handling]
---

Use explicit status field (e.g., `comparability_status: 'not_comparable'`) when required policy inputs are missing, rather than null normalized values or exceptions. Forces downstream consumers to handle incomplete data explicitly and prevents silent propagation of invalid comparisons.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
