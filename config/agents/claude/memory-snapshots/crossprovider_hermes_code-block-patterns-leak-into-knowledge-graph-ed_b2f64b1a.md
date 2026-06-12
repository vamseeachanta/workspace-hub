---
name: crossprovider hermes code-block-patterns-leak-into-knowledge-graph-ed
description: Code-block patterns leak into knowledge-graph edges
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [knowledge-graph, parsing, code-safety]
---

Regex patterns and inline code syntax (e.g., `[[:space:]]`, `[REDACTED]`) are parsed as wikilinks, creating spurious unresolved targets and cites edges. Generator must strip code blocks before link parsing to prevent test fixtures and regex comments from polluting the edge set.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
