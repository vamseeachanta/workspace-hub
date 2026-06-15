---
name: crossprovider codex intermediate-status-in-production-outputs-create
description: Intermediate status in production outputs creates ambiguity
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [data-quality, status-vocabulary, issue-265]
---

Leaving internal/intermediate statuses like rule-manager-route or probe-needed in final outputs (manifest.json, summaries) confuses whether a path is actionable. Issue #265: 4 Rule Manager routes left as probe-needed with null HTTP status in published candidate universe. Statuses should be fully resolved or gated before output.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
