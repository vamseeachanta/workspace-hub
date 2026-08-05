---
name: crossprovider codex constant-array-circular-mean-noise-can-bypass-nu
description: Constant-array circular-mean noise can bypass null-response gates
metadata:
  type: reference
  source: codex
  bridged: 2026-08-04
  tags: [numerics, circular-mean, test-fixtures, quality-metadata]
---

Two physically null responses below a threshold (e.g., `2e-11` vs `8e-11`) may be labeled NULL_RESPONSE yet still produce disagreement consensus if their numerical variance differs. Null-response quality labeling must gate downstream consensus logic; identical magnitude alone is insufficient.

*(Distilled from codex sessions by bridge-providers-to-dream; the Claude dream consolidates and prunes these.)*
