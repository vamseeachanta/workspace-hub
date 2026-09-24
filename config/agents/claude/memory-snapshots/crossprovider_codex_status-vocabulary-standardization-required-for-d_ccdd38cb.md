---
name: crossprovider codex status-vocabulary-standardization-required-for-d
description: Status vocabulary standardization required for deterministic validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [workflow, data-integrity, process-definition]
---

Work-item status fields use conflicting terms (done, archived, completed, closed) which prevent reliable index generation and queue state validation. Single canonical vocabulary with strict folder-to-status mapping prevents false-positive queue corruption detection.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
