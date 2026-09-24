---
name: crossprovider codex undefined-thresholds-in-matching-lookup-systems-
description: Undefined thresholds in matching/lookup systems cause silent garbage matches
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [lookup-design, threshold-policy, silent-bugs]
---

Nearest-neighbor, similarity, or threshold-based lookups without explicit decision thresholds (exact/high/medium/low/reject) will match every input, including garbage. Define configurable thresholds, rejection criteria, and explicit fallthrough logic (estimation, defaults, fail-closed). Without this, every query appears to have a valid match.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
