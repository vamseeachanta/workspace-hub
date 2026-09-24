---
name: crossprovider codex additive-normalization-pattern-for-financial-dat
description: Additive normalization pattern for financial data transformation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [financial-data, architecture, normalization, audit]
---

When normalizing cost data (currency conversion, base-year adjustment, scaling), preserve original as-reported amount/currency/unit fields unchanged and emit separate normalized fields with explicit metadata (normalization method, base year, comparability status). Enables audit trail and non-destructive refinement cycles.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
