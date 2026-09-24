---
name: crossprovider codex explicit-routing-notes-in-artifacts-are-load-bea
description: Explicit routing notes in artifacts are load-bearing
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [artifacts, routing, audit-trail, llm-wiki-pattern]
---

Do not discard human-readable routing decisions during report generation. Capture intended use/migration target (e.g., 'assethold for reusable tooling') as explicit `routing_note` fields in JSON/JSONL. Omitting them forces downstream processes to re-derive the decision and masks audit trails.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
