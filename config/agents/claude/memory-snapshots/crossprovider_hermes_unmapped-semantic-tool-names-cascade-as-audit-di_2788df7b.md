---
name: crossprovider hermes unmapped-semantic-tool-names-cascade-as-audit-di
description: Unmapped semantic tool names cascade as audit distortion
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [audit, semantic-classification, tool-coverage]
---

Tool names that remain unclassified (literal GitHub/MCP names instead of semantic Read/Grep) accumulate and distort aggregate counts. Codex case: 314 unmapped read-likes + 123 unmapped grep-likes would increase Read +102% and Grep +69% if mapped. Add validation gates that flag remaining unmapped names >2% of tool volume as a quality signal.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
