---
name: crossprovider hermes report-artifact-date-count-sync-is-a-validator-g
description: Report-artifact date/count sync is a validator gate
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [validation, artifact-consistency, llm-wiki, knowledge-graph]
---

Generated knowledge graphs can drift: summary.json reports `edge_count=6136, run_date=2026-05-17` while staged report file is stale `2026-05-16, Edges: 6056`. Validator must check report metadata (filename, heading, edge count) matches summary.json; staging without regeneration creates silent failures that tests don't catch.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
