---
name: crossprovider hermes readiness-implementation-type-safety-defects-in-
description: Readiness implementation: type-safety defects in evidence handling
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [readiness, dispatch, type-safety, coercion]
---

Evidence `missing_data` field can be int/string but code assumes list, causing TypeError on list() cast; no type validation before consumption. Dirty evidence strings like 'false' evaluate as Python True (implicit truthiness), not False; requires explicit string→bool parsing, not implicit coercion.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
