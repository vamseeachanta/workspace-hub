---
name: crossprovider codex llm-wiki-queryability-is-frontmatter-structure-n
description: llm-wiki queryability is frontmatter structure, not body text
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [llm-wiki, architecture, content-model]
---

Pages become queryable via metadata/registry fields (domain, code_id, tags, visibility) in frontmatter, not body content; #635 owns navigation/query-surface wiring separate from content. A page can exist in full detail without being registrable or queryable; structure precedes navigation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
