---
name: crossprovider codex inertia-tensor-frame-of-reference-must-match-com
description: Inertia tensor frame-of-reference must match computation origin
metadata:
  type: reference
  source: codex
  bridged: 2026-06-14
  tags: [physics, modeling, assumption-tracking, correctness]
---

Tensor computed relative to centre-of-gravity but labeled as body_origin (or vice versa) breaks physics simulations downstream. Explicit `inertia_tensor_origin` field must match the actual reference point used.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
