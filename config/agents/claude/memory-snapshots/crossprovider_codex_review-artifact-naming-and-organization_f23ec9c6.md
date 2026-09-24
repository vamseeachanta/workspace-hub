---
name: crossprovider codex review-artifact-naming-and-organization
description: Review artifact naming and organization
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [review, organization, metadata, naming-convention]
---

Multi-round adversarial reviews should store artifacts as `scripts/review/results/<date>-<issue>-<provider>-r<N>.md`, keyed by date, issue, provider, and round number. This enables historical tracking and per-provider/round inspection without external log systems.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
