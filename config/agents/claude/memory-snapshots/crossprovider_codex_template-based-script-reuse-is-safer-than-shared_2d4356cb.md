---
name: crossprovider codex template-based-script-reuse-is-safer-than-shared
description: Template-based script reuse is safer than shared infrastructure for closed-world tools
metadata:
  type: reference
  source: codex
  bridged: 2026-06-21
  tags: [code-organization, testing, ingest-pipeline]
---

For similar generators with local assumptions (routing-queue → disposition → reports), mirroring the structure of a proven existing script (client_private_routing_queue.py pattern) is less risky than building shared libraries. Duplication keeps assumptions explicit and testable within each tool's domain.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
