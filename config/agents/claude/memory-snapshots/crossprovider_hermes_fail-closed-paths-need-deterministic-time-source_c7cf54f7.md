---
name: crossprovider hermes fail-closed-paths-need-deterministic-time-source
description: Fail-closed paths need deterministic time source like success paths
metadata:
  type: reference
  source: hermes
  bridged: 2026-05-26
  tags: [testing, determinism, checkers]
---

Exception fallback paths using `datetime.now()` are non-deterministic while success paths honor injected `readiness_now`. For checker contracts and validators requiring determinism, both paths must use same time source. Force-fail tests are needed.

*(Distilled from hermes sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
