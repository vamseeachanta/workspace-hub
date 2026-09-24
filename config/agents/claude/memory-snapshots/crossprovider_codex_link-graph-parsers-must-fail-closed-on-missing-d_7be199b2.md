---
name: crossprovider codex link-graph-parsers-must-fail-closed-on-missing-d
description: Link-graph parsers must fail closed on missing data
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [parser, generated-artifacts, fail-closed]
---

Parsers extracting embedded JSON from generated artifacts should raise or assert on missing or unparsable JSON, not silently return empty results. Missing data (stale or corrupt artifact) is operationally different from 'no edges defined,' and fail-open parsers can skip validation gates entirely.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
