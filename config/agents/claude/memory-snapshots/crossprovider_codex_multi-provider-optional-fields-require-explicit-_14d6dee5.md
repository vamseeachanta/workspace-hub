---
name: crossprovider codex multi-provider-optional-fields-require-explicit-
description: Multi-provider optional fields require explicit canonical representation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [multi-provider, data-normalization, hidden-bugs]
---

When different providers use different field semantics (e.g., week_pct used%, pct_remaining remaining%), establish one canonical formula before applying business logic. Example: `utilization = week_pct if week_pct is not null else (100 - pct_remaining) if pct_remaining is not null else null`. Apply all thresholds/logic only to canonical values to prevent silent misclassification.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
