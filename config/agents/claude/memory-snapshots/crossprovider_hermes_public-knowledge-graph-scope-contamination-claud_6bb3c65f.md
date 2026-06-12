---
name: crossprovider hermes public-knowledge-graph-scope-contamination-claud
description: Public knowledge graph scope contamination: CLAUDE.md and control files included as nodes
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [llm-wiki, knowledge-graph, public-safety, scope]
---

Knowledge graph generator includes non-content files (CLAUDE.md, .claude/* control/config) as graph nodes in `artifacts/retrieval/public-graph/nodes.jsonl`. These pollute orphan/missing-link analysis and violate public-safety contract; should restrict discovery to content namespaces (`wikis/**/wiki/**/*.md` + explicitly allowed manifests) and filter out maintainer scaffolding.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
