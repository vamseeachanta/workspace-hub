---
name: crossprovider codex sort-key-contracts-must-specify-determinism-and-
description: Sort-key contracts must specify determinism and collision handling
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [sampling, testing, determinism]
---

Seed/sort/shuffle implementations in sampling pipelines need explicit contract: deterministic ordering guarantees, hash collision behavior, reproducibility across runs, and edge-case handling. Weak sort-key tests block formal review.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
