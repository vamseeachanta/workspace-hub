---
name: crossprovider hermes memory-bridge-quality-gates-and-safe-recovery-pa
description: Memory bridge quality gates and safe recovery pattern
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [memory, hermes-to-claude, quality-gate, recovery]
---

Hermes→Claude auto-memory bridge uses quality thresholds: score <50 aborts, 50-70 auto-compacts then bridges, ≥70 bridges directly. If pre-bridge-quality.sh exits nonzero but produces outputs, use pre-bridge-stash as safe recovery to avoid lost durable memory.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
