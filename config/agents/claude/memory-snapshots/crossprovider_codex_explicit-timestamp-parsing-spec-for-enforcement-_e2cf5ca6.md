---
name: crossprovider codex explicit-timestamp-parsing-spec-for-enforcement-
description: Explicit timestamp parsing spec for enforcement logic
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [timestamp-parsing, specification, edge-cases]
---

When timestamps are gate decisions, specify: accepted formats (ISO 8601, UTC-only), parsing library, comparison rule (UTC-aware datetime, not string), and explicit cases for absent/malformed/valid values. Skipping this invites timezone and format edge cases in production.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
