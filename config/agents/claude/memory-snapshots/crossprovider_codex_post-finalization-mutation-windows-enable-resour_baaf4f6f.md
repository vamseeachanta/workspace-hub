---
name: crossprovider codex post-finalization-mutation-windows-enable-resour
description: Post-finalization mutation windows enable resource substitution
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [toctou, resource-safety, validation-gap, renderer, runtime]
---

Validation completes and system returns success, but resource remains mutable until the caller actually uses it, creating a window for substitution attacks. Renderer safety binding ends before commit/push; runtime final validator runs before resource lock is confirmed; publication acceptance row is unscanned after validation gate. Fix: revalidate immediately before use or prevent mutations post-validation.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
