---
name: crossprovider codex high-confidence-score-and-approval-readiness-are
description: High confidence score and approval/readiness are orthogonal gates
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [design, classification, semantics]
---

A system can produce high confidence scores independent of release clearance; classification should not infer approval from score alone. Requires explicit multi-gate structure: gates.reviewer, gates.legal, gates.public_release, etc. High score + zero release clearance should land in needs-human-review, never client-ready.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
