---
name: crossprovider codex dependent-issue-field-contracts-need-explicit-en
description: Dependent-issue field contracts need explicit enumeration and cross-validation
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, plan-review, integration-testing, field-alignment]
---

Issue #266 (source taxonomy) depends on #269 (database manifest), but the plan did not enumerate which #269 fields (database_family, query_params, alias_source_ids) are expected or how #266 maps them. Tests only verify the consuming code works, not that it uses the right fields from the dependency. Fix: require explicit field-by-field alignment tests between issues.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
