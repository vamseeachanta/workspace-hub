---
name: crossprovider codex fail-closed-disposition-routing-gates-prevent-ac
description: Fail-closed disposition/routing gates prevent accidental broad ingestion
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [safety-pattern, ingest-architecture, reuse]
---

Existing patterns in conference_canary_disposition_gate and manual_review_lane keep scale-out locked until explicitly approved (e.g., `broad_ingestion_dispatched=false` unless gate criteria met). Reuse this pattern for new routing/disposition logic to avoid unlocking on plan-approval alone.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
