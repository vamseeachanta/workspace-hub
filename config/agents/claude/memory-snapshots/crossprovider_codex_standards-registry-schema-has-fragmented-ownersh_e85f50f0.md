---
name: crossprovider codex standards-registry-schema-has-fragmented-ownersh
description: Standards registry schema has fragmented ownership boundaries
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [schema-design, ownership-clarity, registry-architecture]
---

Design-codes, transfer-ledger, and intelligence-accessibility registries overlap on fields (code_id, revision, paths, holdings) without explicit ownership contract. Single generic schema cannot represent both code-registry and transfer-ledger; requires separate top-level schema per artifact type with explicit additional-property policy.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
