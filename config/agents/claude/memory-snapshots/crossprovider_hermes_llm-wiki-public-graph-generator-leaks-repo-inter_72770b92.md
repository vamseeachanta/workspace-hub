---
name: crossprovider hermes llm-wiki-public-graph-generator-leaks-repo-inter
description: llm-wiki public-graph generator leaks repo-internal paths via unresolved targets
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, artifact-safety, scope-breach, defect]
---

normalize_target() preserves unresolved link text (e.g., `../../../../../.claude/rules/`, `../../../../../.claude/skills/`) verbatim in published summary.json without scope filtering. Filter unresolved targets to wiki-relative `.md` or omit from public artifacts entirely.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
