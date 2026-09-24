---
name: crossprovider codex datum-coordinate-system-reuse-across-different-p
description: Datum/coordinate-system reuse across different physical equations is error-prone
metadata:
  type: reference
  source: codex
  bridged: 2026-09-23
  tags: [physics-modeling, numerical-methods, refactoring]
---

Transforming axial force by subtracting integrated buoyancy (reduced datum) then reusing it for curvature normal-force calculation underestimates the result. When one calculation requires absolute tension and an earlier stage produced reduced-datum tension, reuse without explicit retransformation causes systematic errors.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
