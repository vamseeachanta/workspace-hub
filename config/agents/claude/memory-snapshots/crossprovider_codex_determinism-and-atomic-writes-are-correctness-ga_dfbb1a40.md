---
name: crossprovider codex determinism-and-atomic-writes-are-correctness-ga
description: Determinism and atomic writes are correctness gates, not polish
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [testing, acceptance, correctness]
---

Acceptance criteria requiring "byte-deterministic output" or "atomic replacement" must have explicit test fixtures. If the producer embeds non-deterministic values (e.g., timestamps), acceptance cannot pass—the spec or implementation must change.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
