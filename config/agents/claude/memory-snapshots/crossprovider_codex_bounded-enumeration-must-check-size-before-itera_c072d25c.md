---
name: crossprovider codex bounded-enumeration-must-check-size-before-itera
description: Bounded enumeration must check size before iteration
metadata:
  type: reference
  source: codex
  bridged: 2026-07-11
  tags: [enumeration, toctou-safety, resource-limits, pre-check]
---

Directory enumeration size limits must be enforced by checking member count via `fstat(descriptor)` or bounded `scandir()` before iterating, not after materializing the full listing. Attacker-controlled pathname enumeration work and memory consumption remain a vulnerability if listing is unbounded first.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
