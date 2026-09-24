---
name: crossprovider codex boundary-enforcement-at-fixture-metadata-level
description: Boundary enforcement at fixture metadata level
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-governance, testing, boundary-enforcement]
---

When enforcing policy boundaries (e.g., reference-only vs. GTM-facing), encode the boundary in fixture metadata and test assertions, not just documentation. Legacy assertions and JSON descriptions must be updated to reflect the current boundary or removed entirely; tests should assert absence of old framing.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
