---
name: crossprovider codex data-extraction-from-generated-embedded-json-mus
description: Data extraction from generated embedded JSON must fail closed
metadata:
  type: reference
  source: codex
  bridged: 2026-07-08
  tags: [json-extraction, robustness, testing, generated-artifacts]
---

When extracting JSON from generated HTML (e.g., `<const FIELD>` blocks), malformed or missing JSON should raise an error, not return an empty result. Fail-open allows stale/corrupted artifacts to skip downstream validation entirely.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
