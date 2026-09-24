---
name: crossprovider codex doc-verified-test-anti-pattern-creates-circular-
description: Doc-verified test anti-pattern creates circular validation
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, verification, validation-gap]
---

Tests labeled 'doc-verified' often re-derive expected values from the implementation rather than extracting actual document examples. This creates circular validation where the test only verifies the code matches itself, not the source material. True doc verification requires extracted document cases (sections, tables, worked examples) as independent inputs.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
