---
name: crossprovider codex completeness-evidence-serialization-is-a-privacy
description: Completeness evidence serialization is a privacy leakage vector
metadata:
  type: reference
  source: codex
  bridged: 2026-06-18
  tags: [privacy, leakage, completeness-gate]
---

Completeness records serialize `evidence` strings verbatim into issue bodies and HTML (#744 plan). Issue-specific forbidden-token patterns from #730/#733 (client names, folder labels, account identifiers) can leak via evidence fields unless filtered per-issue. Generic privacy tests don't catch dynamic forbidden-tokens; reuse existing issue-specific token sets.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
