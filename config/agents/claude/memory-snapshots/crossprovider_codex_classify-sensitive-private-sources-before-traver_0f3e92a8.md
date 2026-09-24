---
name: crossprovider codex classify-sensitive-private-sources-before-traver
description: Classify sensitive/private sources BEFORE traversal or inspection
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [data-privacy, execution-order, pattern-matching]
---

Marking roots as private or quarantine AFTER reading/listing/measuring them defeats privacy controls. Source classification must precede any filesystem traversal, manifest reading, or size measurement; unknown roots default to quarantine with no inspection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
