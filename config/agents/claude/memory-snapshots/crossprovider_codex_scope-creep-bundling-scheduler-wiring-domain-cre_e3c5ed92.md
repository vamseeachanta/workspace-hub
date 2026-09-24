---
name: crossprovider codex scope-creep-bundling-scheduler-wiring-domain-cre
description: Scope creep: bundling scheduler wiring, domain creation, and enforcement into single issues inflates risk
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [plan-review, scope-control, architecture]
---

Plans ostensibly focused on one deliverable (detector, CLI, ingestion) frequently bundle scheduler wiring, wiki-domain creation, enforcement-hook design, and doc updates. This violates single-purpose discipline. Separate concerns into distinct issues unless they are strictly required for core delivery.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
