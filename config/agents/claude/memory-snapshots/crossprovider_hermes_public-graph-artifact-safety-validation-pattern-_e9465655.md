---
name: crossprovider hermes public-graph-artifact-safety-validation-pattern-
description: Public graph/artifact safety validation pattern for shared knowledge systems
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [public-safety, knowledge-graph, artifact-validation]
---

When generating public/shared artifacts from internal knowledge graphs (like llm-wiki public graph), validation must catch: secrets, absolute filesystem paths, raw wiki internal paths, vendor-derivative content, and private metadata. Emit only node/edge metadata and relationships safe for publication.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
