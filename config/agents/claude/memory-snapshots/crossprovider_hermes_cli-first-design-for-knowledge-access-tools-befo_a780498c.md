---
name: crossprovider hermes cli-first-design-for-knowledge-access-tools-befo
description: CLI-first design for knowledge-access tools before protocol wrappers
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [api-design, knowledge-systems, architecture]
---

For multi-protocol knowledge systems (RAG, query surfaces, manifests), ship deterministic JSON CLI first with stable schema. Treat MCP/gRPC/HTTP as thin wrappers only after CLI schema stabilizes. Avoids protocol lock-in and establishes CLI as integration foundation.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
