---
name: crossprovider codex data-pipeline-plans-must-specify-schema-joins-an
description: Data-pipeline plans must specify schema, joins, and fail-closed behavior
metadata:
  type: reference
  source: codex
  bridged: 2026-07-03
  tags: [planning, data-pipeline, schema-verification]
---

When reviewing plans for data pipelines or report generation, verify not just source existence/row counts but schema (which columns exist, which are missing), explicit join paths for promised fields, and whether missing optional sources cause output omission (fail-open, risky) or halt (fail-closed, safe). Current sources may lack columns the plan promises.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
