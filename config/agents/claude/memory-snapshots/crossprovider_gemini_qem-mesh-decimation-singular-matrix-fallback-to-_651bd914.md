---
name: crossprovider gemini qem-mesh-decimation-singular-matrix-fallback-to-
description: QEM mesh decimation: singular matrix fallback to v1, v2, midpoint
metadata:
  type: reference
  source: gemini
  bridged: 2026-05-26
  tags: [mesh-decimation, quadric-error-metrics, numerical-robustness]
---

When the 4x4 optimal-contraction linear system is singular (det < 1e-10), evaluate quadric cost at three candidates (v1, v2, midpoint) and pick minimum. Avoids exceptions and handles degenerate geometry gracefully during iterative edge collapse.

*(Distilled from gemini sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
